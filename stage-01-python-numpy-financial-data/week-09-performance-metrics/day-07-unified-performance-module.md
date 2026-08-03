# 第 9 周第 7 天：统一策略绩效评价模块

> 学习日期：2026-08-03  
> 所属阶段：第一阶段——Python、NumPy 与金融数据基础  
> 预计用时：180—220 分钟  
> 难度等级：综合  
> 学习状态：已完成

---

## 一、今日新名词解释

### 1.1 绩效报告

- 英文名称：Performance Report
- 常用缩写：`Report`
- 基本含义：把策略收益、风险、回撤、相对表现和交易质量等指标组织成统一结果。
- 通俗理解：不再零散地计算一个夏普比率或一个最大回撤，而是一次性生成策略的“体检报告”。
- 今日用途：作为统一绩效评价模块的最终输出。
- 易混淆概念：回测结果。回测结果包含持仓、成交、资金变化等完整过程，绩效报告只是对回测结果的统计总结。

### 1.2 指标协议

- 英文名称：Metric Contract
- 常用缩写：`Contract`
- 基本含义：提前规定每个指标接收什么数据、采用什么频率、如何处理缺失值以及返回什么结果。
- 通俗理解：所有函数遵守同一套“输入输出规则”，避免每个指标各算各的。
- 今日用途：统一策略收益、基准收益、交易收益、年化因子和无风险利率的口径。
- 易混淆概念：函数签名。函数签名只是参数形式，指标协议还包含数学口径、异常处理和边界定义。

### 1.3 不变量

- 英文名称：Invariant
- 常用缩写：`Invariant`
- 基本含义：无论输入样本如何变化，只要满足前提条件，就必须始终成立的性质。
- 通俗理解：用于判断程序有没有算错的“硬规则”。
- 今日用途：为最大回撤、超额收益、Calmar 和交易指标编写自动测试。
- 易混淆概念：样例结果。样例结果只验证一组数据，不变量能够验证一类数据。

---

## 二、今日学习目标

完成今天的学习后，应能够：

1. 把年化收益、年化波动率、夏普比率、最大回撤、Calmar、超额收益、胜率和盈亏比组织为统一绩效向量。
2. 明确策略收益、基准收益和交易收益的不同数据粒度。
3. 正确设置日频、周频或月频数据的年化因子。
4. 将年化无风险利率转换为单期无风险收益率。
5. 对齐策略与基准的共同有效日期，避免错误比较。
6. 使用统一 Python 接口生成完整绩效报告。
7. 使用已知结果测试、边界测试和不变量测试验证绩效模块。
8. 理解为什么一个高收益策略仍可能因为波动、回撤或交易质量较差而不可接受。

---

## 三、核心知识教学

本节学习以下核心概念：

1. 绩效指标向量
2. 统一输入输出协议
3. 可验证绩效模块

### 3.1 绩效指标向量

#### 3.1.1 概念解释

##### 标准定义

> 绩效指标向量是由多个互补指标组成的有序结果，用于同时描述策略的收益水平、波动风险、下行风险、相对表现和交易质量。

单个指标只能回答一个局部问题：

- 年化收益回答“赚了多少”。
- 年化波动率回答“收益有多不稳定”。
- 夏普比率回答“每承担一单位总体波动获得多少超额收益”。
- 最大回撤回答“历史上最严重的资金缩水是多少”。
- Calmar 回答“每承担一单位最大回撤获得多少年化收益”。
- 年化超额收益回答“相对基准多赚了多少”。
- 胜率回答“盈利交易占多少”。
- 盈亏比回答“平均盈利相对平均亏损有多大”。

##### 通俗理解

评价策略不能只看收益率。

一个策略可能年化收益很高，但净值经常大幅波动；也可能胜率很高，却通过多次小赚掩盖少数巨亏。因此需要把多个指标放在同一个结果中联合判断。

##### 为什么需要这个概念

1. 防止只选择对策略有利的单一指标。
2. 让不同策略使用相同列名和相同口径进行比较。
3. 为策略筛选、参数搜索和回测报告提供统一数据结构。
4. 便于后续把绩效结果保存到 pandas、SQL 或 DuckDB。
5. 便于自动测试和批量研究。

##### 核心要点

- 绩效指标之间是互补关系，不是互相替代关系。
- 周期级收益指标与交易级指标必须分开计算。
- 所有指标必须记录频率、样本区间和年化因子。
- 遇到分母为零时，优先返回未定义值 `NaN`，不要伪造一个极大值。

##### 简单示例

策略 A 的年化收益为 \(20\%\)，最大回撤为 \(-40\%\)。

策略 B 的年化收益为 \(15\%\)，最大回撤为 \(-10\%\)。

只看收益时，策略 A 更高；但 Calmar 分别为：

\[
Calmar_A
=
\frac{20\%}{40\%}
=
0.5
\]

\[
Calmar_B
=
\frac{15\%}{10\%}
=
1.5
\]

策略 B 的绝对收益较低，但单位最大回撤对应的收益更高。

#### 3.1.2 数学解释

##### 数学定义

设策略共有 \(T\) 期收益：

\[
r_1,r_2,\ldots,r_T
\]

每年包含 \(A\) 个收益周期。

首先构造净值：

\[
V_0=1
\]

\[
V_t
=
V_{t-1}(1+r_t)
\]

逐期展开：

\[
V_1
=
1+r_1
\]

\[
V_2
=
(1+r_1)(1+r_2)
\]

\[
V_T
=
\prod_{t=1}^{T}(1+r_t)
\]

几何年化收益为：

\[
R_{\text{ann}}
=
V_T^{A/T}-1
\]

样本标准差为：

\[
s_r
=
\sqrt{
\frac{
\sum_{t=1}^{T}(r_t-\bar r)^2
}{
T-1
}
}
\]

年化波动率为：

\[
\sigma_{\text{ann}}
=
s_r\sqrt A
\]

设年化无风险收益率为 \(R_f\)，对应的单期无风险收益率为：

\[
r_f
=
(1+R_f)^{1/A}-1
\]

夏普比率为：

\[
Sharpe
=
\frac{\bar r-r_f}{s_r}\sqrt A
\]

定义历史峰值：

\[
H_t
=
\max_{0\le s\le t}V_s
\]

定义回撤：

\[
D_t
=
\frac{V_t}{H_t}-1
\]

最大回撤为：

\[
MDD
=
\min_{0\le t\le T}D_t
\]

Calmar 比率为：

\[
Calmar
=
\frac{R_{\text{ann}}}{|MDD|}
\]

设基准收益为 \(b_t\)，基准年化收益为：

