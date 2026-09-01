from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from threading import Lock
import time

import numpy as np
import pandas as pd

from .providers import (
    add_close_timestamp_utc,
    fetch_cn_history,
    fetch_cn_industry_map,
    fetch_cn_security_master,
    fetch_us_history,
    fetch_us_security_master,
    fetch_usd_cny_history,
)
from .taxonomy import apply_unified_taxonomy, taxonomy_coverage


@dataclass(frozen=True)
class MarketDataConfig:
    start_date: str
    end_date: str
    cache_dir: Path
    output_dir: Path
    markets: tuple[str, ...] = ("CN", "US")
    sector_level: str = "l2"
    workers: int = 2
    request_pause_seconds: float = 0.20
    refresh_master: bool = False
    refresh_history: bool = False
    include_non_common_us: bool = False
    usd_cny_fallback: float = 7.20
    max_cn_symbols: int | None = None
    max_us_symbols: int | None = None


class RequestThrottle:
    """Thread-safe global request-start limiter for per-symbol history calls."""

    def __init__(self, interval_seconds: float):
        self.interval = max(0.0, float(interval_seconds))
        self.lock = Lock()
        self.last_started = 0.0

    def wait(self) -> None:
        if self.interval <= 0:
            return
        with self.lock:
            now = time.monotonic()
            remaining = self.interval - (now - self.last_started)
            if remaining > 0:
                time.sleep(remaining)
            self.last_started = time.monotonic()


MASTER_COLUMNS = [
    "symbol", "provider_symbol", "name", "market", "exchange", "active",
    "instrument_type", "source_sector", "source_industry", "source_taxonomy",
    "metadata_asof_date", "sector_l1", "sector_l2", "taxonomy_rule",
    "market_cap", "float_market_cap", "pe_current", "pb_current",
]


def _safe_symbol(symbol: str) -> str:
    return str(symbol).replace("/", "_").replace("\\", "_").replace(":", "_")


def _cache_read(path: Path, date_col: str | None = None) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, compression="infer")
    if date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col]).sort_values(date_col)
    return df


