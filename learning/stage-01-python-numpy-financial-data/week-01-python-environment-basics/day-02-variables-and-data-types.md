# 第 1 周第 2 天：变量与数据类型

## 今日目标

- 理解变量是对对象的引用。
- 掌握数值、字符串、布尔值、列表、元组和字典。
- 学会类型检查与类型转换。
- 使用基础数据结构表达股票价格和交易信息。

---

## 一、变量与命名

```python
stock_code = "000001.SZ"
close_price = 12.35
volume = 1_250_000
is_tradable = True
```

推荐命名规则：

- 使用有含义的英文单词；
- 使用小写字母与下划线；
- 不使用 `list`、`str`、`sum` 等内置名称；
- 名称应表达金融含义和数据口径。

例如 `adjusted_close` 比 `x` 更适合研究代码。

---

## 二、数值类型

### 整数 `int`

```python
trading_days = 252
shares = 1000
```

### 浮点数 `float`

```python
price = 10.25
return_rate = 0.032
```

浮点数是近似表示：

```python
print(0.1 + 0.2)
```

结果可能不是精确的 `0.3`。因此比较浮点数时，后续应使用允许误差的方法。

### 基础运算

```python
addition = 10 + 2
subtraction = 10 - 2
multiplication = 10 * 2
division = 10 / 2
floor_division = 10 // 3
remainder = 10 % 3
power = 10 ** 2
```

收益率：

```python
previous_price = 10.0
current_price = 10.5
simple_return = current_price / previous_price - 1
```

---

## 三、字符串 `str`

```python
stock_name = "平安银行"
stock_code = "000001.SZ"
```

字符串拼接：

```python
label = stock_code + " " + stock_name
```

推荐使用 f-string：

```python
message = f"{stock_code} 收盘价为 {close_price:.2f}"
```

常用格式：

```python
f"{close_price:.2f}"   # 两位小数
f"{return_rate:.2%}"  # 百分比
f"{volume:,}"         # 千位分隔
```

---

## 四、布尔值 `bool`

布尔值只有：

```python
True
False
```

示例：

```python
is_up = current_price > previous_price
is_limit_up = return_rate >= 0.10
```

比较运算：

```python
price > 10
price >= 10
price < 20
price == 10
price != 10
```

逻辑运算：

```python
is_candidate = is_tradable and return_rate > 0
is_special = is_limit_up or is_limit_down
is_missing = not has_price
```

---

## 五、列表 `list`

列表有顺序、可修改：

```python
prices = [10.0, 10.2, 10.1, 10.5]
```

常用操作：

```python
prices.append(10.8)
first_price = prices[0]
last_price = prices[-1]
number_of_prices = len(prices)
```

修改元素：

```python
prices[0] = 10.05
```

列表适合初步保存一组价格，但大量数值计算后续应使用 NumPy。

---

## 六、元组 `tuple`

元组有顺序，但通常不修改：

```python
price_range = (10.0, 10.8)
```

解包：

```python
low_price, high_price = price_range
```

适合表示结构固定的数据，例如函数返回的两个统计量。

---

## 七、字典 `dict`

字典使用键值对表达带名称的数据：

```python
stock = {
    "code": "000001.SZ",
    "name": "平安银行",
    "close": 12.35,
    "volume": 1_250_000,
    "tradable": True,
}
```

读取：

```python
print(stock["code"])
print(stock.get("close"))
```

修改：

```python
stock["close"] = 12.50
```

字典适合表达一条股票记录，但多行表格数据后续应使用 pandas。

---

## 八、类型检查与转换

```python
print(type(close_price))
print(isinstance(close_price, float))
```

类型转换：

```python
price_text = "12.35"
price = float(price_text)
shares = int("1000")
code = str(1)
```

外部数据经常以字符串形式读取，转换失败时会抛出 `ValueError`。

---

## 九、可变对象与复制

```python
prices_a = [10.0, 10.2]
prices_b = prices_a
prices_b.append(10.5)
```

此时两个变量引用同一个列表。

创建浅复制：

```python
prices_b = prices_a.copy()
```

量化研究中应特别注意：修改一个变量是否会意外改变原始数据。

---

## 十、最小综合示例

```python
stock = {
    "code": "000001.SZ",
    "prices": [10.0, 10.2, 10.1, 10.5],
    "tradable": True,
}

prices = stock["prices"]
previous_price = prices[-2]
current_price = prices[-1]
return_rate = current_price / previous_price - 1

print(f"股票：{stock['code']}")
print(f"当前价格：{current_price:.2f}")
print(f"当期收益率：{return_rate:.2%}")
print(f"是否上涨：{return_rate > 0}")
```

---

## 今日练习

1. 创建一条包含代码、名称、收盘价和成交量的股票字典。
2. 使用列表保存 5 个收盘价。
3. 计算最后两个价格之间的收益率。
4. 使用 f-string 输出百分比。
5. 观察列表赋值和 `.copy()` 的区别。

---

## 今日检查清单

- [ ] 能区分 `int`、`float`、`str` 和 `bool`。
- [ ] 能解释列表与元组的区别。
- [ ] 能用字典表达一条股票记录。
- [ ] 能进行安全的基础类型转换。
- [ ] 理解浮点数是近似表示。
