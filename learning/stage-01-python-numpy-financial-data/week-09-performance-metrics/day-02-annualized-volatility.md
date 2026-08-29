# 第九周 · 第二天

## 年化波动率：标准差、时间缩放与风险口径

---

## 1. 今日学习目标

完成今天的学习后，你需要能够：

- 理解波动率衡量的是什么
- 区分收益率波动与价格波动
- 理解方差和标准差的含义
- 区分总体标准差与样本标准差
- 理解 pandas 中 `ddof=1` 的作用
- 从日频、周频和月频收益计算年化波动率
- 逐步推导平方根时间法则
- 说明为什么日波动率使用 \(\sqrt{252}\) 年化
- 理解平方根时间法则成立所需的假设
- 识别自相关、波动聚集和不规则时间间隔带来的问题
- 从净值序列生成收益率后计算波动率
- 编写可复用的年化波动率函数
- 编写滚动年化波动率函数
- 使用已知样例和单元测试验证函数

---

## 2. 今日学习顺序

建议学习时间：约 120—150 分钟。

| 阶段 | 内容 | 建议时间 |
|---|---|---:|
| 1 | 理解波动率 | 20 分钟 |
| 2 | 方差与标准差 | 25 分钟 |
| 3 | 年化公式推导 | 30 分钟 |
| 4 | 口径与适用条件 | 25 分钟 |
| 5 | Python 实现与测试 | 40 分钟 |
| 6 | 练习与复盘 | 15 分钟 |

---

# 一、波动率衡量什么

## 3. 波动率是收益率的离散程度

假设两个策略在同一段时间内都取得了 \(10\%\) 的累计收益。

策略 A 的每日收益较平稳：

```text
0.10%, 0.12%, 0.08%, 0.11%, 0.09%
```

策略 B 的每日收益大幅波动：

```text
3.00%, -2.80%, 2.50%, -2.40%, 0.20%
```

两个策略的最终收益可能接近，但持有过程完全不同。

波动率用于描述：

> 收益率围绕其平均值上下波动的程度。

波动越大，说明收益结果越不稳定。

波动越小，说明收益序列相对平稳。

---

## 4. 波动率通常使用收益率计算

策略绩效分析中，不应直接对价格或净值计算标准差。

原因是价格水平本身通常具有趋势，而且不同资产的价格单位不同。

例如：

- 股票 A 的价格约为 10 元
- 股票 B 的价格约为 100 元

即使两只股票的相对波动完全相同，价格标准差也可能相差约 10 倍。

因此，应先计算收益率：

\[
r_t
=
\frac{P_t-P_{t-1}}{P_{t-1}}
\]

再对收益率序列计算标准差。

---

## 5. 波动率的单位

若输入的是日收益率，则标准差是日波动率。

若输入的是周收益率，则标准差是周波动率。

若输入的是月收益率，则标准差是月波动率。

例如，日波动率为：

\[
\sigma_{\text{daily}}=1.2\%
\]

它表示日收益率相对于日均收益的典型偏离程度约为 \(1.2\%\)。

注意：标准差不是最大涨跌幅，也不是每天必然发生的涨跌幅。

---

## 6. 波动率不是亏损概率

波动率同时统计正向和负向波动。

若收益率大幅上涨，波动率也会增加。

若收益率大幅下跌，波动率同样会增加。

因此：

- 波动率高不等于一定亏损
- 波动率低不等于一定安全
- 波动率不区分上涨波动和下跌波动
- 波动率不能单独描述尾部风险

波动率是风险的重要代理指标，但不是风险的完整定义。

---

# 二、均值、方差与标准差

## 7. 收益率均值

给定 \(N\) 个周期收益率：

\[
r_1,r_2,\ldots,r_N
\]

样本均值为：

\[
\bar r
=
\frac{1}{N}
\sum_{t=1}^{N}r_t
\]

均值代表样本期间的平均单期收益。

---

## 8. 每个收益率与均值的偏差

第 \(t\) 期收益率与均值的偏差为：

\[
d_t
=
r_t-\bar r
\]

若收益率高于均值，则偏差为正。

若收益率低于均值，则偏差为负。

所有偏差直接相加会得到：

\[
\sum_{t=1}^{N}(r_t-\bar r)=0
\]

因此，不能直接使用偏差平均值衡量波动。

---

## 9. 为什么对偏差平方

为了避免正负偏差互相抵消，可以对偏差平方：

\[
(r_t-\bar r)^2
\]

平方具有两个作用：

1. 将负偏差变为正数
2. 对较大的偏差给予更高权重

