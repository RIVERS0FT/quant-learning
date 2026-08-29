# 第八周 · 第四天

## 标准差、标准误与置信区间

---

## 1. 今日学习目标

完成今天的学习后，你需要能够：

- 区分标准差和标准误
- 理解样本均值为什么存在不确定性
- 掌握均值标准误的计算公式
- 理解置信水平和置信区间
- 掌握正态分布置信区间
- 掌握 $t$ 分布置信区间
- 理解样本量对置信区间宽度的影响
- 理解置信水平对置信区间宽度的影响
- 使用 NumPy 和 SciPy 计算均值置信区间
- 正确解释 95% 置信区间
- 避免对置信区间的常见误解

---

# 一、标准差

## 2. 标准差的含义

标准差描述原始数据围绕平均值的离散程度。

总体标准差记为：

$$
\sigma
$$

样本标准差记为：

$$
s
$$

样本标准差公式为：

$$
s=\sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar{x})^2}
$$

其中：

- $x_i$：第 $i$ 个样本值
- $\bar{x}$：样本均值
- $n$：样本数量
- $s$：样本标准差

---

## 3. 金融中的标准差

在金融数据中，收益率标准差通常被用作波动率。

例如，某股票的日收益率标准差为：

$$
s=0.02
$$

即：

$$
s=2\%
$$

这表示该股票日收益率通常会在平均收益率附近产生约 2% 量级的波动。

标准差描述的是：

> 单个收益率数据的波动程度。

它不直接表示平均收益率估计得是否准确。

---

## 4. 两组收益率示例

### 股票 A

```text
0.8%、1.0%、1.2%、0.9%、1.1%
```

### 股票 B

```text
-4%、6%、-2%、7%、-2%
```

两组数据的平均收益可能比较接近，但股票 B 的数据更加分散。

因此：

$$
s_B>s_A
$$

股票 B 的波动率更高。

---

# 二、标准误

## 5. 标准误的含义

标准误描述的是：

> 样本统计量在重复抽样中的波动程度。

今天重点研究样本均值的标准误。

样本均值标准误记为：

$$
SE(\bar{x})
$$

如果总体标准差已知：

$$
SE(\bar{x})=\frac{\sigma}{\sqrt{n}}
$$

如果总体标准差未知，通常使用样本标准差估计：

$$
SE(\bar{x})=\frac{s}{\sqrt{n}}
$$

---

## 6. 标准差和标准误的区别

| 项目 | 标准差 | 标准误 |
|---|---|---|
| 常见符号 | $s$ 或 $\sigma$ | $SE$ |
| 描述对象 | 原始数据 | 样本统计量 |
| 衡量内容 | 单个数据的离散程度 | 统计量估计的不确定性 |
| 是否受样本量直接影响 | 不一定 | 明显受影响 |
| 样本量增加时 | 不一定变小 | 通常变小 |
| 金融解释 | 收益率波动 | 平均收益估计精度 |

---

## 7. 核心区别

标准差回答：

> 每个交易日的收益率波动有多大？

标准误回答：

> 我们计算出来的平均收益率有多稳定？

因此：

$$
\text{标准差}\neq\text{标准误}
$$

也不能把标准误称为股票波动率。

---

# 三、标准误的计算

## 8. 基础示例

假设某策略有 100 笔交易：

$$
n=100
$$

样本收益率标准差为：

$$
s=2\%
$$

则平均收益率的标准误为：

$$
SE=\frac{2\%}{\sqrt{100}}
$$

$$
=\frac{2\%}{10}
$$

$$
=0.2\%
$$

这表示样本平均收益率在重复抽样中的典型波动约为 0.2%。

---

## 9. 样本量对标准误的影响

标准误公式为：

$$
SE=\frac{s}{\sqrt{n}}
$$

假设标准差固定为：

$$
s=2\%
$$

| 样本量 $n$ | 标准误 |
|---:|---:|
| 25 | 0.40% |
| 100 | 0.20% |
| 400 | 0.10% |
| 1,600 | 0.05% |

随着样本量增加，标准误下降。

---

## 10. 标准误下降速度

标准误与样本量的平方根成反比：

$$
SE\propto\frac{1}{\sqrt{n}}
$$

如果希望标准误下降一半，需要将样本量扩大到原来的四倍。

