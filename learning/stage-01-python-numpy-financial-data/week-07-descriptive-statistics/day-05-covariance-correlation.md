# 第七周第五天：协方差、相关系数与滚动相关性

## 一、今日学习目标

完成本课程后，应能够：

1. 理解协方差衡量的内容。
2. 区分正协方差、负协方差和接近零的协方差。
3. 理解协方差为什么不适合直接比较不同股票组合。
4. 理解相关系数的标准化过程。
5. 正确解释相关系数的方向和强弱。
6. 区分相关关系与因果关系。
7. 使用 pandas 计算协方差矩阵和相关系数矩阵。
8. 正确对齐多只股票的交易日期。
9. 计算滚动相关系数。
10. 分析不同市场环境中的相关性变化。
11. 使用相关性初步判断组合分散化效果。
12. 避免直接使用价格序列计算普通收益联动关系。

今日核心问题：

> 两只股票是否经常在同一个交易日朝相同方向变化？

---

## 二、为什么研究股票之间的关系

组合风险不仅取决于每只股票自身的波动率，还取决于股票之间是否同时上涨或同时下跌。

- 经常同涨同跌：分散效果有限；
- 关系较弱：部分波动可能互相抵消；
- 经常反向变化：在一定条件下分散作用更强。

因此组合分析要同时观察：

```text
单只股票波动率
股票之间的协方差
股票之间的相关系数
```

---

## 三、协方差的定义

总体协方差：

$$
Cov(X,Y)=\frac{1}{n}\sum_{i=1}^{n}(x_i-\mu_X)(y_i-\mu_Y)
$$

样本协方差：

$$
Cov_s(X,Y)=\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar x)(y_i-\bar y)
$$

分析历史股票收益时，通常使用样本协方差。

---

## 四、离差乘积与共同变化

协方差的核心是：

$$
(x_i-\bar x)(y_i-\bar y)
$$

| X 离差 | Y 离差 | 乘积 | 含义 |
|---:|---:|---:|---|
| 正 | 正 | 正 | 两者同时高于均值 |
| 负 | 负 | 正 | 两者同时低于均值 |
| 正 | 负 | 负 | X 高于均值、Y 低于均值 |
| 负 | 正 | 负 | X 低于均值、Y 高于均值 |

因此：

- 同方向变化较多，协方差通常为正；
- 反方向变化较多，协方差通常为负；
- 正负关系互相抵消，协方差可能接近零。

---

## 五、正协方差、负协方差和零协方差

### 正协方差

$$
Cov(X,Y)>0
$$

表示两只股票倾向于同方向变化。同行业股票、共同受市场或商品价格影响的股票常出现正协方差。

### 负协方差

$$
Cov(X,Y)<0
$$

表示两只资产倾向于反方向变化，可能具有较好的分散作用。A 股股票之间长期稳定的显著负相关并不常见，因为许多股票共同受到市场因素影响。

### 接近零

$$
Cov(X,Y)\approx0
$$

表示没有明显的平均线性共同变化方向，但不等于完全没有关系。可能存在：

- 非线性关系；
- 滞后关系；
- 分阶段关系；
- 极端行情关系；
- 正负关系在全样本中互相抵消。

---

## 六、手工计算协方差

```text
股票 X：-2%、-1%、0%、1%、2%
股票 Y：-1%、-0.5%、0%、0.5%、1%
```

两者均值为 0，离差乘积之和为 0.00050。

样本协方差：

$$
Cov_s(X,Y)=\frac{0.00050}{5-1}=0.000125
$$

结果为正，说明两只股票同向变化。

---

## 七、协方差的局限

协方差受两只股票自身波动率和收益率单位影响。

例如：

```text
A与B协方差：0.00010
C与D协方差：0.00025
```

不能只因为 0.00025 更大，就认定 C 与 D 的关系更强，因为 C、D 可能本身波动更大。

因此需要将协方差标准化。

---

## 八、相关系数

皮尔逊相关系数：

$$
\rho_{XY}=\frac{Cov(X,Y)}{\sigma_X\sigma_Y}
$$

样本形式：

$$
r_{XY}=\frac{Cov_s(X,Y)}{s_Xs_Y}
$$

取值范围：

$$
-1\le r_{XY}\le1
$$

- $r=1$：完全线性正相关；
- $r=-1$：完全线性负相关；
- $r\approx0$：线性关系较弱。

---

## 九、相关强弱的经验解释

| 相关系数绝对值 | 初步解释 |
|---:|---|
| 0.00—0.20 | 线性关系很弱 |
| 0.20—0.40 | 较弱相关 |
| 0.40—0.60 | 中等相关 |
| 0.60—0.80 | 较强相关 |
| 0.80—1.00 | 很强相关 |

