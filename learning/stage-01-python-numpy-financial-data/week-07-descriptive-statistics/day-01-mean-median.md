# 第七周第一天：均值、中位数与收益率中心位置

## 一、今日学习目标

完成本课程后，应能够：

1. 理解算术平均数与中位数的计算方法。
2. 解释均值和中位数在股票收益分析中的含义。
3. 判断均值是否被极端收益扭曲。
4. 使用均值、中位数和分位数描述收益率的中心位置。
5. 比较多只股票的平均收益与典型收益。
6. 使用 pandas 完成分组统计。
7. 区分平均收益与累计收益。
8. 避免把短期历史均值误认为稳定的未来收益。

今日核心问题：

> 一组股票收益率的“正常水平”应该怎样描述？

---

## 二、为什么研究收益率的中心位置

假设一只股票过去五天的收益率为：

```text
-1%、0%、0.5%、1%、10%
```

平均收益率为：

$$
\bar r=\frac{-1\%+0\%+0.5\%+1\%+10\%}{5}=2.1\%
$$

但五天中有四天的收益率都低于 2.1%。这说明均值被单日 10% 的涨幅明显抬高。

因此分析股票收益时，不能只计算均值，还需要观察：

- 中位数；
- 最大值和最小值；
- 分位数；
- 极端收益；
- 上涨、下跌和零收益天数比例。

---

## 三、算术平均数

### 1. 定义

假设有 $n$ 个收益率 $r_1,r_2,\ldots,r_n$，算术平均数为：

$$
\bar r=\frac{1}{n}\sum_{t=1}^{n}r_t
$$

示例：

```text
1%、2%、-1%、0%、3%
```

平均收益率：

$$
\bar r=\frac{1\%+2\%-1\%+0\%+3\%}{5}=1\%
$$

### 2. 金融含义

日收益率均值描述：

> 在当前样本区间内，每个交易日收益率的平均水平。

它可以用于：

- 比较不同股票的历史平均日收益；
- 计算波动率、协方差等统计量；
- 描述策略样本期内的平均表现；
- 计算夏普比率等风险调整指标。

但平均收益不代表：

- 股票每天都会获得该收益；
- 未来一定能够获得该收益；
- 该收益具有统计显著性；
- 投资者实际获得的复合收益；
- 风险已经被考虑。

### 3. 均值的平衡点性质

均值可以理解为数据的平衡点：

$$
\sum_{t=1}^{n}(r_t-\bar r)=0
$$

正离差和负离差会互相抵消。

### 4. 均值的主要缺点

均值对极端值敏感。

股票 A：

```text
-1%、0%、0.5%、1%、1.5%
```

平均收益为 0.4%。

股票 B：

```text
-1%、0%、0.5%、1%、10%
```

平均收益为 2.1%。

股票 B 的高均值主要来自一次极端上涨。看到高均值时，需要继续检查：

1. 高收益是否由少数交易日贡献；
2. 删除最大收益后，均值是否明显下降；
3. 中位数是否远低于均值；
4. 样本数量是否足够；
5. 是否存在涨停、复牌或除权数据；
6. 该收益是否具有可重复性。

---

## 四、中位数

### 1. 定义

中位数是将数据从小到大排列后，位于中间位置的数。

奇数个观测：

```text
-2%、-1%、0%、1%、8%
```

中位数为 0%。

偶数个观测：

```text
-2%、-1%、1%、8%
```

中位数为：

$$
\frac{-1\%+1\%}{2}=0\%
$$

### 2. 金融含义

中位数描述：

> 一半交易日收益率低于该值，另一半交易日收益率高于该值。

因此中位数通常更接近“典型交易日”的收益水平。

### 3. 中位数的稳健性

原始数据：

```text
-1%、0%、0.5%、1%、2%
```

均值和中位数均为 0.5%。

将 2% 改为 20%：

```text
-1%、0%、0.5%、1%、20%
```

