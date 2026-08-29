# 第 3 周第 7 天：多资产分析综合项目

## 今日目标

把第三周学习的二维数组、`axis`、广播、收益率、年化指标、布尔筛选和异常值识别整合为一个完整流程：

```text
多资产价格矩阵
→ 数据校验
→ 日收益率
→ 累计净值
→ 均值与波动率
→ 年化指标
→ 上涨比例
→ 异常收益识别
→ 单元测试
```

完成后，应能够从形状为 `(交易日数量, 股票数量)` 的价格矩阵生成完整的多资产统计报告。

---

## 一、输入与输出

输入价格矩阵：

$$
P\in\mathbb{R}^{T\times N}
$$

其中：

- $T$：交易日数量；
- $N$：股票数量；
- 每一行代表一个交易日；
- 每一列代表一只股票。

主要输出：

| 输出 | 形状 |
|---|---:|
| 简单收益率矩阵 | $(T-1,N)$ |
| 归一化净值矩阵 | $(T,N)$ |
| 平均日收益率 | $(N,)$ |
| 日波动率 | $(N,)$ |
| 年化收益率 | $(N,)$ |
| 年化波动率 | $(N,)$ |
| 上涨比例 | $(N,)$ |
| 累计收益率 | $(N,)$ |
| 稳健 Z-score | $(T-1,N)$ |
| 异常值标记矩阵 | $(T-1,N)$ |

---

## 二、核心数学关系

### 1. 简单收益率

股票 $i$ 在第 $t$ 个收益期间的简单收益率为：

$$
R_{t,i}=\frac{P_{t,i}}{P_{t-1,i}}-1
$$

价格矩阵有 $T$ 行时，只能形成 $T-1$ 个相邻价格区间，因此收益率矩阵比价格矩阵少一行。

### 2. 累计净值

初始净值设为：

$$
NAV_{0,i}=1
$$

之后的净值为：

$$
NAV_{t,i}=\prod_{k=1}^{t}(1+R_{k,i})
$$

在不考虑分红、拆股和复权问题时，还应满足：

$$
NAV_{t,i}=\frac{P_{t,i}}{P_{0,i}}
$$

这两个公式是验证程序正确性的核心依据。

### 3. 平均日收益率

$$
\bar R_i=\frac{1}{n}\sum_{t=1}^{n}R_{t,i}
$$

平均日收益率表示样本内单期收益的算术平均，不等于累计收益率。

### 4. 样本波动率

$$
s_i=\sqrt{\frac{1}{n-1}\sum_{t=1}^{n}(R_{t,i}-\bar R_i)^2}
$$

在 NumPy 中使用：

```python
np.std(returns, axis=0, ddof=1)
```

### 5. 年化指标

线性年化收益率：

$$
\mu_{annual,i}=252\bar R_i
$$

年化波动率：

$$
\sigma_{annual,i}=s_i\sqrt{252}
$$

年化结果是标准化估计，不代表未来必然获得相同收益或风险水平。

### 6. 上涨比例

定义上涨指示函数：

$$
\mathbf{1}(R_{t,i}>0)=
\begin{cases}
1,&R_{t,i}>0\\
0,&R_{t,i}\le 0
\end{cases}
$$

上涨比例为：

$$
p_i=\frac{1}{n}\sum_{t=1}^{n}\mathbf{1}(R_{t,i}>0)
$$

### 7. 累计收益率

以下三种方法应得到一致结果：

$$
CR_i=\prod_t(1+R_{t,i})-1
$$

$$
CR_i=NAV_{T-1,i}-1
$$

$$
CR_i=\frac{P_{T-1,i}}{P_{0,i}}-1
$$

### 8. MAD 稳健异常值

每只股票的收益率中位数：

$$
m_i=\operatorname{median}(R_{t,i})
$$

中位绝对偏差：

$$
MAD_i=\operatorname{median}(|R_{t,i}-m_i|)
$$

稳健 Z-score：

$$
Z_{t,i}^{robust}=\frac{R_{t,i}-m_i}{1.4826\times MAD_i}
$$

可使用以下规则进行统计标记：

