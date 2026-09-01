# -*- coding: utf-8 -*-
"""资本迁移模型：金融距离、Gravity 先验与 Sinkhorn 最优传输。"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import Config, VALUATION_RATIO_COLS
from .features import attraction_score


def pairwise_euclidean(features: pd.DataFrame) -> pd.DataFrame:
    x = np.nan_to_num(features.to_numpy(float), nan=0.0)
    diff = x[:, None, :] - x[None, :, :]
    dist = np.sqrt(np.mean(diff**2, axis=2))
    out = pd.DataFrame(dist, index=features.index, columns=features.index)
    values = out.to_numpy()[~np.eye(len(out), dtype=bool)]
    scale = np.nanpercentile(values, 95) if len(values) else 1.0
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = 1.0
    return (out / scale).clip(0, 1)


def valuation_distance_features(day: pd.DataFrame, cfg: Config) -> pd.DataFrame | None:
    available_raw = [c for c in VALUATION_RATIO_COLS if c in day.columns]
    if not available_raw:
        return None
    raw = day[available_raw].apply(pd.to_numeric, errors="coerce")
    positive_mask = raw > 0
    if positive_mask.any(axis=1).mean() < cfg.valuation_min_coverage:
        return None
    z_cols: list[str] = []
    for raw_col in available_raw:
        z_col = f"{raw_col}_z"
        if z_col in day.columns and positive_mask[raw_col].sum() >= 3 and day[z_col].dropna().nunique() >= 2:
            z_cols.append(z_col)
    return day[z_cols].fillna(0.0) if z_cols else None


def build_distance(date: pd.Timestamp, day: pd.DataFrame, features: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    symbols = day.index.tolist()
    trailing = features[(features["date"] <= date) & features["symbol"].isin(symbols)].pivot(
        index="date", columns="symbol", values="return_1d"
    )
    corr = trailing.tail(cfg.corr_window).corr(min_periods=max(10, cfg.corr_window // 3))
    corr = corr.reindex(index=symbols, columns=symbols).fillna(0).clip(-1, 1)
    d_corr = 0.5 * (1 - corr)

    sectors = day["sector"].astype(str).to_numpy()
    d_sector = pd.DataFrame((sectors[:, None] != sectors[None, :]).astype(float), index=symbols, columns=symbols)

    factor_cols = ["momentum_z", "volatility_z", "liquidity_z", "turnover_intensity_z", "price_impact_z"]
    if cfg.use_auxiliary_main_flow and "flow_strength_z" in day.columns:
        factor_cols.append("flow_strength_z")
    d_factor = pairwise_euclidean(day[factor_cols].fillna(0.0))

    components: list[tuple[float, pd.DataFrame]] = [
        (cfg.distance_w_corr, d_corr),
        (cfg.distance_w_sector, d_sector),
        (cfg.distance_w_factor, d_factor),
    ]
    val_features = valuation_distance_features(day, cfg)
    if val_features is not None and cfg.distance_w_valuation > 0:
        components.append((cfg.distance_w_valuation, pairwise_euclidean(val_features)))

    active = [(w, d) for w, d in components if w > 0]
    total_w = sum(w for w, _ in active)
    if total_w <= 0:
        raise ValueError("金融距离权重之和必须大于 0")
    distance = (sum(w * d for w, d in active) / total_w).clip(lower=cfg.min_distance)
    values = distance.to_numpy(dtype=float, copy=True)
    np.fill_diagonal(values, np.inf)
    return pd.DataFrame(values, index=symbols, columns=symbols)


def _normalize_capped(values: pd.Series, exponent: float, uniform_mix: float, max_share: float) -> pd.Series:
    x = pd.to_numeric(values, errors="coerce").fillna(0.0).clip(lower=0.0)
    arr = x.to_numpy(float)
    n = len(arr)
    if n == 0:
        return pd.Series(dtype=float, index=values.index)
    arr = np.power(np.maximum(arr, 1e-12), max(float(exponent), 1e-8))
    if not np.isfinite(arr).all() or arr.sum() <= 0:
        arr = np.ones(n, dtype=float)
    p = arr / arr.sum()
    mix = float(np.clip(uniform_mix, 0.0, 1.0))
    p = (1.0 - mix) * p + mix / n
    cap = float(np.clip(max_share, 1.0 / n, 0.499999)) if n > 1 else 1.0
    for _ in range(n + 2):
        over = p > cap + 1e-15
        if not over.any():
            break
        excess = float((p[over] - cap).sum())
        p[over] = cap
        under = ~over
        room = np.maximum(cap - p[under], 0.0)
        if room.sum() <= 1e-15:
            break
        p[under] += excess * room / room.sum()
    p = np.maximum(p, 1e-15)
    p /= p.sum()
    return pd.Series(p, index=values.index, dtype=float)


def _transport_mass(day: pd.DataFrame, cfg: Config) -> float:
    amount = pd.to_numeric(day["amount"], errors="coerce").fillna(0).clip(lower=0)
    total_amount = float(amount.sum())
    if total_amount <= 0:
        total_amount = float(pd.to_numeric(day["avg_amount"], errors="coerce").fillna(0).clip(lower=0).sum())
    base_mass = max(total_amount * cfg.transport_mass_fraction, 0.0)
    if not cfg.use_auxiliary_main_flow or cfg.transport_aux_mass_blend <= 0 or "main_net_flow" not in day.columns:
        return base_mass
    flow = pd.to_numeric(day["main_net_flow"], errors="coerce")
    if flow.notna().mean() < 0.5:
        return base_mass
    out_mass = float((-flow.clip(upper=0)).sum())
    in_mass = float(flow.clip(lower=0).sum())
    aux_mass = 0.5 * (out_mass + in_mass)
    if aux_mass <= 0 or base_mass <= 0:
        return base_mass if base_mass > 0 else aux_mass
    aux_mass = float(np.clip(aux_mass, base_mass * 0.25, base_mass * 4.0))
    blend = float(np.clip(cfg.transport_aux_mass_blend, 0.0, 1.0))
    return (1.0 - blend) * base_mass + blend * aux_mass


def build_transport_marginals(day: pd.DataFrame, cfg: Config) -> tuple[pd.Series, pd.Series]:
    supply_share = _normalize_capped(day["capital_supply_weight"], cfg.alpha, cfg.transport_uniform_mix, cfg.transport_max_node_share)
    demand_share = _normalize_capped(day["capital_demand_weight"], cfg.beta, cfg.transport_uniform_mix, cfg.transport_max_node_share)
    mass = _transport_mass(day, cfg)
    return supply_share * mass, demand_share * mass


def gravity_prior(day: pd.DataFrame, distance: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    symbols = day.index.tolist()
    attraction = day["attractiveness"].reindex(symbols).fillna(1.0).clip(lower=1e-12).to_numpy(float)
    d = distance.reindex(index=symbols, columns=symbols).to_numpy(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        log_kernel = cfg.beta * np.log(attraction)[None, :] - cfg.gamma * np.log(d)
    np.fill_diagonal(log_kernel, -np.inf)
    finite = np.isfinite(log_kernel)
    if not finite.any():
        raise ValueError("Gravity 先验没有有效的股票间迁移边")
    temperature = max(float(cfg.transport_temperature), 1e-6)
    max_log = float(np.max(log_kernel[finite]))
    kernel = np.zeros_like(log_kernel, dtype=float)
    kernel[finite] = np.exp((log_kernel[finite] - max_log) / temperature)
    kernel[finite] = np.maximum(kernel[finite], 1e-15)
    np.fill_diagonal(kernel, 0.0)
    return pd.DataFrame(kernel, index=symbols, columns=symbols)


def sinkhorn_transport(prior: pd.DataFrame, supply: pd.Series, demand: pd.Series, cfg: Config) -> pd.DataFrame:
    symbols = prior.index.tolist()
    k = prior.reindex(index=symbols, columns=symbols).to_numpy(float, copy=True)
    a = supply.reindex(symbols).fillna(0).clip(lower=0).to_numpy(float)
    b = demand.reindex(symbols).fillna(0).clip(lower=0).to_numpy(float)
    mass_a = float(a.sum())
    mass_b = float(b.sum())
    if mass_a <= 0 or mass_b <= 0:
        return pd.DataFrame(0.0, index=symbols, columns=symbols)
    b *= mass_a / mass_b
    u = np.ones(len(symbols), dtype=float)
    v = np.ones(len(symbols), dtype=float)
    tiny = 1e-300
    for iteration in range(max(1, cfg.sinkhorn_max_iter)):
        kv = k @ v
        u = np.divide(a, kv, out=np.zeros_like(a), where=kv > tiny)
        ktu = k.T @ u
        v = np.divide(b, ktu, out=np.zeros_like(b), where=ktu > tiny)
        if iteration % 10 == 0 or iteration == cfg.sinkhorn_max_iter - 1:
            flow = (u[:, None] * k) * v[None, :]
            row_err = np.max(np.abs(flow.sum(axis=1) - a)) / mass_a
            col_err = np.max(np.abs(flow.sum(axis=0) - b)) / mass_a
            if max(row_err, col_err) <= cfg.sinkhorn_tol:
                break
    flow = (u[:, None] * k) * v[None, :]
    flow[~np.isfinite(flow)] = 0.0
    np.fill_diagonal(flow, 0.0)
    return pd.DataFrame(flow, index=symbols, columns=symbols)


def optimal_transport_flows(day: pd.DataFrame, distance: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    supply, demand = build_transport_marginals(day, cfg)
    return sinkhorn_transport(gravity_prior(day, distance, cfg), supply, demand, cfg)


def gravity_flows(day: pd.DataFrame, distance: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """向后兼容旧 API；当前实现已升级为 Gravity-prior Optimal Transport。"""
    return optimal_transport_flows(day, distance, cfg)


def build_snapshot(date: pd.Timestamp, features: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = [
        "avg_amount", "momentum_z", "volatility_z", "liquidity_z",
        "turnover_intensity_z", "price_impact_z",
        "capital_supply_weight", "capital_demand_weight",
    ]
    day = features[features["date"] == date].dropna(subset=required).drop_duplicates("symbol").set_index("symbol")
    if len(day) < cfg.min_cross_section:
        raise ValueError("有效横截面不足")
    day = day.copy()
    day["attraction_score"] = attraction_score(day, cfg)
    day["attractiveness"] = np.exp(day["attraction_score"].clip(-4, 4))
    flow = optimal_transport_flows(day, build_distance(date, day, features, cfg), cfg)
    result = day.copy()
    result["inferred_inflow"] = flow.sum(axis=0)
    result["inferred_outflow"] = flow.sum(axis=1)
    result["net_migration"] = result["inferred_inflow"] - result["inferred_outflow"]
    result["migration_pressure"] = result["net_migration"] / result["avg_amount"].replace(0, np.nan)
    total_in = result["inferred_inflow"].sum()
    total_out = result["inferred_outflow"].sum()
    result["inflow_share"] = result["inferred_inflow"] / total_in if total_in > 0 else 0.0
    result["outflow_share"] = result["inferred_outflow"] / total_out if total_out > 0 else 0.0
    return result.sort_values("migration_pressure", ascending=False), flow


def flow_edges(flow: pd.DataFrame, day: pd.DataFrame, top_per_source: int = 3) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for source in flow.index:
        source_total = float(flow.loc[source].sum())
        for target, value in flow.loc[source].sort_values(ascending=False).head(top_per_source).items():
            if value <= 0:
                continue
            target_total = float(flow[target].sum())
            rows.append({
                "source": source,
                "source_name": day.loc[source, "name"],
                "source_sector": day.loc[source, "sector"],
                "target": target,
                "target_name": day.loc[target, "name"],
                "target_sector": day.loc[target, "sector"],
                "inferred_flow": float(value),
                "source_flow_share": float(value / source_total) if source_total > 0 else np.nan,
                "target_flow_share": float(value / target_total) if target_total > 0 else np.nan,
            })
    return pd.DataFrame(rows).sort_values("inferred_flow", ascending=False) if rows else pd.DataFrame()
