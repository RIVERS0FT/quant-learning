# 第九周 · 第一天

## 年化收益：累计收益、几何年化与净值口径

---

## 1. 今日学习目标

完成今天的学习后，你需要能够：

- 区分单期收益、累计收益和年化收益
- 理解为什么年化收益必须使用复利逻辑
- 从周期收益率序列计算累计收益
- 从累计收益推导几何年化收益
- 从净值序列计算年化收益
- 区分几何年化收益、算术年化近似和 CAGR
- 理解交易日年化与自然日年化的差异
- 正确选择日频、周频和月频数据的年化因子
- 识别缺失值、零净值、负净值和样本过短等边界问题
- 编写可复用的 Python 年化收益函数
- 使用已知样例和单元测试验证函数

---

## 2. 今日学习顺序

建议学习时间：约 120—150 分钟。

| 阶段 | 内容 | 建议时间 |
|---|---|---:|
| 1 | 回顾收益率与复利 | 20 分钟 |
| 2 | 累计收益 | 20 分钟 |
| 3 | 几何年化收益 | 30 分钟 |
| 4 | 不同年化口径比较 | 25 分钟 |
| 5 | Python 实现与测试 | 40 分钟 |
| 6 | 练习与复盘 | 15 分钟 |

---

# 一、为什么需要年化收益

## 3. 不同策略不能直接比较原始收益

假设有两个策略：

- 策略 A：3 个月累计收益为 \(8\%\)
- 策略 B：2 年累计收益为 \(30\%\)

只看累计收益，策略 B 更高。

但两个策略的运行时间不同，因此不能直接比较。

年化收益的作用是：

> 将不同长度投资区间的复合收益，换算成“假设以相同复利速度持续一年”时对应的收益率。

年化收益不是对未来收益的预测，也不表示策略每年都会取得同样收益。

它只是一个统一时间尺度后的历史绩效指标。

---

## 4. 年化收益回答的问题

年化收益回答：

> 如果这段历史区间中的复利增长速度持续一整年，对应的收益率是多少？

因此年化收益必须同时考虑：

1. 起始资产价值
2. 结束资产价值
3. 投资持续时间
4. 复利效应

---

# 二、单期收益与累计收益

## 5. 单期简单收益率

设第 \(t-1\) 期末资产价格或净值为 \(V_{t-1}\)，第 \(t\) 期末为 \(V_t\)。

单期简单收益率为：

\[
r_t
=
\frac{V_t-V_{t-1}}{V_{t-1}}
\]

等价地：

\[
r_t
=
\frac{V_t}{V_{t-1}}-1
\]

因此：

\[
V_t
=
V_{t-1}(1+r_t)
\]

其中 \(1+r_t\) 称为该期的增长因子。

---

## 6. 多期资产价值的逐期推导

第 1 期结束后：

\[
V_1
=
V_0(1+r_1)
\]

第 2 期结束后：

\[
V_2
=
V_1(1+r_2)
\]

将 \(V_1\) 代入：

\[
V_2
=
V_0(1+r_1)(1+r_2)
\]

第 3 期结束后：

\[
V_3
=
V_2(1+r_3)
\]

继续代入：

\[
V_3
=
V_0(1+r_1)(1+r_2)(1+r_3)
\]

推广到 \(N\) 期：

\[
V_N
=
V_0\prod_{t=1}^{N}(1+r_t)
\]

两边同时除以 \(V_0\)：

\[
\frac{V_N}{V_0}
=
\prod_{t=1}^{N}(1+r_t)
\]

因此多期累计收益为：

\[
R_{\text{cum}}
=
\frac{V_N}{V_0}-1
\]

代入增长因子后：

\[
R_{\text{cum}}
=
\prod_{t=1}^{N}(1+r_t)-1
\]

---

## 7. 为什么不能直接相加

假设两期收益分别为：

\[
r_1=10\%
\]

\[
r_2=-10\%
\]

直接相加得到：

\[
10\%-10\%=0
\]

但复利计算为：

\[
(1+10\%)(1-10\%)-1
\]

\[
=1.1\times0.9-1
\]

\[
=0.99-1
\]

\[
=-1\%
\]

原因是上涨和下跌对应的本金不同。

如果初始净值为 100：

\[
100\times1.1=110
\]

然后下跌 \(10\%\)：

\[
110\times0.9=99
\]

最终净值为 99，而不是 100。

---

# 三、几何年化收益

## 8. 年化因子

年化因子表示一年中包含多少个收益周期。