\[
R_{b,\text{ann}}
=
\left(
\prod_{t=1}^{T}(1+b_t)
\right)^{A/T}-1
\]

本模块把年化超额收益定义为：

\[
ER_{\text{ann}}
=
R_{\text{ann}}
-
R_{b,\text{ann}}
\]

设共有 \(N\) 笔已经完成的交易，单笔交易收益为：

\[
q_1,q_2,\ldots,q_N
\]

盈利交易数量为：

\[
N_+
=
\sum_{j=1}^{N}\mathbf{1}(q_j>0)
\]

胜率为：

\[
WR
=
\frac{N_+}{N}
\]

平均盈利为：

\[
\bar q_+
=
\frac{
\sum_{j:q_j>0}q_j
}{
N_+
}
\]

亏损交易数量为：

\[
N_-
=
\sum_{j=1}^{N}\mathbf{1}(q_j<0)
\]

平均亏损为：

\[
\bar q_-
=
\frac{
\sum_{j:q_j<0}q_j
}{
N_-
}
\]

盈亏比为：

\[
PLR
=
\frac{\bar q_+}{|\bar q_-|}
\]

最终绩效指标向量可以写为：

\[
\mathbf{m}
=
\begin{bmatrix}
R_{\text{ann}} \\
\sigma_{\text{ann}} \\
Sharpe \\
MDD \\
Calmar \\
ER_{\text{ann}} \\
WR \\
PLR
\end{bmatrix}
\]

##### 公式推导

以几何年化收益为例。

第一步，计算总增长因子：

\[
G
=
\prod_{t=1}^{T}(1+r_t)
\]

第二步，假设每期以固定增长因子 \(g\) 增长，则：

\[
g^T
=
G
\]

第三步，两边同时取 \(T\) 次方根：

\[
g
=
G^{1/T}
\]

第四步，一年包含 \(A\) 期，因此年度增长因子为：

\[
g^A
=
\left(G^{1/T}\right)^A
\]

第五步，整理指数：

\[
g^A
=
G^{A/T}
\]

第六步，年度增长因子减去 1：

\[
R_{\text{ann}}
=
G^{A/T}-1
\]

再推导 Calmar。

第一步，最大回撤是负数或零：

\[
MDD\le 0
\]

第二步，风险幅度应为非负值：

\[
|MDD|
=
-MDD
\]

第三步，用年化收益除以最大回撤幅度：

\[
Calmar
=
\frac{R_{\text{ann}}}{|MDD|}
\]

因此，当年化收益为正时，Calmar 越高，表示相同历史最大回撤对应的收益越高。

##### 数值示例

已知三期收益：

\[
r_1=10\%
\]

\[
r_2=-20\%
\]

\[
r_3=25\%
\]

并设：

\[
A=3
\]

总增长因子为：

\[
G
=
(1+10\%)(1-20\%)(1+25\%)
\]

\[
G
=
1.10\times0.80\times1.25
\]

\[
G
=
1.10
\]

年化收益为：

\[
R_{\text{ann}}
=
1.10^{3/3}-1
\]

\[
R_{\text{ann}}
=
10\%
\]

净值路径为：

\[
1.00
\rightarrow
1.10
\rightarrow
0.88
\rightarrow
1.10
\]

从峰值 \(1.10\) 到谷底 \(0.88\) 的回撤为：

\[
MDD
=
\frac{0.88}{1.10}-1
\]

\[
MDD
=
-20\%
\]

Calmar 为：

\[
Calmar
=
\frac{10\%}{20\%}
\]

\[
Calmar
=
0.5
\]

##### 结果解释

该策略三期累计收益为 \(10\%\)，由于三期正好被视为一年，所以年化收益也是 \(10\%\)。其历史最大回撤为 \(-20\%\)，因此每承担一单位最大回撤幅度，只获得 \(0.5\) 单位年化收益。

#### 3.1.3 Python 代码

##### 相关函数

- `pd.Series`：保存带索引的收益序列。
- `Series.prod()`：计算复利增长因子。
- `Series.std()`：计算样本标准差。
- `Series.cumprod()`：构造净值序列。
- `numpy.maximum.accumulate()`：构造历史峰值序列。
- `pd.Series`：统一返回指标名称与指标值。

##### 示例代码

```python
import numpy as np
import pandas as pd


def build_metric_vector(
    strategy_returns: pd.Series,
    periods_per_year: int,
) -> pd.Series:
    """计算基础绩效指标向量。"""
    if strategy_returns.empty:
        raise ValueError("strategy_returns 不能为空")

    if periods_per_year <= 0:
        raise ValueError("periods_per_year 必须大于 0")

    returns = strategy_returns.astype(float).dropna()

    if returns.empty:
        raise ValueError("收益率清洗后不能为空")

    if (returns <= -1).any():
        raise ValueError("单期收益率必须大于 -1")

    growth = float((1.0 + returns).prod())
    annualized_return = growth ** (
        periods_per_year / len(returns)
    ) - 1.0

    annualized_volatility = float(
        returns.std(ddof=1) * np.sqrt(periods_per_year)
    )

    wealth = np.concatenate(
        ([1.0], (1.0 + returns).cumprod().to_numpy())
    )
    running_peak = np.maximum.accumulate(wealth)
    drawdown = wealth / running_peak - 1.0
    max_drawdown = float(drawdown.min())

    if np.isclose(max_drawdown, 0.0):
        calmar = float("nan")
    else:
        calmar = annualized_return / abs(max_drawdown)

    return pd.Series(
        {
            "annualized_return": annualized_return,
            "annualized_volatility": annualized_volatility,
            "max_drawdown": max_drawdown,
            "calmar_ratio": calmar,
        },
        name="value",
    )


def main() -> None:
    returns = pd.Series([0.10, -0.20, 0.25])

    report = build_metric_vector(
        strategy_returns=returns,
        periods_per_year=3,
    )

    print(report.round(6))


if __name__ == "__main__":
    main()
```

##### 运行结果

```text
annualized_return        0.100000
annualized_volatility    0.396863
max_drawdown            -0.200000
calmar_ratio             0.500000
Name: value, dtype: float64
```

##### 代码解释

1. `prod()` 把单期收益按复利规则连接为总增长因子。
2. `periods_per_year / len(returns)` 把样本增长速度换算为年度增长速度。
3. `cumprod()` 构造从期初资金 1 开始的净值路径。
4. `maximum.accumulate()` 为每个时点寻找历史最高净值。
5. 当前净值除以历史峰值再减 1，得到回撤序列。
6. 当最大回撤为 0 时，Calmar 没有有效分母，因此返回 `NaN`。

#### 3.1.4 量化应用

##### 应用场景

