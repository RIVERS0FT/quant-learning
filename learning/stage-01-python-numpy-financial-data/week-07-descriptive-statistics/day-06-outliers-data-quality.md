# 第七周第六天：异常收益识别、Z 分数与数据质量检查

## 一、今日学习目标

完成本课程后，应能够：

1. 区分异常值、极端值和错误数据。
2. 理解异常收益可能来自真实行情或数据问题。
3. 使用 Z 分数识别异常收益候选。
4. 使用 IQR 规则识别异常收益候选。
5. 比较全样本 Z 分数与滚动 Z 分数。
6. 理解均值和标准差对异常值的敏感性。
7. 使用中位数和 MAD 构造稳健异常指标。
8. 结合 A 股涨跌停、停牌、复权和公司行为检查异常收益。
9. 建立异常收益检查表。
10. 为异常数据制定保留、修正、标记和排除规则。
11. 避免未经核验直接删除极端收益。
12. 完成可复用的数据质量检查模块。

今日核心问题：

> 一个极端收益究竟是真实市场风险，还是行情数据出现了错误？

---

## 二、异常收益是什么

异常收益是相对某只股票正常收益分布而言，明显偏离大多数观测的收益率。

例如一只股票平时日收益大多位于 -2% 到 2%，某天出现 -18%，该记录需要重点检查。

正确流程：

```text
发现异常候选
→ 检查原始价格
→ 检查日期和排序
→ 检查交易状态
→ 检查复权与公司行为
→ 判断真实行情还是数据错误
→ 保留、修正、标记、排除或继续核验
```

统计异常不等于错误数据。

---

## 三、异常值、极端值与错误数据

### 异常值

从统计分布看，明显偏离大多数数据的观测。例如 Z 分数为 -4.2。

### 极端值

幅度很大的真实观测，例如真实跌停、重大利空、复牌跳跃或市场危机。极端值通常应保留在风险分析中。

### 错误数据

由采集、存储、计算或处理问题造成的不真实记录，例如：

- 收盘价小数点错位；
- 前收盘价来自其他股票；
- 同一日期重复记录；
- 日期错位；
- 复权因子方向错误；
- 缺失价格被填为 0；
- 股票代码映射错误。

错误数据需要修正或排除，并保留完整记录。

---

## 四、异常收益的两大来源

### 真实市场事件

- 涨停、跌停；
- 重大公告；
- 业绩预告变化；
- 监管调查；
- 重组和控股权变化；
- 行业政策冲击；
- 系统性市场大跌；
- 停牌后复牌；
- 新股上市初期；
- 退市整理期。

### 数据质量问题

- 原始价格错误；
- 复权因子错误；
- 日期重复或缺失；
- 股票代码错配；
- 停牌日处理错误；
- 单位错误；
- 前收盘价错位；
- OHLC 字段关系错误；
- 不同数据源定义不一致。

一个错误价格可能同时扭曲收益率、波动率、偏度、峰度、分位数、最大回撤、因子值和回测结果。

---

## 五、异常检测方法的定位

异常检测方法只能回答：

> 哪些记录值得进一步检查？

不能直接回答：

> 哪些记录一定是错误的？

本课程使用：

1. 业务规则法；
2. Z 分数法；
3. 滚动 Z 分数法；
4. IQR 法；
5. 稳健 Z 分数法；
6. 横截面异常分析。

统计方法负责发现候选，业务规则和原始数据负责最终核验。

---

## 六、基础业务规则检查

正常日线数据通常应满足：

```text
high >= open
high >= close
high >= low
low <= open
low <= close
open > 0
high > 0
low > 0
close > 0
volume >= 0
amount >= 0
```

Python：

