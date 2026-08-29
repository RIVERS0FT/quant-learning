# 第 5 周第 3 天：`rolling` 与移动平均线

## 今日目标

- 理解滚动窗口的含义。
- 掌握 `rolling()`、`mean()`、`min_periods` 和 `transform()`。
- 能够按股票计算 5 日与 20 日移动平均线。
- 能够计算价格相对均线的偏离度。

## 一、什么是滚动窗口

滚动窗口表示：对每一个交易日，只使用最近固定数量的数据进行计算。

例如 5 日移动平均线在交易日 $t$ 的定义为：

$$
MA_{t,5}
= \frac{P_t + P_{t-1} + P_{t-2} + P_{t-3} + P_{t-4}}{5}
$$

更一般地，$N$ 日移动平均线为：

$$
MA_{t,N}
= \frac{1}{N}
\sum_{i=0}^{N-1} P_{t-i}
$$

滚动窗口每向后移动一个交易日，就移除最早的数据并加入最新的数据。

## 二、单只股票的滚动均值

```python
df["ma_5"] = (
    df["close"]
      .rolling(5)
      .mean()
)
```

但当 DataFrame 中包含多只股票时，必须先分组。

## 三、多股票移动平均线

### 5 日均线

```python
df["ma_5"] = (
    df.groupby("symbol")["close"]
      .transform(
          lambda x: x.rolling(5).mean()
      )
)
```

### 20 日均线

```python
df["ma_20"] = (
    df.groupby("symbol")["close"]
      .transform(
          lambda x: x.rolling(20).mean()
      )
)
```

这里使用 `transform()` 的原因是：滚动结果需要与原始 DataFrame 的每一行对齐。

## 四、`min_periods` 的作用

### 完整窗口

```python
x.rolling(
    window=5,
    min_periods=5,
).mean()
```

只有窗口中存在 5 个有效数据时才计算均值。

因此，5 日均线前 4 行通常为缺失值。

### 非完整窗口

```python
x.rolling(
    window=5,
    min_periods=1,
).mean()
```

第一天只有 1 个数据也会计算均值，第二天用 2 个数据计算，直到第 5 天才成为完整的 5 日均线。

### 量化研究中的注意事项

`min_periods=1` 虽然减少了缺失值，但早期指标的统计含义与完整窗口不同。

例如：

- 第 1 天的“5 日均线”实际只使用了 1 天数据。
- 第 3 天的“5 日均线”实际只使用了 3 天数据。
- 第 5 天以后才真正使用 5 天数据。

因此，因子研究中通常更推荐：

```python
rolling(window=5, min_periods=5)
```

## 五、均线偏离度

价格相对 20 日均线的偏离度：

```python
df["close_ma20_ratio"] = (
    df["close"] / df["ma_20"] - 1
)
```

对应公式：

$$
D_{t,20}
= \frac{P_t}{MA_{t,20}} - 1
$$

解释：

- 大于 0：当前价格位于 20 日均线上方。
- 小于 0：当前价格位于 20 日均线下方。
- 接近 0：当前价格接近 20 日均线。
- 绝对值较大：价格偏离均线较远。

均线偏离度可以描述趋势强弱，但不能单独证明未来一定上涨或下跌。

## 六、完整示例

```python
import pandas as pd


df = pd.DataFrame({
    "trade_date": pd.date_range(
        "2026-01-01",
        periods=25,
        freq="D",
    ),
    "symbol": ["000001"] * 25,
    "close": [
        10.0, 10.1, 10.2, 10.3, 10.4,
        10.5, 10.6, 10.7, 10.8, 10.9,
        11.0, 11.1, 11.2, 11.3, 11.4,
        11.5, 11.6, 11.7, 11.8, 11.9,
        12.0, 12.1, 12.2, 12.3, 12.4,
    ],
})

df = df.sort_values(["symbol", "trade_date"])

df["ma_5"] = (
    df.groupby("symbol")["close"]
      .transform(
          lambda x: x.rolling(
              window=5,
              min_periods=5,
          ).mean()
      )
)

df["ma_20"] = (
    df.groupby("symbol")["close"]
      .transform(
          lambda x: x.rolling(
              window=20,
              min_periods=20,
          ).mean()
      )
)

df["close_ma20_ratio"] = (
    df["close"] / df["ma_20"] - 1
)

print(df.tail(10))
```

## 七、验证滚动计算

可以手动验证第 5 行的 5 日均线：

```python
manual_ma5 = df.loc[0:4, "close"].mean()
calculated_ma5 = df.loc[4, "ma_5"]

assert abs(manual_ma5 - calculated_ma5) < 1e-12
```

检查每只股票前 19 行的 20 日均线：

```python
first_nineteen = (
    df.groupby("symbol")
      .head(19)
)

assert first_nineteen["ma_20"].isna().all()
```

## 八、绘制价格与均线

```python
import matplotlib.pyplot as plt

stock = df[df["symbol"] == "000001"]

plt.plot(
    stock["trade_date"],
    stock["close"],
    label="close",
)
plt.plot(
    stock["trade_date"],
    stock["ma_5"],
    label="ma_5",
)
plt.plot(
    stock["trade_date"],
    stock["ma_20"],
    label="ma_20",
)

plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

观察重点：

- 短期均线比长期均线更接近当前价格。
- 价格快速上涨时，5 日均线通常先于 20 日均线上升。
- 价格快速下跌时，5 日均线通常先于 20 日均线下降。

## 九、今日练习

1. 计算每只股票的 5 日和 20 日移动平均线。
2. 比较 `min_periods=1` 与 `min_periods=window` 的差异。
3. 计算收盘价相对 20 日均线的偏离度。
4. 找出每只股票偏离度最高和最低的 5 个交易日。
5. 绘制一只股票的收盘价、5 日均线和 20 日均线。
6. 手动验证至少一个滚动窗口结果。

## 十、今日输出

建议实现：

```python
import pandas as pd


def add_moving_average(
    df: pd.DataFrame,
    windows: tuple[int, ...] = (5, 20),
    price_col: str = "close",
    symbol_col: str = "symbol",
    date_col: str = "trade_date",
) -> pd.DataFrame:
    """按股票计算多个周期的移动平均线。"""
    required = {symbol_col, date_col, price_col}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"缺少字段: {sorted(missing)}")

    if not windows:
        raise ValueError("windows 不能为空")

    if any(window <= 0 for window in windows):
        raise ValueError("所有窗口必须为正整数")

    result = df.copy()
    result = result.sort_values(
        [symbol_col, date_col]
    ).reset_index(drop=True)

    for window in windows:
        result[f"ma_{window}"] = (
            result.groupby(symbol_col)[price_col]
                  .transform(
                      lambda x, w=window: x.rolling(
                          window=w,
                          min_periods=w,
                      ).mean()
                  )
        )

    if 20 in windows:
        result["close_ma20_ratio"] = (
            result[price_col] / result["ma_20"] - 1
        )

    return result
```

## 十一、检查清单

- [ ] 滚动计算前已按股票和日期排序。
- [ ] `rolling()` 没有跨越不同股票。
- [ ] 明确设置了 `min_periods`。
- [ ] 5 日均线前 4 行为空。
- [ ] 20 日均线前 19 行为空。
- [ ] 已手动验证至少一个窗口结果。
- [ ] 能解释均线偏离度的正负含义。
