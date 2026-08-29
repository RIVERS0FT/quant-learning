# 第七周第四天：偏度、峰度与非正态收益分布

## 一、今日学习目标

完成本课程后，应能够：

1. 理解收益分布的对称性。
2. 理解偏度的定义与金融含义。
3. 区分正偏、负偏和近似对称分布。
4. 理解普通峰度和超额峰度。
5. 解释股票收益率中的尖峰厚尾现象。
6. 比较实际极端收益频率与正态分布理论值。
7. 使用 pandas 和 SciPy 计算偏度、峰度。
8. 判断高峰度是否由少数异常数据造成。
9. 结合均值、中位数和分位数解释收益分布。
10. 完成多股票收益分布形状分析表。

今日核心问题：

> 一只股票的大涨和大跌是否对称，极端行情是否比正态分布预计得更加频繁？

---

## 二、为什么研究分布形状

均值和中位数描述中心，标准差描述整体离散程度，分位数描述尾部位置，但它们仍不能完整回答：

- 极端收益主要发生在左侧还是右侧；
- 左右尾部是否对称；
- 极端涨跌是否比正态分布更加频繁；
- 两只均值、标准差接近的股票是否具有相同风险结构。

因此需要研究偏度和峰度。

---

## 三、正态分布作为参考

正态分布具有：

- 左右对称；
- 均值、中位数和众数相同；
- 偏度为 0；
- 普通峰度为 3；
- 超额峰度为 0。

理论覆盖比例：

| 区间 | 理论比例 |
|---|---:|
| 均值上下 1 个标准差 | 约 68.27% |
| 均值上下 2 个标准差 | 约 95.45% |
| 均值上下 3 个标准差 | 约 99.73% |

因此正态分布下，落在 3 倍标准差之外的比例约为 0.27%。真实股票收益通常远高于这一比例。

---

## 四、偏度

总体偏度的一种表达：

$$
\gamma_1=E\left[\left(\frac{X-\mu}{\sigma}\right)^3\right]
$$

三次方保留离差方向：

- 负离差三次方仍为负；
- 正离差三次方仍为正；
- 大幅偏离被显著放大。

因此偏度可以判断哪一侧尾部更长或更重。

---

## 五、正偏分布

正偏也称右偏，通常表现为：

- 右侧尾部较长；
- 存在少数较大的正收益；
- 均值通常高于中位数；
- 偏度大于 0。

示例：

```text
-2%、-1%、0%、0%、1%、2%、10%
```

金融含义可能是：

- 大多数时间收益普通；
- 偶尔出现大幅上涨；
- 总收益可能依赖少数大盈利日；
- 胜率不一定高。

正偏不代表平均收益一定为正，也不代表策略一定赚钱。

---

## 六、负偏分布

负偏也称左偏，通常表现为：

- 左侧尾部较长；
- 存在少数严重负收益；
- 均值通常低于中位数；
- 偏度小于 0。

示例：

```text
-10%、-2%、-1%、0%、0%、1%、2%
```

金融含义可能是：

- 大多数时间获得小额收益；
- 胜率可能较高；
- 偶尔发生严重亏损；
- 少数大跌可能吞噬长期收益。

因此高胜率和低日常波动不能排除严重左尾风险。

---

## 七、偏度接近零不等于正态

示例：

```text
-10%、-1%、0%、0%、0%、1%、10%
```

左右尾大致对称，偏度可能接近 0，但存在明显极端收益，峰度会很高。

因此：

```text
偏度描述不对称性
峰度描述极端尾部与集中程度
```

二者不能互相替代。

---

## 八、偏度数值的经验解释

| 偏度绝对值 | 初步解释 |
|---:|---|
| 小于 0.5 | 偏斜较弱 |
| 0.5 至 1.0 | 中等偏斜 |
| 大于 1.0 | 偏斜较明显 |

这些只是经验范围，分析时还需要结合：

- 样本数量；
- 最大、最小收益；
- 1% 和 99% 分位数；
- 直方图和箱线图；
- 具体市场事件。

---

## 九、偏度与均值、中位数

经验上：

$$
\text{正偏：均值}>\text{中位数}
$$

$$
\text{负偏：均值}<\text{中位数}
$$

$$
\text{近似对称：均值}\approx\text{中位数}
$$

但小样本和特殊分布中可能不成立，正式判断仍应计算偏度。

---

## 十、Python 计算偏度

pandas：

```python
returns.skew()
```

SciPy：

```python
from scipy.stats import skew

skewness = skew(
    returns.dropna(),
    bias=False,
)
```

