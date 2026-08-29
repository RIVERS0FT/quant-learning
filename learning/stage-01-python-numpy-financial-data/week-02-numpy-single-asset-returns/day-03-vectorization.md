# 第 2 周第 3 天：NumPy 向量化与逐元素运算

## 今日目标

- 理解向量化与 Python 循环的区别。
- 掌握数组与标量、数组与数组的逐元素运算。
- 使用布尔数组完成批量判断。
- 理解形状兼容是向量化计算的前提。
- 将第一周的循环收益率函数改写为 NumPy 版本。

---

## 一、什么是向量化

第一周使用循环：

```python
returns = []

for index in range(1, len(prices)):
    returns.append(
        prices[index] / prices[index - 1] - 1
    )
```

NumPy 写法：

```python
returns = prices[1:] / prices[:-1] - 1
```

向量化表示把计算表达为数组操作，由 NumPy 在底层批量执行。

主要优点：

- 更接近数学表达；
- 代码更短；
- 通常执行更快；
- 更容易扩展到长时间序列；
- 减少手工索引错误。

---

## 二、标量与数组运算

```python
import numpy as np

prices = np.array([10.0, 10.2, 10.1, 10.5])

print(prices + 1)
print(prices * 2)
print(prices / 10)
print(prices ** 2)
```

标量会应用到数组中的每个元素。

---

## 三、数组之间逐元素运算

```python
a = np.array([1.0, 2.0, 3.0])
b = np.array([10.0, 20.0, 30.0])

print(a + b)
print(a - b)
print(a * b)
print(a / b)
```

这些运算要求形状兼容。

`a * b` 是逐元素乘法，不是线性代数中的矩阵乘法。

---

## 四、收益率向量化

设价格序列为：

$$
P_0,P_1,\ldots,P_n
$$

收益率序列为：

$$
R_t=\frac{P_t}{P_{t-1}}-1
$$

NumPy 实现：

```python
previous_prices = prices[:-1]
current_prices = prices[1:]
returns = current_prices / previous_prices - 1
```

先检查形状：

```python
assert previous_prices.shape == current_prices.shape
```

---

## 五、向量化布尔判断

```python
is_up = returns > 0
is_down = returns < 0
is_flat = returns == 0
```

统计：

```python
up_days = is_up.sum()
down_days = is_down.sum()
flat_days = is_flat.sum()
```

布尔值参与求和时：

```text
True  = 1
False = 0
```

上涨比例：

```python
up_ratio = is_up.mean()
```

---

## 六、常用通用函数 `ufunc`

NumPy 的通用函数可以逐元素计算：

```python
np.abs(returns)
np.sqrt(prices)
np.log(prices)
np.exp(returns)
np.maximum(returns, 0)
np.minimum(returns, 0)
```

这些函数通常比逐元素调用 Python 标准库函数更适合数组。

---

## 七、聚合运算

```python
returns.sum()
returns.mean()
returns.min()
returns.max()
returns.std()
```

聚合函数把一组数压缩为一个统计结果。

注意：收益率平均值、累计收益率和最终价格变化不是同一个概念。

---

## 八、`np.where`

根据条件选择：

```python
labels = np.where(
    returns > 0,
    "上涨",
    "非上涨",
)
```

数值处理：

```python
positive_part = np.where(
    returns > 0,
    returns,
    0.0,
)
```

`np.where` 不应被用于掩盖错误数据。替换规则必须有明确金融依据。

---

## 九、循环与向量化结果验证

```python
loop_returns = []

for index in range(1, len(prices)):
    loop_returns.append(
        prices[index] / prices[index - 1] - 1
    )

vectorized_returns = prices[1:] / prices[:-1] - 1

assert np.allclose(
    np.array(loop_returns),
    vectorized_returns,
)
```

`np.allclose` 用于判断浮点数组是否在误差范围内近似相等。

---

## 十、性能概念

可以使用 `timeit` 比较执行时间，但学习阶段不要只追求速度。

优先顺序应为：

1. 数学和金融逻辑正确；
2. 时间与数据对齐正确；
3. 输入校验明确；
4. 测试充分；
5. 再考虑性能优化。

向量化代码如果形状或方向错误，也可能快速地产生大量错误结果。

---

## 十一、向量化收益率函数

```python
import numpy as np


def simple_returns(prices: np.ndarray) -> np.ndarray:
    """计算一维正价格数组的简单收益率。"""

    array = np.asarray(prices, dtype=np.float64)

    if array.ndim != 1:
        raise ValueError("prices 必须是一维数组")
    if array.size < 2:
        raise ValueError("至少需要两个价格")
    if not np.isfinite(array).all():
        raise ValueError("价格不能包含 NaN 或无穷值")
    if np.any(array <= 0):
        raise ValueError("价格必须严格大于 0")

    return array[1:] / array[:-1] - 1
```

---

## 十二、什么时候仍然使用循环

循环仍适合：

- 每个元素执行不同的复杂流程；
- 需要调用无法接受数组的外部接口；
- 逐条输出日志；
- 状态依赖前一步且难以向量化；
- 学习和验证算法。

核心数值计算优先向量化，格式化输出可以使用循环。

---

## 今日练习

1. 用循环和向量化分别计算收益率。
2. 使用 `np.allclose` 验证结果一致。
3. 统计上涨、下跌和平盘数量。
4. 使用 `np.where` 生成涨跌标签。
5. 为 `simple_returns` 加入维度、长度和价格校验。

---

## 今日检查清单

- [ ] 能解释向量化的含义。
- [ ] 能区分逐元素乘法与矩阵乘法。
- [ ] 能使用布尔数组批量判断。
- [ ] 能检查数组形状是否兼容。
- [ ] 能用 `np.allclose` 验证两种实现。
