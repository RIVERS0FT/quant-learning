# 第七周第七天：多股票收益分布分析阶段项目

## 一、今日课程定位

前六天分别学习了：

| 天数 | 核心内容 |
|---:|---|
| 第一天 | 均值、中位数与收益中心 |
| 第二天 | 方差、标准差与年化波动率 |
| 第三天 | 分位数、IQR 与尾部风险 |
| 第四天 | 偏度、峰度与尖峰厚尾 |
| 第五天 | 协方差、相关系数与滚动相关性 |
| 第六天 | 异常收益识别与数据质量检查 |

今天不重点学习新的统计量，而是完成一套完整研究流程：

```text
提出问题
→ 准备数据
→ 检查质量
→ 计算指标
→ 绘制图表
→ 解释结果
→ 核验异常
→ 得出结论
→ 记录局限
→ 输出研究报告
```

今日核心问题：

> 如何将一组统计指标组织成一份可信、可复现、能够支持投资研究的收益分布分析报告？

---

## 二、今日学习目标

完成本课程后，应能够：

1. 独立设计一个多股票收益分布研究项目。
2. 明确研究问题、样本范围和数据口径。
3. 建立统一的数据质量检查流程。
4. 生成多股票描述统计汇总表。
5. 分析收益中心、波动率和尾部风险。
6. 判断收益分布是否存在偏度和厚尾。
7. 比较股票之间的相关性和分散化效果。
8. 建立异常收益核验表。
9. 区分统计事实、研究推断和投资观点。
10. 编写结构完整的量化研究报告。
11. 将研究代码拆分为可复用函数。
12. 为关键统计函数编写基础单元测试。
13. 保证研究结果可复现和可审计。

---

## 三、阶段项目任务

选择 5 至 10 只 A 股股票，使用至少一年日线数据，完成：

```text
多股票收益分布与风险特征分析报告
```

股票尽量覆盖不同类型，例如：

- 银行或保险；
- 消费；
- 医药；
- 科技；
- 周期；
- 高股息；
- 小市值成长；
- 宽基指数 ETF。

目的不是预测未来，而是比较不同资产的历史收益分布和风险结构。

---

## 四、研究问题

### 收益中心

- 哪只股票平均日收益率最高？
- 哪只股票中位数最高？
- 哪只股票均值明显高于中位数？
- 高平均收益是否由少数极端上涨贡献？

### 波动水平

- 哪只股票日波动率最高？
- 哪只股票年化波动率最低？
- 最近 20 日波动率是否高于全样本水平？
- 哪些股票存在明显波动率聚集？

### 尾部风险

- 哪只股票 5% 分位数最低？
- 哪只股票最差 5% 交易日平均跌幅最大？
- 哪只股票 IQR 最大？
- 哪只股票左尾风险最严重？

### 分布形状

- 哪只股票负偏最明显？
- 哪只股票正偏最明显？
- 哪只股票超额峰度最高？
- 哪些股票 3 倍标准差事件远高于正态理论值？

### 相关性

- 哪两只股票相关性最高？
- 哪两只股票相关性最低？
- 哪些股票可能提供更好的分散效果？
- 最近 60 日相关性是否发生明显变化？
- 市场下跌时相关性是否上升？

### 数据质量

- 哪些极端收益是真实市场行情？
- 哪些记录与除权或复权有关？
- 哪些记录存在价格字段错误？
- 数据处理前后统计结果发生了什么变化？

---

## 五、研究假设

正式计算前，可以提出可检验的初步假设，例如：

1. 同行业股票的收益相关性通常高于不同行业股票。
2. 小市值成长股的波动率和峰度可能高于大盘蓝筹股。
3. 多数股票收益率不服从正态分布。
4. 市场下跌时期，不同股票之间的相关性可能上升。
5. 部分高峰度来自真实涨跌停，部分可能来自复权或数据错误。

假设不是预设结论，最终判断必须由数据支持。

---

## 六、数据口径

### 最低字段

```text
date
code
close
```

建议字段：

```text
open
high
low
previous_close
volume
amount
adjustment_factor
is_trading
is_suspended
up_limit_price
down_limit_price
industry
listing_date
```

### 时间范围

最低建议：

```text
至少252个有效日收益率
```

更推荐 2 至 3 年数据。样本过短时，均值、1% 分位数、偏度、峰度和相关性都不稳定。

### 收益率定义

简单收益率：

$$
r_t=\frac{P_t}{P_{t-1}}-1
$$

对数收益率：