常用约定如下：

| 数据频率 | 常用年化因子 |
|---|---:|
| 日频交易数据 | 252 |
| 周频数据 | 52 |
| 月频数据 | 12 |
| 季度数据 | 4 |
| 年频数据 | 1 |

其中日频使用 252 是一种常见市场惯例，不是数学常数。

实际研究中应明确说明所使用的年化因子。

---

## 9. 几何年化收益公式

设：

- 共观察 \(N\) 个收益周期
- 每年包含 \(A\) 个同频周期
- 区间累计增长因子为 \(1+R_{\text{cum}}\)

假设每期的等价复合增长率为 \(g\)，则：

\[
(1+g)^N
=
1+R_{\text{cum}}
\]

两边同时取 \(N\) 次方根：

\[
1+g
=
(1+R_{\text{cum}})^{1/N}
\]

一年包含 \(A\) 个周期，因此一年后的增长因子为：

\[
(1+g)^A
\]

将 \(1+g\) 代入：

\[
(1+R_{\text{ann}})
=
\left((1+R_{\text{cum}})^{1/N}\right)^A
\]

根据幂的乘方法则：

\[
1+R_{\text{ann}}
=
(1+R_{\text{cum}})^{A/N}
\]

因此几何年化收益为：

\[
R_{\text{ann}}
=
(1+R_{\text{cum}})^{A/N}-1
\]

结合累计收益公式：

\[
1+R_{\text{cum}}
=
\prod_{t=1}^{N}(1+r_t)
\]

得到收益率序列口径：

\[
R_{\text{ann}}
=
\left(\prod_{t=1}^{N}(1+r_t)\right)^{A/N}-1
\]

---

## 10. 净值口径公式

因为：

\[
1+R_{\text{cum}}
=
\frac{V_N}{V_0}
\]

所以：

\[
R_{\text{ann}}
=
\left(\frac{V_N}{V_0}\right)^{A/N}-1
\]

该公式适用于：

- 策略净值序列
- 基金复权净值
- 不存在外部现金流的投资组合价值序列
- 已经正确处理申购、赎回和资金流的单位净值序列

若组合中途有外部资金流入或流出，直接使用账户总资产的首尾值可能产生错误。

---

## 11. 一个日频例子

某策略运行了 126 个交易日，累计收益为 \(10\%\)，使用年化因子 252。

\[
R_{\text{ann}}
=
(1+10\%)^{252/126}-1
\]

\[
=
1.1^2-1
\]

\[
=
1.21-1
\]

\[
=
21\%
\]

这里不是简单地将 \(10\%\) 乘以 2，而是将增长因子 \(1.1\) 平方。

在收益较小时，两者可能接近；收益较大或区间较长时，差异会更明显。

---

## 12. 一个亏损例子

某策略在 126 个交易日内累计亏损 \(10\%\)。

\[
R_{\text{ann}}
=
(1-10\%)^{252/126}-1
\]

\[
=
0.9^2-1
\]

\[
=
0.81-1
\]

\[
=-19\%
\]

不能将 \(-10\%\) 简单乘以 2 得到 \(-20\%\)。

几何年化反映的是复合增长速度。

---

# 四、CAGR 与几何年化收益

## 13. CAGR 的定义

CAGR 是 Compound Annual Growth Rate，即复合年增长率。

设投资持续 \(Y\) 年，则：

\[
CAGR
=
\left(\frac{V_T}{V_0}\right)^{1/Y}-1
\]

如果使用 \(N\) 个日频收益且一年按 252 个交易日计算，则：

\[
Y
=
\frac{N}{252}
\]

代入后：

\[
CAGR
=
\left(\frac{V_T}{V_0}\right)^{252/N}-1
\]

因此在相同时间口径下，CAGR 与几何年化收益是同一个核心概念。

区别通常只在表达方式：

- CAGR 常用于首尾价值和年数
- 几何年化收益常用于收益率序列和年化因子

---

# 五、算术年化近似

## 14. 算术年化公式

日均收益的算术年化通常写为：

\[
R_{\text{ann,arith}}
=
A\bar r
\]

其中：

\[
\bar r
=
\frac{1}{N}\sum_{t=1}^{N}r_t
\]

日频时经常写成：

\[
R_{\text{ann,arith}}
=
252\bar r
\]

但这不是实际复合年化收益。

它忽略了收益波动和复利路径。

---

## 15. 几何年化与算术年化的差异

几何年化：

