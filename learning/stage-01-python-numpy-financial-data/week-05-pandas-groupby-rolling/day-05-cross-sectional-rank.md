# 第 5 周第 5 天：`rank` 与股票截面排名

## 今日目标

- 区分时间序列计算与截面计算。
- 掌握 `rank()` 的基本用法和常见参数。
- 能够计算每日收益率、动量、成交额和波动率排名。
- 能够使用百分位排名构造相对强弱指标。

## 一、两种计算方向

### 时间序列计算

比较同一只股票在不同日期的变化。

常见指标：

- 过去 5 日收益率。
- 过去 20 日收益率。
- 20 日移动平均线。
- 20 日滚动波动率。

分组方向：

```python
df.groupby("symbol")
```

### 截面计算

比较同一个交易日不同股票之间的相对位置。

常见指标：

- 当日涨幅排名。
- 20 日动量排名。
- 成交额排名。
- 波动率排名。

分组方向：

```python
df.groupby("trade_date")
```

核心思维：

```text
纵向按股票计算时间序列指标
横向按日期计算股票截面排名
```

## 二、计算每日收益率排名

```python
df["return_1d_rank"] = (
    df.groupby("trade_date")["return_1d"]
      .rank(
          ascending=False,
          method="average",
      )
)
```

参数解释：

- `ascending=False`：数值越大，名次越靠前。
- `method="average"`：相同数值使用并列名次的平均值。

例如：

```text
收益率     排名
5%         1
3%         2
3%         2
1%         4
```

两个 3% 并列时，原本占据第 2 和第 3 名，因此平均排名为 2.5。pandas 的具体结果会依照样本位置计算平均名次。

## 三、百分位排名

```python
df["return_20d_rank_pct"] = (
    df.groupby("trade_date")["return_20d"]
      .rank(
          ascending=True,
          pct=True,
          method="average",
      )
)
```

解释：

- 接近 1：在当日股票中数值较高。
- 接近 0：在当日股票中数值较低。
- 百分位排名便于比较不同交易日，即使每日股票数量不同。

当因子数值越大越好时，常用：

```python
ascending=True
```

这样最高值的百分位排名接近 1。

## 四、为什么普通排名和百分位排名不同

普通排名受到股票数量影响。

例如：

- 某日有 100 只股票，第 10 名属于前 10%。
- 某日有 5000 只股票，第 10 名属于前 0.2%。

百分位排名将名次缩放到相对位置，更适合跨日期比较。

## 五、常见排名方法

```python
method="average"
method="min"
method="max"
method="first"
method="dense"
```

### `average`

并列值使用平均名次，因子研究中常用。

### `min`

并列值都使用最小名次。

### `max`

并列值都使用最大名次。

### `first`

按照原始行顺序打破并列关系。结果依赖数据顺序，需要谨慎。

### `dense`

并列值使用同一名次，下一名不跳号。

## 六、多个截面指标

### 20 日动量排名

```python
df["momentum_rank_pct"] = (
    df.groupby("trade_date")["return_20d"]
      .rank(pct=True)
)
```

### 成交额排名

```python
df["amount_rank_pct"] = (
    df.groupby("trade_date")["amount"]
      .rank(pct=True)
)
```

成交额排名较高，通常表示当日流动性更强，但还需要结合股票市值、停牌和涨跌停状态分析。

### 波动率排名

如果希望低波动股票排名更高：

```python
df["low_vol_rank_pct"] = (
    df.groupby("trade_date")["volatility_20d"]
      .rank(
          ascending=False,
          pct=True,
      )
)
```

这里要仔细定义方向。

如果使用 `ascending=True`，高波动值的排名接近 1。

如果想让“低波动”因子得分越大越好，可以使用：

```python
df["low_vol_score"] = 1 - (
    df.groupby("trade_date")["volatility_20d"]
      .rank(pct=True)
)
```

## 七、筛选排名前 10% 的股票

```python
top_momentum = df[
    df["return_20d_rank_pct"] >= 0.9
]
```

