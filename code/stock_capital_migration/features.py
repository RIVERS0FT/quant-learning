# -*- coding: utf-8 -*-
"""特征工程：价格/成交状态、可选资金流、估值与资本供需特征。"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import Config, HORIZONS, VALUATION_RATIO_COLS


def zscore(s: pd.Series) -> pd.Series:
    std = s.std(skipna=True, ddof=0)
    if pd.isna(std) or std <= 1e-12:
        return pd.Series(0.0, index=s.index)
    return (s - s.mean(skipna=True)) / std


def add_valuation_features(df: pd.DataFrame) -> pd.DataFrame:
    """构造日截面估值标准分与“便宜度”指标。"""
    df = df.copy()
    z_cols: list[str] = []

    for col in VALUATION_RATIO_COLS:
        if col in df.columns:
            raw = pd.to_numeric(df[col], errors="coerce")
        else:
            raw = pd.Series(np.nan, index=df.index)
        positive = raw.where(raw > 0)
        log_col = f"{col}_log"
        z_col = f"{col}_z"
        df[log_col] = np.log1p(positive)
        df[z_col] = df.groupby("date")[log_col].transform(zscore)
        z_cols.append(z_col)

    df["valuation_cheapness_z"] = -df[z_cols].mean(axis=1, skipna=True)
    df["valuation_cheapness_z"] = df["valuation_cheapness_z"].fillna(0.0)
    return df


def _aux_flow_z(day: pd.DataFrame, cfg: Config) -> pd.Series:
    if cfg.use_auxiliary_main_flow and "flow_strength_z" in day.columns:
        return day["flow_strength_z"].fillna(0.0)
    return pd.Series(0.0, index=day.index)


def attraction_score(day: pd.DataFrame, cfg: Config) -> pd.Series:
    """目标股票吸引力；主力资金默认不参与，仅在显式开启时作为辅助项。"""
    flow_z = _aux_flow_z(day, cfg)
    return (
        cfg.attraction_w_momentum * day["momentum_z"].fillna(0)
        + cfg.attraction_w_flow * flow_z
        + cfg.attraction_w_liquidity * day["liquidity_z"].fillna(0)
        + cfg.attraction_w_volatility * day["volatility_z"].fillna(0)
        + cfg.attraction_w_valuation * day["valuation_cheapness_z"].fillna(0)
    )


def capital_supply_score(day: pd.DataFrame, cfg: Config) -> pd.Series:
    """潜在迁出压力 O_i 的无量纲得分。"""
    flow_z = _aux_flow_z(day, cfg)
    return (
        -cfg.supply_w_return * day["return_z"].fillna(0)
        - cfg.supply_w_momentum * day["momentum_z"].fillna(0)
        + cfg.supply_w_turnover * day["turnover_intensity_z"].fillna(0)
        + cfg.supply_w_impact * day["price_impact_z"].fillna(0)
        - cfg.supply_w_aux_flow * flow_z
    )


def capital_demand_score(day: pd.DataFrame, cfg: Config) -> pd.Series:
    """潜在迁入需求 I_j 的无量纲得分。"""
    flow_z = _aux_flow_z(day, cfg)
    return (
        cfg.demand_w_return * day["return_z"].fillna(0)
        + cfg.demand_w_momentum * day["momentum_z"].fillna(0)
        + cfg.demand_w_turnover * day["turnover_intensity_z"].fillna(0)
        - cfg.demand_w_impact * day["price_impact_z"].fillna(0)
        + cfg.demand_w_valuation * day["valuation_cheapness_z"].fillna(0)
        + cfg.demand_w_aux_flow * flow_z
    )


def add_features(data: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    df0 = data.copy()
    if "main_net_flow" not in df0.columns:
        df0["main_net_flow"] = np.nan

    def per_symbol(g: pd.DataFrame) -> pd.DataFrame:
        g = g.copy().sort_values("date")
        g["return_1d"] = g["close"].pct_change()
        g["momentum"] = g["close"].pct_change(cfg.momentum_window)
        g["volatility"] = (
            g["return_1d"].rolling(cfg.volatility_window).std() * np.sqrt(252)
        )
        g["avg_amount"] = g["amount"].rolling(cfg.liquidity_window).mean()
        g["liquidity"] = np.log1p(g["avg_amount"].clip(lower=0))
        g["turnover_intensity"] = (
            g["amount"] / g["avg_amount"].replace(0, np.nan)
        ).clip(lower=0, upper=10)
        g["price_impact"] = (
            g["return_1d"].abs()
            / g["turnover_intensity"].clip(lower=0.05)
        )
        g["flow_ratio"] = (
            g["main_net_flow"] / g["amount"].replace(0, np.nan)
        )
        g["flow_strength"] = g["flow_ratio"].rolling(cfg.flow_window).mean()
        return g

    parts = [per_symbol(g) for _, g in df0.groupby("symbol", sort=False)]
    df = pd.concat(parts, ignore_index=True)

    cross_section_cols = [
        "return_1d",
        "momentum",
        "volatility",
        "liquidity",
        "turnover_intensity",
        "price_impact",
        "flow_strength",
    ]
    for col in cross_section_cols:
        z_name = "return_z" if col == "return_1d" else f"{col}_z"
        df[z_name] = df.groupby("date")[col].transform(zscore)

    df = add_valuation_features(df)

    df["capital_supply_score"] = capital_supply_score(df, cfg)
    df["capital_demand_score"] = capital_demand_score(df, cfg)
    df["capital_state_score"] = (
        df["capital_demand_score"] - df["capital_supply_score"]
    )
    # softplus 把任意实数分数映射到正数，作为 OT 边际的相对权重。
    df["capital_supply_weight"] = np.logaddexp(
        0.0, df["capital_supply_score"].clip(-8, 8)
    )
    df["capital_demand_weight"] = np.logaddexp(
        0.0, df["capital_demand_score"].clip(-8, 8)
    )

    score = attraction_score(df, cfg)
    df["attraction_score"] = score
    df["attractiveness"] = np.exp(score.clip(-4, 4))
    return df


def add_forward_returns(features: pd.DataFrame) -> pd.DataFrame:
    """未来 h 个交易日收益：P[t+h]/P[t]-1。"""
    df = features.copy().sort_values(["symbol", "date"])
    grouped = df.groupby("symbol", group_keys=False)
    for h in HORIZONS:
        df[f"forward_return_{h}d"] = grouped["close"].transform(
            lambda s, h=h: s.shift(-h) / s - 1.0
        )
    return df
