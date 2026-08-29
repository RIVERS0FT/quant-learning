# 第 3 周第 3 天：NumPy 广播机制

## 今日目标

- 理解不同形状数组如何进行广播运算。
- 使用首日价格对多只股票进行归一化。
- 对每只股票进行中心化和标准化。
- 区分按股票广播与按日期广播。
- 使用资产权重计算组合收益率与收益贡献。

---

## 一、什么是广播

标量与数组运算是最简单的广播：

```python
import numpy as np

prices = np.array([10.0, 20.0, 30.0])
print(prices * 2)
```

标量 `2` 在概念上被扩展到数组中的每个位置。

NumPy 通常不会真的复制数据，而是按照广播规则完成计算。

---

## 二、广播规则

NumPy 从最右侧维度开始比较两个形状。每一维满足以下任意条件时可以兼容：

1. 两个维度相等；
2. 其中一个维度等于 1；
3. 某个数组缺少该维度。

可广播示例：

```text
(5, 3) 和 (3,)
(5, 3) 和 (1, 3)
(5, 3) 和 (5, 1)
(5, 3) 和标量 ()
```

不可广播示例：

```text
(5, 3) 和 (5,)
```

因为从最右侧比较时，3 与 5 不相等，且都不为 1。

---

## 三、按股票广播

价格矩阵：

```text
(交易日数量, 股票数量)
```

若每只股票有一个参数，可以使用形状：

```text
(股票数量,)
```

例如：

```python
adjustments = np.array([1.0, 2.0, 3.0])
result = prices + adjustments
```

第一个参数应用于股票 A 的全部日期，第二个参数应用于股票 B，第三个参数应用于股票 C。

---

## 四、首日价格归一化

获取首日价格：

```python
initial_prices = prices[0, :]
```

形状为 `(股票数量,)`，可以向下广播到全部交易日：

```python
normalized_prices = prices / initial_prices
```

数学表达：

$$
NAV_{t,i}=\frac{P_{t,i}}{P_{0,i}}
$$

第一行全部为 1。最后一行减去 1，就是每只股票相对首日的累计收益率：

```python
returns_from_start = normalized_prices - 1
final_returns = returns_from_start[-1]
```

归一化价格可以理解为每只股票初始投入 1 元后的净值路径。

---

## 五、验证累计收益率

三种计算方式应当一致：

```python
returns = prices[1:] / prices[:-1] - 1

result_1 = normalized_prices[-1] - 1
result_2 = prices[-1] / prices[0] - 1
result_3 = np.prod(1 + returns, axis=0) - 1

assert np.allclose(result_1, result_2)
assert np.allclose(result_2, result_3)
```

---

## 六、按股票中心化

每只股票的平均价格：

```python
mean_prices = prices.mean(axis=0)
```

中心化：

```python
centered_prices = prices - mean_prices
```

数学表达：

$$
X_{t,i}^{centered}=P_{t,i}-\bar P_i
$$

验证中心化后每列均值接近 0：

```python
assert np.allclose(
    centered_prices.mean(axis=0),
    0.0,
)
```

浮点计算可能得到非常接近 0 的小数，而不一定是精确的 0。

---

## 七、按股票标准化

标准化公式：

$$
z_{t,i}=\frac{P_{t,i}-\bar P_i}{\sigma_i}
$$

代码：

```python
mean_prices = prices.mean(axis=0)
std_prices = prices.std(axis=0, ddof=0)
standardized_prices = (
    prices - mean_prices
) / std_prices
```

验证：

```python
assert np.allclose(
    standardized_prices.mean(axis=0),
    0.0,
)

assert np.allclose(
    standardized_prices.std(axis=0, ddof=0),
    1.0,
)
```

标准化后：

- 正数表示高于该股票自身平均值；
- 负数表示低于自身平均值；
- 绝对值表示偏离均值的标准差数量。

价格标准化只是数据变换，不应直接被理解为交易信号。

---

## 八、`keepdims=True`

默认：

```python
prices.mean(axis=0).shape
```

结果：

```text
(3,)
```

保留维度：

```python
prices.mean(axis=0, keepdims=True).shape
```

结果：

```text
(1, 3)
```

两种形状都能与 `(5, 3)` 广播，但 `keepdims=True` 在复杂代码中能让维度含义更明确。

