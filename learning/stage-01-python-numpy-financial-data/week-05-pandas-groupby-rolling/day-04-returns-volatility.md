# 第 5 周第 4 天：滚动收益率与滚动波动率

## 今日目标

- 掌握 1 日、5 日和 20 日收益率的计算。
- 理解历史波动率的统计含义。
- 能够计算 20 日滚动波动率和年化波动率。
- 能够识别收益率窗口与波动率窗口的差异。

## 一、多周期历史收益率

### 1 日收益率

```python
df["return_1d"] = (
    df.groupby("symbol")["close"]
      .pct_change(1)
)
```

公式：

$$
r_{t,1}
= \frac{P_t}{P_{t-1}} - 1
$$

### 5 日收益率

```python
df["return_5d"] = (
    df.groupby("symbol")["close"]
      .pct_change(5)
)
```

公式：

$$
r_{t,5}
= \frac{P_t}{P_{t-5}} - 1
$$

### 20 日收益率

```python
df["return_20d"] = (
    df.groupby("symbol")["close"]
      .pct_change(20)
)
```

公式：

$$
r_{t,20}
= \frac{P_t}{P_{t-20}} - 1
$$

## 二、多周期收益率不是日收益率相加

简单收益率需要复利连接。

假设连续两日收益率分别为 $r_1$ 和 $r_2$，两日累计收益率为：

$$
r_{1:2}
= (1+r_1)(1+r_2)-1
$$

而不是：

$$
r_1+r_2
$$

使用价格比值计算多周期收益率，可以自动得到正确的复利结果。

## 三、波动率的含义

波动率用于描述收益率围绕平均值的离散程度。

最近 $N$ 日收益率的样本标准差为：

$$
\sigma_{t,N}
= \sqrt{
\frac{1}{N-1}
\sum_{i=t-N+1}^{t}
(r_i-\bar r)^2
}
$$

其中：

- $r_i$：第 $i$ 日收益率。
- $\bar r$：窗口内平均收益率。
- $N-1$：样本标准差的分母。

波动率越高，表示近期收益率变化越剧烈，但不代表收益一定更高或更低。

## 四、计算 20 日滚动波动率

先计算日收益率：

```python
df["return_1d"] = (
    df.groupby("symbol")["close"]
      .pct_change()
)
```

再计算最近 20 个日收益率的标准差：

```python
df["volatility_20d"] = (
    df.groupby("symbol")["return_1d"]
      .transform(
          lambda x: x.rolling(
              window=20,
              min_periods=20,
          ).std()
      )
)
```

注意：因为每只股票第一天的 `return_1d` 是缺失值，所以第一条有效 20 日波动率通常需要至少 21 个价格数据。

## 五、年化波动率

如果假设一年有 252 个交易日，日波动率年化为：

$$
\sigma_{\text{annual}}
= \sigma_{\text{daily}}\sqrt{252}
$$

代码：

```python
import numpy as np


df["annual_volatility_20d"] = (
    df["volatility_20d"] * np.sqrt(252)
)
```

### 为什么乘以 $\sqrt{252}$

在独立同分布的简化假设下，多期收益的方差随时间线性增长：

$$
\operatorname{Var}(R_T)
= T\operatorname{Var}(r)
$$

标准差是方差的平方根，因此：

$$
\operatorname{Std}(R_T)
= \sqrt{T}\operatorname{Std}(r)
$$

真实市场收益并不完全独立同分布，因此年化波动率是一种常用近似，而不是绝对规律。

## 六、完整示例

```python
import numpy as np
import pandas as pd


np.random.seed(42)

symbols = ["000001", "000002", "000003"]
dates = pd.bdate_range("2026-01-01", periods=80)

rows = []
for symbol in symbols:
    daily_returns = np.random.normal(
        loc=0.0005,
        scale=0.02,
        size=len(dates),
    )
    close = 10 * np.cumprod(1 + daily_returns)

    for date, price in zip(dates, close):
        rows.append({
            "trade_date": date,
            "symbol": symbol,
            "close": price,
        })

df = pd.DataFrame(rows)
df = df.sort_values(
    ["symbol", "trade_date"]
).reset_index(drop=True)

df["return_1d"] = (
    df.groupby("symbol")["close"]
      .pct_change()
)

df["return_5d"] = (
    df.groupby("symbol")["close"]
      .pct_change(5)
)

df["return_20d"] = (
    df.groupby("symbol")["close"]
      .pct_change(20)
)

df["volatility_20d"] = (
    df.groupby("symbol")["return_1d"]
      .transform(
          lambda x: x.rolling(
              20,
              min_periods=20,
          ).std()
      )
)

df["annual_volatility_20d"] = (
    df["volatility_20d"] * np.sqrt(252)
)

print(df.tail())
```