不同库在样本修正、缺失值和小样本算法方面可能略有差异，同一项目应统一口径。

---

## 十一、峰度

峰度的一种表达：

$$
Kurtosis=E\left[\left(\frac{X-\mu}{\sigma}\right)^4\right]
$$

四次方会大幅放大远离均值的观测，例如：

$$
2^4=16
$$

$$
5^4=625
$$

因此峰度对极端值非常敏感。

---

## 十二、普通峰度与超额峰度

正态分布普通峰度为 3。

超额峰度定义：

$$
ExcessKurtosis=Kurtosis-3
$$

因此正态分布的超额峰度为 0。

pandas：

```python
returns.kurt()
returns.kurtosis()
```

通常返回超额峰度。

SciPy：

```python
from scipy.stats import kurtosis

excess_kurtosis = kurtosis(
    returns.dropna(),
    fisher=True,
    bias=False,
)
```

- `fisher=True`：返回超额峰度，正态分布为 0；
- `fisher=False`：返回普通峰度，正态分布为 3。

---

## 十三、尖峰厚尾

高超额峰度通常意味着：

- 大量收益集中在均值附近；
- 中等幅度收益相对较少；
- 极端涨跌出现频率高于正态分布；
- 分布呈现尖峰厚尾。

峰度不应只解释为“峰顶有多尖”，风险管理中更重要的是：

> 分布是否更容易出现距离均值很远的观测值。

---

## 十四、偏度和峰度联合解释

| 偏度 | 超额峰度 | 初步特征 |
|---:|---:|---|
| 接近 0 | 接近 0 | 可能较接近正态分布 |
| 明显为负 | 较高 | 严重左尾和极端下跌风险 |
| 明显为正 | 较高 | 少数极端上涨较明显 |
| 接近 0 | 较高 | 左右对称但双侧厚尾 |
| 明显偏斜 | 较低 | 不对称，但尾部未必很厚 |

---

## 十五、案例解释

### 负偏高峰度

```text
平均日收益：0.04%
中位数：0.09%
偏度：-1.25
超额峰度：8.40
1%分位数：-7.20%
99%分位数：5.10%
```

说明：

- 均值低于中位数；
- 左尾比右尾严重；
- 极端行情频繁；
- 平均收益为正不能掩盖左尾风险。

### 正偏高峰度

```text
平均日收益：0.08%
中位数：0.01%
偏度：1.60
超额峰度：7.20
1%分位数：-4.00%
99%分位数：8.50%
```

说明少数大涨日抬高均值，右尾明显，同时仍存在厚尾。

### 偏度接近零但高峰度

```text
偏度：0.05
超额峰度：10.30
```

说明左右尾大致对称，但双侧极端行情都很频繁，并不接近正态分布。

---

## 十六、标准差倍数事件

Z 分数：

$$
z_t=\frac{r_t-\bar r}{s}
$$

Python：

```python
mean_return = returns.mean()
std_return = returns.std()
z_score = (returns - mean_return) / std_return

count_above_2sigma = (z_score.abs() > 2).sum()
count_above_3sigma = (z_score.abs() > 3).sum()

ratio_above_2sigma = (z_score.abs() > 2).mean()
ratio_above_3sigma = (z_score.abs() > 3).mean()
left_3sigma_ratio = (z_score < -3).mean()
right_3sigma_ratio = (z_score > 3).mean()
```

正态理论比例：

| 条件 | 理论比例 |
|---|---:|
| $|Z|>2$ | 约 4.55% |
| $|Z|>3$ | 约 0.27% |
| $Z<-3$ | 约 0.135% |
| $Z>3$ | 约 0.135% |

极端频率倍数：

$$
ThreeSigmaMultiplier=\frac{\text{实际 }|Z|>3\text{ 比例}}{0.27\%}
$$

---

## 十七、真实收益与正态模拟比较

```python
import numpy as np
import pandas as pd

clean = returns.dropna()
rng = np.random.default_rng(42)

normal_sample = pd.Series(
    rng.normal(
        loc=clean.mean(),
        scale=clean.std(ddof=1),
        size=len(clean),
    )
)

comparison = pd.DataFrame({
    "真实收益": [
        clean.mean(), clean.std(), clean.skew(), clean.kurt(),
        clean.min(), clean.max(),
    ],
    "正态模拟": [
        normal_sample.mean(), normal_sample.std(),
        normal_sample.skew(), normal_sample.kurt(),
        normal_sample.min(), normal_sample.max(),
    ],
}, index=["均值", "标准差", "偏度", "超额峰度", "最小值", "最大值"])
```