新的均值为 4.1%，中位数仍为 0.5%。

单个极端值大幅改变均值，却没有改变中位数。

### 4. 中位数的局限

中位数不反映收益幅度。

股票 A：

```text
-1%、-0.5%、0%、0.5%、1%
```

股票 B：

```text
-10%、-0.5%、0%、0.5%、10%
```

两者中位数都是 0%，但股票 B 风险明显更高。因此中位数不能代替波动率、分位数和极端收益分析。

---

## 五、均值与中位数比较

| 指标 | 均值 | 中位数 |
|---|---|---|
| 计算方式 | 所有数据求和后除以数量 | 排序后寻找中间位置 |
| 使用所有数值大小 | 是 | 主要使用排序位置 |
| 极端值敏感性 | 高 | 低 |
| 金融解释 | 样本期平均收益 | 典型交易日收益 |
| 能否单独描述风险 | 不能 | 不能 |

实际研究通常同时报告：

```text
均值 + 中位数 + 标准差 + 分位数
```

---

## 六、均值与中位数对分布形态的初步提示

### 情况一：均值约等于中位数

可能说明分布较为对称。

### 情况二：均值明显大于中位数

可能说明：

- 存在较大的正收益；
- 右侧尾部较长；
- 少数大涨日抬高均值。

### 情况三：均值明显小于中位数

可能说明：

- 存在较大的负收益；
- 左侧尾部较长；
- 少数大跌日拉低均值。

注意：均值与中位数的关系只能提供线索，不能替代偏度计算。

---

## 七、平均收益与累计收益的区别

假设两天收益率为：

```text
第一天：+10%
第二天：-10%
```

算术平均收益率为：

$$
\frac{10\%-10\%}{2}=0\%
$$

若初始资金为 100 元：

$$
100\times1.10=110
$$

$$
110\times0.90=99
$$

累计收益为：

$$
\frac{99}{100}-1=-1\%
$$

累计收益应计算为：

$$
R=\prod_{t=1}^{n}(1+r_t)-1
$$

不能使用 $n\times\bar r$ 代替累计收益。

---

## 八、样本均值的不稳定性

股票日收益率均值通常很小，而日波动率通常远高于均值。例如：

```text
平均日收益率：0.05%
日收益率标准差：2.00%
```

短期样本中的均值很容易受到随机波动影响，因此报告均值时必须同时说明：

- 样本开始日期；
- 样本结束日期；
- 有效交易日数量；
- 平均收益；
- 标准差；
- 后续将学习的标准误和置信区间。

---

## 九、上涨、下跌和零收益比例

上涨天数比例：

$$
P(r>0)=\frac{\text{收益率大于 0 的交易日数量}}{\text{有效交易日总数}}
$$

Python 中布尔值可以直接求均值：

```python
positive_ratio = (returns > 0).mean()
negative_ratio = (returns < 0).mean()
zero_ratio = (returns == 0).mean()
```

注意：上涨比例高不代表策略一定赚钱。高胜率策略仍可能因为少数大额亏损而整体亏损。

---

## 十、Python 核心函数

```python
returns.mean()
returns.median()
returns.quantile(0.50)
returns.count()
returns.min()
returns.max()
returns.describe()
```

单只股票示例：

```python
import pandas as pd

returns = pd.Series(
    [-0.01, 0.00, 0.005, 0.01, 0.10],
    name="daily_return",
)

print(f"平均收益率：{returns.mean():.2%}")
print(f"中位数：{returns.median():.2%}")
print(f"最小收益率：{returns.min():.2%}")
print(f"最大收益率：{returns.max():.2%}")
print(f"上涨比例：{(returns > 0).mean():.2%}")
print(f"下跌比例：{(returns < 0).mean():.2%}")
```

---

## 十一、多股票分组统计

行情长表包含：

```text
date, code, close
```

先排序并计算日收益率：