$$
|Z_{t,i}^{robust}|>3
$$

该标记只说明收益率相对自身历史分布较极端，不代表数据一定错误。

---

## 三、项目目录

```text
quant-learning-path/
├── src/
│   └── quant_research/
│       ├── __init__.py
│       └── multi_asset.py
├── tests/
│   └── test_multi_asset.py
└── stages/
    └── stage-01-python-numpy-financial-data/
        └── weeks/
            └── week-03-numpy-multi-asset/
                └── days/
                    └── day-07-multi-asset-analysis-project.md
```

---

## 四、核心分析模块

```python
from typing import Any

import numpy as np


def validate_prices(prices: np.ndarray) -> np.ndarray:
    """校验并返回二维浮点价格矩阵。"""

    array = np.asarray(prices, dtype=np.float64)

    if array.ndim != 2:
        raise ValueError(
            "prices 必须是二维数组，形状应为 "
            "(交易日数量, 股票数量)"
        )

    n_days, n_assets = array.shape

    if n_days < 2:
        raise ValueError("至少需要两个交易日")

    if n_assets < 1:
        raise ValueError("至少需要包含一只股票")

    if not np.isfinite(array).all():
        raise ValueError("价格矩阵不能包含 NaN 或无穷值")

    if np.any(array <= 0):
        raise ValueError("所有价格必须严格大于 0")

    return array


def simple_returns(prices: np.ndarray) -> np.ndarray:
    """计算多资产简单收益率。"""

    array = validate_prices(prices)
    return array[1:, :] / array[:-1, :] - 1


def normalized_nav(prices: np.ndarray) -> np.ndarray:
    """将每只股票的首日净值归一化为 1。"""

    array = validate_prices(prices)
    return array / array[0, :]


def nav_from_returns(returns: np.ndarray) -> np.ndarray:
    """根据简单收益率计算累计净值。"""

    array = np.asarray(returns, dtype=np.float64)

    if array.ndim != 2:
        raise ValueError("returns 必须是二维数组")

    if array.shape[1] < 1:
        raise ValueError("收益率矩阵至少需要一只股票")

    if not np.isfinite(array).all():
        raise ValueError("收益率矩阵不能包含 NaN 或无穷值")

    if np.any(array <= -1):
        raise ValueError("简单收益率不能小于或等于 -100%")

    initial_nav = np.ones(
        (1, array.shape[1]),
        dtype=np.float64,
    )

    accumulated_nav = np.cumprod(
        1 + array,
        axis=0,
    )

    return np.vstack([initial_nav, accumulated_nav])


def summarize_returns(
    returns: np.ndarray,
    *,
    trading_days: int = 252,
) -> dict[str, np.ndarray]:
    """计算每只股票的收益率统计指标。"""

    array = np.asarray(returns, dtype=np.float64)

    if array.ndim != 2:
        raise ValueError("returns 必须是二维数组")

    if array.shape[0] < 2:
        raise ValueError("至少需要两个收益观察值")

    if not np.isfinite(array).all():
        raise ValueError("当前基础项目不接受 NaN 或无穷值")

    if trading_days <= 0:
        raise ValueError("trading_days 必须大于 0")

    valid_counts = np.isfinite(array).sum(axis=0)
    mean_daily_returns = np.mean(array, axis=0)
    daily_volatility = np.std(array, axis=0, ddof=1)

    annualized_returns = mean_daily_returns * trading_days
    annualized_volatility = (
        daily_volatility * np.sqrt(trading_days)
    )

    up_ratio = np.mean(array > 0, axis=0)

    cumulative_returns = (
        np.prod(1 + array, axis=0) - 1
    )

    return {
        "valid_counts": valid_counts,
        "mean_daily_returns": mean_daily_returns,
        "daily_volatility": daily_volatility,
        "annualized_returns": annualized_returns,
        "annualized_volatility": annualized_volatility,
        "up_ratio": up_ratio,
        "cumulative_returns": cumulative_returns,
    }


def robust_z_scores(returns: np.ndarray) -> np.ndarray:
    """使用中位数和 MAD 计算稳健 Z-score。"""

    array = np.asarray(returns, dtype=np.float64)

    if array.ndim != 2:
        raise ValueError("returns 必须是二维数组")

    if not np.isfinite(array).all():
        raise ValueError("收益率矩阵不能包含 NaN 或无穷值")

    median_returns = np.median(
        array,
        axis=0,
        keepdims=True,
    )

    mad = np.median(
        np.abs(array - median_returns),
        axis=0,
        keepdims=True,
    )

    scaled_mad = 1.4826 * mad

    safe_scaled_mad = np.where(
        scaled_mad == 0,
        np.nan,
        scaled_mad,
    )

    return (
        array - median_returns
    ) / safe_scaled_mad


def detect_outliers(
    returns: np.ndarray,
    *,
    threshold: float = 3.0,
) -> np.ndarray:
    """使用稳健 Z-score 标记异常收益。"""

    if threshold <= 0:
        raise ValueError("threshold 必须大于 0")

    scores = robust_z_scores(returns)
    return np.abs(scores) > threshold


def analyze_prices(
    prices: np.ndarray,
    *,
    trading_days: int = 252,
    outlier_threshold: float = 3.0,
) -> dict[str, Any]:
    """执行完整的多资产价格分析。"""

    array = validate_prices(prices)
    returns = simple_returns(array)

    nav_by_prices = normalized_nav(array)
    nav_by_returns = nav_from_returns(returns)

    if not np.allclose(nav_by_prices, nav_by_returns):
        raise RuntimeError(
            "价格法和收益率法计算的净值不一致"
        )

    statistics = summarize_returns(
        returns,
        trading_days=trading_days,
    )

    scores = robust_z_scores(returns)
    outlier_mask = detect_outliers(
        returns,
        threshold=outlier_threshold,
    )

    return {
        "prices": array,
        "returns": returns,
        "nav": nav_by_prices,
        "statistics": statistics,
        "robust_z_scores": scores,
        "outlier_mask": outlier_mask,
    }
```

