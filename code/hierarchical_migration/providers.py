from __future__ import annotations

import math
import re
import time
from typing import Iterable
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

try:
    import akshare as ak
except ImportError:  # pragma: no cover
    ak = None

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None


NASDAQ_SCREENER_URL = "https://api.nasdaq.com/api/screener/stocks"
NASDAQ_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36"
    ),
}


def require_akshare() -> None:
    if ak is None:
        raise RuntimeError("未安装 akshare，请先运行: pip install -U akshare")


def require_requests() -> None:
    if requests is None:
        raise RuntimeError("未安装 requests，请先运行: pip install requests")


def parse_number(value) -> float:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return np.nan
    text = str(value).replace("$", "").replace(",", "").replace("%", "").strip()
    if text in {"", "N/A", "n/a", "--", "None", "nan"}:
        return np.nan
    try:
        return float(text)
    except ValueError:
        return np.nan


def infer_cn_exchange(symbol: str) -> str:
    code = str(symbol).zfill(6)
    if code.startswith(("4", "8", "92")):
        return "BSE"
    if code.startswith(("5", "6", "9")):
        return "SSE"
    return "SZSE"


def canonical_us_symbol(symbol: object) -> str:
    text = "" if symbol is None else str(symbol).strip().upper()
    text = text.replace("/", "-").replace(".", "-").replace(" ", "-")
    return re.sub(r"-+", "-", text)


def eastmoney_us_ticker(provider_symbol: object) -> str:
    text = "" if provider_symbol is None else str(provider_symbol).strip()
    if "." in text:
        text = text.split(".", 1)[1]
    return canonical_us_symbol(text)