$$
\ell_t=\ln\left(\frac{P_t}{P_{t-1}}\right)
$$

本项目主要使用简单收益率，并明确：

- 原始价格或复权价格；
- 前复权或后复权；
- 是否考虑现金分红；
- 停牌日处理方式；
- 无效价格处理方式。

---

## 七、项目目录结构

```text
quant-research/
├── data/
│   ├── raw/
│   ├── processed/
│   └── research/
├── notebooks/
│   └── week07_day07_return_distribution_project.ipynb
├── src/
│   ├── returns.py
│   ├── statistics.py
│   ├── data_quality.py
│   └── visualization.py
├── tests/
│   ├── test_returns.py
│   ├── test_statistics.py
│   └── test_data_quality.py
├── reports/
│   ├── figures/
│   ├── tables/
│   └── week07_return_distribution_report.md
└── README.md
```

---

## 八、研究配置

将研究参数集中管理，不要分散在 Notebook 各处：

```python
STOCK_CODES = [
    "000001",
    "000002",
    "600000",
    "600519",
    "300750",
]

START_DATE = "2024-01-01"
END_DATE = "2025-12-31"
ANNUALIZATION_FACTOR = 252
ROLLING_VOL_WINDOW = 20
ROLLING_CORR_WINDOW = 60
```

记录：

```text
股票代码
股票名称
所属行业
开始日期
结束日期
价格口径
收益率类型
数据来源
数据版本
```

---

## 九、数据读取与字段检查

```python
from pathlib import Path
import numpy as np
import pandas as pd

DATA_PATH = Path("data/processed/daily_prices.parquet")
df = pd.read_parquet(DATA_PATH)

required_columns = {"date", "code", "close"}
missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(f"缺少必要字段：{sorted(missing_columns)}")

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["code"] = df["code"].astype(str).str.zfill(6)
df["close"] = pd.to_numeric(df["close"], errors="coerce")

df = df.loc[
    df["code"].isin(STOCK_CODES)
    & df["date"].between(START_DATE, END_DATE)
].copy()
```

---

## 十、数据质量检查

### 重复记录

```python
duplicate_mask = df.duplicated(
    subset=["date", "code"],
    keep=False,
)
duplicate_rows = df.loc[duplicate_mask]
```

存在重复时不能直接继续转换宽表。

### 非正价格

```python
df["invalid_close"] = (
    df["close"].isna()
    | (df["close"] <= 0)
)
```

### OHLC 关系

```python
df["invalid_high_low"] = (
    (df["high"] < df["low"])
    | (df["high"] < df["open"])
    | (df["high"] < df["close"])
    | (df["low"] > df["open"])
    | (df["low"] > df["close"])
)
```

### 样本范围

```python
sample_summary = (
    df.groupby("code")
      .agg(
          start_date=("date", "min"),
          end_date=("date", "max"),
          row_count=("date", "size"),
          valid_close_count=("close", "count"),
      )
      .reset_index()
)
```

---

## 十一、计算收益率

```python
df = df.sort_values(["code", "date"])
df["previous_close"] = df.groupby("code")["close"].shift(1)
df["return"] = df["close"] / df["previous_close"] - 1

df["return"] = df["return"].replace(
    [np.inf, -np.inf],
    np.nan,
)
```

不要立即删除全部缺失收益，应先检查是否为每只股票第一条记录、上市较晚、停牌、价格缺失或数据错误。

---

## 十二、基础描述统计表

推荐字段：

| 股票 | 样本数 | 平均收益 | 中位数 | 日波动率 | 年化波动率 | 最小值 | 最大值 |
|---|---:|---:|---:|---:|---:|---:|---:|

```python
basic_stats = (
    df.groupby("code")["return"]
      .agg(
          sample_count="count",
          mean_return="mean",
          median_return="median",
          daily_volatility="std",
          min_return="min",
          max_return="max",
      )
)

basic_stats["annual_volatility"] = (
    basic_stats["daily_volatility"]
    * np.sqrt(ANNUALIZATION_FACTOR)
)

basic_stats["mean_median_diff"] = (
    basic_stats["mean_return"]
    - basic_stats["median_return"]
)
```

解释时不能只按平均收益排序，还要观察中位数、波动率、极端值和样本数量。

---

## 十三、分位数与尾部风险表

