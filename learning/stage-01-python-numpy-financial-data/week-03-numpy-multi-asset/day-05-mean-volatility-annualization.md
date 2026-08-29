# 第 3 周第 5 天：多资产均值、波动率与年化指标

## 今日目标

今天减少 Python 练习，重点理解：

1. 平均收益率的数学含义；
2. 波动率为什么使用收益率标准差；
3. 日频指标如何年化；
4. 缺失值条件下统计结果是否可靠；
5. 有效样本数量为什么必须与统计指标一起报告。

---

## 一、收益率矩阵

设多资产收益率矩阵：

$$
R\in\mathbb{R}^{T\times N}
$$

其中：

- $T$：收益观察期数量；
- $N$：股票数量；
- $R_{t,i}$：股票 $i$ 在第 $t$ 个观察期的收益率。

计算每只股票的时间序列统计量时，通常使用 `axis=0`。

---

## 二、算术平均收益率

股票 $i$ 的平均收益率：

$$
\bar R_i=\frac{1}{T}\sum_{t=1}^{T}R_{t,i}
$$

代码：

```python
mean_returns = returns.mean(axis=0)
```

它回答：

> 在样本期间内，每一期收益率平均是多少？

平均收益率常用于描述历史单期收益、估计期望收益和计算风险调整指标。

---

## 三、平均收益率不是累计收益率

若两期收益率是 `+10%` 和 `-10%`：

$$
\bar r=\frac{10\%-10\%}{2}=0
$$

但累计净值：

$$
1.1\times0.9=0.99
$$

累计收益率为 `-1%`。

平均收益率：

```python
returns.mean(axis=0)
```

累计收益率：

```python
np.prod(1 + returns, axis=0) - 1
```

两个指标不能混用。

---

## 四、平均收益率的局限

算术平均值容易受到极端值影响。例如：

```text
1%、1%、1%、20%
```

最后一个收益会明显抬高均值。

因此分析平均收益率时，还应检查：

- 中位数；
- 分位数；
- 极端收益；
- 样本长度；
- 数据区间是否一致。

---

## 五、波动率

量化研究中通常用收益率标准差衡量波动率。

总体标准差：

$$
\sigma_i=\sqrt{\frac{1}{n}\sum_{t=1}^{n}(R_{t,i}-\bar R_i)^2}
$$

样本标准差：

$$
s_i=\sqrt{\frac{1}{n-1}\sum_{t=1}^{n}(R_{t,i}-\bar R_i)^2}
$$

代码：

```python
daily_volatility = returns.std(
    axis=0,
    ddof=1,
)
```

历史收益通常被视为未来收益分布的样本，因此常使用 `ddof=1`。

---

## 六、波动率的含义

波动率描述收益率围绕均值波动得有多大。

它同时考虑：

- 向上的波动；
- 向下的波动。

因此高波动不一定表示亏损，但通常表示结果更不稳定。

波动率不是平均亏损，也不是最大回撤。后续还需学习下行波动率、最大回撤和 Sortino 比率。

---

## 七、样本数量与波动率可靠性

如果一只股票只有两个收益观察值，程序仍可能计算标准差，但统计意义很弱。

一般规律：

- 样本越少，均值与波动率估计越不稳定；
- 不同股票有效样本量不同，不应机械比较；
- 使用 `ddof=1` 时，至少需要两个有效观察值。

---

## 八、为什么需要年化

日、周、月收益率和波动率不能直接比较，需要统一到相同时间尺度。

A 股日频研究通常近似使用：

```text
一年 252 个交易日
```

该数字是研究约定，不代表每个自然年都精确有 252 个交易日。

---

## 九、线性年化平均收益率

$$
\mu_{annual}=252\mu_{daily}
$$

代码：

```python
annualized_returns = mean_daily_returns * 252
```

它回答：

> 如果样本平均日收益线性延续一年，大致对应多少收益？

该方法不考虑复利，短样本下可能产生夸张结果。

---

## 十、复利年化收益率

若样本期间最终净值为 $NAV_{final}$，收益观察期数量为 $n$：

$$
R_{annual}=NAV_{final}^{252/n}-1
$$

代码：

```python
annualized_return = (
    final_nav ** (252 / n_periods) - 1
)
```

它回答：

> 按样本期间实际复合增长速度折算到一年，大致是多少？

线性年化与复利年化回答的问题不同，研究报告必须说明所用方法。

---

## 十一、年化波动率

根号时间法则：

$$
\sigma_{annual}=\sigma_{daily}\sqrt{252}
$$

代码：

```python
annualized_volatility = (
    daily_volatility * np.sqrt(252)
)
```

原因：在简化假设下，方差随时间近似线性累加：

$$
\operatorname{Var}(R_{annual})
\approx
252\operatorname{Var}(r_{daily})
$$

标准差是方差的平方根，因此乘以 $\sqrt{252}$。

不要把波动率直接乘以 252。

---

## 十二、根号时间法则的前提

年化波动率近似依赖：

- 收益率关系较稳定；
- 自相关不强；
- 波动率没有剧烈变化；
- 不存在明显的波动聚集。

现实金融市场经常不完全满足这些条件，所以年化波动率是标准化估计，不是绝对真实风险。

---

## 十三、缺失值

普通均值遇到 `NaN`：

```python
returns.mean(axis=0)
```