大幅偏离均值的收益会显著提高方差和波动率。

---

## 10. 总体方差

若当前数据包含我们关心的完整总体，则总体方差为：

\[
\sigma^2
=
\frac{1}{N}
\sum_{t=1}^{N}(r_t-\mu)^2
\]

其中：

- \(\mu\) 是总体均值
- \(\sigma^2\) 是总体方差
- \(\sigma\) 是总体标准差

总体标准差为：

\[
\sigma
=
\sqrt{\sigma^2}
\]

---

## 11. 样本方差

在量化研究中，历史收益通常被视为未来收益分布的一组样本。

样本方差通常使用：

\[
s^2
=
\frac{1}{N-1}
\sum_{t=1}^{N}(r_t-\bar r)^2
\]

样本标准差为：

\[
s
=
\sqrt{s^2}
\]

分母使用 \(N-1\)，而不是 \(N\)。

这称为贝塞尔校正。

---

## 12. 为什么样本方差除以 \(N-1\)

计算样本均值后，偏差受到约束：

\[
\sum_{t=1}^{N}(r_t-\bar r)=0
\]

若前 \(N-1\) 个偏差已知，最后一个偏差就被唯一确定。

因此，只有 \(N-1\) 个偏差可以自由变化。

样本方差的自由度为：

\[
N-1
\]

使用 \(N-1\) 可以修正用样本均值代替总体均值造成的低估。

---

## 13. `ddof` 的含义

在 NumPy 和 pandas 中，标准差的分母通常写为：

\[
N-\text{ddof}
\]

当：

```python
ddof=0
```

分母为：

\[
N
\]

对应总体标准差。

当：

```python
ddof=1
```

分母为：

\[
N-1
\]

对应样本标准差。

`pandas.Series.std()` 默认使用 `ddof=1`。

`numpy.std()` 默认使用 `ddof=0`。

这两个默认值不同，是常见结果差异来源。

---

## 14. 手工计算示例

假设四个日收益率为：

\[
1\%,-1\%,2\%,0\%
\]

先计算均值：

\[
\bar r
=
\frac{1\%-1\%+2\%+0\%}{4}
\]

\[
\bar r
=
\frac{2\%}{4}
\]

\[
\bar r
=
0.5\%
\]

四个偏差依次为：

\[
1\%-0.5\%=0.5\%
\]

\[
-1\%-0.5\%=-1.5\%
\]

\[
2\%-0.5\%=1.5\%
\]

\[
0\%-0.5\%=-0.5\%
\]

将收益率写成小数后，偏差平方和为：

\[
0.005^2+(-0.015)^2+0.015^2+(-0.005)^2
\]

\[
=0.000025+0.000225+0.000225+0.000025
\]

\[
=0.0005
\]

样本方差为：

\[
s^2
=
\frac{0.0005}{4-1}
\]

\[
s^2
=
0.0001666667
\]

样本标准差为：

\[
s
=
\sqrt{0.0001666667}
\]

\[
s
\approx
0.0129099
\]

转换为百分比：

\[
s
\approx
1.2910\%
\]

若使用总体标准差，则：

\[
\sigma^2
=
\frac{0.0005}{4}
\]

\[
\sigma^2
=
0.000125
\]

\[
\sigma
=
\sqrt{0.000125}
\]

\[
\sigma
\approx
1.1180\%
\]

样本较短时，`ddof` 的选择会带来明显差异。

---

# 三、年化波动率

## 15. 为什么需要年化

日波动率、周波动率和月波动率不能直接比较。

例如：

- 日波动率为 \(1\%\)
- 周波动率为 \(2.3\%\)

不能仅根据数值大小判断哪个风险更高，因为时间单位不同。

年化波动率的作用是：

> 将不同频率的单期波动率换算到统一的一年尺度。

---

## 16. 年化因子

常用年化因子如下：

| 数据频率 | 常用年化因子 |
|---|---:|
| 日频交易收益 | 252 |
| 周频收益 | 52 |
| 月频收益 | 12 |
| 季度收益 | 4 |
| 年频收益 | 1 |

年化因子是研究约定，不是固定数学常数。

A 股日频研究通常使用 252 个交易日。

研究报告必须明确写出所使用的年化因子。

---

## 17. 从多期收益近似开始推导

设未来一年包含 \(A\) 个收益周期。

每个周期收益为：

\[
r_1,r_2,\ldots,r_A
\]

简单收益的精确复利累计收益为：

\[
R
=
\prod_{t=1}^{A}(1+r_t)-1
\]