- 比较多个策略的收益与风险。
- 为参数优化生成目标指标。
- 对策略进行上线前验收。
- 构建每日、每周或每月自动绩效报告。
- 将回测结果批量保存到研究数据库。

##### 使用方式

1. 从回测系统获取周期级策略收益。
2. 根据收益频率设置年化因子。
3. 计算收益、波动、回撤和相对指标。
4. 从成交记录生成交易级收益。
5. 将所有指标组合为一行绩效报告。
6. 对比策略之间的收益、风险和稳定性。

##### 使用限制

- 指标向量不能替代净值曲线和逐笔交易检查。
- 不同样本区间的指标不能直接比较。
- 高频与低频策略的交易级指标定义可能不同。
- 短样本年化会放大偶然结果。
- 高胜率不代表正期望，高盈亏比也不代表交易足够稳定。

### 3.2 统一输入输出协议

#### 3.2.1 概念解释

##### 标准定义

> 统一输入输出协议是对绩效函数的数据类型、索引、频率、缺失值处理、异常值边界和输出字段作出的明确约定。

今天的模块使用三类输入：

1. `strategy_returns`：周期级策略收益。
2. `benchmark_returns`：同频率、同日期的周期级基准收益。
3. `trade_returns`：每笔已完成交易的收益。

同时使用一个配置对象：

- `periods_per_year`：每年的收益周期数量。
- `annual_risk_free_rate`：年化无风险收益率。
- `ddof`：标准差自由度。

##### 通俗理解

统一协议相当于规定：

- 日收益不能误当月收益。
- 年化无风险收益率不能直接从日收益中相减。
- 策略和基准必须先对齐日期。
- 缺失值和无穷值必须先处理。
- 单期收益不能小于或等于 \(-100\%\)。
- 无法定义的比率返回 `NaN`。

##### 为什么需要这个概念

1. 同一个公式在不同频率下需要不同年化因子。
2. 基准缺失一个交易日就会造成日期错位。
3. 交易收益与每日收益不能混用。
4. 不同函数各自清洗数据会产生不一致样本。
5. 自动化研究需要稳定的字段名和异常处理规则。

##### 核心要点

- 日频 A 股收益通常使用 \(A=252\)，但应根据数据和研究约定明确设置。
- 周频常使用 \(A=52\)，月频常使用 \(A=12\)。
- 策略与基准必须采用共同有效区间。
- 年化无风险收益率必须先转换为单期无风险收益率。
- 标准差采用样本口径时通常设置 `ddof=1`。
- 零波动、零回撤、没有盈利交易或没有亏损交易时，相应比率应视为未定义。

##### 简单示例

假设策略有 252 个日收益，基准只有 251 个有效日期。

错误做法是按数组位置直接相减。

正确做法是根据日期索引进行内连接，只保留策略与基准都有效的日期，再计算相对指标。

#### 3.2.2 数学解释

##### 数学定义

把模块输入表示为：

\[
\mathcal{D}
=
\left(
\mathbf r,
\mathbf b,
\mathbf q;
A,
R_f,
d
\right)
\]

其中：

- \(\mathbf r\)：策略周期收益向量。
- \(\mathbf b\)：基准周期收益向量。
- \(\mathbf q\)：交易收益向量。
- \(A\)：年化因子。
- \(R_f\)：年化无风险收益率。
- \(d\)：标准差自由度。

绩效模块是一个映射：

\[
F:
\mathcal{D}
\rightarrow
\mathbf m
\]

这里的 \(\mathbf m\) 是统一绩效指标向量。

为了保证频率一致，需要把年化无风险增长因子分解到每一期。

年度增长因子为：

\[
1+R_f
\]

设单期无风险增长因子为：

\[
1+r_f
\]

一年共有 \(A\) 期，因此：

\[
(1+r_f)^A
=
1+R_f
\]

两边同时取 \(A\) 次方根：

\[
1+r_f
=
(1+R_f)^{1/A}
\]

两边同时减去 1：

\[
r_f
=
(1+R_f)^{1/A}-1
\]

策略与基准的日期集合分别为：

\[
I_p
\]

和：

\[
I_b
\]

共同有效日期集合为：

\[
I
=
I_p\cap I_b
\]

相对指标只能使用：

\[
\{r_t,b_t:t\in I\}
\]

不能使用日期不一致的两个序列。

##### 公式推导

证明为什么不能把年化无风险收益率直接除以年化因子作为精确单期收益率。

精确单期收益率为：

\[
r_f
=
(1+R_f)^{1/A}-1
\]

当 \(R_f\) 很小时，可以使用一阶近似：

\[
(1+R_f)^{1/A}
\approx
1+\frac{R_f}{A}
\]

因此：

\[
r_f
\approx
\frac{R_f}{A}
\]

这只是近似关系。

精确关系仍然是：

\[
r_f
=
(1+R_f)^{1/A}-1
\]

当收益率较高或周期较长时，直接使用 \(R_f/A\) 会产生更明显误差。

##### 数值示例

设年化无风险收益率为：

\[
R_f=2\%
\]

月频数据的年化因子为：

\[
A=12
\]

精确月度无风险收益率为：

\[
r_f
=
(1+2\%)^{1/12}-1
\]

\[
r_f
=
1.02^{1/12}-1
\]

\[
r_f
\approx
0.1652\%
\]

简单除法近似为：

\[
\frac{2\%}{12}
\]

\[
\frac{2\%}{12}
\approx
0.1667\%
\]

两者非常接近，但并不完全相等。

##### 结果解释

当无风险收益率较低时，简单除法可作为近似；统一模块应优先采用复利转换公式，使日频、周频和月频结果保持一致。

#### 3.2.3 Python 代码

##### 相关函数

- `dataclasses.dataclass`：保存只读配置。
- `Series.replace()`：把正负无穷转换为缺失值。
- `Series.dropna()`：删除无效观测。
- `pd.concat(..., join="inner")`：按索引保留共同有效日期。
- `__post_init__()`：在配置对象创建时验证参数。

##### 示例代码