```python
df = df.sort_values(["code", "date"])
df["return"] = df.groupby("code")["close"].pct_change()
```

分组统计：

```python
stats = (
    df.groupby("code")["return"]
      .agg(
          sample_count="count",
          mean_return="mean",
          median_return="median",
          min_return="min",
          max_return="max",
      )
)

ratio_stats = (
    df.groupby("code")["return"]
      .agg(
          positive_ratio=lambda x: (x.dropna() > 0).mean(),
          negative_ratio=lambda x: (x.dropna() < 0).mean(),
          zero_ratio=lambda x: (x.dropna() == 0).mean(),
      )
)

result = stats.join(ratio_stats)
result["mean_median_diff"] = (
    result["mean_return"] - result["median_return"]
)
```

---

## 十二、可复用函数

```python
import pandas as pd


def calculate_center_statistics(
    df: pd.DataFrame,
    code_col: str = "code",
    return_col: str = "return",
) -> pd.DataFrame:
    """按股票代码计算收益率中心位置统计量。"""
    required_columns = {code_col, return_col}

    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"缺少必要字段：{sorted(missing)}")

    data = df[[code_col, return_col]].copy()
    data[return_col] = pd.to_numeric(
        data[return_col],
        errors="coerce",
    )

    grouped = data.groupby(code_col)[return_col]

    result = grouped.agg(
        sample_count="count",
        mean_return="mean",
        median_return="median",
        min_return="min",
        max_return="max",
    )

    result["positive_ratio"] = grouped.apply(
        lambda x: (x.dropna() > 0).mean()
    )
    result["negative_ratio"] = grouped.apply(
        lambda x: (x.dropna() < 0).mean()
    )
    result["zero_ratio"] = grouped.apply(
        lambda x: (x.dropna() == 0).mean()
    )
    result["mean_median_diff"] = (
        result["mean_return"] - result["median_return"]
    )

    return result.reset_index()
```

---

## 十三、缺失值注意事项

使用 `pct_change()` 时，每只股票第一条收益率通常为缺失值，因为没有上一期价格。

- `Series.count()`：统计非缺失值；
- `len(series)`：统计全部行，包括缺失值。

因此两者可能不同。

---

## 十四、极端值影响实验

```python
import pandas as pd

returns = pd.Series([-0.01, -0.005, 0.00, 0.005, 0.01])
returns_with_outlier = pd.concat(
    [returns, pd.Series([0.10])],
    ignore_index=True,
)

print("原始均值：", returns.mean())
print("原始中位数：", returns.median())
print("加入极端值后的均值：", returns_with_outlier.mean())
print("加入极端值后的中位数：", returns_with_outlier.median())
```

继续将 10% 改为 -10%，观察均值和中位数的变化。

---

## 十五、截尾均值

截尾均值先删除两端一定比例的数据，再计算均值。

```python
from scipy.stats import trim_mean

trimmed_mean = trim_mean(
    returns.dropna(),
    proportiontocut=0.05,
)
```

截尾均值比普通均值更稳健，同时比中位数使用更多数值信息。今天只需理解概念。

---

## 十六、A 股收益分析中的特殊问题

### 1. 涨跌停

连续涨停或跌停可能显著改变均值，需要检查高均值是否由少数封板交易日造成。

### 2. 停牌

停牌收益若被错误填为 0，会影响中位数和零收益比例。

### 3. 除权除息

未复权价格可能在除权日产生虚假大跌，影响均值、极值和异常统计。

### 4. 新股上市

新股上市初期的极端涨跌不应与成熟交易阶段简单混合。

### 5. 幸存者偏差

只分析当前仍上市股票，可能遗漏退市或经营失败公司，从而高估历史平均表现。

---

## 十七、实践任务

使用至少 5 只股票、至少一年日线数据完成：

### 任务一：基础统计表

| 股票代码 | 样本数 | 平均收益率 | 中位数 | 均值减中位数 |
|---|---:|---:|---:|---:|

