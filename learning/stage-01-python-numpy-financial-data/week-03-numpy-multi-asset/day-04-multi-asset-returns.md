# 第 3 周第 4 天：多资产收益率模块

## 今日目标

- 掌握多资产简单收益率与对数收益率。
- 理解收益率和日期的对齐关系。
- 使用收益率生成累计净值。
- 理解简单收益率与对数收益率的不同用途。
- 对价格矩阵进行维度、缺失值、无穷值和非正价格校验。

---

## 一、数据结构约定

价格矩阵：

```text
行：交易日
列：股票
```

形状：

$$
P\in\mathbb{R}^{T\times N}
$$

其中 $T$ 是交易日数量，$N$ 是股票数量。

---

## 二、多资产简单收益率

公式：

$$
R_{t,i}=\frac{P_{t,i}}{P_{t-1,i}}-1
$$

代码：

```python
simple = prices[1:, :] / prices[:-1, :] - 1
```

如果价格矩阵形状为 `(T, N)`，收益率矩阵形状为：

```text
(T - 1, N)
```

---

## 三、收益率日期对齐

假设价格日期：

```python
dates = np.array([
    "2026-07-01",
    "2026-07-02",
    "2026-07-03",
    "2026-07-06",
    "2026-07-07",
])
```

第一行收益率由第 1 日和第 2 日价格计算，因此应标记在第 2 日：

```python
return_dates = dates[1:]
```

不能写成：

```python
return_dates = dates[:-1]
```

时间对齐错误可能在回测中造成未来数据泄露或信号错位。

---

## 四、多资产对数收益率

公式：

$$
g_{t,i}=\ln\left(\frac{P_{t,i}}{P_{t-1,i}}\right)
$$

等价形式：

$$
g_{t,i}=\ln P_{t,i}-\ln P_{t-1,i}
$$

代码：

```python
logarithmic = np.log(
    prices[1:, :] / prices[:-1, :]
)
```

或：

```python
logarithmic = (
    np.log(prices[1:, :])
    - np.log(prices[:-1, :])
)
```

验证：

```python
assert np.allclose(log_returns_1, log_returns_2)
```

---

## 五、简单收益率与对数收益率的转换

两者关系：

$$
g_t=\ln(1+r_t)
$$

$$
r_t=e^{g_t}-1
$$

NumPy 推荐函数：

```python
log_from_simple = np.log1p(simple)
simple_from_log = np.expm1(logarithmic)
```

`np.log1p(x)` 在 $x$ 很小时比 `np.log(1 + x)` 更稳定，`np.expm1(x)` 比 `np.exp(x) - 1` 更稳定。

---

## 六、两种收益率的用途

### 简单收益率适合资产组合

单期固定权重组合收益：

$$
r_{p,t}=\sum_{i=1}^{N}w_i r_{t,i}
$$

代码：

```python
portfolio_return = daily_returns @ weights
```

### 对数收益率适合跨时间累加

$$
\sum_{t=1}^{T}g_t
=
\ln\left(\frac{P_T}{P_0}\right)
$$

累计简单收益率：

```python
total_simple = np.expm1(log_returns.sum(axis=0))
```

注意：组合的对数收益率通常不能简单地用个股对数收益率按权重相加来替代。

---

## 七、从简单收益率计算累计净值

增长因子：

```python
growth_factors = 1 + simple
```

累计净值：

```python
nav_without_initial = np.cumprod(
    growth_factors,
    axis=0,
)
```

在开头添加初始净值 1：

```python
initial_nav = np.ones((1, simple.shape[1]))
nav = np.vstack([initial_nav, nav_without_initial])
```

数学表达：

$$
NAV_{t,i}=\prod_{k=1}^{t}(1+R_{k,i})
$$

---

## 八、从对数收益率计算累计净值

对数收益率沿时间累加：

```python
cumulative_log = np.cumsum(
    logarithmic,
    axis=0,
)
```

转换成净值：

```python
nav_log_without_initial = np.exp(cumulative_log)
nav_log = np.vstack([
    np.ones((1, logarithmic.shape[1])),
    nav_log_without_initial,
])
```

数学表达：

$$
NAV_{t,i}=\exp\left(\sum_{k=1}^{t}g_{k,i}\right)
$$

---

## 九、三种净值方法等价

在价格连续、未考虑分红和公司行为时：

```python
nav_from_simple = np.vstack([
    np.ones((1, prices.shape[1])),
    np.cumprod(1 + simple, axis=0),
])

nav_from_log = np.vstack([
    np.ones((1, prices.shape[1])),
    np.exp(np.cumsum(logarithmic, axis=0)),
])

nav_from_prices = prices / prices[0]
```

验证：

```python
assert np.allclose(nav_from_simple, nav_from_log)
assert np.allclose(nav_from_simple, nav_from_prices)
```

累计收益率：

```python
cumulative_returns = nav_from_simple[-1] - 1
```

---

## 十、缺失值传播