## 七、手动验证波动率

选择某只股票的一个完整窗口：

```python
stock = (
    df[df["symbol"] == "000001"]
    .reset_index(drop=True)
)

manual_vol = stock.loc[1:20, "return_1d"].std()
calculated_vol = stock.loc[20, "volatility_20d"]

assert abs(manual_vol - calculated_vol) < 1e-12
```

这里使用索引 `1:20`，是因为索引 0 的日收益率为空。

## 八、找出高波动交易日

```python
high_vol_days = (
    df.dropna(subset=["volatility_20d"])
      .sort_values(
          ["symbol", "volatility_20d"],
          ascending=[True, False],
      )
      .groupby("symbol")
      .head(5)
)
```

观察以下字段：

```text
trade_date
symbol
return_1d
return_20d
volatility_20d
annual_volatility_20d
```

需要注意：滚动波动率反映最近一段时间，而不是单日涨跌。

## 九、波动率分析中的常见错误

### 错误 1：直接对价格计算标准差

```python
# 不推荐用作收益波动率
x.rolling(20).std()
```

价格标准差受股票价格单位影响，不能直接比较 5 元股票和 100 元股票的风险。

更合理的是对收益率计算标准差。

### 错误 2：忘记按股票分组

```python
# 会跨股票滚动
x.rolling(20).std()
```

必须确保滚动窗口只包含同一只股票。

### 错误 3：把波动率解释为下跌概率

高波动表示涨跌幅变化较大，既可能来自大涨，也可能来自大跌。

### 错误 4：忽略窗口长度

5 日波动率反应更快，但噪声更大；60 日波动率更平滑，但反应更慢。

## 十、今日练习

1. 计算 1 日、5 日和 20 日收益率。
2. 计算 20 日滚动波动率。
3. 计算年化波动率。
4. 手动验证至少一个 20 日波动率窗口。
5. 找出每只股票波动率最高的 5 个交易日。
6. 比较 5 日波动率与 20 日波动率的响应速度。
7. 观察高波动期是否通常伴随大幅上涨或下跌。

## 十一、今日输出

建议实现：

```python
import numpy as np
import pandas as pd


def add_return_features(
    df: pd.DataFrame,
    return_windows: tuple[int, ...] = (1, 5, 20),
    volatility_window: int = 20,
    annual_trading_days: int = 252,
    symbol_col: str = "symbol",
    date_col: str = "trade_date",
    price_col: str = "close",
) -> pd.DataFrame:
    """计算多周期收益率、滚动波动率和年化波动率。"""
    required = {symbol_col, date_col, price_col}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"缺少字段: {sorted(missing)}")

    if volatility_window <= 1:
        raise ValueError("volatility_window 必须大于 1")

    result = df.copy()
    result = result.sort_values(
        [symbol_col, date_col]
    ).reset_index(drop=True)

    for window in return_windows:
        if window <= 0:
            raise ValueError("收益率窗口必须为正整数")

        result[f"return_{window}d"] = (
            result.groupby(symbol_col)[price_col]
                  .pct_change(window)
        )

    if "return_1d" not in result.columns:
        result["return_1d"] = (
            result.groupby(symbol_col)[price_col]
                  .pct_change()
        )

    result[f"volatility_{volatility_window}d"] = (
        result.groupby(symbol_col)["return_1d"]
              .transform(
                  lambda x: x.rolling(
                      window=volatility_window,
                      min_periods=volatility_window,
                  ).std()
              )
    )

    result[f"annual_volatility_{volatility_window}d"] = (
        result[f"volatility_{volatility_window}d"]
        * np.sqrt(annual_trading_days)
    )

    return result
```

## 十二、检查清单

- [ ] 多周期收益率按股票分组计算。
- [ ] 波动率基于收益率而不是价格计算。
- [ ] 波动率窗口没有跨越不同股票。
- [ ] 明确使用样本标准差。
- [ ] 年化时使用了 $\sqrt{252}$。
- [ ] 已理解年化波动率依赖简化假设。
- [ ] 已手动验证至少一个滚动窗口。