```python
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PerformanceConfig:
    periods_per_year: int = 252
    annual_risk_free_rate: float = 0.0
    ddof: int = 1

    def __post_init__(self) -> None:
        if self.periods_per_year <= 0:
            raise ValueError("periods_per_year 必须大于 0")

        if self.annual_risk_free_rate <= -1:
            raise ValueError(
                "annual_risk_free_rate 必须大于 -1"
            )

        if self.ddof < 0:
            raise ValueError("ddof 不能为负数")


def clean_return_series(
    values: pd.Series,
    name: str,
) -> pd.Series:
    series = values.astype(float).rename(name)
    series = series.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna()

    if series.empty:
        raise ValueError(f"{name} 清洗后不能为空")

    if (series <= -1).any():
        raise ValueError(
            f"{name} 中的单期收益必须大于 -1"
        )

    return series


def align_returns(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> pd.DataFrame:
    strategy = clean_return_series(
        strategy_returns,
        "strategy_return",
    )
    benchmark = clean_return_series(
        benchmark_returns,
        "benchmark_return",
    )

    aligned = pd.concat(
        [strategy, benchmark],
        axis=1,
        join="inner",
    ).dropna()

    if aligned.empty:
        raise ValueError("策略与基准没有共同有效日期")

    return aligned


def periodic_risk_free_rate(
    config: PerformanceConfig,
) -> float:
    return (
        1.0 + config.annual_risk_free_rate
    ) ** (1.0 / config.periods_per_year) - 1.0
```

##### 运行结果

```text
配置对象负责验证年化因子、无风险利率和自由度。
clean_return_series 负责统一清洗收益。
align_returns 负责按日期对齐策略与基准。
periodic_risk_free_rate 返回与收益频率一致的无风险收益率。
```

##### 代码解释

1. `frozen=True` 防止计算过程中意外修改年化参数。
2. `replace([np.inf, -np.inf], np.nan)` 统一处理无穷值。
3. 收益小于或等于 \(-1\) 意味着单期亏损达到或超过全部资本，不符合普通简单收益复利计算的输入条件。
4. `join="inner"` 只保留策略与基准共同存在的日期。
5. 无风险收益率使用复利关系转换，而不是机械除以年化因子。

#### 3.2.4 量化应用

##### 应用场景

- 日频股票策略与沪深 300 对比。
- 周频行业轮动策略评价。
- 月频资产配置策略评价。
- 多策略批量回测。
- 自动生成研究数据库中的标准绩效表。

##### 使用方式

1. 为每个回测保存收益频率。
2. 创建对应的 `PerformanceConfig`。
3. 对策略收益进行统一清洗。
4. 对策略与基准按日期进行内连接。
5. 从交易日志单独提取交易收益。
6. 调用统一评价函数。
7. 保存配置、样本起止日期和指标结果。

##### 使用限制

- `dropna()` 是否合理取决于缺失原因，真实研究中应先调查缺失数据。
- 基准必须与策略风格和可投资范围匹配。
- 股票停牌、涨跌停和无成交日可能使收益序列的经济含义发生变化。
- 日频年化因子不应无条件固定为 252，应明确研究口径。
- 交易收益必须来自完整闭合交易，不能把未平仓浮盈亏混入已完成交易。

### 3.3 可验证绩效模块

#### 3.3.1 概念解释

##### 标准定义

> 可验证绩效模块是指每个核心指标都具有明确数学定义、可复现实现和自动测试，且能对错误输入、边界输入与已知结果作出稳定响应。

绩效模块至少需要三类测试：

1. 已知结果测试：输入人工可计算的数据，检查程序结果。
2. 边界测试：检查空数据、零波动、零回撤、无盈利交易和无亏损交易。
3. 不变量测试：检查最大回撤范围、相同策略与基准的超额收益等恒定性质。

##### 通俗理解

代码“能运行”不等于“算得正确”。

绩效指标经常不会报错，却可能因为漏掉期初净值、日期错位、年化因子错误或分母为零而悄悄给出错误结果。自动测试就是把这些错误在进入真实回测前暴露出来。

##### 为什么需要这个概念

1. 绩效指标会被用于策略筛选和资金决策。
2. 小错误经过参数搜索后可能被放大。
3. 多个函数组合后，人工检查难以覆盖所有情况。
4. 后续修改代码时需要防止旧功能被破坏。
5. 自动化 Agent 研究必须依赖可验证的底层函数。

##### 核心要点

- 最大回撤必须满足 \(-1<MDD\le 0\)。
- 策略与基准完全相同时，年化超额收益应为 0。
- 净值从未下降时，最大回撤为 0，Calmar 应返回 `NaN`。
- 波动率为 0 时，夏普比率应返回 `NaN`。
- 没有盈利交易或没有亏损交易时，盈亏比应返回 `NaN`。
- 已知样例应同时验证收益、回撤、Calmar、胜率和盈亏比。

##### 简单示例

使用收益：

\[
10\%,-20\%,25\%
\]

已知：

\[
R_{\text{ann}}=10\%
\]

\[
MDD=-20\%
\]

\[
Calmar=0.5
\]

程序必须得到相同结果。

#### 3.3.2 数学解释

##### 数学定义

最大回撤的不变量来自：

\[
H_t
=
\max_{0\le s\le t}V_s
\]

根据最大值定义：

\[
H_t
\ge
V_t
\]

两边同时除以正数 \(H_t\)：

\[
\frac{V_t}{H_t}
\le
1
\]

两边同时减去 1：

\[
\frac{V_t}{H_t}-1
\le
0
\]

因此：

\[
D_t\le 0
\]

在普通净值始终大于 0 的前提下：

\[
\frac{V_t}{H_t}>0
\]

两边同时减去 1：

\[
D_t>-1
\]

所以：

\[
-1<D_t\le 0
\]

最大回撤是所有回撤中的最小值，因此：

\[
-1<MDD\le 0
\]

再证明策略与基准相同时年化超额收益为 0。

若：

\[
r_t=b_t
\]

则：

\[
\prod_{t=1}^{T}(1+r_t)
=
\prod_{t=1}^{T}(1+b_t)
\]

因此：

\[
R_{\text{ann}}
=
R_{b,\text{ann}}
\]

根据定义：

\[
ER_{\text{ann}}
=
R_{\text{ann}}
-
R_{b,\text{ann}}
\]

代入相等关系：

\[
ER_{\text{ann}}
=
R_{\text{ann}}
-
R_{\text{ann}}
\]

最终得到：

\[
ER_{\text{ann}}
=
0
\]

##### 公式推导

证明净值单调不下降时最大回撤为 0。

若对所有 \(t\) 都有：

\[
V_t\ge V_{t-1}
\]

则当前净值始终等于当前历史最高值：

\[
V_t=H_t
\]

因此：

\[
D_t
=
\frac{V_t}{H_t}-1
\]

代入 \(V_t=H_t\)：

\[
D_t
=
\frac{H_t}{H_t}-1
\]

\[
D_t
=
1-1
\]

\[
D_t
=
0
\]

所有时点回撤都为 0，因此：

\[
MDD
=
0
\]

此时 Calmar 的分母为：

\[
|MDD|
=
0
\]

所以：

\[
Calmar
=
\frac{R_{\text{ann}}}{0}
\]

