# 第 3 周第 2 天：`axis` 与聚合运算

## 今日目标

- 彻底理解 `axis=0` 与 `axis=1`。
- 批量计算每只股票的均值、最高价、最低价、收益率和波动率。
- 使用布尔数组统计上涨、下跌和平盘天数。
- 区分平均收益率与累计收益率。
- 初步理解总体标准差、样本标准差与年化指标。

---

## 一、`axis` 表示被压缩的维度

价格矩阵形状：

```text
(5, 3)
```

表示 5 个交易日、3 只股票。

```python
prices.mean(axis=0)
```

压缩第 0 维，也就是交易日维度，保留 3 列，得到每只股票一个结果：

```text
(3,)
```

```python
prices.mean(axis=1)
```

压缩第 1 维，也就是股票维度，保留 5 行，得到每天一个结果：

```text
(5,)
```

最实用的记忆方法：

- 想得到每只股票的结果，通常使用 `axis=0`；
- 想得到每天的结果，通常使用 `axis=1`。

---

## 二、不指定 axis

```python
prices.mean()
```

会把矩阵中所有价格混在一起计算一个平均值。

不同股票的绝对价格基数不同，所以这种整体价格均值通常金融意义有限。多资产分析更关注每只股票的统计量，或者同一天的收益率横截面。

---

## 三、按股票计算价格统计

```python
mean_prices = prices.mean(axis=0)
max_prices = prices.max(axis=0)
min_prices = prices.min(axis=0)
```

价格绝对区间：

```python
price_ranges = max_prices - min_prices
```

相对区间更适合比较不同价格基数的股票：

```python
relative_ranges = max_prices / min_prices - 1
```

最高价和最低价所在位置：

```python
max_indices = prices.argmax(axis=0)
min_indices = prices.argmin(axis=0)
```

索引从 0 开始，如需转换成“第几日”：

```python
max_days = max_indices + 1
min_days = min_indices + 1
```

---

## 四、收益率矩阵

```python
returns = prices[1:, :] / prices[:-1, :] - 1
```

形状：

```text
(收益观察期数量, 股票数量)
```

例如价格矩阵 `(5, 3)` 对应收益率矩阵 `(4, 3)`。

---

## 五、每只股票的平均收益率

```python
mean_returns = returns.mean(axis=0)
```

数学表达：

$$
\bar r_i=\frac{1}{T}\sum_{t=1}^{T}R_{t,i}
$$

结果中每只股票得到一个算术平均日收益率。

每日市场等权平均收益：

```python
market_mean_returns = returns.mean(axis=1)
```

它比每日股票平均价格更有意义，因为收益率消除了价格基数差异。

---

## 六、最大和最小单日收益率

```python
max_returns = returns.max(axis=0)
min_returns = returns.min(axis=0)
```

这些指标描述历史样本中的极端单日表现，但不能单独代表长期收益或风险。

---

## 七、上涨、下跌和平盘统计

```python
is_up = returns > 0
is_down = returns < 0
is_flat = returns == 0
```

每只股票的涨跌天数：

```python
up_days = is_up.sum(axis=0)
down_days = is_down.sum(axis=0)
flat_days = is_flat.sum(axis=0)
```

每个收益区间上涨的股票数量：

```python
up_assets_by_day = is_up.sum(axis=1)
```

上涨比例：

```python
up_ratio = is_up.mean(axis=0)
```

因为布尔值参与计算时，`True=1`、`False=0`。

每只股票应满足：

```python
assert np.all(
    up_days + down_days + flat_days == returns.shape[0]
)
```

---

## 八、波动率

收益率标准差常用于衡量波动率：

```python
volatility = returns.std(axis=0)
```

波动率描述收益率围绕平均值的离散程度，同时包含向上和向下波动。高波动不等于一定亏损，但表示结果更加不稳定。

### 总体标准差

```python
returns.std(axis=0, ddof=0)
```

方差分母为 $n$。

### 样本标准差

```python
returns.std(axis=0, ddof=1)
```

方差分母为 $n-1$。历史收益通常被视为总体分布的样本，所以量化研究中经常使用 `ddof=1`。

---

## 九、年化指标初步

A 股日频研究常近似使用一年 252 个交易日。

线性年化平均收益率：

$$
\mu_{annual}=252\mu_{daily}
$$

```python
annualized_return = mean_returns * 252
```

年化波动率：

$$
\sigma_{annual}=\sigma_{daily}\sqrt{252}
$$

```python
annualized_volatility = volatility * np.sqrt(252)
```

短样本年化会产生夸张且不可靠的结果。现阶段重点是理解公式与数组方向。

---

## 十、平均收益率不等于累计收益率

若两期收益率是 `+10%` 与 `-10%`：

$$
\frac{10\%-10\%}{2}=0
$$

但累计净值：

$$
1.10\times0.90=0.99
$$

最终亏损 1%。

累计收益率：

```python
cumulative_returns = np.prod(1 + returns, axis=0) - 1
```

在没有分红、复权等复杂因素时，也等于：

```python
prices[-1, :] / prices[0, :] - 1
```

验证：

```python
assert np.allclose(
    np.prod(1 + returns, axis=0) - 1,
    prices[-1] / prices[0] - 1,
)
```

---

## 十一、聚合函数速查

| 目标 | 代码 |
|---|---|
| 每只股票平均收益率 | `returns.mean(axis=0)` |
| 每天市场平均收益率 | `returns.mean(axis=1)` |
| 每只股票最大收益率 | `returns.max(axis=0)` |
| 每只股票最小收益率 | `returns.min(axis=0)` |
| 每只股票样本波动率 | `returns.std(axis=0, ddof=1)` |
| 每只股票上涨天数 | `(returns > 0).sum(axis=0)` |
| 每天上涨股票数量 | `(returns > 0).sum(axis=1)` |
| 每只股票上涨比例 | `(returns > 0).mean(axis=0)` |
| 每只股票累计收益率 | `np.prod(1 + returns, axis=0) - 1` |

---

## 十二、最小综合示例

```python
import numpy as np

prices = np.array(
    [
        [10.00, 20.00, 30.00],
        [10.20, 19.80, 30.60],
        [10.10, 20.40, 30.30],
        [10.50, 20.80, 31.20],
        [10.80, 20.50, 31.80],
    ],
    dtype=np.float64,
)

returns = prices[1:] / prices[:-1] - 1

statistics = {
    "mean_return": returns.mean(axis=0),
    "max_return": returns.max(axis=0),
    "min_return": returns.min(axis=0),
    "volatility": returns.std(axis=0, ddof=1),
    "up_days": (returns > 0).sum(axis=0),
    "up_ratio": (returns > 0).mean(axis=0),
    "cumulative_return": np.prod(1 + returns, axis=0) - 1,
}

for name, values in statistics.items():
    print(name, values)
```

循环只负责格式化输出，核心金融计算仍然是向量化的。

---

## 今日检查清单

- [ ] 能从“压缩维度”的角度解释 `axis`。
- [ ] 能判断聚合结果的形状。
- [ ] 能批量计算每只股票的均值、最大值和最小值。
- [ ] 能统计上涨、下跌和平盘天数。
- [ ] 能解释波动率的含义。
- [ ] 能区分 `ddof=0` 与 `ddof=1`。
- [ ] 能区分平均收益率与累计收益率。