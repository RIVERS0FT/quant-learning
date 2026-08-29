# 第 5 周第 7 天：多股票特征工程综合项目

## 项目名称

多股票量化特征与未来收益标签生成器。

## 今日目标

- 综合使用 `groupby()`、`shift()`、`rolling()`、`rank()` 和 `merge()`。
- 构建可复用的多股票特征处理流程。
- 检查排序、主键、缺失值和未来数据泄漏。
- 输出标准化的日频特征数据集。

## 一、输入数据

标准日线行情表至少包含：

```text
trade_date
symbol
open
high
low
close
volume
amount
```

字段要求：

- `trade_date` 使用日期类型。
- `symbol` 使用字符串类型并保留前导零。
- 同一只股票同一交易日只能有一行。
- 价格和成交数据应明确是否复权。

## 二、输出字段

### 基础字段

```text
trade_date
symbol
close
volume
amount
```

### 收益率字段

```text
return_1d
return_5d
return_20d
```

### 趋势字段

```text
ma_5
ma_20
close_ma20_ratio
```

### 风险字段

```text
volatility_20d
annual_volatility_20d
```

### 截面字段

```text
return_20d_rank_pct
amount_rank_pct
volatility_rank_pct
```

### 标签字段

```text
future_return_1d
future_return_5d
```

## 三、推荐目录结构

```text
quant-learning-path/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── features/
│   │   ├── returns.py
│   │   ├── rolling.py
│   │   ├── ranking.py
│   │   └── labels.py
│   └── pipelines/
│       └── build_features.py
├── tests/
│   ├── test_returns.py
│   ├── test_rolling.py
│   └── test_labels.py
└── notebooks/
    └── week05_factor_analysis.ipynb
```

## 四、处理流程

```text
读取数据
  ↓
检查必要字段
  ↓
统一日期和股票代码类型
  ↓
检查重复主键
  ↓
按股票代码和日期排序
  ↓
计算历史收益率
  ↓
计算均线与均线偏离度
  ↓
计算滚动波动率
  ↓
按交易日计算截面排名
  ↓
构造未来收益标签
  ↓
检查缺失值和未来数据泄漏
  ↓
保存特征数据
```

## 五、完整特征生成函数

```python
import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "trade_date",
    "symbol",
    "close",
    "volume",
    "amount",
}


def validate_input(df: pd.DataFrame) -> None:
    """检查输入字段和主键。"""
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"缺少字段: {sorted(missing)}")

    duplicate_count = df.duplicated(
        ["trade_date", "symbol"]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"发现 {duplicate_count} 个重复的日期股票主键"
        )


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """构建多股票日频特征和未来收益标签。"""
    result = df.copy()

    result["trade_date"] = pd.to_datetime(
        result["trade_date"]
    )

    result["symbol"] = (
        result["symbol"]
        .astype(str)
        .str.zfill(6)
    )

    validate_input(result)

    result = result.sort_values(
        ["symbol", "trade_date"]
    ).reset_index(drop=True)

    # 历史收益率
    for window in (1, 5, 20):
        result[f"return_{window}d"] = (
            result.groupby("symbol")["close"]
                  .pct_change(window)
        )

    # 移动平均线
    for window in (5, 20):
        result[f"ma_{window}"] = (
            result.groupby("symbol")["close"]
                  .transform(
                      lambda x, w=window: x.rolling(
                          window=w,
                          min_periods=w,
                      ).mean()
                  )
        )

    # 均线偏离度
    result["close_ma20_ratio"] = (
        result["close"] / result["ma_20"] - 1
    )

    # 20 日滚动波动率
    result["volatility_20d"] = (
        result.groupby("symbol")["return_1d"]
              .transform(
                  lambda x: x.rolling(
                      window=20,
                      min_periods=20,
                  ).std()
              )
    )

    result["annual_volatility_20d"] = (
        result["volatility_20d"] * np.sqrt(252)
    )

    # 截面排名
    result["return_20d_rank_pct"] = (
        result.groupby("trade_date")["return_20d"]
              .rank(pct=True)
    )

    result["amount_rank_pct"] = (
        result.groupby("trade_date")["amount"]
              .rank(pct=True)
    )

    result["volatility_rank_pct"] = (
        result.groupby("trade_date")["volatility_20d"]
              .rank(pct=True)
    )

    # 未来收益标签
    for window in (1, 5):
        future_price = (
            result.groupby("symbol")["close"]
                  .shift(-window)
        )

        result[f"future_return_{window}d"] = (
            future_price / result["close"] - 1
        )

    return result
```

