# 第 4 周：pandas 基础与金融时间序列

## 本周核心目标

本周结束时，应当能够：

1. 使用 `pandas` 读取和保存行情数据；
2. 理解 `Series`、`DataFrame` 和索引的基本结构；
3. 正确处理日期、股票代码和数值字段；
4. 按股票、日期和交易条件筛选数据；
5. 在长表与宽表之间进行转换；
6. 将原始日线数据整理成统一、可复用的标准行情表。

## 本周学习安排

| 天 | 内容 | 预期产出 | 课程正文 |
|---:|---|---|---|
| 1 | Series 与 DataFrame 基础 | 股票日线 DataFrame | [查看](day-01-series-and-dataframe-basics.md) |
| 2 | 数据读取、保存与字段类型 | 标准类型行情文件 | [查看](day-02-data-io-and-dtypes.md) |
| 3 | 日期索引与金融时间序列 | 标准日期索引行情 | [查看](day-03-datetime-index.md) |
| 4 | 筛选、排序与列操作 | 行情筛选脚本 | [查看](day-04-filter-sort-columns.md) |
| 5 | 长表与宽表 | 收盘价宽表 | [查看](day-05-long-wide-format.md) |
| 6 | 标准行情表设计 | 行情清洗模块 | [查看](day-06-standard-market-schema.md) |
| 7 | 阶段项目与复习 | 标准行情表项目 | [查看](day-07-project-and-review.md) |

## 第一天：Series 与 DataFrame 基础

### 核心概念

- `Series`：带索引的一维数据；
- `DataFrame`：带行列标签的二维表格；
- 行索引与列名；
- 数据类型 `dtype`；
- 行、列、形状和基础信息。

### 重点函数

```python
pd.Series()
pd.DataFrame()

DataFrame.head()
DataFrame.tail()
DataFrame.info()
DataFrame.describe()
DataFrame.shape
DataFrame.columns
DataFrame.index
DataFrame.dtypes
```

### 学习重点

`DataFrame` 不只是二维数组，而是一张带字段名称、索引和数据类型的结构化表。

### 当日练习

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

## 第二天：数据读取、保存与字段类型

### 核心概念

- CSV 文件；
- Parquet 文件；
- 字符串、整数、浮点数和日期类型；
- 股票代码前导零；
- 缺失值识别。

### 重点函数

```python
pd.read_csv()
pd.read_parquet()

DataFrame.to_csv()
DataFrame.to_parquet()

DataFrame.astype()
pd.to_numeric()
pd.to_datetime()
```

### 学习重点

股票代码通常应保存为字符串，而不是整数。

正确：

```text
000001
```

错误读取结果：

```text
1
```

### 当日练习

读取一份日线 CSV，并完成：

- 股票代码转换为字符串；
- 交易日期转换为日期类型；
- 价格字段转换为浮点数；
- 保存为 Parquet 文件。

## 第三天：日期索引与金融时间序列

### 核心概念

- `DatetimeIndex`；
- 日期排序；
- 按时间范围筛选；
- 时间序列索引；
- 交易日与自然日的区别。

### 重点函数

```python
pd.to_datetime()

DataFrame.set_index()
DataFrame.reset_index()
DataFrame.sort_index()
DataFrame.sort_values()

DataFrame.loc[]
```

### 学习重点

理解以下两种数据结构的差异。

日期作为普通字段：

```text
trade_date  stock_code  close
```

日期作为索引：

```text
index=trade_date
columns=[stock_code, close]
```

### 当日练习

提取某只股票在以下日期范围内的行情：

```text
2026-01-01 至 2026-03-31
```

并检查数据是否按日期升序排列。

## 第四天：DataFrame 筛选、排序与列操作

### 核心概念

- 选择行和列；
- 条件筛选；
- 多条件组合；
- 创建新字段；
- 修改列名；
- 删除无用字段。

### 重点函数

```python
DataFrame.loc[]
DataFrame.iloc[]
DataFrame.query()
DataFrame.sort_values()
DataFrame.rename()
DataFrame.drop()
DataFrame.assign()
```

### 典型条件

筛选某只股票：

```python
prices["stock_code"] == "000001"
```

筛选成交量大于指定值：

```python
prices["volume"] > 1_000_000
```

组合条件：

```python
(
    (prices["stock_code"] == "000001")
    & (prices["close"] > 10)
)
```

### 当日练习

完成以下筛选：

- 指定股票；
- 指定日期范围；
- 收盘价高于开盘价；
- 成交量大于设定阈值；
- 按日期和股票代码排序。

## 第五天：长表与宽表

### 长表

每一行代表某只股票在某一天的一条记录。

```text
trade_date  stock_code  close
2026-01-05  000001      10.20
2026-01-05  000002      15.30
```

### 宽表

每一行代表日期，每一列代表一只股票。

```text
trade_date  000001  000002
2026-01-05  10.20   15.30
```

### 重点函数

```python
DataFrame.pivot()
DataFrame.pivot_table()
DataFrame.melt()
DataFrame.stack()
DataFrame.unstack()
```

### 学习重点

在量化研究中：

- 长表适合数据存储、筛选和数据库查询；
- 宽表适合多资产收益率、相关性和矩阵运算。

### 当日练习

1. 将多股票收盘价数据从长表转换为宽表；
2. 再从宽表还原成长表；
3. 检查转换前后数据是否一致。

## 第六天：标准行情表设计