```python
price_check = df.copy()

price_check["invalid_non_positive_price"] = (
    (price_check["open"] <= 0)
    | (price_check["high"] <= 0)
    | (price_check["low"] <= 0)
    | (price_check["close"] <= 0)
)

price_check["invalid_high"] = (
    (price_check["high"] < price_check["open"])
    | (price_check["high"] < price_check["close"])
    | (price_check["high"] < price_check["low"])
)

price_check["invalid_low"] = (
    (price_check["low"] > price_check["open"])
    | (price_check["low"] > price_check["close"])
    | (price_check["low"] > price_check["high"])
)

price_check["invalid_volume"] = price_check["volume"] < 0
price_check["invalid_amount"] = price_check["amount"] < 0

price_check["has_basic_price_error"] = price_check[[
    "invalid_non_positive_price",
    "invalid_high",
    "invalid_low",
    "invalid_volume",
    "invalid_amount",
]].any(axis=1)
```

违反 `high >= close` 等基本关系的记录通常高度可疑。

---

## 七、重复记录检查

同一股票同一交易日通常只能有一条日线记录。

```python
duplicate_mask = df.duplicated(
    subset=["date", "code"],
    keep=False,
)

duplicate_rows = df.loc[duplicate_mask].sort_values(
    ["code", "date"]
)
```

不能简单保留第一条或最后一条，应先检查重复行是否完全相同、是否来自多个数据源或重复下载。

---

## 八、收益率计算与反算检查

简单收益率：

$$
r_t=\frac{P_t}{P_{t-1}}-1
$$

必须先按股票代码和日期排序：

```python
df = df.sort_values(["code", "date"])
df["previous_close"] = df.groupby("code")["close"].shift(1)
df["return"] = df["close"] / df["previous_close"] - 1
```

若数据源提供收益率，可反算核验：

```python
df["calculated_return"] = (
    df["close"] / df["previous_close"] - 1
)
df["return_difference"] = (
    df["source_return"] - df["calculated_return"]
)
df["return_mismatch"] = (
    df["return_difference"].abs() > 1e-6
)
```

检查时要确认收益率单位、前收盘价定义、复权口径和小数精度。

---

## 九、Z 分数

Z 分数表示某个收益距离样本均值多少个标准差：

$$
z_t=\frac{r_t-\bar r}{s}
$$

例如：

```text
平均日收益率：0.10%
日标准差：2.00%
某日收益率：-7.90%
```

$$
z=\frac{-7.90\%-0.10\%}{2.00\%}=-4
$$

表示该收益位于均值下方 4 个标准差。

经验阈值：

| 条件 | 初步含义 |
|---|---|
| $|z|>2$ | 较少见收益 |
| $|z|>3$ | 极端收益候选 |
| $|z|>4$ | 非常极端，需要重点核验 |

这些不是固定金融规则。

---

## 十、按股票计算 Z 分数

```python
import numpy as np
import pandas as pd


def calculate_z_score(series: pd.Series) -> pd.Series:
    mean_value = series.mean()
    std_value = series.std(ddof=1)

    if pd.isna(std_value) or std_value == 0:
        return pd.Series(
            np.nan,
            index=series.index,
            dtype=float,
        )

    return (series - mean_value) / std_value


df["z_score"] = (
    df.groupby("code")["return"]
      .transform(calculate_z_score)
)
```

不同股票波动水平不同，不能把所有股票混合计算一个均值和标准差。

---

## 十一、全样本 Z 分数的局限

全样本 Z 分数混合不同市场状态。如果一只股票前两年低波动、最近三个月高波动，全样本标准差可能：

- 误判低波动阶段的普通收益；
- 低估当前高波动阶段的异常程度；
- 无法反映风险环境变化。

因此还需要滚动 Z 分数。

---

## 十二、滚动 Z 分数与前视偏差

滚动 Z 分数：

$$
rolling\_z_t=\frac{r_t-rolling\_mean_t}{rolling\_std_t}
$$

若当天收益参与均值和标准差计算，极端收益本身会抬高标准差，降低自身 Z 分数绝对值。

更严格的方法是使用截至前一日的历史窗口：