这些是经验范围，不是固定交易规则。

---

## 十、相关系数与方向一致率

方向一致率：

$$
DirectionAgreement=\frac{\text{同方向交易日数量}}{\text{共同有效交易日数量}}
$$

Python：

```python
direction_agreement = (
    (returns_x * returns_y) > 0
).mean()
```

方向一致率只看正负方向，相关系数还考虑收益幅度之间的线性关系，因此两者不同。

---

## 十一、相关性不等于因果关系

若两只股票相关系数为 0.80，不能直接得出“股票 A 上涨导致股票 B 上涨”。高相关可能来自：

- 同一行业因素；
- 共同市场指数暴露；
- 相同利率、汇率或商品价格影响；
- 相同风险偏好变化。

研究因果关系还需要明确经济机制、控制其他变量、检查时间顺序并进行统计检验。

---

## 十二、为什么使用收益率而不是价格

股票价格常具有长期趋势和非平稳性，两只无关股票只要长期都上涨，价格相关性也可能很高。

错误做法：

```python
price_wide.corr()
```

普通收益联动研究通常应使用：

```python
return_wide.corr()
```

可能出现：

```text
价格相关系数：0.95
收益率相关系数：0.18
```

价格高相关主要来自共同趋势，不代表每日收益同步。

---

## 十三、pandas 计算协方差和相关系数

两只股票：

```python
covariance = returns_x.cov(returns_y)
correlation = returns_x.corr(returns_y)
```

多只股票：

```python
covariance_matrix = returns_wide.cov()
correlation_matrix = returns_wide.corr()
```

协方差矩阵对角线是各股票方差：

$$
Cov(X,X)=Var(X)
$$

相关系数矩阵对角线为 1，并且矩阵对称：

$$
Corr(X,Y)=Corr(Y,X)
$$

---

## 十四、长表转换为收益率宽表

长表：

```text
date, code, return
```

转换：

```python
returns_wide = df.pivot(
    index="date",
    columns="code",
    values="return",
).sort_index()
```

转换前必须确保同一日期、同一代码只有一条记录。

---

## 十五、日期对齐

不同日期的收益不能按行号直接配对。

正确做法：

```python
pair_data = pd.concat(
    [returns_x, returns_y],
    axis=1,
    join="inner",
).dropna()
```

或先建立以日期为索引的收益率宽表。

---

## 十六、缺失值与共同样本数

股票可能因停牌、上市时间不同、退市或数据缺失而没有相同日期收益。

pandas 通常对每一对股票使用共同非缺失观测计算相关系数，因此同一个矩阵中的每个数可能使用不同样本数量。

共同有效样本数矩阵：

```python
import pandas as pd


def calculate_overlap_counts(
    returns_wide: pd.DataFrame,
) -> pd.DataFrame:
    valid = returns_wide.notna().astype(int)
    return valid.T @ valid
```

设置最低样本数：

```python
correlation_matrix = returns_wide.corr(
    min_periods=120,
)
```

---

## 十七、提取股票组合相关性

```python
import numpy as np
import pandas as pd


def correlation_pairs(
    correlation_matrix: pd.DataFrame,
) -> pd.DataFrame:
    mask = np.triu(
        np.ones(correlation_matrix.shape, dtype=bool),
        k=1,
    )

    pairs = (
        correlation_matrix
        .where(mask)
        .stack()
        .rename("correlation")
        .reset_index()
    )

    pairs.columns = ["stock_x", "stock_y", "correlation"]
    return pairs.sort_values("correlation", ascending=False)
```

对角线和重复的下三角元素会被排除。

---

## 十八、滚动相关系数

全样本相关系数只给出整个样本期的平均关系。相关性会随市场环境变化。

60 日滚动相关：

```python
rolling_corr_60d = (
    returns_wide["000001"]
    .rolling(
        window=60,
        min_periods=40,
    )
    .corr(returns_wide["000002"])
)
```

若：

```text
全样本相关系数：0.42
最近60日相关系数：0.78
```

说明近期联动明显增强，当前组合分散效果可能弱于历史平均。

窗口特点：

- 短窗口反应快，但噪声大；
- 长窗口更稳定，但反应慢。

---

## 十九、危机时期的相关性

正常时期不同行业股票相关性可能较低，但市场快速下跌时，投资者可能同时卖出大量股票，导致相关性上升。

因此：

> 历史低相关不保证极端行情中仍然低相关。

可以分别计算：

- 全部交易日；
- 市场上涨日；
- 市场下跌日；
- 市场大跌日。

