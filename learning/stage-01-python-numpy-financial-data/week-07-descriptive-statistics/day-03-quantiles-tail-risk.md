# 第七周第三天：分位数、四分位距与尾部风险

## 一、今日学习目标

完成本课程后，应能够：

1. 理解百分位数和分位数。
2. 正确解释 1%、5%、25%、50%、75%、95% 和 99% 分位数。
3. 使用分位数描述股票收益率的左右尾部。
4. 理解四分位距及其稳健性。
5. 使用 IQR 方法识别异常收益候选值。
6. 比较不同股票的尾部风险。
7. 区分分位数风险与标准差风险。
8. 避免把历史 5% 分位数误解为最大亏损。
9. 使用 pandas 完成多股票分位数统计。
10. 计算最差 5% 交易日的平均收益。

今日核心问题：

> 在历史样本中，最差的 5% 交易日通常会跌到什么程度？

---

## 二、为什么还需要分位数

标准差描述收益率整体离散程度，但不能直接回答：

- 最差 5% 交易日跌了多少；
- 左尾风险是否比右尾机会更加严重；
- 最大跌幅是否远大于典型波动；
- 两只波动率接近的股票，哪只极端下跌更严重。

因此需要直接观察收益分布的位置和尾部。

---

## 三、分位数定义

将数据从小到大排列后，分位数表示处于某个累计比例位置的数值。

| 分位数 | 含义 |
|---:|---|
| 1% | 约 1% 的收益低于或等于该值 |
| 5% | 约 5% 的收益低于或等于该值 |
| 25% | 第一四分位数 $Q_1$ |
| 50% | 中位数 $Q_2$ |
| 75% | 第三四分位数 $Q_3$ |
| 95% | 约 95% 的收益低于该值，约 5% 高于该值 |
| 99% | 约 99% 的收益低于该值，约 1% 高于该值 |

例如：

```text
1%分位数：-5.80%
5%分位数：-3.20%
50%分位数：0.05%
95%分位数：3.40%
99%分位数：6.10%
```

解释：

- 约 5% 的历史交易日收益率低于 -3.20%；
- 约 5% 的历史交易日收益率高于 3.40%；
- 一半交易日收益率低于 0.05%。

---

## 四、分位数不是未来保证

历史 5% 分位数为 -3%，不能理解为：

- 未来最多跌 3%；
- 未来恰好只有 5% 的交易日跌破 3%；
- -3% 是风险上限。

正确含义是：

> 在当前历史样本中，约 5% 的有效观测低于该收益率。

未来市场状态变化、公司事件和制度变化都可能使历史分位数失效。

---

## 五、小样本与插值

小样本中，分位数可能落在两个观测值之间，软件会按照指定方法插值。

不同工具或插值方法可能产生略有差异的结果。研究中应：

- 统一使用同一计算工具和参数；
- 记录分位数算法；
- 避免用很短样本解释 1% 尾部；
- 比较股票时使用相似样本数量。

例如只有 20 个交易日时，5% 分位数大约由一个观测决定；1% 分位数几乎没有稳定意义。

---

## 六、pandas 与 NumPy 计算

pandas：

```python
returns.quantile(0.05)
returns.quantile([0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99])
```

NumPy：

```python
import numpy as np

np.quantile(
    returns.dropna(),
    [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99],
)

np.percentile(
    returns.dropna(),
    [1, 5, 25, 50, 75, 95, 99],
)
```

`quantile` 参数范围为 0 到 1，`percentile` 参数范围为 0 到 100。

---

## 七、四分位数与四分位距

第一四分位数：

$$
Q_1=Q_{0.25}
$$

第二四分位数：

$$
Q_2=Q_{0.50}
$$

第三四分位数：

$$
Q_3=Q_{0.75}
$$

四分位距：

$$
IQR=Q_3-Q_1
$$

若：

```text
Q1 = -1.20%
Q3 = 1.30%
```

则：