该比率没有有限定义，程序应返回 `NaN`。

##### 数值示例

交易收益为：

\[
10\%,-5\%,2\%,-1\%,0\%
\]

交易数量为：

\[
N=5
\]

盈利交易数量为：

\[
N_+=2
\]

胜率为：

\[
WR
=
\frac{2}{5}
\]

\[
WR
=
40\%
\]

平均盈利为：

\[
\bar q_+
=
\frac{10\%+2\%}{2}
\]

\[
\bar q_+
=
6\%
\]

平均亏损为：

\[
\bar q_-
=
\frac{-5\%-1\%}{2}
\]

\[
\bar q_-
=
-3\%
\]

盈亏比为：

\[
PLR
=
\frac{6\%}{|-3\%|}
\]

\[
PLR
=
2
\]

##### 结果解释

该交易集合的胜率只有 \(40\%\)，但平均盈利是平均亏损幅度的 2 倍。它说明低胜率策略仍可能依靠较高盈亏比获得正期望，但还需要结合交易成本和实际收益判断。

#### 3.3.3 Python 代码

##### 相关函数

- `numpy.isclose()`：比较浮点结果是否接近期望值。
- `assert`：表达必须成立的测试条件。
- `numpy.isnan()`：检查未定义结果。
- `Series.between()` 或区间比较：验证指标范围。
- 自定义 `run_self_tests()`：集中运行最小测试集合。

##### 示例代码

```python
import numpy as np
import pandas as pd


def win_rate(trade_returns: pd.Series) -> float:
    trades = trade_returns.astype(float).dropna()

    if trades.empty:
        raise ValueError("trade_returns 不能为空")

    return float((trades > 0).mean())


def profit_loss_ratio(
    trade_returns: pd.Series,
) -> float:
    trades = trade_returns.astype(float).dropna()

    if trades.empty:
        raise ValueError("trade_returns 不能为空")

    wins = trades[trades > 0]
    losses = trades[trades < 0]

    if wins.empty or losses.empty:
        return float("nan")

    return float(
        wins.mean() / abs(losses.mean())
    )


def run_trade_metric_tests() -> None:
    trades = pd.Series(
        [0.10, -0.05, 0.02, -0.01, 0.00]
    )

    actual_win_rate = win_rate(trades)
    actual_profit_loss_ratio = profit_loss_ratio(
        trades
    )

    assert np.isclose(actual_win_rate, 0.40)
    assert np.isclose(
        actual_profit_loss_ratio,
        2.00,
    )

    only_wins = pd.Series([0.01, 0.02, 0.03])
    assert np.isnan(
        profit_loss_ratio(only_wins)
    )


if __name__ == "__main__":
    run_trade_metric_tests()
    print("所有交易指标测试通过")
```

##### 运行结果

```text
所有交易指标测试通过
```

##### 代码解释

1. 零收益交易不属于盈利交易，但仍计入已完成交易总数。
2. 盈亏比只使用严格大于 0 的盈利交易和严格小于 0 的亏损交易。
3. 当没有盈利或没有亏损时，平均盈利与平均亏损无法同时定义，所以返回 `NaN`。
4. `np.isclose()` 避免浮点数精度问题造成测试误判。
5. 测试先验证正常样例，再验证只有盈利交易的边界样例。

#### 3.3.4 量化应用

##### 应用场景

- 在回测提交前自动运行绩效测试。
- 对多个策略批量生成报告并检查异常值。
- 在重构代码后进行回归测试。
- 为研究 Agent 提供可靠的基础指标函数。
- 对实盘与回测绩效采用同一套计算模块。

##### 使用方式

1. 为每个公式准备人工可验证样例。
2. 为分母为零和空数据准备边界样例。
3. 为最大回撤和超额收益编写不变量测试。
4. 每次修改指标代码后自动运行测试。
5. 测试通过后再对真实数据生成报告。

##### 使用限制

- 测试通过只能证明覆盖到的情况正确。
- 交易成本、滑点和停牌规则必须在上游回测中正确处理。
- 使用合成数据不能替代真实市场数据检查。
- 指标定义发生变化时，测试期望值也必须同步更新。
- 不同研究团队可能采用不同胜率分母或超额收益定义，必须在协议中写清楚。

---

## 四、综合案例

### 4.1 各个概念之间的关系

```text
策略周期收益、基准周期收益、逐笔交易收益
    ↓
统一输入输出协议
    ↓
数据清洗、频率配置、日期对齐
    ↓
绩效指标向量
    ↓
收益、波动、回撤、相对表现、交易质量
    ↓
已知结果测试、边界测试、不变量测试
    ↓
可复用的统一绩效评价模块
```

具体关系：

1. 统一输入输出协议决定每个指标使用什么数据和什么口径。
2. 绩效指标向量把多个互补指标组织成稳定输出。
3. 可验证绩效模块保证这些指标在正常输入和边界输入下符合数学定义。
4. 三者组合后，可以把一次回测结果转换为可比较、可保存、可测试的标准绩效报告。

### 4.2 综合使用场景

#### 场景描述

> 某月频策略已经得到 12 个月策略收益、同期基准收益和 8 笔已完成交易。现在需要一次性计算绝对绩效、风险调整绩效、相对绩效和交易质量，并通过自动测试验证模块。

#### 研究目标

1. 使用月频年化因子 \(A=12\)。
2. 使用年化无风险收益率 \(R_f=2\%\)。
3. 计算总收益、年化收益、年化波动率、夏普比率。
4. 计算最大回撤和 Calmar。
5. 计算基准年化收益和年化超额收益。
6. 计算胜率和盈亏比。
7. 对已知样例运行自动测试。
8. 输出统一绩效报告。

### 4.3 综合数学关系

策略年化收益：

\[
R_{p,\text{ann}}
=
\left(
\prod_{t=1}^{T}(1+r_t)
\right)^{A/T}-1
\]

基准年化收益：

\[
R_{b,\text{ann}}
=
\left(
\prod_{t=1}^{T}(1+b_t)
\right)^{A/T}-1
\]

年化超额收益：

\[
ER_{\text{ann}}
=
R_{p,\text{ann}}
-
R_{b,\text{ann}}
\]

单期无风险收益率：

\[
r_f
=
(1+R_f)^{1/A}-1
\]

夏普比率：

\[
Sharpe
=
\frac{\bar r-r_f}{s_r}\sqrt A
\]

最大回撤：

\[
MDD
=
\min_t
\left(
\frac{V_t}{H_t}-1
\right)
\]

Calmar：

\[
Calmar
=
\frac{R_{p,\text{ann}}}{|MDD|}
\]

胜率：

\[
WR
=
\frac{N_+}{N}
\]