例如：

$$
n=100
$$

扩大到：

$$
n=400
$$

标准误才会下降一半。

---

## 11. 增加样本量的边际收益

假设标准差不变。

从 25 个样本增加到 100 个样本：

$$
SE
$$

下降一半。

但从 100 个样本增加到 200 个样本：

$$
SE_{\text{new}}=\frac{SE_{\text{old}}}{\sqrt{2}}
$$

约下降：

$$
29.3\%
$$

样本量增加会提高估计精度，但并非线性提高。

---

# 四、点估计与区间估计

## 12. 点估计

使用一个具体数值估计总体参数，称为点估计。

例如，某策略过去 100 笔交易的平均收益率为：

$$
\bar{x}=0.4\%
$$

于是使用：

$$
0.4\%
$$

估计策略的总体平均收益率。

但点估计没有直接说明估计的不确定性。

---

## 13. 区间估计

区间估计给出一个可能包含总体参数的范围。

例如：

$$
[-0.1\%,0.9\%]
$$

相比单独报告：

$$
\bar{x}=0.4\%
$$

区间估计包含了更多信息：

- 估计中心
- 估计精度
- 结果的不确定性
- 总体均值可能所在的范围

---

## 14. 为什么需要区间估计

假设两个策略的样本平均收益率都是：

$$
0.5\%
$$

### 策略 A

95% 置信区间：

$$
[0.4\%,0.6\%]
$$

### 策略 B

95% 置信区间：

$$
[-1.5\%,2.5\%]
$$

虽然点估计相同，但策略 A 的估计更加稳定。

策略 B 的不确定性很大，无法确认真实平均收益是否为正。

---

# 五、置信区间

## 15. 置信区间的基本形式

置信区间通常写成：

$$
\text{点估计}\pm\text{临界值}\times\text{标准误}
$$

对于总体均值：

$$
\bar{x}\pm\text{临界值}\times SE(\bar{x})
$$

其中：

$$
SE(\bar{x})=\frac{s}{\sqrt{n}}
$$

---

## 16. 置信水平

常见置信水平包括：

- 90%
- 95%
- 99%

对应显著性水平：

$$
\alpha=1-\text{置信水平}
$$

### 90% 置信水平

$$
\alpha=0.10
$$

### 95% 置信水平

$$
\alpha=0.05
$$

### 99% 置信水平

$$
\alpha=0.01
$$

---

## 17. 正确理解 95% 置信区间

95% 置信区间的严格含义是：

> 如果用相同方法重复抽样，并且每次都构造一个置信区间，那么长期来看，大约 95% 的这些区间会覆盖真实总体参数。

它不是说：

> 已经计算出的这个区间有 95% 的概率包含总体均值。

在经典频率统计中，总体均值被视为固定值，区间是随机的。

区间计算完成后，它要么包含真实参数，要么不包含。

---

## 18. 重复抽样示意

假设真实总体均值为：

$$
\mu=0.05\%
$$

重复抽样 100 次，并构造 100 个 95% 置信区间。

理论上，大约：

$$
95
$$

个区间会包含：

$$
\mu
$$

大约：

$$
5
$$

个区间不会包含：

$$
\mu
$$

---

# 六、正态分布置信区间

## 19. 总体标准差已知

如果总体标准差 $\sigma$ 已知，并且样本均值近似服从正态分布，则均值置信区间为：

$$
\bar{x}\pm z_{\alpha/2}\frac{\sigma}{\sqrt{n}}
$$

其中：

- $\bar{x}$：样本均值
- $\sigma$：总体标准差
- $n$：样本量
- $z_{\alpha/2}$：标准正态分布临界值

---

## 20. 常见 $z$ 临界值

| 置信水平 | 临界值 |
|---:|---:|
| 90% | 1.645 |
| 95% | 1.960 |
| 99% | 2.576 |

因此，95% 置信区间通常写为：

$$
\bar{x}\pm1.96\frac{\sigma}{\sqrt{n}}
$$

---

## 21. 正态置信区间示例

假设：

$$
\bar{x}=0.1\%
$$

$$
\sigma=2\%
$$

$$
n=100
$$

标准误为：

$$
SE=\frac{2\%}{\sqrt{100}}=0.2\%
$$