当单期收益较小时，可以使用近似：

\[
R
\approx
\sum_{t=1}^{A}r_t
\]

因此，可以先研究收益率之和的方差。

---

## 18. 多期收益方差的一般形式

收益率之和为：

\[
S_A
=
\sum_{t=1}^{A}r_t
\]

其方差为：

\[
\operatorname{Var}(S_A)
=
\operatorname{Var}
\left(
\sum_{t=1}^{A}r_t
\right)
\]

展开后：

\[
\operatorname{Var}(S_A)
=
\sum_{t=1}^{A}\operatorname{Var}(r_t)
+
2\sum_{i<j}\operatorname{Cov}(r_i,r_j)
\]

这说明多期方差不仅取决于每一期的方差，还取决于不同时期之间的协方差。

---

## 19. 独立同分布假设

若假设每期收益：

1. 方差相同
2. 彼此不相关

则每期方差为：

\[
\operatorname{Var}(r_t)=\sigma^2
\]

并且：

\[
\operatorname{Cov}(r_i,r_j)=0
\]

因此：

\[
\operatorname{Var}(S_A)
=
\sum_{t=1}^{A}\sigma^2
\]

\[
\operatorname{Var}(S_A)
=
A\sigma^2
\]

标准差是方差的平方根：

\[
\operatorname{Std}(S_A)
=
\sqrt{A\sigma^2}
\]

由于 \(\sigma\ge 0\)，所以：

\[
\operatorname{Std}(S_A)
=
\sqrt{A}\sigma
\]

这就是平方根时间法则。

---

## 20. 年化波动率公式

设单期收益率标准差为：

\[
\sigma_{\text{period}}
\]

一年包含 \(A\) 个同频周期。

则年化波动率为：

\[
\sigma_{\text{annual}}
=
\sigma_{\text{period}}\sqrt{A}
\]

日频收益使用 252 年化时：

\[
\sigma_{\text{annual}}
=
\sigma_{\text{daily}}\sqrt{252}
\]

周频收益使用 52 年化时：

\[
\sigma_{\text{annual}}
=
\sigma_{\text{weekly}}\sqrt{52}
\]

月频收益使用 12 年化时：

\[
\sigma_{\text{annual}}
=
\sigma_{\text{monthly}}\sqrt{12}
\]

---

## 21. 为什么不是乘以 252

方差随时间长度近似线性增长：

\[
\sigma^2_{\text{annual}}
=
252\sigma^2_{\text{daily}}
\]

波动率是标准差，不是方差。

因此两边开平方：

\[
\sigma_{\text{annual}}
=
\sqrt{252\sigma^2_{\text{daily}}}
\]

\[
\sigma_{\text{annual}}
=
\sqrt{252}\sigma_{\text{daily}}
\]

所以日波动率应乘以 \(\sqrt{252}\)，而不是乘以 252。

---

## 22. 日频示例

假设某策略的日收益率样本标准差为：

\[
\sigma_{\text{daily}}=1.2\%
\]

使用 252 个交易日年化：

\[
\sigma_{\text{annual}}
=
1.2\%\times\sqrt{252}
\]

因为：

\[
\sqrt{252}
\approx
15.8745
\]

所以：

\[
\sigma_{\text{annual}}
\approx
1.2\%\times15.8745
\]

\[
\sigma_{\text{annual}}
\approx
19.0494\%
\]

即年化波动率约为：

\[
19.05\%
\]

---

## 23. 月频示例

假设某策略的月收益率标准差为：

\[
\sigma_{\text{monthly}}=4\%
\]

使用 12 个月年化：

\[
\sigma_{\text{annual}}
=
4\%\times\sqrt{12}
\]

\[
\sqrt{12}
\approx
3.4641
\]

因此：

\[
\sigma_{\text{annual}}
\approx
4\%\times3.4641
\]

\[
\sigma_{\text{annual}}
\approx
13.8564\%
\]

即年化波动率约为：

\[
13.86\%
\]

---

# 四、平方根时间法则的适用条件

## 24. 收益间隔必须一致

如果输入包含：

- 一部分日收益
- 一部分周收益
- 不规则日期间隔收益

则不能直接对整列计算标准差后乘以 \(\sqrt{252}\)。

年化前必须保证每个收益观测对应相同时间长度。

---

## 25. 收益分布应相对稳定

平方根时间法则隐含每期方差大致稳定。

如果市场从低波动状态切换到高波动状态，则全样本标准差只是多个状态的混合结果。

金融市场常见波动聚集：