\[
R_{\text{ann,geo}}
=
\left(\prod_{t=1}^{N}(1+r_t)\right)^{A/N}-1
\]

算术年化：

\[
R_{\text{ann,arith}}
=
A\bar r
\]

一般来说，在收益存在波动时，算术平均收益会高于几何平均收益。

直观原因是波动会损害复利增长。

例如两期收益为 \(20\%\) 和 \(-20\%\)。

算术平均为：

\[
\frac{20\%+(-20\%)}{2}=0
\]

累计收益为：

\[
1.2\times0.8-1
\]

\[
=0.96-1
\]

\[
=-4\%
\]

虽然平均单期收益为 0，但资产仍然亏损 \(4\%\)。

因此，在评价策略已经实现的复合增长时，应优先使用几何年化收益。

---

## 16. 算术年化什么时候有用

算术均值不是无用的。

它常用于：

- 估计单期收益的期望值
- 夏普比率中的平均周期超额收益
- 统计推断和收益分布研究
- 短周期、小收益条件下的近似计算

但在回答“策略净值每年以多快速度复合增长”时，应使用几何年化收益。

---

# 六、对数收益率口径

## 17. 对数收益率

单期对数收益率为：

\[
\ell_t
=
\ln(1+r_t)
\]

对数收益具有可加性：

\[
\sum_{t=1}^{N}\ell_t
=
\ln\left(\prod_{t=1}^{N}(1+r_t)\right)
\]

平均每期对数收益为：

\[
\bar\ell
=
\frac{1}{N}\sum_{t=1}^{N}\ell_t
\]

年化对数收益为：

\[
\ell_{\text{ann}}
=
A\bar\ell
\]

将其转换为简单年化收益：

\[
R_{\text{ann}}
=
e^{A\bar\ell}-1
\]

逐步代入：

\[
e^{A\bar\ell}-1
=
e^{\frac{A}{N}\sum_{t=1}^{N}\ln(1+r_t)}-1
\]

\[
=
\left(e^{\sum_{t=1}^{N}\ln(1+r_t)}\right)^{A/N}-1
\]

\[
=
\left(\prod_{t=1}^{N}(1+r_t)\right)^{A/N}-1
\]

因此，对数收益率方法与几何年化方法完全一致。

---

# 七、交易日年化与自然日年化

## 18. 交易日口径

当输入是连续的日频交易收益率时，常用：

\[
R_{\text{ann}}
=
\left(\frac{V_N}{V_0}\right)^{252/N}-1
\]

这里 \(N\) 是有效收益率观测数量。

这种方法适合：

- 股票或策略日收益序列
- 研究框架统一采用 252 个交易日
- 不特别关心真实日历跨度

---

## 19. 自然日口径

若已知真实起止日期，可以按自然日计算：

设起止日期相隔 \(D\) 天，则：

\[
R_{\text{ann,calendar}}
=
\left(\frac{V_T}{V_0}\right)^{365.2425/D}-1
\]

也可以使用 365，关键是保持研究口径一致并明确说明。

自然日口径更适合：

- 基金或账户跨多年持有期
- 样本起止日不是规则交易周期
- 需要精确反映真实持有时间

---

## 20. 两种口径不能混用

错误示例：

- 分子使用 100 个有效交易日的收益
- 指数却使用真实自然日天数的一部分
- 或者收益序列缺失很多交易日，却仍把观测数当作完整交易日数

正确做法是二选一：

1. 使用收益观测数和交易日年化因子
2. 使用真实起止日期和自然日年化因子

并在报告中写明口径。

---

# 八、数据清洗与边界条件

## 21. 缺失值

收益率序列中的缺失值可能来自：

- 第一行计算收益时自然产生
- 停牌
- 数据缺失
- 股票尚未上市
- 不同资产交易日不一致

不能不加说明地把所有缺失值都填为 0。

对于单策略净值序列，通常可以：

- 删除开头因 `pct_change()` 产生的第一个缺失值
- 检查中间缺失值的原因
- 只有明确表示“该日净值不变”时才填 0

---

## 22. 收益率不能小于 \(-100\%\)

简单收益率必须满足：

\[
r_t\ge -1
\]

若：

\[
r_t<-1
\]

则增长因子：

\[
1+r_t<0
\]

这意味着资产价值变成负数，通常说明：

- 数据错误
- 单位错误
- 价格口径错误
- 该序列并不是普通资产简单收益率

若某期收益恰好为 \(-100\%\)，则组合净值归零，累计收益为 \(-100\%\)。

