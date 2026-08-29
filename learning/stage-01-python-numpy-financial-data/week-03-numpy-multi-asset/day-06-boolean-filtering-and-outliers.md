# 第 3 周第 6 天：布尔筛选、异常收益与数据质量

## 今日目标

今天增加数学学习权重，重点理解：

- 布尔数组与集合、指示函数之间的关系；
- 如何统计上涨、下跌和异常事件；
- 固定阈值、Z-score、IQR 和 MAD 四种异常值方法；
- 时间序列异常与横截面异常的区别；
- 异常值、缺失值和错误值不是同一个概念。

---

## 一、布尔筛选的集合含义

设某只股票收益率序列为：

$$
r_1,r_2,\ldots,r_n
$$

正收益日期集合：

$$
A=\{t:r_t>0\}
$$

NumPy 表达：

```python
is_up = returns > 0
```

布尔数组就是集合条件在每个位置是否成立的计算机表示。

---

## 二、指示函数

指示函数：

$$
\mathbf{1}(r_t>0)=
\begin{cases}
1,&r_t>0\\
0,&r_t\leq0
\end{cases}
$$

上涨天数：

$$
\sum_{t=1}^{n}\mathbf{1}(r_t>0)
$$

代码：

```python
up_days = (returns > 0).sum()
```

上涨比例：

$$
\frac{1}{n}\sum_{t=1}^{n}\mathbf{1}(r_t>0)
$$

代码：

```python
up_ratio = (returns > 0).mean()
```

布尔值参与计算时，`True=1`、`False=0`。

---

## 三、多资产事件统计

设：

$$
R\in\mathbb{R}^{T\times N}
$$

上涨指示矩阵：

$$
U_{t,i}=\mathbf{1}(R_{t,i}>0)
$$

代码：

```python
is_up = returns > 0
```

每只股票上涨天数：

```python
up_days = is_up.sum(axis=0)
```

每日上涨股票数量：

```python
up_assets = is_up.sum(axis=1)
```

每日上涨股票比例：

```python
up_ratio_by_day = is_up.mean(axis=1)
```

---

## 四、缺失值条件下的上涨比例

`np.nan > 0` 会得到 `False`，若直接求平均，会把缺失值错误计入分母。

正确做法：

```python
valid = np.isfinite(returns)

up_ratio_by_day = (
    ((returns > 0) & valid).sum(axis=1)
    / valid.sum(axis=1)
)
```

数学表达：

$$
P_t=
\frac{
\sum_i\mathbf{1}(R_{t,i}>0)
}{
\sum_i\mathbf{1}(R_{t,i}\text{ 有效})
}
$$

---

## 五、多个条件组合

逻辑与：

```python
mask = (returns > 0) & (returns < 0.05)
```

逻辑或：

```python
mask = (returns > 0.05) | (returns < -0.05)
```

等价双侧条件：

```python
mask = np.abs(returns) > 0.05
```

逻辑非：

```python
valid = ~np.isnan(returns)
```

推荐使用更全面的：

```python
valid = np.isfinite(returns)
```

每个比较条件都应加括号。

---

## 六、异常收益没有唯一标准

某个收益率是否异常，取决于：

- 数据频率；
- 股票自身波动水平；
- 市场环境；
- 是否涨跌停；
- 是否正确复权；
- 是否存在公司行为；
- 判断是在时间序列还是横截面中进行。

因此：

```text
数值极端 ≠ 数据错误
数据错误 ≠ 一定数值极端
```

---

## 七、方法一：固定阈值

规则：

$$
|r_t|>c
$$

代码：

```python
extreme_mask = np.abs(returns) > 0.10
```

优点：

- 简单；
- 容易解释；
- 适合业务规则和数据质量初筛。

缺点：

- 忽略不同股票波动差异；
- 阈值具有主观性；
- 高波动和低波动股票使用同一标准不公平。

---

## 八、方法二：普通 Z-score

均值：

$$
\bar r=\frac{1}{n}\sum_{t=1}^{n}r_t
$$

样本标准差：

$$
s=\sqrt{\frac{1}{n-1}\sum_{t=1}^{n}(r_t-\bar r)^2}
$$

Z-score：

$$
z_t=\frac{r_t-\bar r}{s}
$$

按股票时间序列计算：

```python
mean_returns = np.nanmean(
    returns,
    axis=0,
    keepdims=True,
)

std_returns = np.nanstd(
    returns,
    axis=0,
    ddof=1,
    keepdims=True,
)

safe_std = np.where(
    std_returns == 0,
    np.nan,
    std_returns,
)

z_scores = (
    returns - mean_returns
) / safe_std

outliers = np.abs(z_scores) > 3
```

### 局限

极端值会同时拉动均值和标准差，导致自身 Z-score 被压低。金融收益还常具有厚尾、尖峰和波动率聚集，所以 `|z|>3` 只是统计标记，不等于错误数据。

---

## 九、时间序列与横截面 Z-score

### 时间序列 Z-score

$$
z_{t,i}^{TS}=\frac{R_{t,i}-\bar R_i}{s_i}
$$

问题：

> 今天这只股票相对于自身历史是否异常？

通常按 `axis=0` 计算。

### 横截面 Z-score

$$
z_{t,i}^{CS}=\frac{R_{t,i}-\bar R_t}{s_t}
$$

代码：

```python
cross_mean = np.nanmean(
    returns,
    axis=1,
    keepdims=True,
)

cross_std = np.nanstd(
    returns,
    axis=1,
    ddof=1,
    keepdims=True,
)

cross_z = (
    returns - cross_mean
) / cross_std
```

问题：

> 这只股票今天相对于同日其他股票是否异常？

两个问题完全不同，不能混淆。