```python
quantile_stats = (
    df.groupby("code")["return"]
      .quantile([0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99])
      .unstack()
)

quantile_stats.columns = [
    "q01", "q05", "q25", "q50", "q75", "q95", "q99"
]

quantile_stats["iqr"] = (
    quantile_stats["q75"] - quantile_stats["q25"]
)
quantile_stats["range_90"] = (
    quantile_stats["q95"] - quantile_stats["q05"]
)
quantile_stats["range_98"] = (
    quantile_stats["q99"] - quantile_stats["q01"]
)
quantile_stats["tail_asymmetry"] = (
    quantile_stats["q99"] + quantile_stats["q01"]
)
```

尾部不对称指标仅供辅助，正式判断还应结合偏度。

---

## 十四、最差与最好 5% 交易日

$$
LeftTailMean_{5\%}=E[r\mid r\le Q_{0.05}]
$$

```python
import numpy as np
import pandas as pd


def calculate_tail_means(
    series: pd.Series,
) -> pd.Series:
    clean = series.dropna()
    if clean.empty:
        return pd.Series({
            "left_tail_mean_5pct": np.nan,
            "right_tail_mean_5pct": np.nan,
        })

    q05 = clean.quantile(0.05)
    q95 = clean.quantile(0.95)

    return pd.Series({
        "left_tail_mean_5pct": clean.loc[clean <= q05].mean(),
        "right_tail_mean_5pct": clean.loc[clean >= q95].mean(),
    })


tail_means = (
    df.groupby("code")["return"]
      .apply(calculate_tail_means)
      .unstack()
)
```

5% 分位数描述进入尾部的阈值，最差 5% 平均收益描述进入尾部后的平均损失。

---

## 十五、偏度、峰度与极端频率表

```python
shape_stats = (
    df.groupby("code")["return"]
      .agg(
          skewness="skew",
          excess_kurtosis="kurt",
      )
)
```

极端频率：

```python
def calculate_sigma_frequency(
    series: pd.Series,
) -> pd.Series:
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
```

正态理论：

```text
|Z| > 2：约4.55%
|Z| > 3：约0.27%
```

实际 3σ 比例相对正态理论倍数：

$$
Multiple_{3\sigma}=\frac{\text{实际 }|Z|>3\text{ 比例}}{0.0027}
$$

---

## 十六、上涨、下跌和零收益比例

```python
direction_stats = (
    df.groupby("code")["return"]
      .agg(
          positive_ratio=lambda x: (x.dropna() > 0).mean(),
          negative_ratio=lambda x: (x.dropna() < 0).mean(),
          zero_ratio=lambda x: (x.dropna() == 0).mean(),
      )
)

direction_stats["ratio_sum"] = (
    direction_stats["positive_ratio"]
    + direction_stats["negative_ratio"]
    + direction_stats["zero_ratio"]
)
```

三项之和应接近 100%。上涨比例高不代表收益一定好，还需要结合平均涨跌幅和尾部风险。

---

## 十七、滚动波动率

```python
df = df.sort_values(["code", "date"])

df["volatility_20d"] = (
    df.groupby("code")["return"]
      .rolling(window=20, min_periods=15)
      .std()
      .reset_index(level=0, drop=True)
)

df["volatility_60d"] = (
    df.groupby("code")["return"]
      .rolling(window=60, min_periods=40)
      .std()
      .reset_index(level=0, drop=True)
)

df["annual_volatility_20d"] = (
    df["volatility_20d"] * np.sqrt(252)
)
df["annual_volatility_60d"] = (
    df["volatility_60d"] * np.sqrt(252)
)
```

提取最新值，与全样本波动率比较：

```python
latest_volatility = (
    df.sort_values("date")
      .groupby("code")
      .tail(1)[[
          "code",
          "date",
          "annual_volatility_20d",
          "annual_volatility_60d",
      ]]
)
```

若近期波动率明显高于全样本水平，说明当前风险环境可能已经变化。

---

## 十八、收益率宽表和相关矩阵

```python
if df.duplicated(["date", "code"]).any():
    raise ValueError("存在重复的日期与股票代码组合")

returns_wide = df.pivot(
    index="date",
    columns="code",
    values="return",
).sort_index()

correlation_matrix = returns_wide.corr(
    method="pearson",
    min_periods=120,
)

overlap_counts = (
    returns_wide.notna().astype(int).T
    @ returns_wide.notna().astype(int)
)
```

相关矩阵必须和共同样本数一起解释。

---

## 十九、提取最高和最低相关组合

