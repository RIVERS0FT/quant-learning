# 第 4 周第 7 天：阶段项目与复习

## 今日目标

- 整合本周的 pandas 数据处理知识。
- 将原始多股票日线数据整理为标准行情长表。
- 生成收盘价宽表并完成一致性验证。
- 将数据处理流程拆分为可复用模块。

## 阶段项目

将一份原始多股票日线数据整理为标准行情表。

## 项目流程

```text
读取原始文件
    ↓
检查字段和数据类型
    ↓
统一字段名称
    ↓
转换日期和股票代码
    ↓
处理缺失值与重复值
    ↓
按股票和日期排序
    ↓
生成长表行情数据
    ↓
生成收盘价宽表
    ↓
保存为 CSV 和 Parquet
    ↓
重新读取并验证
```

## 推荐项目结构

```text
quant-research/
├── data/
│   ├── raw/
│   │   └── daily_prices.csv
│   └── processed/
│       ├── daily_prices.parquet
│       └── close_matrix.parquet
├── src/
│   ├── data_loader.py
│   ├── data_cleaner.py
│   └── data_transform.py
└── tests/
    └── test_data_cleaner.py
```

## 模块职责

### `data_loader.py`

负责：

- 读取 CSV；
- 读取 Parquet；
- 检查文件路径；
- 统一读取参数。

```python
from pathlib import Path

import pandas as pd


def load_daily_csv(path: str | Path) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    return pd.read_csv(
        file_path,
        dtype={"stock_code": "string"},
    )
```

### `data_cleaner.py`

负责：

- 字段重命名；
- 日期转换；
- 股票代码标准化；
- 数值字段转换；
- 缺失值和重复值检查；
- 排序。

### `data_transform.py`

负责：

- 长表转宽表；
- 宽表转长表；
- 生成收盘价矩阵；
- 验证转换前后数据数量。

## 生成收盘价宽表

```python
def build_close_matrix(
    daily_data: pd.DataFrame,
) -> pd.DataFrame:
    key_columns = ["trade_date", "stock_code"]

    if daily_data.duplicated(key_columns).any():
        raise ValueError("无法生成宽表：主键存在重复记录")

    close_matrix = daily_data.pivot(
        index="trade_date",
        columns="stock_code",
        values="close",
    )

    return close_matrix.sort_index()
```

## 保存项目结果

```python
from pathlib import Path

processed_dir = Path("data/processed")
processed_dir.mkdir(parents=True, exist_ok=True)

standard_data.to_csv(
    processed_dir / "daily_prices.csv",
    index=False,
    encoding="utf-8-sig",
)

standard_data.to_parquet(
    processed_dir / "daily_prices.parquet",
    index=False,
)

close_matrix.to_parquet(
    processed_dir / "close_matrix.parquet",
)
```

## 验证要求

### 字段检查

```python
required_columns = {
    "trade_date",
    "stock_code",
    "open",
    "high",
    "low",
    "close",
    "volume",
}

assert required_columns.issubset(standard_data.columns)
```

### 类型检查

```python
assert pd.api.types.is_datetime64_any_dtype(
    standard_data["trade_date"]
)

assert pd.api.types.is_string_dtype(
    standard_data["stock_code"]
)
```

### 主键检查

```python
assert not standard_data.duplicated(
    ["trade_date", "stock_code"]
).any()
```

### 排序检查

```python
expected = standard_data.sort_values(
    ["stock_code", "trade_date"]
).reset_index(drop=True)

pd.testing.assert_frame_equal(
    standard_data.reset_index(drop=True),
    expected,
)
```

### 长宽表一致性检查

```python
long_non_null = standard_data["close"].notna().sum()
wide_non_null = close_matrix.notna().sum().sum()

assert long_non_null == wide_non_null
```

### 保存后重新读取

```python
reloaded = pd.read_parquet(
    "data/processed/daily_prices.parquet"
)

pd.testing.assert_frame_equal(
    standard_data,
    reloaded,
)
```

## 最终输出文件

```text
data/raw/daily_prices.csv
data/processed/daily_prices.csv
data/processed/daily_prices.parquet
data/processed/close_matrix.parquet
src/data_loader.py
src/data_cleaner.py
src/data_transform.py
tests/test_data_cleaner.py
```

## 本周需要掌握的主要 pandas 函数

```python
pd.Series
pd.DataFrame
pd.read_csv
pd.read_parquet
pd.to_datetime
pd.to_numeric

DataFrame.head
DataFrame.info
DataFrame.describe
DataFrame.astype
DataFrame.loc
DataFrame.iloc
DataFrame.query
DataFrame.sort_values
DataFrame.set_index
DataFrame.reset_index
DataFrame.rename
DataFrame.drop
DataFrame.drop_duplicates
DataFrame.pivot
DataFrame.pivot_table
DataFrame.melt
DataFrame.to_csv
DataFrame.to_parquet
```

## 本周数学与数据结构复习

- 时间序列由观测值和时间索引组成；
- 单资产价格序列通常是一维结构；
- 多资产价格矩阵通常以日期为行、资产为列；
- 缺失值会影响收益率、相关性和滚动统计；
- 交易日与自然日不同；
- 日期排序错误会直接导致收益率计算错误；
- 长表适合存储与筛选，宽表适合矩阵运算。

## 本周验收问题

1. `Series` 和 `DataFrame` 有什么区别？
2. 为什么股票代码必须使用字符串？
3. 为什么金融数据必须先按日期排序？
4. 长表和宽表分别适合什么场景？
5. 如何提取某只股票某段时间的行情？
6. 如何将多股票收盘价转换成价格矩阵？
7. 如何检查重复数据、缺失值和字段类型？
8. 如何把原始 CSV 整理为标准 Parquet 行情文件？

## 完成标准

- [ ] 能读取 CSV 并正确指定股票代码类型；
- [ ] 能将日期转换为日期类型；
- [ ] 能处理字段重命名、缺失值和重复记录；
- [ ] 能按股票和日期稳定排序；
- [ ] 能生成标准行情长表；
- [ ] 能生成收盘价宽表；
- [ ] 能保存为 CSV 和 Parquet；
- [ ] 能重新读取并验证结果；
- [ ] 能解释每一步处理的原因。

本周最终成果是：**一套能够将原始日线数据转换为标准行情长表和收盘价宽表的数据整理程序。**
