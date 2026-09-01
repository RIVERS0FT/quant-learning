from __future__ import annotations

import numpy as np
import pandas as pd

from .config import HierarchicalConfig


def sigmoid(values):
    arr = np.clip(np.asarray(values, dtype=float), -30.0, 30.0)
    out = 1.0 / (1.0 + np.exp(-arr))
    return pd.Series(out, index=values.index) if isinstance(values, pd.Series) else out


def zscore(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    std = s.std(ddof=0, skipna=True)
    if pd.isna(std) or std <= 1e-12:
        return pd.Series(0.0, index=s.index)
    return (s - s.mean(skipna=True)) / std


def validate_input(df: pd.DataFrame) -> None:
    required = {"date", "symbol", "market", "sector", "close", "amount"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"输入缺少字段: {missing}")


def prepare_panel(raw: pd.DataFrame, cfg: HierarchicalConfig) -> pd.DataFrame:
    """构造 CN/US 统一历史面板。capital_supply/demand 若存在则优先使用。"""
    validate_input(raw)
    df = raw.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["symbol", "market", "sector"]:
        df[col] = df[col].astype(str)
    df = df.dropna(subset=["date", "symbol", "market", "sector"])
    df = df.sort_values(["market", "symbol", "date"]).reset_index(drop=True)

    numeric = [
        "close", "amount", "amount_base", "fx_to_base", "pe_ttm", "pb",
        "ps_ttm", "capital_supply", "capital_demand",
    ]
    for col in numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "amount_base" not in df.columns:
        fx = df["fx_to_base"].fillna(1.0) if "fx_to_base" in df.columns else 1.0
        df["amount_base"] = df["amount"] * fx

    def per_stock(g: pd.DataFrame) -> pd.DataFrame:
        g = g.copy().sort_values("date")
        g["return_1d"] = g["close"].pct_change()
        g["momentum"] = g["close"].pct_change(cfg.momentum_window)
        g["volatility"] = (
            g["return_1d"].rolling(cfg.volatility_window).std()
            * np.sqrt(252.0)
        )
        g["avg_amount_base"] = (
            g["amount_base"].rolling(cfg.liquidity_window).mean()
        )
        g["liquidity"] = np.log1p(g["avg_amount_base"].clip(lower=0.0))
        g["history_count"] = np.arange(1, len(g) + 1)
        return g

    df = pd.concat(
        [
            per_stock(g)
            for _, g in df.groupby(["market", "symbol"], sort=False)
        ],
        ignore_index=True,
    )

    group = df.groupby(["date", "market"])
    for col in ["return_1d", "momentum", "volatility", "liquidity"]:
        df[f"{col}_z"] = group[col].transform(zscore)

    valuation_z = []
    for col in ["pe_ttm", "pb", "ps_ttm"]:
        if col not in df.columns:
            continue
        positive = df[col].where(df[col] > 0)
        z_col = f"{col}_z"
        log_values = np.log1p(positive)
        df[z_col] = log_values.groupby(
            [df["date"], df["market"]]
        ).transform(zscore)
        valuation_z.append(z_col)

    df["valuation_cheapness_z"] = (
        -df[valuation_z].mean(axis=1, skipna=True)
        if valuation_z
        else 0.0
    )
    df["valuation_cheapness_z"] = pd.Series(
        df["valuation_cheapness_z"], index=df.index
    ).fillna(0.0)

    supply_score = (
        cfg.supply_w_negative_return * -df["return_1d_z"].fillna(0.0)
        + cfg.supply_w_volatility * df["volatility_z"].fillna(0.0)
        + cfg.supply_w_negative_momentum * -df["momentum_z"].fillna(0.0)
    )
    demand_score = (
        cfg.demand_w_return * df["return_1d_z"].fillna(0.0)
        + cfg.demand_w_momentum * df["momentum_z"].fillna(0.0)
        + cfg.demand_w_liquidity * df["liquidity_z"].fillna(0.0)
        + cfg.demand_w_valuation * df["valuation_cheapness_z"].fillna(0.0)
    )
    df["supply_score"] = supply_score
    df["demand_score"] = demand_score
    df["stock_attractiveness"] = np.exp(demand_score.clip(-4.0, 4.0))

    inferred_supply = (
        df["avg_amount_base"].clip(lower=0.0)
        * cfg.inferred_supply_fraction
        * sigmoid(supply_score)
    )
    inferred_demand = (
        df["avg_amount_base"].clip(lower=0.0)
        * cfg.inferred_demand_fraction
        * sigmoid(demand_score)
    )

    if "capital_supply" in raw.columns:
        df["capital_supply"] = df["capital_supply"].where(
            df["capital_supply"].notna(), inferred_supply
        )
    else:
        df["capital_supply"] = inferred_supply
    if "capital_demand" in raw.columns:
        df["capital_demand"] = df["capital_demand"].where(
            df["capital_demand"].notna(), inferred_demand
        )
    else:
        df["capital_demand"] = inferred_demand

    df["capital_supply"] = df["capital_supply"].clip(lower=0.0)
    df["capital_demand"] = df["capital_demand"].clip(lower=0.0)
    return df


def latest_snapshot(
    panel: pd.DataFrame,
    date,
    cfg: HierarchicalConfig,
) -> pd.DataFrame:
    target = pd.to_datetime(date) if date is not None else panel["date"].max()
    out = panel[
        (panel["date"] == target)
        & (panel["history_count"] >= cfg.min_history)
    ].copy()
    required = [
        "capital_supply",
        "capital_demand",
        "return_1d_z",
        "momentum_z",
        "volatility_z",
        "liquidity_z",
    ]
    out = out.dropna(subset=required).reset_index(drop=True)
    if out.empty:
        raise ValueError(f"{target.date()} 没有足够有效的股票状态")
    out["stock_id"] = np.arange(len(out), dtype=np.int32)
    return out
