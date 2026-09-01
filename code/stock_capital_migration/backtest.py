# -*- coding: utf-8 -*-
"""节点级回测：多周期 Rank IC、Top-N 组合与资本状态消融实验。"""

from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd

from .config import Config, HORIZONS
from .model import build_snapshot


def rank_ic(x: pd.Series, y: pd.Series) -> float:
    pair = pd.concat([x, y], axis=1).dropna()
    if len(pair) < 3:
        return np.nan
    xr = pair.iloc[:, 0].rank()
    yr = pair.iloc[:, 1].rank()
    if xr.nunique() < 2 or yr.nunique() < 2:
        return np.nan
    return float(xr.corr(yr))


def valid_dates(features: pd.DataFrame, cfg: Config) -> pd.Index:
    """核心模型只要求价格/成交生成的供需特征，不再要求 main_net_flow。"""
    valid = features.dropna(subset=[
        "momentum", "volatility", "avg_amount",
        "capital_supply_weight", "capital_demand_weight",
    ])
    counts = valid.groupby("date")["symbol"].nunique()
    return counts[counts >= cfg.min_cross_section].index.sort_values()


def summarize_ic(ic: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    if ic.empty:
        return pd.DataFrame()
    rows = []
    grouper = groups[0] if len(groups) == 1 else groups
    for key, g in ic.groupby(grouper, dropna=False):
        keys = (key,) if len(groups) == 1 else tuple(key)
        values = g["rank_ic"].dropna()
        row = dict(zip(groups, keys))
        row["observations"] = len(values)
        row["mean_rank_ic"] = values.mean()
        row["median_rank_ic"] = values.median()
        row["positive_ratio"] = (values > 0).mean() if len(values) else np.nan
        std = values.std(ddof=1)
        row["ic_std"] = std
        row["ic_ir"] = values.mean() / std if len(values) > 1 and std > 1e-12 else np.nan
        row["t_stat"] = values.mean() / (std / np.sqrt(len(values))) if len(values) > 1 and std > 1e-12 else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values(groups)


def multi_horizon_test(features: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    """测试节点净迁移压力对 1/3/5/10/20 日未来收益的 Rank IC。"""
    rows = []
    predictions = []
    for date in valid_dates(features, cfg):
        try:
            summary, _ = build_snapshot(date, features, cfg)
        except ValueError:
            continue
        day = summary.reset_index()
        predictions.append(day)
        for h in HORIZONS:
            col = f"forward_return_{h}d"
            rows.append({
                "date": date,
                "horizon": h,
                "rank_ic": rank_ic(day["migration_pressure"], day[col]),
                "n": day[["migration_pressure", col]].dropna().shape[0],
            })
    return (pd.concat(predictions, ignore_index=True) if predictions else pd.DataFrame(), pd.DataFrame(rows))


def ablation_definitions(cfg: Config) -> list[dict[str, object]]:
    """节点预测消融；pair 拓扑需 ETF/基金持仓变化等真实 A->B 标签验证。"""
    return [
        {"model": "A_momentum", "kind": "direct", "weights": {"momentum_z": 1.0}},
        {"model": "B_return", "kind": "direct", "weights": {"return_z": 1.0}},
        {"model": "C_return_momentum", "kind": "direct", "weights": {"return_z": 0.5, "momentum_z": 0.5}},
        {"model": "D_activity_state", "kind": "direct", "weights": {
            "return_z": 0.45, "momentum_z": 0.25,
            "turnover_intensity_z": 0.20, "price_impact_z": -0.10,
        }},
        {"model": "E_valuation_state", "kind": "direct", "weights": {
            "return_z": 0.35, "momentum_z": 0.20,
            "turnover_intensity_z": 0.20, "price_impact_z": -0.10,
            "valuation_cheapness_z": 0.15,
        }},
        {"model": "F_capital_state", "kind": "direct", "weights": {"capital_state_score": 1.0}},
        {"model": "G_ot_net_migration", "kind": "transport", "weights": {}},
    ]


def direct_signal(day: pd.DataFrame, weights: Mapping[str, float]) -> pd.Series:
    signal = pd.Series(0.0, index=day.index)
    for col, weight in weights.items():
        if col in day.columns:
            signal = signal + weight * day[col].fillna(0)
    return signal


def portfolio_metrics(returns: pd.Series) -> dict[str, float]:
    r = returns.dropna()
    if r.empty:
        return {"annual_return": np.nan, "annual_volatility": np.nan, "sharpe": np.nan, "max_drawdown": np.nan}
    nav = (1 + r).cumprod()
    years = len(r) / 252
    annual = nav.iloc[-1] ** (1 / years) - 1 if years > 0 and nav.iloc[-1] > 0 else np.nan
    std = r.std(ddof=1)
    sharpe = r.mean() / std * np.sqrt(252) if len(r) > 1 and std > 1e-12 else np.nan
    drawdown = nav / nav.cummax() - 1
    return {
        "annual_return": float(annual),
        "annual_volatility": float(std * np.sqrt(252)),
        "sharpe": float(sharpe),
        "max_drawdown": float(drawdown.min()),
    }


def run_ablation(features: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """A-G 节点信号消融：从动量到资本状态，再到 OT 归一化净迁移。"""
    ic_rows = []
    portfolio_rows = []
    dates = valid_dates(features, cfg)
    required = [
        "avg_amount", "momentum_z", "volatility_z", "return_z",
        "turnover_intensity_z", "price_impact_z",
        "capital_supply_weight", "capital_demand_weight",
    ]

    for definition in ablation_definitions(cfg):
        model = str(definition["model"])
        kind = str(definition["kind"])
        weights = definition["weights"]
        previous: set[str] | None = None

        for date in dates:
            day = features[features["date"] == date].drop_duplicates("symbol").set_index("symbol").dropna(subset=required)
            if len(day) < cfg.min_cross_section:
                continue
            if kind == "direct":
                scored = day.copy()
                scored["signal"] = direct_signal(scored, weights)
            else:
                try:
                    scored, _ = build_snapshot(date, features, cfg)
                except ValueError:
                    continue
                scored["signal"] = scored["migration_pressure"]

            for h in HORIZONS:
                col = f"forward_return_{h}d"
                ic_rows.append({
                    "date": date,
                    "model": model,
                    "horizon": h,
                    "rank_ic": rank_ic(scored["signal"], scored[col]),
                    "n": scored[["signal", col]].dropna().shape[0],
                })

            ranked = scored.sort_values("signal", ascending=False)
            n = min(cfg.top_n, max(1, len(ranked) // 2))
            holdings = set(ranked.head(n).index.astype(str))
            turnover = np.nan if previous is None else 1 - len(previous & holdings) / max(1, n)
            previous = holdings
            top_ret = ranked.head(n)["forward_return_1d"].mean()
            eq_ret = ranked["forward_return_1d"].mean()
            portfolio_rows.append({
                "date": date,
                "model": model,
                "top_n_return": top_ret,
                "equal_weight_return": eq_ret,
                "excess_return": top_ret - eq_ret,
                "turnover": turnover,
            })

    daily_ic = pd.DataFrame(ic_rows)
    portfolio = pd.DataFrame(portfolio_rows)
    summary = summarize_ic(daily_ic, ["model", "horizon"])
    metrics = []
    if not portfolio.empty:
        for model, g in portfolio.groupby("model"):
            metrics.append({
                "model": model,
                **portfolio_metrics(g["top_n_return"]),
                "avg_turnover": g["turnover"].mean(),
                "mean_top_n_return": g["top_n_return"].mean(),
                "mean_excess_return": g["excess_return"].mean(),
            })
    if metrics:
        summary = summary.merge(pd.DataFrame(metrics), on="model", how="left")
    return summary, daily_ic, portfolio
