# 第 5 周第 6 天：`merge` 与多表合并

## 今日目标

- 掌握行情表、股票信息表和因子表的合并方法。
- 理解 `left`、`inner`、`outer` 的区别。
- 检查合并主键是否唯一。
- 避免重复键导致数据行数异常增加。

## 一、常见数据表

行情表：

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

股票信息表：

```text
symbol
stock_name
industry
list_date
```

因子表：

```text
trade_date
symbol
momentum
volatility
```

## 二、按股票代码合并基本信息

```python
result = price_df.merge(
    stock_info,
    on="symbol",
    how="left",
    validate="many_to_one",
)
```

行情表中一只股票有多个交易日，而股票信息表中每只股票通常只有一行，因此关系应为多对一。

## 三、按日期和股票代码合并因子

```python
result = price_df.merge(
    factor_df,
    on=["trade_date", "symbol"],
    how="left",
    validate="one_to_one",
)
```

日频因子同时依赖交易日期和股票代码。只按 `symbol` 合并会让不同日期的数据错误匹配。

## 四、连接方式

### `left`

保留左表全部记录。量化研究中常用行情表作为左表，再补充行业和因子字段。

### `inner`

只保留左右表都存在的记录。使用后必须检查丢失了多少股票和交易日。

### `outer`

保留两张表的全部记录，适合排查数据覆盖差异和缺口。

## 五、检查主键重复

股票信息表：

```python
stock_info.duplicated(["symbol"]).sum()
```

因子表：

```python
factor_df.duplicated(
    ["trade_date", "symbol"]
).sum()
```

如果右表同一个主键出现两行，左表的一行就会匹配两次，导致合并后数据行数增加。

若左右表同一主键分别有 $m$ 行和 $n$ 行，多对多合并会产生：

$$
m \times n
$$

行匹配结果。

## 六、使用 `validate`

```text
one_to_one   一对一
one_to_many  一对多
many_to_one  多对一
many_to_many 多对多
```

研究流程中应尽量避免直接允许 `many_to_many`，除非已经明确理解数据关系。

## 七、检查匹配情况

```python
check = price_df.merge(
    factor_df,
    on=["trade_date", "symbol"],
    how="left",
    indicator=True,
)

print(check["_merge"].value_counts())
```

`_merge` 的含义：

```text
both        左右表均匹配
left_only   只存在于左表
right_only  只存在于右表
```

匹配率：

```python
match_rate = check["_merge"].eq("both").mean()
```

## 八、完整示例

```python
import pandas as pd


price_df = pd.DataFrame({
    "trade_date": pd.to_datetime([
        "2026-01-05", "2026-01-05",
        "2026-01-06", "2026-01-06",
    ]),
    "symbol": ["000001", "000002", "000001", "000002"],
    "close": [10.0, 20.0, 10.5, 19.5],
})

stock_info = pd.DataFrame({
    "symbol": ["000001", "000002"],
    "stock_name": ["示例股票1", "示例股票2"],
    "industry": ["行业1", "行业2"],
})

factor_df = pd.DataFrame({
    "trade_date": pd.to_datetime([
        "2026-01-05", "2026-01-05",
        "2026-01-06", "2026-01-06",
    ]),
    "symbol": ["000001", "000002", "000001", "000002"],
    "momentum": [0.10, 0.05, 0.12, 0.03],
    "volatility": [0.02, 0.04, 0.025, 0.045],
})

result = price_df.merge(
    stock_info,
    on="symbol",
    how="left",
    validate="many_to_one",
)

result = result.merge(
    factor_df,
    on=["trade_date", "symbol"],
    how="left",
    validate="one_to_one",
)

assert len(result) == len(price_df)
print(result)
```

## 九、字段类型检查

日期字段应统一为日期类型：

```python
price_df["trade_date"] = pd.to_datetime(
    price_df["trade_date"]
)
```

股票代码应保存为字符串，避免前导零丢失：

```python
price_df["symbol"] = (
    price_df["symbol"]
    .astype(str)
    .str.zfill(6)
)
```

## 十、常见错误

1. 因子表只按股票代码合并，导致不同日期相互匹配。
2. 合并前没有检查重复主键。
3. 股票代码被读取为整数，前导零丢失。
4. 两张表的日期字段类型不同。
5. 使用 `inner` 后没有检查样本损失。
6. 合并后没有核对数据行数。

## 十一、今日练习

1. 创建股票信息表并合并到行情表。
2. 创建因子表并按日期和股票代码合并。
3. 比较 `left`、`inner` 和 `outer` 的结果。
4. 使用 `indicator=True` 检查匹配情况。
5. 人为制造重复主键，观察 `validate` 的报错。
6. 将股票代码统一为 6 位字符串。
7. 检查合并前后数据行数。

## 十二、今日输出

```python
from collections.abc import Sequence

import pandas as pd


def safe_merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: str | Sequence[str],
    how: str = "left",
    validate: str = "one_to_one",
) -> pd.DataFrame:
    """检查字段和行数后合并两张表。"""
    keys = [on] if isinstance(on, str) else list(on)

    missing_left = set(keys).difference(left.columns)
    missing_right = set(keys).difference(right.columns)

    if missing_left:
        raise ValueError(
            f"左表缺少字段: {sorted(missing_left)}"
        )

    if missing_right:
        raise ValueError(
            f"右表缺少字段: {sorted(missing_right)}"
        )

    before_rows = len(left)

    result = left.merge(
        right,
        on=keys,
        how=how,
        validate=validate,
        indicator=True,
    )

    if how == "left" and len(result) != before_rows:
        raise ValueError("左连接后行数发生变化")

    return result
```

## 十三、检查清单

- [ ] 合并字段的数据类型一致。
- [ ] 股票代码保留前导零。
- [ ] 合并前检查了重复主键。
- [ ] 根据数据关系设置了 `validate`。
- [ ] 合并后检查了行数变化。
- [ ] 使用 `_merge` 检查了匹配情况。
- [ ] 没有无意中使用多对多连接。
