# -*- coding: utf-8 -*-
"""股票资本迁移模型：研究增强版。

在 stock_capital_migration.py 基线模型上增加：
1. 本地增量缓存：价格 / 主力资金流 / 历史估值。
2. 1/3/5/10/20 个交易日前瞻收益与 Rank IC。
3. A-G 七组因子消融实验，比较普通因子与 Gravity/Migration 的增量价值。

运行：
    python stock_capital_migration_research.py
    python stock_capital_migration_research.py --offline
    python stock_capital_migration_research.py --refresh-cache
    python stock_capital_migration_research.py --skip-ablation
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

import stock_capital_migration as base


HORIZONS = (1, 3, 5, 10, 20)
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_OUTPUT_DIR = BASE_DIR / "outputs"


def read_cache(path: Path, date_col: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])
    return df


def merge_cache(old: pd.DataFrame, new: pd.DataFrame, date_col: str) -> pd.DataFrame:
    if old.empty:
        merged = new.copy()
    elif new.empty:
        merged = old.copy()
    else:
        merged = pd.concat([old, new], ignore_index=True)
    if merged.empty:
        return merged
    merged[date_col] = pd.to_datetime(merged[date_col], errors="coerce")
    return (
        merged.dropna(subset=[date_col])
        .drop_duplicates(date_col, keep="last")
        .sort_values(date_col)
        .reset_index(drop=True)
    )


def write_cache(df: pd.DataFrame, path: Path, date_col: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = merge_cache(pd.DataFrame(), df, date_col)
    tmp = path.with_suffix(path.suffix + ".tmp")
    out.to_csv(tmp, index=False, encoding="utf-8-sig")
    tmp.replace(path)


def slice_range(df: pd.DataFrame, date_col: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    if df.empty:
        return df
    return df[(df[date_col] >= start) & (df[date_col] <= end)].copy()


def retry_fetch(fetch, label: str) -> pd.DataFrame:
    """优先复用基线脚本已有的限流重试；兼容较旧基线。"""
    if hasattr(base, "call_with_retry"):
        return base.call_with_retry(fetch, label)
    return fetch()


def cached_price(
    symbol: str,
    start_date: str,
    end_date: str,
    data_dir: Path,
    offline: bool,
    refresh: bool,
) -> pd.DataFrame:
    path = data_dir / "prices" / f"{symbol}.csv"
    cached = read_cache(path, "date")
    start, end = pd.to_datetime(start_date), pd.to_datetime(end_date)

    need_fetch = cached.empty or refresh
    if not cached.empty and not refresh:
        need_fetch = cached["date"].min() > start or cached["date"].max() < end

    if need_fetch and not offline:
        fetch_start = start
        if not cached.empty and cached["date"].min() <= start and not refresh:
            fetch_start = max(start, cached["date"].max() + pd.Timedelta(days=1))
        try:
            if fetch_start <= end or refresh:
                actual_start = start if refresh else fetch_start
                new = retry_fetch(
                    lambda: base.fetch_price(
                        symbol,
                        actual_start.strftime("%Y%m%d"),
                        end.strftime("%Y%m%d"),
                    ),
                    f"{symbol} 行情",
                )
                cached = merge_cache(cached, new, "date")
                write_cache(cached, path, "date")
        except Exception:
            if cached.empty:
                raise
            print(f"  {symbol} 行情更新失败，使用本地缓存")

    if cached.empty:
        raise RuntimeError(f"{symbol} 没有行情缓存")
    result = slice_range(cached, "date", start, end)
    if result.empty:
        raise RuntimeError(f"{symbol} 缓存中没有请求区间行情")
    result["symbol"] = str(symbol).zfill(6)
    return result


def cached_flow(
    symbol: str,
    start_date: str,
    end_date: str,
    data_dir: Path,
    offline: bool,
) -> pd.DataFrame:
    """资金流接口窗口较短；每次联网运行都与本地历史做 union，长期积累。"""
    path = data_dir / "fund_flow" / f"{symbol}.csv"
    cached = read_cache(path, "date")

    if not offline:
        try:
            new = retry_fetch(lambda: base.fetch_flow(symbol), f"{symbol} 资金流")
            cached = merge_cache(cached, new, "date")
            write_cache(cached, path, "date")
        except Exception:
            if cached.empty:
                raise
            print(f"  {symbol} 资金流更新失败，使用本地缓存")

    if cached.empty:
        raise RuntimeError(f"{symbol} 没有资金流缓存")
    return slice_range(
        cached,
        "date",
        pd.to_datetime(start_date),
        pd.to_datetime(end_date),
    )


def cached_valuation(
    symbol: str,
    start_date: str,
    end_date: str,
    data_dir: Path,
    cfg: base.Config,
    offline: bool,
    refresh: bool,
) -> pd.DataFrame:
    path = data_dir / "valuation" / f"{symbol}.csv"
    cached = read_cache(path, "valuation_date")
    start = pd.to_datetime(start_date) - pd.Timedelta(days=cfg.valuation_max_staleness_days)
    end = pd.to_datetime(end_date)

    need_fetch = cached.empty or refresh
    if not cached.empty and not refresh:
        need_fetch = (
            cached["valuation_date"].min() > start
            or cached["valuation_date"].max() < end
        )

    if need_fetch and not offline:
        try:
            new = retry_fetch(
                lambda: base.fetch_valuation(
                    symbol,
                    start.strftime("%Y%m%d"),
                    end.strftime("%Y%m%d"),
                    lookback_days=cfg.valuation_max_staleness_days,
                ),
                f"{symbol} 估值",
            )
            cached = merge_cache(cached, new, "valuation_date")
            write_cache(cached, path, "valuation_date")
        except Exception:
            if cached.empty:
                raise
            print(f"  {symbol} 估值更新失败，使用本地缓存")

    if cached.empty:
        return pd.DataFrame(columns=base.VALUATION_DATA_COLS)
    return slice_range(cached, "valuation_date", start, end)


def load_data_cached(
    universe: Mapping[str, Mapping[str, str]],
    start_date: str,
    end_date: str,
    cfg: base.Config,
    data_dir: Path,
    offline: bool,
    refresh: bool,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    failures: list[str] = []

    for symbol, meta in universe.items():
        print(f"加载 {symbol} {meta['name']} ...")
        try:
            price = cached_price(symbol, start_date, end_date, data_dir, offline, refresh)
            flow = cached_flow(symbol, start_date, end_date, data_dir, offline)
            merged = price.merge(flow, on="date", how="left")
            try:
                valuation = cached_valuation(
                    symbol, start_date, end_date, data_dir, cfg, offline, refresh
                )
                merged = base.attach_valuation(merged, valuation, cfg)
            except Exception as exc:
                print(f"  {symbol} 估值不可用，自动降级：{exc}")
                merged = base.attach_valuation(merged, pd.DataFrame(), cfg)
            merged["name"] = meta["name"]
            merged["sector"] = meta["sector"]
            frames.append(merged)
        except Exception as exc:
            failures.append(f"{symbol} {meta['name']}: {exc}")

    if failures:
        print("\n加载失败：")
        for item in failures:
            print(f"- {item}")
    if len(frames) < 3:
        raise RuntimeError("成功加载的股票不足 3 只")
    return pd.concat(frames, ignore_index=True).sort_values(["symbol", "date"])


def add_forward_returns(features: pd.DataFrame) -> pd.DataFrame:
    """未来 h 个交易日收益：P[t+h]/P[t]-1。"""
    df = features.copy().sort_values(["symbol", "date"])
    grouped = df.groupby("symbol", group_keys=False)
    for h in HORIZONS:
        df[f"forward_return_{h}d"] = grouped["close"].transform(
            lambda s, h=h: s.shift(-h) / s - 1.0
        )
    return df


def attraction_score(day: pd.DataFrame, cfg: base.Config) -> pd.Series:
    return (
        cfg.attraction_w_momentum * day["momentum_z"].fillna(0)
        + cfg.attraction_w_flow * day["flow_strength_z"].fillna(0)
        + cfg.attraction_w_liquidity * day["liquidity_z"].fillna(0)
        + cfg.attraction_w_volatility * day["volatility_z"].fillna(0)
        + cfg.attraction_w_valuation * day["valuation_cheapness_z"].fillna(0)
    )


def snapshot_with_cfg(
    date: pd.Timestamp,
    features: pd.DataFrame,
    cfg: base.Config,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = [
        "main_net_flow",
        "avg_amount",
        "momentum_z",
        "volatility_z",
        "liquidity_z",
        "flow_strength_z",
    ]
    day = (
        features[features["date"] == date]
        .dropna(subset=required)
        .drop_duplicates("symbol")
        .set_index("symbol")
    )
    if len(day) < cfg.min_cross_section:
        raise ValueError("有效横截面不足")

    day = day.copy()
    day["attraction_score"] = attraction_score(day, cfg)
    day["attractiveness"] = np.exp(day["attraction_score"].clip(-4, 4))
    distance = base.build_distance(date, day, features, cfg)
    flow = base.gravity_flows(day, distance, cfg)

    result = day.copy()
    result["inferred_inflow"] = flow.sum(axis=0)
    result["inferred_outflow"] = flow.sum(axis=1)
    result["net_migration"] = result["inferred_inflow"] - result["inferred_outflow"]
    result["migration_pressure"] = (
        result["net_migration"] / result["avg_amount"].replace(0, np.nan)
    )
    return result.sort_values("migration_pressure", ascending=False), flow


def valid_dates(features: pd.DataFrame, cfg: base.Config) -> pd.Index:
    valid = features.dropna(
        subset=["main_net_flow", "flow_strength", "momentum", "volatility", "avg_amount"]
    )
    counts = valid.groupby("date")["symbol"].nunique()
    return counts[counts >= cfg.min_cross_section].index.sort_values()


def rank_ic(x: pd.Series, y: pd.Series) -> float:
    return base.rank_ic(x, y)


def summarize_ic(ic: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    if ic.empty:
        return pd.DataFrame()
    rows = []
    grouper = groups[0] if len(groups) == 1 else groups
    for key, g in ic.groupby(grouper, dropna=False):
        keys = (key,) if len(groups) == 1 else tuple(key)
        values = g["rank_ic"].dropna()
        row = dict(zip(groups, keys))
        row["observations"] = len(values)
        row["mean_rank_ic"] = values.mean()
        row["median_rank_ic"] = values.median()
        row["positive_ratio"] = (values > 0).mean() if len(values) else np.nan
        std = values.std(ddof=1)
        row["ic_std"] = std
        row["ic_ir"] = values.mean() / std if len(values) > 1 and std > 1e-12 else np.nan
        row["t_stat"] = (
            values.mean() / (std / np.sqrt(len(values)))
            if len(values) > 1 and std > 1e-12
            else np.nan
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values(groups)


def multi_horizon_test(features: pd.DataFrame, cfg: base.Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    predictions = []
    for date in valid_dates(features, cfg):
        try:
            summary, _ = snapshot_with_cfg(date, features, cfg)
        except ValueError:
            continue
        day = summary.reset_index()
        predictions.append(day)
        for h in HORIZONS:
            col = f"forward_return_{h}d"
            rows.append(
                {
                    "date": date,
                    "horizon": h,
                    "rank_ic": rank_ic(day["migration_pressure"], day[col]),
                    "n": day[["migration_pressure", col]].dropna().shape[0],
                }
            )
    return (
        pd.concat(predictions, ignore_index=True) if predictions else pd.DataFrame(),
        pd.DataFrame(rows),
    )


def ablation_definitions(cfg: base.Config) -> list[dict[str, object]]:
    financial = replace(
        cfg,
        distance_w_corr=0.55,
        distance_w_factor=0.45,
        distance_w_sector=0.0,
        distance_w_valuation=0.0,
        attraction_w_momentum=0.40,
        attraction_w_flow=0.40,
        attraction_w_liquidity=0.20,
        attraction_w_volatility=0.0,
        attraction_w_valuation=0.0,
    )
    sector = replace(
        financial,
        distance_w_corr=0.45,
        distance_w_factor=0.35,
        distance_w_sector=0.20,
    )
    valuation = replace(
        sector,
        distance_w_corr=0.35,
        distance_w_factor=0.30,
        distance_w_sector=0.15,
        distance_w_valuation=0.20,
        attraction_w_valuation=0.15,
    )
    return [
        {"model": "A_momentum", "kind": "direct", "weights": {"momentum_z": 1.0}, "cfg": cfg},
        {"model": "B_momentum_flow", "kind": "direct", "weights": {"momentum_z": 0.5, "flow_strength_z": 0.5}, "cfg": cfg},
        {
            "model": "C_momentum_flow_liquidity",
            "kind": "direct",
            "weights": {"momentum_z": 0.4, "flow_strength_z": 0.4, "liquidity_z": 0.2},
            "cfg": cfg,
        },
        {"model": "D_gravity_financial", "kind": "gravity", "weights": {}, "cfg": financial},
        {"model": "E_gravity_sector", "kind": "gravity", "weights": {}, "cfg": sector},
        {"model": "F_gravity_valuation", "kind": "gravity", "weights": {}, "cfg": valuation},
        {"model": "G_full_migration", "kind": "gravity", "weights": {}, "cfg": cfg},
    ]


def direct_signal(day: pd.DataFrame, weights: Mapping[str, float]) -> pd.Series:
    signal = pd.Series(0.0, index=day.index)
    for col, weight in weights.items():
        signal = signal + weight * day[col].fillna(0)
    return signal


def portfolio_metrics(returns: pd.Series) -> dict[str, float]:
    r = returns.dropna()
    if r.empty:
        return {"annual_return": np.nan, "annual_volatility": np.nan, "sharpe": np.nan, "max_drawdown": np.nan}
    nav = (1 + r).cumprod()
    years = len(r) / 252
    annual = nav.iloc[-1] ** (1 / years) - 1 if years > 0 and nav.iloc[-1] > 0 else np.nan
    std = r.std(ddof=1)
    sharpe = r.mean() / std * np.sqrt(252) if len(r) > 1 and std > 1e-12 else np.nan
    drawdown = nav / nav.cummax() - 1
    return {
        "annual_return": float(annual),
        "annual_volatility": float(std * np.sqrt(252)),
        "sharpe": float(sharpe),
        "max_drawdown": float(drawdown.min()),
    }


def run_ablation(features: pd.DataFrame, cfg: base.Config) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ic_rows = []
    portfolio_rows = []
    dates = valid_dates(features, cfg)

    for definition in ablation_definitions(cfg):
        model = str(definition["model"])
        kind = str(definition["kind"])
        model_cfg = definition["cfg"]
        weights = definition["weights"]
        previous: set[str] | None = None

        for date in dates:
            day = (
                features[features["date"] == date]
                .drop_duplicates("symbol")
                .set_index("symbol")
                .dropna(
                    subset=[
                        "main_net_flow",
                        "avg_amount",
                        "momentum_z",
                        "flow_strength_z",
                        "liquidity_z",
                        "volatility_z",
                    ]
                )
            )
            if len(day) < cfg.min_cross_section:
                continue

            if kind == "direct":
                scored = day.copy()
                scored["signal"] = direct_signal(scored, weights)
            else:
                try:
                    scored, _ = snapshot_with_cfg(date, features, model_cfg)
                except ValueError:
                    continue
                scored["signal"] = scored["migration_pressure"]

            for h in HORIZONS:
                col = f"forward_return_{h}d"
                ic_rows.append(
                    {
                        "date": date,
                        "model": model,
                        "horizon": h,
                        "rank_ic": rank_ic(scored["signal"], scored[col]),
                        "n": scored[["signal", col]].dropna().shape[0],
                    }
                )

            ranked = scored.sort_values("signal", ascending=False)
            n = min(cfg.top_n, max(1, len(ranked) // 2))
            holdings = set(ranked.head(n).index.astype(str))
            turnover = np.nan if previous is None else 1 - len(previous & holdings) / max(1, n)
            previous = holdings
            top_ret = ranked.head(n)["forward_return_1d"].mean()
            eq_ret = ranked["forward_return_1d"].mean()
            portfolio_rows.append(
                {
                    "date": date,
                    "model": model,
                    "top_n_return": top_ret,
                    "equal_weight_return": eq_ret,
                    "excess_return": top_ret - eq_ret,
                    "turnover": turnover,
                }
            )

    daily_ic = pd.DataFrame(ic_rows)
    portfolio = pd.DataFrame(portfolio_rows)
    summary = summarize_ic(daily_ic, ["model", "horizon"])

    metrics = []
    for model, g in portfolio.groupby("model") if not portfolio.empty else []:
        metrics.append(
            {
                "model": model,
                **portfolio_metrics(g["top_n_return"]),
                "avg_turnover": g["turnover"].mean(),
                "mean_top_n_return": g["top_n_return"].mean(),
                "mean_excess_return": g["excess_return"].mean(),
            }
        )
    if metrics:
        summary = summary.merge(pd.DataFrame(metrics), on="model", how="left")
    return summary, daily_ic, portfolio


def save_outputs(
    raw: pd.DataFrame,
    predictions: pd.DataFrame,
    multi_ic: pd.DataFrame,
    ablation: pd.DataFrame,
    ablation_daily: pd.DataFrame,
    ablation_portfolio: pd.DataFrame,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output_dir / "stock_capital_migration_research_predictions.csv", index=False, encoding="utf-8-sig")
    multi_ic.to_csv(output_dir / "stock_capital_migration_multi_ic.csv", index=False, encoding="utf-8-sig")
    summarize_ic(multi_ic, ["horizon"]).to_csv(
        output_dir / "stock_capital_migration_multi_ic_summary.csv", index=False, encoding="utf-8-sig"
    )
    ablation.to_csv(output_dir / "stock_capital_migration_ablation.csv", index=False, encoding="utf-8-sig")
    ablation_daily.to_csv(output_dir / "stock_capital_migration_ablation_daily_ic.csv", index=False, encoding="utf-8-sig")
    ablation_portfolio.to_csv(output_dir / "stock_capital_migration_ablation_portfolio.csv", index=False, encoding="utf-8-sig")

    coverage = (
        raw.groupby("symbol")
        .agg(
            first_date=("date", "min"),
            last_date=("date", "max"),
            price_rows=("date", "size"),
            flow_rows=("main_net_flow", "count"),
            valuation_rows=("valuation_date", "count"),
        )
        .reset_index()
    )
    coverage.to_csv(output_dir / "stock_capital_migration_data_coverage.csv", index=False, encoding="utf-8-sig")


def print_results(multi_ic: pd.DataFrame, ablation: pd.DataFrame, data_dir: Path) -> None:
    print(f"\n数据缓存目录：{data_dir}")
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stock Capital Migration Research")
    parser.add_argument(
        "--start-date",
        default=(pd.Timestamp.today() - pd.DateOffset(years=2)).strftime("%Y%m%d"),
    )
    parser.add_argument("--end-date", default=pd.Timestamp.today().strftime("%Y%m%d"))
    parser.add_argument("--top-n", type=int, default=3)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--skip-ablation", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = base.Config(top_n=max(1, args.top_n))
    raw = load_data_cached(
        base.DEFAULT_UNIVERSE,
        args.start_date,
        args.end_date,
        cfg,
        args.data_dir,
        args.offline,
        args.refresh_cache,
    )
    features = add_forward_returns(base.add_features(raw, cfg))
    predictions, multi_ic = multi_horizon_test(features, cfg)

    if args.skip_ablation:
        ablation = pd.DataFrame()
        ablation_daily = pd.DataFrame()
        ablation_portfolio = pd.DataFrame()
    else:
        ablation, ablation_daily, ablation_portfolio = run_ablation(features, cfg)

    save_outputs(
        raw,
        predictions,
        multi_ic,
        ablation,
        ablation_daily,
        ablation_portfolio,
        args.output_dir,
    )
    print_results(multi_ic, ablation, args.data_dir)


if __name__ == "__main__":
    main()