```python
import numpy as np
import pandas as pd


def extract_correlation_pairs(
    correlation_matrix: pd.DataFrame,
    overlap_counts: pd.DataFrame,
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
    pairs["overlap_count"] = [
        overlap_counts.loc[x, y]
        for x, y in zip(pairs["stock_x"], pairs["stock_y"])
    ]
    return pairs.sort_values("correlation", ascending=False)
```

分别保留相关性最高 3 组、最低 3 组，并检查样本数量和行业关系。

---

## 二十、滚动相关性

```python
def rolling_correlation(
    returns_wide: pd.DataFrame,
    stock_x: str,
    stock_y: str,
    window: int = 60,
    min_periods: int = 40,
) -> pd.Series:
    return (
        returns_wide[stock_x]
        .rolling(window=window, min_periods=min_periods)
        .corr(returns_wide[stock_y])
    )
```

分析：

- 当前相关性是否高于长期平均；
- 是否经常穿越 0；
- 市场剧烈波动时是否上升；
- 低相关是否只存在于短暂阶段。

---

## 二十一、异常收益报告

至少计算：

```text
全样本Z分数
60日滞后滚动Z分数
稳健Z分数
IQR异常标志
横截面Z分数
```

筛选候选：

```python
outlier_candidates = df.loc[
    (df["z_score"].abs() > 3)
    | (df["rolling_z_score"].abs() > 3)
    | (df["modified_z_score"].abs() > 3.5)
    | df["is_iqr_outlier"]
].copy()
```

每条记录最终处理只能选择：

```text
KEEP
KEEP_WITH_FLAG
CORRECT
EXCLUDE
REVIEW
```

---

## 二十二、原始数据与研究数据对比

保留：

```text
raw_return
research_return
```

不要覆盖原始收益率。

比较处理前后的：

- 均值；
- 标准差；
- 偏度；
- 峰度；
- 1% 和 99% 分位数；
- 最大回撤。

重点判断：

- 修正错误记录后峰度是否下降；
- 真实极端行情是否仍保留；
- 数据清洗是否不合理地美化收益分布。

---

## 二十三、统一统计汇总表

```python
summary_table = (
    basic_stats
    .join(quantile_stats)
    .join(tail_means)
    .join(shape_stats)
    .join(direction_stats)
)
```

推荐核心字段：

```text
sample_count
mean_return
median_return
mean_median_diff
daily_volatility
annual_volatility
q01
q05
q95
q99
iqr
left_tail_mean_5pct
right_tail_mean_5pct
skewness
excess_kurtosis
three_sigma_ratio
positive_ratio
negative_ratio
```

---

## 二十四、单只股票的解释顺序

1. 样本区间和有效观测数量；
2. 均值与中位数；
3. 日波动率与年化波动率；
4. 5% 分位数与最差 5% 平均收益；
5. 偏度与峰度；
6. 当前滚动波动率；
7. 与其他股票的相关性；
8. 极端收益的数据质量核验。

这种顺序可以避免依赖单一指标。

---

## 二十五、必须绘制的图表

### 1. 累计净值曲线

$$
NV_t=\prod_{i=1}^{t}(1+r_i)
$$

```python
net_value = (1 + returns_wide).cumprod()
```

### 2. 收益率时间序列

观察极端涨跌、停牌断点和波动率聚集。

### 3. 收益率直方图

观察中心集中、左右尾和尖峰厚尾。

### 4. 箱线图

比较中位数、IQR、尾部和异常候选。

### 5. 20 日滚动年化波动率

观察近期风险状态。

### 6. 相关系数矩阵

观察高相关股票群和潜在分散组合。

### 7. 60 日滚动相关系数

观察相关性的时变特征。

可选图表：Q-Q 图、滚动偏度、滚动峰度、散点图、异常数量图和清洗前后对比图。

---

## 二十六、报告结构

### 1. 执行摘要

总结样本范围、主要收益特征、主要风险、相关性发现、关键数据问题和限制。

### 2. 研究目的

说明报告希望回答的问题。

### 3. 数据与方法

说明数据来源、股票范围、日期、复权方式、收益定义、停牌处理、异常处理、年化因子和滚动窗口。

### 4. 基础描述统计

展示均值、中位数、标准差、年化波动率和极值。

### 5. 分位数与尾部风险

展示 1%、5%、95%、99% 分位数、IQR 和尾部均值。

### 6. 偏度与峰度

展示偏度、超额峰度和 3σ 事件比例。

### 7. 相关性分析

展示相关矩阵、共同样本数、最高最低组合和滚动相关性。

### 8. 异常收益与数据质量

