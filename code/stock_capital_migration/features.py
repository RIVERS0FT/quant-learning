# -*- coding: utf-8 -*-
"""特征工程：动量/波动/流动性/资金流强度与估值标准分。"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import Config, VALUATION_RATIO_COLS


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
        raw = pd.to_numeric(df.get(col), errors="coerce")
        # PE/PB/PS 非正值不适合直接作为常规估值倍数比较。
        positive = raw.where(raw > 0)
        log_col = f"{col}_log"
        z_col = f"{col}_z"
        df[log_col] = np.log1p(positive)
        df[z_col] = df.groupby("date")[log_col].transform(zscore)
        z_cols.append(z_col)

    # 越低估值 -> 越高 cheapness。缺失指标按横截面中性值 0 处理。
    df["valuation_cheapness_z"] = -df[z_cols].mean(axis=1, skipna=True)
    df["valuation_cheapness_z"] = df["valuation_cheapness_z"].fillna(0.0)
    return df


def add_features(data: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    def per_symbol(g: pd.DataFrame) -> pd.DataFrame:
        g = g.copy().sort_values("date")
        g["return_1d"] = g["close"].pct_change()
        g["next_return"] = g["close"].shift(-1) / g["close"] - 1.0
        g["momentum"] = g["close"].pct_change(cfg.momentum_window)
        g["volatility"] = (
            g["return_1d"]
            .rolling(cfg.volatility_window)
            .std()
            * np.sqrt(252)
        )
        g["avg_amount"] = g["amount"].rolling(cfg.liquidity_window).mean()
        g["liquidity"] = np.log1p(g["avg_amount"].clip(lower=0))
        g["flow_ratio"] = (
            g["main_net_flow"] / g["amount"].replace(0, np.nan)
        )
        g["flow_strength"] = (
            g["flow_ratio"].rolling(cfg.flow_window).mean()
        )
        return g

    parts = [
        per_symbol(g)
        for _, g in data.groupby("symbol", sort=False)
    ]
    df = pd.concat(parts, ignore_index=True)

    for col in ["momentum", "volatility", "liquidity", "flow_strength"]:
        df[f"{col}_z"] = df.groupby("date")[col].transform(zscore)

    df = add_valuation_features(df)

    score = (
        cfg.attraction_w_momentum * df["momentum_z"]
        + cfg.attraction_w_flow * df["flow_strength_z"]
        + cfg.attraction_w_liquidity * df["liquidity_z"]
        + cfg.attraction_w_volatility * df["volatility_z"]
        + cfg.attraction_w_valuation * df["valuation_cheapness_z"]
    )
    df["attraction_score"] = score
    df["attractiveness"] = np.exp(score.clip(-4, 4))
    df["outflow_budget"] = (
        (-df["main_net_flow"]).clip(lower=0).fillna(0.0)
    )
    return df
