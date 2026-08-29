# 第 2 周第 7 天：综合项目——单资产收益率模块与测试

## 今日目标

- 整合 NumPy 数组、切片、向量化、收益率、净值和数据校验。
- 建立可复用的单资产收益率模块。
- 使用 `pytest` 验证数学关系和边界条件。
- 完成第二周项目、README 和 Git 提交。

---

## 一、项目需求

输入一维价格数组，提供：

- 价格校验；
- 简单收益率；
- 对数收益率；
- 简单收益率累计净值；
- 对数收益率累计净值；
- 数据质量报告；
- 基础单元测试。

核心数学关系：

$$
R_t=\frac{P_t}{P_{t-1}}-1
$$

$$
r_t=\ln\left(\frac{P_t}{P_{t-1}}\right)
$$

$$
NAV_t=\prod_{k=1}^{t}(1+R_k)
$$

$$
NAV_t=\exp\left(\sum_{k=1}^{t}r_k\right)
$$

---

## 二、项目目录

```text
quant-research/
├── pyproject.toml
├── README.md
├── src/
│   └── quant_research/
│       ├── __init__.py
│       └── returns.py
└── tests/
    └── test_returns.py
```

---

## 三、收益率模块

`src/quant_research/returns.py`：

```python
import numpy as np


def validate_prices(
    prices: np.ndarray,
    *,
    allow_nan: bool = False,
) -> np.ndarray:
    """校验并返回一维 float64 价格数组。"""

    array = np.asarray(prices, dtype=np.float64)

    if array.ndim != 1:
        raise ValueError("prices 必须是一维数组")

    if array.size < 2:
        raise ValueError("至少需要两个价格")

    if np.isinf(array).any():
        raise ValueError("价格不能包含无穷值")

    if not allow_nan and np.isnan(array).any():
        raise ValueError("价格不能包含 NaN")

    valid_prices = array[~np.isnan(array)]

    if np.any(valid_prices <= 0):
        raise ValueError("有效价格必须严格大于 0")

    return array


def simple_returns(
    prices: np.ndarray,
    *,
    allow_nan: bool = False,
) -> np.ndarray:
    """计算简单收益率。"""

    array = validate_prices(
        prices,
        allow_nan=allow_nan,
    )

    return array[1:] / array[:-1] - 1


def log_returns(
    prices: np.ndarray,
    *,
    allow_nan: bool = False,
) -> np.ndarray:
    """计算对数收益率。"""

    array = validate_prices(
        prices,
        allow_nan=allow_nan,
    )

    return np.log(array[1:]) - np.log(array[:-1])


def nav_from_simple_returns(
    returns: np.ndarray,
) -> np.ndarray:
    """根据简单收益率计算以 1 开始的累计净值。"""

    array = np.asarray(returns, dtype=np.float64)

    if array.ndim != 1:
        raise ValueError("returns 必须是一维数组")
    if np.isinf(array).any():
        raise ValueError("收益率不能包含无穷值")

    valid_returns = array[~np.isnan(array)]

    if np.any(valid_returns <= -1):
        raise ValueError("简单收益率不能小于或等于 -100%")

    return np.concatenate(
        [
            np.array([1.0]),
            np.cumprod(1 + array),
        ]
    )


def nav_from_log_returns(
    returns: np.ndarray,
) -> np.ndarray:
    """根据对数收益率计算以 1 开始的累计净值。"""

    array = np.asarray(returns, dtype=np.float64)

    if array.ndim != 1:
        raise ValueError("returns 必须是一维数组")
    if np.isinf(array).any():
        raise ValueError("收益率不能包含无穷值")

    return np.concatenate(
        [
            np.array([1.0]),
            np.exp(np.cumsum(array)),
        ]
    )


def price_quality_report(
    prices: np.ndarray,
) -> dict[str, int | bool]:
    """返回价格数组的基础质量统计。"""

    array = np.asarray(prices, dtype=np.float64)

    return {
        "total_count": int(array.size),
        "nan_count": int(np.isnan(array).sum()),
        "inf_count": int(np.isinf(array).sum()),
        "non_positive_finite_count": int(
            ((array <= 0) & np.isfinite(array)).sum()
        ),
        "all_finite": bool(np.isfinite(array).all()),
    }
```

---

## 四、测试模块

`tests/test_returns.py`：