## 六、保存特征数据

推荐使用 Parquet：

```python
features = build_features(raw_df)

output_path = "data/processed/daily_features.parquet"
features.to_parquet(
    output_path,
    index=False,
)
```

Parquet 的优点：

- 保留字段类型。
- 读写速度通常优于 CSV。
- 文件体积通常更小。
- 适合后续使用 pandas、DuckDB 和 Arrow。

## 七、关键数学公式

### 简单收益率

$$
r_t
= \frac{P_t}{P_{t-1}} - 1
$$

### 多周期历史收益率

$$
r_{t,N}
= \frac{P_t}{P_{t-N}} - 1
$$

### 未来收益率

$$
r_{t \rightarrow t+N}
= \frac{P_{t+N}}{P_t} - 1
$$

### 移动平均线

$$
MA_{t,N}
= \frac{1}{N}
\sum_{i=0}^{N-1} P_{t-i}
$$

### 滚动波动率

$$
\sigma_{t,N}
= \sqrt{
\frac{1}{N-1}
\sum_{i=0}^{N-1}
(r_{t-i}-\bar r)^2
}
$$

### 年化波动率

$$
\sigma_{\text{annual}}
= \sigma_{\text{daily}}\sqrt{252}
$$

## 八、单元测试

### 测试 1 日收益率

```python
import numpy as np
import pandas as pd


def test_return_1d():
    df = pd.DataFrame({
        "trade_date": pd.to_datetime([
            "2026-01-01",
            "2026-01-02",
        ]),
        "symbol": ["000001", "000001"],
        "close": [10.0, 11.0],
        "volume": [100, 120],
        "amount": [1000, 1320],
    })

    result = build_features(df)

    assert np.isnan(result.loc[0, "return_1d"])
    assert np.isclose(result.loc[1, "return_1d"], 0.10)
```

### 测试不同股票不互相污染

```python
def test_group_boundary():
    df = pd.DataFrame({
        "trade_date": pd.to_datetime([
            "2026-01-01", "2026-01-02",
            "2026-01-01", "2026-01-02",
        ]),
        "symbol": ["000001", "000001", "000002", "000002"],
        "close": [10.0, 11.0, 20.0, 18.0],
        "volume": [100, 110, 200, 180],
        "amount": [1000, 1210, 4000, 3240],
    })

    result = build_features(df)
    first_rows = result.groupby("symbol").head(1)

    assert first_rows["return_1d"].isna().all()
```

### 测试未来收益标签

```python
def test_future_return_1d():
    df = pd.DataFrame({
        "trade_date": pd.to_datetime([
            "2026-01-01",
            "2026-01-02",
        ]),
        "symbol": ["000001", "000001"],
        "close": [10.0, 11.0],
        "volume": [100, 120],
        "amount": [1000, 1320],
    })

    result = build_features(df)

    assert np.isclose(
        result.loc[0, "future_return_1d"],
        0.10,
    )
    assert np.isnan(
        result.loc[1, "future_return_1d"]
    )
```

## 九、未来数据泄漏检查

### 允许使用未来数据的字段

```text
future_return_1d
future_return_5d
```

这些字段只能用于：

- 因子有效性检验。
- 分组收益计算。
- 监督学习标签。
- 事后绩效评价。

### 不允许作为实时交易特征

以下代码使用未来价格：

