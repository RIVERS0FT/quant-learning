# 第 4 周第 5 天：长表与宽表

## 今日目标

- 理解金融数据长表和宽表的结构差异。
- 使用 `pivot` 和 `pivot_table` 将长表转换为宽表。
- 使用 `melt` 将宽表还原成长表。
- 根据研究任务选择合适的数据结构。

## 长表

长表中每一行表示某只股票在某一天的一条记录。

```text
trade_date  stock_code  close
2026-01-05  000001      10.20
2026-01-05  000002      15.30
2026-01-06  000001      10.10
2026-01-06  000002      15.60
```

长表适合：

- 保存原始行情；
- 按股票和日期筛选；
- 与行业、市场和财务信息连接；
- 写入数据库；
- 使用 `groupby` 进行分组计算。

## 宽表

宽表中每一行表示一个日期，每一列表示一只股票。

```text
trade_date  000001  000002
2026-01-05  10.20   15.30
2026-01-06  10.10   15.60
```

宽表适合：

- 多资产收益率计算；
- 相关系数矩阵；
- 协方差矩阵；
- 组合权重计算；
- NumPy 矩阵运算。

## 使用 `pivot()`

```python
close_matrix = prices.pivot(
    index="trade_date",
    columns="stock_code",
    values="close",
)
```

结果：

- 行索引是交易日期；
- 列名是股票代码；
- 单元格是收盘价。

## `pivot()` 的唯一性要求

对于同一个 `(trade_date, stock_code)` 组合，只能有一个 `close` 值。

若存在重复记录，`pivot()` 会报错。转换前应检查主键是否重复：

```python
duplicate_mask = prices.duplicated(
    subset=["trade_date", "stock_code"],
    keep=False,
)

duplicates = prices.loc[duplicate_mask]
```

## 使用 `pivot_table()`

若数据中存在重复记录，可以使用聚合规则：

```python
close_matrix = prices.pivot_table(
    index="trade_date",
    columns="stock_code",
    values="close",
    aggfunc="last",
)
```

但必须明确为什么允许聚合，不能通过 `pivot_table()` 隐藏数据质量问题。

## 从宽表还原成长表

```python
close_long = (
    close_matrix
    .reset_index()
    .melt(
        id_vars="trade_date",
        var_name="stock_code",
        value_name="close",
    )
)
```

若宽表中存在缺失值，可根据任务决定是否删除：

```python
close_long = close_long.dropna(
    subset=["close"]
)
```

## `stack()` 与 `unstack()`

### `stack()`

将列标签压入行索引：

```python
stacked = close_matrix.stack()
```

### `unstack()`

将索引层级展开为列：

```python
restored = stacked.unstack()
```

这两个函数常用于多级索引结构转换。

## 长宽表转换检查

转换后应检查：

- 日期数量是否一致；
- 股票数量是否一致；
- 非空价格数量是否一致；
- 随机抽样值是否一致；
- 股票代码是否仍为字符串；
- 日期是否保持升序。

示例：

```python
original_count = prices["close"].notna().sum()
wide_count = close_matrix.notna().sum().sum()

assert original_count == wide_count
```

## 今日练习

将多股票收盘价数据完成以下转换：

1. 从长表转换为宽表；
2. 检查重复主键；
3. 检查宽表日期和股票数量；
4. 从宽表还原成长表；
5. 按股票代码和日期排序；
6. 抽样检查转换前后价格是否一致。

```python
key_columns = ["trade_date", "stock_code"]

assert not prices.duplicated(key_columns).any()

close_matrix = prices.pivot(
    index="trade_date",
    columns="stock_code",
    values="close",
)

restored = (
    close_matrix
    .reset_index()
    .melt(
        id_vars="trade_date",
        var_name="stock_code",
        value_name="close",
    )
    .dropna(subset=["close"])
    .sort_values(["stock_code", "trade_date"])
    .reset_index(drop=True)
)
```

## 今日输出

```text
data/processed/daily_prices.parquet
data/processed/close_matrix.parquet
```

以及一段可重复运行的长宽表转换脚本。

## 自检问题

1. 长表和宽表分别适合哪些量化场景？
2. 为什么 `pivot()` 要求主键唯一？
3. `pivot_table()` 为什么不能用来掩盖重复数据？
4. 如何验证长宽表转换没有丢失数据？
