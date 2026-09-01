from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from .config import CORE_FEATURES, HierarchicalConfig
from .features import latest_snapshot


def normalized_positive(values: pd.Series) -> pd.Series:
    x = pd.to_numeric(values, errors="coerce").fillna(0.0).clip(lower=0.0)
    if x.sum() > 1e-12:
        return x / x.sum()
    return pd.Series(1.0 / max(1, len(x)), index=x.index)


def sparse_probabilities(
    raw: np.ndarray,
    min_probability: float = 0.0,
) -> np.ndarray:
    scores = np.clip(
        np.nan_to_num(np.asarray(raw, dtype=float), nan=0.0),
        0.0,
        None,
    )
    if scores.size == 0:
        return scores
    if scores.sum() > 1e-12:
        p = scores / scores.sum()
    else:
        p = np.full(scores.shape, 1.0 / scores.size)
    if min_probability > 0:
        keep = p >= min_probability
        if not keep.any():
            keep[int(np.argmax(p))] = True
        p = np.where(keep, p, 0.0)
        p /= p.sum()
    return p


def weighted_centroid(
    group: pd.DataFrame,
    features: Iterable[str],
) -> np.ndarray:
    cols = list(features)
    matrix = group[cols].fillna(0.0).to_numpy(float)
    weights = (
        group["avg_amount_base"]
        .fillna(0.0)
        .clip(lower=0.0)
        .to_numpy(float)
    )
    if weights.sum() > 1e-12:
        return np.average(matrix, axis=0, weights=weights)
    return matrix.mean(axis=0)


def vector_distance(
    a: np.ndarray,
    b: np.ndarray,
    cfg: HierarchicalConfig,
) -> float:
    distance = float(np.sqrt(np.mean((a - b) ** 2)))
    if not np.isfinite(distance):
        distance = 1.0
    return max(cfg.min_distance, distance)


def gravity_raw(
    target_mass,
    distance,
    cfg: HierarchicalConfig,
) -> np.ndarray:
    mass = np.asarray(target_mass, dtype=float)
    positive = mass[mass > 0]
    scale = float(np.median(positive)) if len(positive) else 1.0
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = 1.0
    mass = np.clip(mass / scale, 1e-8, None)
    dist = np.clip(
        np.asarray(distance, dtype=float),
        cfg.min_distance,
        None,
    )
    raw = np.power(mass, cfg.beta) / np.power(dist, cfg.gamma)
    return np.nan_to_num(
        raw,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )


