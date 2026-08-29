# 第七周第二天：方差、标准差与年化波动率

## 一、今日学习目标

完成本课程后，应能够：

1. 理解离差、平方离差、方差和标准差。
2. 区分总体方差与样本方差。
3. 解释样本方差为什么使用 $n-1$。
4. 使用标准差衡量股票收益率的波动程度。
5. 将日波动率转换为年化波动率。
6. 理解根号时间法则的假设和局限。
7. 认识滚动波动率与波动率聚集。
8. 计算下行波动率。
9. 比较多只股票的风险水平。
10. 避免把标准差等同于最大亏损。

今日核心问题：

> 一只股票的收益率通常会偏离平均水平多远？

---

## 二、为什么只看平均收益不够

股票 A：

```text
1%、1%、1%、1%、1%
```

股票 B：

```text
-5%、0%、1%、4%、5%
```

两者平均收益率都是 1%，但股票 B 的收益在 -5% 到 5% 之间剧烈变化。

均值描述收益中心，不能描述收益率围绕中心的离散程度。方差和标准差用于回答：

- 收益率通常偏离均值多少；
- 哪只股票更加稳定；
- 最近风险是否正在上升；
- 极端涨跌是否集中出现。

---

## 三、离差

给定收益率：

```text
-2%、0%、1%、2%、4%
```

均值：

$$
\bar r=\frac{-2\%+0\%+1\%+2\%+4\%}{5}=1\%
$$

离差为：

$$
r_t-\bar r
$$

| 收益率 | 均值 | 离差 |
|---:|---:|---:|
| -2% | 1% | -3% |
| 0% | 1% | -1% |
| 1% | 1% | 0% |
| 2% | 1% | 1% |
| 4% | 1% | 3% |

正离差表示收益高于均值，负离差表示收益低于均值。

---

## 四、为什么不能直接平均离差

均值具有以下性质：

$$
\sum_{t=1}^{n}(r_t-\bar r)=0
$$

正负离差会抵消，所以离差平均值永远为 0，不能衡量波动。

解决办法包括：

- 对离差取绝对值；
- 对离差平方。

统计学中更常使用平方离差。

---

## 五、平方离差

平方离差：

$$
(r_t-\bar r)^2
$$

它有两个重要特点：

1. 正负离差平方后均为非负数；
2. 大幅偏离会被赋予更高权重。

因此极端收益会显著影响方差和标准差。

---

## 六、总体方差

如果数据包含研究对象的全部观测，总体方差为：

$$
\sigma^2=\frac{1}{n}\sum_{t=1}^{n}(r_t-\mu)^2
$$

其中：

- $\sigma^2$：总体方差；
- $\mu$：总体均值；
- $n$：总体观测数量。

方差单位是收益率单位的平方，因此金融解释不够直观。

---

## 七、样本方差

金融研究通常只有历史样本，因此常用样本方差：

$$
s^2=\frac{1}{n-1}\sum_{t=1}^{n}(r_t-\bar r)^2
$$

### 为什么除以 $n-1$

样本均值由当前样本估计。当 $n-1$ 个离差确定后，最后一个离差也被确定，因为离差之和必须为 0。

自由度为：

$$
\text{df}=n-1
$$

使用 $n-1$ 可以修正使用样本均值时对总体方差的系统性低估，这称为贝塞尔校正。

---

## 八、标准差

标准差是方差的平方根。

总体标准差：

$$
\sigma=\sqrt{\frac{1}{n}\sum_{t=1}^{n}(r_t-\mu)^2}
$$

样本标准差：

$$
s=\sqrt{\frac{1}{n-1}\sum_{t=1}^{n}(r_t-\bar r)^2}
$$

标准差与收益率使用相同单位，因此更容易解释。

例如：

```text
平均日收益率：0.05%
日收益率标准差：2.00%
```

可初步理解为日收益围绕均值的典型波动尺度约为 2%。

---

## 九、标准差的金融含义与局限

标准差越大，收益率越分散，历史不确定性越高。

但标准差同时把上涨和下跌视为波动。大幅上涨也会提高标准差。

标准差不是：

- 最大跌幅；
- 最大回撤；
- 涨跌停边界；
- 未来风险的确定预测；
- 纯粹的下行风险。

完整风险分析还需结合分位数、偏度、峰度、下行波动率和最大回撤。

---

## 十、正态分布中的标准差区间

若收益率近似服从正态分布，则理论上：

- 约 68.27% 位于均值上下 1 个标准差；
- 约 95.45% 位于均值上下 2 个标准差；
- 约 99.73% 位于均值上下 3 个标准差。

但真实金融收益通常存在偏度、厚尾和波动率聚集，超过 3 倍标准差的事件往往比正态理论更加频繁。

---