通常真实收益会表现出更高峰度和更严重极端值。

---

## 十八、直方图与 Q-Q 图

直方图：

```python
import matplotlib.pyplot as plt

clean = returns.dropna()
plt.figure(figsize=(9, 5))
plt.hist(clean, bins=50)
plt.xlabel("Daily Return")
plt.ylabel("Frequency")
plt.title("Daily Return Distribution")
plt.show()
```

Q-Q 图：

```python
from scipy import stats

plt.figure(figsize=(7, 6))
stats.probplot(clean, dist="norm", plot=plt)
plt.title("Normal Q-Q Plot")
plt.show()
```

Q-Q 图观察：

- 左端向下偏离：左尾更厚；
- 右端向上偏离：右尾更厚；
- 两端同时明显偏离：双侧厚尾；
- 整体弯曲：可能存在偏度。

---

## 十九、正态性检验简介

Jarque-Bera 检验同时利用偏度和峰度：

```python
from scipy.stats import jarque_bera

result = jarque_bera(returns.dropna())
print(result.statistic)
print(result.pvalue)
```

原假设通常是数据来自正态分布。p 值很小表示有证据拒绝正态性，但大样本中很小的偏离也可能显著，因此不能只看 p 值，还应结合偏度、峰度、Q-Q 图和金融意义。

---

## 二十、多股票分布形状统计

```python
shape_stats = (
    df.groupby("code")["return"]
      .agg(
          sample_count="count",
          mean_return="mean",
          median_return="median",
          daily_volatility="std",
          skewness="skew",
          excess_kurtosis="kurt",
          min_return="min",
          max_return="max",
      )
)

shape_stats["q01"] = df.groupby("code")["return"].quantile(0.01)
shape_stats["q99"] = df.groupby("code")["return"].quantile(0.99)
shape_stats["mean_median_diff"] = (
    shape_stats["mean_return"] - shape_stats["median_return"]
)
```

---

## 二十一、可复用函数

```python
import numpy as np
import pandas as pd


def calculate_distribution_shape(
    df: pd.DataFrame,
    code_col: str = "code",
    return_col: str = "return",
) -> pd.DataFrame:
    """按股票计算偏度、峰度和极端收益频率。"""
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
        median_return="median",
        daily_volatility="std",
        skewness="skew",
        excess_kurtosis="kurt",
        min_return="min",
        max_return="max",
    )

    result["q01"] = grouped.quantile(0.01)
    result["q05"] = grouped.quantile(0.05)
    result["q95"] = grouped.quantile(0.95)
    result["q99"] = grouped.quantile(0.99)
    result["mean_median_diff"] = (
        result["mean_return"] - result["median_return"]
    )

    def sigma_frequency(series: pd.Series) -> pd.Series:
        clean = series.dropna()
        if len(clean) < 3:
            return pd.Series({
                "two_sigma_ratio": np.nan,
                "three_sigma_ratio": np.nan,
                "left_three_sigma_ratio": np.nan,
                "right_three_sigma_ratio": np.nan,
            })

        std_value = clean.std(ddof=1)
        if std_value == 0:
            return pd.Series({
                "two_sigma_ratio": 0.0,
                "three_sigma_ratio": 0.0,
                "left_three_sigma_ratio": 0.0,
                "right_three_sigma_ratio": 0.0,
            })

        z_score = (clean - clean.mean()) / std_value
        return pd.Series({
            "two_sigma_ratio": (z_score.abs() > 2).mean(),
            "three_sigma_ratio": (z_score.abs() > 3).mean(),
            "left_three_sigma_ratio": (z_score < -3).mean(),
            "right_three_sigma_ratio": (z_score > 3).mean(),
        })

    result = result.join(grouped.apply(sigma_frequency).unstack())
    result["three_sigma_normal_multiple"] = (
        result["three_sigma_ratio"] / 0.0027
    )

    return result.reset_index()
```

---

## 二十二、滚动偏度与峰度

```python
df = df.sort_values(["code", "date"])

df["skewness_60d"] = (
    df.groupby("code")["return"]
      .rolling(60)
      .skew()
      .reset_index(level=0, drop=True)
)

df["kurtosis_60d"] = (
    df.groupby("code")["return"]
      .rolling(60)
      .kurt()
      .reset_index(level=0, drop=True)
)
```

短窗口中的偏度和峰度非常不稳定，一个极端观测就可能主导结果。长期研究应使用更长样本，并报告样本数量。