95% 置信区间为：

$$
0.1\%\pm1.96\times0.2\%
$$

误差范围为：

$$
1.96\times0.2\%=0.392\%
$$

因此：

$$
[-0.292\%,0.492\%]
$$

区间包含 0。

这说明当前样本无法提供充分证据证明总体平均收益率显著不等于 0。

---

# 七、为什么需要 $t$ 分布

## 22. 总体标准差通常未知

实际量化研究中，我们通常不知道真实总体标准差：

$$
\sigma
$$

只能通过样本标准差：

$$
s
$$

进行估计。

当使用样本标准差代替总体标准差时，会增加额外的不确定性。

因此通常使用 $t$ 分布，而不是直接使用标准正态分布。

---

## 23. $t$ 分布的特点

$t$ 分布具有以下特点：

- 以 0 为中心
- 左右对称
- 形状类似正态分布
- 尾部比正态分布更厚
- 样本量较小时与正态分布差异明显
- 样本量增大时逐渐接近正态分布

---

## 24. 自由度

单样本均值问题中，自由度通常为：

$$
df=n-1
$$

例如样本量为：

$$
n=20
$$

则自由度为：

$$
df=19
$$

样本量越小，$t$ 分布的尾部越厚，对应临界值越大。

---

# 八、$t$ 分布置信区间

## 25. 均值置信区间公式

当总体标准差未知时：

$$
\bar{x}\pm t_{\alpha/2,n-1}\frac{s}{\sqrt{n}}
$$

其中：

- $\bar{x}$：样本均值
- $s$：样本标准差
- $n$：样本数量
- $n-1$：自由度
- $t_{\alpha/2,n-1}$：$t$ 分布临界值

---

## 26. $t$ 区间示例

假设某策略有 20 笔交易：

$$
n=20
$$

样本平均收益率：

$$
\bar{x}=0.5\%
$$

样本标准差：

$$
s=2\%
$$

标准误为：

$$
SE=\frac{2\%}{\sqrt{20}}
$$

约为：

$$
0.447\%
$$

自由度为：

$$
df=19
$$

95% 置信区间对应的 $t$ 临界值约为：

$$
2.093
$$

误差范围为：

$$
2.093\times0.447\%\approx0.936\%
$$

因此置信区间为：

$$
[0.5\%-0.936\%,0.5\%+0.936\%]
$$

即：

$$
[-0.436\%,1.436\%]
$$

区间包含 0。

虽然样本平均收益率为正，但真实平均收益率可能并不为正。

---

# 九、置信区间的宽度

## 27. 置信区间宽度公式

置信区间的总宽度为：

$$
2\times\text{临界值}\times SE
$$

对于 $t$ 置信区间：

$$
\text{区间宽度}=2t_{\alpha/2,n-1}\frac{s}{\sqrt{n}}
$$

---

## 28. 影响置信区间宽度的因素

置信区间宽度主要受三个因素影响：

1. 样本标准差
2. 样本量
3. 置信水平

---

## 29. 标准差越大，区间越宽

当其他条件不变时：

$$
s\uparrow\quad\Rightarrow\quad SE\uparrow
$$

因此：

$$
\text{置信区间变宽}
$$

金融含义：

> 收益率波动越大，平均收益率越难准确估计。

---

## 30. 样本量越大，区间越窄

当其他条件不变时：

$$
n\uparrow\quad\Rightarrow\quad\frac{s}{\sqrt{n}}\downarrow
$$

因此：

$$
\text{置信区间变窄}
$$

金融含义：

> 交易样本越多，平均收益率估计通常越稳定。

---

## 31. 置信水平越高，区间越宽

置信水平越高，临界值越大。

因此：

$$
99\%\text{ 置信区间}>95\%\text{ 置信区间}>90\%\text{ 置信区间}
$$

这里的“大于”表示区间宽度更大。

提高覆盖率，需要付出降低精确度的代价。

---

# 十、置信区间与策略判断

## 32. 区间完全大于 0

例如：

$$
[0.10\%,0.50\%]
$$

整个区间都大于 0。

这表示样本数据支持总体平均收益率为正。

---

## 33. 区间包含 0

例如：

$$
[-0.20\%,0.60\%]
$$

该区间包含 0。

这表示：