```python
df = df.sort_values(["code", "date"])

grouped = df.groupby("code")["return"]

rolling_mean_previous = grouped.transform(
    lambda x: x.shift(1)
               .rolling(window=60, min_periods=40)
               .mean()
)

rolling_std_previous = grouped.transform(
    lambda x: x.shift(1)
               .rolling(window=60, min_periods=40)
               .std()
)

df["rolling_z_60d_lagged"] = (
    df["return"] - rolling_mean_previous
) / rolling_std_previous
```

这更接近实时异常检测，也避免使用当天信息构造当天基准。

---

## 十三、Z 分数的局限

Z 分数依赖均值和标准差，但金融收益常有：

- 偏度；
- 厚尾；
- 波动率聚集；
- 市场状态变化；
- 极端事件。

异常值还会拉动均值、抬高标准差，从而影响自身和其他记录的 Z 分数。因此 Z 分数只能作为候选筛选方法。

---

## 十四、IQR 异常规则

$$
IQR=Q_3-Q_1
$$

$$
Lower=Q_1-1.5\times IQR
$$

$$
Upper=Q_3+1.5\times IQR
$$

IQR 主要使用中间 50% 数据，对极端值比均值和标准差更稳健。

按股票计算：

```python
def add_iqr_flags(
    df: pd.DataFrame,
    code_col: str = "code",
    return_col: str = "return",
    multiplier: float = 1.5,
) -> pd.DataFrame:
    result = df.copy()
    grouped = result.groupby(code_col)[return_col]

    q1 = grouped.transform(lambda x: x.quantile(0.25))
    q3 = grouped.transform(lambda x: x.quantile(0.75))
    iqr = q3 - q1

    result["iqr_q1"] = q1
    result["iqr_q3"] = q3
    result["iqr"] = iqr
    result["iqr_lower_bound"] = q1 - multiplier * iqr
    result["iqr_upper_bound"] = q3 + multiplier * iqr
    result["is_iqr_lower_outlier"] = (
        result[return_col] < result["iqr_lower_bound"]
    )
    result["is_iqr_upper_outlier"] = (
        result[return_col] > result["iqr_upper_bound"]
    )
    result["is_iqr_outlier"] = (
        result["is_iqr_lower_outlier"]
        | result["is_iqr_upper_outlier"]
    )

    return result
```

---

## 十五、稳健 Z 分数与 MAD

中位数绝对偏差：

$$
MAD=median(|x_i-median(x)|)
$$

稳健 Z 分数：

$$
modified\_z=0.6745\times\frac{x_i-median(x)}{MAD}
$$

Python：

```python
import numpy as np
import pandas as pd


def calculate_modified_z_score(
    series: pd.Series,
) -> pd.Series:
    median_value = series.median()
    absolute_deviation = (series - median_value).abs()
    mad = absolute_deviation.median()

    if pd.isna(mad) or mad == 0:
        return pd.Series(
            np.nan,
            index=series.index,
            dtype=float,
        )

    return 0.6745 * (series - median_value) / mad


df["modified_z_score"] = (
    df.groupby("code")["return"]
      .transform(calculate_modified_z_score)
)
```

常见候选阈值为：

$$
|modified\_z|>3.5
$$

MAD 为 0 可能说明大量零收益、长期停牌、流动性不足或错误填充，本身也需要检查。

---

## 十六、联合异常标记

```python
df["is_z_outlier"] = df["z_score"].abs() > 3
df["is_rolling_z_outlier"] = (
    df["rolling_z_60d_lagged"].abs() > 3
)
df["is_modified_z_outlier"] = (
    df["modified_z_score"].abs() > 3.5
)

df["is_statistical_outlier"] = (
    df["is_z_outlier"]
    | df["is_rolling_z_outlier"]
    | df["is_modified_z_outlier"]
    | df["is_iqr_outlier"]
)
```

可以统计触发方法数量，作为检查优先级，但不能代替业务判断。

---

## 十七、时间序列异常与横截面异常

### 时间序列异常

比较某只股票今天与其自身历史：

> 今天的收益相对这只股票过去是否异常？

使用按股票计算的 Z 分数、滚动 Z 分数、IQR 和 MAD。