---

## 九、按日期广播

如果每个交易日只有一个参数，需要使用列向量：

```text
(交易日数量, 1)
```

例如每日市场平均收益：

```python
returns = prices[1:] / prices[:-1] - 1

market_returns = returns.mean(
    axis=1,
    keepdims=True,
)
```

形状：

```text
returns:        (4, 3)
market_returns: (4, 1)
```

市场调整收益率：

```python
market_adjusted_returns = returns - market_returns
```

数学表达：

$$
R_{t,i}^{adjusted}=R_{t,i}-\bar R_t
$$

验证每天横截面均值接近 0：

```python
assert np.allclose(
    market_adjusted_returns.mean(axis=1),
    0.0,
)
```

---

## 十、`np.newaxis` 与 `None`

将一维数组转换为列向量：

```python
daily_values = np.array([1.0, 2.0, 3.0, 4.0])
column_values = daily_values[:, np.newaxis]
```

也可写成：

```python
column_values = daily_values[:, None]
```

形状区别：

```text
(4,)   一维数组
(4, 1) 四行一列
(1, 4) 一行四列
```

如果收益率矩阵是 `(4, 3)`，每日参数必须是 `(4, 1)`，而不能直接是 `(4,)`。

---

## 十一、组合权重与收益贡献

假设权重：

```python
weights = np.array([0.50, 0.30, 0.20])
```

应检查权重和：

```python
if not np.isclose(weights.sum(), 1.0):
    raise ValueError("组合权重之和必须为 1")
```

每只股票每日收益贡献：

```python
contributions = returns * weights
```

组合每日简单收益率：

```python
portfolio_returns = contributions.sum(axis=1)
```

等价矩阵乘法：

```python
portfolio_returns_2 = returns @ weights
```

验证：

```python
assert np.allclose(
    portfolio_returns,
    portfolio_returns_2,
)
```

`returns * weights` 适合观察各股票贡献，`returns @ weights` 适合直接得到组合收益。

---

## 十二、等权组合

```python
n_assets = returns.shape[1]
equal_weights = np.full(n_assets, 1 / n_assets)

equal_weight_returns = returns @ equal_weights
market_mean_returns = returns.mean(axis=1)

assert np.allclose(
    equal_weight_returns,
    market_mean_returns,
)
```

对股票收益求横截面平均，相当于使用等权组合。

---

## 十三、除零与形状风险

若某只股票价格始终不变，其标准差为 0：

```python
safe_std = np.where(
    std_prices == 0,
    np.nan,
    std_prices,
)

standardized = (
    prices - mean_prices
) / safe_std
```

NumPy 只能判断形状是否兼容，不能判断金融含义是否正确。广播前应检查：

```python
print(returns.shape)
print(weights.shape)
```

---

## 十四、广播形状速查

假设数据矩阵形状为 `(n_days, n_assets)`：

| 参数含义 | 推荐形状 | 广播方向 |
|---|---:|---|
| 一个统一参数 | `()` | 应用于所有元素 |
| 每只股票一个参数 | `(n_assets,)` | 向下广播到所有日期 |
| 每只股票一个参数 | `(1, n_assets)` | 向下广播到所有日期 |
| 每天一个参数 | `(n_days, 1)` | 横向广播到所有股票 |
| 每日每股一个参数 | `(n_days, n_assets)` | 逐元素运算 |

---

## 今日必须掌握的代码

```python
normalized_prices = prices / prices[0]
```

```python
standardized_prices = (
    prices - prices.mean(axis=0)
) / prices.std(axis=0)
```

```python
adjusted_returns = (
    returns
    - returns.mean(axis=1, keepdims=True)
)
```

```python
portfolio_returns = (
    returns * weights
).sum(axis=1)
```

---

## 今日检查清单

- [ ] 能解释广播的三条兼容规则。
- [ ] 能区分按股票参数与按日期参数的形状。
- [ ] 能用首日价格归一化多资产价格。
- [ ] 能完成按股票中心化和标准化。
- [ ] 能使用 `keepdims=True` 或 `[:, None]` 保留列向量。
- [ ] 能计算股票收益贡献与组合收益率。
- [ ] 能解释形状兼容不等于金融逻辑正确。