盈亏比：

\[
PLR
=
\frac{\bar q_+}{|\bar q_-|}
\]

最终统一输出：

\[
\mathbf m
=
F(
\mathbf r,
\mathbf b,
\mathbf q;
A,
R_f,
d
)
\]

### 4.4 综合处理流程

```text
读取策略收益、基准收益和交易收益
    ↓
验证配置参数
    ↓
清洗缺失值与无穷值
    ↓
检查单期收益是否大于 -100%
    ↓
按日期对齐策略与基准
    ↓
计算绝对绩效指标
    ↓
计算相对绩效指标
    ↓
计算交易级指标
    ↓
组合为统一 pandas Series
    ↓
运行自动测试
    ↓
解释综合结果
```

### 4.5 示例 Python 代码

```python
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PerformanceConfig:
    """绩效评价配置。"""

    periods_per_year: int = 252
    annual_risk_free_rate: float = 0.0
    ddof: int = 1

    def __post_init__(self) -> None:
        if self.periods_per_year <= 0:
            raise ValueError(
                "periods_per_year 必须大于 0"
            )

        if self.annual_risk_free_rate <= -1:
            raise ValueError(
                "annual_risk_free_rate 必须大于 -1"
            )

        if self.ddof < 0:
            raise ValueError("ddof 不能为负数")


def clean_return_series(
    values: pd.Series | Iterable[float],
    name: str,
) -> pd.Series:
    """清洗并验证简单收益率序列。"""
    if isinstance(values, pd.Series):
        series = values.astype(float).rename(name)
    else:
        series = pd.Series(
            values,
            dtype=float,
            name=name,
        )

    series = series.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna()

    if series.empty:
        raise ValueError(f"{name} 清洗后不能为空")

    if (series <= -1).any():
        raise ValueError(
            f"{name} 中的单期收益必须大于 -1"
        )

    return series


def calculate_total_return(
    returns: pd.Series,
) -> float:
    """计算累计总收益。"""
    return float((1.0 + returns).prod() - 1.0)


def calculate_annualized_return(
    returns: pd.Series,
    periods_per_year: int,
) -> float:
    """计算几何年化收益。"""
    growth = float((1.0 + returns).prod())

    return float(
        growth ** (
            periods_per_year / len(returns)
        ) - 1.0
    )


def calculate_annualized_volatility(
    returns: pd.Series,
    config: PerformanceConfig,
) -> float:
    """计算年化波动率。"""
    if len(returns) <= config.ddof:
        return float("nan")

    return float(
        returns.std(ddof=config.ddof)
        * np.sqrt(config.periods_per_year)
    )


def calculate_sharpe_ratio(
    returns: pd.Series,
    config: PerformanceConfig,
) -> float:
    """计算年化夏普比率。"""
    if len(returns) <= config.ddof:
        return float("nan")

    periodic_risk_free_rate = (
        1.0 + config.annual_risk_free_rate
    ) ** (1.0 / config.periods_per_year) - 1.0

    volatility = float(
        returns.std(ddof=config.ddof)
    )

    if np.isclose(volatility, 0.0):
        return float("nan")

    periodic_excess_mean = float(
        returns.mean() - periodic_risk_free_rate
    )

    return float(
        periodic_excess_mean
        / volatility
        * np.sqrt(config.periods_per_year)
    )


def calculate_max_drawdown(
    returns: pd.Series,
) -> float:
    """计算带符号最大回撤。"""
    wealth = np.concatenate(
        (
            [1.0],
            (1.0 + returns).cumprod().to_numpy(),
        )
    )

    running_peak = np.maximum.accumulate(wealth)
    drawdown = wealth / running_peak - 1.0

    return float(drawdown.min())


def calculate_calmar_ratio(
    returns: pd.Series,
    periods_per_year: int,
) -> float:
    """计算 Calmar 比率。"""
    annualized_return = calculate_annualized_return(
        returns,
        periods_per_year,
    )
    max_drawdown = calculate_max_drawdown(
        returns
    )

    if np.isclose(max_drawdown, 0.0):
        return float("nan")

    return float(
        annualized_return / abs(max_drawdown)
    )


def align_strategy_and_benchmark(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> pd.DataFrame:
    """按索引对齐策略与基准收益。"""
    aligned = pd.concat(
        [
            strategy_returns.rename(
                "strategy_return"
            ),
            benchmark_returns.rename(
                "benchmark_return"
            ),
        ],
        axis=1,
        join="inner",
    ).dropna()

    if aligned.empty:
        raise ValueError(
            "策略与基准没有共同有效区间"
        )

    return aligned


def calculate_annualized_excess_return(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    periods_per_year: int,
) -> tuple[float, float]:
    """计算基准年化收益和年化超额收益。"""
    aligned = align_strategy_and_benchmark(
        strategy_returns,
        benchmark_returns,
    )

    strategy_annualized_return = (
        calculate_annualized_return(
            aligned["strategy_return"],
            periods_per_year,
        )
    )
    benchmark_annualized_return = (
        calculate_annualized_return(
            aligned["benchmark_return"],
            periods_per_year,
        )
    )

    annualized_excess_return = (
        strategy_annualized_return
        - benchmark_annualized_return
    )

    return (
        benchmark_annualized_return,
        float(annualized_excess_return),
    )


def calculate_win_rate(
    trade_returns: pd.Series,
) -> float:
    """计算已完成交易胜率。"""
    return float((trade_returns > 0).mean())


def calculate_profit_loss_ratio(
    trade_returns: pd.Series,
) -> float:
    """计算平均盈利与平均亏损幅度之比。"""
    wins = trade_returns[trade_returns > 0]
    losses = trade_returns[trade_returns < 0]

    if wins.empty or losses.empty:
        return float("nan")

    return float(
        wins.mean() / abs(losses.mean())
    )


def evaluate_performance(
    strategy_returns: pd.Series | Iterable[float],
    config: PerformanceConfig,
    benchmark_returns:
        pd.Series | Iterable[float] | None = None,
    trade_returns:
        pd.Series | Iterable[float] | None = None,
) -> pd.Series:
    """生成统一绩效报告。"""
    strategy = clean_return_series(
        strategy_returns,
        "strategy_return",
    )

    result = {
        "observations": float(len(strategy)),
        "total_return": calculate_total_return(
            strategy
        ),
        "annualized_return":
            calculate_annualized_return(
                strategy,
                config.periods_per_year,
            ),
        "annualized_volatility":
            calculate_annualized_volatility(
                strategy,
                config,
            ),
        "sharpe_ratio":
            calculate_sharpe_ratio(
                strategy,
                config,
            ),
        "max_drawdown":
            calculate_max_drawdown(
                strategy
            ),
        "calmar_ratio":
            calculate_calmar_ratio(
                strategy,
                config.periods_per_year,
            ),
        "benchmark_annualized_return":
            float("nan"),
        "annualized_excess_return":
            float("nan"),
        "win_rate":
            float("nan"),
        "profit_loss_ratio":
            float("nan"),
    }

    if benchmark_returns is not None:
        benchmark = clean_return_series(
            benchmark_returns,
            "benchmark_return",
        )

        (
            benchmark_annualized_return,
            annualized_excess_return,
        ) = calculate_annualized_excess_return(
            strategy,
            benchmark,
            config.periods_per_year,
        )

        result[
            "benchmark_annualized_return"
        ] = benchmark_annualized_return
        result[
            "annualized_excess_return"
        ] = annualized_excess_return

    if trade_returns is not None:
        trades = clean_return_series(
            trade_returns,
            "trade_return",
        )

        result["win_rate"] = calculate_win_rate(
            trades
        )
        result[
            "profit_loss_ratio"
        ] = calculate_profit_loss_ratio(
            trades
        )

    return pd.Series(result, name="value")


def run_self_tests() -> None:
    """运行已知结果和不变量测试。"""
    sample_returns = pd.Series(
        [0.10, -0.20, 0.25]
    )

    sample_trades = pd.Series(
        [0.10, -0.05, 0.02, -0.01, 0.00]
    )

    report = evaluate_performance(
        strategy_returns=sample_returns,
        config=PerformanceConfig(
            periods_per_year=3
        ),
        benchmark_returns=sample_returns,
        trade_returns=sample_trades,
    )

    assert np.isclose(
        report["total_return"],
        0.10,
    )
    assert np.isclose(
        report["annualized_return"],
        0.10,
    )
    assert np.isclose(
        report["max_drawdown"],
        -0.20,
    )
    assert np.isclose(
        report["calmar_ratio"],
        0.50,
    )
    assert np.isclose(
        report["annualized_excess_return"],
        0.00,
    )
    assert np.isclose(
        report["win_rate"],
        0.40,
    )
    assert np.isclose(
        report["profit_loss_ratio"],
        2.00,
    )
    assert (
        -1.0
        < report["max_drawdown"]
        <= 0.0
    )


def main() -> None:
    dates = pd.date_range(
        "2025-01-31",
        periods=12,
        freq="ME",
    )

    strategy_returns = pd.Series(
        [
            0.020,
            -0.010,
            0.030,
            0.015,
            -0.025,
            0.040,
            0.010,
            -0.005,
            0.025,
            0.018,
            -0.012,
            0.030,
        ],
        index=dates,
    )

    benchmark_returns = pd.Series(
        [
            0.015,
            -0.008,
            0.020,
            0.012,
            -0.020,
            0.025,
            0.008,
            0.000,
            0.018,
            0.012,
            -0.010,
            0.020,
        ],
        index=dates,
    )

    trade_returns = pd.Series(
        [
            0.035,
            -0.018,
            0.022,
            0.011,
            -0.009,
            0.028,
            -0.015,
            0.006,
        ]
    )

    config = PerformanceConfig(
        periods_per_year=12,
        annual_risk_free_rate=0.02,
        ddof=1,
    )

    run_self_tests()

    report = evaluate_performance(
        strategy_returns=strategy_returns,
        config=config,
        benchmark_returns=benchmark_returns,
        trade_returns=trade_returns,
    )

    print("所有自动测试通过")
    print(report.round(6))


if __name__ == "__main__":
    main()
```