在没有追加资金的情况下，之后无法通过普通收益率恢复为正值。

---

## 23. 净值必须为正

几何年化公式包含：

\[
\left(\frac{V_T}{V_0}\right)^{A/N}
\]

通常要求：

\[
V_0>0
\]

并且：

\[
V_T>0
\]

若净值为 0，则年化结果为 \(-100\%\)，但需要明确策略已经完全损失。

若净值为负，普通 CAGR 不再具有标准金融含义。

---

## 24. 样本过短

假设策略只运行 5 个交易日并上涨 \(3\%\)。

年化后为：

\[
1.03^{252/5}-1
\]

该数值会非常高。

数学计算没有错，但经济解释很弱。

短样本年化会将很短时间内的偶然波动放大。

因此报告中应同时提供：

- 样本起止日期
- 观测数量
- 累计收益
- 年化收益

不能只展示年化收益。

---

## 25. 外部现金流

假设账户初始资产为 10 万元，半年后追加 10 万元，一年末账户总资产为 21 万元。

直接使用首尾值会得到：

\[
\frac{21}{10}-1=110\%
\]

但其中大部分增长来自追加资金，不是投资收益。

因此有外部现金流时，应使用：

- 单位净值
- 时间加权收益率
- 或根据现金流时间计算资金加权收益率

今天的年化函数默认输入已经是不受外部资金流污染的收益率或单位净值。

---

# 九、Python 实现

## 26. 从收益率序列计算累计收益

```python
from __future__ import annotations

import numpy as np
import pandas as pd


def cumulative_return(returns: pd.Series) -> float:
    """根据简单收益率序列计算累计收益。"""
    clean = pd.Series(returns, dtype="float64").dropna()

    if clean.empty:
        raise ValueError("收益率序列不能为空")

    if (clean < -1).any():
        raise ValueError("简单收益率不能小于 -100%")

    return float((1.0 + clean).prod() - 1.0)
```

核心代码：

```python
(1.0 + clean).prod() - 1.0
```

对应数学公式：

\[
R_{\text{cum}}
=
\prod_{t=1}^{N}(1+r_t)-1
\]

---

## 27. 从收益率序列计算几何年化收益

```python
def annualized_return(
    returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """根据简单收益率序列计算几何年化收益。"""
    clean = pd.Series(returns, dtype="float64").dropna()

    if clean.empty:
        raise ValueError("收益率序列不能为空")

    if periods_per_year <= 0:
        raise ValueError("periods_per_year 必须为正数")

    if (clean < -1).any():
        raise ValueError("简单收益率不能小于 -100%")

    growth = float((1.0 + clean).prod())
    n_periods = clean.size

    if growth == 0.0:
        return -1.0

    return growth ** (periods_per_year / n_periods) - 1.0
```

计算步骤为：

1. 删除缺失值
2. 检查收益率是否合法
3. 计算累计增长因子
4. 统计有效观测数量
5. 使用几何年化公式

---

## 28. 从净值序列计算年化收益

```python
def annualized_return_from_nav(
    nav: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """根据等频净值序列计算年化收益。"""
    clean = pd.Series(nav, dtype="float64").dropna()

    if clean.size < 2:
        raise ValueError("净值序列至少需要两个有效观测")

    if periods_per_year <= 0:
        raise ValueError("periods_per_year 必须为正数")

    if (clean <= 0).any():
        raise ValueError("净值必须全部为正")

    start_value = float(clean.iloc[0])
    end_value = float(clean.iloc[-1])

    # M 个净值点之间只有 M - 1 个收益区间
    n_periods = clean.size - 1

    return (end_value / start_value) ** (
        periods_per_year / n_periods
    ) - 1.0
```

注意：

若净值序列包含 \(M\) 个观测点，则收益区间数为：

\[
N=M-1
\]

这是常见的一个 off-by-one 错误来源。

---

## 29. 按真实日期计算 CAGR

```python
def cagr_from_dated_nav(nav: pd.Series) -> float:
    """根据带 DatetimeIndex 的净值序列和真实日历跨度计算 CAGR。"""
    clean = pd.Series(nav, dtype="float64").dropna().sort_index()

    if clean.size < 2:
        raise ValueError("净值序列至少需要两个有效观测")

    if not isinstance(clean.index, pd.DatetimeIndex):
        raise TypeError("索引必须是 DatetimeIndex")

    if (clean <= 0).any():
        raise ValueError("净值必须全部为正")

    start_date = clean.index[0]
    end_date = clean.index[-1]
    elapsed_days = (end_date - start_date).days

    if elapsed_days <= 0:
        raise ValueError("起止日期必须至少相差一天")

    years = elapsed_days / 365.2425
    growth = float(clean.iloc[-1] / clean.iloc[0])

    return growth ** (1.0 / years) - 1.0
```

