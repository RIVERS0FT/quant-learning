# VeighNa 自动化稳健性测试

## 目标

将手工点击 CTA 回测界面的流程改成 Python 批量回测，自动完成：

- 样本内/样本外测试
- 参数扰动测试
- 多标的泛化测试
- 手续费与滑点压力测试
- 结果汇总到 CSV

VeighNa 的 `BacktestingEngine` 可以直接通过 Python 设置回测参数、加载本地数据库、运行策略并返回统计指标，因此 GUI 回测可以迁移为可复现脚本。

## 当前候选参数

```python
BASE_SETTING = {
    "atr_length": 21,
    "atr_ma_length": 6,
    "rsi_length": 6,
    "rsi_entry": 19,
    "trailing_percent": 14.0,
    "capital": 1_000_000,
    "position_percent": 1.0,
    "buy_price_offset": 0.01,
    "lot_size": 100,
}
```

## 自动化回测核心

```python
from datetime import datetime

from vnpy.trader.constant import Interval
from vnpy_ctastrategy.backtesting import BacktestingEngine

from strategies.atr_rsi_long_position_strategy import AtrRsiLongPositionStrategy


def run_backtest(
    vt_symbol: str,
    start: datetime,
    end: datetime,
    setting: dict,
    rate: float = 3 / 10000,
    slippage: float = 0.02,
    capital: int = 1_000_000,
) -> dict:
    engine = BacktestingEngine()

    engine.set_parameters(
        vt_symbol=vt_symbol,
        interval=Interval.DAILY,
        start=start,
        end=end,
        rate=rate,
        slippage=slippage,
        size=1,
        pricetick=0.01,
        capital=capital,
    )

    engine.add_strategy(
        AtrRsiLongPositionStrategy,
        setting,
    )

    engine.load_data()
    engine.run_backtesting()

    df = engine.calculate_result()
    stats = engine.calculate_statistics(df, output=False)

    return stats
```

## 样本外测试

训练期只用于找到参数，验证期和测试期禁止继续调参。

```python
PERIODS = {
    "train": (datetime(2015, 1, 1), datetime(2021, 12, 31)),
    "validation": (datetime(2022, 1, 1), datetime(2024, 12, 31)),
    "test": (datetime(2025, 1, 1), datetime(2026, 8, 19)),
}
```

重点比较：

- `annual_return`
- `max_ddpercent`
- `sharpe_ratio`
- `return_drawdown_ratio`
- `total_trade_count`

如果样本内很好、样本外快速崩溃，应优先判断为过拟合风险，而不是继续调参数。

## 参数扰动测试

不要只测试最优点，要测试最优点附近是否形成参数平台。

例如当前 `rsi_entry=19`，测试：

```python
[15, 17, 19, 21, 23]
```

当前 `trailing_percent=14`，测试：

```python
[10, 12, 14, 16, 18]
```

如果只有 `19/14` 表现异常优秀，而附近参数全部失效，则过拟合风险较高。

## 多标的泛化测试

同一组参数直接用于多个股票，不允许逐股票重新优化参数。

示例：

```python
SYMBOLS = [
    "600519.SSE",
    "000858.SZSE",
    "600036.SSE",
    "601318.SSE",
    "000333.SZSE",
]
```

如果策略只在一个标的有效，应将结论限定为标的特定策略，而不是普遍有效策略。

## 成本压力测试

例如固定参数后测试不同滑点：

```python
SLIPPAGES = [0.01, 0.02, 0.05, 0.10]
```

以及不同手续费：

```python
RATES = [
    3 / 10000,
    6 / 10000,
    9 / 10000,
]
```

策略在成本增加后仍能保持正的风险调整收益，说明稳健性更高。

## 判断过拟合的核心标准

一个候选策略更可信时通常同时满足：

1. 样本外仍然有效。
2. 参数附近存在较宽的平台，而不是孤立尖峰。
3. 多个标的具有一定泛化能力。
4. 不同市场阶段均有合理表现。
5. 提高手续费和滑点后仍可接受。
6. 收益不是由极少数交易贡献。
7. 测试区间和参数选择在运行前固定。

自动化测试的目标不是找到最高年化收益，而是尽快淘汰脆弱策略。