注意：

- 排名靠前不等于未来必然上涨。
- 排名只是将连续因子转化为相对位置。
- 还需要使用未来收益率验证因子是否有效。

## 八、缺失值与排名

`rank()` 默认不会给缺失值排名。

```python
ranked = (
    df.groupby("trade_date")["return_20d"]
      .rank(pct=True)
)
```

当股票没有足够 20 日历史时，`return_20d` 为缺失值，对应排名也为空。

不要在不了解原因的情况下把缺失排名填充为 0，因为 0 会被误解为真实的最低排名。

## 九、完整示例

```python
import pandas as pd


df = pd.DataFrame({
    "trade_date": pd.to_datetime([
        "2026-01-05", "2026-01-05", "2026-01-05",
        "2026-01-06", "2026-01-06", "2026-01-06",
    ]),
    "symbol": [
        "000001", "000002", "000003",
        "000001", "000002", "000003",
    ],
    "return_1d": [0.03, -0.01, 0.02, 0.01, 0.04, -0.02],
    "return_20d": [0.12, 0.05, 0.20, 0.15, 0.08, 0.25],
    "amount": [1000, 3000, 2000, 1500, 4000, 2500],
    "volatility_20d": [0.02, 0.04, 0.03, 0.025, 0.045, 0.035],
})

df["return_1d_rank"] = (
    df.groupby("trade_date")["return_1d"]
      .rank(
          ascending=False,
          method="average",
      )
)

df["return_20d_rank_pct"] = (
    df.groupby("trade_date")["return_20d"]
      .rank(
          ascending=True,
          pct=True,
      )
)

df["amount_rank_pct"] = (
    df.groupby("trade_date")["amount"]
      .rank(pct=True)
)

df["low_vol_score"] = 1 - (
    df.groupby("trade_date")["volatility_20d"]
      .rank(pct=True)
)

print(df)
```

## 十、截面排名的手动检查

选择某个交易日：

```python
one_day = df[
    df["trade_date"] == pd.Timestamp("2026-01-05")
].sort_values("return_20d")

print(one_day[
    ["symbol", "return_20d", "return_20d_rank_pct"]
])
```

确认：

- 最低收益率的百分位最小。
- 最高收益率的百分位最大。
- 排名只在同一交易日内部比较。

## 十一、今日练习

1. 计算每日 1 日收益率普通排名。
2. 计算每日 20 日收益率百分位排名。
3. 计算每日成交额百分位排名。
4. 构造低波动得分，使低波动股票得分更高。
5. 找出每天 20 日收益率排名前 10% 的股票。
6. 比较绝对收益率和截面排名的区别。
7. 人为减少某些交易日的股票数量，观察普通排名与百分位排名的变化。

## 十二、今日输出

建议实现：

```python
import pandas as pd


def add_cross_sectional_rank(
    df: pd.DataFrame,
    factor_col: str,
    date_col: str = "trade_date",
    ascending: bool = True,
    pct: bool = True,
    method: str = "average",
    output_col: str | None = None,
) -> pd.DataFrame:
    """在每个交易日内部计算因子截面排名。"""
    required = {date_col, factor_col}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"缺少字段: {sorted(missing)}")

    result = df.copy()

    if output_col is None:
        suffix = "rank_pct" if pct else "rank"
        output_col = f"{factor_col}_{suffix}"

    result[output_col] = (
        result.groupby(date_col)[factor_col]
              .rank(
                  ascending=ascending,
                  pct=pct,
                  method=method,
              )
    )

    return result
```

## 十三、检查清单

- [ ] 时间序列计算按 `symbol` 分组。
- [ ] 截面排名按 `trade_date` 分组。
- [ ] 已明确因子方向是“越大越好”还是“越小越好”。
- [ ] 百分位排名没有跨日期计算。
- [ ] 缺失因子值没有被错误填充为真实排名。
- [ ] 已抽取至少一个交易日手动核验排名。