---

## 30. 示例数据

```python
returns = pd.Series(
    [0.01, -0.005, 0.012, 0.003, -0.004],
    name="strategy_return",
)

cum_ret = cumulative_return(returns)
ann_ret = annualized_return(returns, periods_per_year=252)

print(f"累计收益: {cum_ret:.4%}")
print(f"年化收益: {ann_ret:.4%}")
```

由于样本只有 5 个交易日，年化收益可能非常大。

这恰好说明：

> 年化公式可以统一时间尺度，但不能替代对样本长度和稳定性的判断。

---

# 十、函数验证

## 31. 已知结果测试：半年上涨 10%

126 个交易日累计上涨 \(10\%\)，按 252 个交易日年化，结果应为 \(21\%\)。

```python
import math


def test_half_year_growth() -> None:
    returns = pd.Series([0.10])

    result = annualized_return(
        returns,
        periods_per_year=2,
    )

    assert math.isclose(result, 0.21, rel_tol=1e-12)
```

这里将一个观测周期理解为半年，因此一年包含 2 个周期。

---

## 32. 零收益测试

```python
def test_zero_return() -> None:
    returns = pd.Series([0.0] * 252)

    result = annualized_return(returns)

    assert math.isclose(result, 0.0, abs_tol=1e-12)
```

---

## 33. 完全损失测试

```python
def test_total_loss() -> None:
    returns = pd.Series([0.01, -1.0, 0.50])

    result = annualized_return(returns)

    assert result == -1.0
```

一旦增长因子变为 0，普通复利净值已经归零。

---

## 34. 收益率与净值口径一致性测试

```python
def test_returns_and_nav_are_consistent() -> None:
    returns = pd.Series([0.01, -0.02, 0.03, 0.005])
    nav = pd.concat(
        [
            pd.Series([1.0]),
            (1.0 + returns).cumprod(),
        ],
        ignore_index=True,
    )

    from_returns = annualized_return(
        returns,
        periods_per_year=252,
    )
    from_nav = annualized_return_from_nav(
        nav,
        periods_per_year=252,
    )

    assert math.isclose(
        from_returns,
        from_nav,
        rel_tol=1e-12,
    )
```

该测试可以发现：

- 净值点数量与收益区间数量混淆
- 累计收益计算错误
- 年化指数使用错误

---

## 35. 非法输入测试

```python
import pytest


def test_return_below_minus_one_raises() -> None:
    returns = pd.Series([0.01, -1.20])

    with pytest.raises(ValueError):
        annualized_return(returns)


def test_empty_returns_raises() -> None:
    returns = pd.Series(dtype="float64")

    with pytest.raises(ValueError):
        annualized_return(returns)


def test_non_positive_nav_raises() -> None:
    nav = pd.Series([1.0, 0.9, 0.0])

    with pytest.raises(ValueError):
        annualized_return_from_nav(nav)
```

---

# 十一、统一输出建议

## 36. 不要只返回一个数字

绩效评价函数至少应同时返回：

- 有效观测数量
- 年化因子
- 累计收益
- 年化收益
- 起始净值
- 结束净值
- 样本起止日期

示例：

```python
def annualized_return_report(
    returns: pd.Series,
    periods_per_year: int = 252,
) -> dict[str, float | int]:
    clean = pd.Series(returns, dtype="float64").dropna()

    cum_ret = cumulative_return(clean)
    ann_ret = annualized_return(clean, periods_per_year)

    return {
        "observations": int(clean.size),
        "periods_per_year": int(periods_per_year),
        "cumulative_return": cum_ret,
        "annualized_return": ann_ret,
    }
```

这样可以避免脱离样本长度解释年化收益。

---

# 十二、常见错误

## 37. 错误一：累计收益直接除以年数

错误写法：

\[
R_{\text{ann}}
=
\frac{R_{\text{cum}}}{Y}
\]

该方法忽略复利。

正确写法：

\[
R_{\text{ann}}
=
(1+R_{\text{cum}})^{1/Y}-1
\]

---

## 38. 错误二：日均收益直接乘 252 并称为实际年化收益

\[
252\bar r
\]

是算术年化近似，不是净值的实际复合年化收益。