$$
IQR=1.30\%-(-1.20\%)=2.50\%
$$

IQR 表示中间 50% 的收益率覆盖区间宽度。

---

## 八、IQR 与标准差、极差的区别

| 指标 | 数据范围 | 极端值敏感度 |
|---|---|---|
| 标准差 | 全部观测 | 高 |
| 极差 | 最大值和最小值 | 极高 |
| IQR | 中间 50% | 较低 |
| 中位数 | 中间位置 | 很低 |

极差公式：

$$
Range=\max(r)-\min(r)
$$

极差非常容易被单个错误价格或极端事件扭曲，不能单独判断风险。

---

## 九、IQR 异常值规则

异常下界：

$$
Lower=Q_1-1.5\times IQR
$$

异常上界：

$$
Upper=Q_3+1.5\times IQR
$$

满足以下条件的观测被标记为异常候选：

$$
r<Lower
$$

或：

$$
r>Upper
$$

1.5 倍 IQR 是经验规则，不是金融定律。异常候选可能是：

- 真实涨停或跌停；
- 重大公告行情；
- 复牌跳跃；
- 除权造成的虚假收益；
- 错误价格；
- 复权方式错误。

发现异常后不能直接删除。

---

## 十、IQR 异常检测代码

```python
import pandas as pd


def detect_iqr_outliers(
    returns: pd.Series,
    multiplier: float = 1.5,
) -> pd.DataFrame:
    clean = returns.dropna()

    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr

    result = pd.DataFrame({"return": clean})
    result["is_lower_outlier"] = result["return"] < lower
    result["is_upper_outlier"] = result["return"] > upper
    result["is_outlier"] = (
        result["is_lower_outlier"]
        | result["is_upper_outlier"]
    )

    return result
```

---

## 十一、左尾、右尾与尾部不对称

左尾代表较大的负收益，常观察：

- 最小收益率；
- 1% 分位数；
- 5% 分位数；
- 左侧 IQR 异常数量。

右尾代表较大的正收益，常观察：

- 最大收益率；
- 95% 分位数；
- 99% 分位数；
- 右侧 IQR 异常数量。

辅助尾部不对称指标：

$$
TailAsymmetry=Q_{0.99}+Q_{0.01}
$$

- 结果为负：左尾绝对幅度可能更大；
- 结果为正：右尾绝对幅度可能更大。

该指标只是辅助工具，正式判断还应结合偏度。

---

## 十二、分位区间

中间 90% 收益区间宽度：

$$
Range_{90}=Q_{0.95}-Q_{0.05}
$$

中间 98% 收益区间宽度：

$$
Range_{98}=Q_{0.99}-Q_{0.01}
$$

它们比极差更稳健，因为不完全依赖最大和最小观测。

---

## 十三、分位数与历史模拟 VaR

若日收益率 5% 分位数为 -3.2%，则从损失的正数表达角度，可说历史 95% 单日 VaR 约为 3.2%。

但 VaR 只给出阈值，不说明跌破阈值后会亏多少，也不是最大亏损。

今天只需理解：

> 收益率左侧 5% 分位数与历史模拟 VaR 存在直接联系。

---

## 十四、最差 5% 平均收益

分位数只给出尾部阈值，可以进一步计算最差 5% 交易日的平均收益：

$$
LeftTailMean_{5\%}=E[r\mid r\le Q_{0.05}]
$$

Python：

```python
q05 = returns.quantile(0.05)
left_tail_mean = returns.loc[returns <= q05].mean()

q95 = returns.quantile(0.95)
right_tail_mean = returns.loc[returns >= q95].mean()
```

例如：

```text
5%分位数：-3.0%
最差5%交易日平均收益：-5.2%
```

说明 -3.0% 是进入左尾区域的阈值，而真正进入该区域后，平均跌幅约为 5.2%。

---

## 十五、多股票分位数统计