def aggregate_nodes(
    snapshot: pd.DataFrame,
    level: str,
) -> pd.DataFrame:
    groups = ["market"] if level == "market" else ["market", "sector"]
    rows = []
    key_spec = groups[0] if len(groups) == 1 else groups
    for key, group in snapshot.groupby(key_spec, sort=False):
        keys = (key,) if len(groups) == 1 else tuple(key)
        row = dict(zip(groups, keys))
        row.update(
            capital_supply=float(group["capital_supply"].sum()),
            capital_demand=float(group["capital_demand"].sum()),
            n_stocks=len(group),
        )
        centroid = weighted_centroid(group, CORE_FEATURES)
        row.update(
            {
                col: float(value)
                for col, value in zip(CORE_FEATURES, centroid)
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def build_market_layer(
    snapshot: pd.DataFrame,
    cfg: HierarchicalConfig,
):
    nodes = aggregate_nodes(snapshot, "market")
    indexed = nodes.set_index("market")
    markets = indexed.index.tolist()
    rows = []
    edge_id = 0

    for source_market in markets:
        source = indexed.loc[source_market]
        budget = float(source["capital_supply"])
        if budget <= 0:
            continue

        targets = []
        masses = []
        distances = []
        source_vector = source[list(CORE_FEATURES)].to_numpy(float)

        for target_market in markets:
            target = indexed.loc[target_market]
            distance = vector_distance(
                source_vector,
                target[list(CORE_FEATURES)].to_numpy(float),
                cfg,
            )
            distance += (
                cfg.same_market_friction
                if source_market == target_market
                else cfg.cross_market_friction
            )
            targets.append(target_market)
            masses.append(float(target["capital_demand"]))
            distances.append(distance)

        if cfg.include_outside:
            targets.append(cfg.outside_name)
            masses.append(
                max(
                    1e-8,
                    cfg.outside_attractiveness
                    * np.mean(masses or [1.0]),
                )
            )
            distances.append(
                max(cfg.min_distance, cfg.outside_distance)
            )

        probabilities = sparse_probabilities(
            gravity_raw(masses, distances, cfg),
            cfg.min_edge_probability,
        )
        for target, probability, distance, mass in zip(
            targets,
            probabilities,
            distances,
            masses,
        ):
            if probability <= 0:
                continue
            rows.append(
                {
                    "date": snapshot["date"].iloc[0],
                    "market_edge_id": edge_id,
                    "source_market": source_market,
                    "target_market": target,
                    "source_budget": budget,
                    "target_mass": mass,
                    "distance": distance,
                    "probability": float(probability),
                    "flow": budget * float(probability),
                }
            )
            edge_id += 1

    return nodes, pd.DataFrame(rows)


def build_sector_layer(
    snapshot: pd.DataFrame,
    market_edges: pd.DataFrame,
    cfg: HierarchicalConfig,
):
    nodes = aggregate_nodes(snapshot, "sector")
    rows = []
    edge_id = 0

    for parent in market_edges.itertuples(index=False):
        if parent.target_market == cfg.outside_name:
            continue

        sources = nodes[nodes["market"] == parent.source_market]
        targets = nodes[nodes["market"] == parent.target_market]
        source_shares = normalized_positive(sources["capital_supply"])

        for pos, (_, source) in enumerate(sources.iterrows()):
            budget = float(parent.flow) * float(source_shares.iloc[pos])
            if budget <= 0:
                continue

            source_sector = str(source["sector"])
            source_vector = source[list(CORE_FEATURES)].to_numpy(float)
            target_names = []
            masses = []
            distances = []

            for _, target in targets.iterrows():
                target_sector = str(target["sector"])
                distance = vector_distance(
                    source_vector,
                    target[list(CORE_FEATURES)].to_numpy(float),
                    cfg,
                )
                distance += (
                    cfg.same_sector_friction
                    if source_sector == target_sector
                    else cfg.cross_sector_friction
                )
                target_names.append(target_sector)
                masses.append(float(target["capital_demand"]))
                distances.append(distance)

            raw = gravity_raw(masses, distances, cfg)
            k = (
                min(cfg.sector_top_k, len(raw))
                if cfg.sector_top_k > 0
                else len(raw)
            )
            keep = (
                np.argpartition(raw, -k)[-k:]
                if len(raw) > k
                else np.arange(len(raw))
            )
            keep = keep[np.argsort(raw[keep])[::-1]]
            probabilities = sparse_probabilities(
                raw[keep],
                cfg.min_edge_probability,
            )

            for idx, probability in zip(keep, probabilities):
                if probability <= 0:
                    continue
                rows.append(
                    {
                        "date": snapshot["date"].iloc[0],
                        "sector_edge_id": edge_id,
                        "parent_market_edge_id": int(
                            parent.market_edge_id
                        ),
                        "source_market": parent.source_market,
                        "source_sector": source_sector,
                        "target_market": parent.target_market,
                        "target_sector": target_names[int(idx)],
                        "source_sector_budget": budget,
                        "distance": distances[int(idx)],
                        "probability_within_source_sector": float(
                            probability
                        ),
                        "flow": budget * float(probability),
                    }
                )
                edge_id += 1

    return nodes, pd.DataFrame(rows)


def squared_distance_block(
    x: np.ndarray,
    y: np.ndarray,
) -> np.ndarray:
    return np.maximum(
        np.sum(x * x, axis=1, keepdims=True)
        + np.sum(y * y, axis=1)[None, :]
        - 2.0 * (x @ y.T),
        0.0,
    )


def build_stock_layer(
    snapshot: pd.DataFrame,
    sector_edges: pd.DataFrame,
    cfg: HierarchicalConfig,
) -> pd.DataFrame:
    columns = [
        "date",
        "parent_sector_edge_id",
        "source_stock_id",
        "target_stock_id",
        "distance",
        "probability_within_source_stock",
        "flow",
    ]
    if sector_edges.empty:
        return pd.DataFrame(columns=columns)

    groups = {
        (str(market), str(sector)): group.reset_index(drop=True)
        for (market, sector), group in snapshot.groupby(
            ["market", "sector"],
            sort=False,
        )
    }
    rows = []
    feature_cols = list(CORE_FEATURES)

    for parent in sector_edges.itertuples(index=False):
        source_key = (
            str(parent.source_market),
            str(parent.source_sector),
        )
        target_key = (
            str(parent.target_market),
            str(parent.target_sector),
        )
        sources = groups.get(source_key)
        targets = groups.get(target_key)
        if (
            sources is None
            or targets is None
            or sources.empty
            or targets.empty
        ):
            continue

        source_budgets = (
            float(parent.flow)
            * normalized_positive(
                sources["capital_supply"]
            ).to_numpy(float)
        )
        x_all = sources[feature_cols].fillna(0.0).to_numpy(np.float32)
        y_all = targets[feature_cols].fillna(0.0).to_numpy(np.float32)
        target_mass = (
            targets["capital_demand"]
            .fillna(0.0)
            .clip(lower=0.0)
            .to_numpy(float)
        )
        positive = target_mass[target_mass > 0]
        mass_scale = (
            float(np.median(positive))
            if len(positive)
            else 1.0
        )
        if not np.isfinite(mass_scale) or mass_scale <= 1e-12:
            mass_scale = 1.0
        normalized_mass = np.clip(
            target_mass / mass_scale,
            1e-8,
            None,
        )
        source_ids = sources["stock_id"].to_numpy(np.int32)
        target_ids = targets["stock_id"].to_numpy(np.int32)
        source_symbols = sources["symbol"].astype(str).to_numpy()
        target_symbols = targets["symbol"].astype(str).to_numpy()

        block_size = max(1, cfg.stock_block_size)
        for start in range(0, len(sources), block_size):
            end = min(start + block_size, len(sources))
            distance = np.sqrt(
                squared_distance_block(
                    x_all[start:end],
                    y_all,
                )
                / len(feature_cols)
            ).astype(float)
            distance = np.maximum(distance, cfg.min_distance)
            raw = (
                np.power(normalized_mass[None, :], cfg.beta)
                / np.power(distance, cfg.gamma)
            )
            raw = np.nan_to_num(
                raw,
                nan=0.0,
                posinf=0.0,
                neginf=0.0,
            )

            if source_key == target_key:
                for local, global_idx in enumerate(
                    range(start, end)
                ):
                    raw[
                        local,
                        target_symbols == source_symbols[global_idx],
                    ] = 0.0

            for local, global_idx in enumerate(range(start, end)):
                budget = float(source_budgets[global_idx])
                scores = raw[local]
                valid = np.flatnonzero(scores > 0)
                if budget <= 0 or len(valid) == 0:
                    continue

                k = (
                    min(cfg.stock_top_k, len(valid))
                    if cfg.stock_top_k > 0
                    else len(valid)
                )
                if len(valid) > k:
                    keep = valid[
                        np.argpartition(scores[valid], -k)[-k:]
                    ]
                else:
                    keep = valid
                keep = keep[np.argsort(scores[keep])[::-1]]
                probabilities = sparse_probabilities(
                    scores[keep],
                    cfg.min_edge_probability,
                )

                for target_idx, probability in zip(
                    keep,
                    probabilities,
                ):
                    if probability <= 0:
                        continue
                    rows.append(
                        (
                            snapshot["date"].iloc[0],
                            int(parent.sector_edge_id),
                            int(source_ids[global_idx]),
                            int(target_ids[int(target_idx)]),
                            float(distance[local, int(target_idx)]),
                            float(probability),
                            budget * float(probability),
                        )
                    )

    out = pd.DataFrame.from_records(rows, columns=columns)
    if not out.empty:
        for col in [
            "parent_sector_edge_id",
            "source_stock_id",
            "target_stock_id",
        ]:
            out[col] = out[col].astype(np.int32)
        out["distance"] = out["distance"].astype(np.float32)
        out["probability_within_source_stock"] = out[
            "probability_within_source_stock"
        ].astype(np.float32)
    return out


def stock_net_migration(
    snapshot: pd.DataFrame,
    stock_edges: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "stock_id",
        "market",
        "sector",
        "symbol",
        "capital_supply",
        "capital_demand",
        "stock_attractiveness",
        "avg_amount_base",
    ]
    out = snapshot[cols].copy()
    if stock_edges.empty:
        out["inferred_inflow"] = 0.0
        out["inferred_outflow"] = 0.0
    else:
        inflow = (
            stock_edges.groupby("target_stock_id")["flow"]
            .sum()
            .rename("inferred_inflow")
        )
        outflow = (
            stock_edges.groupby("source_stock_id")["flow"]
            .sum()
            .rename("inferred_outflow")
        )
        out = out.merge(
            inflow,
            left_on="stock_id",
            right_index=True,
            how="left",
        ).merge(
            outflow,
            left_on="stock_id",
            right_index=True,
            how="left",
        )
        out[["inferred_inflow", "inferred_outflow"]] = out[
            ["inferred_inflow", "inferred_outflow"]
        ].fillna(0.0)

    out["net_migration"] = (
        out["inferred_inflow"] - out["inferred_outflow"]
    )
    out["migration_pressure"] = (
        out["net_migration"]
        / out["avg_amount_base"].replace(0.0, np.nan)
    )
    return out.sort_values(
        "migration_pressure",
        ascending=False,
    )


def conservation_report(
    snapshot: pd.DataFrame,
    market_edges: pd.DataFrame,
    sector_edges: pd.DataFrame,
    stock_edges: pd.DataFrame,
    cfg: HierarchicalConfig,
) -> pd.DataFrame:
    rows = []

    market_out = (
        market_edges.groupby("source_market")["flow"].sum()
        if not market_edges.empty
        else pd.Series(dtype=float)
    )
    for market, expected in snapshot.groupby("market")[
        "capital_supply"
    ].sum().items():
        actual = float(market_out.get(market, 0.0))
        rows.append(
            ("market_source", str(market), float(expected), actual)
        )

    sector_child = (
        sector_edges.groupby("parent_market_edge_id")["flow"].sum()
        if not sector_edges.empty
        else pd.Series(dtype=float)
    )
    for edge in market_edges.itertuples(index=False):
        if edge.target_market != cfg.outside_name:
            rows.append(
                (
                    "sector_children",
                    str(edge.market_edge_id),
                    float(edge.flow),
                    float(
                        sector_child.get(edge.market_edge_id, 0.0)
                    ),
                )
            )

    stock_child = (
        stock_edges.groupby("parent_sector_edge_id")["flow"].sum()
        if not stock_edges.empty
        else pd.Series(dtype=float)
    )
    for edge in sector_edges.itertuples(index=False):
        rows.append(
            (
                "stock_children",
                str(edge.sector_edge_id),
                float(edge.flow),
                float(stock_child.get(edge.sector_edge_id, 0.0)),
            )
        )

    out = pd.DataFrame(
        rows,
        columns=["level", "parent_id", "expected", "actual"],
    )
    out["absolute_error"] = (
        out["expected"] - out["actual"]
    ).abs()
    out["relative_error"] = (
        out["absolute_error"]
        / out["expected"].replace(0.0, np.nan)
    )
    return out


def run_hierarchy(
    panel: pd.DataFrame,
    cfg: HierarchicalConfig,
    date=None,
) -> dict[str, pd.DataFrame]:
    snapshot = latest_snapshot(panel, date, cfg)
    market_nodes, market_edges = build_market_layer(snapshot, cfg)
    sector_nodes, sector_edges = build_sector_layer(
        snapshot,
        market_edges,
        cfg,
    )
    stock_edges = build_stock_layer(snapshot, sector_edges, cfg)
    return {
        "snapshot": snapshot,
        "market_nodes": market_nodes,
        "market_edges": market_edges,
        "sector_nodes": sector_nodes,
        "sector_edges": sector_edges,
        "stock_edges": stock_edges,
        "stock_state": stock_net_migration(
            snapshot,
            stock_edges,
        ),
        "conservation": conservation_report(
            snapshot,
            market_edges,
            sector_edges,
            stock_edges,
            cfg,
        ),
    }