---

## 十、方法三：四分位距 IQR

第一四分位数：

$$
Q_1=P_{25}
$$

第三四分位数：

$$
Q_3=P_{75}
$$

四分位距：

$$
IQR=Q_3-Q_1
$$

常见异常区间：

$$
[Q_1-1.5IQR,\ Q_3+1.5IQR]
$$

代码：

```python
q1 = np.nanpercentile(
    returns,
    25,
    axis=0,
    keepdims=True,
)

q3 = np.nanpercentile(
    returns,
    75,
    axis=0,
    keepdims=True,
)

iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr

outlier_mask = (
    (returns < lower)
    | (returns > upper)
)
```

IQR 不依赖均值和标准差，对少量极端值更稳健，但小样本下分位数也可能不稳定。

---

## 十一、方法四：中位数与 MAD

中位数：

$$
m=\operatorname{median}(r_t)
$$

中位绝对偏差：

$$
MAD=\operatorname{median}(|r_t-m|)
$$

稳健 Z-score：

$$
z_t^{robust}=
\frac{r_t-m}{1.4826\cdot MAD}
$$

代码：

```python
median_returns = np.nanmedian(
    returns,
    axis=0,
    keepdims=True,
)

mad = np.nanmedian(
    np.abs(returns - median_returns),
    axis=0,
    keepdims=True,
)

safe_mad = np.where(
    mad == 0,
    np.nan,
    mad,
)

robust_z = (
    returns - median_returns
) / (1.4826 * safe_mad)

outliers = np.abs(robust_z) > 3
```

系数 `1.4826` 用于在近似正态分布下，把 MAD 调整到与标准差相近的尺度。

MAD 使用中位数和绝对偏差，比普通 Z-score 更不容易被少数极端值影响。

---

## 十二、四种方法对比

| 方法 | 数学基础 | 优点 | 主要问题 |
|---|---|---|---|
| 固定阈值 | 绝对范围 | 简单、明确 | 忽略资产差异 |
| Z-score | 均值和标准差 | 标准化、易比较 | 容易被极端值影响 |
| IQR | 分位数 | 稳健、直观 | 小样本不稳定 |
| MAD | 中位数与绝对偏差 | 厚尾数据下更稳健 | MAD 可能为 0 |

合理流程：

```text
业务规则检查
→ 固定阈值初筛
→ 统计方法标记
→ 回看原始价格与公司行为
→ 决定保留、修正、设为缺失或剔除
```

---

## 十三、异常值的处理

### 保留原值

适合确认是真实市场极端行情的情况，尤其是研究尾部风险时。

### 设为 `NaN`

```python
clean_returns = returns.copy()
clean_returns[outlier_mask] = np.nan
```

适合高度怀疑错误、但暂时无法确认正确值的情况。缺点是减少样本并破坏时间连续性。

### Winsorization 截尾

$$
r_t^*=\begin{cases}
L,&r_t<L\\
r_t,&L\le r_t\le U\\
U,&r_t>U
\end{cases}
$$

```python
winsorized = np.clip(
    returns,
    lower,
    upper,
)
```

常用于横截面因子处理，但不应未经说明直接修改真实策略收益序列。

### 使用正确数据替换

最理想的方式是回到数据源修复：

- 重新获取行情；
- 修正复权因子；
- 修正日期错位；
- 修正小数点或重复记录。

---

## 十四、缺失值、异常值和错误值

- 缺失值：没有可用观测，通常表示为 `NaN`；
- 异常值：有数值，但相对某种统计或业务规则显得极端；
- 错误值：数据本身不正确。

关系：

```text
缺失值 ≠ 异常值
异常值 ≠ 错误值
```

---

## 十五、今天需要掌握的 Python 函数

| 函数或运算 | 用途 |
|---|---|
| `>`、`<`、`==` | 生成布尔条件 |
| `&` | 逻辑与 |
| `|` | 逻辑或 |
| `~` | 逻辑取反 |
| `np.abs` | 计算绝对值 |
| `np.isfinite` | 检查有效有限值 |
| `np.nanmedian` | 忽略缺失值计算中位数 |
| `np.nanpercentile` | 忽略缺失值计算分位数 |
| `np.where` | 按条件选择值 |
| `np.clip` | 将数值限制在上下界内 |
| `array[mask]` | 布尔索引提取或修改数据 |

---

## 十六、最小综合示例

```python
import numpy as np

returns = np.array(
    [
        [0.010, 0.015, 0.012],
        [0.020, -0.010, 0.018],
        [-0.015, 0.005, np.nan],
        [0.150, 0.012, 0.020],
        [0.008, -0.090, 0.011],
    ],
    dtype=np.float64,
)

valid = np.isfinite(returns)

up_ratio = (
    ((returns > 0) & valid).sum(axis=0)
    / valid.sum(axis=0)
)

median_returns = np.nanmedian(
    returns,
    axis=0,
    keepdims=True,
)

mad = np.nanmedian(
    np.abs(returns - median_returns),
    axis=0,
    keepdims=True,
)

safe_mad = np.where(mad == 0, np.nan, mad)

robust_z = (
    returns - median_returns
) / (1.4826 * safe_mad)

robust_outliers = np.abs(robust_z) > 3
```

---

## 今日检查清单

- [ ] 能用集合和指示函数解释布尔数组。
- [ ] 能正确处理存在 `NaN` 时的上涨比例分母。
- [ ] 能组合多个布尔条件。
- [ ] 能推导并解释普通 Z-score。
- [ ] 能区分时间序列与横截面 Z-score。
- [ ] 能解释 IQR 区间。
- [ ] 能推导 MAD 与稳健 Z-score。
- [ ] 能说明异常值为什么不能自动删除。