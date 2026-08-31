# -*- coding: utf-8 -*-
"""命令行入口。"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .backtest import backtest
from .config import Config, DEFAULT_OUTPUT_DIR, DEFAULT_UNIVERSE
from .data import load_data
from .features import add_features
from .model import build_snapshot, flow_edges
from .report import print_summary, save_results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stock Capital Migration Model"
    )
    parser.add_argument(
        "--start-date",
        default=(
            pd.Timestamp.today()
            - pd.DateOffset(years=2)
        ).strftime("%Y%m%d"),
    )
    parser.add_argument(
        "--end-date",
        default=pd.Timestamp.today().strftime("%Y%m%d"),
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=(
            "结果输出目录"
            f"（默认：{DEFAULT_OUTPUT_DIR}，"
            "整个目录已被 .gitignore 排除）"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = Config(top_n=max(1, args.top_n))

    raw = load_data(
        DEFAULT_UNIVERSE,
        args.start_date,
        args.end_date,
        cfg,
    )
    features = add_features(raw, cfg)

    valid = features.dropna(
        subset=[
            "main_net_flow",
            "flow_strength",
            "momentum",
            "volatility",
            "avg_amount",
        ]
    )
    counts = valid.groupby("date")["symbol"].nunique()
    valid_dates = counts[
        counts >= cfg.min_cross_section
    ].index.sort_values()
    if len(valid_dates) == 0:
        raise RuntimeError("没有足够完整的资金流截面")

    latest_date = valid_dates[-1]
    latest, flow = build_snapshot(
        latest_date,
        features,
        cfg,
    )
    day = (
        features[
            features["date"] == latest_date
        ]
        .drop_duplicates("symbol")
        .set_index("symbol")
    )
    edges = flow_edges(flow, day)
    predictions, ic_df, portfolio = backtest(
        features,
        cfg,
    )

    save_results(
        raw,
        latest,
        edges,
        predictions,
        ic_df,
        portfolio,
        args.no_plot,
        args.output_dir,
    )
    print_summary(
        latest_date,
        latest,
        edges,
        ic_df,
        portfolio,
        cfg.top_n,
    )


if __name__ == "__main__":
    main()