---

## 五、运行示例

```python
import numpy as np

prices = np.array(
    [
        [20.00, 15.00, 8.00, 40.00],
        [20.40, 15.30, 7.90, 40.80],
        [20.20, 15.60, 8.10, 41.20],
        [21.00, 15.40, 8.30, 40.50],
        [21.50, 15.80, 8.20, 41.50],
        [21.20, 16.00, 8.50, 42.00],
    ],
    dtype=np.float64,
)

result = analyze_prices(prices)

print("收益率矩阵：")
print(result["returns"])

print("归一化净值：")
print(result["nav"])

print("累计收益率：")
print(result["statistics"]["cumulative_returns"])

print("异常值标记：")
print(result["outlier_mask"])
```

---

## 六、如何解读结果

### 平均日收益率

表示样本内单期收益的算术平均。它不是累计收益，也不是未来收益预测。

### 日波动率

表示收益率围绕均值的离散程度，同时包含上涨和下跌波动。

### 年化收益率

这里使用平均日收益率乘以 252。样本较短时，结果可能非常夸张，必须同时报告样本长度。

### 年化波动率

使用根号时间法则将日波动率转换到年度尺度。该方法依赖收益相对稳定等简化假设。

### 上涨比例

只统计上涨次数，不考虑每次涨跌幅度。上涨比例高不代表累计收益一定为正。

### 异常收益数量

表示收益率相对自身历史分布较极端。异常收益可能是真实行情、涨跌停、公司事件、未复权价格或数据错误，不能自动删除。

---

## 七、单元测试