展示真实极端行情、公司行为、疑似错误和处理方式。

### 9. 综合结论

逐一回答研究问题。

### 10. 局限与下一步

说明历史样本、方法和数据不能解决的问题。

---

## 二十七、如何写统计结论

完整结论应包含：

```text
研究对象
+ 样本区间
+ 指标名称
+ 具体数值
+ 比较基准
+ 金融解释
+ 限制条件
```

示例：

```text
股票000001在2024年1月至2025年12月期间的平均日收益率为0.07%，中位数为0.02%，均值高于中位数0.05个百分点。

删除最大单日收益后，平均收益率下降至0.04%，说明原始均值部分由少数大涨日推动。

该分析仅基于历史样本，尚未控制市场和行业共同因素，不能直接解释为未来超额收益能力。
```

不合格结论包括“股票 A 很好”“波动率高所以不能买”“相关性最低所以组合一定安全”。

---

## 二十八、综合判断框架

### 收益中心

- 平均收益；
- 中位数；
- 上涨比例。

### 日常波动

- 日标准差；
- 年化波动率；
- IQR。

### 尾部风险

- 1% 和 5% 分位数；
- 最差 5% 平均收益；
- 偏度；
- 最大单日跌幅。

### 极端风险

- 超额峰度；
- 3σ 事件比例；
- IQR 异常数量；
- 真实涨跌停和复牌记录。

不能简单把这些指标相加形成“好股票分数”。当前重点是理解每个维度描述的风险不同。

---

## 二十九、单元测试

收益率测试：

```python
import numpy as np
import pandas as pd


def test_simple_returns():
    prices = pd.Series([100.0, 110.0, 99.0])
    returns = prices.pct_change()

    assert np.isnan(returns.iloc[0])
    assert np.isclose(returns.iloc[1], 0.10)
    assert np.isclose(returns.iloc[2], -0.10)
```

均值中位数测试：

```python
def test_center_statistics():
    returns = pd.Series([-0.01, 0.00, 0.01])
    assert np.isclose(returns.mean(), 0.0)
    assert np.isclose(returns.median(), 0.0)
```

样本标准差测试：

```python
def test_sample_std():
    returns = pd.Series([-0.01, 0.00, 0.01])
    expected = np.std(returns, ddof=1)
    assert np.isclose(returns.std(), expected)
```

IQR 异常测试：

```python
def test_iqr_outlier():
    returns = pd.Series([
        -0.01, -0.005, 0.00, 0.005, 0.01, 0.20
    ])
    q1 = returns.quantile(0.25)
    q3 = returns.quantile(0.75)
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    assert returns.iloc[-1] > upper
```

完全正相关测试：

```python
def test_perfect_positive_correlation():
    x = pd.Series([-0.02, -0.01, 0.00, 0.01, 0.02])
    y = x * 2
    assert np.isclose(x.corr(y), 1.0)
```

---

## 三十、代码组织

### `returns.py`

```text
calculate_simple_returns()
calculate_log_returns()
calculate_cumulative_returns()
```

### `statistics.py`

```text
calculate_center_statistics()
calculate_volatility_statistics()
calculate_quantile_statistics()
calculate_distribution_shape()
calculate_dependency_statistics()
```

### `data_quality.py`

```text
check_duplicate_rows()
check_price_relationships()
calculate_z_score()
calculate_modified_z_score()
add_iqr_flags()
build_return_outlier_report()
```

### `visualization.py`

```text
plot_return_series()
plot_return_histogram()
plot_boxplot()
plot_rolling_volatility()
plot_correlation_matrix()
plot_rolling_correlation()
```

Notebook 负责组织流程和展示结果，不承担全部计算逻辑。

---

## 三十一、主流程函数

```python
def run_week07_analysis(
    df: pd.DataFrame,
) -> dict[str, object]:
    data = df.copy()
    data = data.sort_values(["code", "date"])
    data["return"] = data.groupby("code")["close"].pct_change()

    basic_stats = calculate_center_statistics(data)
    volatility_stats = calculate_volatility_statistics(data)
    quantile_stats = calculate_quantile_statistics(data)
    shape_stats = calculate_distribution_shape(data)
    dependency_stats = calculate_dependency_statistics(data)
    outlier_report = build_return_outlier_report(data)

    return {
        "data": data,
        "basic_stats": basic_stats,
        "volatility_stats": volatility_stats,
        "quantile_stats": quantile_stats,
        "shape_stats": shape_stats,
        "dependency_stats": dependency_stats,
        "outlier_report": outlier_report,
    }
```