> 当前样本不足以排除总体平均收益率等于 0 的可能性。

不能直接判断策略有效。

---

## 34. 区间完全小于 0

例如：

$$
[-0.80\%,-0.20\%]
$$

整个区间都小于 0。

这表示样本数据支持总体平均收益率为负。

---

## 35. 统计意义不等于经济意义

假设某高频策略平均每笔收益的 95% 置信区间为：

$$
[0.001\%,0.003\%]
$$

虽然区间完全大于 0，但还要考虑：

- 手续费
- 滑点
- 冲击成本
- 延迟
- 成交概率
- 策略容量

如果交易成本为：

$$
0.01\%
$$

那么策略在经济上可能仍然无效。

---

# 十一、使用 NumPy 计算标准误

## 36. 基础代码

```python
import numpy as np

returns = np.array([
    0.01,
    -0.02,
    0.015,
    0.005,
    -0.01
])

sample_size = len(returns)

sample_mean = np.mean(returns)

sample_std = np.std(
    returns,
    ddof=1
)

standard_error = (
    sample_std
    / np.sqrt(sample_size)
)

print(f"样本数量：{sample_size}")
print(f"样本均值：{sample_mean:.4%}")
print(f"样本标准差：{sample_std:.4%}")
print(f"标准误：{standard_error:.4%}")
```

---

# 十二、使用 SciPy 计算标准误

## 37. `stats.sem()`

```python
from scipy import stats

standard_error = stats.sem(
    returns
)
```

`stats.sem()` 默认使用样本标准差计算：

$$
SE=\frac{s}{\sqrt{n}}
$$

完整示例：

```python
import numpy as np
from scipy import stats

returns = np.array([
    0.01,
    -0.02,
    0.015,
    0.005,
    -0.01
])

standard_error = stats.sem(
    returns
)

print(f"标准误：{standard_error:.4%}")
```

---

# 十三、使用 SciPy 计算 $t$ 置信区间

## 38. `stats.t.interval()`

```python
confidence_interval = stats.t.interval(
    confidence=0.95,
    df=len(returns) - 1,
    loc=np.mean(returns),
    scale=stats.sem(returns)
)
```

其中：

- `confidence=0.95`：置信水平为 95%
- `df=len(returns) - 1`：自由度
- `loc=np.mean(returns)`：区间中心
- `scale=stats.sem(returns)`：标准误

---

## 39. 完整代码

```python
import numpy as np
from scipy import stats

returns = np.array([
    0.01,
    -0.02,
    0.015,
    0.005,
    -0.01,
    0.008,
    0.012,
    -0.006,
    0.004,
    0.009
])

sample_size = len(returns)

sample_mean = np.mean(returns)

sample_std = np.std(
    returns,
    ddof=1
)

standard_error = stats.sem(
    returns
)

confidence_interval = stats.t.interval(
    confidence=0.95,
    df=sample_size - 1,
    loc=sample_mean,
    scale=standard_error
)

lower_bound = confidence_interval[0]
upper_bound = confidence_interval[1]

print(f"样本数量：{sample_size}")
print(f"样本均值：{sample_mean:.4%}")
print(f"样本标准差：{sample_std:.4%}")
print(f"标准误：{standard_error:.4%}")
print(f"95%置信区间：[{lower_bound:.4%}, {upper_bound:.4%}]")
```

---

# 十四、手工计算 $t$ 置信区间

## 40. 获取 $t$ 临界值

```python
from scipy import stats

confidence = 0.95

alpha = 1 - confidence

degrees_of_freedom = sample_size - 1

critical_value = stats.t.ppf(
    1 - alpha / 2,
    df=degrees_of_freedom
)
```

---

## 41. 计算误差范围

```python
margin_of_error = (
    critical_value
    * standard_error
)
```

---

## 42. 计算区间上下限

```python
lower_bound = (
    sample_mean
    - margin_of_error
)

upper_bound = (
    sample_mean
    + margin_of_error
)
```

---

## 43. 完整手工版本