对应股票的结果通常会成为 `NaN`。

忽略缺失值：

```python
mean_returns = np.nanmean(
    returns,
    axis=0,
)
```

忽略缺失值计算样本标准差：

```python
volatility = np.nanstd(
    returns,
    axis=0,
    ddof=1,
)
```

但忽略 `NaN` 不代表缺失问题已经解决。

---

## 十四、有效样本数量

```python
valid_counts = np.isfinite(
    returns
).sum(axis=0)
```

`np.isfinite` 会把以下值判定为无效：

- `NaN`；
- `inf`；
- `-inf`。

数学表达：

$$
n_i=\sum_{t=1}^{T}\mathbf{1}(R_{t,i}\text{ 有效})
$$

有效样本量必须与均值、波动率一起报告。

---

## 十五、最低样本要求

例如规定至少需要 60 个有效日收益：

```python
enough_data = valid_counts >= 60
```

样本不足的结果设为 `NaN`：

```python
mean_returns = np.where(
    enough_data,
    mean_returns,
    np.nan,
)
```

这比输出一个看似精确、实际极不稳定的数字更合理。

---

## 十六、比较多只股票的正确顺序

不要只看平均收益率大小。更合理的顺序：

1. 有效样本数量是否充足；
2. 数据区间是否一致；
3. 平均收益率是否由少数极端值驱动；
4. 波动率是否过高；
5. 是否存在停牌、上市时间差异等问题；
6. 是否使用相同复权与交易规则口径。

---

## 十七、今天需要掌握的 Python 函数

### `np.mean`

```python
np.mean(array, axis=0)
```

计算普通均值，遇到 `NaN` 通常传播为 `NaN`。

### `np.nanmean`

```python
np.nanmean(array, axis=0)
```

忽略 `NaN` 计算均值。

### `np.std`

```python
np.std(array, axis=0, ddof=1)
```

计算标准差。

### `np.nanstd`

```python
np.nanstd(array, axis=0, ddof=1)
```

忽略 `NaN` 计算标准差。

### `np.isnan`

```python
missing_mask = np.isnan(array)
```

判断是否为 `NaN`。

### `np.isfinite`

```python
valid_mask = np.isfinite(array)
```

同时检查 `NaN` 和正负无穷。

### `np.sum`

```python
valid_counts = np.sum(valid_mask, axis=0)
```

布尔数组求和可统计条件成立数量。

### `np.sqrt`

```python
annualized_volatility = daily_volatility * np.sqrt(252)
```

计算平方根。

### `np.prod`

```python
cumulative_returns = np.prod(
    1 + returns,
    axis=0,
) - 1
```

计算最终累计收益率。

### `np.cumprod`

```python
nav = np.cumprod(1 + returns, axis=0)
```

计算完整累计净值路径。

### `np.where`

```python
filtered = np.where(
    valid_counts >= minimum_observations,
    values,
    np.nan,
)
```

根据条件选择数值。

### `np.allclose`

```python
np.allclose(result_1, result_2)
```

验证浮点数组近似相等。

---

## 十八、最小综合代码

```python
import numpy as np

returns = np.array(
    [
        [0.020, -0.010, 0.015],
        [0.010,  0.020, np.nan],
        [-0.015, 0.005, 0.010],
        [0.030, -0.020, 0.025],
        [0.005,  0.015, 0.000],
    ],
    dtype=np.float64,
)

trading_days = 252
minimum_observations = 3

valid_counts = np.isfinite(returns).sum(axis=0)
mean_daily_returns = np.nanmean(returns, axis=0)
daily_volatility = np.nanstd(
    returns,
    axis=0,
    ddof=1,
)

annualized_returns = (
    mean_daily_returns * trading_days
)

annualized_volatility = (
    daily_volatility * np.sqrt(trading_days)
)

annualized_returns = np.where(
    valid_counts >= minimum_observations,
    annualized_returns,
    np.nan,
)

annualized_volatility = np.where(
    valid_counts >= minimum_observations,
    annualized_volatility,
    np.nan,
)
```

正确流程：

```text
检查有效样本
→ 计算日频指标
→ 年化
→ 过滤样本不足结果
```

---

## 十九、概念速查

| 指标 | 含义 | 代码 |
|---|---|---|
| 平均日收益率 | 单期收益的算术平均 | `np.nanmean(returns, axis=0)` |
| 累计收益率 | 整个期间复利增长 | `np.prod(1 + returns, axis=0) - 1` |
| 日波动率 | 日收益率样本标准差 | `np.nanstd(returns, axis=0, ddof=1)` |
| 线性年化收益 | 日均收益乘交易日数 | `mean_return * 252` |
| 年化波动率 | 日波动率乘根号时间 | `volatility * np.sqrt(252)` |
| 有效样本数 | 有限数据数量 | `np.isfinite(returns).sum(axis=0)` |

---

## 今日检查清单

- [ ] 能解释算术平均收益率的含义与局限。
- [ ] 能解释波动率不是平均亏损。
- [ ] 能区分总体标准差与样本标准差。
- [ ] 能区分线性年化与复利年化收益率。
- [ ] 能解释年化波动率为什么乘 $\sqrt{252}$。
- [ ] 能使用 `nanmean`、`nanstd` 和 `isfinite`。
- [ ] 能说明为什么有效样本数量必须同时报告。