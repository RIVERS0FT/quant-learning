# -*- coding: utf-8 -*-

from pathlib import Path

import akshare as ak
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ==============================
# 配置区
# ==============================
# 你原脚本使用的是 sh600584；如果你要回测贵州茅台，请改为 sh600519。
MAIN_SYMBOL = "sh600584"
START_DATE = "20200101"
END_DATE = pd.Timestamp.today().strftime("%Y%m%d")
ADJUST = "qfq"

# 单边交易成本：示例按 0.1% 处理。真实交易应拆分佣金、印花税、滑点等。
COST_RATE = 0.0006

# MA20 / MA60
MA_SHORT = 20
MA_LONG = 60

# Momentum 参数扫描：比较不同回看周期。
MOMENTUM_WINDOWS = [5, 10, 20, 40, 60, 120, 250]
# 综合策略图只保留一个代表周期，避免曲线过多。
PRIMARY_MOMENTUM_WINDOW = 20

# Donchian Breakout：20 日新高入场，10 日新低离场
BREAKOUT_ENTRY_WINDOW = 20
BREAKOUT_EXIT_WINDOW = 10

# Z-Score Mean Reversion：低于均值 1.5 个标准差入场，回到均值离场
ZSCORE_WINDOW = 20
ZSCORE_ENTRY = -1.5
ZSCORE_EXIT = 0.0

# Bollinger Bands：跌破下轨入场，回到中轨离场
BB_WINDOW = 20
BB_K = 2.0

# Pairs Trading
# 这里只给一个“示例配对”，不代表二者已经通过协整检验。
# 正式研究应先做相关性、协整、稳定性检验后再决定交易对。
PAIR_SYMBOL = "sh603986"
PAIR_WINDOW = 60
PAIR_ENTRY_Z = 2.0
PAIR_EXIT_Z = 0.5

# Factor Investing
# 这里使用价格/成交量可直接得到的技术因子做一个简化横截面多因子组合。
# 如果要做价值、质量、盈利能力等基本面因子，需要额外接入财务与估值数据。
FACTOR_UNIVERSE = [
    "sh600584",
    "sh603986",
    "sh600519",
    "sh600036",
    "sz000333",
    "sz300750",
]
FACTOR_MOMENTUM_WINDOW = 60
FACTOR_VOL_WINDOW = 20
FACTOR_TREND_WINDOW = 20
FACTOR_TOP_N = 3
FACTOR_REBALANCE_DAYS = 5


# ==============================
# 数据与通用工具
# ==============================
def fetch_daily(symbol: str) -> pd.DataFrame:
    """获取 A 股前复权日线数据，并转换为统一格式。"""
    df = ak.stock_zh_a_daily(
        symbol=symbol,
        start_date=START_DATE,
        end_date=END_DATE,
        adjust=ADJUST,
    )

    if df.empty:
        raise RuntimeError(f"{symbol} 没有获取到数据，请检查网络、代码或稍后重试")

    required = ["date", "open", "high", "low", "close", "volume"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise RuntimeError(f"{symbol} 返回数据缺少字段：{missing}")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["close"]).copy()
    return df


def stateful_long_signal(entry: pd.Series, exit_: pd.Series) -> pd.Series:
    """
    long/flat 状态机：
    - 空仓时满足 entry -> 持有
    - 持有时满足 exit_ -> 空仓
    输出的是“当日收盘后得到的信号状态”，真正持仓会在外部 shift(1)。
    """
    state = 0.0
    out = []

    entry = entry.fillna(False)
    exit_ = exit_.fillna(False)

    for date in entry.index:
        if state == 0.0 and bool(entry.loc[date]):
            state = 1.0
        elif state == 1.0 and bool(exit_.loc[date]):
            state = 0.0
        out.append(state)

    return pd.Series(out, index=entry.index, dtype=float)