```python
result.groupby("symbol")["close"].shift(-5)
```

因此由它生成的字段不能进入当日信号计算。

推荐在模型数据中明确拆分：

```python
feature_columns = [
    "return_1d",
    "return_5d",
    "return_20d",
    "ma_5",
    "ma_20",
    "close_ma20_ratio",
    "volatility_20d",
    "return_20d_rank_pct",
    "amount_rank_pct",
]

label_column = "future_return_5d"
```

## 十、数据质量检查

```python
def check_feature_output(
    raw_df: pd.DataFrame,
    feature_df: pd.DataFrame,
) -> None:
    if len(raw_df) != len(feature_df):
        raise ValueError("特征计算前后行数不一致")

    if feature_df.duplicated(
        ["trade_date", "symbol"]
    ).any():
        raise ValueError("输出数据存在重复主键")

    first_rows = feature_df.groupby("symbol").head(1)
    if not first_rows["return_1d"].isna().all():
        raise ValueError("股票边界可能发生收益率污染")

    last_rows = feature_df.groupby("symbol").tail(5)
    if not last_rows["future_return_5d"].isna().all():
        raise ValueError("未来 5 日标签窗口异常")
```

## 十一、结果分析任务

使用生成的特征表回答：

1. 哪些股票过去 20 日收益率最高？
2. 哪些股票当前 20 日波动率最高？
3. 20 日收益率排名靠前的股票，未来 5 日平均收益是否更高？
4. 高波动股票的未来收益分布有什么特点？
5. 不同交易日的有效股票数量是否稳定？
6. 成交额排名靠前的股票是否拥有更少的缺失数据？

### 示例：动量分组

```python
analysis_df = features.dropna(
    subset=[
        "return_20d_rank_pct",
        "future_return_5d",
    ]
).copy()

analysis_df["momentum_group"] = pd.qcut(
    analysis_df["return_20d_rank_pct"],
    q=5,
    labels=[1, 2, 3, 4, 5],
)

summary = (
    analysis_df.groupby("momentum_group", observed=True)
               ["future_return_5d"]
               .agg(["count", "mean", "median", "std"])
)

print(summary)
```

注意：这只是初步相关性分析，还没有处理交易成本、停牌、涨跌停和股票池偏差。

## 十二、项目检查清单

- [ ] 输入字段完整。
- [ ] 股票代码和日期类型正确。
- [ ] 股票日期主键没有重复。
- [ ] 数据先按股票和日期排序。
- [ ] 收益率按股票分组计算。
- [ ] 滚动窗口没有跨股票。
- [ ] 截面排名按交易日分组。
- [ ] 未来收益只作为标签。
- [ ] 每只股票最后 5 行的未来 5 日收益为空。
- [ ] 特征计算前后行数一致。
- [ ] 关键指标经过手工核验。
- [ ] 核心函数拥有单元测试。
- [ ] 输出文件可以被重新读取。

## 十三、完成标准

### 基础标准

能够独立使用：

```text
groupby
shift
rolling
rank
merge
```

### 合格标准

能够完成：

- 多股票收益率计算。
- 移动平均线计算。
- 滚动波动率计算。
- 截面排名。
- 未来收益标签。

### 优秀标准

能够做到：

- 将功能拆分为多个模块。
- 对输入字段和主键进行检查。
- 避免跨股票滚动计算。
- 编写收益率和标签单元测试。
- 输出标准化 Parquet 特征文件。
- 写出一份简短的因子分组分析。

## 十四、最终成果

本周最终产出：

```text
data/processed/daily_features.parquet
```

以及：

```text
src/features/returns.py
src/features/rolling.py
src/features/ranking.py
src/features/labels.py
src/pipelines/build_features.py
tests/test_returns.py
tests/test_rolling.py
tests/test_labels.py
notebooks/week05_factor_analysis.ipynb
```

第五周最重要的思维转变是：

```text
先明确计算方向：
纵向按股票处理时间序列，横向按日期处理截面排名。
```
