# -*- coding: utf-8 -*-
"""Build the CN + US full-market input dataset for the hierarchical migration model.

Examples
--------
Quick smoke test with the largest 20 stocks in each market::

    python code/build_hierarchical_market_data.py \
        --start-date 20250101 --end-date 20250901 \
        --max-cn 20 --max-us 20

Full current-listed universe (resumable; uses local per-symbol caches)::

    python code/build_hierarchical_market_data.py \
        --start-date 20240101 --end-date 20260901 \
        --workers 2
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from hierarchical_migration.data_pipeline import MarketDataConfig, build_market_dataset


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CACHE_DIR = BASE_DIR / "data" / "hierarchical_market"
DEFAULT_OUTPUT_DIR = BASE_DIR / "outputs" / "hierarchical_market_data"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build current-listed A-share + US-stock unified market dataset"
    )
    parser.add_argument(
        "--start-date",
        default=(pd.Timestamp.today() - pd.DateOffset(years=2)).strftime("%Y%m%d"),
    )
    parser.add_argument("--end-date", default=pd.Timestamp.today().strftime("%Y%m%d"))
    parser.add_argument(
        "--markets",
        nargs="+",
        choices=["CN", "US"],
        default=["CN", "US"],
    )
    parser.add_argument(
        "--sector-level",
        choices=["l1", "l2"],
        default="l2",
        help="canonical sector level exposed as the model's sector column",
    )
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--request-pause", type=float, default=0.20)
    parser.add_argument("--refresh-master", action="store_true")
    parser.add_argument("--refresh-history", action="store_true")
    parser.add_argument("--include-non-common-us", action="store_true")
    parser.add_argument("--usd-cny-fallback", type=float, default=7.20)
    parser.add_argument("--max-cn", type=int, default=None, help="debug: top N CN by market cap")
    parser.add_argument("--max-us", type=int, default=None, help="debug: top N US by market cap")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = MarketDataConfig(
        start_date=args.start_date,
        end_date=args.end_date,
        cache_dir=args.cache_dir,
        output_dir=args.output_dir,
        markets=tuple(args.markets),
        sector_level=args.sector_level,
        workers=max(1, args.workers),
        request_pause_seconds=max(0.0, args.request_pause),
        refresh_master=args.refresh_master,
        refresh_history=args.refresh_history,
        include_non_common_us=args.include_non_common_us,
        usd_cny_fallback=args.usd_cny_fallback,
        max_cn_symbols=args.max_cn,
        max_us_symbols=args.max_us,
    )
    result = build_market_dataset(cfg)

    print("\n========== 数据集构建完成 ==========")
    for name, path in result["paths"].items():
        print(f"{name}: {path}")

    status = result["status"]
    failed = status[status["rows"] == 0]
    if not failed.empty:
        print(f"\n失败证券: {len(failed)}，详见 download_status 输出。")


if __name__ == "__main__":
    main()