---

## 二十三、极端值敏感性实验

```python
import pandas as pd

base_returns = pd.Series([-0.01, -0.005, 0.00, 0.005, 0.01])
positive_outlier = pd.concat(
    [base_returns, pd.Series([0.10])],
    ignore_index=True,
)
negative_outlier = pd.concat(
    [base_returns, pd.Series([-0.10])],
    ignore_index=True,
)

comparison = pd.DataFrame({
    "原始": [base_returns.skew(), base_returns.kurt()],
    "加入正异常": [positive_outlier.skew(), positive_outlier.kurt()],
    "加入负异常": [negative_outlier.skew(), negative_outlier.kurt()],
}, index=["偏度", "超额峰度"])
```

加入正异常后偏度为正，加入负异常后偏度为负，两种异常都会提高峰度。

---

## 二十四、A 股特殊问题

1. 涨跌停制度会使收益集中在特定边界附近。
2. 价格限制会截断单日收益分布，连续跌停可能把冲击分散到多个交易日。
3. 长期停牌后复牌会显著影响偏度和峰度。
4. 复权错误可能制造虚假极端收益。
5. 新股上市阶段与正常交易阶段不宜直接混合。
6. ST 状态会随时间变化，历史规则必须使用历史状态字段判断。

---

## 二十五、实践任务

### 任务一：分布形状表

| 股票代码 | 样本数 | 均值 | 中位数 | 偏度 | 超额峰度 |
|---|---:|---:|---:|---:|---:|

### 任务二：尾部对比

| 股票代码 | 1%分位数 | 5%分位数 | 95%分位数 | 99%分位数 | 尾部方向 |
|---|---:|---:|---:|---:|---|

### 任务三：标准差事件频率

| 股票代码 | $|Z|>2$ 比例 | $|Z|>3$ 比例 | 左 3σ 比例 | 右 3σ 比例 |
|---|---:|---:|---:|---:|

### 任务四：极端值敏感性

比较原始偏度峰度、删除最大值、删除最小值和删除两端后的结果。

### 任务五：绘图

至少绘制：

- 收益率直方图；
- 正态 Q-Q 图；
- 收益率时间序列；
- 60 日滚动偏度；
- 60 日滚动峰度。

---

## 二十六、常见错误

1. 偏度为正就认为收益高。
2. 负偏股票一定会亏损。
3. 偏度接近 0 就认为正态。
4. 峰度高就认为每天波动都大。
5. 混淆普通峰度和超额峰度。
6. 一个极端值后直接认定长期厚尾。
7. 只看正态性检验 p 值。
8. 使用过短窗口解释滚动偏度。
9. 不同样本区间直接比较偏度和峰度。

---

## 二十七、数学练习

某股票 1000 个交易日中，有 15 天位于 3 倍标准差范围之外：

$$
\frac{15}{1000}=1.5\%
$$

与正态理论值 0.27% 比较：

$$
\frac{1.5\%}{0.27\%}\approx5.56
$$

说明 3 倍标准差事件频率约为正态理论的 5.56 倍。

---

## 二十八、自测题

1. 偏度衡量什么？
2. 负偏意味着什么？
3. 正偏意味着什么？
4. 偏度为 0 是否表示正态分布？
5. pandas 的 `kurt()` 通常返回什么？
6. 正态分布超额峰度是多少？
7. 高峰度通常意味着什么？
8. 为什么股票收益不适合完全依赖正态分布？
9. 为什么偏度和峰度需要较大样本？
10. 高峰度数据能否直接删除极端值？

---

## 二十九、今日验收标准

- 能正确解释偏度方向；
- 能说明三次方为什么保留方向；
- 能区分正偏、负偏和近似对称分布；
- 能解释普通峰度和超额峰度；
- 能解释尖峰厚尾；
- 能计算偏度、峰度和 2σ、3σ 事件比例；
- 能比较实际极端频率与正态理论；
- 能绘制直方图和 Q-Q 图；
- 能检查偏度峰度对极端值的敏感性；
- 能完成多股票分布形状比较表。

---

## 三十、今日最终产出

```text
notebooks/week07_day04_skewness_kurtosis.ipynb
src/statistics.py
```

建议实现：

```python
calculate_distribution_shape()
shape_without_extremes()
```

今日最重要的结论：

> 偏度告诉我们极端收益主要出现在左侧还是右侧，峰度告诉我们极端行情是否比正态分布更加频繁。偏度接近 0 不代表正态，高峰度也不一定意味着每天都剧烈波动。