def stateful_pair_signal(
    zscore: pd.Series,
    entry_z: float,
    exit_z: float,
) -> pd.Series:
    """
    配对交易状态机：
    +1: 多主标的 / 空配对标的
    -1: 空主标的 / 多配对标的
     0: 空仓

    注意：A 股个股直接卖空受限，因此这更接近研究型/理论型回测。
    """
    state = 0.0
    out = []

    for value in zscore:
        if pd.isna(value):
            out.append(state)
            continue

        if state == 0.0:
            if value <= -entry_z:
                state = 1.0
            elif value >= entry_z:
                state = -1.0
        else:
            if abs(value) <= exit_z:
                state = 0.0

        out.append(state)

    return pd.Series(out, index=zscore.index, dtype=float)


def long_flat_return(
    asset_return: pd.Series,
    position: pd.Series,
    cost_rate: float,
) -> pd.Series:
    """计算 long/flat 策略收益，仓位变化时扣除简化交易成本。"""
    position = position.reindex(asset_return.index).fillna(0.0)
    turnover = position.diff().abs().fillna(position.abs())
    return position * asset_return - turnover * cost_rate


def nav_from_returns(strategy_return: pd.Series) -> pd.Series:
    """把日收益序列转成净值。"""
    return (1.0 + strategy_return.fillna(0.0)).cumprod()


def evaluate(nav: pd.Series) -> dict:
    """常用策略评价指标。"""
    nav = nav.dropna()
    if len(nav) < 2:
        return {
            "累计收益率": np.nan,
            "年化收益率": np.nan,
            "年化波动率": np.nan,
            "最大回撤": np.nan,
            "夏普比率": np.nan,
            "Calmar比率": np.nan,
        }

    returns = nav.pct_change().dropna()
    total_return = nav.iloc[-1] / nav.iloc[0] - 1.0

    years = len(returns) / 252.0
    annual_return = (
        (nav.iloc[-1] / nav.iloc[0]) ** (1.0 / years) - 1.0
        if years > 0
        else np.nan
    )

    annual_vol = returns.std() * np.sqrt(252)
    return_std = returns.std()
    sharpe = (
        returns.mean() / return_std * np.sqrt(252)
        if return_std > 0
        else np.nan
    )

    rolling_max = nav.cummax()
    drawdown = nav / rolling_max - 1.0
    max_drawdown = drawdown.min()

    calmar = (
        annual_return / abs(max_drawdown)
        if pd.notna(max_drawdown) and max_drawdown != 0
        else np.nan
    )

    return {
        "累计收益率": float(total_return),
        "年化收益率": float(annual_return),
        "年化波动率": float(annual_vol),
        "最大回撤": float(max_drawdown),
        "夏普比率": float(sharpe),
        "Calmar比率": float(calmar),
    }


def print_metrics_table(metrics: dict[str, dict]) -> pd.DataFrame:
    """打印并返回统一指标表。"""
    table = pd.DataFrame(metrics).T

    pct_cols = ["累计收益率", "年化收益率", "年化波动率", "最大回撤"]
    display = table.copy()
    for col in pct_cols:
        display[col] = display[col].map(
            lambda x: f"{x:.2%}" if pd.notna(x) else "NaN"
        )

    for col in ["夏普比率", "Calmar比率"]:
        display[col] = display[col].map(
            lambda x: f"{x:.3f}" if pd.notna(x) else "NaN"
        )

    print("\n========== 策略评价 ==========")
    print(display.to_string())
    return table


# Okabe-Ito 风格的色弱友好配色。
# 同时使用不同线型，避免只依靠颜色区分曲线。
COLORBLIND_COLORS = [
    "#0072B2",  # blue
    "#E69F00",  # orange
    "#009E73",  # bluish green
    "#56B4E9",  # sky blue
    "#CC79A7",  # reddish purple
    "#D55E00",  # vermillion
    "#666666",  # dark gray
]
LINE_STYLES = ["-", "-.", ":", (0, (5, 2)), (0, (3, 1, 1, 1)), (0, (7, 2)), (0, (1, 1))]


