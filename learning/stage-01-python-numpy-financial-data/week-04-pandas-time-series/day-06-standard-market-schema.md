# 第 4 周第 6 天：标准行情表设计

## 今日目标

- 为日线行情建立统一字段规范。
- 统一日期、股票代码和数值字段类型。
- 处理重复记录、缺失值和排序问题。
- 编写可复用的行情标准化函数。

## 为什么需要标准行情表

若每个数据源使用不同字段名、类型和排序方式，后续策略代码会不断重复清洗逻辑，也更容易产生隐蔽错误。

统一标准后，收益率、均线、波动率、因子和回测模块都可以基于同一种输入结构工作。

## 推荐标准字段

```text
trade_date
stock_code
open
high
low
close
volume
amount
adj_factor
source
```

## 字段含义

| 字段 | 含义 | 推荐类型 |
|---|---|---|
| `trade_date` | 交易日期 | `datetime64[ns]` |
| `stock_code` | 股票代码 | `string` |
| `open` | 开盘价 | 浮点数 |
| `high` | 最高价 | 浮点数 |
| `low` | 最低价 | 浮点数 |
| `close` | 收盘价 | 浮点数 |
| `volume` | 成交量 | 数值类型 |
| `amount` | 成交额 | 数值类型 |
| `adj_factor` | 复权因子 | 浮点数 |
| `source` | 数据来源 | `string` |

## 主键规则

日线行情通常使用以下复合主键：

```text
trade_date + stock_code
```

每只股票每天最多只能有一条标准日线记录。

```python
key_columns = ["trade_date", "stock_code"]

duplicates = prices.loc[
    prices.duplicated(key_columns, keep=False)
]
```

在删除重复值前，必须先确认重复记录产生的原因。

## 推荐规则

- `trade_date` 使用日期类型；
- `stock_code` 使用字符串并保留前导零；
- 价格字段使用浮点数；
- 成交量和成交额使用数值类型；
- 每只股票每天最多一条记录；
- 按股票代码和交易日期升序排列；
- 原始数据与清洗数据分开保存；
- 数据来源字段必须可追踪；
- 缺失值的保留、填充或删除规则必须明确。

## 原始数据与清洗数据分离

```text
data/
├── raw/
│   └── daily_prices.csv
└── processed/
    └── daily_prices.parquet
```

`raw` 目录中的文件应尽量保持原样，便于重新清洗、审计和排错。

## 重点函数

```python
DataFrame.copy()
DataFrame.rename()
DataFrame.astype()
DataFrame.sort_values()
DataFrame.drop_duplicates()
DataFrame.isna()
DataFrame.notna()
```

## 标准化函数示例

```python
from collections.abc import Mapping

import pandas as pd


def standardize_daily_data(
    df: pd.DataFrame,
    column_mapping: Mapping[str, str] | None = None,
) -> pd.DataFrame:
    """将原始日线数据转换为标准行情表。"""
    result = df.copy()

    if column_mapping:
        result = result.rename(columns=column_mapping)

    required_columns = {
        "trade_date",
        "stock_code",
        "open",
        "high",
        "low",
        "close",
        "volume",
    }

    missing_columns = required_columns - set(result.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"缺少必要字段: {missing_text}")

    result["trade_date"] = pd.to_datetime(
        result["trade_date"],
        errors="coerce",
    )

    result["stock_code"] = (
        result["stock_code"]
        .astype("string")
        .str.strip()
        .str.zfill(6)
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "adj_factor",
    ]

    for column in numeric_columns:
        if column in result.columns:
            result[column] = pd.to_numeric(
                result[column],
                errors="coerce",
            )

    result = result.dropna(
        subset=["trade_date", "stock_code"]
    )

    result = result.drop_duplicates(
        subset=["trade_date", "stock_code"],
        keep="last",
    )

    result = (
        result
        .sort_values(["stock_code", "trade_date"])
        .reset_index(drop=True)
    )

    return result
```

## 注意：不要无条件删除重复值

上面的 `keep="last"` 只是示例规则。真实研究中应先检查：

- 是否来自重复下载；
- 是否存在多个数据源；
- 是否有盘中与收盘版本混合；
- 不同记录的价格或成交量是否冲突；
- 应依据哪个时间戳或来源保留记录。

## 数据质量检查

```python
def validate_daily_data(df: pd.DataFrame) -> None:
    key_columns = ["trade_date", "stock_code"]

    if df[key_columns].isna().any().any():
        raise ValueError("主键字段存在缺失值")

    if df.duplicated(key_columns).any():
        raise ValueError("主键存在重复记录")

    invalid_ohlc = (
        (df["high"] < df[["open", "close", "low"]].max(axis=1))
        | (df["low"] > df[["open", "close", "high"]].min(axis=1))
    )

    if invalid_ohlc.any():
        raise ValueError("存在不符合 OHLC 关系的记录")
```

## 今日练习

编写 `standardize_daily_data(df)`，至少完成：

1. 字段重命名；
2. 日期转换；
3. 股票代码标准化；
4. 数值字段转换；
5. 必要字段检查；
6. 重复记录检查或处理；
7. 按股票和日期排序；
8. 返回新的 DataFrame，不直接破坏原始输入。

## 今日输出

```text
src/data_cleaner.py
tests/test_data_cleaner.py
```

## 自检问题

1. 为什么要统一行情字段名称？
2. 为什么原始数据和清洗数据要分开保存？
3. 日线行情的复合主键通常是什么？
4. 为什么不能在不了解原因时直接删除重复值？