策略绩效报告应明确指标口径。

---

## 39. 错误三：净值点数当作收益期数

若净值有 253 个日度观测点，则区间数为：

\[
253-1=252
\]

不是 253。

---

## 40. 错误四：忽略外部资金流

账户总资产增加，不一定表示投资盈利。

必须区分：

- 投资收益
- 入金
- 出金
- 分红再投资
- 费用

---

## 41. 错误五：短样本过度年化

5 天、10 天或 20 天的高收益被年化后可能十分夸张。

应把年化收益与累计收益、样本长度一起报告。

---

## 42. 错误六：随意填充缺失收益为 0

缺失不一定等于零收益。

填充前必须确认该缺失值是否代表：

- 停牌且净值确实不变
- 数据尚未获取
- 资产不存在
- 对齐后无观测

---

# 十三、今日练习

## 43. 基础练习

给定三期收益：

\[
5\%,\quad -2\%,\quad 3\%
\]

计算：

1. 累计增长因子
2. 累计收益
3. 若一年有 12 个同类周期，计算年化收益

参考计算路径：

\[
G
=
1.05\times0.98\times1.03
\]

\[
R_{\text{cum}}
=
G-1
\]

\[
R_{\text{ann}}
=
G^{12/3}-1
\]

---

## 44. 对比练习

构造下面两条收益路径：

- 路径 A：每期收益均为 \(1\%\)
- 路径 B：收益在 \(11\%\) 和 \(-9\%\) 之间交替

比较：

- 算术平均收益
- 累计收益
- 几何年化收益

观察波动如何影响复利增长。

---

## 45. 编程练习

完成以下任务：

1. 为 `annualized_return()` 增加类型注解
2. 检查输入是否包含正无穷或负无穷
3. 增加 `frequency` 参数，支持 `daily`、`weekly`、`monthly`
4. 使用映射表自动选择 252、52 或 12
5. 编写至少 5 个单元测试
6. 比较收益率序列口径与净值口径结果是否一致

频率映射示例：

```python
PERIODS_PER_YEAR = {
    "daily": 252,
    "weekly": 52,
    "monthly": 12,
}
```

---

# 十四、今日输出

## 46. 必须完成的文件

建议在练习代码目录中完成：

```text
performance_metrics.py
```

至少包含：

```python
cumulative_return()
annualized_return()
annualized_return_from_nav()
cagr_from_dated_nav()
```

并创建：

```text
test_performance_metrics.py
```

至少覆盖：

- 正收益
- 负收益
- 零收益
- 完全损失
- 缺失值
- 非法收益率
- 净值与收益率口径一致性

---

# 十五、今日检查

## 47. 概念检查

- [ ] 我能解释累计收益为什么不能直接相加
- [ ] 我能从复利公式推导几何年化收益
- [ ] 我能区分累计收益与年化收益
- [ ] 我能区分几何年化与算术年化
- [ ] 我知道 CAGR 与几何年化的关系
- [ ] 我知道 252 是研究约定而不是数学常数
- [ ] 我能解释交易日年化与自然日年化的差异
- [ ] 我知道短样本年化为什么可能误导
- [ ] 我知道有外部现金流时不能直接使用账户首尾资产

## 48. 编程检查

- [ ] 函数会删除并检查缺失值
- [ ] 函数拒绝小于 \(-100\%\) 的简单收益率
- [ ] 函数检查年化因子为正数
- [ ] 净值函数正确使用 \(M-1\) 个收益区间
- [ ] 收益率口径与净值口径结果一致
- [ ] 已知样例测试通过
- [ ] 函数输出中包含观测数量与年化因子

---

# 十六、今日总结

今天最重要的公式是：

累计收益：

\[
R_{\text{cum}}
=
\prod_{t=1}^{N}(1+r_t)-1
\]

几何年化收益：

\[
R_{\text{ann}}
=
\left(\prod_{t=1}^{N}(1+r_t)\right)^{A/N}-1
\]

净值口径：

\[
R_{\text{ann}}
=
\left(\frac{V_N}{V_0}\right)^{A/N}-1
\]

真实年份口径：

\[
CAGR
=
\left(\frac{V_T}{V_0}\right)^{1/Y}-1
\]

需要牢牢记住：

> 年化收益是历史复合增长速度的标准化表达，不是未来收益预测。

> 策略评价中必须同时报告累计收益、年化收益和样本长度。

下一天将学习年化波动率，重点理解标准差、样本标准差、平方根时间法则以及年化因子的使用条件。
