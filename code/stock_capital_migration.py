# -*- coding: utf-8 -*-
"""Stock Capital Migration Model（股票资本迁移模型）

把股票视为“城市”、资金视为“人口”，使用 Gravity Model 推断资金从股票 i
向股票 j 的迁移：

    Flow(i -> j) ∝ Capital_i^alpha * Attractiveness_j^beta / D_ij^gamma

这里无法直接观察真实 A -> B，因此使用“主力净流出”作为源端可迁移资金预算，
再由金融距离和目标股票吸引力决定这部分资金的推断去向。

数据来源：
- AkShare stock_zh_a_hist：A 股日线
- AkShare stock_individual_fund_flow：个股主力资金流
- AkShare stock_value_em：历史 PE(TTM)、PB、PS、市值

估值数据按交易日向后对齐（merge_asof direction="backward"），因此任意历史时点
只使用该日或更早已经存在的估值记录，避免未来数据泄漏。

运行：
    python stock_capital_migration.py
    python stock_capital_migration.py --top-n 3 --no-plot

输出：
- stock_capital_migration_snapshot.csv
- stock_capital_migration_edges.csv
- stock_capital_migration_backtest.csv
- stock_capital_migration_ic.csv
- stock_capital_migration_valuation.csv
- stock_capital_migration_nav.png
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

try:
    import akshare as ak
except ImportError:
    ak = None

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_UNIVERSE: dict[str, dict[str, str]] = {
    "600519": {"name": "贵州茅台", "sector": "白酒"},
    "600036": {"name": "招商银行", "sector": "银行"},
    "600030": {"name": "中信证券", "sector": "证券"},
    "600584": {"name": "长电科技", "sector": "半导体"},
    "603986": {"name": "兆易创新", "sector": "半导体"},
    "300750": {"name": "宁德时代", "sector": "新能源"},
    "000333": {"name": "美的集团", "sector": "家电"},
    "002230": {"name": "科大讯飞", "sector": "AI"},
    "601857": {"name": "中国石油", "sector": "能源"},
    "600276": {"name": "恒瑞医药", "sector": "医药"},
}

VALUATION_RATIO_COLS = ["pe_ttm", "pb", "ps_ttm"]
VALUATION_DATA_COLS = [
    "valuation_date",
    "pe_ttm",
    "pb",
    "ps_ttm",
    "total_market_cap",
    "float_market_cap",
]


@dataclass(frozen=True)
class Config:
    momentum_window: int = 20
    volatility_window: int = 20
    liquidity_window: int = 20
    flow_window: int = 5
    corr_window: int = 60

    alpha: float = 1.0
    beta: float = 1.0
    gamma: float = 1.5

    # 金融距离权重。估值距离已经接入历史 PE/PB/PS。
    distance_w_corr: float = 0.40
    distance_w_sector: float = 0.15
    distance_w_factor: float = 0.25
    distance_w_valuation: float = 0.20
    min_distance: float = 0.05

    # 估值数据允许使用最近一个历史值，但不能向未来取值。
    valuation_max_staleness_days: int = 10
    valuation_min_coverage: float = 0.60

    attraction_w_momentum: float = 0.35
    attraction_w_flow: float = 0.35
    attraction_w_liquidity: float = 0.15
    attraction_w_volatility: float = -0.15
    # 估值越便宜，吸引力越高。设为 0 可只把估值用于“距离”。
    attraction_w_valuation: float = 0.15

    top_n: int = 3
    min_cross_section: int = 5
    impact_lambda: float = 1.0


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
            base = fetch_price(symbol, start_date, end_date).merge(
                fetch_flow(symbol),
                on="date",
                how="left",
            )
        except Exception as exc:
            failures.append(f"{symbol} {meta['name']}: {exc}")
            continue

        try:
            valuation = fetch_valuation(
                symbol,
                start_date,
                end_date,
                lookback_days=cfg.valuation_max_staleness_days,
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


def zscore(s: pd.Series) -> pd.Series:
    std = s.std(skipna=True, ddof=0)
    if pd.isna(std) or std <= 1e-12:
        return pd.Series(0.0, index=s.index)
    return (s - s.mean(skipna=True)) / std


def add_valuation_features(df: pd.DataFrame) -> pd.DataFrame:
    """构造日截面估值标准分与“便宜度”指标。"""
    df = df.copy()
    z_cols: list[str] = []

    for col in VALUATION_RATIO_COLS:
        raw = pd.to_numeric(df.get(col), errors="coerce")
        # PE/PB/PS 非正值不适合直接作为常规估值倍数比较。
        positive = raw.where(raw > 0)
        log_col = f"{col}_log"
        z_col = f"{col}_z"
        df[log_col] = np.log1p(positive)
        df[z_col] = df.groupby("date")[log_col].transform(zscore)
        z_cols.append(z_col)

    # 越低估值 -> 越高 cheapness。缺失指标按横截面中性值 0 处理。
    df["valuation_cheapness_z"] = -df[z_cols].mean(axis=1, skipna=True)
    df["valuation_cheapness_z"] = df["valuation_cheapness_z"].fillna(0.0)
    return df


def add_features(data: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    def per_symbol(g: pd.DataFrame) -> pd.DataFrame:
        g = g.copy().sort_values("date")
        g["return_1d"] = g["close"].pct_change()
        g["next_return"] = g["close"].shift(-1) / g["close"] - 1.0
        g["momentum"] = g["close"].pct_change(cfg.momentum_window)
        g["volatility"] = (
            g["return_1d"]
            .rolling(cfg.volatility_window)
            .std()
            * np.sqrt(252)
        )
        g["avg_amount"] = g["amount"].rolling(cfg.liquidity_window).mean()
        g["liquidity"] = np.log1p(g["avg_amount"].clip(lower=0))
        g["flow_ratio"] = (
            g["main_net_flow"] / g["amount"].replace(0, np.nan)
        )
        g["flow_strength"] = (
            g["flow_ratio"].rolling(cfg.flow_window).mean()
        )
        return g

    parts = [
        per_symbol(g)
        for _, g in data.groupby("symbol", sort=False)
    ]
    df = pd.concat(parts, ignore_index=True)

    for col in ["momentum", "volatility", "liquidity", "flow_strength"]:
        df[f"{col}_z"] = df.groupby("date")[col].transform(zscore)

    df = add_valuation_features(df)

    score = (
        cfg.attraction_w_momentum * df["momentum_z"]
        + cfg.attraction_w_flow * df["flow_strength_z"]
        + cfg.attraction_w_liquidity * df["liquidity_z"]
        + cfg.attraction_w_volatility * df["volatility_z"]
        + cfg.attraction_w_valuation * df["valuation_cheapness_z"]
    )
    df["attraction_score"] = score
    df["attractiveness"] = np.exp(score.clip(-4, 4))
    df["outflow_budget"] = (
        (-df["main_net_flow"]).clip(lower=0).fillna(0.0)
    )
    return df


def pairwise_euclidean(features: pd.DataFrame) -> pd.DataFrame:
    x = np.nan_to_num(features.to_numpy(float), nan=0.0)
    diff = x[:, None, :] - x[None, :, :]
    dist = np.sqrt(np.mean(diff**2, axis=2))
    out = pd.DataFrame(
        dist,
        index=features.index,
        columns=features.index,
    )
    values = out.to_numpy()[~np.eye(len(out), dtype=bool)]
    scale = np.nanpercentile(values, 95) if len(values) else 1.0
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = 1.0
    return (out / scale).clip(0, 1)


def valuation_distance_features(
    day: pd.DataFrame,
    cfg: Config,
) -> pd.DataFrame | None:
    """返回估值距离特征；覆盖不足时返回 None，让模型自动重新归一化权重。"""
    available_raw = [
        c for c in VALUATION_RATIO_COLS if c in day.columns
    ]
    if not available_raw:
        return None

    raw = day[available_raw].apply(
        pd.to_numeric,
        errors="coerce",
    )
    positive_mask = raw > 0
    coverage = positive_mask.any(axis=1).mean()
    if coverage < cfg.valuation_min_coverage:
        return None

    z_cols: list[str] = []
    for raw_col in available_raw:
        z_col = f"{raw_col}_z"
        if z_col not in day.columns:
            continue
        valid_count = positive_mask[raw_col].sum()
        if valid_count >= 3 and day[z_col].dropna().nunique() >= 2:
            z_cols.append(z_col)

    if not z_cols:
        return None

    return day[z_cols].fillna(0.0)


def build_distance(
    date: pd.Timestamp,
    day: pd.DataFrame,
    features: pd.DataFrame,
    cfg: Config,
) -> pd.DataFrame:
    symbols = day.index.tolist()

    trailing = features[
        (features["date"] <= date)
        & features["symbol"].isin(symbols)
    ].pivot(
        index="date",
        columns="symbol",
        values="return_1d",
    )
    corr = trailing.tail(cfg.corr_window).corr(
        min_periods=max(10, cfg.corr_window // 3)
    )
    corr = (
        corr.reindex(index=symbols, columns=symbols)
        .fillna(0)
        .clip(-1, 1)
    )
    d_corr = 0.5 * (1 - corr)

    sectors = day["sector"].astype(str).to_numpy()
    d_sector = pd.DataFrame(
        (sectors[:, None] != sectors[None, :]).astype(float),
        index=symbols,
        columns=symbols,
    )

    factor_cols = [
        "momentum_z",
        "volatility_z",
        "liquidity_z",
        "flow_strength_z",
    ]
    d_factor = pairwise_euclidean(
        day[factor_cols].fillna(0.0)
    )

    components: list[tuple[float, pd.DataFrame]] = [
        (cfg.distance_w_corr, d_corr),
        (cfg.distance_w_sector, d_sector),
        (cfg.distance_w_factor, d_factor),
    ]

    val_features = valuation_distance_features(day, cfg)
    if (
        val_features is not None
        and cfg.distance_w_valuation > 0
    ):
        d_valuation = pairwise_euclidean(val_features)
        components.append(
            (cfg.distance_w_valuation, d_valuation)
        )

    active = [(w, d) for w, d in components if w > 0]
    total_w = sum(w for w, _ in active)
    distance = sum(w * d for w, d in active) / total_w
    distance = distance.clip(lower=cfg.min_distance)
    np.fill_diagonal(distance.values, np.inf)
    return distance


def gravity_flows(
    day: pd.DataFrame,
    distance: pd.DataFrame,
    cfg: Config,
) -> pd.DataFrame:
    symbols = day.index.tolist()
    source = (
        day["outflow_budget"]
        .reindex(symbols)
        .fillna(0)
        .clip(lower=0)
        .to_numpy(float)
    )
    attraction = (
        day["attractiveness"]
        .reindex(symbols)
        .fillna(1)
        .clip(lower=1e-8)
        .to_numpy(float)
    )

    with np.errstate(
        divide="ignore",
        invalid="ignore",
        over="ignore",
    ):
        raw = (
            np.power(source, cfg.alpha)[:, None]
            * np.power(attraction, cfg.beta)[None, :]
            / np.power(
                distance.to_numpy(float),
                cfg.gamma,
            )
        )

    raw[~np.isfinite(raw)] = 0.0
    np.fill_diagonal(raw, 0.0)

    row_sum = raw.sum(axis=1, keepdims=True)
    weights = np.divide(
        raw,
        row_sum,
        out=np.zeros_like(raw),
        where=row_sum > 0,
    )
    flow = weights * source[:, None]
    return pd.DataFrame(
        flow,
        index=symbols,
        columns=symbols,
    )


def build_snapshot(
    date: pd.Timestamp,
    features: pd.DataFrame,
    cfg: Config,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = [
        "main_net_flow",
        "avg_amount",
        "momentum_z",
        "volatility_z",
        "liquidity_z",
        "flow_strength_z",
        "attractiveness",
    ]
    day = features[
        features["date"] == date
    ].dropna(subset=required)
    day = day.drop_duplicates("symbol").set_index("symbol")
    if len(day) < cfg.min_cross_section:
        raise ValueError("有效横截面不足")

    distance = build_distance(date, day, features, cfg)
    flow = gravity_flows(day, distance, cfg)

    result = day.copy()
    result["inferred_inflow"] = flow.sum(axis=0)
    result["inferred_outflow"] = flow.sum(axis=1)
    result["net_migration"] = (
        result["inferred_inflow"]
        - result["inferred_outflow"]
    )
    result["migration_pressure"] = (
        result["net_migration"]
        / result["avg_amount"].replace(0, np.nan)
    )
    result["predicted_price_pressure"] = (
        cfg.impact_lambda * result["migration_pressure"]
    )
    return (
        result.sort_values(
            "migration_pressure",
            ascending=False,
        ),
        flow,
    )


def flow_edges(
    flow: pd.DataFrame,
    day: pd.DataFrame,
    top_per_source: int = 3,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for source in flow.index:
        top_targets = (
            flow.loc[source]
            .sort_values(ascending=False)
            .head(top_per_source)
        )
        for target, value in top_targets.items():
            if value <= 0:
                continue
            rows.append(
                {
                    "source": source,
                    "source_name": day.loc[source, "name"],
                    "source_sector": day.loc[source, "sector"],
                    "target": target,
                    "target_name": day.loc[target, "name"],
                    "target_sector": day.loc[target, "sector"],
                    "inferred_flow": float(value),
                }
            )

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        "inferred_flow",
        ascending=False,
    )


def rank_ic(x: pd.Series, y: pd.Series) -> float:
    pair = pd.concat([x, y], axis=1).dropna()
    if len(pair) < 3:
        return np.nan
    xr = pair.iloc[:, 0].rank()
    yr = pair.iloc[:, 1].rank()
    if xr.nunique() < 2 or yr.nunique() < 2:
        return np.nan
    return float(xr.corr(yr))


def backtest(
    features: pd.DataFrame,
    cfg: Config,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    valid = features.dropna(
        subset=[
            "main_net_flow",
            "flow_strength",
            "momentum",
            "volatility",
            "avg_amount",
            "next_return",
        ]
    )
    counts = valid.groupby("date")["symbol"].nunique()
    dates = counts[
        counts >= cfg.min_cross_section
    ].index.sort_values()

    predictions: list[pd.DataFrame] = []
    ic_rows: list[dict[str, object]] = []
    portfolio_rows: list[dict[str, object]] = []

    for date in dates:
        try:
            summary, _ = build_snapshot(
                date,
                features,
                cfg,
            )
        except ValueError:
            continue

        day = summary.reset_index()
        predictions.append(day)
        ic_rows.append(
            {
                "date": date,
                "rank_ic": rank_ic(
                    day["migration_pressure"],
                    day["next_return"],
                ),
                "n": len(day),
            }
        )

        ranked = day.sort_values(
            "migration_pressure",
            ascending=False,
        )
        n = min(
            cfg.top_n,
            max(1, len(ranked) // 2),
        )
        top_ret = ranked.head(n)["next_return"].mean()
        bottom_ret = ranked.tail(n)["next_return"].mean()
        portfolio_rows.append(
            {
                "date": date,
                "top_n_return": top_ret,
                "bottom_n_return": bottom_ret,
                "long_short_return": (
                    top_ret - bottom_ret
                ),
                "equal_weight_return": (
                    ranked["next_return"].mean()
                ),
            }
        )

    pred_df = (
        pd.concat(predictions, ignore_index=True)
        if predictions
        else pd.DataFrame()
    )
    ic_df = pd.DataFrame(ic_rows)
    portfolio = pd.DataFrame(portfolio_rows)

    if not portfolio.empty:
        cols = [
            "top_n_return",
            "bottom_n_return",
            "long_short_return",
            "equal_weight_return",
        ]
        for col in cols:
            portfolio[f"{col}_nav"] = (
                1 + portfolio[col].fillna(0)
            ).cumprod()

    return pred_df, ic_df, portfolio


def save_results(
    raw: pd.DataFrame,
    latest: pd.DataFrame,
    edges: pd.DataFrame,
    predictions: pd.DataFrame,
    ic_df: pd.DataFrame,
    portfolio: pd.DataFrame,
    no_plot: bool,
) -> None:
    out = Path(__file__).resolve().parent

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
