# 第 2 周第 2 天：NumPy 索引、切片与条件选择

## 今日目标

- 熟练使用正向、负向索引和切片。
- 理解切片的左闭右开规则。
- 掌握步长、反转和条件索引。
- 正确对齐当前价格与前一期价格。
- 理解切片通常返回视图带来的影响。

---

## 一、价格数组

```python
import numpy as np

prices = np.array(
    [10.0, 10.2, 10.1, 10.5, 10.8, 10.6],
    dtype=np.float64,
)
```

数组长度：

```python
print(prices.shape)  # (6,)
print(prices.size)   # 6
```

---

## 二、单元素索引

```python
prices[0]   # 第一个价格
prices[1]   # 第二个价格
prices[-1]  # 最后一个价格
prices[-2]  # 倒数第二个价格
```

最后一个合法正向索引为：

```python
len(prices) - 1
```

索引超出范围会抛出 `IndexError`。

---

## 三、基础切片

切片格式：

```python
array[start:stop:step]
```

`stop` 不包含在结果中。

```python
prices[:3]    # 索引 0、1、2
prices[1:4]   # 索引 1、2、3
prices[2:]    # 从索引 2 到结尾
prices[:-1]   # 除最后一个元素
prices[1:]    # 除第一个元素
```

---

## 四、步长与反转

每隔一个元素取值：

```python
prices[::2]
```

从索引 1 开始每隔一个元素：

```python
prices[1::2]
```

反转数组：

```python
prices[::-1]
```

在金融时间序列中，默认应保持从早到晚的顺序。反转后必须清楚时间方向已经改变。

---

## 五、相邻价格对齐

收益率需要当前价格和前一期价格一一对应：

```python
previous_prices = prices[:-1]
current_prices = prices[1:]
```

两者形状一致：

```python
assert previous_prices.shape == current_prices.shape
```

对应关系：

| 前一期 | 当前期 |
|---:|---:|
| 10.0 | 10.2 |
| 10.2 | 10.1 |
| 10.1 | 10.5 |
| 10.5 | 10.8 |
| 10.8 | 10.6 |

收益率：

```python
returns = current_prices / previous_prices - 1
```

---

## 六、整数索引与切片的维度区别

```python
prices[0]
```

返回标量。

```python
prices[0:1]
```

返回形状为 `(1,)` 的数组。

在需要保持数组结构时，应使用切片而不是单个整数索引。

---

## 七、条件索引

筛选大于 10.5 的价格：

```python
mask = prices > 10.5
selected = prices[mask]
```

`mask` 是布尔数组：

```text
[False False False False  True  True]
```

组合条件：

```python
selected = prices[
    (prices >= 10.2) & (prices <= 10.6)
]
```

NumPy 数组中应使用：

- `&` 表示逻辑与；
- `|` 表示逻辑或；
- `~` 表示逻辑非。

每个比较条件必须加括号。

---

## 八、按位置数组选择

```python
indices = np.array([0, 2, 5])
selected = prices[indices]
```

结果按指定位置排列。

这种方式称为高级索引，通常返回新数组，而不是原数组视图。

---

## 九、切片视图与复制

```python
subset = prices[1:4]
subset[0] = 99.0
```

基础切片通常是原数组的视图，因此修改 `subset` 可能同时修改 `prices`。

如果需要独立副本：

```python
subset = prices[1:4].copy()
```

研究中建议在准备修改切片数据前明确调用 `.copy()`，避免污染原始价格。

---

## 十、条件修改

将低于 10.2 的价格标记为 `NaN`：

```python
clean_prices = prices.copy()
clean_prices[clean_prices < 10.2] = np.nan
```

这只是展示语法。真实研究中不能因为价格低就认为数据无效。

---

## 十一、价格区间提取函数

```python
import numpy as np


def select_price_window(
    prices: np.ndarray,
    start: int,
    stop: int,
) -> np.ndarray:
    """提取左闭右开的价格区间并返回副本。"""

    array = np.asarray(prices, dtype=np.float64)

    if array.ndim != 1:
        raise ValueError("prices 必须是一维数组")
    if start < 0 or stop > array.size:
        raise ValueError("索引范围超出价格数组")
    if start >= stop:
        raise ValueError("start 必须小于 stop")

    return array[start:stop].copy()
```

---

## 今日练习

1. 取出前三个、后三个和中间三个价格。
2. 使用步长提取奇数位置和偶数位置。
3. 反转数组并解释时间方向。
4. 使用条件索引提取上涨后的当前价格。
5. 证明基础切片可能修改原数组，再使用 `.copy()` 修复。
6. 编写并测试 `select_price_window`。

---

## 今日检查清单

- [ ] 能解释左闭右开规则。
- [ ] 能使用负向索引和步长。
- [ ] 能对齐 `prices[:-1]` 与 `prices[1:]`。
- [ ] 能正确组合多个布尔条件。
- [ ] 理解视图和复制的区别。