如果某个价格是 `NaN`，通常会影响相邻两个收益区间：

- 当前价格缺失，当前收益无法计算；
- 下一期计算时，前一期价格又缺失。

这是合理的传播行为。

不要默认：

```python
returns = np.nan_to_num(returns, nan=0.0)
```

因为缺失数据不代表真实收益率为 0。

---

## 十一、价格校验原则

股票价格中的有效值通常必须严格大于 0：

- 零价格会导致除零；
- 负价格通常不符合普通股票价格含义；
- 对数收益率不能对零或负数取对数；
- `inf` 和 `-inf` 应被拒绝；
- 是否允许 `NaN` 应由函数参数明确控制。

---

## 十二、价格校验函数

```python
import numpy as np


def validate_prices(
    prices: np.ndarray,
    *,
    allow_nan: bool = True,
) -> np.ndarray:
    array = np.asarray(prices, dtype=np.float64)

    if array.ndim != 2:
        raise ValueError(
            "prices 必须是二维数组，"
            "形状为 (交易日数量, 股票数量)"
        )

    if array.shape[0] < 2:
        raise ValueError("至少需要两个交易日")

    if array.shape[1] < 1:
        raise ValueError("至少需要一只股票")

    if np.isinf(array).any():
        raise ValueError("价格不能包含无穷值")

    if not allow_nan and np.isnan(array).any():
        raise ValueError("价格不能包含 NaN")

    valid_prices = array[~np.isnan(array)]

    if np.any(valid_prices <= 0):
        raise ValueError("有效股票价格必须严格大于 0")

    return array
```

---

## 十三、收益率函数

```python
def simple_returns(
    prices: np.ndarray,
    *,
    allow_nan: bool = True,
) -> np.ndarray:
    array = validate_prices(
        prices,
        allow_nan=allow_nan,
    )
    return array[1:] / array[:-1] - 1
```

```python
def log_returns(
    prices: np.ndarray,
    *,
    allow_nan: bool = True,
) -> np.ndarray:
    array = validate_prices(
        prices,
        allow_nan=allow_nan,
    )
    return np.log(array[1:]) - np.log(array[:-1])
```

---

## 十四、从收益率生成净值

```python
def nav_from_simple_returns(
    returns: np.ndarray,
) -> np.ndarray:
    array = np.asarray(returns, dtype=np.float64)

    if array.ndim != 2:
        raise ValueError("returns 必须是二维数组")

    if np.isinf(array).any():
        raise ValueError("收益率不能包含无穷值")

    valid_returns = array[~np.isnan(array)]

    if np.any(valid_returns <= -1):
        raise ValueError("简单收益率不能小于或等于 -100%")

    initial_nav = np.ones((1, array.shape[1]))
    accumulated = np.cumprod(1 + array, axis=0)
    return np.vstack([initial_nav, accumulated])
```

```python
def nav_from_log_returns(
    returns: np.ndarray,
) -> np.ndarray:
    array = np.asarray(returns, dtype=np.float64)

    if array.ndim != 2:
        raise ValueError("returns 必须是二维数组")

    if np.isinf(array).any():
        raise ValueError("收益率不能包含无穷值")

    initial_nav = np.ones((1, array.shape[1]))
    accumulated = np.exp(np.cumsum(array, axis=0))
    return np.vstack([initial_nav, accumulated])
```

---

## 十五、真实 A 股价格的复权问题

真实行情可能包含：

- 现金分红；
- 送股与转增；
- 配股；
- 除权除息；
- 拆股或合股。

直接使用未复权收盘价，可能把公司行为造成的价格跳变误认为投资亏损。当前课程先掌握数组计算，后续再系统学习前复权、后复权和总收益口径。

---

## 今日必须掌握的函数

| 函数 | 用途 |
|---|---|
| `np.log` | 计算自然对数 |
| `np.log1p` | 稳定计算 `log(1+x)` |
| `np.expm1` | 稳定计算 `exp(x)-1` |
| `np.cumprod` | 沿时间累计连乘 |
| `np.cumsum` | 沿时间累计求和 |
| `np.exp` | 将累计对数收益转换为净值 |
| `np.vstack` | 在首行加入初始净值 |
| `np.asarray` | 统一输入为指定类型数组 |
| `np.isnan` | 检查缺失值 |
| `np.isinf` | 检查正负无穷 |
| `np.allclose` | 验证浮点结果近似相等 |

---

## 今日检查清单

- [ ] 能计算多资产简单收益率和对数收益率。
- [ ] 能解释收益率日期为什么使用 `dates[1:]`。
- [ ] 能使用 `log1p` 和 `expm1` 转换两种收益率。
- [ ] 能说明简单收益率适合组合、对数收益率适合跨时间累加。
- [ ] 能用三种方式验证累计净值。
- [ ] 能解释一个缺失价格为什么可能影响两个收益区间。
- [ ] 能校验二维形状、无穷值和非正价格。