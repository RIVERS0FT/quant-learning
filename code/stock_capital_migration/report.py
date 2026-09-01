# -*- coding: utf-8 -*-
"""结果输出：CSV 落盘与终端摘要。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .backtest import summarize_ic


VALUATION_REPORT_COLS = [
    "date",
    "symbol",
    "name",
    "sector",
    "valuation_date",
    "valuation_age_days",
    "pe_ttm",
    "pb",
    "ps_ttm",
    "total_market_cap",
    "float_market_cap",
]


def _to_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, encoding="utf-8-sig")


def save_results(
    raw: pd.DataFrame,
    latest: pd.DataFrame,
    edges: pd.DataFrame,
    predictions: pd.DataFrame,
    multi_ic: pd.DataFrame,
    ablation: pd.DataFrame,
    ablation_daily: pd.DataFrame,
    ablation_portfolio: pd.DataFrame,
    output_dir: Path,
) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # 最新截面与推断迁移路径。
    _to_csv(latest.reset_index(), out / "stock_capital_migration_snapshot.csv")
    _to_csv(edges, out / "stock_capital_migration_edges.csv")

    # 多周期 Rank IC 与逐日预测。
    _to_csv(predictions, out / "stock_capital_migration_predictions.csv")
    _to_csv(multi_ic, out / "stock_capital_migration_multi_ic.csv")
    _to_csv(
        summarize_ic(multi_ic, ["horizon"]),
        out / "stock_capital_migration_multi_ic_summary.csv",
    )

    # A-G 消融实验。
    _to_csv(ablation, out / "stock_capital_migration_ablation.csv")
    _to_csv(ablation_daily, out / "stock_capital_migration_ablation_daily_ic.csv")
    _to_csv(ablation_portfolio, out / "stock_capital_migration_ablation_portfolio.csv")

    # 估值明细与数据覆盖度。
    existing = [c for c in VALUATION_REPORT_COLS if c in raw.columns]
    _to_csv(raw[existing], out / "stock_capital_migration_valuation.csv")

    coverage = (
        raw.groupby("symbol")
        .agg(
            first_date=("date", "min"),
            last_date=("date", "max"),
            price_rows=("date", "size"),
            flow_rows=("main_net_flow", "count"),
        )
        .reset_index()
    )
    coverage["valuation_rows"] = (
        raw.groupby("symbol")["valuation_date"].count()
        if "valuation_date" in raw.columns
        else 0
    )
    coverage["valuation_rows"] = coverage["valuation_rows"].reindex(
        coverage.index, fill_value=0
    )
    _to_csv(coverage, out / "stock_capital_migration_data_coverage.csv")


def print_summary(
    date: pd.Timestamp,
    latest: pd.DataFrame,
    edges: pd.DataFrame,
    multi_ic: pd.DataFrame,
    ablation: pd.DataFrame,
    data_dir: Path,
) -> None:
    print(f"\n========== 股票资本迁移模型：{date.date()} ==========")
    print(f"\n数据缓存目录：{data_dir}")

    cols = [
        "name",
        "sector",
        "main_net_flow",
        "pe_ttm",
        "pb",
        "ps_ttm",
        "valuation_cheapness_z",
        "attractiveness",
        "net_migration",
        "migration_pressure",
    ]
    cols = [c for c in cols if c in latest.columns]
    view = latest[cols].copy()

    if "main_net_flow" in view.columns:
        view["main_net_flow"] /= 1e8
    if "net_migration" in view.columns:
        view["net_migration"] /= 1e8

    print("\n迁移压力排名：")
    print(
        view.rename(
            columns={
                "main_net_flow": "主力净流入(亿)",
                "pe_ttm": "PE(TTM)",
                "pb": "PB",
                "ps_ttm": "PS(TTM)",
                "valuation_cheapness_z": "估值便宜度Z",
                "net_migration": "净迁移(亿)",
            }
        ).to_string()
    )

    if not edges.empty:
        top_edges = edges.head(12).copy()
        top_edges["inferred_flow"] /= 1e8
        print("\n最大推断迁移路径：")
        print(
            top_edges[["source_name", "target_name", "inferred_flow"]]
            .rename(columns={"inferred_flow": "推断迁移(亿)"})
            .to_string(index=False)
        )

    print("\n多周期 Rank IC：")
    print(summarize_ic(multi_ic, ["horizon"]).to_string(index=False))

    if not ablation.empty:
        cols = [
            "model",
            "mean_rank_ic",
            "positive_ratio",
            "sharpe",
            "max_drawdown",
            "avg_turnover",
            "mean_excess_return",
        ]
        print("\n消融实验（1日）：")
        print(ablation[ablation["horizon"] == 1][cols].to_string(index=False))
