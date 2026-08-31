# -*- coding: utf-8 -*-
"""引力模型：金融距离、资金迁移矩阵与截面快照。"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import Config, VALUATION_RATIO_COLS


def pairwise_euclidean(features: pd.DataFrame) -> pd.DataFrame:
    x = np.nan_to_num(features.to_numpy(float), nan=0.0)
    diff = x[:, None, :] - x[None, :, :]
    dist = np.sqrt(np.mean(diff**2, axis=2))
    out = pd.DataFrame(
        dist,
        index=features.index,
        columns=features.index,
    )
    values = out.to_numpy()[~np.eye(len(out), dtype=bool)]
    scale = np.nanpercentile(values, 95) if len(values) else 1.0
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = 1.0
    return (out / scale).clip(0, 1)


def valuation_distance_features(
    day: pd.DataFrame,
    cfg: Config,
) -> pd.DataFrame | None:
    """返回估值距离特征；覆盖不足时返回 None，让模型自动重新归一化权重。"""
    available_raw = [
        c for c in VALUATION_RATIO_COLS if c in day.columns
    ]
    if not available_raw:
        return None

    raw = day[available_raw].apply(
        pd.to_numeric,
        errors="coerce",
    )
    positive_mask = raw > 0
    coverage = positive_mask.any(axis=1).mean()
    if coverage < cfg.valuation_min_coverage:
        return None

    z_cols: list[str] = []
    for raw_col in available_raw:
        z_col = f"{raw_col}_z"
        if z_col not in day.columns:
            continue
        valid_count = positive_mask[raw_col].sum()
        if valid_count >= 3 and day[z_col].dropna().nunique() >= 2:
            z_cols.append(z_col)

    if not z_cols:
        return None

    return day[z_cols].fillna(0.0)


def build_distance(
    date: pd.Timestamp,
    day: pd.DataFrame,
    features: pd.DataFrame,
    cfg: Config,
) -> pd.DataFrame:
    symbols = day.index.tolist()

    trailing = features[
        (features["date"] <= date)
        & features["symbol"].isin(symbols)
    ].pivot(
        index="date",
        columns="symbol",
        values="return_1d",
    )
    corr = trailing.tail(cfg.corr_window).corr(
        min_periods=max(10, cfg.corr_window // 3)
    )
    corr = (
        corr.reindex(index=symbols, columns=symbols)
        .fillna(0)
        .clip(-1, 1)
    )
    d_corr = 0.5 * (1 - corr)

    sectors = day["sector"].astype(str).to_numpy()
    d_sector = pd.DataFrame(
        (sectors[:, None] != sectors[None, :]).astype(float),
        index=symbols,
        columns=symbols,
    )

    factor_cols = [
        "momentum_z",
        "volatility_z",
        "liquidity_z",
        "flow_strength_z",
    ]
    d_factor = pairwise_euclidean(
        day[factor_cols].fillna(0.0)
    )

    components: list[tuple[float, pd.DataFrame]] = [
        (cfg.distance_w_corr, d_corr),
        (cfg.distance_w_sector, d_sector),
        (cfg.distance_w_factor, d_factor),
    ]

    val_features = valuation_distance_features(day, cfg)
    if (
        val_features is not None
        and cfg.distance_w_valuation > 0
    ):
        d_valuation = pairwise_euclidean(val_features)
        components.append(
            (cfg.distance_w_valuation, d_valuation)
        )

    active = [(w, d) for w, d in components if w > 0]
    total_w = sum(w for w, _ in active)
    distance = sum(w * d for w, d in active) / total_w
    distance = distance.clip(lower=cfg.min_distance)
    # pandas 3.x Copy-on-Write 下 DataFrame.values 可能是只读视图，
    # 必须先复制再写对角线，否则 np.fill_diagonal 会抛 read-only 错误。
    distance_values = distance.to_numpy(dtype=float, copy=True)
    np.fill_diagonal(distance_values, np.inf)
    distance = pd.DataFrame(
        distance_values,
        index=distance.index,
        columns=distance.columns,
    )
    return distance


def gravity_flows(
    day: pd.DataFrame,
    distance: pd.DataFrame,
    cfg: Config,
) -> pd.DataFrame:
    symbols = day.index.tolist()
    source = (
        day["outflow_budget"]
        .reindex(symbols)
        .fillna(0)
        .clip(lower=0)
        .to_numpy(float)
    )
    attraction = (
        day["attractiveness"]
        .reindex(symbols)
        .fillna(1)
        .clip(lower=1e-8)
        .to_numpy(float)
    )

    with np.errstate(
        divide="ignore",
        invalid="ignore",
        over="ignore",
    ):
        raw = (
            np.power(source, cfg.alpha)[:, None]
            * np.power(attraction, cfg.beta)[None, :]
            / np.power(
                distance.to_numpy(float),
                cfg.gamma,
            )
        )

    raw[~np.isfinite(raw)] = 0.0
    np.fill_diagonal(raw, 0.0)

    row_sum = raw.sum(axis=1, keepdims=True)
    weights = np.divide(
        raw,
        row_sum,
        out=np.zeros_like(raw),
        where=row_sum > 0,
    )
    flow = weights * source[:, None]
    return pd.DataFrame(
        flow,
        index=symbols,
        columns=symbols,
    )


def build_snapshot(
    date: pd.Timestamp,
    features: pd.DataFrame,
    cfg: Config,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = [
        "main_net_flow",
        "avg_amount",
        "momentum_z",
        "volatility_z",
        "liquidity_z",
        "flow_strength_z",
        "attractiveness",
    ]
    day = features[
        features["date"] == date
    ].dropna(subset=required)
    day = day.drop_duplicates("symbol").set_index("symbol")
    if len(day) < cfg.min_cross_section:
        raise ValueError("有效横截面不足")

    distance = build_distance(date, day, features, cfg)
    flow = gravity_flows(day, distance, cfg)

    result = day.copy()
    result["inferred_inflow"] = flow.sum(axis=0)
    result["inferred_outflow"] = flow.sum(axis=1)
    result["net_migration"] = (
        result["inferred_inflow"]
        - result["inferred_outflow"]
    )
    result["migration_pressure"] = (
        result["net_migration"]
        / result["avg_amount"].replace(0, np.nan)
    )
    result["predicted_price_pressure"] = (
        cfg.impact_lambda * result["migration_pressure"]
    )
    return (
        result.sort_values(
            "migration_pressure",
            ascending=False,
        ),
        flow,
    )


def flow_edges(
    flow: pd.DataFrame,
    day: pd.DataFrame,
    top_per_source: int = 3,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for source in flow.index:
        top_targets = (
            flow.loc[source]
            .sort_values(ascending=False)
            .head(top_per_source)
        )
        for target, value in top_targets.items():
            if value <= 0:
                continue
            rows.append(
                {
                    "source": source,
                    "source_name": day.loc[source, "name"],
                    "source_sector": day.loc[source, "sector"],
                    "target": target,
                    "target_name": day.loc[target, "name"],
                    "target_sector": day.loc[target, "sector"],
                    "inferred_flow": float(value),
                }
            )

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        "inferred_flow",
        ascending=False,
    )