```python
up_market = pair_data.loc[pair_data["market_return"] > 0]
down_market = pair_data.loc[pair_data["market_return"] < 0]
stress_market = pair_data.loc[pair_data["market_return"] <= -0.02]

corr_all = pair_data["stock_x"].corr(pair_data["stock_y"])
corr_up = up_market["stock_x"].corr(up_market["stock_y"])
corr_down = down_market["stock_x"].corr(down_market["stock_y"])
corr_stress = stress_market["stock_x"].corr(stress_market["stock_y"])
```

每个状态都必须报告样本数量。

---

## 二十、Pearson 与 Spearman

Pearson：

```python
returns_wide.corr(method="pearson")
```

主要衡量线性关系，对极端值较敏感。

Spearman：

```python
returns_wide.corr(method="spearman")
```

先转换为排名，主要衡量单调关系，通常对极端值更稳健。

如果 Pearson 为 0.20、Spearman 为 0.55，可能说明存在同方向排序关系，但收益幅度之间的线性关系较弱，或者极端值影响了 Pearson。

---

## 二十一、相关系数对异常值敏感

某一天两只股票同时大涨或一涨一跌，都可能显著改变 Pearson 相关系数。

应比较：

1. 原始相关系数；
2. 核验极端交易日后的相关系数；
3. Pearson 与 Spearman；
4. 不同市场状态下的相关性。

不能未经核验直接删除真实极端行情。

---

## 二十二、散点图

```python
import matplotlib.pyplot as plt

pair_data = returns_wide[["000001", "000002"]].dropna()

plt.figure(figsize=(7, 6))
plt.scatter(
    pair_data["000001"],
    pair_data["000002"],
    alpha=0.6,
)
plt.xlabel("000001 Daily Return")
plt.ylabel("000002 Daily Return")
plt.title("Return Relationship")
plt.show()
```

观察：

- 是否围绕右上倾斜直线；
- 是否围绕右下倾斜直线；
- 是否存在极端孤立点；
- 是否存在弯曲或多个市场状态群组。

---

## 二十三、组合风险与相关性

两资产组合方差：

$$
Var(P)=w_1^2\sigma_1^2+w_2^2\sigma_2^2+2w_1w_2Cov(1,2)
$$

由于：

$$
Cov(1,2)=\rho_{12}\sigma_1\sigma_2
$$

所以：

$$
Var(P)=w_1^2\sigma_1^2+w_2^2\sigma_2^2+2w_1w_2\rho_{12}\sigma_1\sigma_2
$$

组合标准差：

$$
\sigma_P=\sqrt{Var(P)}
$$

相关性降低时，组合风险通常下降；负相关可能产生更强分散作用。

---

## 二十四、组合风险示例

假设：

```text
股票A年化波动率：20%
股票B年化波动率：30%
权重：各50%
相关系数：0.60
```

$$
Var(P)=0.5^2\times0.2^2+0.5^2\times0.3^2+2\times0.5\times0.5\times0.60\times0.2\times0.3
$$

$$
Var(P)=0.0505
$$

$$
\sigma_P=\sqrt{0.0505}\approx22.47\%
$$

若相关系数降为 0：

$$
Var(P)=0.0325
$$

$$
\sigma_P\approx18.03\%
$$

相关性降低后，组合风险明显下降。

---

## 二十五、低相关不等于优质资产

一只股票与现有组合相关性较低，不代表应该直接买入，还需检查：

- 预期收益；
- 自身波动率；
- 最大回撤和左尾风险；
- 流动性和交易成本；
- 样本稳定性；
- 压力时期相关性。

---

## 二十六、A 股数据特殊问题

1. 停牌导致非同步交易，停牌收益填 0 会低估相关性。
2. 涨跌停会截断单日收益，连续跌停可能把冲击分散到多个交易日。
3. 新股与老股共同样本可能很少。
4. 同行业高相关可能主要来自市场和行业共同因素。
5. 小盘股非同步成交可能导致当日相关性被低估、滞后相关性上升。

---

## 二十七、可复用分析函数