### 任务二：涨跌比例表

| 股票代码 | 上涨比例 | 下跌比例 | 零收益比例 |
|---|---:|---:|---:|

### 任务三：极端值影响

对每只股票计算：

1. 原始平均收益率；
2. 删除最大单日收益后的均值；
3. 删除最小单日收益后的均值；
4. 同时删除最大和最小收益后的均值。

```python
def mean_without_extremes(series: pd.Series) -> pd.Series:
    clean = series.dropna()

    if len(clean) < 3:
        return pd.Series({
            "original_mean": clean.mean(),
            "without_max": float("nan"),
            "without_min": float("nan"),
            "without_both": float("nan"),
        })

    max_index = clean.idxmax()
    min_index = clean.idxmin()

    return pd.Series({
        "original_mean": clean.mean(),
        "without_max": clean.drop(index=max_index).mean(),
        "without_min": clean.drop(index=min_index).mean(),
        "without_both": clean.drop(
            index=[max_index, min_index]
        ).mean(),
    })
```

### 任务四：写出至少三条统计结论

结论必须包含：

- 股票代码；
- 样本区间；
- 具体指标和数值；
- 对数值的解释；
- 必要的限制条件。

---

## 十八、常见错误

1. 把平均日收益直接乘以 252 当作精确年化收益。
2. 认为均值越高股票就越好。
3. 忽略样本数量和样本区间。
4. 把中位数当作平均盈利。
5. 使用 `returns >= 0` 计算上涨比例，将零收益日算成上涨日。
6. 发现极端值后直接删除，不检查真实市场事件和数据质量。

---

## 十九、数学练习

给定收益率：

```text
-2%、-1%、0%、1%、7%
```

计算结果：

$$
\bar r=\frac{-2\%-1\%+0\%+1\%+7\%}{5}=1\%
$$

- 中位数：0%；
- 均值减中位数：1%；
- 上涨比例：40%；
- 下跌比例：40%；
- 零收益比例：20%。

另一个重要例子：

```text
股票 A：1%、1%、1%、1%、1%
股票 B：-5%、0%、0%、0%、10%
```

两者均值都是 1%，但股票 A 中位数为 1%，股票 B 中位数为 0%，且股票 B 风险明显更高。

---

## 二十、自测题

1. 中位数是否使用所有观测值的数值大小？
2. 为什么股票收益分析不能只看均值？
3. 均值明显高于中位数可能说明什么？
4. 平均收益为 0，累计收益是否一定为 0？
5. 中位数能否描述风险？
6. 上涨比例超过 50%，策略是否一定赚钱？
7. 为什么需要报告样本数量？

参考结论：均值容易受极端值影响，中位数更稳健；平均收益不等于累计收益；胜率不能代替盈亏幅度和尾部风险。

---

## 二十一、今日验收标准

- 能手工计算均值和中位数；
- 能解释均值对极端值敏感的原因；
- 能说明中位数的金融含义；
- 能计算上涨、下跌和零收益比例；
- 能区分平均收益和累计收益；
- 能使用 `groupby()` 和 `agg()` 进行多股票统计；
- 能生成多股票中心位置统计表；
- 能写出至少三条带数据证据的结论；
- 能说明为什么不能仅按平均收益选择股票。

---

## 二十二、今日最终产出

```text
notebooks/week07_day01_center_statistics.ipynb
src/statistics.py
```

Notebook 至少包含：

1. 数据读取与字段检查；
2. 日收益率计算；
3. 单只股票均值和中位数示例；
4. 多股票分组统计；
5. 上涨、下跌和零收益比例；
6. 极端值对均值影响实验；
7. 结果汇总表；
8. 三条以上分析结论。

今日最重要的结论：

> 均值描述样本期的平均收益，但容易被极端值扭曲；中位数更接近典型交易日表现。两者必须结合波动率、分位数和样本数量共同解释。
