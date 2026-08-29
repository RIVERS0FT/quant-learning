# -*- coding: utf-8 -*-

from pathlib import Path

import akshare as ak
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# 东方财富日线接口当前会主动断开连接，因此使用已验证可用的新浪日线接口。
df = ak.stock_zh_a_daily(
    symbol="sh600584",
    start_date="20260101",
    end_date=pd.Timestamp.today().strftime("%Y%m%d"),
    adjust="qfq",
)

if df.empty:
    raise RuntimeError("没有获取到数据，请检查网络或稍后重试")

# 新浪接口已经返回英文列名：date/open/high/low/close/volume 等。
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").set_index("date")

for col in ["open", "close", "high", "low", "volume"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 计算 20 日、60 日均线。
df["ma20"] = df["close"].rolling(20).mean()
df["ma60"] = df["close"].rolling(60).mean()
df = df.dropna(subset=["ma20", "ma60"]).copy()

# MA20 高于 MA60 时产生持仓信号，并延迟一天执行以避免前视偏差。
df["signal"] = (df["ma20"] > df["ma60"]).astype(float)
df["position"] = df["signal"].shift(1).fillna(0)

# 计算含简化交易成本的策略收益。
df["stock_return"] = df["close"].pct_change().fillna(0)
cost_rate = 0.001
df["turnover"] = df["position"].diff().abs().fillna(df["position"].abs())
df["strategy_return"] = (
    df["position"] * df["stock_return"] - df["turnover"] * cost_rate
)

df["strategy_nav"] = (1 + df["strategy_return"]).cumprod()
df["benchmark_nav"] = (1 + df["stock_return"]).cumprod()

# 常用策略评价指标。
annual_return = df["strategy_nav"].iloc[-1] ** (252 / len(df)) - 1
annual_volatility = df["strategy_return"].std() * np.sqrt(252)
return_std = df["strategy_return"].std()
sharpe = (
    df["strategy_return"].mean() / return_std * np.sqrt(252)
    if return_std > 0
    else np.nan
)
drawdown = df["strategy_nav"] / df["strategy_nav"].cummax() - 1
max_drawdown = drawdown.min()

print(f"数据区间：{df.index.min():%Y-%m-%d} 至 {df.index.max():%Y-%m-%d}")
print(f"数据行数：{len(df)}")
print(f"策略年化收益：{annual_return:.2%}")
print(f"策略年化波动：{annual_volatility:.2%}")
print(f"夏普比率：{sharpe:.2f}")
print(f"最大回撤：{max_drawdown:.2%}")

ax = df[["strategy_nav", "benchmark_nav"]].plot(
    figsize=(12, 6),
    title="Kweichow Moutai: MA20/MA60 Strategy vs Buy & Hold",
    grid=True,
)
ax.set_ylabel("Net Asset Value")
plt.tight_layout()

chart_path = Path(__file__).with_name("maotai_backtest.png")
plt.savefig(chart_path, dpi=150)
print(f"回测图已保存：{chart_path}")
plt.show()

import numpy as np

def evaluate(nav):
    returns = nav.pct_change().dropna()

    total_return = nav.iloc[-1] / nav.iloc[0] - 1

    years = len(returns) / 252
    annual_return = (nav.iloc[-1] / nav.iloc[0]) ** (1 / years) - 1

    annual_vol = returns.std() * np.sqrt(252)

    sharpe = (
        returns.mean() / returns.std() * np.sqrt(252)
        if returns.std() != 0
        else np.nan
    )

    rolling_max = nav.cummax()
    drawdown = nav / rolling_max - 1
    max_drawdown = drawdown.min()

    calmar = (
        annual_return / abs(max_drawdown)
        if max_drawdown != 0
        else np.nan
    )

    return {
        "累计收益率": total_return,
        "年化收益率": annual_return,
        "年化波动率": annual_vol,
        "最大回撤": max_drawdown,
        "夏普比率": sharpe,
        "Calmar比率": calmar,
    }

strategy_metrics = evaluate(df["strategy_nav"])
benchmark_metrics = evaluate(df["benchmark_nav"])

print(strategy_metrics)
print(benchmark_metrics)