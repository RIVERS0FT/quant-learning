# 第 5 周第 1 天：`groupby` 多股票分组计算

## 今日目标

- 理解多股票行情为什么必须按股票代码分组计算。
- 掌握 `sort_values()`、`groupby()`、`pct_change()` 和 `transform()`。
- 能够计算每只股票独立的 1 日收益率。
- 能够识别跨股票计算造成的数据污染。

## 一、问题背景

假设行情表中同时存在多只股票：

```text
trade_date  symbol  close
2026-01-01  000001  10.0
2026-01-02  000001  10.5
2026-01-01  000002  20.0
2026-01-02  000002  19.0
```

不同股票的价格序列彼此独立，因此不能直接把整列收盘价当作一条连续时间序列。

### 错误写法

```python
df["return_1d"] = df["close"].pct_change()
```

当数据从 `000001` 切换到 `000002` 时，这种写法可能用 `000001` 的最后一个收盘价计算 `000002` 的第一天收益率。

### 正确写法

```python
df["return_1d"] = (
    df.groupby("symbol")["close"]
      .pct_change()
)
```

`groupby("symbol")` 保证每只股票只使用自己的历史价格。

## 二、计算收益率前必须排序

时间序列计算依赖数据顺序。推荐先按股票代码和交易日期排序：

```python
df = df.sort_values(["symbol", "trade_date"])
```

排序后的结构应当是：

```text
000001 的全部日期，从早到晚
000002 的全部日期，从早到晚
000003 的全部日期，从早到晚
```

如果日期顺序错误，即使使用了 `groupby()`，收益率仍然会计算错误。

## 三、核心函数

### 1. `sort_values()`

```python
df = df.sort_values(
    ["symbol", "trade_date"]
).reset_index(drop=True)
```

用途：

- 保证每只股票内部按日期升序排列。
- 为 `shift()`、`pct_change()` 和 `rolling()` 提供正确顺序。
- `reset_index(drop=True)` 让排序后的行索引重新连续编号。

### 2. `groupby()`

```python
groups = df.groupby("symbol")
```

含义：按照 `symbol` 将数据拆分为多个股票组。

常见用法：

```python
df.groupby("symbol")["close"].mean()
df.groupby("symbol")["close"].max()
df.groupby("symbol")["volume"].sum()
```

### 3. `pct_change()`

```python
df["return_1d"] = (
    df.groupby("symbol")["close"]
      .pct_change()
)
```

简单收益率为：

$$
r_t = \frac{P_t}{P_{t-1}} - 1
$$

其中：

- $P_t$：当前交易日收盘价。
- $P_{t-1}$：上一交易日收盘价。
- $r_t$：当前交易日简单收益率。

### 4. `transform()`

`transform()` 会将分组计算结果对齐回原始 DataFrame 的每一行。

```python
df["mean_return"] = (
    df.groupby("symbol")["return_1d"]
      .transform("mean")
)
```

结果中，同一只股票的每一行都会得到该股票的平均日收益率。

与聚合的区别：

```python
# 聚合后每只股票只保留一行
summary = df.groupby("symbol")["return_1d"].mean()

# transform 后仍保留原始行数
result = df.groupby("symbol")["return_1d"].transform("mean")
```

## 四、完整示例

```python
import pandas as pd


data = {
    "trade_date": [
        "2026-01-01", "2026-01-02", "2026-01-03",
        "2026-01-01", "2026-01-02", "2026-01-03",
    ],
    "symbol": [
        "000001", "000001", "000001",
        "000002", "000002", "000002",
    ],
    "close": [10.0, 10.5, 10.2, 20.0, 19.0, 19.5],
}

df = pd.DataFrame(data)
df["trade_date"] = pd.to_datetime(df["trade_date"])

df = (
    df.sort_values(["symbol", "trade_date"])
      .reset_index(drop=True)
)

df["return_1d"] = (
    df.groupby("symbol")["close"]
      .pct_change()
)

df["mean_return"] = (
    df.groupby("symbol")["return_1d"]
      .transform("mean")
)

print(df)
```

## 五、结果检查

每只股票的第一条记录都没有上一交易日，因此收益率应为缺失值：

```python
first_rows = df.groupby("symbol").head(1)
assert first_rows["return_1d"].isna().all()
```

检查分组前后行数是否一致：

```python
assert len(df) == len(data["close"])
```

检查股票和日期组合是否重复：

```python
duplicate_count = df.duplicated(
    ["symbol", "trade_date"]
).sum()

assert duplicate_count == 0
```

## 六、今日练习

1. 创建包含 3 只股票、每只股票 10 个交易日的模拟行情。
2. 打乱数据顺序，再使用 `sort_values()` 恢复正确顺序。
3. 分别使用“分组”和“不分组”两种方式计算收益率。
4. 找出不分组计算中跨股票产生的错误值。
5. 计算每只股票的平均收益率、最高收益率和最低收益率。
6. 使用 `transform()` 将每只股票的平均收益率写回原表。

## 七、今日输出

建议创建：

```text
src/features/group_features.py
```

参考函数：

```python
import pandas as pd


def add_group_return_features(
    df: pd.DataFrame,
    symbol_col: str = "symbol",
    date_col: str = "trade_date",
    price_col: str = "close",
) -> pd.DataFrame:
    """按股票分组计算 1 日收益率和平均收益率。"""
    required = {symbol_col, date_col, price_col}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"缺少字段: {sorted(missing)}")

    result = df.copy()
    result = result.sort_values(
        [symbol_col, date_col]
    ).reset_index(drop=True)

    result["return_1d"] = (
        result.groupby(symbol_col)[price_col]
              .pct_change()
    )

    result["mean_return"] = (
        result.groupby(symbol_col)["return_1d"]
              .transform("mean")
    )

    return result
```

## 八、检查清单

- [ ] 数据已经按股票代码和日期排序。
- [ ] 收益率使用 `groupby("symbol")` 计算。
- [ ] 每只股票第一天的收益率为缺失值。
- [ ] 不存在重复的股票代码与交易日期组合。
- [ ] 分组计算前后数据行数保持不变。
- [ ] 能解释聚合结果与 `transform()` 结果的区别。