```python
import numpy as np
from scipy import stats

returns = np.array([
    0.01,
    -0.02,
    0.015,
    0.005,
    -0.01,
    0.008,
    0.012,
    -0.006,
    0.004,
    0.009
])

confidence = 0.95

sample_size = len(returns)

sample_mean = np.mean(returns)

sample_std = np.std(
    returns,
    ddof=1
)

standard_error = (
    sample_std
    / np.sqrt(sample_size)
)

degrees_of_freedom = sample_size - 1

alpha = 1 - confidence

critical_value = stats.t.ppf(
    1 - alpha / 2,
    df=degrees_of_freedom
)

margin_of_error = (
    critical_value
    * standard_error
)

lower_bound = (
    sample_mean
    - margin_of_error
)

upper_bound = (
    sample_mean
    + margin_of_error
)

print(f"t临界值：{critical_value:.4f}")
print(f"误差范围：{margin_of_error:.4%}")
print(f"置信区间：[{lower_bound:.4%}, {upper_bound:.4%}]")
```

---

# 十五、编写统一置信区间函数

## 44. 函数目标

编写函数：

```python
mean_confidence_interval()
```

输入：

- 收益率序列
- 置信水平

输出：

- 样本数量
- 样本均值
- 样本标准差
- 标准误
- 自由度
- 临界值
- 误差范围
- 置信区间下限
- 置信区间上限

---

## 45. 函数实现

```python
import numpy as np
from scipy import stats


def mean_confidence_interval(
    values,
    confidence=0.95
):
    values = np.asarray(
        values,
        dtype=float
    )

    values = values[
        ~np.isnan(values)
    ]

    sample_size = len(values)

    if sample_size < 2:
        raise ValueError(
            "至少需要两个有效样本"
        )

    if not 0 < confidence < 1:
        raise ValueError(
            "confidence 必须位于 0 和 1 之间"
        )

    sample_mean = np.mean(values)

    sample_std = np.std(
        values,
        ddof=1
    )

    standard_error = (
        sample_std
        / np.sqrt(sample_size)
    )

    degrees_of_freedom = (
        sample_size - 1
    )

    alpha = 1 - confidence

    critical_value = stats.t.ppf(
        1 - alpha / 2,
        df=degrees_of_freedom
    )

    margin_of_error = (
        critical_value
        * standard_error
    )

    lower_bound = (
        sample_mean
        - margin_of_error
    )

    upper_bound = (
        sample_mean
        + margin_of_error
    )

    return {
        "sample_size": sample_size,
        "mean": sample_mean,
        "std": sample_std,
        "standard_error": standard_error,
        "degrees_of_freedom": degrees_of_freedom,
        "critical_value": critical_value,
        "margin_of_error": margin_of_error,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound
    }
```

---

## 46. 调用函数

```python
returns = [
    0.01,
    -0.02,
    0.015,
    0.005,
    -0.01,
    0.008,
    0.012,
    -0.006,
    0.004,
    0.009
]

result = mean_confidence_interval(
    returns,
    confidence=0.95
)

print(f"样本数量：{result['sample_size']}")
print(f"样本均值：{result['mean']:.4%}")
print(f"样本标准差：{result['std']:.4%}")
print(f"标准误：{result['standard_error']:.4%}")
print(
    f"置信区间："
    f"[{result['lower_bound']:.4%}, "
    f"{result['upper_bound']:.4%}]"
)
```

---

# 十六、比较不同置信水平

## 47. 计算 90%、95% 和 99% 置信区间

```python
confidence_levels = [
    0.90,
    0.95,
    0.99
]

for confidence in confidence_levels:
    result = mean_confidence_interval(
        returns,
        confidence=confidence
    )

    print(
        f"{confidence:.0%}置信区间："
        f"[{result['lower_bound']:.4%}, "
        f"{result['upper_bound']:.4%}]"
    )
```

---

## 48. 预期结果

通常会得到：

$$
\text{90% 区间最窄}
$$

$$
\text{95% 区间居中}
$$

$$
\text{99% 区间最宽}
$$

原因是置信水平越高，临界值越大。

---

# 十七、比较不同样本量

## 49. 实验设计

假设收益率来自：

$$
R_t\sim N(0.0005,0.02^2)
$$

分别使用：

- 20 个样本
- 60 个样本
- 250 个样本
- 1,000 个样本

计算每组样本的 95% 置信区间。

---

## 50. 实验代码