- 高波动之后仍容易高波动
- 低波动之后仍容易低波动

因此，历史年化波动率不应被理解为未来固定风险。

---

## 26. 自相关会破坏简单缩放

若收益存在自相关，则协方差项不再为零。

一般形式为：

\[
\operatorname{Var}(S_A)
=
A\sigma^2
+
2\sum_{k=1}^{A-1}(A-k)\gamma_k
\]

其中：

\[
\gamma_k
=
\operatorname{Cov}(r_t,r_{t-k})
\]

若 \(\gamma_k>0\)，简单平方根年化可能低估长期波动。

若 \(\gamma_k<0\)，简单平方根年化可能高估长期波动。

对多数基础日频绩效报告，可以先使用标准平方根时间法则，但必须理解其假设。

---

## 27. 波动率年化是统计缩放，不是精确复利

年化收益使用复利增长公式。

年化波动率使用标准差的时间缩放。

两者逻辑不同：

- 年化收益关注增长因子
- 年化波动率关注方差如何随时间累积

不能将年化收益公式用于波动率。

也不能将波动率直接乘以年化周期数。

---

## 28. 年化波动率不是预测保证

假设过去一年年化波动率为 \(20\%\)，并不表示下一年收益一定落在某个固定区间。

年化波动率是基于历史样本和统计假设得到的风险描述。

它可能受到以下因素影响：

- 样本区间选择
- 市场状态变化
- 极端行情
- 停牌和涨跌停
- 数据清洗方式
- 复权方式
- 收益频率

---

# 五、收益率口径

## 29. 简单收益率

简单收益率为：

\[
r_t
=
\frac{P_t}{P_{t-1}}-1
\]

它易于解释，也是策略净值分析中最常用的收益率形式。

---

## 30. 对数收益率

对数收益率为：

\[
g_t
=
\ln\left(\frac{P_t}{P_{t-1}}\right)
\]

根据简单收益率定义：

\[
\frac{P_t}{P_{t-1}}
=
1+r_t
\]

所以：

\[
g_t
=
\ln(1+r_t)
\]

当收益率较小时：

\[
\ln(1+r_t)
\approx
r_t
\]

因此，低频小幅收益下，简单收益率波动率与对数收益率波动率通常接近。

但研究中必须统一口径，不能在同一绩效表中混用而不说明。

---

## 31. 从净值计算收益率

给定净值序列：

\[
V_0,V_1,\ldots,V_N
\]

简单收益率为：

\[
r_t
=
\frac{V_t}{V_{t-1}}-1
\]

在 pandas 中可使用：

```python
returns = nav.pct_change()
```

第一行没有前一期净值，因此会得到缺失值。

计算波动率前应删除该缺失值。

---

## 32. A 股价格应使用正确复权口径

直接使用未复权收盘价计算收益，可能将分红、送股和拆股误识别为价格暴跌。

研究普通持有收益时，应根据研究目的选择：

- 前复权价格
- 后复权价格
- 总回报口径

绩效计算前必须确认价格序列已经正确处理公司行为。

---

# 六、数据清洗与边界问题

## 33. 缺失值

收益率序列可能包含：

```text
0.01, NaN, -0.02, 0.005
```

基础绩效函数通常先删除缺失值：

```python
clean = returns.dropna()
```

但删除缺失值后，必须确认剩余观测仍然保持等频。

若缺失值代表缺失交易日，而不是普通空值，则可能需要先补齐交易日历并判断缺失原因。

---

## 34. 样本至少需要两个观测

样本标准差分母为：

\[
N-1
\]

若只有一个有效收益率：

\[
N=1
\]

则分母为：

\[
N-1=0
\]

因此，`ddof=1` 时至少需要两个有效观测。

---

## 35. 常数收益序列

若每天收益都相同：

```text
0.1%, 0.1%, 0.1%, 0.1%
```

每个收益率都等于均值。

因此：

\[
r_t-\bar r=0
\]

方差为：

\[
s^2=0
\]

标准差为：

\[
s=0
\]

年化波动率也为 0。

这只是说明样本内收益没有变化，不代表未来没有风险。

---

## 36. 停牌与零收益

A 股停牌期间，价格可能连续不变，从而产生连续零收益。

若直接保留这些零收益，估计波动率可能下降。

复牌后价格可能一次性跳变。

因此，个股研究中要明确：

- 停牌日是否保留
- 是否按交易状态过滤
- 复牌跳空如何解释
- 股票是否在当日可交易

策略净值的日频绩效计算通常保留每日净值，但股票层面的风险研究应结合交易状态字段。

