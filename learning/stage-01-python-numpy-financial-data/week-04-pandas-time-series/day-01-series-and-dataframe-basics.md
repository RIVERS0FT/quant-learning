# 第 4 周第 1 天：Series 与 DataFrame 基础

## 今日目标

- 理解 `Series` 与 `DataFrame` 的基本结构。
- 理解行索引、列名和数据类型的作用。
- 能够查看表格的形状、字段和基础统计信息。
- 手动创建一张股票日线行情表。

## 核心概念

### Series

`Series` 是带索引的一维数据结构，适合表示一只股票的一段收盘价、成交量或收益率序列。

```python
import pandas as pd

close = pd.Series(
    [10.00, 10.20, 10.10],
    index=["2026-01-05", "2026-01-06", "2026-01-07"],
    name="close",
)
```

### DataFrame

`DataFrame` 是带行标签和列标签的二维表格，适合表示股票日线行情、财务数据和因子数据。

```python
import pandas as pd

prices = pd.DataFrame(
    {
        "trade_date": ["2026-01-05", "2026-01-06"],
        "stock_code": ["000001", "000001"],
        "open": [10.00, 10.15],
        "high": [10.30, 10.40],
        "low": [9.95, 10.05],
        "close": [10.20, 10.10],
        "volume": [1_200_000, 980_000],
    }
)
```

## Series 与 DataFrame 的区别

| 对比项 | Series | DataFrame |
|---|---|---|
| 维度 | 一维 | 二维 |
| 主要结构 | 索引和值 | 行索引、列名和值 |
| 典型用途 | 单个字段或单资产序列 | 多字段、多资产表格 |
| 示例 | 一只股票的收盘价 | 多只股票的日线行情 |

## 重点属性与函数

```python
pd.Series()
pd.DataFrame()

prices.head()
prices.tail()
prices.info()
prices.describe()
prices.shape
prices.columns
prices.index
prices.dtypes
```

### `head()` 与 `tail()`

```python
prices.head(3)
prices.tail(3)
```

用于快速查看数据开头和结尾，检查读取结果、排序和字段是否正确。

### `shape`

```python
rows, columns = prices.shape
```

`shape` 返回 `(行数, 列数)`。

### `dtypes`

```python
print(prices.dtypes)
```

数据类型会直接影响日期筛选、数值计算和股票代码是否保留前导零。

### `info()`

```python
prices.info()
```

用于检查：

- 行数；
- 非空值数量；
- 字段类型；
- 内存占用。

### `describe()`

```python
prices.describe()
```

用于查看数值字段的数量、均值、标准差、最小值、分位数和最大值。

## 学习重点

`DataFrame` 不只是二维数组。它还包含：

- 字段名称；
- 行索引；
- 每列独立的数据类型；
- 缺失值信息；
- 对齐和筛选规则。

这些结构使其比普通二维数组更适合处理金融表格数据。

## 今日练习

手动创建一张包含以下字段的股票日线表：

```text
trade_date
stock_code
open
high
low
close
volume
```

完成后检查：

```python
print(prices.head())
print(prices.shape)
print(prices.columns)
print(prices.dtypes)
prices.info()
```

## 今日输出

- 一张股票日线 `DataFrame`；
- 一段检查字段、形状和数据类型的代码；
- 对 `Series` 与 `DataFrame` 区别的文字说明。

## 自检问题

1. `Series` 和 `DataFrame` 的主要区别是什么？
2. 行索引和列名分别解决什么问题？
3. 为什么不能只看表格显示结果，还要检查 `dtypes`？
4. `shape` 返回的两个数字分别代表什么？