```python
import numpy as np

np.random.seed(42)

population = np.random.normal(
    loc=0.0005,
    scale=0.02,
    size=10000
)

sample_sizes = [
    20,
    60,
    250,
    1000
]

for sample_size in sample_sizes:
    sample = np.random.choice(
        population,
        size=sample_size,
        replace=False
    )

    result = mean_confidence_interval(
        sample,
        confidence=0.95
    )

    interval_width = (
        result["upper_bound"]
        - result["lower_bound"]
    )

    print(f"样本量：{sample_size}")
    print(f"样本均值：{result['mean']:.4%}")
    print(f"标准误：{result['standard_error']:.4%}")
    print(
        f"95%置信区间："
        f"[{result['lower_bound']:.4%}, "
        f"{result['upper_bound']:.4%}]"
    )
    print(f"区间宽度：{interval_width:.4%}")
    print("-" * 40)
```

---

## 51. 实验观察

随着样本量增加：

- 标准差不一定持续下降
- 标准误通常下降
- 误差范围通常下降
- 置信区间通常变窄
- 平均收益率估计通常更加稳定

---

# 十八、置信区间覆盖率模拟

## 52. 实验目标

验证 95% 置信区间的长期覆盖率。

假设总体为：

$$
R_t\sim N(0.001,0.02^2)
$$

真实总体均值为：

$$
\mu=0.001
$$

重复进行：

1. 抽取一个样本
2. 构造 95% 置信区间
3. 判断区间是否包含真实均值
4. 重复 5,000 次
5. 计算覆盖比例

---

## 53. 模拟代码

```python
import numpy as np
from scipy import stats

np.random.seed(42)

true_mean = 0.001
true_std = 0.02

sample_size = 30
simulation_count = 5000

covered_count = 0

for _ in range(simulation_count):
    sample = np.random.normal(
        loc=true_mean,
        scale=true_std,
        size=sample_size
    )

    sample_mean = np.mean(sample)

    standard_error = stats.sem(
        sample
    )

    lower_bound, upper_bound = stats.t.interval(
        confidence=0.95,
        df=sample_size - 1,
        loc=sample_mean,
        scale=standard_error
    )

    if lower_bound <= true_mean <= upper_bound:
        covered_count += 1

coverage_ratio = (
    covered_count
    / simulation_count
)

print(f"覆盖次数：{covered_count}")
print(f"模拟次数：{simulation_count}")
print(f"实际覆盖率：{coverage_ratio:.2%}")
```

---

## 54. 预期结果

实际覆盖率通常会接近：

$$
95\%
$$

但不一定正好等于 95%。

例如可能得到：

- 94.6%
- 95.2%
- 95.8%

原因是模拟次数有限，存在随机波动。

---

# 十九、真实收益率数据处理

## 55. 使用 pandas 计算

假设 DataFrame 中有一列日收益率：

```python
import pandas as pd

data = pd.DataFrame({
    "return": [
        0.01,
        -0.02,
        0.015,
        0.005,
        -0.01
    ]
})
```

计算：

```python
sample_mean = data["return"].mean()

sample_std = data["return"].std()

standard_error = data["return"].sem()
```

其中：

```python
Series.std()
```

默认使用：

$$
ddof=1
$$

即样本标准差。

---

## 56. 删除缺失值

```python
returns = (
    data["return"]
    .dropna()
)
```

再计算：

```python
result = mean_confidence_interval(
    returns,
    confidence=0.95
)
```

在金融数据中，必须注意：

- 停牌数据
- 缺失交易日
- 收益率计算错误
- 无穷值
- 复权方式
- 异常价格

---

# 二十、常见错误

## 57. 把标准差当作标准误

错误：

> 日收益率标准差为 2%，因此平均收益率的误差也是 2%。

正确：

$$
SE=\frac{2\%}{\sqrt{n}}
$$

平均收益率的不确定性还取决于样本量。

---

## 58. 把 95% 置信区间理解成概率区间

错误：

> 总体均值有 95% 的概率位于这个已经计算出的区间内。

更准确的解释：

> 使用该方法重复构造区间，长期约 95% 的区间会覆盖真实总体均值。

---

## 59. 认为区间包含 0 就证明没有效果

错误：

> 置信区间包含 0，所以策略一定无效。

正确：

> 当前样本没有提供足够证据排除总体平均收益为 0。

可能的原因包括：

