# 第 2 周第 6 天：NaN、无穷值与数据质量

## 今日目标

- 理解 `NaN`、`inf` 和真实零值的区别。
- 掌握 `np.isnan`、`np.isinf`、`np.isfinite`。
- 理解缺失价格如何影响相邻收益率。
- 学会在计算前进行数据质量检查。
- 避免把缺失值随意填成零。

---

## 一、三类特殊情况

### `NaN`

表示缺失或未定义：

```python
missing_price = np.nan
```

### `inf` 与 `-inf`

表示正无穷和负无穷，常由除零或溢出产生：

```python
positive_infinity = np.inf
negative_infinity = -np.inf
```

### 零值

零是一个真实数值，不等于缺失值。

对于普通股票价格，零通常不是有效交易价格；对于收益率，零表示真实平盘。

---

## 二、检测特殊值

```python
values = np.array(
    [10.0, np.nan, np.inf, -np.inf, 0.0]
)

print(np.isnan(values))
print(np.isinf(values))
print(np.isfinite(values))
```

`np.isfinite` 同时排除：

- `NaN`；
- `inf`；
- `-inf`。

统计有效值数量：

```python
valid_count = np.isfinite(values).sum()
```

---

## 三、缺失价格的传播

```python
prices = np.array(
    [10.0, np.nan, 10.4, 10.6],
    dtype=np.float64,
)

returns = prices[1:] / prices[:-1] - 1
```

结果中：

- 第 1 个收益率缺少当前价格；
- 第 2 个收益率缺少前一期价格；
- 第 3 个收益率可以正常计算。

一个缺失价格通常影响相邻两个收益区间。

---

## 四、为什么不能默认填零

```python
clean_returns = np.nan_to_num(
    returns,
    nan=0.0,
)
```

这等于假设缺失期间收益率为 0%。通常没有数据依据。

缺失可能来自：

- 停牌；
- 尚未上市；
- 数据源缺失；
- 日期未对齐；
- 文件损坏；
- 公司行为处理失败。

不同原因需要不同处理策略。

---

## 五、普通统计与忽略缺失值的统计

```python
np.mean(returns)
np.std(returns)
```

如果存在 `NaN`，结果通常为 `NaN`。

忽略缺失值：

```python
np.nanmean(returns)
np.nanstd(returns, ddof=1)
```

但忽略缺失值并不代表数据质量问题已经解决。还需要报告有效样本数量。

---

## 六、输入校验策略

### 严格模式

发现任何非有限值就拒绝：

```python
if not np.isfinite(prices).all():
    raise ValueError("价格不能包含 NaN 或无穷值")
```

适合：

- 基础模块；
- 单元测试；
- 要求连续完整价格的任务。

### 允许缺失模式

允许 `NaN`，但拒绝无穷值和非正有效价格：

```python
if np.isinf(prices).any():
    raise ValueError("价格不能包含无穷值")

valid_prices = prices[~np.isnan(prices)]

if np.any(valid_prices <= 0):
    raise ValueError("有效价格必须严格大于 0")
```

适合需要保留缺失状态的研究流程。

---

## 七、数据质量报告

```python
import numpy as np


def price_quality_report(
    prices: np.ndarray,
) -> dict[str, int | bool]:
    array = np.asarray(prices, dtype=np.float64)

    return {
        "total_count": int(array.size),
        "nan_count": int(np.isnan(array).sum()),
        "positive_inf_count": int(np.isposinf(array).sum()),
        "negative_inf_count": int(np.isneginf(array).sum()),
        "non_positive_finite_count": int(
            ((array <= 0) & np.isfinite(array)).sum()
        ),
        "all_finite": bool(np.isfinite(array).all()),
    }
```

在清洗数据前先生成报告，可以保留原始问题的证据。

---

## 八、安全除法

当分母可能为零时，可以使用 `np.divide`：

```python
result = np.full_like(
    numerator,
    np.nan,
    dtype=np.float64,
)

np.divide(
    numerator,
    denominator,
    out=result,
    where=denominator != 0,
)
```

对于股票收益率，更推荐在计算前直接拒绝非正价格，而不是让除零发生后再修补。

---

## 九、无穷值产生原因

```python
prices[1:] / prices[:-1]
```

如果前一期价格为零，可能产生 `inf`。

指数运算过大也可能溢出：

```python
np.exp(1000)
```

当程序出现无穷值时，应追查来源，而不是只在最终结果中删除。

---

## 十、清洗原则

1. 保留原始数据副本。
2. 先报告问题，再执行清洗。
3. 缺失值、错误值和极端值分开处理。
4. 清洗规则必须记录原因。
5. 不使用未来数据填补历史缺失。
6. 清洗后重新验证形状、日期和数值范围。
7. 累计净值对缺失处理非常敏感，不能机械忽略。

---

## 十一、允许 NaN 的收益率函数

```python
import numpy as np


def simple_returns_allow_nan(
    prices: np.ndarray,
) -> np.ndarray:
    """允许 NaN 自然传播的简单收益率。"""

    array = np.asarray(prices, dtype=np.float64)

    if array.ndim != 1:
        raise ValueError("prices 必须是一维数组")
    if array.size < 2:
        raise ValueError("至少需要两个价格")
    if np.isinf(array).any():
        raise ValueError("价格不能包含无穷值")

    valid_prices = array[~np.isnan(array)]

    if np.any(valid_prices <= 0):
        raise ValueError("有效价格必须严格大于 0")

    return array[1:] / array[:-1] - 1
```

---

## 十二、关键函数

| 函数 | 用法 |
|---|---|
| `np.isnan` | 检测 `NaN` |
| `np.isinf` | 检测正负无穷 |
| `np.isfinite` | 检测有限数 |
| `np.isposinf` | 检测正无穷 |
| `np.isneginf` | 检测负无穷 |
| `np.nanmean` | 忽略 `NaN` 计算均值 |
| `np.nanstd` | 忽略 `NaN` 计算标准差 |
| `np.nan_to_num` | 替换特殊值，使用前必须有明确依据 |
| `np.divide` | 支持条件化安全除法 |

---

## 今日练习

1. 构造同时包含 `NaN`、`inf`、零和正常价格的数组。
2. 生成数据质量报告。
3. 观察一个缺失价格影响几个收益率。
4. 比较严格模式与允许缺失模式。
5. 解释为什么缺失收益不能直接填零。
6. 为收益率函数加入无穷值和非正价格校验。

---

## 今日检查清单

- [ ] 能区分 `NaN`、`inf` 和零。
- [ ] 能使用 `np.isfinite` 检查数据。
- [ ] 理解缺失价格的相邻传播。
- [ ] 不把缺失值默认解释为零收益。
- [ ] 能先生成质量报告再清洗数据。
