# 第 4 周第 4 天：DataFrame 筛选、排序与列操作

## 今日目标

- 使用标签和位置选择行列。
- 使用单条件和多条件筛选行情数据。
- 按股票代码、日期和数值字段排序。
- 创建、重命名和删除字段。

## 核心概念

### 选择列

```python
selected = prices[[
    "trade_date",
    "stock_code",
    "close",
    "volume",
]]
```

选择单列时通常返回 `Series`：

```python
close = prices["close"]
```

选择多列时返回 `DataFrame`：

```python
ohlc = prices[["open", "high", "low", "close"]]
```

## `loc` 与 `iloc`

### `loc`

`loc` 按标签或布尔条件选择数据。

```python
sample = prices.loc[
    prices["stock_code"] == "000001",
    ["trade_date", "close", "volume"],
]
```

### `iloc`

`iloc` 按整数位置选择数据。

```python
first_five_rows = prices.iloc[:5]
first_three_columns = prices.iloc[:, :3]
```

## 条件筛选

### 指定股票

```python
mask = prices["stock_code"] == "000001"
stock = prices.loc[mask]
```

### 成交量大于阈值

```python
large_volume = prices.loc[
    prices["volume"] > 1_000_000
]
```

### 收盘价高于开盘价

```python
up_days = prices.loc[
    prices["close"] > prices["open"]
]
```

### 多条件组合

```python
mask = (
    (prices["stock_code"] == "000001")
    & (prices["close"] > 10)
    & (prices["volume"] > 1_000_000)
)

result = prices.loc[mask]
```

注意：

- 使用 `&` 表示“并且”；
- 使用 `|` 表示“或者”；
- 每个条件需要使用括号包围；
- 不要使用 Python 的 `and` 和 `or` 连接 Series 条件。

## `query()`

```python
result = prices.query(
    "stock_code == '000001' and close > 10"
)
```

`query()` 可提高较简单条件的可读性，但复杂逻辑仍可使用布尔条件。

## 排序

### 按日期排序

```python
prices = prices.sort_values("trade_date")
```

### 多字段排序

```python
prices = prices.sort_values(
    ["stock_code", "trade_date"],
    ascending=[True, True],
)
```

### 按成交量降序

```python
largest_volume = prices.sort_values(
    "volume",
    ascending=False,
)
```

## 创建新字段

### 直接赋值

```python
prices["price_change"] = (
    prices["close"] - prices["open"]
)
```

### 使用 `assign()`

```python
prices = prices.assign(
    intraday_return=(
        prices["close"] / prices["open"] - 1
    )
)
```

## 修改列名

```python
prices = prices.rename(
    columns={
        "code": "stock_code",
        "date": "trade_date",
        "vol": "volume",
    }
)
```

## 删除字段

```python
prices = prices.drop(
    columns=["unused_column"]
)
```

若不希望修改原表，可保留默认行为并接收返回值。

## 避免链式赋值

不推荐：

```python
prices[prices["stock_code"] == "000001"]["flag"] = 1
```

推荐：

```python
mask = prices["stock_code"] == "000001"
prices.loc[mask, "flag"] = 1
```

## 今日练习

完成以下操作：

1. 筛选指定股票；
2. 筛选指定日期范围；
3. 筛选收盘价高于开盘价的交易日；
4. 筛选成交量大于设定阈值的记录；
5. 按股票代码和日期排序；
6. 创建日内收益率字段；
7. 重命名原始字段；
8. 删除无用字段。

示例：

```python
mask = (
    (prices["stock_code"] == "000001")
    & (prices["trade_date"] >= "2026-01-01")
    & (prices["trade_date"] <= "2026-03-31")
    & (prices["close"] > prices["open"])
    & (prices["volume"] > 1_000_000)
)

result = (
    prices.loc[mask]
    .sort_values(["stock_code", "trade_date"])
    .assign(
        intraday_return=lambda frame: (
            frame["close"] / frame["open"] - 1
        )
    )
)
```

## 今日输出

- 一段多条件行情筛选代码；
- 一张排序后的结果表；
- 一个新建的日内收益率字段。

## 自检问题

1. `loc` 和 `iloc` 有什么区别？
2. 多条件筛选为什么要为每个条件加括号？
3. 为什么量化计算前通常按股票和日期排序？
4. 如何避免链式赋值问题？