- 策略确实没有效果
- 样本量太小
- 收益率波动太大
- 信号较弱
- 样本质量较差

未能证明有效，不等于已经证明无效。

---

## 60. 认为区间不包含 0 就一定可交易

错误：

> 区间完全大于 0，所以策略可以直接实盘。

还需要检查：

- 交易成本
- 滑点
- 最大回撤
- 样本外表现
- 多重检验
- 未来函数
- 数据泄漏
- 策略容量
- 市场状态稳定性

---

## 61. 忽略收益率相关性

标准误公式：

$$
SE=\frac{s}{\sqrt{n}}
$$

通常假设样本相互独立。

但金融数据可能存在：

- 自相关
- 波动率聚集
- 同行业股票联动
- 同一天多笔交易高度相关
- 重叠持有期收益

这会导致表面样本量大于有效样本量。

简单标准误可能低估真实不确定性。

---

## 62. 重叠收益问题

假设每天计算未来 5 日收益：

$$
R_{t,t+5}
$$

相邻两天的数据会共享多个交易日。

例如：

- 第一天使用第 1 至第 5 日收益
- 第二天使用第 2 至第 6 日收益

两组收益高度重叠，不再相互独立。

这时不能机械使用普通标准误。

后续可以学习：

- Newey-West 标准误
- 区块 Bootstrap
- 非重叠样本
- 聚类标准误

---

# 二十一、今日编程练习

## 63. 练习一：计算标准误

给定收益率：

```python
returns = [
    0.012,
    -0.008,
    0.015,
    0.004,
    -0.011,
    0.006,
    0.009,
    -0.003,
    0.007,
    0.002
]
```

计算：

- 样本数量
- 样本均值
- 样本标准差
- 标准误

要求分别使用：

```python
np.std(..., ddof=1)
```

和：

```python
stats.sem()
```

确认两种方法结果一致。

---

## 64. 练习二：计算三个置信区间

使用同一组收益率，分别计算：

- 90% 置信区间
- 95% 置信区间
- 99% 置信区间

比较：

- 临界值
- 误差范围
- 区间宽度

---

## 65. 练习三：比较样本量

模拟收益率：

$$
R_t\sim N(0.0005,0.02^2)
$$

分别使用：

```python
sample_sizes = [
    20,
    60,
    250,
    1000
]
```

计算每组数据的：

- 样本均值
- 样本标准差
- 标准误
- 95% 置信区间
- 区间宽度

---

## 66. 练习四：比较不同波动率

构造两个策略：

### 策略 A

$$
R_A\sim N(0.001,0.01^2)
$$

### 策略 B

$$
R_B\sim N(0.001,0.04^2)
$$

两个策略样本量都为：

$$
n=100
$$

比较：

- 平均收益
- 标准差
- 标准误
- 95% 置信区间宽度

思考为什么平均收益相同，置信区间却不同。

---

## 67. 练习五：覆盖率模拟

分别使用置信水平：

```python
confidence_levels = [
    0.90,
    0.95,
    0.99
]
```

每个置信水平重复模拟 5,000 次。

统计实际覆盖率。

理论上，实际覆盖率应分别接近：

- 90%
- 95%
- 99%

---

# 二十二、思考题

## 68. 思考题一

某策略的平均日收益率为 0.1%，标准差为 2%，样本量为 25。

标准误是多少？

$$
SE=\frac{2\%}{\sqrt{25}}
$$

$$
=0.4\%
$$

平均收益率只有 0.1%，但标准误达到 0.4%。

说明平均收益估计存在较大不确定性。

---

## 69. 思考题二

两个策略都有 100 笔交易。

策略 A 标准差为 1%，策略 B 标准差为 5%。

哪个策略平均收益的估计更精确？

因为：

$$
SE=\frac{s}{\sqrt{n}}
$$

两者样本量相同，策略 A 的标准差更小，所以策略 A 的标准误更小。

因此策略 A 的平均收益估计更精确。

---

## 70. 思考题三

95% 置信区间为：

$$
[-0.1\%,0.8\%]
$$

能否判断策略平均收益为正？

不能。

因为区间包含：

$$
0
$$

当前样本没有提供充分证据证明总体平均收益率为正。

---

## 71. 思考题四

