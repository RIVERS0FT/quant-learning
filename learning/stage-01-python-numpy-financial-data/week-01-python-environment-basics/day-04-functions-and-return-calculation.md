# 第 1 周第 4 天：函数与第一个收益率函数

## 今日目标

- 理解函数用于封装可重复逻辑。
- 掌握参数、返回值、默认参数和关键字参数。
- 使用类型提示和文档字符串说明函数契约。
- 编写带输入校验的简单收益率函数。

---

## 一、为什么使用函数

不使用函数时，相同收益率计算可能在多个位置重复出现：

```python
return_a = 10.5 / 10.0 - 1
return_b = 20.2 / 20.0 - 1
```

函数可以把规则集中到一个位置：

```python
def simple_return(previous_price, current_price):
    return current_price / previous_price - 1
```

函数的主要价值：

- 减少重复；
- 明确输入和输出；
- 便于测试；
- 修改规则时只改一个位置；
- 让代码表达金融概念。

---

## 二、定义与调用

```python
def greet(name):
    message = f"你好，{name}"
    return message

result = greet("量化研究者")
print(result)
```

函数定义使用 `def`，`return` 把结果返回给调用者。

没有显式 `return` 的函数会返回 `None`。

---

## 三、位置参数与关键字参数

```python
def simple_return(previous_price, current_price):
    return current_price / previous_price - 1
```

位置参数：

```python
result = simple_return(10.0, 10.5)
```

关键字参数：

```python
result = simple_return(
    previous_price=10.0,
    current_price=10.5,
)
```

研究代码中，关键字参数有助于避免价格顺序写反。

---

## 四、默认参数

```python
def format_return(value, decimals=2):
    return f"{value:.{decimals}%}"
```

调用：

```python
format_return(0.035)
format_return(0.035, decimals=4)
```

默认参数适合稳定、明确的默认规则。不要把可能变化的重要研究口径隐藏在不清晰的默认值中。

---

## 五、仅关键字参数

```python
def annualize_return(
    mean_daily_return: float,
    *,
    trading_days: int = 252,
) -> float:
    return mean_daily_return * trading_days
```

`*` 之后的参数必须使用名称调用：

```python
annualize_return(0.001, trading_days=252)
```

这适合交易日数量、是否复权、交易成本等重要配置。

---

## 六、类型提示

```python
def simple_return(
    previous_price: float,
    current_price: float,
) -> float:
    return current_price / previous_price - 1
```

类型提示不会自动阻止错误类型，但它可以：

- 帮助编辑器检查；
- 提高可读性；
- 明确函数契约；
- 为后续静态检查做准备。

---

## 七、文档字符串

```python
def simple_return(
    previous_price: float,
    current_price: float,
) -> float:
    """计算相邻两个价格之间的简单收益率。

    参数
    ----
    previous_price:
        前一期价格，必须大于 0。
    current_price:
        当前价格，必须大于或等于 0。

    返回
    ----
    float
        简单收益率。
    """
    return current_price / previous_price - 1
```

文档字符串应说明口径和限制，而不是简单重复函数名。

---

## 八、输入校验

简单收益率公式：

$$
R=\frac{P_1}{P_0}-1
$$

其中分母价格必须大于 0。

```python
def simple_return(
    previous_price: float,
    current_price: float,
) -> float:
    """计算简单收益率。"""

    if previous_price <= 0:
        raise ValueError("previous_price 必须大于 0")

    if current_price < 0:
        raise ValueError("current_price 不能小于 0")

    return current_price / previous_price - 1
```

测试：

```python
print(simple_return(10.0, 11.0))
print(simple_return(10.0, 9.0))
```

---

## 九、返回多个结果

```python
def price_change(
    previous_price: float,
    current_price: float,
) -> tuple[float, float]:
    absolute_change = current_price - previous_price
    return_rate = current_price / previous_price - 1
    return absolute_change, return_rate
```

调用：

```python
change, return_rate = price_change(10.0, 10.5)
```

Python 实际返回的是元组。

---

## 十、纯函数思想

下面的函数只依赖输入并返回结果：

```python
def simple_return(previous_price: float, current_price: float) -> float:
    return current_price / previous_price - 1
```

它不会修改外部变量，也不会写文件。这样的函数更容易测试和复用。

量化计算的核心函数应尽量保持：

- 输入明确；
- 输出明确；
- 不隐藏外部状态；
- 不在计算函数中混入大量打印操作。

---

## 十一、批量计算的基础函数

```python
def calculate_returns(prices: list[float]) -> list[float]:
    """根据价格列表计算相邻简单收益率。"""

    if len(prices) < 2:
        raise ValueError("至少需要两个价格")

    returns: list[float] = []

    for index in range(1, len(prices)):
        value = simple_return(
            previous_price=prices[index - 1],
            current_price=prices[index],
        )
        returns.append(value)

    return returns
```

第二周会使用 NumPy 将该循环改写为向量化计算。

---

## 十二、基础验证

```python
result = simple_return(10.0, 11.0)
assert abs(result - 0.10) < 1e-12

result = simple_return(10.0, 10.0)
assert abs(result) < 1e-12
```

`assert` 适合学习阶段快速验证，但正式测试应使用 `pytest`。

---

## 今日练习

1. 编写 `simple_return`。
2. 为函数加入类型提示和文档字符串。
3. 验证前一期价格为 0 时抛出异常。
4. 编写 `price_change`，同时返回绝对变化和收益率。
5. 编写 `calculate_returns` 处理价格列表。

---

## 今日检查清单

- [ ] 能解释参数和返回值。
- [ ] 能使用位置参数与关键字参数。
- [ ] 能编写类型提示和文档字符串。
- [ ] 能使用 `raise ValueError` 拒绝非法输入。
- [ ] 第一个收益率函数通过手工结果验证。