def plot_nav(nav_df: pd.DataFrame, title: str, filename: str) -> Path:
    """使用色弱友好的“颜色 + 线型”双重编码保存并展示净值曲线。"""
    fig, ax = plt.subplots(figsize=(13, 7))

    strategy_i = 0
    for name in nav_df.columns:
        series = nav_df[name].dropna()
        if series.empty:
            continue

        is_benchmark = name == "BuyHold" or "Benchmark" in name
        if is_benchmark:
            color = "#000000"
            linestyle = "--"
            linewidth = 2.4
        else:
            color = COLORBLIND_COLORS[strategy_i % len(COLORBLIND_COLORS)]
            linestyle = LINE_STYLES[strategy_i % len(LINE_STYLES)]
            linewidth = 1.8
            strategy_i += 1

        ax.plot(
            series.index,
            series.values,
            label=name,
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
        )

    ax.set_title(title)
    ax.set_ylabel("Net Asset Value")
    ax.set_xlabel("date")
    ax.grid(True, alpha=0.35)
    ax.legend()
    plt.tight_layout()

    chart_path = Path(__file__).with_name(filename)
    plt.savefig(chart_path, dpi=150)
    print(f"回测图已保存：{chart_path}")
    plt.show()
    return chart_path


# ==============================
# 1. 单标的策略
# ==============================
def build_single_asset_strategies(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    在同一只股票上回测：
    - Buy & Hold
    - MA20/MA60
    - Momentum
    - Breakout
    - Z-Score Mean Reversion
    - Bollinger Bands
    """
    out = df.copy()
    out["stock_return"] = out["close"].pct_change().fillna(0.0)

    # ---------- Buy & Hold ----------
    out["BuyHold"] = nav_from_returns(out["stock_return"])

    # ---------- MA20 / MA60 ----------
    out["ma_short"] = out["close"].rolling(MA_SHORT).mean()
    out["ma_long"] = out["close"].rolling(MA_LONG).mean()
    ma_signal = (out["ma_short"] > out["ma_long"]).astype(float)
    ma_signal = ma_signal.where(out["ma_long"].notna(), 0.0)
    out["ma_position"] = ma_signal.shift(1).fillna(0.0)
    out["ma_return"] = long_flat_return(
        out["stock_return"], out["ma_position"], COST_RATE
    )
    out["MA20_MA60"] = nav_from_returns(out["ma_return"])

    # ---------- Momentum（综合图使用 20 日代表周期） ----------
    momentum_col = f"momentum_{PRIMARY_MOMENTUM_WINDOW}"
    momentum_pos_col = f"{momentum_col}_position"
    momentum_ret_col = f"{momentum_col}_return"
    momentum_nav_col = f"Momentum_{PRIMARY_MOMENTUM_WINDOW}"

    out[momentum_col] = (
        out["close"] / out["close"].shift(PRIMARY_MOMENTUM_WINDOW) - 1.0
    )
    momentum_signal = (out[momentum_col] > 0).astype(float)
    momentum_signal = momentum_signal.where(out[momentum_col].notna(), 0.0)
    out[momentum_pos_col] = momentum_signal.shift(1).fillna(0.0)
    out[momentum_ret_col] = long_flat_return(
        out["stock_return"], out[momentum_pos_col], COST_RATE
    )
    out[momentum_nav_col] = nav_from_returns(out[momentum_ret_col])

    # ---------- Breakout ----------
    # 使用“昨日及更早”的区间高低点作为阈值，避免把当日高低价直接放入阈值。
    out["breakout_upper"] = (
        out["high"].shift(1).rolling(BREAKOUT_ENTRY_WINDOW).max()
    )
    out["breakout_lower"] = (
        out["low"].shift(1).rolling(BREAKOUT_EXIT_WINDOW).min()
    )
    breakout_entry = out["close"] > out["breakout_upper"]
    breakout_exit = out["close"] < out["breakout_lower"]
    breakout_state = stateful_long_signal(breakout_entry, breakout_exit)
    out["breakout_position"] = breakout_state.shift(1).fillna(0.0)
    out["breakout_return"] = long_flat_return(
        out["stock_return"], out["breakout_position"], COST_RATE
    )
    out["Breakout"] = nav_from_returns(out["breakout_return"])

    # ---------- Z-Score Mean Reversion ----------
    out["z_mean"] = out["close"].rolling(ZSCORE_WINDOW).mean()
    out["z_std"] = out["close"].rolling(ZSCORE_WINDOW).std()
    out["zscore"] = (out["close"] - out["z_mean"]) / out["z_std"]

    z_entry = out["zscore"] <= ZSCORE_ENTRY
    z_exit = out["zscore"] >= ZSCORE_EXIT
    z_state = stateful_long_signal(z_entry, z_exit)
    out["zscore_position"] = z_state.shift(1).fillna(0.0)
    out["zscore_return"] = long_flat_return(
        out["stock_return"], out["zscore_position"], COST_RATE
    )
    out["ZScoreMeanReversion"] = nav_from_returns(out["zscore_return"])

    # ---------- Bollinger Bands ----------
    out["bb_mid"] = out["close"].rolling(BB_WINDOW).mean()
    out["bb_std"] = out["close"].rolling(BB_WINDOW).std()
    out["bb_upper"] = out["bb_mid"] + BB_K * out["bb_std"]
    out["bb_lower"] = out["bb_mid"] - BB_K * out["bb_std"]

    bb_entry = out["close"] < out["bb_lower"]
    bb_exit = out["close"] >= out["bb_mid"]
    bb_state = stateful_long_signal(bb_entry, bb_exit)
    out["bb_position"] = bb_state.shift(1).fillna(0.0)
    out["bb_return"] = long_flat_return(
        out["stock_return"], out["bb_position"], COST_RATE
    )
    out["BollingerBands"] = nav_from_returns(out["bb_return"])

    nav_cols = [
        "BuyHold",
        "MA20_MA60",
        f"Momentum_{PRIMARY_MOMENTUM_WINDOW}",
        "Breakout",
        "ZScoreMeanReversion",
        "BollingerBands",
    ]
    nav_df = out[nav_cols].copy()
    return out, nav_df


# ==============================
# 2. Momentum 参数扫描
# ==============================
def backtest_momentum_windows(
    df: pd.DataFrame,
    windows: list[int],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    """
    在同一标的上比较多个 Momentum 回看周期。

    交易规则：
    - Momentum_N = close / close.shift(N) - 1
    - Momentum_N > 0：下一交易日持有
    - Momentum_N <= 0：下一交易日空仓

    为了公平比较 5/10/.../250 日参数，所有参数都从最长回看周期
    首次可用的共同日期开始评价，并在共同起点统一从空仓、净值 1.0 开始。
    这样可以避免 Momentum_250 因前 250 日没有信号而天然吃亏。
    """
    if not windows:
        raise ValueError("Momentum 参数列表不能为空")

    windows = sorted(set(int(window) for window in windows))
    if windows[0] <= 0:
        raise ValueError("Momentum 回看周期必须为正整数")

    max_window = max(windows)
    if len(df) <= max_window + 2:
        raise RuntimeError(
            f"数据只有 {len(df)} 行，不足以测试最长 Momentum_{max_window}"
        )

    out = df.copy()
    out["stock_return"] = out["close"].pct_change().fillna(0.0)

    for window in windows:
        momentum_col = f"momentum_{window}"
        signal_col = f"momentum_{window}_signal"
        position_col = f"momentum_{window}_position"

        out[momentum_col] = out["close"] / out["close"].shift(window) - 1.0
        out[signal_col] = (out[momentum_col] > 0).astype(float)
        out[signal_col] = out[signal_col].where(out[momentum_col].notna(), 0.0)

        # 当日收盘得到信号，下一交易日执行。
        out[position_col] = out[signal_col].shift(1).fillna(0.0)

    # 共同评价起点：最长回看周期首次拥有完整历史数据的日期。
    common_start = out.index[max_window]
    common_index = out.loc[common_start:].index
    common_stock_return = out.loc[common_index, "stock_return"].copy()

    # 第一行仅作为统一净值基准，不计入当天收益。
    common_stock_return.iloc[0] = 0.0

    nav_data: dict[str, pd.Series] = {}
    metrics: dict[str, dict] = {}

    buyhold_nav = nav_from_returns(common_stock_return)
    buyhold_nav.name = "BuyHold"
    nav_data["BuyHold"] = buyhold_nav

    buyhold_metrics = evaluate(buyhold_nav)
    buyhold_metrics["持仓比例"] = 1.0
    buyhold_metrics["仓位切换次数"] = 0
    metrics["BuyHold"] = buyhold_metrics

    for window in windows:
        position_col = f"momentum_{window}_position"
        name = f"Momentum_{window}"

        position = out.loc[common_index, position_col].copy()

        # 所有参数统一从共同起点的空仓状态开始。
        # 若第二天应持仓，long_flat_return 会正常扣除一次开仓成本。
        position.iloc[0] = 0.0

        strategy_return = long_flat_return(
            common_stock_return,
            position,
            COST_RATE,
        )
        strategy_return.iloc[0] = 0.0

        strategy_nav = nav_from_returns(strategy_return)
        strategy_nav.name = name
        nav_data[name] = strategy_nav

        strategy_metrics = evaluate(strategy_nav)
        strategy_metrics["持仓比例"] = float(position.mean())
        strategy_metrics["仓位切换次数"] = int(
            (position.diff().abs().fillna(0.0) > 0).sum()
        )
        metrics[name] = strategy_metrics

        # 保存共同评价区间内真正用于回测的仓位和收益。
        out.loc[common_index, f"momentum_{window}_test_position"] = position
        out.loc[common_index, f"momentum_{window}_test_return"] = strategy_return

    nav_df = pd.DataFrame(nav_data, index=common_index)
    metrics_table = pd.DataFrame(metrics).T

    return out, nav_df, metrics_table, common_start


def print_momentum_metrics_table(metrics_table: pd.DataFrame) -> None:
    """打印 Momentum 参数扫描结果。"""
    display = metrics_table.copy()

    for col in ["累计收益率", "年化收益率", "年化波动率", "最大回撤", "持仓比例"]:
        display[col] = display[col].map(
            lambda x: f"{x:.2%}" if pd.notna(x) else "NaN"
        )

    for col in ["夏普比率", "Calmar比率"]:
        display[col] = display[col].map(
            lambda x: f"{x:.3f}" if pd.notna(x) else "NaN"
        )

    display["仓位切换次数"] = display["仓位切换次数"].map(
        lambda x: f"{int(x)}" if pd.notna(x) else "NaN"
    )

    print("\n========== Momentum 参数扫描 ==========")
    print(display.to_string())


# ==============================
# 3. Pairs Trading
# ==============================
def backtest_pairs(main_df: pd.DataFrame, pair_symbol: str) -> tuple[pd.DataFrame, pd.Series]:
    """
    使用滚动 hedge ratio + spread Z-Score 的简化配对交易。

    说明：
    1. beta 使用滚动协方差 / 方差估计，不使用未来数据。
    2. 信号 shift(1) 后执行。
    3. 该策略包含空头方向，真实 A 股个股交易需要融券能力。
    4. 交易对正式使用前应做协整与稳定性检验。
    """
    pair_df = fetch_daily(pair_symbol)

    pair = pd.concat(
        [
            main_df["close"].rename("main_close"),
            pair_df["close"].rename("pair_close"),
        ],
        axis=1,
        join="inner",
    ).dropna()

    pair["main_return"] = pair["main_close"].pct_change().fillna(0.0)
    pair["pair_return"] = pair["pair_close"].pct_change().fillna(0.0)

    pair["log_main"] = np.log(pair["main_close"])
    pair["log_pair"] = np.log(pair["pair_close"])

    rolling_cov = pair["log_main"].rolling(PAIR_WINDOW).cov(pair["log_pair"])
    rolling_var = pair["log_pair"].rolling(PAIR_WINDOW).var()
    pair["beta"] = rolling_cov / rolling_var.replace(0.0, np.nan)

    pair["spread"] = pair["log_main"] - pair["beta"] * pair["log_pair"]
    pair["spread_mean"] = pair["spread"].rolling(PAIR_WINDOW).mean()
    pair["spread_std"] = pair["spread"].rolling(PAIR_WINDOW).std()
    pair["spread_z"] = (
        (pair["spread"] - pair["spread_mean"]) / pair["spread_std"]
    )

    raw_signal = stateful_pair_signal(
        pair["spread_z"],
        entry_z=PAIR_ENTRY_Z,
        exit_z=PAIR_EXIT_Z,
    )

    # 收盘得到信号，下一交易日使用。
    pair["position"] = raw_signal.shift(1).fillna(0.0)
    pair["beta_exec"] = pair["beta"].shift(1)

    # 将两条腿按 gross exposure 归一化，避免 beta 大小时收益尺度变化过大。
    gross = 1.0 + pair["beta_exec"].abs()
    pair["spread_return"] = (
        pair["main_return"] - pair["beta_exec"] * pair["pair_return"]
    ) / gross
    pair["spread_return"] = pair["spread_return"].fillna(0.0)

    turnover = pair["position"].diff().abs().fillna(pair["position"].abs())
    pair["strategy_return"] = (
        pair["position"] * pair["spread_return"] - turnover * COST_RATE
    )
    pair["PairsTrading"] = nav_from_returns(pair["strategy_return"])

    return pair, pair["PairsTrading"]


# ==============================
# 4. Factor Investing
# ==============================
def cross_sectional_zscore(frame: pd.DataFrame) -> pd.DataFrame:
    """对每个交易日做横截面标准化。"""
    row_mean = frame.mean(axis=1)
    row_std = frame.std(axis=1).replace(0.0, np.nan)
    return frame.sub(row_mean, axis=0).div(row_std, axis=0)


def backtest_factor_investing(
    universe: list[str],
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """
    简化横截面多因子策略：

    FactorScore = 0.5 * Momentum + 0.3 * LowVol + 0.2 * Trend

    其中每个因子先在当日股票横截面上做 Z-Score 标准化。
    每隔 FACTOR_REBALANCE_DAYS 个交易日，买入得分最高的 FACTOR_TOP_N 只股票，等权持有。

    这是技术因子示例，不等于完整的基本面 Factor Investing。
    """
    close_map = {}

    for symbol in universe:
        try:
            data = fetch_daily(symbol)
            close_map[symbol] = data["close"]
            print(f"Factor 数据获取成功：{symbol}，{len(data)} 行")
        except Exception as exc:
            print(f"Factor 数据跳过 {symbol}：{exc}")

    if len(close_map) < 2:
        raise RuntimeError("Factor Investing 至少需要 2 只成功获取数据的股票")

    close = pd.concat(close_map, axis=1).sort_index()
    close = close.dropna(axis=1, how="all")

    returns = close.pct_change()

    momentum = close / close.shift(FACTOR_MOMENTUM_WINDOW) - 1.0
    low_vol = -returns.rolling(FACTOR_VOL_WINDOW).std()
    trend = close / close.rolling(FACTOR_TREND_WINDOW).mean() - 1.0

    z_momentum = cross_sectional_zscore(momentum)
    z_low_vol = cross_sectional_zscore(low_vol)
    z_trend = cross_sectional_zscore(trend)

    score = 0.5 * z_momentum + 0.3 * z_low_vol + 0.2 * z_trend

    # 用上一交易日收盘后的因子分数决定今天的组合，避免前视偏差。
    score_exec = score.shift(1)

    weights = pd.DataFrame(0.0, index=close.index, columns=close.columns)
    current_weights = pd.Series(0.0, index=close.columns)

    for i, date in enumerate(close.index):
        if i % FACTOR_REBALANCE_DAYS == 0:
            row = score_exec.loc[date].dropna()
            if not row.empty:
                top_n = min(FACTOR_TOP_N, len(row))
                selected = row.nlargest(top_n).index
                current_weights = pd.Series(0.0, index=close.columns)
                current_weights.loc[selected] = 1.0 / top_n

        weights.loc[date] = current_weights

    # 对无价格的股票权重归零，再重新归一化。
    valid_price = close.notna().astype(float)
    weights = weights * valid_price
    weight_sum = weights.sum(axis=1).replace(0.0, np.nan)
    weights = weights.div(weight_sum, axis=0).fillna(0.0)

    turnover = weights.diff().abs().sum(axis=1)
    turnover.iloc[0] = weights.iloc[0].abs().sum()

    factor_return = (weights * returns.fillna(0.0)).sum(axis=1)
    factor_return = factor_return - turnover * COST_RATE
    factor_nav = nav_from_returns(factor_return)
    factor_nav.name = "FactorInvesting"

    # 用同一股票池的等权组合做一个更公平的 benchmark。
    available = close.notna().astype(float)
    benchmark_weights = available.div(available.sum(axis=1), axis=0).fillna(0.0)
    benchmark_return = (benchmark_weights * returns.fillna(0.0)).sum(axis=1)
    benchmark_nav = nav_from_returns(benchmark_return)
    benchmark_nav.name = "FactorEqualWeightBenchmark"

    detail = pd.concat(
        {
            "close": close,
            "score": score,
            "weights": weights,
        },
        axis=1,
    )

    return detail, factor_nav, benchmark_nav


# ==============================
# 主程序
# ==============================
def main() -> None:
    print(f"主标的：{MAIN_SYMBOL}")
    print(f"数据区间：{START_DATE} 至 {END_DATE}")
    print(f"简化交易成本：{COST_RATE:.2%}")

    main_df = fetch_daily(MAIN_SYMBOL)
    print(
        f"主标的数据区间：{main_df.index.min():%Y-%m-%d} 至 "
        f"{main_df.index.max():%Y-%m-%d}"
    )
    print(f"主标的数据行数：{len(main_df)}")

    # ---------- 单标的策略 ----------
    single_detail, single_nav = build_single_asset_strategies(main_df)

    metrics = {
        name: evaluate(single_nav[name])
        for name in single_nav.columns
    }

    plot_nav(
        single_nav,
        title=f"{MAIN_SYMBOL}: Single-Asset Strategies vs Buy & Hold",
        filename="single_asset_strategies.png",
    )

    # ---------- Momentum 参数扫描 ----------
    try:
        (
            momentum_detail,
            momentum_nav,
            momentum_metrics_table,
            momentum_common_start,
        ) = backtest_momentum_windows(main_df, MOMENTUM_WINDOWS)

        print(
            f"\nMomentum 公平比较区间：{momentum_common_start:%Y-%m-%d} 至 "
            f"{momentum_nav.index.max():%Y-%m-%d}"
        )
        print_momentum_metrics_table(momentum_metrics_table)

        plot_nav(
            momentum_nav,
            title=f"{MAIN_SYMBOL}: Momentum Window Comparison",
            filename="momentum_window_comparison.png",
        )

        momentum_metrics_path = Path(__file__).with_name(
            "momentum_window_metrics.csv"
        )
        momentum_metrics_table.to_csv(
            momentum_metrics_path,
            encoding="utf-8-sig",
        )
        print(f"Momentum 参数指标已保存：{momentum_metrics_path}")

        momentum_detail_path = Path(__file__).with_name(
            "momentum_window_detail.csv"
        )
        momentum_detail.to_csv(
            momentum_detail_path,
            encoding="utf-8-sig",
        )
        print(f"Momentum 参数明细已保存：{momentum_detail_path}")

        momentum_only = momentum_metrics_table.drop(index="BuyHold")
        best_annual = momentum_only["年化收益率"].idxmax()
        best_sharpe = momentum_only["夏普比率"].idxmax()
        best_calmar = momentum_only["Calmar比率"].idxmax()
        best_drawdown = momentum_only["最大回撤"].idxmax()

        print("\n========== Momentum 样本内最佳参数 ==========")
        print(
            f"最高年化收益：{best_annual} "
            f"({momentum_only.loc[best_annual, '年化收益率']:.2%})"
        )
        print(
            f"最高夏普比率：{best_sharpe} "
            f"({momentum_only.loc[best_sharpe, '夏普比率']:.3f})"
        )
        print(
            f"最高 Calmar：{best_calmar} "
            f"({momentum_only.loc[best_calmar, 'Calmar比率']:.3f})"
        )
        print(
            f"最小最大回撤：{best_drawdown} "
            f"({momentum_only.loc[best_drawdown, '最大回撤']:.2%})"
        )
        print("注意：以上只是当前样本区间内的结果，不等于未来实盘最优参数。")

    except Exception as exc:
        print(f"Momentum 参数扫描跳过：{exc}")
        momentum_detail = None

    # ---------- Pairs Trading ----------
    try:
        pair_detail, pair_nav = backtest_pairs(main_df, PAIR_SYMBOL)
        metrics["PairsTrading"] = evaluate(pair_nav)

        plot_nav(
            pair_nav.to_frame(),
            title=f"Pairs Trading: {MAIN_SYMBOL} vs {PAIR_SYMBOL}",
            filename="pairs_trading.png",
        )
    except Exception as exc:
        print(f"Pairs Trading 跳过：{exc}")
        pair_detail = None

    # ---------- Factor Investing ----------
    try:
        factor_detail, factor_nav, factor_benchmark_nav = backtest_factor_investing(
            FACTOR_UNIVERSE
        )
        metrics["FactorInvesting"] = evaluate(factor_nav)
        metrics["FactorEqualWeightBenchmark"] = evaluate(factor_benchmark_nav)

        factor_plot = pd.concat(
            [factor_nav, factor_benchmark_nav],
            axis=1,
        )
        plot_nav(
            factor_plot,
            title="Factor Investing vs Equal-Weight Universe Benchmark",
            filename="factor_investing.png",
        )
    except Exception as exc:
        print(f"Factor Investing 跳过：{exc}")
        factor_detail = None

    # ---------- 统一评价 ----------
    metrics_table = print_metrics_table(metrics)

    metrics_path = Path(__file__).with_name("strategy_metrics.csv")
    metrics_table.to_csv(metrics_path, encoding="utf-8-sig")
    print(f"评价指标已保存：{metrics_path}")

    # 保存单标的详细结果，方便后续学习与分析。
    detail_path = Path(__file__).with_name("single_asset_strategy_detail.csv")
    single_detail.to_csv(detail_path, encoding="utf-8-sig")
    print(f"单标的详细数据已保存：{detail_path}")

    print("\n策略说明：")
    print("1. MA20/MA60：短均线高于长均线时持有。")
    print("2. Momentum：测试 5/10/20/40/60/120/250 日回看周期，过去 N 日收益为正时持有。")
    print("3. Breakout：突破 N 日高点入场，跌破较短周期低点离场。")
    print("4. ZScoreMeanReversion：价格显著低于均值时买入，回归均值后离场。")
    print("5. BollingerBands：跌破下轨买入，回到中轨离场。")
    print("6. PairsTrading：交易两个资产的相对价差回归，示例包含空头。")
    print("7. FactorInvesting：横截面多因子打分，定期买入排名靠前股票。")


if __name__ == "__main__":
    main()
