# 第 4 周第 3 天：日期索引与金融时间序列

## 今日目标

- 将交易日期转换为标准日期类型。
- 理解普通日期字段与 `DatetimeIndex` 的区别。
- 按时间范围筛选股票行情。
- 确保金融时间序列按正确顺序排列。

## 核心概念

### 日期类型

字符串日期不能稳定支持时间范围筛选和时间序列运算，因此应转换为日期类型。

```python
import pandas as pd

prices["trade_date"] = pd.to_datetime(
    prices["trade_date"],
    errors="coerce",
)
```

### DatetimeIndex

`DatetimeIndex` 是专门表示日期时间的索引，可用于日期切片、排序和时间序列操作。

```python
stock = prices.loc[
    prices["stock_code"] == "000001"
].copy()

stock = stock.set_index("trade_date")
```

## 日期作为字段与日期作为索引

### 日期作为普通字段

```text
trade_date  stock_code  close
2026-01-05  000001      10.20
2026-01-06  000001      10.10
```

优点：

- 适合长表存储；
- 适合多股票筛选和数据库写入；
- 日期字段含义直观。

### 日期作为索引

```text
index=trade_date
columns=[stock_code, close]
```

优点：

- 便于按日期切片；
- 便于时间序列运算；
- 适合单资产分析和宽表计算。

## 重点函数

```python
pd.to_datetime()

DataFrame.set_index()
DataFrame.reset_index()
DataFrame.sort_index()
DataFrame.sort_values()

DataFrame.loc[]
```

## 日期排序

金融数据必须先排序再计算收益率、移动平均和滚动波动率。

```python
prices = prices.sort_values(
    ["stock_code", "trade_date"]
).reset_index(drop=True)
```

单只股票使用日期索引后，可写为：

```python
stock = stock.sort_index()
```

## 时间范围筛选

### 日期为普通字段

```python
mask = (
    (prices["stock_code"] == "000001")
    & (prices["trade_date"] >= "2026-01-01")
    & (prices["trade_date"] <= "2026-03-31")
)

sample = prices.loc[mask]
```

### 日期为索引

```python
sample = stock.loc["2026-01-01":"2026-03-31"]
```

## 交易日与自然日

股票行情通常只包含交易日，不包含周末和休市日。

因此：

- 相邻两行不一定相差一个自然日；
- 不能通过自然日间隔判断是否缺失行情；
- 检查缺失交易日时需要使用交易日历；
- 滚动 5 行通常表示 5 个交易日，而不是 5 个自然日。

## 排序错误的影响

假设真实价格顺序为：

```text
10.00 → 10.50 → 10.20
```

若数据顺序被打乱为：

```text
10.50 → 10.00 → 10.20
```

计算出的收益率会完全错误。因此所有依赖前后顺序的计算都必须先检查日期排序。

## 排序检查

```python
is_sorted = (
    stock.index.is_monotonic_increasing
)

print(is_sorted)
```

多股票长表可分组检查：

```python
sorted_flags = (
    prices.groupby("stock_code")["trade_date"]
    .apply(lambda values: values.is_monotonic_increasing)
)
```

## 今日练习

提取股票 `000001` 在以下日期范围内的行情：

```text
2026-01-01 至 2026-03-31
```

要求：

1. 日期字段转换为日期类型；
2. 先按股票代码和日期升序排列；
3. 将单只股票的日期设置为索引；
4. 使用日期切片提取数据；
5. 检查索引是否单调递增；
6. 使用 `reset_index()` 恢复普通字段结构。

## 今日输出

- 一张按日期升序排列的单股票行情表；
- 一段日期范围筛选代码；
- 对交易日与自然日区别的说明。

## 自检问题

1. 为什么字符串日期应转换为日期类型？
2. 日期作为字段和作为索引分别适合什么场景？
3. 为什么计算收益率前必须排序？
4. 滚动 5 行为什么通常表示 5 个交易日？