## 十一、手工计算示例

给定：

```text
-2%、-1%、0%、1%、2%
```

均值为 0，平方离差之和为 0.001。

总体方差：

$$
\sigma^2=\frac{0.001}{5}=0.0002
$$

总体标准差：

$$
\sigma=\sqrt{0.0002}\approx1.414\%
$$

样本方差：

$$
s^2=\frac{0.001}{4}=0.00025
$$

样本标准差：

$$
s=\sqrt{0.00025}\approx1.581\%
$$

样本标准差通常略高于总体标准差。

---

## 十二、pandas 与 NumPy 的 `ddof`

pandas 默认使用 `ddof=1`：

```python
returns.var()
returns.std()
returns.var(ddof=1)
returns.std(ddof=1)
```

NumPy 默认使用 `ddof=0`：

```python
import numpy as np

np.var(returns)
np.std(returns)
```

计算样本统计量：

```python
np.var(returns, ddof=1)
np.std(returns, ddof=1)
```

| 工具 | 默认 `ddof` | 默认统计量 |
|---|---:|---|
| pandas | 1 | 样本方差、样本标准差 |
| NumPy | 0 | 总体方差、总体标准差 |

---

## 十三、年化波动率

日波动率常转换为年化波动率：

$$
\sigma_{annual}=\sigma_{daily}\sqrt{252}
$$

例如日波动率为 2%：

$$
2\%\times\sqrt{252}\approx31.75\%
$$

Python：

```python
annual_volatility = daily_volatility * np.sqrt(252)
```

不同频率的常用转换：

$$
\sigma_{annual}=\sigma_{weekly}\sqrt{52}
$$

$$
\sigma_{annual}=\sigma_{monthly}\sqrt{12}
$$

---

## 十四、为什么乘以根号时间

若每日收益相互独立且每日方差相同，则：

$$
Var(r_1+\cdots+r_T)=T\sigma_d^2
$$

因此：

$$
\sigma_T=\sqrt{T\sigma_d^2}=\sigma_d\sqrt{T}
$$

根号时间法则隐含：

- 收益相互独立；
- 方差相对稳定；
- 不存在强烈自相关；
- 波动结构没有显著变化。

现实市场并不完全满足这些条件，所以年化波动率是标准化比较指标，不是精确预测。

---

## 十五、滚动波动率

全样本标准差只描述整个样本期的平均风险，无法反映风险随时间变化。

20 日滚动标准差：

```python
df = df.sort_values(["code", "date"])

df["volatility_20d"] = (
    df.groupby("code")["return"]
      .rolling(20)
      .std()
      .reset_index(level=0, drop=True)
)

df["annual_volatility_20d"] = (
    df["volatility_20d"] * np.sqrt(252)
)
```

若全样本年化波动率为 25%，最近 20 日为 48%，说明近期风险明显高于历史平均。

---

## 十六、波动率聚集

金融市场常出现：

```text
高波动 → 高波动 → 高波动
低波动 → 低波动 → 低波动
```

这称为波动率聚集。

观察方法：

```python
df["abs_return"] = df["return"].abs()
df["squared_return"] = df["return"] ** 2
```

结合日收益率时间序列和滚动波动率曲线，观察极端涨跌是否集中出现。

---

## 十七、下行波动率

标准差同时考虑正负收益，投资者通常更关心下跌。

一种简单方法只对负收益计算标准差：

```python
negative_returns = returns[returns < 0]
downside_volatility = negative_returns.std()
```

更常见的目标收益法：

$$
DownsideDeviation=\sqrt{\frac{1}{n}\sum_{t=1}^{n}\min(r_t-r_{target},0)^2}
$$

目标收益为 0 时：

$$
DownsideDeviation=\sqrt{\frac{1}{n}\sum_{t=1}^{n}\min(r_t,0)^2}
$$

Python：

```python
import numpy as np
import pandas as pd


def downside_deviation(
    returns: pd.Series,
    target: float = 0.0,
) -> float:
    clean = returns.dropna()
    if clean.empty:
        return float("nan")

    downside = np.minimum(clean - target, 0.0)
    return float(np.sqrt(np.mean(downside ** 2)))
```

---

## 十八、多股票波动率统计

```python
volatility_stats = (
    df.groupby("code")["return"]
      .agg(
          sample_count="count",
          daily_mean="mean",
          daily_variance="var",
          daily_volatility="std",
          min_return="min",
          max_return="max",
      )
)

volatility_stats["annual_volatility"] = (
    volatility_stats["daily_volatility"] * np.sqrt(252)
)
```

按年化波动率排序：

```python
volatility_stats.sort_values(
    "annual_volatility",
    ascending=False,
)
```

---

## 十九、可复用函数

