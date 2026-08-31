# -*- coding: utf-8 -*-
"""结果输出：CSV/图像落盘与终端摘要。"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_results(
    raw: pd.DataFrame,
    latest: pd.DataFrame,
    edges: pd.DataFrame,
    predictions: pd.DataFrame,
    ic_df: pd.DataFrame,
    portfolio: pd.DataFrame,
    no_plot: bool,
    output_dir: Path,
) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    latest.reset_index().to_csv(
        out / "stock_capital_migration_snapshot.csv",
        index=False,
        encoding="utf-8-sig",
    )
    edges.to_csv(
        out / "stock_capital_migration_edges.csv",
        index=False,
        encoding="utf-8-sig",
    )
    predictions.to_csv(
        out / "stock_capital_migration_backtest.csv",
        index=False,
        encoding="utf-8-sig",
    )
    ic_df.to_csv(
        out / "stock_capital_migration_ic.csv",
        index=False,
        encoding="utf-8-sig",
    )

    valuation_cols = [
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
    existing = [
        c for c in valuation_cols if c in raw.columns
    ]
    raw[existing].to_csv(
        out / "stock_capital_migration_valuation.csv",
        index=False,
        encoding="utf-8-sig",
    )

    if not no_plot and not portfolio.empty:
        ax = portfolio.plot(
            x="date",
            y=[
                "top_n_return_nav",
                "equal_weight_return_nav",
            ],
            figsize=(12, 6),
            grid=True,
            title=(
                "Stock Capital Migration: "
                "Top-N vs Equal Weight"
            ),
        )
        ax.set_ylabel("NAV")
        ax.legend(
            ["Migration Top-N", "Equal Weight"]
        )
        plt.tight_layout()
        plt.savefig(
            out / "stock_capital_migration_nav.png",
            dpi=150,
        )
        plt.close()


def print_summary(
    date: pd.Timestamp,
    latest: pd.DataFrame,
    edges: pd.DataFrame,
    ic_df: pd.DataFrame,
    portfolio: pd.DataFrame,
    top_n: int,
) -> None:
    print(
        f"\n========== 股票资本迁移模型："
        f"{date.date()} =========="
    )

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
            top_edges[
                [
                    "source_name",
                    "target_name",
                    "inferred_flow",
                ]
            ]
            .rename(
                columns={
                    "inferred_flow": "推断迁移(亿)"
                }
            )
            .to_string(index=False)
        )

    if not ic_df.empty:
        print(
            f"\n平均 Rank IC："
            f"{ic_df['rank_ic'].mean():.4f}"
        )
        print(
            "Rank IC > 0 占比："
            f"{(ic_df['rank_ic'] > 0).mean():.2%}"
        )

    if not portfolio.empty:
        top_nav = portfolio[
            "top_n_return_nav"
        ].iloc[-1]
        eq_nav = portfolio[
            "equal_weight_return_nav"
        ].iloc[-1]
        print(f"Top-{top_n} 净值：{top_nav:.4f}")
        print(f"等权净值：{eq_nav:.4f}")
        print(f"相对净值：{top_nav / eq_nav:.4f}")
