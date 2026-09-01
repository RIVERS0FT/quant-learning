# -*- coding: utf-8 -*-
"""命令行入口。"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .backtest import multi_horizon_test, run_ablation, valid_dates
from .config import Config, DEFAULT_DATA_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_UNIVERSE
from .data import load_data
from .features import add_features, add_forward_returns
from .model import build_snapshot, flow_edges
from .report import print_summary, save_results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stock Capital Migration Model")
    parser.add_argument(
        "--start-date",
        default=(pd.Timestamp.today() - pd.DateOffset(years=2)).strftime("%Y%m%d"),
    )
    parser.add_argument("--end-date", default=pd.Timestamp.today().strftime("%Y%m%d"))
    parser.add_argument("--top-n", type=int, default=3)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=(
            "本地市场数据缓存目录"
            f"（默认：{DEFAULT_DATA_DIR}，整个目录已被 .gitignore 排除）"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=(
            "结果输出目录"
            f"（默认：{DEFAULT_OUTPUT_DIR}，整个目录已被 .gitignore 排除）"
        ),
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="只使用本地缓存，不发起任何网络请求",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="忽略缓存已有时间范围，强制重拉行情与估值",
    )
    parser.add_argument(
        "--skip-ablation",
        action="store_true",
        help="跳过 A-G 因子消融实验",
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
        args.data_dir,
        args.offline,
        args.refresh_cache,
    )
    features = add_forward_returns(add_features(raw, cfg))
    predictions, multi_ic = multi_horizon_test(features, cfg)

    dates = valid_dates(features, cfg)
    if len(dates) == 0:
        raise RuntimeError("没有足够完整的资金流截面")
    latest_date = dates[-1]
    latest, flow = build_snapshot(latest_date, features, cfg)
    edges = flow_edges(flow, latest)

    if args.skip_ablation:
        ablation = pd.DataFrame()
        ablation_daily = pd.DataFrame()
        ablation_portfolio = pd.DataFrame()
    else:
        ablation, ablation_daily, ablation_portfolio = run_ablation(features, cfg)

    save_results(
        raw,
        latest,
        edges,
        predictions,
        multi_ic,
        ablation,
        ablation_daily,
        ablation_portfolio,
        args.output_dir,
    )
    print_summary(
        latest_date,
        latest,
        edges,
        multi_ic,
        ablation,
        args.data_dir,
    )


if __name__ == "__main__":
    main()
