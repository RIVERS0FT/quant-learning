# -*- coding: utf-8 -*-
"""回测：Rank IC 与 Top-N 组合收益。"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import Config
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


def backtest(
    features: pd.DataFrame,
    cfg: Config,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    valid = features.dropna(
        subset=[
            "main_net_flow",
            "flow_strength",
            "momentum",
            "volatility",
            "avg_amount",
            "next_return",
        ]
    )
    counts = valid.groupby("date")["symbol"].nunique()
    dates = counts[
        counts >= cfg.min_cross_section
    ].index.sort_values()

    predictions: list[pd.DataFrame] = []
    ic_rows: list[dict[str, object]] = []
    portfolio_rows: list[dict[str, object]] = []

    for date in dates:
        try:
            summary, _ = build_snapshot(
                date,
                features,
                cfg,
            )
        except ValueError:
            continue

        day = summary.reset_index()
        predictions.append(day)
        ic_rows.append(
            {
                "date": date,
                "rank_ic": rank_ic(
                    day["migration_pressure"],
                    day["next_return"],
                ),
                "n": len(day),
            }
        )

        ranked = day.sort_values(
            "migration_pressure",
            ascending=False,
        )
        n = min(
            cfg.top_n,
            max(1, len(ranked) // 2),
        )
        top_ret = ranked.head(n)["next_return"].mean()
        bottom_ret = ranked.tail(n)["next_return"].mean()
        portfolio_rows.append(
            {
                "date": date,
                "top_n_return": top_ret,
                "bottom_n_return": bottom_ret,
                "long_short_return": (
                    top_ret - bottom_ret
                ),
                "equal_weight_return": (
                    ranked["next_return"].mean()
                ),
            }
        )

    pred_df = (
        pd.concat(predictions, ignore_index=True)
        if predictions
        else pd.DataFrame()
    )
    ic_df = pd.DataFrame(ic_rows)
    portfolio = pd.DataFrame(portfolio_rows)

    if not portfolio.empty:
        cols = [
            "top_n_return",
            "bottom_n_return",
            "long_short_return",
            "equal_weight_return",
        ]
        for col in cols:
            portfolio[f"{col}_nav"] = (
                1 + portfolio[col].fillna(0)
            ).cumprod()

    return pred_df, ic_df, portfolio
