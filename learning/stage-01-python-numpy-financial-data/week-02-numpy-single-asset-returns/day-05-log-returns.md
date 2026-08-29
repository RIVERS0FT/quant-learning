# 第 2 周第 5 天：对数收益率与时间可加性

## 今日目标

- 理解对数收益率的定义。
- 掌握简单收益率与对数收益率的相互转换。
- 理解对数收益率为什么可以跨时间相加。
- 学会使用 `np.log`、`np.log1p`、`np.exp` 和 `np.expm1`。
- 明确两种收益率的适用场景与限制。

---

## 一、对数收益率

对数收益率定义为：

$$
r_t=\ln\left(\frac{P_t}{P_{t-1}}\right)
$$

也可以写成：

$$
r_t=\ln(P_t)-\ln(P_{t-1})
$$

NumPy：

```python
log_returns = np.log(prices[1:] / prices[:-1])
```

或：

```python
log_returns = np.log(prices[1:]) - np.log(prices[:-1])
```

两种方法应近似一致。

---

## 二、与简单收益率的关系

简单收益率：

$$
R_t=\frac{P_t}{P_{t-1}}-1
$$

所以：

$$
1+R_t=\frac{P_t}{P_{t-1}}
$$

对数收益率为：

$$
r_t=\ln(1+R_t)
$$

从对数收益率恢复简单收益率：

$$
R_t=e^{r_t}-1
$$

NumPy 推荐：

```python
log_returns = np.log1p(simple_returns)
simple_returns = np.expm1(log_returns)
```

`log1p` 和 `expm1` 对非常小的数通常具有更好的数值稳定性。

---

## 三、时间可加性

连续两期对数收益率：

$$
r_1=\ln\left(\frac{P_1}{P_0}\right)
$$

$$
r_2=\ln\left(\frac{P_2}{P_1}\right)
$$

相加：

$$
r_1+r_2
=\ln\left(\frac{P_1}{P_0}\right)
+\ln\left(\frac{P_2}{P_1}\right)
=\ln\left(\frac{P_2}{P_0}\right)
$$

中间价格 $P_1$ 被约掉。因此对数收益率可以沿时间直接相加。

```python
total_log_return = log_returns.sum()
cumulative_simple_return = np.expm1(total_log_return)
```

---

## 四、对数收益率净值

累计对数收益：

```python
cumulative_log_returns = np.cumsum(log_returns)
```

转换为累计净值：

```python
nav_without_initial = np.exp(cumulative_log_returns)
nav = np.concatenate(
    [np.array([1.0]), nav_without_initial]
)
```

验证：

```python
assert np.allclose(nav, prices / prices[0])
```

---

## 五、小收益下的近似

当收益率绝对值较小时：

$$
\ln(1+R)\approx R
$$

例如 0.1% 的简单收益率和对数收益率非常接近。

但收益率较大时差异会明显：

| 简单收益率 | 对数收益率 |
|---:|---:|
| 10% | 约 9.53% |
| -10% | 约 -10.54% |
| 100% | 约 69.31% |

因此不能在所有场景中把两者视为相同。

---

## 六、对称性的区别

价格从 10 上涨到 11：

$$
R=10\%
$$

再从 11 回到 10：

$$
R\approx-9.09\%
$$

简单收益率不对称。

对数收益率：

$$
\ln(11/10)\approx9.53\%
$$

$$
\ln(10/11)\approx-9.53\%
$$

两段对数收益率大小相同、方向相反，相加为 0。

---

## 七、适用场景

### 简单收益率

适合：

- 表达投资者单期实际盈亏比例；
- 计算固定权重组合的单期收益；
- 构建累计净值；
- 交易和绩效报告。

### 对数收益率

适合：

- 时间序列统计建模；
- 跨期收益相加；
- 连续复利分析；
- 某些理论推导。

不能把资产的对数收益率简单加权，直接当作组合的精确对数收益率。

---

## 八、价格要求

对数函数的输入必须严格大于 0：

```python
np.log(0.0)   # 无效
np.log(-1.0)  # 无效
```

因此对数收益率函数必须校验：

```python
if np.any(prices <= 0):
    raise ValueError("计算对数收益率时价格必须大于 0")
```

---

## 九、函数实现

```python
import numpy as np


def log_returns(prices: np.ndarray) -> np.ndarray:
    """计算一维正价格数组的对数收益率。"""

    array = np.asarray(prices, dtype=np.float64)

    if array.ndim != 1:
        raise ValueError("prices 必须是一维数组")
    if array.size < 2:
        raise ValueError("至少需要两个价格")
    if not np.isfinite(array).all():
        raise ValueError("价格必须为有限数")
    if np.any(array <= 0):
        raise ValueError("价格必须严格大于 0")

    return np.log(array[1:]) - np.log(array[:-1])
```

---

## 十、关键函数

| 函数 | 用法 |
|---|---|
| `np.log` | 计算自然对数 |
| `np.log1p(x)` | 稳定计算 $\ln(1+x)$ |
| `np.exp` | 计算指数函数 |
| `np.expm1(x)` | 稳定计算 $e^x-1$ |
| `np.sum` | 累加对数收益率 |
| `np.cumsum` | 得到累计对数收益路径 |

---

## 今日练习

1. 从价格计算简单收益率和对数收益率。
2. 验证 `log_returns == np.log1p(simple_returns)`。
3. 验证 `simple_returns == np.expm1(log_returns)`。
4. 从对数收益率恢复净值。
5. 用 `10 → 11 → 10` 解释对数收益率的对称性。

---

## 今日检查清单

- [ ] 能写出对数收益率公式。
- [ ] 能解释时间可加性。
- [ ] 能完成两种收益率的转换。
- [ ] 知道 `log1p` 和 `expm1` 的用途。
- [ ] 能说明简单收益率和对数收益率的适用区别。
