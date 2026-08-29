# 第 2 周第 4 天：简单收益率、累计收益率与净值

## 今日目标

- 掌握简单收益率的数学定义。
- 区分单期收益、平均收益和累计收益。
- 使用 `np.prod` 与 `np.cumprod` 计算复利。
- 构造与价格日期对齐的累计净值序列。
- 使用数学恒等式验证程序。

---

## 一、简单收益率

$$
R_t=\frac{P_t}{P_{t-1}}-1
$$

NumPy：

```python
returns = prices[1:] / prices[:-1] - 1
```

若有 $n$ 个价格，只能得到 $n-1$ 个收益率。

收益率通常对应区间结束日期，因此日期应使用：

```python
return_dates = price_dates[1:]
```

---

## 二、增长因子

每一期的增长因子是：

$$
G_t=1+R_t
$$

例如收益率为 5%，增长因子为 1.05。

```python
growth_factors = 1 + returns
```

---

## 三、累计收益率

多期收益通过乘法复利：

$$
R_{cum}=\prod_{t=1}^{n}(1+R_t)-1
$$

```python
cumulative_return = np.prod(1 + returns) - 1
```

不能直接把日收益率相加作为精确累计收益率。

---

## 四、累计净值

初始净值设为 1：

$$
NAV_0=1
$$

之后：

$$
NAV_t=\prod_{k=1}^{t}(1+R_k)
$$

```python
nav_without_initial = np.cumprod(1 + returns)
nav = np.concatenate(
    [np.array([1.0]), nav_without_initial]
)
```

此时净值长度与价格长度一致。

---

## 五、直接从价格归一化

```python
nav_from_prices = prices / prices[0]
```

在没有分红、拆股和复权问题时，应满足：

$$
\frac{P_t}{P_0}=\prod_{k=1}^{t}(1+R_k)
$$

验证：

```python
assert np.allclose(nav, nav_from_prices)
```

---

## 六、平均收益率不等于累计收益率

收益率为：

```text
+10%、-10%
```

算术平均：

$$
\frac{10\%-10\%}{2}=0
$$

累计净值：

$$
1.1\times0.9=0.99
$$

最终亏损 1%。

波动会造成几何增长率低于算术平均增长率，这也是理解波动拖累的起点。

---

## 七、首尾价格法

最终累计收益率也可以直接计算：

$$
R_{cum}=\frac{P_n}{P_0}-1
$$

```python
cumulative_from_prices = prices[-1] / prices[0] - 1
cumulative_from_returns = np.prod(1 + returns) - 1

assert np.isclose(
    cumulative_from_prices,
    cumulative_from_returns,
)
```

---

## 八、最大回撤的初步认识

虽然本周不正式学习绩效指标，但净值可以用于理解回撤。

历史最高净值：

```python
running_max = np.maximum.accumulate(nav)
```

回撤：

```python
drawdown = nav / running_max - 1
```

最大回撤：

```python
max_drawdown = drawdown.min()
```

最大回撤反映从历史高点到后续低点的最大跌幅，不等于波动率。

---

## 九、函数实现

```python
import numpy as np


def simple_returns(prices: np.ndarray) -> np.ndarray:
    array = np.asarray(prices, dtype=np.float64)

    if array.ndim != 1:
        raise ValueError("prices 必须是一维数组")
    if array.size < 2:
        raise ValueError("至少需要两个价格")
    if not np.isfinite(array).all():
        raise ValueError("价格必须为有限数")
    if np.any(array <= 0):
        raise ValueError("价格必须严格大于 0")

    return array[1:] / array[:-1] - 1


def nav_from_returns(returns: np.ndarray) -> np.ndarray:
    array = np.asarray(returns, dtype=np.float64)

    if array.ndim != 1:
        raise ValueError("returns 必须是一维数组")
    if not np.isfinite(array).all():
        raise ValueError("收益率必须为有限数")
    if np.any(array <= -1):
        raise ValueError("收益率不能小于或等于 -100%")

    return np.concatenate(
        [
            np.array([1.0]),
            np.cumprod(1 + array),
        ]
    )
```

---

## 十、关键函数

| 函数 | 用法 |
|---|---|
| `np.prod` | 得到最终连乘结果 |
| `np.cumprod` | 得到每一期累计连乘路径 |
| `np.concatenate` | 拼接初始净值与累计路径 |
| `np.isclose` | 比较两个浮点数 |
| `np.allclose` | 比较两个浮点数组 |
| `np.maximum.accumulate` | 计算历史累计最高值 |

---

## 今日练习

1. 根据 6 个价格计算 5 个收益率。
2. 计算最终累计收益率。
3. 构造以 1 开始的净值序列。
4. 验证净值等于价格除以首日价格。
5. 使用 `+10%、-10%` 解释平均收益和累计收益的区别。
6. 计算示例净值的回撤序列。

---

## 今日检查清单

- [ ] 能解释增长因子。
- [ ] 能区分 `np.prod` 和 `np.cumprod`。
- [ ] 净值长度与价格长度一致。
- [ ] 累计收益率与首尾价格计算一致。
- [ ] 理解平均收益率不能代替复利累计收益率。