函数应输入明确、输出明确、不依赖隐藏全局变量、不修改原始输入，并在缺失字段时给出清晰错误。

---

## 三十二、可复现性检查

项目完成后回答：

1. 其他人能否找到原始数据？
2. 是否记录数据下载时间和版本？
3. 是否记录复权口径？
4. 是否记录股票选择规则？
5. 是否固定分析日期？
6. 是否保留异常处理原因？
7. 是否能从原始数据重新生成全部结果？
8. 是否使用未来信息清洗历史数据？
9. 是否修改原始数据文件？
10. 是否保存代码版本？

建议记录：

```text
Python版本
pandas版本
NumPy版本
SciPy版本
项目Git提交编号
数据版本
运行日期
```

---

## 三十三、阶段项目常见错误

1. 先看结果，再选择股票，形成选择偏差。
2. 不同股票使用不同时间区间。
3. 只报告均值和标准差，忽略尾部和厚尾。
4. 把统计描述直接写成投资建议。
5. 忽略相关系数的共同样本数量。
6. 删除全部异常收益，低估真实风险。
7. 使用未复权价格计算长期投资收益。
8. 停牌日全部填 0。
9. 图表很多但没有回答研究问题。
10. 只写结论，不写方法和限制。

---

## 三十四、报告必须说明的局限

至少包括：

- 历史收益不代表未来收益；
- 样本区间影响统计结果；
- 偏度和峰度对极端值敏感；
- 分位数不是最大损失；
- 相关性不等于因果关系；
- 相关性会随市场状态变化；
- 涨跌停和停牌影响收益分布；
- 数据源可能存在缺失和修订；
- 未控制市场、行业和风格因子；
- 未考虑交易成本和流动性；
- 报告不是买卖建议。

---

## 三十五、今日实践安排

1. 研究设计：选择股票、时间范围、价格口径和研究问题；
2. 数据检查：字段、重复、价格关系、样本区间和缺失值；
3. 统计计算：中心、波动、分位数、尾部、偏度、峰度和极端频率；
4. 相关分析：宽表、相关矩阵、共同样本数和滚动相关；
5. 异常核验：至少检查 10 条异常记录；
6. 图表和报告：完成执行摘要、核心图表、结论和限制。

---

## 三十六、自测题

1. 为什么不能只按平均收益给股票排名？
2. 为什么 5% 分位数和最差 5% 平均收益要同时计算？
3. 偏度接近 0 是否代表风险低？
4. 为什么相关矩阵要配合共同样本数？
5. 为什么滚动相关性重要？
6. 真实跌停收益应该怎样处理？
7. 为什么不能覆盖原始收益率？
8. 报告为什么必须写局限？

---

## 三十七、今日验收标准

- 明确 5 至 10 只股票的选择规则；
- 使用统一样本区间和收益口径；
- 完成数据质量检查；
- 生成基础统计、分位数尾部、偏度峰度和相关性表；
- 计算滚动波动率和滚动相关性；
- 核验至少 10 条异常收益；
- 绘制至少 7 张核心图表；
- 编写至少 5 条有数据证据的结论；
- 编写研究限制说明；
- 为至少 3 个核心函数编写单元测试；
- 从原始数据重新运行并生成相同结果。

---

## 三十八、今日最终产出

```text
notebooks/week07_day07_return_distribution_project.ipynb
src/statistics.py
src/data_quality.py
reports/figures/
reports/tables/week07_summary_statistics.csv
reports/tables/week07_correlation_matrix.csv
reports/tables/week07_outlier_review.csv
reports/week07_return_distribution_report.md
tests/test_returns.py
tests/test_statistics.py
tests/test_data_quality.py
```

---

## 三十九、第七周总结

1. 均值和中位数描述收益中心，但不能代表未来收益能力。
2. 标准差描述整体波动，同时把上涨和下跌视为不确定性。
3. 分位数描述收益位置，最差 5% 平均收益描述尾部损失严重程度。
4. 偏度描述左右尾不对称，峰度描述极端收益是否频繁。
5. 低相关可能帮助分散风险，但压力时期相关性可能上升。
6. 统计异常不等于数据错误，真实极端行情应保留，错误记录应修正。
7. 量化研究最终成果是一条能够检查、复现和解释的研究证据链。

今日最重要的结论：

> 一份可信的收益分布报告不能只展示统计表，还必须说明数据口径、异常处理、相关性变化、研究限制和复现方法。