```python
import numpy as np
import pandas as pd


def calculate_volatility_statistics(
    df: pd.DataFrame,
    code_col: str = "code",
    return_col: str = "return",
    annualization_factor: int = 252,
) -> pd.DataFrame:
    """按股票代码计算方差、波动率和下行波动率。"""
    required_columns = {code_col, return_col}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"缺少必要字段：{sorted(missing)}")

    data = df[[code_col, return_col]].copy()
    data[return_col] = pd.to_numeric(
        data[return_col],
        errors="coerce",
    )

    grouped = data.groupby(code_col)[return_col]
    result = grouped.agg(
        sample_count="count",
        mean_return="mean",
        variance="var",
        daily_volatility="std",
        min_return="min",
        max_return="max",
    )

    result["annual_volatility"] = (
        result["daily_volatility"]
        * np.sqrt(annualization_factor)
    )

    result["daily_downside_deviation"] = grouped.apply(
        lambda x: downside_deviation(x, target=0.0)
    )

    result["annual_downside_deviation"] = (
        result["daily_downside_deviation"]
        * np.sqrt(annualization_factor)
    )

    return result.reset_index()
```

---

## 二十、极端值对标准差的影响

```python
import pandas as pd

returns = pd.Series([-0.01, -0.005, 0.00, 0.005, 0.01])
returns_with_outlier = pd.concat(
    [returns, pd.Series([0.10])],
    ignore_index=True,
)

print(f"原始标准差：{returns.std():.2%}")
print(f"加入极端值后：{returns_with_outlier.std():.2%}")
```

高波动率可能由少数极端交易日造成。发现高波动后，应检查是否存在真实涨跌停、复牌、公司行为或数据错误，但不能未经核验就删除极端值。

---

## 二十一、A 股数据注意事项

1. 涨跌停会影响收益分布边界，不同板块和历史时期规则可能不同。
2. 停牌日被错误填为 0 会低估波动率。
3. 未复权价格可能在除权日制造虚假大跌。
4. 新股上市和长期停牌后复牌的收益分布与普通阶段不同。
5. 比较股票时应使用相同时间区间、复权方式和有效样本定义。

---

## 二十二、实践任务

### 任务一：基础波动统计

| 股票代码 | 样本数 | 平均日收益 | 日方差 | 日标准差 | 年化波动率 |
|---|---:|---:|---:|---:|---:|

### 任务二：下行风险

| 股票代码 | 日下行波动率 | 年化下行波动率 | 总体波动率减下行波动率 |
|---|---:|---:|---:|

### 任务三：滚动波动率

计算：

- 20 日滚动标准差；
- 20 日滚动年化波动率；
- 60 日滚动年化波动率。

### 任务四：极端值影响

对每只股票比较：

- 原始标准差；
- 删除最大收益后的标准差；
- 删除最小收益后的标准差；
- 删除最大和最小收益后的标准差。

### 任务五：写出至少三条风险结论

结论需包含股票代码、样本区间、指标数值、比较基准和限制条件。

---

## 二十三、常见错误

1. 混淆方差和标准差的单位。
2. 忽略 pandas 与 NumPy 的 `ddof` 默认值差异。
3. 把日标准差直接乘以 252。
4. 把标准差当作最大跌幅。
5. 把高波动简单理解为坏事。
6. 比较不同样本区间的波动率。
7. 忽略停牌日和复权问题。
8. 把历史年化波动率当作未来精确预测。

---

## 二十四、自测题

1. 为什么离差不能直接求平均衡量风险？
2. 为什么使用平方离差？
3. 方差与标准差有什么区别？
4. 样本方差为什么除以 $n-1$？
5. 日波动率怎样年化？
6. 标准差是否只衡量下跌？
7. 标准差是否代表最大亏损？
8. 为什么需要滚动波动率？
9. 什么是波动率聚集？
10. 年化波动率是否是未来风险的精确预测？

---

## 二十五、今日验收标准

- 能解释离差为什么会互相抵消；
- 能手工计算简单样本的方差和标准差；
- 能区分总体与样本统计量；
- 能解释 $n-1$ 的基本含义；
- 能计算日波动率和年化波动率；
- 能说明根号时间法则的假设；
- 能解释标准差为什么不等于亏损风险；
- 能计算 20 日和 60 日滚动波动率；
- 能识别波动率聚集；
- 能计算下行波动率；
- 能完成多股票波动率比较表。

---

## 二十六、今日最终产出

```text
notebooks/week07_day02_volatility.ipynb
src/statistics.py
```

建议实现：

```python
calculate_volatility_statistics()
downside_deviation()
```

今日最重要的结论：

> 均值描述收益中心，标准差描述收益通常离中心有多远；但标准差衡量的是整体不确定性，并不等同于最大亏损或纯粹的下跌风险。