```python
quantile_stats = (
    df.groupby("code")["return"]
      .quantile([0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99])
      .unstack()
)

quantile_stats.columns = [
    "q01", "q05", "q25", "q50", "q75", "q95", "q99"
]

quantile_stats["iqr"] = (
    quantile_stats["q75"] - quantile_stats["q25"]
)
quantile_stats["range_90"] = (
    quantile_stats["q95"] - quantile_stats["q05"]
)
quantile_stats["range_98"] = (
    quantile_stats["q99"] - quantile_stats["q01"]
)
quantile_stats["tail_asymmetry"] = (
    quantile_stats["q99"] + quantile_stats["q01"]
)
```

---

## 十六、可复用函数

```python
import pandas as pd


def calculate_quantile_statistics(
    df: pd.DataFrame,
    code_col: str = "code",
    return_col: str = "return",
) -> pd.DataFrame:
    """按股票计算收益率分位数、IQR 与尾部统计。"""
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
    result = grouped.quantile(
        [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
    ).unstack()

    result.columns = [
        "q01", "q05", "q25", "q50", "q75", "q95", "q99"
    ]

    result["iqr"] = result["q75"] - result["q25"]
    result["range_90"] = result["q95"] - result["q05"]
    result["range_98"] = result["q99"] - result["q01"]
    result["tail_asymmetry"] = result["q99"] + result["q01"]
    result["min_return"] = grouped.min()
    result["max_return"] = grouped.max()
    result["sample_count"] = grouped.count()

    result["left_tail_mean_5pct"] = grouped.apply(
        lambda x: x.loc[x <= x.quantile(0.05)].mean()
    )
    result["right_tail_mean_5pct"] = grouped.apply(
        lambda x: x.loc[x >= x.quantile(0.95)].mean()
    )

    return result.reset_index()
```

---

## 十七、按股票添加 IQR 标记

```python
def add_iqr_outlier_flags(
    df: pd.DataFrame,
    code_col: str = "code",
    return_col: str = "return",
    multiplier: float = 1.5,
) -> pd.DataFrame:
    result = df.copy()
    grouped = result.groupby(code_col)[return_col]

    q1 = grouped.transform(lambda x: x.quantile(0.25))
    q3 = grouped.transform(lambda x: x.quantile(0.75))
    iqr = q3 - q1

    result["iqr_lower_bound"] = q1 - multiplier * iqr
    result["iqr_upper_bound"] = q3 + multiplier * iqr
    result["is_lower_outlier"] = (
        result[return_col] < result["iqr_lower_bound"]
    )
    result["is_upper_outlier"] = (
        result[return_col] > result["iqr_upper_bound"]
    )
    result["is_iqr_outlier"] = (
        result["is_lower_outlier"]
        | result["is_upper_outlier"]
    )

    return result
```

---

## 十八、箱线图

箱线图通常包含：

- 箱体下边缘：$Q_1$；
- 箱体中线：中位数；
- 箱体上边缘：$Q_3$；
- 箱体高度：IQR；
- 上下须：通常延伸到 1.5 倍 IQR 范围内的最远观测；
- 须外点：异常候选。

```python
import matplotlib.pyplot as plt

groups = [
    group["return"].dropna().values
    for _, group in df.groupby("code")
]
labels = [code for code, _ in df.groupby("code")]

plt.figure(figsize=(10, 6))
plt.boxplot(groups, labels=labels)
plt.ylabel("Daily Return")
plt.title("Return Distribution by Stock")
plt.show()
```

---

## 十九、A 股分析注意事项

1. 不同板块、ST 状态和历史时期的涨跌幅规则不同。
2. 未复权价格可能在除权除息日产生虚假大跌。
3. 停牌日被填为 0 会使中位数向 0 靠近、IQR 被低估。
4. 研究 1% 分位数需要足够长的样本。
5. 牛市、熊市和震荡市的尾部分布可能完全不同。
6. 比较股票时应统一样本区间、收益率定义和复权口径。

---

## 二十、联合标准差与分位数解释