---

## 37. 极端值

极端收益会显著提高平方偏差，因此对标准差影响很大。

发现极端值时，不应立即删除。

应先判断：

1. 是否为真实市场波动
2. 是否为未复权造成
3. 是否为价格录入错误
4. 是否为涨跌停或复牌跳空
5. 是否为策略净值计算错误

真实极端行情属于风险的一部分，不能仅为了降低波动率而删除。

---

## 38. 短样本问题

只使用 5 天或 10 天收益估计年化波动率，数学上可以计算，但统计上很不稳定。

短样本的一个极端收益就可能显著改变结果。

输出年化波动率时，至少应同时保留：

- 有效观测数
- 样本起止日期
- 收益频率
- 年化因子
- `ddof` 口径

---

# 七、Python 实现

## 39. 今日需要掌握的 Python 函数

### `pd.Series()`

将输入转换为 pandas 序列：

```python
series = pd.Series(values, dtype="float64")
```

### `.dropna()`

删除缺失值：

```python
clean = series.dropna()
```

### `.std()`

计算标准差：

```python
sample_std = clean.std(ddof=1)
population_std = clean.std(ddof=0)
```

### `.pct_change()`

从价格或净值计算简单收益率：

```python
returns = nav.pct_change()
```

### `.rolling()`

创建滚动窗口：

```python
rolling_std = returns.rolling(window=20).std(ddof=1)
```

### `np.sqrt()`

计算平方根：

```python
annualization_scale = np.sqrt(252)
```

### `np.isfinite()`

检查输入是否为有限数：

```python
np.isfinite(clean).all()
```

---

## 40. 年化波动率函数

```python
from __future__ import annotations

import numpy as np
import pandas as pd


def annualized_volatility(
    returns: pd.Series,
    periods_per_year: int = 252,
    ddof: int = 1,
) -> float:
    """根据等频收益率序列计算年化波动率。"""
    clean = pd.Series(returns, dtype="float64").dropna()

    if periods_per_year <= 0:
        raise ValueError("periods_per_year 必须为正数")

    if ddof < 0:
        raise ValueError("ddof 不能为负数")

    if clean.size <= ddof:
        raise ValueError("有效观测数量必须大于 ddof")

    if not np.isfinite(clean.to_numpy()).all():
        raise ValueError("收益率必须为有限数")

    period_volatility = float(clean.std(ddof=ddof))

    return period_volatility * float(np.sqrt(periods_per_year))
```

核心代码为：

```python
clean.std(ddof=ddof) * np.sqrt(periods_per_year)
```

对应数学公式：

\[
\sigma_{\text{annual}}
=
\sigma_{\text{period}}\sqrt{A}
\]

---

## 41. 函数设计说明

第一步，将输入统一转换为浮点型序列：

```python
clean = pd.Series(returns, dtype="float64").dropna()
```

第二步，检查年化因子：

```python
if periods_per_year <= 0:
    raise ValueError(...)
```

第三步，检查自由度：

```python
if clean.size <= ddof:
    raise ValueError(...)
```

第四步，计算单期标准差：

```python
period_volatility = clean.std(ddof=ddof)
```

第五步，使用平方根时间法则年化：

```python
period_volatility * np.sqrt(periods_per_year)
```

---

## 42. 从净值计算年化波动率

```python
def annualized_volatility_from_nav(
    nav: pd.Series,
    periods_per_year: int = 252,
    ddof: int = 1,
) -> float:
    """根据等频净值序列计算年化波动率。"""
    clean_nav = pd.Series(nav, dtype="float64").dropna()

    if clean_nav.size < 3:
        raise ValueError("样本标准差至少需要三个净值点")

    if (clean_nav <= 0).any():
        raise ValueError("净值必须全部为正")

    returns = clean_nav.pct_change().dropna()

    return annualized_volatility(
        returns,
        periods_per_year=periods_per_year,
        ddof=ddof,
    )
```

为什么样本标准差至少需要三个净值点？

若净值点数量为 \(M\)，收益率数量为：

\[
N=M-1
\]

当 `ddof=1` 时，至少需要：

\[
N=2
\]

所以净值点至少需要：

\[
M=N+1=3
\]

---

## 43. 滚动年化波动率

滚动波动率用于观察风险随时间的变化。