99% 置信区间是否一定比 95% 置信区间更好？

不一定。

99% 置信区间覆盖率更高，但区间也更宽。

这反映了：

$$
\text{置信程度}\quad\text{与}\quad\text{估计精度}
$$

之间的权衡。

---

## 72. 思考题五

样本量达到 10,000，是否可以忽略数据质量问题？

不可以。

大样本只能降低随机抽样误差，不能消除：

- 未来函数
- 幸存者偏差
- 数据泄漏
- 样本选择偏差
- 错误复权
- 交易成本遗漏
- 市场状态偏差

系统性偏差不会因为样本量增加而自动消失。

---

# 二十三、今日必须掌握的公式

## 样本标准差

$$
s=\sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar{x})^2}
$$

## 均值标准误

$$
SE(\bar{x})=\frac{s}{\sqrt{n}}
$$

## 总体标准差已知时的置信区间

$$
\bar{x}\pm z_{\alpha/2}\frac{\sigma}{\sqrt{n}}
$$

## 总体标准差未知时的置信区间

$$
\bar{x}\pm t_{\alpha/2,n-1}\frac{s}{\sqrt{n}}
$$

## 自由度

$$
df=n-1
$$

## 显著性水平

$$
\alpha=1-\text{置信水平}
$$

## 误差范围

$$
ME=t_{\alpha/2,n-1}\times SE
$$

## 置信区间宽度

$$
\text{Width}=2\times t_{\alpha/2,n-1}\times SE
$$

---

# 二十四、今日 Python 函数清单

## NumPy

```python
np.asarray()
np.isnan()
np.mean()
np.std()
np.sqrt()
np.random.seed()
np.random.normal()
np.random.choice()
```

## pandas

```python
Series.dropna()
Series.mean()
Series.std()
Series.sem()
```

## SciPy

```python
stats.sem()
stats.t.ppf()
stats.t.interval()
stats.norm.ppf()
stats.norm.interval()
```

---

# 二十五、今日知识检查

- [ ] 标准差描述什么？
- [ ] 标准误描述什么？
- [ ] 标准差与标准误有什么区别？
- [ ] 均值标准误如何计算？
- [ ] 样本量增加时标准误如何变化？
- [ ] 为什么样本量扩大四倍，标准误才下降一半？
- [ ] 什么是点估计？
- [ ] 什么是区间估计？
- [ ] 什么是置信水平？
- [ ] 95% 置信区间应该如何解释？
- [ ] 总体标准差未知时为什么使用 $t$ 分布？
- [ ] 什么是自由度？
- [ ] 哪些因素会影响置信区间宽度？
- [ ] 置信水平提高后区间为什么变宽？
- [ ] 置信区间包含 0 表示什么？
- [ ] 置信区间不包含 0 是否代表策略一定可交易？
- [ ] 为什么金融收益率相关性会影响标准误？
- [ ] 大样本能否解决系统性偏差？

---

# 二十六、今日成果

建议新增文件：

```text
quant-research/
├── src/
│   └── statistics/
│       └── confidence_interval.py
├── tests/
│   └── test_confidence_interval.py
└── notebooks/
    └── confidence_interval.ipynb
```

Notebook 至少包含：

1. 样本标准差计算
2. 标准误计算
3. 标准差与标准误对比
4. 90% 置信区间
5. 95% 置信区间
6. 99% 置信区间
7. 不同样本量的置信区间比较
8. 不同波动率的置信区间比较
9. 置信区间覆盖率模拟
10. 对置信区间含义的文字解释

---

# 二十七、今日总结

今天最重要的区别是：

$$
\text{标准差衡量原始收益率的波动}
$$

$$
\text{标准误衡量平均收益率估计的不确定性}
$$

均值标准误为：

$$
SE=\frac{s}{\sqrt{n}}
$$

总体均值的 $t$ 置信区间为：

$$
\bar{x}\pm t_{\alpha/2,n-1}\frac{s}{\sqrt{n}}
$$

置信区间越窄，通常说明总体均值估计越精确。

但置信区间不能解决：

- 数据偏差
- 未来函数
- 数据泄漏
- 样本相关性
- 交易成本
- 过度拟合

下一天将学习：

# 第八周 · 第五天

## 假设检验、$p$ 值与单样本 $t$ 检验