```python
import numpy as np
import pytest


def test_returns_shape() -> None:
    prices = np.array(
        [
            [10.0, 20.0, 30.0],
            [10.2, 19.8, 30.6],
            [10.1, 20.4, 30.3],
            [10.5, 20.8, 31.2],
            [10.8, 20.5, 31.8],
        ],
        dtype=np.float64,
    )

    returns = simple_returns(prices)
    assert returns.shape == (4, 3)


def test_first_return() -> None:
    prices = np.array(
        [
            [10.0, 20.0, 30.0],
            [10.2, 19.8, 30.6],
        ],
        dtype=np.float64,
    )

    expected = np.array([0.02, -0.01, 0.02])
    assert np.allclose(simple_returns(prices)[0], expected)


def test_two_nav_methods_are_equal() -> None:
    prices = np.array(
        [
            [10.0, 20.0],
            [10.2, 19.8],
            [10.5, 20.4],
        ],
        dtype=np.float64,
    )

    returns = simple_returns(prices)

    assert np.allclose(
        normalized_nav(prices),
        nav_from_returns(returns),
    )


def test_cumulative_return_matches_prices() -> None:
    prices = np.array(
        [
            [10.0, 20.0],
            [10.2, 19.8],
            [10.5, 20.4],
        ],
        dtype=np.float64,
    )

    result = analyze_prices(prices)

    cumulative_from_statistics = (
        result["statistics"]["cumulative_returns"]
    )

    cumulative_from_prices = (
        prices[-1] / prices[0] - 1
    )

    assert np.allclose(
        cumulative_from_statistics,
        cumulative_from_prices,
    )


def test_invalid_zero_price() -> None:
    prices = np.array(
        [
            [10.0, 20.0],
            [0.0, 21.0],
        ]
    )

    with pytest.raises(ValueError):
        validate_prices(prices)


def test_robust_outlier_detection() -> None:
    returns = np.array(
        [
            [0.010],
            [0.011],
            [0.009],
            [0.0105],
            [0.200],
        ],
        dtype=np.float64,
    )

    outliers = detect_outliers(
        returns,
        threshold=3.0,
    )

    assert outliers.shape == returns.shape
    assert outliers[-1, 0]
    assert outliers.sum() == 1
```

运行测试：

```bash
pytest -q
```

---

## 八、今天需要掌握的 Python 函数

| 函数 | 用法 |
|---|---|
| `np.asarray` | 将输入转换为指定类型的 NumPy 数组 |
| `np.isfinite` | 检查 `NaN`、`inf` 和 `-inf` |
| `np.any` | 判断是否至少有一个元素满足条件 |
| `np.mean` | 沿指定方向计算均值 |
| `np.std` | 沿指定方向计算标准差 |
| `np.prod` | 计算最终累计乘积 |
| `np.cumprod` | 计算完整累计净值路径 |
| `np.median` | 计算中位数 |
| `np.abs` | 计算绝对值 |
| `np.where` | 根据条件选择数值 |
| `np.allclose` | 判断两个浮点数组是否近似相等 |
| `np.vstack` | 沿行方向拼接数组 |

---

## 九、第三周验收标准

完成本周后，应能够解释：

- 为什么价格矩阵通常采用“行是日期、列是股票”；
- 为什么收益率矩阵比价格矩阵少一行；
- `axis=0` 和 `axis=1` 的金融含义；
- 广播如何将每只股票的参数应用到所有日期；
- 简单收益率和对数收益率的区别；
- 平均收益率和累计收益率为什么不同；
- 年化收益与年化波动率为什么使用不同倍数；
- 时间序列异常和横截面异常的区别；
- 为什么异常值不等于错误数据。

编程上应能够独立完成：

```python
returns = prices[1:] / prices[:-1] - 1
nav = prices / prices[0]
mean_returns = returns.mean(axis=0)
volatility = returns.std(axis=0, ddof=1)
annualized_volatility = volatility * np.sqrt(252)
portfolio_returns = returns @ weights
```

---

## 十、复盘问题

1. 两只股票累计收益率相同，风险是否一定相同？
2. 一只股票上涨比例为 60%，是否一定赚钱？
3. 年化收益率很高，是否足以说明策略有效？
4. 稳健 Z-score 超过 3，是否应该直接删除该收益？
5. 为什么数学恒等关系可以用作单元测试？

---

## 今日结论

第三周已经完成从单资产一维数组到多资产二维矩阵的升级，并建立了以下完整能力：

```text
多资产收益率计算
多资产净值计算
批量均值与波动率
年化指标
组合收益率
布尔事件统计
稳健异常值识别
数据输入校验
基础单元测试
```

下一周进入 pandas 基础与金融时间序列，开始使用真实日期、股票代码和带标签的标准行情表。