运行结果：

```text
所有自动测试通过
observations                   12.000000
total_return                    0.142318
annualized_return               0.142318
annualized_volatility           0.069492
sharpe_ratio                    1.671870
max_drawdown                   -0.025000
calmar_ratio                    5.692703
benchmark_annualized_return     0.094794
annualized_excess_return        0.047523
win_rate                        0.625000
profit_loss_ratio               1.457143
Name: value, dtype: float64
```

### 4.6 代码逻辑解释

1. `PerformanceConfig` 集中保存年化因子、年化无风险收益率和标准差自由度。
2. `clean_return_series()` 统一处理类型、缺失值、无穷值和非法收益。
3. 绝对绩效函数只使用策略周期收益。
4. 相对绩效函数先按索引对齐策略与基准，再在共同区间计算年化收益。
5. 交易级指标只使用已完成交易收益，不与周期级收益混合。
6. `evaluate_performance()` 负责组织所有指标，并统一返回一个 `pd.Series`。
7. `run_self_tests()` 使用人工可验证数据检查核心公式和不变量。
8. 主程序先运行测试，再对示例策略生成正式报告。

### 4.7 综合结果分析

#### 指标关系

- 年化收益为 \(14.2318\%\)，说明策略在这 12 个月内取得约 \(14.23\%\) 的累计与年化收益。
- 年化波动率约为 \(6.9492\%\)，与年化收益结合后得到夏普比率约 \(1.6719\)。
- 最大回撤为 \(-2.5\%\)，说明示例净值历史峰值到后续谷底的最大下降幅度较小。
- Calmar 约为 \(5.6927\)，来源于较高年化收益与较小最大回撤的组合。
- 基准年化收益约为 \(9.4794\%\)，策略年化超额收益约为 \(4.7523\%\)。
- 胜率为 \(62.5\%\)，表示 8 笔交易中有 5 笔盈利。
- 盈亏比约为 \(1.4571\)，表示平均盈利约为平均亏损幅度的 \(1.46\) 倍。

#### 综合结果

- 该示例同时表现出正收益、较低回撤、正超额收益和大于 1 的盈亏比。
- 夏普和 Calmar 都较高，但样本只有 12 个月，不能据此断言策略长期稳定。
- 胜率与盈亏比共同为正，但还没有计入交易成本、滑点和成交限制。
- 年化超额收益使用共同日期计算，避免了策略和基准样本错位。

#### 量化意义

统一模块的价值不只是少写几行代码，而是建立固定研究协议。未来每个策略都可以输出同样的字段，使用同样的数学口径，并接受同样的测试。这样才能进行可靠的横向比较、自动筛选和长期维护。

#### 案例限制

- 示例使用人工构造的月度收益，不代表真实市场表现。
- 只有 12 个周期，夏普、Calmar 和年化收益都可能不稳定。
- 未计算交易成本、滑点、冲击成本和税费。
- 未处理 A 股停牌、涨跌停和无法成交问题。
- 年化超额收益不等于信息比率，也不等于逐期主动收益的简单年化。
- 交易胜率没有区分持有期、仓位大小和单笔风险暴露。