### 横截面异常

比较同一天不同股票：

> 今天这只股票相对全市场是否异常？

```python
def cross_sectional_z_score(
    series: pd.Series,
) -> pd.Series:
    std_value = series.std(ddof=1)
    if pd.isna(std_value) or std_value == 0:
        return pd.Series(np.nan, index=series.index)
    return (series - series.mean()) / std_value


df["cross_sectional_z"] = (
    df.groupby("date")["return"]
      .transform(cross_sectional_z_score)
)
```

联合解释：

- 时间序列异常、横截面正常：可能是系统性市场事件；
- 两者都异常：可能是个股特有事件或数据问题；
- 时间序列普通、横截面异常：对高波动股票并不罕见，但当天表现突出。

---

## 十八、行业相对异常收益

行业相对收益：

$$
industry\_relative\_return=stock\_return-industry\_mean\_return
$$

```python
industry_mean_return = (
    df.groupby(["date", "industry"])["return"]
      .transform("mean")
)

df["industry_relative_return"] = (
    df["return"] - industry_mean_return
)
```

这有助于区分行业共同冲击和个股特有冲击。

---

## 十九、A 股涨跌停检查

不能简单使用固定 10% 阈值判断全部 A 股，因为不同板块、ST 状态、历史时期和特殊交易阶段规则不同。

更合理的方法是维护当日适用的：

```text
limit_ratio
up_limit_price
down_limit_price
```

若数据源提供涨跌停价格：

```python
price_tolerance = 1e-6

df["is_limit_up"] = (
    (df["close"] - df["up_limit_price"]).abs()
    <= price_tolerance
)
df["is_limit_down"] = (
    (df["close"] - df["down_limit_price"]).abs()
    <= price_tolerance
)
```

浮点价格不宜直接使用完全相等判断。

---

## 二十、停牌与复牌

最好使用明确的交易状态字段：

```text
is_trading
is_suspended
is_resume_day
trade_status
```

停牌日不应未经判断就当作普通零收益日参与分布统计。

结合成交量为 0、开高低收相同等特征只能辅助判断，不能替代明确状态字段。

---

## 二十一、复权与公司行为

未复权价格在除权除息日可能自然下降，不能直接解释为投资损失。

异常检查时应比较：

```text
未复权收益
复权收益
复权因子变化
公司行为日期
```

复权因子变化：

```python
df = df.sort_values(["code", "date"])
df["previous_adjustment_factor"] = (
    df.groupby("code")["adjustment_factor"].shift(1)
)
df["adjustment_factor_changed"] = (
    (
        df["adjustment_factor"]
        - df["previous_adjustment_factor"]
    ).abs() > 1e-12
)
```

异常收益与复权因子变化同日出现时，应优先核验公司行为和价格口径。

---

## 二十二、新股与特殊交易阶段

建议维护：

```text
listing_date
days_since_listing
is_ipo_period
historical_st_status
```

```python
df["days_since_listing"] = (
    df["date"] - df["listing_date"]
).dt.days

df["is_ipo_period"] = df["days_since_listing"] <= 20
```

20 天只是研究标记示例，不是统一交易规则。历史涨跌幅限制必须依据当时规则和证券状态。

---

## 二十三、成交量与异常收益

收益率异常且成交量显著放大，更可能是真实市场事件；收益率异常但成交量为 0，可能是停牌处理或数据错误。

滞后滚动成交量 Z 分数：

```python
volume_mean = (
    df.groupby("code")["volume"]
      .transform(
          lambda x: x.shift(1)
                     .rolling(60, min_periods=40)
                     .mean()
      )
)

volume_std = (
    df.groupby("code")["volume"]
      .transform(
          lambda x: x.shift(1)
                     .rolling(60, min_periods=40)
                     .std()
      )
)

df["volume_z_60d"] = (
    df["volume"] - volume_mean
) / volume_std
```

---

## 二十四、异常值处理方式

### 保留 `KEEP`

适用于真实普通或真实极端行情。