def _rename_price_frame(df: pd.DataFrame, market: str) -> pd.DataFrame:
    columns = {
        "日期": "date",
        "开盘": "open",
        "开盘价": "open",
        "收盘": "close",
        "最高": "high",
        "最高价": "high",
        "最低": "low",
        "最低价": "low",
        "成交量": "volume",
        "成交额": "amount",
        "换手率": "turnover",
        "涨跌幅": "pct_change",
    }
    out = df.rename(columns=columns).copy()
    required = ["date", "close", "amount"]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise RuntimeError(f"{market} 历史行情缺少字段: {missing}")
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    for col in ["open", "high", "low", "close", "volume", "amount", "turnover", "pct_change"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.dropna(subset=["date", "close"]).sort_values("date")


def fetch_cn_security_master() -> pd.DataFrame:
    require_akshare()
    df = ak.stock_zh_a_spot_em()
    if df.empty:
        raise RuntimeError("stock_zh_a_spot_em 未返回 A 股数据")
    out = df.rename(
        columns={
            "代码": "symbol",
            "名称": "name",
            "总市值": "market_cap",
            "流通市值": "float_market_cap",
            "市盈率-动态": "pe_current",
            "市净率": "pb_current",
        }
    ).copy()
    required = ["symbol", "name"]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise RuntimeError(f"A 股证券列表缺少字段: {missing}")
    out["symbol"] = out["symbol"].astype(str).str.zfill(6)
    out["provider_symbol"] = out["symbol"]
    out["market"] = "CN"
    out["exchange"] = out["symbol"].map(infer_cn_exchange)
    out["source_sector"] = ""
    out["source_industry"] = ""
    out["active"] = True
    out["instrument_type"] = "CommonStock"
    for col in ["market_cap", "float_market_cap", "pe_current", "pb_current"]:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")
    keep = [
        "symbol", "provider_symbol", "name", "market", "exchange", "active",
        "instrument_type", "source_sector", "source_industry", "market_cap",
        "float_market_cap", "pe_current", "pb_current",
    ]
    return out[keep].drop_duplicates(["market", "symbol"]).reset_index(drop=True)


def fetch_cn_industry_map(pause_seconds: float = 0.25) -> pd.DataFrame:
    """Fetch current Eastmoney industry-board membership for all A shares."""
    require_akshare()
    boards = ak.stock_board_industry_name_em()
    if boards.empty or "板块名称" not in boards.columns:
        raise RuntimeError("stock_board_industry_name_em 未返回行业板块")

    rows: list[pd.DataFrame] = []
    for board in boards["板块名称"].dropna().astype(str).drop_duplicates():
        try:
            cons = ak.stock_board_industry_cons_em(symbol=board)
            if cons.empty:
                continue
            code_col = "代码" if "代码" in cons.columns else None
            name_col = "名称" if "名称" in cons.columns else None
            if code_col is None:
                continue
            part = pd.DataFrame(
                {
                    "symbol": cons[code_col].astype(str).str.zfill(6),
                    "source_industry": board,
                    "industry_member_name": cons[name_col].astype(str) if name_col else "",
                }
            )
            rows.append(part)
        except Exception as exc:
            print(f"  行业板块 {board} 获取失败: {exc}")
        if pause_seconds > 0:
            time.sleep(pause_seconds)

    if not rows:
        return pd.DataFrame(columns=["symbol", "source_industry"])
    combined = pd.concat(rows, ignore_index=True)
    return (
        combined.sort_values(["symbol", "source_industry"])
        .drop_duplicates("symbol", keep="first")[["symbol", "source_industry"]]
        .reset_index(drop=True)
    )


def _extract_nasdaq_rows(payload: dict) -> list[dict]:
    data = payload.get("data") or {}
    rows = data.get("rows")
    if isinstance(rows, list):
        return rows
    table = data.get("table") or {}
    rows = table.get("rows")
    return rows if isinstance(rows, list) else []


def fetch_nasdaq_screener_exchange(
    exchange: str,
    page_size: int = 10000,
    timeout: float = 30.0,
) -> pd.DataFrame:
    """Fetch one major US exchange from Nasdaq's public screener endpoint."""
    require_requests()
    params = {
        "tableonly": "true",
        "limit": page_size,
        "offset": 0,
        "exchange": exchange.upper(),
        "download": "true",
    }
    response = requests.get(
        NASDAQ_SCREENER_URL,
        params=params,
        headers=NASDAQ_HEADERS,
        timeout=timeout,
    )
    response.raise_for_status()
    return pd.DataFrame(_extract_nasdaq_rows(response.json()))


def fetch_nasdaq_security_master(
    exchanges: Iterable[str] = ("NASDAQ", "NYSE", "AMEX"),
) -> pd.DataFrame:
    frames = []
    for exchange in exchanges:
        print(f"下载 Nasdaq Screener: {exchange} ...")
        part = fetch_nasdaq_screener_exchange(exchange)
        if not part.empty:
            part["exchange"] = exchange.upper()
            frames.append(part)
    if not frames:
        raise RuntimeError("Nasdaq Screener 未返回美股证券列表")
    raw = pd.concat(frames, ignore_index=True)

    def col(name: str, default="") -> pd.Series:
        if name in raw.columns:
            return raw[name]
        return pd.Series(default, index=raw.index)

    out = pd.DataFrame(
        {
            "symbol": col("symbol").astype(str).str.strip().str.upper(),
            "name": col("name").astype(str).str.strip(),
            "exchange": raw["exchange"].astype(str),
            "source_sector": col("sector").fillna("").astype(str).str.strip(),
            "source_industry": col("industry").fillna("").astype(str).str.strip(),
            "country": col("country").fillna("").astype(str).str.strip(),
            "market_cap_nasdaq": col("marketCap", np.nan).map(parse_number),
        }
    )
    out["symbol_key"] = out["symbol"].map(canonical_us_symbol)
    return out.drop_duplicates("symbol_key", keep="first").reset_index(drop=True)


def _infer_us_instrument_type(name: str) -> str:
    text = str(name).lower()
    if "warrant" in text:
        return "Warrant"
    if " right" in text or text.endswith("rights"):
        return "Right"
    if " unit" in text or text.endswith("units"):
        return "Unit"
    if "preferred" in text:
        return "Preferred"
    if "etf" in text or "exchange traded fund" in text:
        return "ETF"
    if "closed-end" in text or "closed end" in text:
        return "ClosedEndFund"
    if "reit" in text or "real estate investment trust" in text:
        return "REIT"
    if "adr" in text or "american depositary" in text:
        return "ADR"
    return "CommonStock"


def fetch_us_security_master(include_non_common: bool = False) -> pd.DataFrame:
    """Join Nasdaq industry metadata with Eastmoney codes required by stock_us_hist."""
    require_akshare()
    nasdaq = fetch_nasdaq_security_master()
    em = ak.stock_us_spot_em()
    if em.empty or "代码" not in em.columns:
        raise RuntimeError("stock_us_spot_em 未返回美股列表")
    em2 = em.rename(
        columns={
            "代码": "provider_symbol",
            "名称": "em_name",
            "总市值": "market_cap_em",
            "市盈率": "pe_current",
        }
    ).copy()
    em2["symbol_key"] = em2["provider_symbol"].map(eastmoney_us_ticker)
    em2["market_cap_em"] = pd.to_numeric(em2.get("market_cap_em"), errors="coerce")
    em2["pe_current"] = pd.to_numeric(em2.get("pe_current"), errors="coerce")

    joined = nasdaq.merge(em2, on="symbol_key", how="inner", suffixes=("", "_em"))
    print(f"US 代码交叉匹配: Nasdaq={len(nasdaq):,} -> AkShare可回溯={len(joined):,}")
    joined["name"] = joined["name"].where(
        joined["name"].notna() & joined["name"].astype(str).ne(""),
        joined["em_name"],
    )
    joined["source_sector"] = joined["source_sector"].fillna("")
    joined["source_industry"] = joined["source_industry"].fillna("")
    joined["market_cap"] = joined["market_cap_em"].where(
        joined["market_cap_em"].notna(), joined["market_cap_nasdaq"]
    )
    joined["float_market_cap"] = np.nan
    joined["pb_current"] = np.nan
    joined["market"] = "US"
    joined["active"] = True
    joined["instrument_type"] = joined["name"].map(_infer_us_instrument_type)
    if not include_non_common:
        joined = joined[
            joined["instrument_type"].isin(["CommonStock", "ADR", "REIT"])
        ].copy()
    keep = [
        "symbol", "provider_symbol", "name", "market", "exchange", "active",
        "instrument_type", "source_sector", "source_industry", "market_cap",
        "float_market_cap", "pe_current", "pb_current",
    ]
    return joined[keep].drop_duplicates(["market", "symbol"]).reset_index(drop=True)


def fetch_cn_history(symbol: str, start_date: str, end_date: str, adjust: str = "qfq") -> pd.DataFrame:
    require_akshare()
    raw = ak.stock_zh_a_hist(
        symbol=str(symbol).zfill(6),
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )
    if raw.empty:
        return pd.DataFrame()
    out = _rename_price_frame(raw, "CN")
    out["symbol"] = str(symbol).zfill(6)
    out["provider_symbol"] = str(symbol).zfill(6)
    out["market"] = "CN"
    return out


def fetch_us_history(
    provider_symbol: str,
    symbol: str,
    start_date: str,
    end_date: str,
    adjust: str = "qfq",
) -> pd.DataFrame:
    require_akshare()
    raw = ak.stock_us_hist(
        symbol=str(provider_symbol),
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )
    if raw.empty:
        return pd.DataFrame()
    out = _rename_price_frame(raw, "US")
    out["symbol"] = str(symbol).upper()
    out["provider_symbol"] = str(provider_symbol)
    out["market"] = "US"
    return out


def fetch_usd_cny_history() -> pd.DataFrame:
    """SAFE midpoint: USD column is CNY per 100 USD, therefore divide by 100."""
    require_akshare()
    raw = ak.currency_boc_safe()
    if raw.empty or "日期" not in raw.columns or "美元" not in raw.columns:
        raise RuntimeError("currency_boc_safe 未返回美元人民币中间价")
    out = raw[["日期", "美元"]].rename(columns={"日期": "date", "美元": "usd_cny_100"}).copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["usd_cny_100"] = pd.to_numeric(out["usd_cny_100"], errors="coerce")
    out["fx_to_base"] = out["usd_cny_100"] / 100.0
    return out.dropna(subset=["date", "fx_to_base"]).sort_values("date")[["date", "fx_to_base"]]


def add_close_timestamp_utc(history: pd.DataFrame) -> pd.DataFrame:
    """Attach actual market close time in UTC to preserve cross-market causality metadata."""
    df = history.copy()
    timestamps = []
    for row in df[["date", "market"]].itertuples(index=False):
        day = pd.Timestamp(row.date).date()
        if str(row.market).upper() == "CN":
            local = pd.Timestamp(day).replace(hour=15, minute=0).tz_localize(ZoneInfo("Asia/Shanghai"))
        elif str(row.market).upper() == "US":
            local = pd.Timestamp(day).replace(hour=16, minute=0).tz_localize(ZoneInfo("America/New_York"))
        else:
            local = pd.Timestamp(day).tz_localize("UTC")
        timestamps.append(local.tz_convert("UTC"))
    df["close_timestamp_utc"] = timestamps
    return df