### 标准差高，IQR 也高

日常收益和整体收益都比较分散，高波动并非只由少数异常值造成。

### 标准差高，IQR 较低

大部分时间收益集中，但少数极端收益抬高了标准差。

### 标准差低，但 5% 分位数很差

平时波动不大，但偶尔可能发生严重下跌，标准差可能低估左尾风险。

### 5% 分位数相似，但最差 5% 平均收益差异大

进入尾部的阈值相近，但跌破阈值后的损失严重程度不同。

---

## 二十一、实践任务

### 任务一：分位数汇总表

| 股票代码 | 样本数 | 1% | 5% | 25% | 50% | 75% | 95% | 99% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|

### 任务二：离散范围

| 股票代码 | IQR | 90%区间 | 98%区间 | 极差 |
|---|---:|---:|---:|---:|

### 任务三：尾部风险

| 股票代码 | 5%分位数 | 最差5%平均收益 | 95%分位数 | 最好5%平均收益 |
|---|---:|---:|---:|---:|

### 任务四：异常收益检查表

| 日期 | 股票代码 | 收益率 | 下界 | 上界 | 左侧异常 | 右侧异常 |
|---|---|---:|---:|---:|---|---|

并加入是否交易、停牌、涨跌停和复权因子变化等业务字段。

### 任务五：绘制箱线图

观察：

- 哪只股票箱体最高；
- 哪只股票中位数最高；
- 哪只股票左侧异常值最多；
- 哪只股票右侧异常值最多；
- 哪只股票上下须最不对称。

---

## 二十二、常见错误

1. 把 5% 分位数理解为 5% 的亏损。
2. 把 95% 分位数理解为 95% 的投资收益。
3. 把 5% 分位数当作最大亏损。
4. 使用过短样本计算 1% 分位数。
5. 发现 IQR 异常值后直接删除。
6. 不同股票使用不同时间区间。
7. 混淆收益率小数和百分数。
8. 只使用极差判断风险。

---

## 二十三、数学练习

若：

```text
Q1 = -1.2%
Q3 = 1.4%
```

则：

$$
IQR=1.4\%-(-1.2\%)=2.6\%
$$

异常下界：

$$
-1.2\%-1.5\times2.6\%=-5.1\%
$$

异常上界：

$$
1.4\%+1.5\times2.6\%=5.3\%
$$

收益低于 -5.1% 或高于 5.3% 会被标记为 IQR 异常候选。

---

## 二十四、自测题

1. 5% 分位数表示什么？
2. 95% 分位数表示什么？
3. 中位数对应哪个分位数？
4. IQR 如何计算？
5. 为什么 IQR 比极差稳健？
6. IQR 异常值一定是数据错误吗？
7. 5% 分位数是否代表最大亏损？
8. 为什么还要计算最差 5% 平均收益？
9. 分位数是否会随市场环境变化？
10. 分位数和标准差谁更好？

---

## 二十五、今日验收标准

- 能正确解释常用分位数；
- 能区分分位位置和收益率数值；
- 能计算 $Q_1$、$Q_2$、$Q_3$ 和 IQR；
- 能计算 IQR 异常上下界；
- 能使用 pandas 计算多股票分位数；
- 能计算 90% 和 98% 分位区间；
- 能计算最差 5% 交易日平均收益；
- 能区分分位数、标准差和极差；
- 能绘制和解释箱线图；
- 能识别需要进一步核验的极端收益。

---

## 二十六、今日最终产出

```text
notebooks/week07_day03_quantiles_tail_risk.ipynb
src/statistics.py
```

建议实现：

```python
calculate_quantile_statistics()
add_iqr_outlier_flags()
detect_iqr_outliers()
```

今日最重要的结论：

> 标准差告诉我们收益整体有多分散，分位数告诉我们分布的具体位置；5% 分位数描述左尾阈值，而最差 5% 平均收益描述真正进入尾部后的损失程度。
