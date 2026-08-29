# 第 1 周第 7 天：综合项目——单资产收益率工具

## 今日目标

- 整合环境、数据类型、控制流程、函数、异常处理和 Git。
- 建立清晰的项目目录。
- 完成一个可运行、可测试的单资产收益率工具。
- 完成第一周复盘与提交。

---

## 一、项目需求

输入一组按时间排序的正价格，输出：

- 相邻简单收益率；
- 上涨、下跌和平盘天数；
- 最终累计收益率；
- 清晰的错误信息。

简单收益率：

$$
R_t=\frac{P_t}{P_{t-1}}-1
$$

累计收益率：

$$
R_{cum}=\prod_{t=1}^{n}(1+R_t)-1
$$

在没有分红和拆股时，也应满足：

$$
R_{cum}=\frac{P_n}{P_0}-1
$$

---

## 二、项目目录

```text
quant-research/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── prices.txt
├── src/
│   ├── __init__.py
│   ├── returns.py
│   └── main.py
└── tests/
    └── test_returns.py
```

---

## 三、核心模块

`src/returns.py`：

```python
from math import prod


def validate_prices(prices: list[float]) -> None:
    """校验价格序列。"""

    if len(prices) < 2:
        raise ValueError("至少需要两个价格")

    for index, price in enumerate(prices):
        if price <= 0:
            raise ValueError(
                f"索引 {index} 的价格必须大于 0"
            )


def simple_return(
    previous_price: float,
    current_price: float,
) -> float:
    """计算两个相邻价格之间的简单收益率。"""

    if previous_price <= 0:
        raise ValueError("前一期价格必须大于 0")
    if current_price < 0:
        raise ValueError("当前价格不能小于 0")

    return current_price / previous_price - 1


def calculate_returns(
    prices: list[float],
) -> list[float]:
    """根据价格序列计算相邻简单收益率。"""

    validate_prices(prices)

    returns: list[float] = []

    for index in range(1, len(prices)):
        returns.append(
            simple_return(
                previous_price=prices[index - 1],
                current_price=prices[index],
            )
        )

    return returns


def summarize_returns(
    returns: list[float],
) -> dict[str, float | int]:
    """汇总基础收益统计。"""

    if not returns:
        raise ValueError("收益率列表不能为空")

    up_days = sum(value > 0 for value in returns)
    down_days = sum(value < 0 for value in returns)
    flat_days = sum(value == 0 for value in returns)
    cumulative_return = prod(1 + value for value in returns) - 1

    return {
        "up_days": up_days,
        "down_days": down_days,
        "flat_days": flat_days,
        "cumulative_return": cumulative_return,
    }
```

---

## 四、命令行入口

`src/main.py`：

```python
from pathlib import Path

from returns import calculate_returns, summarize_returns


def read_prices(file_path: Path) -> list[float]:
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")

    prices: list[float] = []

    with file_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            text = line.strip()

            if not text:
                continue

            try:
                prices.append(float(text))
            except ValueError as error:
                raise ValueError(
                    f"第 {line_number} 行不是有效数字"
                ) from error

    return prices


def main() -> None:
    try:
        prices = read_prices(Path("data/prices.txt"))
        returns = calculate_returns(prices)
        summary = summarize_returns(returns)
    except (FileNotFoundError, ValueError) as error:
        print(f"运行失败：{error}")
        return

    print("价格：", prices)
    print("收益率：")

    for index, value in enumerate(returns, start=1):
        print(f"区间 {index}: {value:.2%}")

    print("上涨天数：", summary["up_days"])
    print("下跌天数：", summary["down_days"])
    print("平盘天数：", summary["flat_days"])
    print(
        "累计收益率："
        f"{summary['cumulative_return']:.2%}"
    )


if __name__ == "__main__":
    main()
```

运行：

```bash
python src/main.py
```

---

## 五、基础测试

`tests/test_returns.py`：

```python
import pytest

from src.returns import (
    calculate_returns,
    simple_return,
    summarize_returns,
)


def test_simple_return() -> None:
    assert simple_return(10.0, 11.0) == pytest.approx(0.10)


def test_calculate_returns_length() -> None:
    prices = [10.0, 10.2, 10.1, 10.5]
    returns = calculate_returns(prices)

    assert len(returns) == len(prices) - 1


def test_cumulative_return_matches_prices() -> None:
    prices = [10.0, 10.2, 10.1, 10.5]
    returns = calculate_returns(prices)
    summary = summarize_returns(returns)

    expected = prices[-1] / prices[0] - 1

    assert summary["cumulative_return"] == pytest.approx(
        expected
    )


def test_rejects_zero_price() -> None:
    with pytest.raises(ValueError):
        calculate_returns([10.0, 0.0, 10.5])
```

运行：

```bash
pytest -q
```

---

## 六、README 应记录什么

```markdown
# Quant Research

## 目标

学习 Python 与量化研究基础。

## 环境

- Python 3.11+
- NumPy
- pytest

## 安装

python -m venv .venv
python -m pip install -r requirements.txt

## 运行

python src/main.py

## 测试

pytest -q
```

README 应让未来的自己能够重新运行项目。

---

## 七、验收测试

使用价格：

```text
10.0
11.0
10.0
```

收益率为：

$$
R_1=\frac{11}{10}-1=10\%
$$

$$
R_2=\frac{10}{11}-1\approx-9.09\%
$$

累计收益率应为：

$$
(1+R_1)(1+R_2)-1=0
$$

因为最终价格回到初始价格。

---

## 八、第一周复盘

你应能解释：

- 虚拟环境为什么需要隔离；
- 列表、元组和字典的区别；
- 条件与循环如何表达价格处理规则；
- 函数为什么需要输入校验；
- 异常为什么不能被静默忽略；
- Git 提交为什么应小而清晰；
- 数学恒等式如何用于测试程序。

---

## 九、提交建议

```bash
git status
git diff
git add README.md .gitignore requirements.txt src tests
git diff --staged
git commit -m "完成第一周单资产收益率项目"
```

---

## 第一周验收清单

- [ ] 虚拟环境可重新创建。
- [ ] `python src/main.py` 可以运行。
- [ ] `pytest -q` 全部通过。
- [ ] 非正价格会被拒绝。
- [ ] 收益率数量等于价格数量减 1。
- [ ] 累计收益率与首尾价格计算一致。
- [ ] README 包含环境、运行和测试方法。
- [ ] 已完成规范 Git 提交。
