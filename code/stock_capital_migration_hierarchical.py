# -*- coding: utf-8 -*-
"""Market -> Sector -> Stock 分层稀疏资本迁移模型 V2。

输入最少需要: date,symbol,market,sector,close,amount。
CN/US 的 amount 必须先通过 fx_to_base 或 amount_base 统一到同一货币。
capital_supply/capital_demand 可选；缺失时由价格、波动、流动性、估值代理推断。

本模型不会创建全市场 N×N 稠密矩阵。行业层只保留 Top-K 目标行业，
个股层只在这些行业对内部计算 Top-K 股票边，并用整数 stock_id 保存边。

运行：
    python code/stock_capital_migration_hierarchical.py --demo
    python code/stock_capital_migration_hierarchical.py --input unified_panel.csv
    python code/stock_capital_migration_hierarchical.py --input unified_panel.csv --date 2026-09-01
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from hierarchical_migration import (
    HierarchicalConfig,
    prepare_panel,
    run_hierarchy,
)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = (
    BASE_DIR / "outputs" / "hierarchical_migration"
)


def make_demo_panel(
    days: int = 90,
    seed: int = 7,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(
        end=pd.Timestamp.today().normalize(),
        periods=days,
    )
    sectors = [
        "Semiconductor",
        "Software",
        "Financial",
        "Consumer",
    ]
    specs = {
        "CN": {
            "prefix": "CN",
            "n": 8,
            "price": 50.0,
            "amount": 2e9,
            "fx": 1.0,
        },
        "US": {
            "prefix": "US",
            "n": 8,
            "price": 100.0,
            "amount": 8e9,
            "fx": 7.2,
        },
    }
    rows = []
    global_shock = rng.normal(0, 0.004, len(dates))
    sector_shock = {
        sector: rng.normal(0, 0.008, len(dates))
        for sector in sectors
    }

    for market, spec in specs.items():
        market_shock = rng.normal(0, 0.005, len(dates))
        for sector in sectors:
            for i in range(spec["n"]):
                symbol = (
                    f"{spec['prefix']}_"
                    f"{sector[:3].upper()}_{i:02d}"
                )
                returns = (
                    global_shock
                    + market_shock
                    + sector_shock[sector]
                    + rng.normal(0, 0.012, len(dates))
                )
                close = spec["price"] * np.exp(
                    np.cumsum(returns)
                )
                amount = spec["amount"] * np.exp(
                    rng.normal(0, 0.25, len(dates))
                )
                pe = np.clip(
                    20
                    + rng.normal(0, 4, len(dates))
                    + (5 if sector == "Software" else 0),
                    3,
                    None,
                )
                pb = np.clip(
                    3 + rng.normal(0, 0.6, len(dates)),
                    0.4,
                    None,
                )
                ps = np.clip(
                    4 + rng.normal(0, 0.8, len(dates)),
                    0.3,
                    None,
                )

                for date, price, turnover, pe_v, pb_v, ps_v in zip(
                    dates,
                    close,
                    amount,
                    pe,
                    pb,
                    ps,
                ):
                    rows.append(
                        {
                            "date": date,
                            "symbol": symbol,
                            "name": symbol,
                            "market": market,
                            "sector": sector,
                            "close": price,
                            "amount": turnover,
                            "fx_to_base": spec["fx"],
                            "pe_ttm": pe_v,
                            "pb": pb_v,
                            "ps_ttm": ps_v,
                        }
                    )
    return pd.DataFrame(rows)


def save_results(
    results: dict[str, pd.DataFrame],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in results.items():
        frame.to_csv(
            output_dir / f"hierarchical_{name}.csv",
            index=False,
            encoding="utf-8-sig",
        )


def print_summary(
    results: dict[str, pd.DataFrame],
    cfg: HierarchicalConfig,
) -> None:
    print("\n========== Market -> Sector -> Stock ==========")
    print(f"Market edges: {len(results['market_edges']):,}")
    print(f"Sector edges: {len(results['sector_edges']):,}")
    print(f"Stock edges : {len(results['stock_edges']):,}")
    print(
        f"sector_top_k={cfg.sector_top_k}, "
        f"stock_top_k={cfg.stock_top_k}"
    )

    market_edges = results["market_edges"]
    if not market_edges.empty:
        print("\n市场层：")
        print(
            market_edges[
                [
                    "source_market",
                    "target_market",
                    "probability",
                    "flow",
                ]
            ]
            .sort_values("flow", ascending=False)
            .to_string(index=False)
        )

    sector_edges = results["sector_edges"]
    if not sector_edges.empty:
        print("\n行业层 Top 12：")
        print(
            sector_edges[
                [
                    "source_market",
                    "source_sector",
                    "target_market",
                    "target_sector",
                    "flow",
                ]
            ]
            .nlargest(12, "flow")
            .to_string(index=False)
        )

    stock_edges = results["stock_edges"]
    if not stock_edges.empty:
        nodes = results["snapshot"][
            ["stock_id", "symbol", "sector"]
        ]
        source_nodes = nodes.rename(
            columns={
                "stock_id": "source_stock_id",
                "symbol": "source_symbol",
                "sector": "source_sector",
            }
        )
        target_nodes = nodes.rename(
            columns={
                "stock_id": "target_stock_id",
                "symbol": "target_symbol",
                "sector": "target_sector",
            }
        )
        top = (
            stock_edges.nlargest(20, "flow")
            .merge(source_nodes, on="source_stock_id")
            .merge(target_nodes, on="target_stock_id")
        )
        print("\n个股层 Top 20：")
        print(
            top[
                [
                    "source_symbol",
                    "target_symbol",
                    "source_sector",
                    "target_sector",
                    "flow",
                ]
            ].to_string(index=False)
        )

    print("\n净迁移压力 Top 10：")
    print(
        results["stock_state"][
            [
                "market",
                "sector",
                "symbol",
                "net_migration",
                "migration_pressure",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    conservation = results["conservation"]
    print(
        "\n资金守恒最大绝对误差: "
        f"{conservation['absolute_error'].max():.6g}"
    )
    print(
        "资金守恒最大相对误差: "
        f"{conservation['relative_error'].dropna().max():.6g}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hierarchical Sparse Capital Migration Model"
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="统一 CN/US 历史面板 CSV",
    )
    parser.add_argument(
        "--date",
        help="截面日期 YYYY-MM-DD，默认最新",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )
    parser.add_argument(
        "--sector-top-k",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--stock-top-k",
        type=int,
        default=30,
    )
    parser.add_argument(
        "--include-outside",
        action="store_true",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = HierarchicalConfig(
        sector_top_k=max(1, args.sector_top_k),
        stock_top_k=max(1, args.stock_top_k),
        include_outside=args.include_outside,
    )

    if args.demo:
        raw = make_demo_panel()
    elif args.input:
        raw = pd.read_csv(args.input)
    else:
        raise SystemExit("请提供 --input <csv>，或使用 --demo")

    results = run_hierarchy(
        prepare_panel(raw, cfg),
        cfg,
        args.date,
    )
    save_results(results, args.output_dir)
    print_summary(results, cfg)
    print(f"\n输出目录: {args.output_dir}")


if __name__ == "__main__":
    main()