```python
import numpy as np
import pytest

from quant_research.returns import (
    log_returns,
    nav_from_log_returns,
    nav_from_simple_returns,
    simple_returns,
    validate_prices,
)


@pytest.fixture
def prices() -> np.ndarray:
    return np.array(
        [10.0, 10.2, 10.1, 10.5, 10.8],
        dtype=np.float64,
    )


def test_simple_returns_shape(
    prices: np.ndarray,
) -> None:
    result = simple_returns(prices)
    assert result.shape == (prices.size - 1,)


def test_first_simple_return(
    prices: np.ndarray,
) -> None:
    result = simple_returns(prices)
    assert result[0] == pytest.approx(0.02)


def test_log_and_simple_relation(
    prices: np.ndarray,
) -> None:
    simple = simple_returns(prices)
    logarithmic = log_returns(prices)

    assert np.allclose(
        logarithmic,
        np.log1p(simple),
    )


def test_three_nav_methods_are_equal(
    prices: np.ndarray,
) -> None:
    simple = simple_returns(prices)
    logarithmic = log_returns(prices)

    nav_simple = nav_from_simple_returns(simple)
    nav_log = nav_from_log_returns(logarithmic)
    nav_prices = prices / prices[0]

    assert np.allclose(nav_simple, nav_log)
    assert np.allclose(nav_simple, nav_prices)


def test_rejects_zero_price() -> None:
    with pytest.raises(ValueError):
        validate_prices(np.array([10.0, 0.0]))


def test_rejects_infinity() -> None:
    with pytest.raises(ValueError):
        validate_prices(np.array([10.0, np.inf]))


def test_nan_can_be_allowed() -> None:
    prices = np.array([10.0, np.nan, 10.5])
    result = simple_returns(prices, allow_nan=True)

    assert np.isnan(result).all()
```

运行：

```bash
pytest -q
```

---

## 五、测试设计原则

### 测试具体值

```python
assert result[0] == pytest.approx(0.02)
```

### 测试形状

```python
assert result.shape == (prices.size - 1,)
```

### 测试数学恒等式

```python
assert np.allclose(
    nav_from_simple_returns(simple),
    prices / prices[0],
)
```

### 测试错误输入

```python
with pytest.raises(ValueError):
    validate_prices(...)
```

好的测试不只证明代码“能运行”，还要证明金融和数学关系正确。

---

## 六、`pyproject.toml` 示例

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "quant-research"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "numpy>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

安装开发环境：

```bash
python -m pip install -e ".[dev]"
```

---

## 七、演示程序

```python
import numpy as np

from quant_research.returns import (
    log_returns,
    nav_from_log_returns,
    nav_from_simple_returns,
    simple_returns,
)

prices = np.array(
    [10.0, 10.2, 10.1, 10.5, 10.8],
    dtype=np.float64,
)

simple = simple_returns(prices)
logarithmic = log_returns(prices)

nav_simple = nav_from_simple_returns(simple)
nav_log = nav_from_log_returns(logarithmic)

print("价格：", prices)
print("简单收益率：", simple)
print("对数收益率：", logarithmic)
print("简单收益率净值：", nav_simple)
print("对数收益率净值：", nav_log)
print("净值是否一致：", np.allclose(nav_simple, nav_log))
```

---

## 八、第二周核心函数清单

| 函数 | 作用 |
|---|---|
| `np.array` / `np.asarray` | 创建或转换数组 |
| `np.isfinite` | 检查有限值 |
| `np.isnan` | 检查缺失值 |
| `np.isinf` | 检查无穷值 |
| `np.any` / `np.all` | 汇总布尔条件 |
| `np.log` / `np.log1p` | 计算对数 |
| `np.exp` / `np.expm1` | 从对数恢复增长率 |
| `np.prod` / `np.cumprod` | 计算最终和逐期复利 |
| `np.sum` / `np.cumsum` | 计算最终和逐期累计和 |
| `np.concatenate` | 拼接初始净值 |
| `np.isclose` / `np.allclose` | 比较浮点结果 |

---

## 九、第二周验收标准

你应能独立解释：

- 数组和列表的主要区别；
- 为什么收益率数组少一行；
- 向量化为什么优于手工循环；
- 简单收益率与对数收益率的关系；
- 为什么对数收益率可以跨时间相加；
- 为什么平均收益率不等于累计收益率；
- `NaN`、`inf` 和零值的区别；
- 为什么缺失收益不能默认填零。

---

## 十、提交建议

```bash
git status
git diff
git add src tests pyproject.toml README.md
git diff --staged
git commit -m "完成第二周单资产收益率模块"
```

---

## 第二周检查清单

- [ ] 简单收益率与手工计算一致。
- [ ] 对数收益率等于 `np.log1p(simple_returns)`。
- [ ] 三种净值计算方式一致。
- [ ] 零价格和无穷值会被拒绝。
- [ ] `allow_nan` 的行为有测试。
- [ ] 所有测试通过。
- [ ] README 记录安装、运行和测试方法。
