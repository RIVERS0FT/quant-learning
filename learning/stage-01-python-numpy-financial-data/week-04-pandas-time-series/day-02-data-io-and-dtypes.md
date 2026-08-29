# 第 4 周第 2 天：数据读取、保存与字段类型

## 今日目标

- 使用 pandas 读取和保存 CSV、Parquet 文件。
- 正确处理股票代码、日期和价格字段的数据类型。
- 理解错误类型对量化研究的影响。
- 将原始日线数据转换为规范格式。

## 核心概念

### CSV

CSV 是通用文本格式，便于查看和交换，但读取时容易出现类型推断错误。

```python
import pandas as pd

prices = pd.read_csv("data/raw/daily_prices.csv")
```

### Parquet

Parquet 是列式存储格式，通常能保留字段类型，适合保存清洗后的行情和因子数据。

```python
prices = pd.read_parquet("data/processed/daily_prices.parquet")
```

## 重点函数

```python
pd.read_csv()
pd.read_parquet()

DataFrame.to_csv()
DataFrame.to_parquet()

DataFrame.astype()
pd.to_numeric()
pd.to_datetime()
```

## 股票代码必须使用字符串

A 股代码可能包含前导零，例如：

```text
000001
000002
300054
```

若读取为整数，`000001` 会变成 `1`，代码信息被破坏。因此股票代码应使用字符串。

```python
prices = pd.read_csv(
    "data/raw/daily_prices.csv",
    dtype={"stock_code": "string"},
)
```

若代码已经被读取为数字，可进行标准化：

```python
prices["stock_code"] = (
    prices["stock_code"]
    .astype("string")
    .str.zfill(6)
)
```

## 日期字段转换

```python
prices["trade_date"] = pd.to_datetime(
    prices["trade_date"],
    errors="coerce",
)
```

`errors="coerce"` 会将无法解析的日期转换为缺失值，便于后续检查。

```python
invalid_dates = prices[prices["trade_date"].isna()]
```

## 数值字段转换

```python
numeric_columns = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
]

for column in numeric_columns:
    prices[column] = pd.to_numeric(
        prices[column],
        errors="coerce",
    )
```

这样可以识别混入数值列的文本和非法字符。

## 类型检查

```python
print(prices.dtypes)
prices.info()
```

推荐类型：

| 字段 | 推荐类型 |
|---|---|
| `trade_date` | `datetime64[ns]` |
| `stock_code` | `string` |
| `open`、`high`、`low`、`close` | 浮点数 |
| `volume`、`amount` | 数值类型 |

## 保存数据

### 保存为 CSV

```python
prices.to_csv(
    "data/processed/daily_prices.csv",
    index=False,
    encoding="utf-8-sig",
)
```

### 保存为 Parquet

```python
prices.to_parquet(
    "data/processed/daily_prices.parquet",
    index=False,
)
```

## 重新读取验证

保存完成后，应重新读取并检查类型，而不是只确认文件已经生成。

```python
reloaded = pd.read_parquet(
    "data/processed/daily_prices.parquet"
)

print(reloaded.dtypes)
print(reloaded.head())
```

## 今日练习

读取一份日线 CSV，并完成：

1. 股票代码转换为字符串并补足六位；
2. 交易日期转换为日期类型；
3. 价格字段转换为浮点数；
4. 检查无法转换的日期和数值；
5. 保存为 Parquet 文件；
6. 重新读取并核对字段类型。

## 今日输出

```text
data/raw/daily_prices.csv
data/processed/daily_prices.parquet
```

以及一段可重复运行的数据类型转换代码。

## 自检问题

1. 为什么股票代码不能使用整数类型？
2. CSV 和 Parquet 的主要区别是什么？
3. `errors="coerce"` 有什么作用？
4. 为什么保存后还要重新读取验证？