```python
def rolling_annualized_volatility(
    returns: pd.Series,
    window: int = 20,
    periods_per_year: int = 252,
    ddof: int = 1,
) -> pd.Series:
    """计算滚动年化波动率。"""
    clean = pd.Series(returns, dtype="float64")

    if window <= ddof:
        raise ValueError("window 必须大于 ddof")

    if periods_per_year <= 0:
        raise ValueError("periods_per_year 必须为正数")

    rolling_period_volatility = clean.rolling(
        window=window,
        min_periods=window,
    ).std(ddof=ddof)

    return rolling_period_volatility * np.sqrt(periods_per_year)
```

若使用 20 个交易日窗口：

```python
rolling_vol = rolling_annualized_volatility(
    returns,
    window=20,
    periods_per_year=252,
)
```

其含义是：

> 对每个交易日，使用最近 20 个有效日收益估计日波动率，再换算成年化波动率。

---

## 44. 绩效报告函数

不要只返回一个波动率数字。

```python
def volatility_report(
    returns: pd.Series,
    periods_per_year: int = 252,
    ddof: int = 1,
) -> dict[str, float | int]:
    """返回波动率计算所需的主要口径信息。"""
    clean = pd.Series(returns, dtype="float64").dropna()

    annual_vol = annualized_volatility(
        clean,
        periods_per_year=periods_per_year,
        ddof=ddof,
    )

    period_vol = float(clean.std(ddof=ddof))

    return {
        "observations": int(clean.size),
        "periods_per_year": int(periods_per_year),
        "ddof": int(ddof),
        "period_volatility": period_vol,
        "annualized_volatility": annual_vol,
    }
```

示例输出：

```python
{
    "observations": 252,
    "periods_per_year": 252,
    "ddof": 1,
    "period_volatility": 0.012,
    "annualized_volatility": 0.190494,
}
```

---

## 45. 示例数据

```python
returns = pd.Series(
    [
        0.010,
        -0.010,
        0.020,
        0.000,
    ],
    name="strategy_return",
)

period_vol = returns.std(ddof=1)
annual_vol = annualized_volatility(
    returns,
    periods_per_year=252,
)

print(f"日波动率: {period_vol:.4%}")
print(f"年化波动率: {annual_vol:.4%}")
```

手工计算得到日波动率约为：

\[
1.2910\%
\]

因此年化波动率约为：

\[
1.2910\%\times\sqrt{252}
\]

\[
\approx
20.4939\%
\]

样本只有 4 个交易日，因此该年化结果只能用于验证公式，不适合作为稳定风险估计。

---

# 八、函数验证

## 46. 已知波动率测试

若日波动率为 \(1\%\)，年化因子为 4，则：

\[
\sigma_{\text{annual}}
=
1\%\times\sqrt{4}
\]

\[
\sigma_{\text{annual}}
=
2\%
\]

可以构造总体标准差恰好为 \(1\%\) 的序列：

```python
import math


def test_known_population_volatility() -> None:
    returns = pd.Series([-0.01, 0.01])

    result = annualized_volatility(
        returns,
        periods_per_year=4,
        ddof=0,
    )

    assert math.isclose(result, 0.02, rel_tol=1e-12)
```

该序列均值为 0。

总体方差为：

\[
\frac{(-0.01)^2+(0.01)^2}{2}
\]

\[
=
0.0001
\]

总体标准差为：

\[
\sqrt{0.0001}=0.01
\]

---

## 47. 常数收益测试

```python
def test_constant_returns_have_zero_volatility() -> None:
    returns = pd.Series([0.001] * 20)

    result = annualized_volatility(returns)

    assert math.isclose(result, 0.0, abs_tol=1e-12)
```

---

## 48. 缺失值测试

```python
def test_missing_values_are_ignored() -> None:
    with_missing = pd.Series([0.01, None, -0.01, 0.02])
    without_missing = pd.Series([0.01, -0.01, 0.02])

    result_with_missing = annualized_volatility(
        with_missing,
        periods_per_year=252,
    )
    result_without_missing = annualized_volatility(
        without_missing,
        periods_per_year=252,
    )

    assert math.isclose(
        result_with_missing,
        result_without_missing,
        rel_tol=1e-12,
    )
```

该测试只验证函数的缺失值处理逻辑。

真实研究中仍需确认删除缺失值后是否破坏等频结构。

---

