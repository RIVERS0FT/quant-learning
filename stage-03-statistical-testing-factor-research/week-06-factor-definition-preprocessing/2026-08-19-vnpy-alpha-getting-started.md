# vnpy.alpha 上手：从单因子到 Alpha158

## 1. vnpy.alpha 是什么

`vnpy.alpha` 面向多因子、机器学习和截面选股研究，核心结构是：

```text
AlphaLab
  ↓
行情/成分股数据
  ↓
AlphaDataset
  ↓
因子 + Label + 数据处理
  ↓
因子分析 / AlphaModel
  ↓
预测信号
  ↓
AlphaStrategy / BacktestingEngine
```

VeighNa 4.4.0 中 `vnpy.alpha` 包含 dataset、model、strategy 和 AlphaLab。官方示例提供 XT/RQ 数据准备，以及 Alpha101、Lasso、LightGBM、MLP 研究工作流。

## 2. 第一阶段不要直接上机器学习

先研究一个简单的 20 日动量因子：

\[
Momentum_{20,t}=\frac{P_t}{P_{t-20}}-1
\]

预测目标可以定义为下一交易日开始后的未来 5 日收益：

\[
Y_t=\frac{P_{t+6}}{P_{t+1}}-1
\]

对应表达式：

```python
self.add_feature("mom20", "close / ts_delay(close, 20) - 1")
self.set_label("ts_delay(close, -6) / ts_delay(close, -1) - 1")
```

先验证因子的 IC、分层收益和稳定性，再进入多因子模型。

## 3. 建立 AlphaLab

```python
from vnpy.alpha import AlphaLab

lab = AlphaLab("./lab/demo")
```

AlphaLab 会建立 daily、minute、component、dataset、model、signal 等目录，并使用 Parquet 保存行情数据。

## 4. 使用当前 VeighNa Datafeed 下载少量股票做冒烟测试

```python
from datetime import datetime

from vnpy.alpha import AlphaLab
from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import HistoryRequest

lab = AlphaLab("./lab/demo")
datafeed = get_datafeed()
assert datafeed.init()

symbols = [
    ("600519", Exchange.SSE),
    ("000858", Exchange.SZSE),
    ("600036", Exchange.SSE),
    ("601318", Exchange.SSE),
    ("000333", Exchange.SZSE),
]

for symbol, exchange in symbols:
    req = HistoryRequest(
        symbol=symbol,
        exchange=exchange,
        interval=Interval.DAILY,
        start=datetime(2015, 1, 1),
        end=datetime(2026, 8, 18),
    )

    bars = datafeed.query_bar_history(req)
    if bars:
        lab.save_bar_data(bars)
```

这组股票只用于跑通流程，不适合作为正式截面研究股票池。正式研究应使用带历史成分变化的指数成分股数据，避免幸存者偏差。

## 5. 创建最简单的数据集

```python
from vnpy.alpha import AlphaDataset


class MomentumDataset(AlphaDataset):
    def __init__(self, df, train_period, valid_period, test_period):
        super().__init__(
            df=df,
            train_period=train_period,
            valid_period=valid_period,
            test_period=test_period,
        )

        self.add_feature(
            "mom20",
            "close / ts_delay(close, 20) - 1",
        )

        self.set_label(
            "ts_delay(close, -6) / ts_delay(close, -1) - 1"
        )
```

## 6. 明确训练集、验证集、测试集

例如：

```text
TRAIN  2015-01-01 ~ 2021-12-31
VALID  2022-01-01 ~ 2023-12-31
TEST   2024-01-01 ~ 2026-08-18
```

测试集必须冻结，不用于选参数。

## 7. 下一阶段：Alpha158 + Lasso

`vnpy.alpha` 当前内置 Alpha101、Alpha158，以及 Lasso、LightGBM、MLP 模型。建议顺序：

```text
单因子 Momentum20
→ 因子分析
→ Alpha158
→ Lasso
→ TEST 预测信号
→ 信号分层分析
→ AlphaStrategy 回测
→ LightGBM
```

Lasso 更适合作为第一个 ML 模型，因为模型简单、系数可解释，可以先判断哪些特征真正产生贡献。

## 8. 防止过拟合

- TEST 集不能参与选参数。
- 不要根据一次最高 IC 选择因子。
- 检查不同年份、不同股票池和不同市场环境。
- 检查因子参数附近是否存在稳定平台。
- 正式研究使用历史指数成分，而不是今天的成分股回填到过去。
- 记录失败实验，而不是只保存最好结果。

## 9. 当前最合适的学习任务

先完成一个完整的小闭环：

```text
TuShare / Datafeed
→ 5只股票
→ AlphaLab
→ Momentum20
→ 未来5日收益 Label
→ 因子分析
```

跑通以后，再扩大到沪深300历史成分并使用 Alpha158。

## 10. 环境验证

已确认 VeighNa 自带 Python 环境可以正常导入 `vnpy.alpha` 及其核心依赖：

```powershell
C:\veighna_studio\python.exe -c "from vnpy.alpha import AlphaLab; import polars, sklearn, alphalens; print('vnpy.alpha OK')"
```

输出：

```text
vnpy.alpha OK
```

说明当前 `vnpy.alpha` 研究环境已经可用。需要注意，后续安装依赖应始终使用 VeighNa 自带解释器：

```powershell
C:\veighna_studio\python.exe -m pip install <package>
```

不要直接使用系统 `pip install`，否则依赖可能被装到系统 Python 的用户目录，导致 VeighNa 环境无法导入。