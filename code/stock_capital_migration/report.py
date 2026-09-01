# -*- coding: utf-8 -*-
"""结果输出：完整迁移矩阵、关键边、节点快照、回测与摘要。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .backtest import summarize_ic


VALUATION_REPORT_COLS = [
    "date", "symbol", "name", "sector", "valuation_date", "valuation_age_days",
    "pe_ttm", "pb", "ps_ttm", "total_market_cap", "float_market_cap",
]


def _to_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, encoding="utf-8-sig")


def save_results(
    raw: pd.DataFrame,
    latest: pd.DataFrame,
    flow_matrix: pd.DataFrame,
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

    _to_csv(latest.reset_index(), out / "stock_capital_migration_snapshot.csv")
    matrix = flow_matrix.copy()
    matrix.index.name = "source"
    _to_csv(matrix.reset_index(), out / "stock_capital_migration_matrix.csv")
    _to_csv(edges, out / "stock_capital_migration_edges.csv")

    _to_csv(predictions, out / "stock_capital_migration_predictions.csv")
    _to_csv(multi_ic, out / "stock_capital_migration_multi_ic.csv")
    _to_csv(summarize_ic(multi_ic, ["horizon"]), out / "stock_capital_migration_multi_ic_summary.csv")

    _to_csv(ablation, out / "stock_capital_migration_ablation.csv")
    _to_csv(ablation_daily, out / "stock_capital_migration_ablation_daily_ic.csv")
    _to_csv(ablation_portfolio, out / "stock_capital_migration_ablation_portfolio.csv")

    existing = [c for c in VALUATION_REPORT_COLS if c in raw.columns]
    _to_csv(raw[existing], out / "stock_capital_migration_valuation.csv")

    grouped = raw.groupby("symbol")
    coverage = grouped.agg(
        first_date=("date", "min"),
        last_date=("date", "max"),
        price_rows=("date", "size"),
    ).reset_index()
    if "main_net_flow" in raw.columns:
        flow_rows = grouped["main_net_flow"].count()
        coverage["flow_rows"] = coverage["symbol"].map(flow_rows).fillna(0).astype(int)
    else:
        coverage["flow_rows"] = 0
    if "valuation_date" in raw.columns:
        val_rows = grouped["valuation_date"].count()
        coverage["valuation_rows"] = coverage["symbol"].map(val_rows).fillna(0).astype(int)
    else:
        coverage["valuation_rows"] = 0
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
        "name", "sector", "capital_supply_score", "capital_demand_score",
        "capital_state_score", "pe_ttm", "pb", "valuation_cheapness_z",
        "inferred_outflow", "inferred_inflow", "net_migration", "migration_pressure",
    ]
    if "main_net_flow" in latest.columns and latest["main_net_flow"].notna().any():
        cols.insert(2, "main_net_flow")
    cols = [c for c in cols if c in latest.columns]
    view = latest[cols].copy()

    for col in ["main_net_flow", "inferred_outflow", "inferred_inflow", "net_migration"]:
        if col in view.columns:
            view[col] /= 1e8

    print("\n资本供需与净迁移排名：")
    print(view.rename(columns={
        "main_net_flow": "主力净流入(亿,辅助)",
        "capital_supply_score": "迁出压力",
        "capital_demand_score": "迁入需求",
        "capital_state_score": "资本状态",
        "pe_ttm": "PE(TTM)",
        "pb": "PB",
        "valuation_cheapness_z": "估值便宜度Z",
        "inferred_outflow": "推断流出(亿)",
        "inferred_inflow": "推断流入(亿)",
        "net_migration": "净迁移(亿)",
    }).to_string())

    if not edges.empty:
        top_edges = edges.head(12).copy()
        top_edges["inferred_flow"] /= 1e8
        print("\n最大股票→股票推断迁移路径：")
        print(top_edges[[
            "source_name", "target_name", "inferred_flow",
            "source_flow_share", "target_flow_share",
        ]].rename(columns={
            "inferred_flow": "推断迁移(亿)",
            "source_flow_share": "源资金占比",
            "target_flow_share": "目标流入占比",
        }).to_string(index=False))

    print("\n多周期 Rank IC（节点净迁移，不等同于 pair 拓扑验证）：")
    print(summarize_ic(multi_ic, ["horizon"]).to_string(index=False))

    if not ablation.empty:
        cols = [
            "model", "mean_rank_ic", "positive_ratio", "sharpe",
            "max_drawdown", "avg_turnover", "mean_excess_return",
        ]
        print("\n节点信号消融实验（1日）：")
        print(ablation[ablation["horizon"] == 1][cols].to_string(index=False))
