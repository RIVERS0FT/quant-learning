# 第 5 周第 2 天：`shift` 与时间序列对齐

## 今日目标

- 理解 `shift()` 只移动数据位置，不直接计算指标。
- 掌握滞后变量、领先变量和未来收益标签的构造方法。
- 能够手动计算收益率并与 `pct_change()` 结果核对。
- 明确历史特征与未来标签的边界。

## 一、`shift()` 的作用

`shift()` 用于将一列数据沿行方向移动。

```python
series.shift(1)
```

表示数据向下移动 1 行，因此当前行可以看到上一行的值。

```python
series.shift(-1)
```

表示数据向上移动 1 行，因此当前行可以看到下一行的值。

在多股票数据中，必须先按股票分组：

```python
df["close_lag1"] = (
    df.groupby("symbol")["close"]
      .shift(1)
)
```

否则可能把上一只股票的价格移动到下一只股票中。

## 二、构造历史变量

### 上一日收盘价

```python
df["close_lag1"] = (
    df.groupby("symbol")["close"]
      .shift(1)
)
```

### 前两日收盘价

```python
df["close_lag2"] = (
    df.groupby("symbol")["close"]
      .shift(2)
)
```

### 上一日成交量

```python
df["volume_lag1"] = (
    df.groupby("symbol")["volume"]
      .shift(1)
)
```

滞后变量只使用当前时点以前的信息，因此通常可以作为研究特征。

## 三、手动计算 1 日收益率

先取得上一日收盘价：

```python
df["close_lag1"] = (
    df.groupby("symbol")["close"]
      .shift(1)
)
```

再计算：

```python
df["return_1d_manual"] = (
    df["close"] / df["close_lag1"] - 1
)
```

简单收益率公式：

$$
r_t = \frac{P_t}{P_{t-1}} - 1
$$

与 `pct_change()` 的结果比较：

```python
df["return_1d_pct"] = (
    df.groupby("symbol")["close"]
      .pct_change()
)
```

核对两列是否一致：

```python
import numpy as np

mask = df["return_1d_manual"].notna()

assert np.allclose(
    df.loc[mask, "return_1d_manual"],
    df.loc[mask, "return_1d_pct"],
)
```

## 四、构造未来价格

### 下一交易日收盘价

```python
df["close_future1"] = (
    df.groupby("symbol")["close"]
      .shift(-1)
)
```

### 未来第 5 个交易日收盘价

```python
df["close_future5"] = (
    df.groupby("symbol")["close"]
      .shift(-5)
)
```

这些字段包含未来信息，只能用于研究标签或事后评估。

## 五、构造未来收益标签

### 未来 1 日收益率

```python
df["future_return_1d"] = (
    df.groupby("symbol")["close"]
      .shift(-1) / df["close"] - 1
)
```

对应公式：

$$
r_{t \rightarrow t+1}
= \frac{P_{t+1}}{P_t} - 1
$$

### 未来 5 日收益率

```python
df["future_return_5d"] = (
    df.groupby("symbol")["close"]
      .shift(-5) / df["close"] - 1
)
```

对应公式：

$$
r_{t \rightarrow t+5}
= \frac{P_{t+5}}{P_t} - 1
$$

它表示：在当前交易日收盘买入，并在未来第 5 个交易日收盘卖出时的收益率。

## 六、历史收益与未来收益的区别

### 历史收益率

```python
df["return_5d"] = (
    df.groupby("symbol")["close"]
      .pct_change(5)
)
```

含义：当前价格相对于 5 个交易日前价格的变化。

$$
r_{t,5}
= \frac{P_t}{P_{t-5}} - 1
$$

### 未来收益率

```python
df["future_return_5d"] = (
    df.groupby("symbol")["close"]
      .shift(-5) / df["close"] - 1
)
```

含义：未来第 5 个交易日价格相对于当前价格的变化。

$$
r_{t \rightarrow t+5}
= \frac{P_{t+5}}{P_t} - 1
$$

核心区别：

- 历史收益率可以作为特征。
- 未来收益率只能作为标签或评价结果。
- 将未来收益率直接作为交易信号会造成未来数据泄漏。

## 七、完整示例

```python
import numpy as np
import pandas as pd


df = pd.DataFrame({
    "trade_date": pd.to_datetime([
        "2026-01-01", "2026-01-02", "2026-01-03",
        "2026-01-04", "2026-01-05", "2026-01-06",
    ]),
    "symbol": ["000001"] * 6,
    "close": [10.0, 10.5, 10.2, 10.8, 11.0, 11.5],
    "volume": [100, 120, 90, 150, 130, 160],
})

df = df.sort_values(["symbol", "trade_date"])

df["close_lag1"] = (
    df.groupby("symbol")["close"]
      .shift(1)
)

df["return_1d_manual"] = (
    df["close"] / df["close_lag1"] - 1
)

df["return_1d_pct"] = (
    df.groupby("symbol")["close"]
      .pct_change()
)

df["future_return_1d"] = (
    df.groupby("symbol")["close"]
      .shift(-1) / df["close"] - 1
)

df["future_return_5d"] = (
    df.groupby("symbol")["close"]
      .shift(-5) / df["close"] - 1
)

mask = df["return_1d_manual"].notna()
assert np.allclose(
    df.loc[mask, "return_1d_manual"],
    df.loc[mask, "return_1d_pct"],
)

print(df)
```

## 八、为什么最后几行会出现缺失值

未来 1 日收益率需要下一交易日价格，因此每只股票最后 1 行缺失。

未来 5 日收益率需要未来第 5 个交易日价格，因此每只股票最后 5 行缺失。

检查方法：

```python
last_five = df.groupby("symbol").tail(5)
assert last_five["future_return_5d"].isna().all()
```

这些缺失值是由标签窗口自然产生的，不应随意填充为 0。

## 九、今日练习

1. 计算上一日、前 2 日和前 5 日收盘价。
2. 手动计算 1 日和 5 日历史收益率。
3. 与 `pct_change(1)` 和 `pct_change(5)` 比较。
4. 构造未来 1 日和未来 5 日收益率。
5. 检查每只股票最后几行的缺失值数量。
6. 尝试错误地对整张表使用 `shift(-1)`，观察跨股票污染。

## 十、今日输出

建议实现：

```python
import pandas as pd


def add_future_return(
    df: pd.DataFrame,
    periods: int = 5,
    price_col: str = "close",
    symbol_col: str = "symbol",
    date_col: str = "trade_date",
) -> pd.DataFrame:
    """按股票构造未来 N 日收益率标签。"""
    if periods <= 0:
        raise ValueError("periods 必须为正整数")

    required = {symbol_col, date_col, price_col}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"缺少字段: {sorted(missing)}")

    result = df.copy()
    result = result.sort_values(
        [symbol_col, date_col]
    ).reset_index(drop=True)

    future_price = (
        result.groupby(symbol_col)[price_col]
              .shift(-periods)
    )

    result[f"future_return_{periods}d"] = (
        future_price / result[price_col] - 1
    )

    return result
```

## 十一、检查清单

- [ ] `shift()` 在 `groupby("symbol")` 之后使用。
- [ ] 数据已经按股票代码和日期排序。
- [ ] 手动收益率与 `pct_change()` 结果一致。
- [ ] 未来收益率仅作为标签使用。
- [ ] 每只股票最后 $N$ 行的未来 $N$ 日收益率为空。
- [ ] 没有把未来缺失值错误填充为 0。