### 保留并标记 `KEEP_WITH_FLAG`

适用于涨跌停、复牌、上市初期、特殊规则日等真实记录。

### 修正 `CORRECT`

适用于已确认的原始价格、代码、日期、单位或复权错误。必须记录原始值、修正值、原因、来源和时间。

### 排除 `EXCLUDE`

适用于无法修复、严重缺失或不符合研究样本定义的记录。不要删除原始层数据，应在研究层设置排除标志和原因。

### 继续核验 `REVIEW`

证据不足时暂不做最终处理。

---

## 二十五、为什么不直接缩尾原始收益

缩尾示例：

```python
lower = returns.quantile(0.01)
upper = returns.quantile(0.99)
winsorized_returns = returns.clip(lower=lower, upper=upper)
```

缩尾会：

- 改写真实极端收益；
- 低估尾部风险和波动率；
- 降低峰度；
- 改变最大回撤；
- 美化策略表现。

若研究中使用缩尾，应同时保留：

```text
raw_return
clean_return
winsorized_return
```

并明确用途。

---

## 二十六、数据分层

### 原始层

```text
data/raw/
```

保留数据源原貌，不覆盖，不手工修改。

### 清洗层

```text
data/processed/
```

统一字段、修正确认错误、添加质量标志和处理记录。

### 研究层

```text
data/research/
```

按研究目标筛选样本、处理停牌和特殊状态，但保留完整证据链。

---

## 二十七、异常收益检查表

推荐字段：

| 字段 | 含义 |
|---|---|
| `date` | 交易日期 |
| `code` | 股票代码 |
| `return` | 原始收益率 |
| `z_score` | 全样本 Z 分数 |
| `rolling_z_60d` | 60 日滞后滚动 Z 分数 |
| `modified_z_score` | 稳健 Z 分数 |
| `is_iqr_outlier` | IQR 异常标志 |
| `cross_sectional_z` | 当日横截面 Z 分数 |
| `is_limit_up` | 是否涨停 |
| `is_limit_down` | 是否跌停 |
| `is_suspended` | 是否停牌 |
| `is_resume_day` | 是否复牌日 |
| `adjustment_factor_changed` | 复权因子变化 |
| `is_ipo_period` | 是否上市初期 |
| `volume_z_60d` | 成交量异常程度 |
| `data_quality_status` | 数据质量结论 |
| `handling_action` | 处理方式 |
| `review_note` | 核验说明 |

质量状态建议：

```text
NORMAL
REAL_EXTREME
CORPORATE_ACTION
SUSPENSION_OR_RESUMPTION
SPECIAL_TRADING_RULE
SUSPECTED_DATA_ERROR
CONFIRMED_DATA_ERROR
INSUFFICIENT_INFORMATION
```

---

## 二十八、完整异常报告函数

