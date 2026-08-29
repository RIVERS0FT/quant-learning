# 第 2 周第 1 天：NumPy 数组与单资产收益率

## 今日目标

- 理解为什么量化计算使用 NumPy 数组，而不是只使用 Python 列表。
- 掌握数组创建、数据类型、属性、索引和切片。
- 理解向量化计算。
- 使用相邻价格切片计算简单收益率。
- 掌握价格与收益率长度之间的关系。

---

## 一、为什么量化研究需要 NumPy

普通 Python 列表可以保存价格：

```python
prices = [10.0, 10.2, 10.1]
```

但列表乘以 2 会把列表重复两次，而不是把每个价格乘以 2：

```python
print(prices * 2)
```

NumPy 数组支持逐元素运算：

```python
import numpy as np

prices = np.array([10.0, 10.2, 10.1])
print(prices * 2)
```

输出：

```text
[20.  20.4 20.2]
```

这种一次性对整个数组执行运算的方式称为**向量化计算**。

---

## 二、创建价格数组

```python
import numpy as np

prices = np.array(
    [10.00, 10.20, 10.10, 10.50, 10.80],
    dtype=np.float64,
)
```

金融价格通常应使用浮点数。显式指定 `np.float64` 可以避免整数除法或数据类型不一致的问题。

---

## 三、数组的重要属性

```python
print(prices.ndim)
print(prices.shape)
print(prices.size)
print(prices.dtype)
```

| 属性 | 含义 | 示例结果 |
|---|---|---|
| `ndim` | 数组维度 | `1` |
| `shape` | 每个维度的长度 | `(5,)` |
| `size` | 元素总数量 | `5` |
| `dtype` | 元素数据类型 | `float64` |

`(5,)` 表示长度为 5 的一维数组，不是五行一列的二维矩阵。

---

## 四、索引

```python
print(prices[0])   # 第一个价格
print(prices[1])   # 第二个价格
print(prices[-1])  # 最后一个价格
print(prices[-2])  # 倒数第二个价格
```

Python 和 NumPy 的索引都从 0 开始。

---

## 五、切片

```python
print(prices[:3])   # 前三个价格
print(prices[1:4])  # 索引 1、2、3
print(prices[1:])   # 除第一个价格外
print(prices[:-1])  # 除最后一个价格外
```

切片采用左闭右开规则。

计算收益率时最重要的两个切片是：

```python
previous_prices = prices[:-1]
current_prices = prices[1:]
```

对应关系：

| 前一日价格 | 当前价格 |
|---:|---:|
| 10.00 | 10.20 |
| 10.20 | 10.10 |
| 10.10 | 10.50 |
| 10.50 | 10.80 |

---

## 六、向量化运算

```python
print(prices + 1)
print(prices * 100)
```

将价格相对于第一天归一化：

```python
price_ratio = prices / prices[0]
print(price_ratio)
```

结果约为：

```text
[1.00, 1.02, 1.01, 1.05, 1.08]
```

这可以理解为初始投入 1 元后的价格净值变化。

---

## 七、简单收益率

简单收益率公式：

$$
r_t = \frac{P_t}{P_{t-1}} - 1
$$

其中：

- $P_t$：当前交易日价格；
- $P_{t-1}$：前一个交易日价格；
- $r_t$：当前收益区间的收益率。

NumPy 实现：

```python
returns = prices[1:] / prices[:-1] - 1
print(returns)
```

输出约为：

```text
[ 0.02000000 -0.00980392  0.03960396  0.02857143]
```

转换为百分比：

```python
print(returns * 100)
```

| 区间 | 收益率 |
|---|---:|
| 第 1 日到第 2 日 | 2.00% |
| 第 2 日到第 3 日 | -0.98% |
| 第 3 日到第 4 日 | 3.96% |
| 第 4 日到第 5 日 | 2.86% |

有 $n$ 个价格点时，只能得到 $n-1$ 个收益率：

```python
assert len(returns) == len(prices) - 1
```

---

## 八、为什么优先使用向量化

循环写法可以得到正确结果：

```python
result = []
for i in range(1, len(prices)):
    result.append(prices[i] / prices[i - 1] - 1)
```

但 NumPy 推荐：

```python
returns = prices[1:] / prices[:-1] - 1
```

向量化写法更短、更清晰，通常也更快，并且容易扩展到大量股票和交易日。

---

## 九、常用统计操作

```python
print(prices.min())
print(prices.max())
print(prices.mean())
print(prices.std())
print(prices.sum())
```

收益率统计：

```python
print(returns.mean())
print(returns.std())
print(returns.max())
print(returns.min())
```

当前先使用 NumPy 默认标准差，后续再区分总体标准差与样本标准差。

---

## 十、完整示例

```python
import numpy as np


def main() -> None:
    prices = np.array(
        [10.00, 10.20, 10.10, 10.50, 10.80],
        dtype=np.float64,
    )

    previous_prices = prices[:-1]
    current_prices = prices[1:]
    returns = current_prices / previous_prices - 1

    print("价格数组：", prices)
    print("形状：", prices.shape)
    print("数据类型：", prices.dtype)
    print("简单收益率：", returns)
    print("百分比收益率：", returns * 100)
    print("平均收益率：", returns.mean())
    print("收益率波动：", returns.std())


if __name__ == "__main__":
    main()
```

---

## 十一、练习

### 练习 1：创建数组

将以下收盘价转换成 `float64` 数组：

```text
20.00, 20.50, 20.30, 21.00, 20.80, 21.50
```

输出数组、形状、数据类型、第一个价格和最后一个价格。

### 练习 2：计算收益率

禁止使用循环，计算简单收益率的小数形式和百分比形式。

### 练习 3：上涨判断

```python
is_up = prices[1:] > prices[:-1]
up_days = is_up.sum()
```

理解布尔值参与求和时，`True` 相当于 1，`False` 相当于 0。

### 练习 4：基数效应

价格从 10 元上涨到 11 元，再从 11 元回到 10 元：

$$
\frac{11}{10}-1=10\%
$$

$$
\frac{10}{11}-1\approx-9.09\%
$$

上涨幅度和下跌幅度并不对称，因为两次计算使用的价格基数不同。

---

## 今日检查清单

- [ ] 能解释列表和 NumPy 数组运算的区别。
- [ ] 能解释 `shape=(5,)` 的含义。
- [ ] 能使用正向和负向索引。
- [ ] 能使用 `prices[:-1]` 和 `prices[1:]` 对齐相邻价格。
- [ ] 能不用循环计算简单收益率。
- [ ] 能解释为什么价格数量比收益率数量多 1。