---

## 五、常见错误

### 5.1 概念错误

#### 错误一：把高胜率等同于高收益

错误理解：

> 胜率超过 \(60\%\)，策略一定赚钱。

正确理解：

> 策略是否赚钱取决于胜率、平均盈利、平均亏损、仓位、交易成本和尾部损失的共同作用。

错误原因：只统计了盈利次数，没有统计每次盈利和亏损的幅度。

#### 错误二：把周期收益与交易收益混为一谈

错误理解：

> 每日收益大于 0 的天数占比就是交易胜率。

正确理解：

> 每日收益为周期级表现，交易胜率应由已经完成的独立交易结果计算。

错误原因：忽略了一个交易可能跨越多个交易日，也可能同一天包含多笔交易。

### 5.2 数学错误

#### 错误一：直接用负的最大回撤计算 Calmar

错误公式：

\[
Calmar
=
\frac{R_{\text{ann}}}{MDD}
\]

正确公式：

\[
Calmar
=
\frac{R_{\text{ann}}}{|MDD|}
\]

错误原因：本课程中的 \(MDD\) 是负数，风险幅度应使用绝对值。

#### 错误二：把年化无风险收益率直接从单期收益中相减

错误公式：

\[
Sharpe
=
\frac{\bar r-R_f}{s_r}\sqrt A
\]

正确公式：

\[
r_f
=
(1+R_f)^{1/A}-1
\]

\[
Sharpe
=
\frac{\bar r-r_f}{s_r}\sqrt A
\]

错误原因：\(\bar r\) 是单期平均收益，\(R_f\) 是年化收益，两者频率不一致。

#### 错误三：只用期末净值计算最大回撤

错误做法：

\[
MDD
=
\frac{V_T}{V_0}-1
\]

正确做法：

\[
H_t
=
\max_{0\le s\le t}V_s
\]

\[
D_t
=
\frac{V_t}{H_t}-1
\]

\[
MDD
=
\min_tD_t
\]

错误原因：最大回撤需要完整净值路径，不能只比较期初和期末。

### 5.3 Python 错误

#### 错误一：按位置相减策略与基准

错误代码：

```python
active_return = (
    strategy_returns.to_numpy()
    - benchmark_returns.to_numpy()
)
```

正确代码：

```python
aligned = pd.concat(
    [
        strategy_returns.rename(
            "strategy_return"
        ),
        benchmark_returns.rename(
            "benchmark_return"
        ),
    ],
    axis=1,
    join="inner",
).dropna()

active_return = (
    aligned["strategy_return"]
    - aligned["benchmark_return"]
)
```

错误原因：两个数组可能对应不同日期，按位置相减会产生静默错位。

#### 错误二：分母为零时返回无穷大

错误代码：

```python
calmar = annualized_return / abs(max_drawdown)
```

正确代码：

```python
if np.isclose(max_drawdown, 0.0):
    calmar = float("nan")
else:
    calmar = (
        annualized_return
        / abs(max_drawdown)
    )
```

错误原因：最大回撤为 0 时，Calmar 没有有限定义，返回无穷大会误导策略排序。

#### 错误三：遗漏期初净值

错误代码：

```python
wealth = (1.0 + returns).cumprod()
running_peak = wealth.cummax()
```

正确代码：

```python
wealth = np.concatenate(
    (
        [1.0],
        (1.0 + returns)
        .cumprod()
        .to_numpy(),
    )
)
running_peak = np.maximum.accumulate(
    wealth
)
```

错误原因：若第一期收益为负，遗漏期初净值会漏掉第一期回撤。

### 5.4 量化研究错误

#### 错误一：只报告最优指标

错误做法：策略筛选时只展示年化收益最高的结果，不展示回撤、波动和交易次数。

正确做法：固定输出完整指标向量，并同时保存样本区间、参数和策略版本。

#### 错误二：用不同区间比较策略

错误做法：策略 A 使用牛市区间，策略 B 使用震荡区间，却直接比较夏普和 Calmar。

正确做法：优先使用相同区间、相同频率、相同基准和相同成本假设进行比较。

#### 其他常见问题

- 把算术年化收益与几何年化收益混用。
- 把年化超额收益误认为信息比率。
- 对极短样本进行强烈年化。
- 忽略缺失值背后的停牌或数据质量问题。
- 在参数优化中反复选择最高夏普，造成过拟合。
- 只测试正常样例，不测试零波动和零回撤。
- 修改指标定义后没有同步更新历史报告与测试。
- 没有记录 `periods_per_year` 和 `ddof`，导致结果不可复现。

---

## 六、今日总结

### 6.1 今日新名词总结

- 绩效报告：把多个绩效指标组织为统一、可比较的策略体检结果。
- 指标协议：规定数据类型、频率、清洗方法、边界处理和输出字段。
- 不变量：用于检验指标实现是否始终符合数学定义的稳定性质。

### 6.2 核心概念总结

- 绩效指标向量同时覆盖收益、波动、回撤、相对表现和交易质量。
- 统一输入输出协议解决频率不一致、日期错位和边界定义不清的问题。
- 可验证绩效模块通过已知结果、边界条件和不变量测试降低静默计算错误。
- 周期级收益与交易级收益必须分开建模。
- 无法定义的比率应返回 `NaN`，而不是人为填入 0 或无穷大。
- 所有策略比较都应记录样本区间、年化因子、无风险利率、基准和交易成本口径。

### 6.3 本周知识关系

```text
年化收益
    ├── 描述长期复利增长速度
    ├── 与最大回撤组合得到 Calmar
    └── 与基准年化收益比较得到年化超额收益

年化波动率
    └── 与超额平均收益组合得到夏普比率

净值路径
    └── 生成回撤序列与最大回撤

交易收益
    ├── 生成胜率
    └── 生成盈亏比

统一协议
    └── 将全部指标组合为可复用绩效评价模块
```

### 6.4 今日完成标准

完成本日学习后，应检查：

- [x] 能写出统一绩效指标向量。
- [x] 能解释策略收益、基准收益和交易收益的区别。
- [x] 能根据频率设置年化因子。
- [x] 能把年化无风险收益率转换为单期收益率。
- [x] 能按日期对齐策略与基准。
- [x] 能正确处理零波动、零回撤和无亏损交易。
- [x] 能运行统一绩效评价代码。
- [x] 能使用已知样例验证最大回撤、Calmar、胜率和盈亏比。
- [x] 能说明单个指标不能完整评价一个策略。

### 6.5 一句话总结

> 一个可靠的绩效模块，不只是把公式写成函数，而是把数学口径、数据协议、边界处理和自动测试统一成可复现的研究基础设施。