def _cache_write(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    df.to_csv(tmp, index=False, encoding="utf-8-sig", compression="gzip")
    tmp.replace(path)


def _dedupe_history(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    return (
        out.dropna(subset=["date"])
        .drop_duplicates("date", keep="last")
        .sort_values("date")
        .reset_index(drop=True)
    )


def _fetch_missing_history(
    row,
    start: pd.Timestamp,
    end: pd.Timestamp,
    cached: pd.DataFrame,
    refresh: bool,
    throttle: RequestThrottle | None = None,
) -> pd.DataFrame:
    market = str(row.market)
    symbol = str(row.symbol)
    provider_symbol = str(row.provider_symbol)

    def fetch_range(a: pd.Timestamp, b: pd.Timestamp) -> pd.DataFrame:
        if a > b:
            return pd.DataFrame()
        a_str, b_str = a.strftime("%Y%m%d"), b.strftime("%Y%m%d")

        def once() -> pd.DataFrame:
            if market == "CN":
                return fetch_cn_history(symbol, a_str, b_str)
            if market == "US":
                return fetch_us_history(provider_symbol, symbol, a_str, b_str)
            raise ValueError(f"未知市场: {market}")

        last_error = None
        for attempt in range(3):
            try:
                if throttle is not None:
                    throttle.wait()
                return once()
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"{market} {symbol} 历史行情重试失败: {last_error}")

    pieces = [] if refresh else ([cached] if not cached.empty else [])
    if refresh or cached.empty:
        pieces.append(fetch_range(start, end))
    else:
        cached_dates = pd.to_datetime(cached["date"], errors="coerce")
        first, last = cached_dates.min(), cached_dates.max()
        if pd.isna(first) or pd.isna(last):
            pieces.append(fetch_range(start, end))
        else:
            if start < first:
                pieces.append(fetch_range(start, first - pd.Timedelta(days=1)))
            if end > last:
                pieces.append(fetch_range(last + pd.Timedelta(days=1), end))

    valid = [x for x in pieces if x is not None and not x.empty]
    if not valid:
        return _dedupe_history(cached)
    return _dedupe_history(pd.concat(valid, ignore_index=True))


def _build_cn_master(cfg: MarketDataConfig) -> pd.DataFrame:
    root = cfg.cache_dir / "master"
    master_path = root / "cn_security_master.csv.gz"
    industry_path = root / "cn_industry_map.csv.gz"

    if master_path.exists() and not cfg.refresh_master:
        master = _cache_read(master_path)
    else:
        master = fetch_cn_security_master()

    if industry_path.exists() and not cfg.refresh_master:
        industry = _cache_read(industry_path)
    else:
        industry = fetch_cn_industry_map(cfg.request_pause_seconds)
        _cache_write(industry, industry_path)

    master = master.drop(columns=["source_industry"], errors="ignore").merge(
        industry[["symbol", "source_industry"]], on="symbol", how="left"
    )
    master["source_industry"] = master["source_industry"].fillna("")
    master["source_sector"] = master["source_sector"].fillna("")
    master = apply_unified_taxonomy(master)
    _cache_write(master, master_path)
    return master


def _build_us_master(cfg: MarketDataConfig) -> pd.DataFrame:
    path = cfg.cache_dir / "master" / "us_security_master.csv.gz"
    if path.exists() and not cfg.refresh_master:
        master = _cache_read(path)
    else:
        master = fetch_us_security_master(include_non_common=True)
        master = apply_unified_taxonomy(master)
        _cache_write(master, path)
    if not cfg.include_non_common_us:
        master = master[
            master["instrument_type"].isin(["CommonStock", "ADR", "REIT"])
        ].copy()
    return master


def build_security_master(cfg: MarketDataConfig) -> pd.DataFrame:
    frames = []
    requested = {m.upper() for m in cfg.markets}
    if "CN" in requested:
        cn = _build_cn_master(cfg)
        if cfg.max_cn_symbols:
            cn = cn.sort_values("market_cap", ascending=False).head(cfg.max_cn_symbols)
        frames.append(cn)
    if "US" in requested:
        us = _build_us_master(cfg)
        if cfg.max_us_symbols:
            us = us.sort_values("market_cap", ascending=False).head(cfg.max_us_symbols)
        frames.append(us)
    if not frames:
        raise RuntimeError("未选择 CN/US 市场")
    master = pd.concat(frames, ignore_index=True, sort=False)
    for col in MASTER_COLUMNS:
        if col not in master.columns:
            master[col] = np.nan
    return master[MASTER_COLUMNS].reset_index(drop=True)


def _history_cache_path(cache_dir: Path, market: str, symbol: str) -> Path:
    return cache_dir / "history" / market / f"{_safe_symbol(symbol)}.csv.gz"


def update_history_for_security(
    row,
    cfg: MarketDataConfig,
    throttle: RequestThrottle | None = None,
) -> tuple[str, str, pd.DataFrame, str | None]:
    path = _history_cache_path(cfg.cache_dir, str(row.market), str(row.symbol))
    cached = _cache_read(path, "date")
    start, end = pd.to_datetime(cfg.start_date), pd.to_datetime(cfg.end_date)
    try:
        merged = _fetch_missing_history(row, start, end, cached, cfg.refresh_history, throttle)
        if not merged.empty:
            _cache_write(merged, path)
        selected = merged[(merged["date"] >= start) & (merged["date"] <= end)].copy()
        return str(row.market), str(row.symbol), selected, None
    except Exception as exc:
        if not cached.empty:
            selected = cached[(cached["date"] >= start) & (cached["date"] <= end)].copy()
            if not selected.empty:
                return str(row.market), str(row.symbol), selected, f"update failed; cached: {exc}"
        return str(row.market), str(row.symbol), pd.DataFrame(), str(exc)


def load_fx_history(cfg: MarketDataConfig) -> pd.DataFrame:
    path = cfg.cache_dir / "fx" / "usd_cny.csv.gz"
    if path.exists() and not cfg.refresh_history:
        fx = _cache_read(path, "date")
    else:
        try:
            fx = fetch_usd_cny_history()
            _cache_write(fx, path)
        except Exception as exc:
            print(f"USD/CNY 历史获取失败，使用 fallback={cfg.usd_cny_fallback}: {exc}")
            fx = pd.DataFrame()
    return fx


def _attach_fx(panel: pd.DataFrame, fx: pd.DataFrame, fallback: float) -> pd.DataFrame:
    frames = []
    for market, g in panel.groupby("market", sort=False):
        g = g.sort_values("date").copy()
        if market == "CN":
            g["fx_to_base"] = 1.0
        elif market == "US":
            if fx.empty:
                g["fx_to_base"] = fallback
            else:
                left = g.sort_values("date")
                right = fx[["date", "fx_to_base"]].sort_values("date")
                g = pd.merge_asof(left, right, on="date", direction="backward")
                g["fx_to_base"] = g["fx_to_base"].fillna(fallback)
        else:
            g["fx_to_base"] = 1.0
        g["amount_base"] = pd.to_numeric(g["amount"], errors="coerce") * g["fx_to_base"]
        frames.append(g)
    return pd.concat(frames, ignore_index=True, sort=False)


def build_unified_panel(master: pd.DataFrame, cfg: MarketDataConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = list(master.itertuples(index=False))
    results = []
    status_rows = []

    workers = max(1, int(cfg.workers))
    throttle = RequestThrottle(cfg.request_pause_seconds)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(update_history_for_security, row, cfg, throttle): row
            for row in rows
        }
        completed = 0
        for future in as_completed(futures):
            market, symbol, hist, error = future.result()
            completed += 1
            if not hist.empty:
                results.append(hist)
            status_rows.append(
                {
                    "market": market,
                    "symbol": symbol,
                    "rows": len(hist),
                    "status": "ok" if error is None else "cached" if len(hist) else "failed",
                    "message": error or "",
                }
            )
            if completed % 100 == 0 or completed == len(rows):
                print(f"历史行情进度: {completed}/{len(rows)}")

    if not results:
        raise RuntimeError("没有成功加载任何 CN/US 历史行情")

    panel = pd.concat(results, ignore_index=True, sort=False)
    panel["date"] = pd.to_datetime(panel["date"], errors="coerce")
    meta_cols = [
        "symbol", "market", "name", "exchange", "instrument_type",
        "source_sector", "source_industry", "source_taxonomy", "metadata_asof_date",
        "sector_l1", "sector_l2", "taxonomy_rule",
    ]
    panel = panel.merge(master[meta_cols], on=["symbol", "market"], how="left")
    sector_col = "sector_l1" if cfg.sector_level.lower() == "l1" else "sector_l2"
    panel["sector"] = panel[sector_col].fillna("Other")
    panel = _attach_fx(panel, load_fx_history(cfg), cfg.usd_cny_fallback)
    panel = add_close_timestamp_utc(panel)
    panel["currency"] = np.where(panel["market"].eq("CN"), "CNY", "USD")
    panel["base_currency"] = "CNY"
    panel["industry_mapping_type"] = "current_snapshot"
    panel = panel.sort_values(["market", "symbol", "date"]).reset_index(drop=True)
    return panel, pd.DataFrame(status_rows)


def _write_frame(df: pd.DataFrame, stem: Path) -> Path:
    stem.parent.mkdir(parents=True, exist_ok=True)
    try:
        import pyarrow  # noqa: F401
        path = stem.with_suffix(".parquet")
        df.to_parquet(path, index=False)
        return path
    except ImportError:
        path = Path(str(stem) + ".csv.gz")
        df.to_csv(path, index=False, compression="gzip", encoding="utf-8-sig")
        return path


def save_market_dataset(
    master: pd.DataFrame,
    panel: pd.DataFrame,
    status: pd.DataFrame,
    cfg: MarketDataConfig,
) -> dict[str, Path]:
    out = cfg.output_dir
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "security_master": _write_frame(master, out / "security_master"),
        "unified_panel": _write_frame(panel, out / "unified_panel"),
        "download_status": _write_frame(status, out / "download_status"),
        "taxonomy_coverage": _write_frame(taxonomy_coverage(master), out / "taxonomy_coverage"),
    }

    coverage = (
        panel.groupby(["market", "symbol"])
        .agg(first_date=("date", "min"), last_date=("date", "max"), rows=("date", "size"))
        .reset_index()
    )
    paths["history_coverage"] = _write_frame(coverage, out / "history_coverage")

    manifest = {
        "config": {
            **asdict(cfg),
            "cache_dir": str(cfg.cache_dir),
            "output_dir": str(cfg.output_dir),
        },
        "universe": {
            "scope": "currently_listed_CN_and_US_equities",
            "survivorship_bias": True,
            "industry_mapping": "current_snapshot",
            "point_in_time_industry_membership": False,
        },
        "sources": {
            "CN_master": "AkShare stock_zh_a_spot_em",
            "CN_industry": "AkShare stock_board_industry_name_em + stock_board_industry_cons_em",
            "CN_history": "AkShare stock_zh_a_hist",
            "US_master_prices": "AkShare stock_us_spot_em",
            "US_sector_industry": "Nasdaq public stock screener endpoint",
            "US_history": "AkShare stock_us_hist",
            "FX": "AkShare currency_boc_safe (SAFE RMB midpoint)",
        },
        "rows": {
            "security_master": int(len(master)),
            "unified_panel": int(len(panel)),
            "successful_securities": int((status["rows"] > 0).sum()),
            "failed_securities": int((status["rows"] == 0).sum()),
        },
    }
    manifest_path = out / "dataset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    paths["manifest"] = manifest_path
    return paths


def build_market_dataset(cfg: MarketDataConfig) -> dict[str, object]:
    master = build_security_master(cfg)
    print(
        f"证券主表: {len(master)} 只 | CN={(master['market'] == 'CN').sum()} | "
        f"US={(master['market'] == 'US').sum()}"
    )
    panel, status = build_unified_panel(master, cfg)
    paths = save_market_dataset(master, panel, status, cfg)
    return {"master": master, "panel": panel, "status": status, "paths": paths}