```python
import numpy as np
import pandas as pd


def build_return_outlier_report(
    df: pd.DataFrame,
    code_col: str = "code",
    date_col: str = "date",
    return_col: str = "return",
    rolling_window: int = 60,
    rolling_min_periods: int = 40,
    z_threshold: float = 3.0,
    modified_z_threshold: float = 3.5,
    iqr_multiplier: float = 1.5,
) -> pd.DataFrame:
    required_columns = {code_col, date_col, return_col}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"缺少必要字段：{sorted(missing)}")

    result = df.copy()
    result[date_col] = pd.to_datetime(
        result[date_col], errors="coerce"
    )
    result[return_col] = pd.to_numeric(
        result[return_col], errors="coerce"
    )
    result = result.sort_values([code_col, date_col])

    grouped = result.groupby(code_col)[return_col]
    mean_value = grouped.transform("mean")
    std_value = grouped.transform("std")
    result["z_score"] = (
        result[return_col] - mean_value
    ) / std_value.replace(0, np.nan)

    rolling_mean = grouped.transform(
        lambda x: x.shift(1)
                   .rolling(rolling_window, min_periods=rolling_min_periods)
                   .mean()
    )
    rolling_std = grouped.transform(
        lambda x: x.shift(1)
                   .rolling(rolling_window, min_periods=rolling_min_periods)
                   .std()
    )
    result["rolling_z_score"] = (
        result[return_col] - rolling_mean
    ) / rolling_std.replace(0, np.nan)

    median_value = grouped.transform("median")
    absolute_deviation = (
        result[return_col] - median_value
    ).abs()
    mad_value = absolute_deviation.groupby(
        result[code_col]
    ).transform("median")
    result["modified_z_score"] = (
        0.6745
        * (result[return_col] - median_value)
        / mad_value.replace(0, np.nan)
    )

    q1 = grouped.transform(lambda x: x.quantile(0.25))
    q3 = grouped.transform(lambda x: x.quantile(0.75))
    iqr = q3 - q1
    result["iqr_lower_bound"] = q1 - iqr_multiplier * iqr
    result["iqr_upper_bound"] = q3 + iqr_multiplier * iqr
    result["is_iqr_outlier"] = (
        (result[return_col] < result["iqr_lower_bound"])
        | (result[return_col] > result["iqr_upper_bound"])
    )

    result["is_z_outlier"] = (
        result["z_score"].abs() > z_threshold
    )
    result["is_rolling_z_outlier"] = (
        result["rolling_z_score"].abs() > z_threshold
    )
    result["is_modified_z_outlier"] = (
        result["modified_z_score"].abs()
        > modified_z_threshold
    )

    flag_columns = [
        "is_z_outlier",
        "is_rolling_z_outlier",
        "is_modified_z_outlier",
        "is_iqr_outlier",
    ]
    result["statistical_flag_count"] = (
        result[flag_columns].sum(axis=1)
    )
    result["requires_review"] = (
        result["statistical_flag_count"] > 0
    )

    return result
```

---

## 二十九、自动初步分类

```python
def initial_quality_classification(
    row: pd.Series,
) -> str:
    if not row["requires_review"]:
        return "NORMAL"
    if row.get("is_limit_up", False):
        return "REAL_EXTREME"
    if row.get("is_limit_down", False):
        return "REAL_EXTREME"
    if row.get("adjustment_factor_changed", False):
        return "CORPORATE_ACTION"
    if row.get("is_resume_day", False):
        return "SUSPENSION_OR_RESUMPTION"
    if row.get("is_ipo_period", False):
        return "SPECIAL_TRADING_RULE"
    if row.get("has_basic_price_error", False):
        return "SUSPECTED_DATA_ERROR"
    return "INSUFFICIENT_INFORMATION"
```

自动规则只提供初步分类，最终结论仍需人工或可信数据源核验。

---

## 三十、数据泄漏问题

若使用整个 2015—2026 年样本的分位数处理 2016 年数据，就使用了未来信息。

回测中正确做法是：

> 每个交易日只使用当时已经获得的历史数据计算异常边界。

```python
rolling_lower = (
    df.groupby("code")["return"]
      .transform(
          lambda x: x.shift(1)
                     .rolling(252, min_periods=120)
                     .quantile(0.01)
      )
)

rolling_upper = (
    df.groupby("code")["return"]
      .transform(
          lambda x: x.shift(1)
                     .rolling(252, min_periods=120)
                     .quantile(0.99)
      )
)
```

---

## 三十一、异常处理对回测的影响

### 删除大跌日

会高估收益、低估最大回撤和波动率、提高夏普比率。

### 删除大涨日

会低估趋势策略和正偏策略的收益。

### 停牌日填 0

会低估波动和流动性风险，并错误假设每天都可交易。

任何处理都必须有明确经济理由和可审计记录。

---

## 三十二、核验顺序

1. 检查开盘、最高、最低、收盘、前收盘、成交量和成交额；
2. 检查股票内日期排序、收益计算和重复记录；
3. 检查停牌、复牌、涨跌停和特殊交易状态；
4. 检查除权除息、复权因子和公司行为；
5. 使用其他可信数据源交叉验证；
6. 记录结论和处理动作。

