# -*- coding: utf-8 -*-
"""数据获取：AkShare 行情/资金流/历史估值，含限流重试。"""

from __future__ import annotations

import time
from typing import Mapping

try:
    import akshare as ak
except ImportError:
    ak = None

import numpy as np
import pandas as pd

from .config import Config, VALUATION_DATA_COLS


# 东财 push2his 接口存在突发限流：连续请求会触发一段"直接断连"的封锁窗口。
# 因此对每次网络调用做重试+退避，并在请求之间主动限速。
FETCH_MAX_RETRIES = 5


FETCH_RETRY_BASE_DELAY_SECONDS = 5.0


FETCH_PAUSE_SECONDS = 0.8


def call_with_retry(fetch, label: str):
    """对东财接口调用做重试与退避，抵御间歇性断连/限流。"""
    for attempt in range(FETCH_MAX_RETRIES + 1):
        try:
            result = fetch()
            time.sleep(FETCH_PAUSE_SECONDS)
            return result
        except Exception:
            if attempt >= FETCH_MAX_RETRIES:
                raise
            delay = FETCH_RETRY_BASE_DELAY_SECONDS * (attempt + 1)
            print(
                f"  {label} 请求失败，"
                f"{delay:.0f}s 后重试 "
                f"({attempt + 1}/{FETCH_MAX_RETRIES}) ..."
            )
            time.sleep(delay)


def infer_market(symbol: str) -> str:
    symbol = str(symbol).zfill(6)
    if symbol.startswith(("4", "8", "92")):
        return "bj"
    if symbol.startswith(("5", "6", "9")):
        return "sh"
    return "sz"


def fetch_price(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    if ak is None:
        raise RuntimeError("未安装 akshare，请先运行: pip install akshare")
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust="qfq",
    )
    if df.empty:
        raise RuntimeError(f"{symbol} 无历史行情")

    df = df.rename(
        columns={
            "日期": "date",
            "收盘": "close",
            "成交额": "amount",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
        }
    ).copy()
    required = ["date", "close", "amount"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"{symbol} 行情缺少字段: {missing}")

    df["date"] = pd.to_datetime(df["date"])
    for col in ["open", "high", "low", "close", "volume", "amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["symbol"] = symbol
    return df.sort_values("date")


def fetch_flow(symbol: str) -> pd.DataFrame:
    if ak is None:
        raise RuntimeError("未安装 akshare，请先运行: pip install akshare")
    df = ak.stock_individual_fund_flow(stock=symbol, market=infer_market(symbol))
    if df.empty:
        raise RuntimeError(f"{symbol} 无资金流数据")
    df = df.rename(
        columns={
            "日期": "date",
            "主力净流入-净额": "main_net_flow",
            "主力净流入-净占比": "main_net_flow_pct",
        }
    ).copy()
    if "main_net_flow" not in df.columns:
        raise RuntimeError(f"{symbol} 资金流缺少主力净流入字段")
    df["date"] = pd.to_datetime(df["date"])
    df["main_net_flow"] = pd.to_numeric(df["main_net_flow"], errors="coerce")
    return (
        df[["date", "main_net_flow"]]
        .drop_duplicates("date")
        .sort_values("date")
    )


def fetch_valuation(
    symbol: str,
    start_date: str,
    end_date: str,
    lookback_days: int = 10,
) -> pd.DataFrame:
    """获取真实历史估值。stock_value_em 当前返回最多约 5000 条历史记录。"""
    if ak is None:
        raise RuntimeError("未安装 akshare，请先运行: pip install akshare")
    if not hasattr(ak, "stock_value_em"):
        raise RuntimeError(
            "当前 AkShare 缺少 stock_value_em，请升级: pip install -U akshare"
        )

    df = ak.stock_value_em(symbol=symbol)
    if df.empty:
        raise RuntimeError(f"{symbol} 无历史估值数据")

    df = df.rename(
        columns={
            "数据日期": "valuation_date",
            "PE(TTM)": "pe_ttm",
            "市净率": "pb",
            "市销率": "ps_ttm",
            "总市值": "total_market_cap",
            "流通市值": "float_market_cap",
        }
    ).copy()

    if "valuation_date" not in df.columns:
        raise RuntimeError(f"{symbol} 历史估值缺少数据日期字段")

    for col in VALUATION_DATA_COLS:
        if col not in df.columns:
            df[col] = np.nan

    df["valuation_date"] = pd.to_datetime(df["valuation_date"], errors="coerce")
    for col in VALUATION_DATA_COLS[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    start = pd.to_datetime(start_date) - pd.Timedelta(days=lookback_days)
    end = pd.to_datetime(end_date)
    df = df[
        (df["valuation_date"] >= start)
        & (df["valuation_date"] <= end)
    ].copy()

    return (
        df[VALUATION_DATA_COLS]
        .dropna(subset=["valuation_date"])
        .drop_duplicates("valuation_date", keep="last")
        .sort_values("valuation_date")
    )


def attach_valuation(
    base: pd.DataFrame,
    valuation: pd.DataFrame,
    cfg: Config,
) -> pd.DataFrame:
    """把估值向后对齐到行情日，只允许使用当天或更早的数据。"""
    left = base.sort_values("date").copy()
    if valuation.empty:
        for col in VALUATION_DATA_COLS:
            left[col] = pd.NaT if col == "valuation_date" else np.nan
        left["valuation_age_days"] = np.nan
        return left

    merged = pd.merge_asof(
        left,
        valuation.sort_values("valuation_date"),
        left_on="date",
        right_on="valuation_date",
        direction="backward",
        tolerance=pd.Timedelta(days=cfg.valuation_max_staleness_days),
    )
    merged["valuation_age_days"] = (
        merged["date"] - merged["valuation_date"]
    ).dt.days
    return merged


def load_data(
    universe: Mapping[str, Mapping[str, str]],
    start_date: str,
    end_date: str,
    cfg: Config,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    failures: list[str] = []
    valuation_failures: list[str] = []

    for symbol, meta in universe.items():
        print(f"下载 {symbol} {meta['name']} ...")
        try:
            # 行情与资金流分开重试：一个接口成功后不因另一个失败而重拉。
            price_df = call_with_retry(
                lambda: fetch_price(symbol, start_date, end_date),
                f"{symbol} 行情",
            )
            flow_df = call_with_retry(
                lambda: fetch_flow(symbol),
                f"{symbol} 资金流",
            )
            base = price_df.merge(flow_df, on="date", how="left")
        except Exception as exc:
            failures.append(f"{symbol} {meta['name']}: {exc}")
            continue

        try:
            valuation = call_with_retry(
                lambda: fetch_valuation(
                    symbol,
                    start_date,
                    end_date,
                    lookback_days=cfg.valuation_max_staleness_days,
                ),
                f"{symbol} 估值",
            )
            df = attach_valuation(base, valuation, cfg)
        except Exception as exc:
            valuation_failures.append(f"{symbol} {meta['name']}: {exc}")
            df = attach_valuation(base, pd.DataFrame(), cfg)

        df["name"] = meta["name"]
        df["sector"] = meta["sector"]
        frames.append(df)

    if failures:
        print("\n行情/资金流下载失败：")
        for item in failures:
            print(f"- {item}")

    if valuation_failures:
        print("\n估值下载失败（保留股票，估值因子自动降级）：")
        for item in valuation_failures:
            print(f"- {item}")

    if len(frames) < 3:
        raise RuntimeError("成功获取的股票不足 3 只")

    return pd.concat(frames, ignore_index=True).sort_values(
        ["symbol", "date"]
    )
