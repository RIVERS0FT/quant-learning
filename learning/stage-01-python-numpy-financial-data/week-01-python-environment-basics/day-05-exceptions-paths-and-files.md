# 第 1 周第 5 天：异常处理、文件路径与基础读写

## 今日目标

- 理解异常与普通条件判断的区别。
- 掌握 `try/except/else/finally`。
- 使用 `pathlib.Path` 管理跨平台路径。
- 使用上下文管理器安全读写文本文件。
- 从文件中读取价格并处理非法数据。

---

## 一、什么是异常

异常表示程序运行过程中出现了无法按原计划继续的情况。

常见异常：

| 异常 | 示例 |
|---|---|
| `ValueError` | `float("abc")` |
| `TypeError` | 字符串与数字直接相加 |
| `ZeroDivisionError` | 除数为 0 |
| `FileNotFoundError` | 文件不存在 |
| `KeyError` | 字典中没有指定键 |
| `IndexError` | 列表索引越界 |

异常不是“程序一定写错”，也可能来自外部输入不符合要求。

---

## 二、基础 `try/except`

```python
price_text = "10.25"

try:
    price = float(price_text)
except ValueError:
    print("价格格式错误")
```

只捕获你能够合理处理的异常，不要默认使用：

```python
except:
    ...
```

过于宽泛的捕获会隐藏真正的程序错误。

---

## 三、`else` 与 `finally`

```python
try:
    price = float(price_text)
except ValueError:
    print("无法转换价格")
else:
    print("转换成功：", price)
finally:
    print("处理结束")
```

- `else`：没有异常时执行；
- `finally`：无论是否异常都会执行。

在文件操作中，上下文管理器通常比手动在 `finally` 中关闭文件更简洁。

---

## 四、主动抛出异常

```python
def simple_return(
    previous_price: float,
    current_price: float,
) -> float:
    if previous_price <= 0:
        raise ValueError("前一期价格必须大于 0")

    if current_price < 0:
        raise ValueError("当前价格不能小于 0")

    return current_price / previous_price - 1
```

抛出异常的目的不是让程序崩溃，而是尽早阻止错误数据继续传播。

---

## 五、使用 `pathlib`

```python
from pathlib import Path

project_root = Path.cwd()
data_dir = project_root / "data"
price_file = data_dir / "prices.txt"
```

`/` 在这里表示安全拼接路径，而不是数学除法。

常用操作：

```python
price_file.exists()
price_file.is_file()
data_dir.is_dir()
price_file.name
price_file.suffix
price_file.parent
```

创建目录：

```python
data_dir.mkdir(parents=True, exist_ok=True)
```

`pathlib` 比手工拼接 `"data/prices.txt"` 更适合跨平台项目。

---

## 六、写入文本文件

```python
from pathlib import Path

file_path = Path("data/prices.txt")
file_path.parent.mkdir(parents=True, exist_ok=True)

prices = [10.0, 10.2, 10.1, 10.5]

with file_path.open("w", encoding="utf-8") as file:
    for price in prices:
        file.write(f"{price}\n")
```

`with` 会在代码块结束后自动关闭文件，即使中间发生异常。

---

## 七、读取文本文件

```python
with file_path.open("r", encoding="utf-8") as file:
    lines = file.readlines()
```

转换价格：

```python
prices = []

for line_number, line in enumerate(lines, start=1):
    text = line.strip()

    if not text:
        continue

    try:
        price = float(text)
    except ValueError as error:
        raise ValueError(
            f"第 {line_number} 行不是有效价格：{text}"
        ) from error

    if price <= 0:
        raise ValueError(
            f"第 {line_number} 行价格必须大于 0"
        )

    prices.append(price)
```

使用 `raise ... from error` 可以保留原始异常原因。

---

## 八、安全读取函数

```python
from pathlib import Path


def read_prices(file_path: Path) -> list[float]:
    """从文本文件读取正价格，每行一个价格。"""

    if not file_path.exists():
        raise FileNotFoundError(
            f"价格文件不存在：{file_path}"
        )

    prices: list[float] = []

    with file_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            text = line.strip()

            if not text:
                continue

            try:
                price = float(text)
            except ValueError as error:
                raise ValueError(
                    f"第 {line_number} 行无法转换为价格"
                ) from error

            if price <= 0:
                raise ValueError(
                    f"第 {line_number} 行价格必须大于 0"
                )

            prices.append(price)

    if len(prices) < 2:
        raise ValueError("至少需要两个有效价格")

    return prices
```

---

## 九、路径应相对于什么位置

`Path.cwd()` 表示当前工作目录，它可能随启动方式变化。

模块中也可以使用：

```python
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
```

学习阶段要形成习惯：

- 明确工作目录；
- 不依赖模糊的相对路径；
- 不把个人电脑的绝对路径写死在代码中；
- 数据路径和代码路径分离。

---

## 十、错误处理原则

1. 尽早校验输入。
2. 异常信息应包含位置和原因。
3. 不要静默忽略错误。
4. 不要把缺失或错误数据随意替换为 0。
5. 只在能够恢复或补充上下文时捕获异常。
6. 核心计算函数抛出异常，命令行入口负责友好显示。

---

## 十一、完整示例

```python
from pathlib import Path


def calculate_returns(prices: list[float]) -> list[float]:
    if len(prices) < 2:
        raise ValueError("至少需要两个价格")

    returns: list[float] = []

    for index in range(1, len(prices)):
        previous_price = prices[index - 1]
        current_price = prices[index]

        if previous_price <= 0 or current_price <= 0:
            raise ValueError("价格必须严格大于 0")

        returns.append(current_price / previous_price - 1)

    return returns


try:
    prices = read_prices(Path("data/prices.txt"))
    returns = calculate_returns(prices)
except (FileNotFoundError, ValueError) as error:
    print(f"处理失败：{error}")
else:
    print("价格：", prices)
    print("收益率：", returns)
```

---

## 今日练习

1. 创建 `data/prices.txt`，每行写一个价格。
2. 使用 `Path` 检查文件是否存在。
3. 编写 `read_prices`。
4. 在文件中加入非法字符串，观察错误信息。
5. 删除文件，观察 `FileNotFoundError`。
6. 保证错误数据不会进入收益率计算。

---

## 今日检查清单

- [ ] 能区分条件判断与异常处理。
- [ ] 能针对具体异常编写 `except`。
- [ ] 能用 `Path` 创建和拼接路径。
- [ ] 能使用 `with` 安全读写文件。
- [ ] 错误信息包含文件或行号上下文。