### 推荐标准字段

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

### 推荐规则

- `trade_date`：日期类型；
- `stock_code`：字符串类型；
- 价格字段：浮点数；
- 成交量：数值类型；
- 每只股票每天最多一条记录；
- 按股票代码和交易日期排序；
- 原始数据与清洗数据分开保存。

### 重点函数

```python
DataFrame.copy()
DataFrame.rename()
DataFrame.astype()
DataFrame.sort_values()
DataFrame.drop_duplicates()
DataFrame.isna()
DataFrame.notna()
```

### 当日练习

编写行情标准化函数：

```python
def standardize_daily_data(df):
    ...
```

函数至少完成：

- 字段重命名；
- 日期转换；
- 股票代码标准化；
- 数值字段转换；
- 删除或审查重复记录；
- 数据排序。

## 第七天：阶段项目与复习

### 阶段项目

将一份原始多股票日线数据整理为标准行情表。

### 项目流程

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
```

### 最终输出文件

```text
data/raw/daily_prices.csv
data/processed/daily_prices.csv
data/processed/daily_prices.parquet
data/processed/close_matrix.parquet
```

### 程序结构建议

```text
src/
├── data_loader.py
├── data_cleaner.py
└── data_transform.py

tests/
└── test_data_cleaner.py
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

## 本周数学与数据结构重点

第四周数学内容不宜过重，主要巩固金融时间序列的数据表达：

- 时间序列的观测值与时间索引；
- 单资产价格序列；
- 多资产价格矩阵；
- 行代表日期、列代表资产的矩阵含义；
- 缺失值对收益率计算的影响；
- 交易日与自然日的区别；
- 数据排序错误为什么会导致收益率计算错误。

## 本周验收标准

完成第四周后，应当能够独立回答并实现：

1. `Series` 和 `DataFrame` 有什么区别？
2. 为什么股票代码必须使用字符串？
3. 为什么金融数据必须先按日期排序？
4. 长表和宽表分别适合什么场景？
5. 如何提取某只股票某段时间的行情？
6. 如何将多股票收盘价转换成价格矩阵？
7. 如何检查重复数据、缺失值和字段类型？
8. 如何把原始 CSV 整理为标准 Parquet 行情文件？

## 每日入口

[查看第四周每日学习路径](README.md)

## 核心成果

本周最终成果是：**一套能够将原始日线数据转换为标准行情长表和收盘价宽表的数据整理程序。**

## 完成状态

- [x] 第四周学习计划已保存；
- [x] 7 个每日学习文件已建立；
- [ ] 第 1 天学习完成；
- [ ] 第 2 天学习完成；
- [ ] 第 3 天学习完成；
- [ ] 第 4 天学习完成；
- [ ] 第 5 天学习完成；
- [ ] 第 6 天学习完成；
- [ ] 第 7 天综合项目完成。

## 每日学习路径

## 本周主题

pandas 基础与金融时间序列。

## 每日安排

| 天 | 主题 | 学习与实践 | 当天输出 | 状态 |
|---:|---|---|---|---|
| 1 | Series 与 DataFrame 基础 | 索引、列名、数据类型、形状和基础信息 | 股票日线 DataFrame | [已保存](day-01-series-and-dataframe-basics.md) |
| 2 | 数据读取、保存与字段类型 | CSV、Parquet、日期、股票代码和数值类型 | 标准类型行情文件 | [已保存](day-02-data-io-and-dtypes.md) |
| 3 | 日期索引与金融时间序列 | `DatetimeIndex`、排序、日期范围筛选 | 标准日期索引行情 | [已保存](day-03-datetime-index.md) |
| 4 | 筛选、排序与列操作 | `loc`、`iloc`、多条件筛选、新字段和重命名 | 行情筛选脚本 | [已保存](day-04-filter-sort-columns.md) |
| 5 | 长表与宽表 | `pivot`、`pivot_table`、`melt`、`stack`、`unstack` | 收盘价宽表 | [已保存](day-05-long-wide-format.md) |
| 6 | 标准行情表设计 | 字段规范、主键、缺失值、重复值和标准化函数 | 行情清洗模块 | [已保存](day-06-standard-market-schema.md) |
| 7 | 阶段项目与复习 | 清洗、排序、长宽表转换、保存与验证 | 标准行情表项目 | [已保存](day-07-project-and-review.md) |

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

## 学习顺序

```text
认识 pandas 数据结构
    ↓
读取文件并修正类型
    ↓
建立日期索引和排序规则
    ↓
掌握筛选、排序和列操作
    ↓
完成长表与宽表转换
    ↓
建立标准行情字段规范
    ↓
完成标准行情表阶段项目
```

## 每日学习要求

每天按照以下结构推进：

1. 阅读核心概念；
2. 运行并修改示例代码；
3. 完成当日练习；
4. 保存代码和结果；
5. 回答自检问题；
6. 将完成状态更新为“已完成”。

## 检查清单

- [ ] 日期字段为日期类型；
- [ ] 股票代码使用字符串并保留前导零；
- [ ] OHLCV 字段为数值类型；
- [ ] 数据按股票代码和交易日期排序；
- [ ] `(trade_date, stock_code)` 主键无重复；
- [ ] 长表与宽表转换前后数据一致；
- [ ] CSV 与 Parquet 重新读取后类型符合预期；
- [ ] 原始数据与处理后数据分开保存。
