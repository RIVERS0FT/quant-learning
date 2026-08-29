# 第 1 周第 3 天：条件判断与循环

## 今日目标

- 使用 `if/elif/else` 表达交易规则。
- 使用 `for` 遍历价格序列。
- 理解 `while`、`range`、`enumerate` 和 `zip`。
- 掌握 `break` 与 `continue` 的适用场景。
- 编写基础价格变化统计程序。

---

## 一、条件判断

```python
return_rate = 0.035

if return_rate > 0:
    print("上涨")
elif return_rate < 0:
    print("下跌")
else:
    print("平盘")
```

Python 使用缩进表示代码块。建议统一使用 4 个空格。

---

## 二、组合条件

```python
is_tradable = True
return_rate = 0.035
volume = 2_000_000

if is_tradable and return_rate > 0 and volume > 1_000_000:
    print("满足基础筛选条件")
```

逻辑运算：

| 运算 | 含义 |
|---|---|
| `and` | 所有条件都成立 |
| `or` | 至少一个条件成立 |
| `not` | 条件取反 |

条件顺序应从数据有效性开始，再判断交易逻辑。

---

## 三、`for` 循环

```python
prices = [10.0, 10.2, 10.1, 10.5]

for price in prices:
    print(price)
```

遍历相邻价格：

```python
for index in range(1, len(prices)):
    previous_price = prices[index - 1]
    current_price = prices[index]
    return_rate = current_price / previous_price - 1
    print(index, return_rate)
```

虽然第二周会学习 NumPy 向量化，但循环仍然是理解算法和处理复杂流程的基础。

---

## 四、`range`

```python
range(5)        # 0, 1, 2, 3, 4
range(1, 5)     # 1, 2, 3, 4
range(0, 10, 2) # 0, 2, 4, 6, 8
```

计算相邻收益率时从索引 1 开始，因为第一个价格没有前一期价格。

---

## 五、`enumerate`

同时获取位置和值：

```python
for index, price in enumerate(prices):
    print(index, price)
```

从 1 开始编号：

```python
for day, price in enumerate(prices, start=1):
    print(f"第 {day} 日：{price:.2f}")
```

`enumerate` 通常比手动维护计数变量更安全。

---

## 六、`zip`

同时遍历多个序列：

```python
dates = ["07-01", "07-02", "07-03"]
prices = [10.0, 10.2, 10.1]

for date, price in zip(dates, prices):
    print(date, price)
```

需要注意：`zip` 默认以最短序列为准。研究代码应先验证长度是否一致。

---

## 七、`while` 循环

```python
index = 0

while index < len(prices):
    print(prices[index])
    index += 1
```

`while` 适合循环次数依赖条件的场景。必须确保条件最终会变为 `False`，避免无限循环。

---

## 八、`break` 与 `continue`

遇到非法价格时停止：

```python
for price in prices:
    if price <= 0:
        print("发现非法价格")
        break
    print(price)
```

跳过缺失值：

```python
prices = [10.0, None, 10.2]

for price in prices:
    if price is None:
        continue
    print(price)
```

跳过数据并不等于问题已解决。实际研究中应记录被跳过的原因和数量。

---

## 九、涨跌统计

定义：

$$
R_t=\frac{P_t}{P_{t-1}}-1
$$

程序：

```python
prices = [10.0, 10.2, 10.1, 10.5, 10.5]

up_days = 0
down_days = 0
flat_days = 0
returns = []

for index in range(1, len(prices)):
    previous_price = prices[index - 1]
    current_price = prices[index]
    return_rate = current_price / previous_price - 1
    returns.append(return_rate)

    if return_rate > 0:
        up_days += 1
    elif return_rate < 0:
        down_days += 1
    else:
        flat_days += 1

print("收益率：", returns)
print("上涨天数：", up_days)
print("下跌天数：", down_days)
print("平盘天数：", flat_days)
```

应满足：

```python
assert up_days + down_days + flat_days == len(returns)
```

---

## 十、循环中的常见错误

### 修改正在遍历的列表

不要在遍历列表时随意删除其元素，这可能导致漏处理。

### 索引越界

```python
prices[len(prices)]
```

最后一个合法索引是 `len(prices) - 1`。

### 使用 `==` 比较浮点数

真实计算中应允许极小误差。后续使用 `np.isclose`。

### 条件过于复杂

复杂条件应拆成带名称的布尔变量，使金融含义更清晰。

---

## 今日练习

1. 遍历价格并输出每个交易日编号。
2. 计算相邻价格收益率。
3. 统计上涨、下跌和平盘天数。
4. 使用 `zip` 同时输出日期和价格。
5. 遇到非正价格时停止计算并输出提示。

---

## 今日检查清单

- [ ] 能正确使用 `if/elif/else`。
- [ ] 能解释 `range(1, len(prices))` 的原因。
- [ ] 能使用 `enumerate` 和 `zip`。
- [ ] 能区分 `break` 与 `continue`。
- [ ] 能验证涨跌天数之和等于收益区间数量。