## 49. 净值与收益率口径一致性测试

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

    from_returns = annualized_volatility(
        returns,
        periods_per_year=252,
    )
    from_nav = annualized_volatility_from_nav(
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

- 从净值计算收益率时是否漏掉 `.pct_change()`
- 是否错误地对净值本身求标准差
- 净值点数和收益率点数是否混淆

---

## 50. `ddof` 差异测试

```python
def test_sample_volatility_is_larger_for_short_sample() -> None:
    returns = pd.Series([0.01, -0.01, 0.02, 0.00])

    sample_result = annualized_volatility(
        returns,
        periods_per_year=252,
        ddof=1,
    )
    population_result = annualized_volatility(
        returns,
        periods_per_year=252,
        ddof=0,
    )

    assert sample_result > population_result
```

样本较长时，两者差异会缩小。

---

## 51. 非法输入测试

```python
import pytest


def test_too_few_observations_raise() -> None:
    returns = pd.Series([0.01])

    with pytest.raises(ValueError):
        annualized_volatility(returns, ddof=1)


def test_non_positive_periods_per_year_raise() -> None:
    returns = pd.Series([0.01, -0.01])

    with pytest.raises(ValueError):
        annualized_volatility(
            returns,
            periods_per_year=0,
        )


def test_infinite_return_raises() -> None:
    returns = pd.Series([0.01, np.inf, -0.01])

    with pytest.raises(ValueError):
        annualized_volatility(returns)
```

---

# 九、常见错误

## 52. 错误一：对净值直接求标准差

错误写法：

```python
nav.std()
```

净值通常随时间增长，其标准差受到价格水平和趋势影响。

正确流程是：

```python
returns = nav.pct_change().dropna()
volatility = returns.std(ddof=1)
```

---

## 53. 错误二：日波动率乘以 252

错误写法：

```python
annual_vol = daily_vol * 252
```

正确写法：

```python
annual_vol = daily_vol * np.sqrt(252)
```

原因是方差按时间近似线性累积，而标准差按时间平方根缩放。

---

## 54. 错误三：混淆 `ddof=0` 与 `ddof=1`

以下两行默认结果不同：

```python
np.std(values)
pd.Series(values).std()
```

第一行默认：

```python
ddof=0
```

第二行默认：

```python
ddof=1
```

研究代码应显式写出 `ddof`，避免依赖默认值。

---

## 55. 错误四：混用收益频率和年化因子

若输入是月收益率，却使用：

```python
periods_per_year=252
```

会严重高估年化波动率。

月频数据通常使用：

```python
periods_per_year=12
```

---

## 56. 错误五：将百分数 1 当作 1%

Python 中：

```python
0.01
```

表示 \(1\%\)。

而：

```python
1.0
```

表示 \(100\%\)。

若错误地将 1 输入为 \(1\%\)，计算结果会放大 100 倍。

---

## 57. 错误六：忽略复权和公司行为

未复权价格可能在除权除息日出现机械性跳变。

这种跳变会提高收益率标准差，但不一定代表真实投资损失。

A 股研究中必须先明确价格口径，再计算波动率。

---

## 58. 错误七：认为波动率越低策略一定越好

低波动策略可能同时具有：

- 低收益
- 长期缓慢亏损
- 尾部风险
- 流动性风险
- 极端跳空风险

波动率应与以下指标共同使用：

- 年化收益
- 夏普比率
- 最大回撤
- Calmar 比率
- 胜率
- 盈亏比

---

## 59. 错误八：对短样本过度解释

4 天收益计算出的年化波动率可以用于测试代码。

但不能据此断言策略的长期风险就是该数值。

样本越短，估计误差通常越大。

---

# 十、练习

## 60. 练习一：手工计算日波动率

给定四个日收益率：

\[
2\%,0\%,-2\%,0\%
\]

要求：

1. 计算均值
2. 计算总体方差
3. 计算总体标准差
4. 使用年化因子 4 计算年化波动率

### 解答

均值为：

\[
\bar r
=
\frac{2\%+0\%-2\%+0\%}{4}
\]

\[
\bar r=0
\]

偏差平方和为：

\[
0.02^2+0^2+(-0.02)^2+0^2
\]

\[
=0.0004+0+0.0004+0
\]

\[
=0.0008
\]

总体方差为：

\[
\sigma^2
=
\frac{0.0008}{4}
\]

\[
\sigma^2
=
0.0002
\]

总体标准差为：

\[
\sigma
=
\sqrt{0.0002}
\]

\[
\sigma
\approx
0.0141421
\]

转换为百分比：

\[
\sigma
\approx
1.4142\%
\]

年化波动率为：

\[
\sigma_{\text{annual}}
=
1.4142\%\times\sqrt{4}
\]

\[
\sigma_{\text{annual}}
=
1.4142\%\times2
\]

\[
\sigma_{\text{annual}}
\approx
2.8284\%
\]

---

## 61. 练习二：判断年化因子

分别给出以下数据应使用的常用年化因子：

1. A 股日收益率
2. 每周五收盘计算的周收益率
3. 月末净值计算的月收益率
4. 季度收益率

### 解答

1. 日频：252
2. 周频：52
3. 月频：12
4. 季度：4

实际项目中仍应根据数据生成规则明确写出口径。

---

## 62. 练习三：解释代码差异

下面两段代码为什么可能得到不同结果？

```python
np.std(returns)
```

```python
pd.Series(returns).std()
```

### 解答

`np.std()` 默认使用：

```python
ddof=0
```

`pd.Series.std()` 默认使用：

```python
ddof=1
```

前者使用分母 \(N\)，后者使用分母 \(N-1\)。

---

## 63. 练习四：编写滚动波动率

给定日收益率 `returns`，计算 60 日滚动年化波动率。

### 解答

```python
rolling_vol_60 = rolling_annualized_volatility(
    returns,
    window=60,
    periods_per_year=252,
    ddof=1,
)
```

前 59 个位置通常为缺失值，因为窗口尚未收集满 60 个观测。

---

## 64. 练习五：识别错误

以下代码有什么问题？

```python
annual_vol = nav.std() * 252
```

### 解答

有两个主要错误：

1. 对净值本身求标准差，而不是对收益率求标准差
2. 标准差年化应乘以平方根年化因子，而不是直接乘以年化因子

正确写法为：

```python
returns = nav.pct_change().dropna()
annual_vol = returns.std(ddof=1) * np.sqrt(252)
```

---

# 十一、今日输出

## 65. 最小可复用版本

今天至少应保留以下函数：

```python
from __future__ import annotations

import numpy as np
import pandas as pd


def annualized_volatility(
    returns: pd.Series,
    periods_per_year: int = 252,
    ddof: int = 1,
) -> float:
    """根据等频收益率序列计算年化波动率。"""
    clean = pd.Series(returns, dtype="float64").dropna()

    if periods_per_year <= 0:
        raise ValueError("periods_per_year 必须为正数")

    if ddof < 0:
        raise ValueError("ddof 不能为负数")

    if clean.size <= ddof:
        raise ValueError("有效观测数量必须大于 ddof")

    if not np.isfinite(clean.to_numpy()).all():
        raise ValueError("收益率必须为有限数")

    return float(
        clean.std(ddof=ddof)
        * np.sqrt(periods_per_year)
    )
```

---

## 66. 推荐扩展版本

在统一绩效模块中，建议同时实现：

```python
annualized_volatility()
annualized_volatility_from_nav()
rolling_annualized_volatility()
volatility_report()
```

后续学习夏普比率时，将直接复用年化波动率函数。

---

# 十二、今日检查清单

完成学习后，检查自己能否回答：

- [ ] 波动率为什么对收益率计算，而不是对价格计算
- [ ] 方差为什么使用偏差平方
- [ ] 样本方差为什么除以 \(N-1\)
- [ ] `ddof=0` 和 `ddof=1` 有什么区别
- [ ] pandas 与 NumPy 的标准差默认口径有什么不同
- [ ] 日波动率为什么乘以 \(\sqrt{252}\)
- [ ] 平方根时间法则依赖哪些假设
- [ ] 自相关为什么会影响波动率年化
- [ ] 日频、周频、月频分别使用什么年化因子
- [ ] 如何从净值序列计算年化波动率
- [ ] 如何计算滚动年化波动率
- [ ] 为什么短样本年化结果需要谨慎解释

---

# 十三、今日总结

今天最重要的公式是：

\[
\sigma_{\text{annual}}
=
\sigma_{\text{period}}\sqrt{A}
\]

其中：

- \(\sigma_{\text{period}}\) 是单期收益率标准差
- \(A\) 是一年包含的同频周期数
- 日频数据常用 \(A=252\)

这个公式来自方差的可加性。

在收益彼此不相关且方差稳定时：

\[
\operatorname{Var}
\left(
\sum_{t=1}^{A}r_t
\right)
=
A\sigma^2
\]

两边开平方后：

\[
\operatorname{Std}
\left(
\sum_{t=1}^{A}r_t
\right)
=
\sqrt{A}\sigma
\]

实际研究中，必须同时明确：

- 收益率口径
- 数据频率
- 年化因子
- 样本标准差或总体标准差
- 缺失值处理
- 样本长度
- 复权方式
- 平方根时间法则的假设

下一天将学习夏普比率，把年化收益与年化波动率组合成单位风险收益指标。