---

## 三十三、案例

### 复权问题

```text
收益率：-19.87%
全样本Z：-6.20
滚动Z：-7.10
稳健Z：-9.30
IQR异常：是
复权因子变化：是
前复权收益：0.42%
```

合理结论：异常主要来自除权或复权口径变化，原始未复权价格保留，研究收益使用统一复权价格，并添加公司行为标记。

### 真实跌停

```text
收益率：-9.98%
Z分数：-4.50
跌停状态：是
成交量：明显放大
复权因子变化：否
```

合理结论：真实极端行情，应保留并标记。

### 疑似数据错误

```text
收益率：+830%
最高价：12.50
收盘价：125.00
最高价 < 收盘价
```

违反基本价格关系，疑似小数点或字段错位，需要回查原始数据源。

---

## 三十四、实践任务

### 任务一：基本质量检查

检查至少 5 只股票、至少一年数据中的：

- 日期代码重复；
- 缺失日期；
- 非正价格；
- OHLC 关系错误；
- 负成交量和负成交额；
- 股票内部日期未升序。

### 任务二：计算四种异常指标

| 日期 | 股票 | 收益率 | Z分数 | 滚动Z | 稳健Z | IQR异常 |
|---|---|---:|---:|---:|---:|---|

### 任务三：横截面异常

筛选：

$$
|cross\_sectional\_z|>3
$$

### 任务四：加入业务字段

加入停牌、复牌、涨跌停、上市初期、复权因子变化、成交量异常和行业相对收益。

### 任务五：核验至少 10 条异常收益

| 日期 | 股票 | 收益率 | 统计触发 | 业务特征 | 初步结论 | 处理方式 |
|---|---|---:|---|---|---|---|

### 任务六：比较处理前后统计结果

比较均值、标准差、偏度、峰度、1% 和 99% 分位数、最大回撤。

---

## 三十五、常见错误

1. 把异常值等同于错误数据。
2. 看到 3 倍标准差就直接删除。
3. 所有股票共用一个 Z 分数基准。
4. 当天收益参与当天滚动基准。
5. 停牌日统一填 0。
6. 只检查收益率，不检查价格字段。
7. 忽略复权口径和公司行为。
8. 使用当前 ST 状态判断历史规则。
9. 修改原始数据文件。
10. 回测时用全样本边界清洗历史数据。

---

## 三十六、自测题

1. 异常值是否一定是错误数据？
2. Z 分数衡量什么？
3. 为什么 Z 分数对异常值敏感？
4. IQR 为什么更加稳健？
5. 稳健 Z 分数使用哪些指标？
6. 为什么滚动 Z 最好使用滞后窗口？
7. 为什么要计算横截面异常？
8. 真实涨跌停是否应删除？
9. 除权日未复权跌幅是否等于投资损失？
10. 原始数据为什么不能直接修改？

---

## 三十七、今日验收标准

- 能区分异常值、极端值和错误数据；
- 能计算并解释 Z 分数；
- 能按股票分别计算异常指标；
- 能计算滞后滚动 Z 分数；
- 能计算 IQR 异常边界；
- 能计算稳健 Z 分数和解释 MAD；
- 能区分时间序列与横截面异常；
- 能检查价格字段和重复记录；
- 能识别停牌、复牌、涨跌停和复权变化；
- 能建立异常收益检查表；
- 能为异常记录选择合理处理动作；
- 能保留原始数据和修正记录。

---

## 三十八、今日最终产出

```text
notebooks/week07_day06_outlier_data_quality.ipynb
src/data_quality.py
reports/week07_day06_outlier_report.csv
```

建议实现：

```python
calculate_z_score()
calculate_modified_z_score()
add_iqr_flags()
build_return_outlier_report()
initial_quality_classification()
```

今日最重要的结论：

> 统计方法只能发现值得检查的异常候选，不能直接判断数据是否错误。真实涨跌停和重大事件应保留，错误价格和复权问题应修正；所有处理都必须留下标记、原因和数据证据链。