```python
import numpy as np
import pandas as pd


def calculate_dependency_statistics(
    df: pd.DataFrame,
    date_col: str = "date",
    code_col: str = "code",
    return_col: str = "return",
    min_periods: int = 120,
) -> dict[str, pd.DataFrame]:
    required_columns = {date_col, code_col, return_col}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"缺少必要字段：{sorted(missing)}")

    data = df[[date_col, code_col, return_col]].copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data[return_col] = pd.to_numeric(data[return_col], errors="coerce")
    data = data.dropna(subset=[date_col, code_col])

    if data.duplicated([date_col, code_col], keep=False).any():
        raise ValueError("存在重复的日期与股票代码组合")

    returns_wide = data.pivot(
        index=date_col,
        columns=code_col,
        values=return_col,
    ).sort_index()

    covariance_matrix = returns_wide.cov(min_periods=min_periods)
    correlation_matrix = returns_wide.corr(min_periods=min_periods)
    overlap_counts = returns_wide.notna().astype(int).T @ returns_wide.notna().astype(int)

    upper_mask = np.triu(
        np.ones(correlation_matrix.shape, dtype=bool),
        k=1,
    )

    pairs = (
        correlation_matrix
        .where(upper_mask)
        .stack()
        .rename("correlation")
        .reset_index()
    )
    pairs.columns = ["stock_x", "stock_y", "correlation"]
    pairs["overlap_count"] = [
        overlap_counts.loc[x, y]
        for x, y in zip(pairs["stock_x"], pairs["stock_y"])
    ]
    pairs = pairs.sort_values("correlation", ascending=False)

    return {
        "returns_wide": returns_wide,
        "covariance_matrix": covariance_matrix,
        "correlation_matrix": correlation_matrix,
        "overlap_counts": overlap_counts,
        "correlation_pairs": pairs,
    }
```

滚动相关函数：

```python
def calculate_rolling_correlation(
    returns_wide: pd.DataFrame,
    stock_x: str,
    stock_y: str,
    window: int = 60,
    min_periods: int | None = None,
) -> pd.Series:
    if stock_x not in returns_wide.columns:
        raise ValueError(f"不存在股票代码：{stock_x}")
    if stock_y not in returns_wide.columns:
        raise ValueError(f"不存在股票代码：{stock_y}")
    if window < 2:
        raise ValueError("窗口长度必须至少为2")

    if min_periods is None:
        min_periods = max(2, int(window * 0.7))

    return (
        returns_wide[stock_x]
        .rolling(window=window, min_periods=min_periods)
        .corr(returns_wide[stock_y])
    )
```

---

## 二十八、实践任务

### 任务一：建立收益率宽表

使用至少 5 只股票、至少一年日线数据，统一收益率定义和复权方式，不直接填充停牌收益率。

### 任务二：协方差矩阵

检查：

- 矩阵是否对称；
- 对角线是否等于各股票方差；
- 哪组协方差最高、最低。

### 任务三：相关矩阵与共同样本数

| 股票A | 股票B | 相关系数 | 共同样本数 | 关系判断 |
|---|---|---:|---:|---|

筛选最高 3 组、最低 3 组和样本不足组合。

### 任务四：Pearson 与 Spearman

寻找两种相关系数差异最大的股票组合，检查异常值和非线性关系。

### 任务五：滚动相关性

对高相关、低相关、同行业和不同行业组合计算 20 日、60 日和 120 日滚动相关。

### 任务六：市场状态相关性

| 股票组合 | 全样本相关 | 上涨日相关 | 下跌日相关 | 大跌日相关 |
|---|---:|---:|---:|---:|

必须同时报告各状态样本数。

---

## 二十九、常见错误

1. 使用价格而不是收益率计算普通相关性。
2. 忽略日期对齐。
3. 把停牌收益填成 0。
4. 只看相关系数，不看共同样本数。
5. 把高相关解释为因果关系。
6. 相关系数接近 0 就认为完全无关。
7. 只使用全样本相关系数。
8. 把历史低相关当作永久规律。
9. 把低相关股票直接视为优质股票。
10. 忽略极端收益对 Pearson 相关的影响。

---

## 三十、自测题

1. 协方差大于 0 表示什么？
2. 协方差小于 0 表示什么？
3. 为什么协方差不适合直接比较不同组合？
4. 相关系数的范围是什么？
5. 相关系数为 0 是否代表完全没有关系？
6. 为什么使用收益率计算相关性？
7. 为什么需要滚动相关性？
8. 高相关是否代表因果关系？
9. 为什么报告共同样本数？
10. 市场危机时相关性可能怎样变化？

---

## 三十一、今日验收标准

- 能解释离差乘积与共同变化；
- 能正确解释协方差方向；
- 能说明协方差受波动尺度影响；
- 能写出相关系数计算关系；
- 能区分相关性与因果关系；
- 能使用收益率而不是价格；
- 能将长表转换为宽表；
- 能计算协方差矩阵和相关矩阵；
- 能计算共同有效样本数；
- 能找出最高和最低相关组合；
- 能计算滚动相关和条件相关；
- 能解释相关性对组合分散的影响。

---

## 三十二、今日最终产出

```text
notebooks/week07_day05_covariance_correlation.ipynb
src/statistics.py
```

建议实现：

```python
calculate_dependency_statistics()
calculate_overlap_counts()
correlation_pairs()
calculate_rolling_correlation()
```

今日最重要的结论：

> 协方差告诉我们两只股票是否倾向于共同变化，相关系数消除了波动尺度的影响。低相关有助于风险分散，但相关性并不固定，市场压力时期往往会明显上升。
