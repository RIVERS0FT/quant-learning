# 第 9 周第 6 天：胜率与盈亏比

> 学习日期：2026-08-03  
> 所属阶段：阶段 01：Python、NumPy 与金融数据基础  
> 预计用时：90—120 分钟  
> 难度等级：进阶  
> 学习状态：已完成

---

## 一、今日新名词解释

### 1.1 胜率

- 英文名称：Win Rate
- 常用缩写：`WR`
- 基本含义：盈利观测次数占全部有效观测次数的比例。
- 通俗理解：做了若干笔交易后，其中有多少比例最终赚钱。
- 今日用途：描述策略盈利发生的频率。
- 易混淆概念：交易级胜率、周期级胜率、命中率。

### 1.2 盈亏比

- 英文名称：Payoff Ratio
- 常用缩写：`PR`
- 基本含义：平均盈利金额或收益率与平均亏损绝对值之比。
- 通俗理解：平均赚一次的钱，是平均亏一次的钱的多少倍。
- 今日用途：衡量单次盈利与单次亏损在幅度上的不对称程度。
- 易混淆概念：盈利因子、风险收益比、赔率。

### 1.3 单笔期望收益

- 英文名称：Expected Return per Trade
- 常用缩写：`Expectancy`
- 基本含义：在当前样本分布下，每完成一笔交易平均可以获得的净收益率。
- 通俗理解：把所有盈利和亏损摊到每一笔交易上，平均每笔能赚多少。
- 今日用途：把胜率、平均盈利和平均亏损综合成一个方向性指标。
- 易混淆概念：累计收益、年化收益、单笔平均盈利。

### 1.4 保本胜率

- 英文名称：Break-even Win Rate
- 常用缩写：`BEWR`
- 基本含义：在给定盈亏比下，使单笔期望收益恰好等于零的最低胜率。
- 通俗理解：按照当前平均赚亏幅度，至少要赢多少次才不亏钱。
- 今日用途：判断实际胜率是否足以支撑当前盈亏结构。
- 易混淆概念：历史胜率、目标胜率、盈亏平衡点。

### 1.5 盈利因子

- 英文名称：Profit Factor
- 常用缩写：`PF`
- 基本含义：全部盈利之和除以全部亏损绝对值之和。
- 通俗理解：策略历史上每亏损 1 元，总共赚回了多少元。
- 今日用途：帮助区分“平均盈亏比”和“总盈利对总亏损之比”。
- 易混淆概念：盈亏比。

---

## 二、今日学习目标

完成今天的学习后，应能够：

1. 区分交易级胜率与周期级胜率。
2. 明确盈利、亏损和零收益观测的分类口径。
3. 计算全部交易胜率与排除零收益后的有效胜率。
4. 计算平均盈利、平均亏损绝对值和盈亏比。
5. 推导单笔期望收益与保本胜率公式。
6. 使用 Python 编写胜率、盈亏比和单笔期望收益函数。
7. 解释为什么高胜率策略仍可能亏损，低胜率策略也可能盈利。

---

## 三、核心知识教学

本节学习以下核心概念：

1. 交易样本、胜负分类与胜率
2. 平均盈利、平均亏损与盈亏比
3. 单笔期望收益与保本胜率

### 3.1 交易样本、胜负分类与胜率

#### 3.1.1 概念解释

##### 标准定义

> 胜率是盈利观测数量占指定样本中有效观测总数量的比例，但计算前必须先定义观测单位、交易完成条件、零收益处理规则和交易成本口径。

##### 通俗理解

“胜率是多少”不是一个脱离上下文就能回答的问题。必须先说明统计的是完整交易、每日收益、每周收益，还是每次信号。

同一个策略可能同时出现以下结果：

- 完整交易胜率为 45%。
- 日收益为正的交易日占 54%。
- 月收益为正的月份占 62%。

三个数字都可能正确，但它们描述的是不同问题。

##### 为什么需要这个概念

1. 判断策略盈利出现得是否频繁。
2. 评估策略持有过程中的心理压力和连续亏损概率。
3. 与盈亏比结合，判断策略是否具有正期望。

##### 核心要点

- 交易级胜率必须以已经平仓的完整交易为样本。
- 周期级胜率以日、周、月等固定周期收益为样本。
- 零收益观测是否进入分母必须提前固定。
- 回测收益应先扣除佣金、印花税、滑点等交易成本。
- 加仓、减仓和分批平仓时，必须明确一笔交易如何聚合。

##### 简单示例

假设某策略完成 10 笔交易，其中：

- 5 笔盈利。
- 4 笔亏损。
- 1 笔净收益近似为零。

若零收益交易进入分母，则胜率为 50%。

若只在有明确盈亏的 9 笔交易中统计，则有效胜率约为 55.56%。

#### 3.1.2 数学解释

##### 数学定义

设第 \(i\) 笔已经平仓交易的净收益率为 \(r_i\)，零收益判断容差为 \(\varepsilon\)。

盈利交易数量为：

\[
N_+
=
\sum_{i=1}^{N}
\mathbf{1}(r_i>\varepsilon)
\]

亏损交易数量为：

\[
N_-
=
\sum_{i=1}^{N}
\mathbf{1}(r_i<-\varepsilon)
\]

零收益交易数量为：

\[
N_0
=
\sum_{i=1}^{N}
\mathbf{1}(|r_i|\le\varepsilon)
\]

因此总交易数量为：

\[
N=N_++N_-+N_0
\]

全部已平仓交易胜率定义为：

\[
p_{\text{all}}
=
\frac{N_+}{N}
\]

排除零收益交易后的有效胜率定义为：

\[
p_{\text{decisive}}
=
\frac{N_+}{N_++N_-}
\]

其中：

- \(N_+\)：盈利交易数量。
- \(N_-\)：亏损交易数量。
- \(N_0\)：零收益交易数量。
- \(N\)：全部有效已平仓交易数量。
- \(\varepsilon\)：判断收益是否近似为零的容差。

##### 公式推导

第一步，将全部交易划分为互不重叠的三组：

\[
\{r_i>\varepsilon\},
\quad
\{r_i<-\varepsilon\},
\quad
\{|r_i|\le\varepsilon\}
\]

第二步，三组数量之和等于总样本数量：

\[
N=N_++N_-+N_0
\]

第三步，若零收益交易仍是一次真实完成的交易，则它应进入全部交易胜率的分母：

\[
p_{\text{all}}
=
\frac{N_+}{N_++N_-+N_0}
\]

第四步，若研究目标是比较明确盈利与明确亏损的相对频率，则排除零收益交易：

\[
p_{\text{decisive}}
=
\frac{N_+}{N_++N_-}
\]

最终得到两种口径：

\[
p_{\text{all}}
\ne
p_{\text{decisive}}
\]

只要 \(N_0>0\)，两种胜率通常就不相等。

##### 数值示例

给定 10 笔净交易收益：

\[
4\%,
-2\%,
3\%,
-1\%,
5\%,
-3\%,
2\%,
-1.5\%,
0\%,
1\%
\]

盈利交易数量为：

\[
N_+=5
\]

亏损交易数量为：

\[
N_-=4
\]

零收益交易数量为：

\[
N_0=1
\]

全部交易胜率为：

\[
p_{\text{all}}
=
\frac{5}{10}
\]

\[
p_{\text{all}}=50\%
\]

排除零收益交易后的有效胜率为：

\[
p_{\text{decisive}}
=
\frac{5}{5+4}
\]

\[
p_{\text{decisive}}
=
\frac{5}{9}
\]

\[
p_{\text{decisive}}
\approx55.56\%
\]

##### 结果解释

同一组交易可以得到 50% 和 55.56% 两个胜率。两者都没有计算错误，差异来自零收益交易是否进入分母。因此，报告胜率时必须同时报告统计口径。

#### 3.1.3 Python 代码

##### 相关函数

- `np.asarray()`：把输入转换为 NumPy 数组。
- `np.isfinite()`：检查是否包含 `NaN` 或无穷值。
- `np.count_nonzero()`：统计满足条件的元素数量。

##### 示例代码

```python
import numpy as np


def validate_trade_returns(returns: np.ndarray) -> np.ndarray:
    """检查并返回一维、有限的交易收益数组。"""
    values = np.asarray(returns, dtype=float)

    if values.ndim != 1:
        raise ValueError("returns 必须是一维数组")

    if values.size == 0:
        raise ValueError("returns 不能为空")

    if not np.isfinite(values).all():
        raise ValueError("returns 不能包含 NaN 或无穷值")

    return values


def calculate_win_rates(
    returns: np.ndarray,
    zero_tol: float = 1e-12,
) -> dict[str, float]:
    """计算全部交易胜率和排除零收益后的有效胜率。"""
    if zero_tol < 0:
        raise ValueError("zero_tol 不能为负数")

    values = validate_trade_returns(returns)

    wins = np.count_nonzero(values > zero_tol)
    losses = np.count_nonzero(values < -zero_tol)
    flats = values.size - wins - losses

    decisive_count = wins + losses

    win_rate_all = wins / values.size
    win_rate_decisive = (
        wins / decisive_count
        if decisive_count > 0
        else float("nan")
    )

    return {
        "trades": float(values.size),
        "wins": float(wins),
        "losses": float(losses),
        "flats": float(flats),
        "win_rate_all": win_rate_all,
        "win_rate_decisive": win_rate_decisive,
    }


def main() -> None:
    returns = np.array(
        [0.04, -0.02, 0.03, -0.01, 0.05,
         -0.03, 0.02, -0.015, 0.00, 0.01],
        dtype=float,
    )

    result = calculate_win_rates(returns)

    print(f"全部交易胜率：{result['win_rate_all']:.2%}")
    print(f"有效交易胜率：{result['win_rate_decisive']:.2%}")
    print(f"零收益交易数：{int(result['flats'])}")


if __name__ == "__main__":
    main()
```

##### 运行结果

```text
全部交易胜率：50.00%
有效交易胜率：55.56%
零收益交易数：1
```

##### 代码解释

1. `validate_trade_returns()` 统一检查数组维度、空数组和非法数值。
2. `values > zero_tol` 用于识别盈利交易。
3. `values < -zero_tol` 用于识别亏损交易。
4. 绝对值不超过容差的收益被归为零收益交易。
5. 函数同时输出两种胜率，避免隐含改变分母。

#### 3.1.4 量化应用

##### 应用场景

- 评估完整开仓到平仓交易的成功频率。
- 统计策略日、周、月收益为正的周期比例。
- 研究连续亏损次数和资金管理压力。

##### 使用方式

1. 明确观测单位是完整交易还是固定时间周期。
2. 使用扣除交易成本后的净收益。
3. 根据统一容差划分盈利、亏损和零收益。
4. 同时记录样本数量和胜率。
5. 与盈亏比和期望收益联合解释。

##### 使用限制

- 胜率不包含每次盈亏的幅度信息。
- 小样本胜率波动很大。
- 不同市场状态下胜率可能显著变化。
- 交易级胜率与周期级胜率不能直接比较。
- 未平仓交易不能直接当作已完成交易纳入统计。

### 3.2 平均盈利、平均亏损与盈亏比

#### 3.2.1 概念解释

##### 标准定义

> 平均盈利是所有盈利交易净收益率的算术平均值；平均亏损是所有亏损交易净收益率绝对值的算术平均值；盈亏比是平均盈利除以平均亏损。

##### 通俗理解

胜率只告诉我们“赢几次”，盈亏比告诉我们“赢一次通常赚多少、亏一次通常亏多少”。

例如：

- 策略甲平均盈利 1%，平均亏损 4%，盈亏比为 0.25。
- 策略乙平均盈利 5%，平均亏损 1%，盈亏比为 5。

即使策略甲胜率更高，也未必比策略乙更赚钱。

##### 为什么需要这个概念

1. 补充胜率缺失的盈亏幅度信息。
2. 判断止盈、止损结构是否合理。
3. 为期望收益和保本胜率提供输入。

##### 核心要点

- 平均亏损必须使用正的亏损幅度。
- 盈亏比只比较平均值，不反映样本数量。
- 盈亏比不是全部盈利除以全部亏损。
- 无盈利或无亏损样本时，盈亏比没有稳定定义。
- 必须使用同一收益口径和同一资金基准。

##### 简单示例

若平均盈利为 3%，平均亏损幅度为 1.875%，则：

\[
PR=1.6
\]

表示平均一次盈利约为平均一次亏损的 1.6 倍。

#### 3.2.2 数学解释

##### 数学定义

平均盈利定义为：

\[
\bar g
=
\frac{1}{N_+}
\sum_{i:r_i>\varepsilon}r_i
\]

平均亏损幅度定义为：

\[
\bar \ell
=
-\frac{1}{N_-}
\sum_{i:r_i<-\varepsilon}r_i
\]

因为亏损交易收益为负数，所以在公式前加负号，使 \(\bar\ell>0\)。

盈亏比定义为：

\[
B
=
\frac{\bar g}{\bar \ell}
\]

其中：

- \(\bar g\)：平均盈利收益率。
- \(\bar\ell\)：平均亏损幅度。
- \(B\)：盈亏比。

盈利因子定义为：

\[
PF
=
\frac{
\sum_{i:r_i>\varepsilon}r_i
}{
-\sum_{i:r_i<-\varepsilon}r_i
}
\]

##### 公式推导

第一步，全部盈利之和等于盈利次数乘以平均盈利：

\[
\sum_{i:r_i>\varepsilon}r_i
=
N_+\bar g
\]

第二步，全部亏损绝对值之和等于亏损次数乘以平均亏损幅度：

\[
-\sum_{i:r_i<-\varepsilon}r_i
=
N_-\bar\ell
\]

第三步，将两式代入盈利因子：

\[
PF
=
\frac{N_+\bar g}{N_-\bar\ell}
\]

第四步，将数量比例和平均盈亏比例分开：

\[
PF
=
\frac{N_+}{N_-}
\times
\frac{\bar g}{\bar\ell}
\]

第五步，使用盈亏比定义：

\[
B
=
\frac{\bar g}{\bar\ell}
\]

最终得到：

\[
PF
=
\frac{N_+}{N_-}B
\]

因此，只有当 \(N_+=N_-\) 时，盈利因子才会与盈亏比数值相同。

##### 数值示例

仍使用前述交易收益。

全部盈利之和为：

\[
4\%+3\%+5\%+2\%+1\%
=
15\%
\]

平均盈利为：

\[
\bar g
=
\frac{15\%}{5}
\]

\[
\bar g=3\%
\]

全部亏损绝对值之和为：

\[
2\%+1\%+3\%+1.5\%
=
7.5\%
\]

平均亏损幅度为：

\[
\bar\ell
=
\frac{7.5\%}{4}
\]

\[
\bar\ell=1.875\%
\]

盈亏比为：

\[
B
=
\frac{3\%}{1.875\%}
\]

\[
B=1.6
\]

盈利因子为：

\[
PF
=
\frac{15\%}{7.5\%}
\]

\[
PF=2.0
\]

也可以使用推导关系验证：

\[
PF
=
\frac{5}{4}\times1.6
\]

\[
PF=2.0
\]

##### 结果解释

盈亏比 1.6 表示平均盈利是平均亏损幅度的 1.6 倍；盈利因子 2.0 表示样本中的总盈利是总亏损绝对值的 2 倍。两者回答的问题不同。

#### 3.2.3 Python 代码

##### 相关函数

- 布尔索引：筛选盈利交易和亏损交易。
- `np.mean()`：计算平均盈利与平均亏损。
- `np.sum()`：计算总盈利与总亏损。

##### 示例代码

```python
import numpy as np


def calculate_payoff_metrics(
    returns: np.ndarray,
    zero_tol: float = 1e-12,
) -> dict[str, float]:
    """计算平均盈利、平均亏损、盈亏比和盈利因子。"""
    values = np.asarray(returns, dtype=float)

    if values.ndim != 1 or values.size == 0:
        raise ValueError("returns 必须是非空一维数组")

    if not np.isfinite(values).all():
        raise ValueError("returns 不能包含 NaN 或无穷值")

    wins = values[values > zero_tol]
    losses = values[values < -zero_tol]

    if wins.size == 0 or losses.size == 0:
        return {
            "average_win": float("nan"),
            "average_loss": float("nan"),
            "payoff_ratio": float("nan"),
            "profit_factor": float("nan"),
        }

    average_win = float(wins.mean())
    average_loss = float(-losses.mean())
    payoff_ratio = average_win / average_loss

    gross_profit = float(wins.sum())
    gross_loss = float(-losses.sum())
    profit_factor = gross_profit / gross_loss

    return {
        "average_win": average_win,
        "average_loss": average_loss,
        "payoff_ratio": payoff_ratio,
        "profit_factor": profit_factor,
    }


def main() -> None:
    returns = np.array(
        [0.04, -0.02, 0.03, -0.01, 0.05,
         -0.03, 0.02, -0.015, 0.00, 0.01],
        dtype=float,
    )

    result = calculate_payoff_metrics(returns)

    print(f"平均盈利：{result['average_win']:.3%}")
    print(f"平均亏损：{result['average_loss']:.3%}")
    print(f"盈亏比：{result['payoff_ratio']:.2f}")
    print(f"盈利因子：{result['profit_factor']:.2f}")


if __name__ == "__main__":
    main()
```

##### 运行结果

```text
平均盈利：3.000%
平均亏损：1.875%
盈亏比：1.60
盈利因子：2.00
```

##### 代码解释

1. 盈利交易使用 `values > zero_tol` 筛选。
2. 亏损交易使用 `values < -zero_tol` 筛选。
3. `-losses.mean()` 把负的平均亏损转换为正的亏损幅度。
4. 盈亏比使用平均盈利除以平均亏损幅度。
5. 盈利因子使用全部盈利之和除以全部亏损绝对值之和。

#### 3.2.4 量化应用

##### 应用场景

- 比较趋势策略与均值回归策略的收益结构。
- 检查止盈止损规则是否导致“小赚大亏”。
- 评估参数变化对平均盈利和平均亏损的影响。

##### 使用方式

1. 聚合得到每笔完整交易的净收益。
2. 分别提取盈利交易和亏损交易。
3. 计算平均盈利、平均亏损和盈亏比。
4. 同时记录胜率和盈利因子。
5. 检查极端交易是否主导平均值。

##### 使用限制

- 平均值容易受到极端值影响。
- 盈亏比不能反映盈利和亏损出现的频率。
- 样本中没有亏损时不能把盈亏比简单记为无穷大。
- 不同持仓规模下，简单收益率平均可能忽略资金权重。
- 分批开平仓时，交易聚合规则会影响结果。

### 3.3 单笔期望收益与保本胜率

#### 3.3.1 概念解释

##### 标准定义

> 单笔期望收益是全部已平仓交易净收益率的样本均值，也可以分解为盈利概率乘以平均盈利，减去亏损概率乘以平均亏损幅度。

##### 通俗理解

策略是否赚钱，不由胜率单独决定，而由以下两部分共同决定：

- 赢的时候出现多频繁、平均赚多少。
- 输的时候出现多频繁、平均亏多少。

高胜率但经常“小赚大亏”的策略可能是负期望；低胜率但能够“截断亏损、放大盈利”的策略可能是正期望。

##### 为什么需要这个概念

1. 把胜率和盈亏比组合成统一指标。
2. 判断当前交易结构是否至少在样本内具有正期望。
3. 计算给定盈亏比下所需的最低胜率。

##### 核心要点

- 期望收益必须使用扣除成本后的净交易收益。
- 零收益交易会降低按全部交易计算的单笔期望。
- 保本胜率公式通常基于无零收益或排除零收益后的样本。
- 正期望不等于未来必然盈利。
- 样本均值不能替代置信区间和稳健性检验。

##### 简单示例

若有效胜率为 40%，平均盈利为 3%，平均亏损为 2%，则：

\[
E
=
40\%\times3\%
-
60\%\times2\%
\]

\[
E=0
\]

该组合恰好处于盈亏平衡状态。

#### 3.3.2 数学解释

##### 数学定义

按全部交易计算的样本单笔期望收益为：

\[
\hat E
=
\frac{1}{N}
\sum_{i=1}^{N}r_i
\]

定义全部交易中的盈利概率、亏损概率和零收益概率：

\[
p
=
\frac{N_+}{N}
\]

\[
q
=
\frac{N_-}{N}
\]

\[
z
=
\frac{N_0}{N}
\]

并且：

\[
p+q+z=1
\]

期望收益可以写为：

\[
\hat E
=
p\bar g-q\bar\ell
\]

零收益项为 \(z\times0\)，因此没有出现在最终表达式中。

当样本中没有零收益交易，或只研究排除零收益后的有效交易时：

\[
q=1-p
\]

此时期望收益为：

\[
E
=
p\bar g-(1-p)\bar\ell
\]

##### 公式推导

第一步，将全部交易收益和拆分为盈利、亏损和零收益三部分：

\[
\sum_{i=1}^{N}r_i
=
\sum_{i:r_i>\varepsilon}r_i
+
\sum_{i:r_i<-\varepsilon}r_i
+
\sum_{i:|r_i|\le\varepsilon}r_i
\]

第二步，零收益部分近似为零：

\[
\sum_{i:|r_i|\le\varepsilon}r_i
\approx0
\]

第三步，使用平均盈利定义：

\[
\sum_{i:r_i>\varepsilon}r_i
=
N_+\bar g
\]

第四步，使用平均亏损幅度定义：

\[
\sum_{i:r_i<-\varepsilon}r_i
=
-N_-\bar\ell
\]

第五步，代回总收益和：

\[
\sum_{i=1}^{N}r_i
=
N_+\bar g-N_-\bar\ell
\]

第六步，两边除以 \(N\)：

\[
\frac{1}{N}
\sum_{i=1}^{N}r_i
=
\frac{N_+}{N}\bar g
-
\frac{N_-}{N}\bar\ell
\]

第七步，使用 \(p=N_+/N\) 和 \(q=N_-/N\)：

\[
\hat E
=
p\bar g-q\bar\ell
\]

下面推导无零收益条件下的保本胜率。

第一步，从期望收益公式开始：

\[
E
=
p\bar g-(1-p)\bar\ell
\]

第二步，使用盈亏比定义：

\[
B
=
\frac{\bar g}{\bar\ell}
\]

第三步，将平均盈利写为：

\[
\bar g=B\bar\ell
\]

第四步，代入期望收益公式：

\[
E
=
pB\bar\ell-(1-p)\bar\ell
\]

第五步，提取 \(\bar\ell\)：

\[
E
=
\bar\ell[pB-(1-p)]
\]

第六步，展开括号：

\[
E
=
\bar\ell[pB-1+p]
\]

第七步，合并含 \(p\) 的项：

\[
E
=
\bar\ell[p(B+1)-1]
\]

第八步，保本时令 \(E=0\)：

\[
0
=
\bar\ell[p(B+1)-1]
\]

第九步，因为 \(\bar\ell>0\)，所以：

\[
p(B+1)-1=0
\]

第十步，移项：

\[
p(B+1)=1
\]

第十一步，两边除以 \(B+1\)：

\[
p_{\text{BE}}
=
\frac{1}{B+1}
\]

最终得到保本胜率：

\[
\boxed{
p_{\text{BE}}
=
\frac{1}{1+B}
}
\]

##### 数值示例

前述样本中：

\[
p=50\%
\]

\[
q=40\%
\]

\[
\bar g=3\%
\]

\[
\bar\ell=1.875\%
\]

按全部交易计算单笔期望收益：

\[
\hat E
=
50\%\times3\%
-
40\%\times1.875\%
\]

第一项为：

\[
50\%\times3\%=1.5\%
\]

第二项为：

\[
40\%\times1.875\%=0.75\%
\]

因此：

\[
\hat E
=
1.5\%-0.75\%
\]

\[
\hat E=0.75\%
\]

盈亏比为：

\[
B=1.6
\]

保本胜率为：

\[
p_{\text{BE}}
=
\frac{1}{1+1.6}
\]

\[
p_{\text{BE}}
=
\frac{1}{2.6}
\]

\[
p_{\text{BE}}
\approx38.46\%
\]

应将该保本胜率与排除零收益后的有效胜率比较：

\[
55.56\%>38.46\%
\]

##### 结果解释

样本中的有效胜率高于保本胜率，且按全部交易计算的单笔期望收益为正。但这只是历史样本估计，不能保证未来仍保持相同胜率和盈亏比。

#### 3.3.3 Python 代码

##### 相关函数

- `np.mean()`：直接计算样本单笔期望收益。
- `np.count_nonzero()`：计算盈利和亏损频率。
- `np.nan`：表示无法稳定定义的指标。

##### 示例代码

```python
import numpy as np


def calculate_expectancy_metrics(
    returns: np.ndarray,
    zero_tol: float = 1e-12,
) -> dict[str, float]:
    """计算单笔期望收益、盈亏比和保本胜率。"""
    values = np.asarray(returns, dtype=float)

    if values.ndim != 1 or values.size == 0:
        raise ValueError("returns 必须是非空一维数组")

    if not np.isfinite(values).all():
        raise ValueError("returns 不能包含 NaN 或无穷值")

    wins = values[values > zero_tol]
    losses = values[values < -zero_tol]

    expectancy = float(values.mean())

    if wins.size == 0 or losses.size == 0:
        return {
            "expectancy": expectancy,
            "payoff_ratio": float("nan"),
            "break_even_win_rate": float("nan"),
        }

    average_win = float(wins.mean())
    average_loss = float(-losses.mean())
    payoff_ratio = average_win / average_loss
    break_even_win_rate = 1.0 / (1.0 + payoff_ratio)

    return {
        "expectancy": expectancy,
        "payoff_ratio": payoff_ratio,
        "break_even_win_rate": break_even_win_rate,
    }


def main() -> None:
    returns = np.array(
        [0.04, -0.02, 0.03, -0.01, 0.05,
         -0.03, 0.02, -0.015, 0.00, 0.01],
        dtype=float,
    )

    result = calculate_expectancy_metrics(returns)

    print(f"单笔期望收益：{result['expectancy']:.3%}")
    print(f"盈亏比：{result['payoff_ratio']:.2f}")
    print(f"保本胜率：{result['break_even_win_rate']:.2%}")


if __name__ == "__main__":
    main()
```

##### 运行结果

```text
单笔期望收益：0.750%
盈亏比：1.60
保本胜率：38.46%
```

##### 代码解释

1. `values.mean()` 直接得到按全部交易计算的单笔平均净收益。
2. 盈亏比只在同时存在盈利和亏损交易时计算。
3. 保本胜率使用 \(1/(1+B)\) 计算。
4. 无盈利或无亏损样本时返回 `NaN`，避免制造虚假的无穷大指标。

#### 3.3.4 量化应用

##### 应用场景

- 判断策略是否具有正的历史单笔期望。
- 比较高胜率低盈亏比与低胜率高盈亏比策略。
- 评估止损、止盈和持有期参数的组合效果。

##### 使用方式

1. 使用净交易收益计算实际胜率。
2. 计算平均盈利和平均亏损幅度。
3. 得到盈亏比和保本胜率。
4. 比较有效胜率与保本胜率。
5. 使用单笔期望收益验证综合结果。

##### 使用限制

- 样本期望可能被少数极端盈利交易主导。
- 参数过度优化会抬高样本内期望。
- 胜率和盈亏比在不同市场状态下可能不稳定。
- 单笔期望没有反映交易频率和资金占用时间。
- 正期望策略仍可能出现较长连续亏损。

---

## 四、综合案例

### 4.1 各个概念之间的关系

```text
已平仓交易的净收益
    ↓
按统一容差划分盈利、亏损、零收益
    ↓
计算全部交易胜率与有效胜率
    ↓
计算平均盈利与平均亏损幅度
    ↓
计算盈亏比
    ↓
计算单笔期望收益与保本胜率
    ↓
综合判断策略的交易质量
```

具体关系：

1. 胜率描述盈利出现的频率。
2. 盈亏比描述平均盈利与平均亏损的幅度关系。
3. 单笔期望收益把频率和幅度合并起来。
4. 保本胜率给出当前盈亏比所要求的最低有效胜率。
5. 盈利因子同时受到胜负次数比例和盈亏比影响。

### 4.2 综合使用场景

#### 场景描述

> 比较策略 A 和策略 B。策略 A 经常小幅盈利，但偶尔出现大额亏损；策略 B 经常小幅亏损，但少数盈利交易幅度较大。全部数据均为扣除交易成本后的完整交易净收益率。

策略 A 的 10 笔交易收益为：

\[
1\%,
1.2\%,
0.9\%,
1.1\%,
0.8\%,
1\%,
-5\%,
1\%,
0.9\%,
-4\%
\]

策略 B 的 10 笔交易收益为：

\[
-1\%,
-1.2\%,
-0.8\%,
-0.9\%,
-1.1\%,
-1\%,
5\%,
-1.5\%,
6\%,
-1.2\%
\]

#### 研究目标

1. 计算两个策略的胜率。
2. 计算平均盈利、平均亏损与盈亏比。
3. 计算单笔期望收益和保本胜率。
4. 判断高胜率是否必然意味着更好的策略。
5. 输出统一的交易绩效表。

### 4.3 综合数学关系

对于无零收益交易的样本：

\[
p
=
\frac{N_+}{N_++N_-}
\]

\[
B
=
\frac{\bar g}{\bar\ell}
\]

\[
E
=
p\bar g-(1-p)\bar\ell
\]

将 \(\bar g=B\bar\ell\) 代入：

\[
E
=
pB\bar\ell-(1-p)\bar\ell
\]

提取 \(\bar\ell\)：

\[
E
=
\bar\ell[p(B+1)-1]
\]

因此：

\[
E>0
\]

等价于：

\[
p(B+1)-1>0
\]

移项得到：

\[
p(B+1)>1
\]

两边除以 \(B+1\)：

\[
p>
\frac{1}{B+1}
\]

最终得到正期望条件：

\[
\boxed{
p>p_{\text{BE}}
}
\]

其中：

\[
p_{\text{BE}}
=
\frac{1}{B+1}
\]

### 4.4 综合处理流程

```text
准备完整交易净收益
    ↓
检查维度、空值和无穷值
    ↓
使用容差划分胜、负、平
    ↓
计算胜率与样本数量
    ↓
计算平均盈利和平均亏损
    ↓
计算盈亏比与盈利因子
    ↓
计算单笔期望和保本胜率
    ↓
比较实际胜率与保本胜率
    ↓
结合样本量和市场状态解释结果
```

### 4.5 示例 Python 代码

```python
import numpy as np
import pandas as pd


def validate_returns(returns: np.ndarray) -> np.ndarray:
    """验证交易收益数据。"""
    values = np.asarray(returns, dtype=float)

    if values.ndim != 1:
        raise ValueError("returns 必须是一维数组")

    if values.size == 0:
        raise ValueError("returns 不能为空")

    if not np.isfinite(values).all():
        raise ValueError("returns 不能包含 NaN 或无穷值")

    return values


def evaluate_trade_performance(
    returns: np.ndarray,
    zero_tol: float = 1e-12,
) -> pd.Series:
    """输出一组交易收益的统一绩效指标。"""
    if zero_tol < 0:
        raise ValueError("zero_tol 不能为负数")

    values = validate_returns(returns)

    wins = values[values > zero_tol]
    losses = values[values < -zero_tol]
    flats = values[np.abs(values) <= zero_tol]

    trade_count = values.size
    decisive_count = wins.size + losses.size

    win_rate_all = wins.size / trade_count
    win_rate_decisive = (
        wins.size / decisive_count
        if decisive_count > 0
        else float("nan")
    )

    average_win = (
        float(wins.mean())
        if wins.size > 0
        else float("nan")
    )

    average_loss = (
        float(-losses.mean())
        if losses.size > 0
        else float("nan")
    )

    if wins.size > 0 and losses.size > 0:
        payoff_ratio = average_win / average_loss
        profit_factor = float(wins.sum() / -losses.sum())
        break_even_win_rate = 1.0 / (1.0 + payoff_ratio)
    else:
        payoff_ratio = float("nan")
        profit_factor = float("nan")
        break_even_win_rate = float("nan")

    expectancy = float(values.mean())

    return pd.Series({
        "trades": trade_count,
        "wins": wins.size,
        "losses": losses.size,
        "flats": flats.size,
        "win_rate_all": win_rate_all,
        "win_rate_decisive": win_rate_decisive,
        "average_win": average_win,
        "average_loss": average_loss,
        "payoff_ratio": payoff_ratio,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "break_even_win_rate": break_even_win_rate,
    })


def main() -> None:
    strategy_a = np.array(
        [0.010, 0.012, 0.009, 0.011, 0.008,
         0.010, -0.050, 0.010, 0.009, -0.040],
        dtype=float,
    )

    strategy_b = np.array(
        [-0.010, -0.012, -0.008, -0.009, -0.011,
         -0.010, 0.050, -0.015, 0.060, -0.012],
        dtype=float,
    )

    result = pd.DataFrame({
        "strategy_a": evaluate_trade_performance(strategy_a),
        "strategy_b": evaluate_trade_performance(strategy_b),
    }).T

    columns = [
        "trades",
        "win_rate_all",
        "average_win",
        "average_loss",
        "payoff_ratio",
        "expectancy",
        "break_even_win_rate",
    ]

    print(result[columns].round(4))


if __name__ == "__main__":
    main()
```

##### 运行结果

```text
            trades  win_rate_all  average_win  average_loss  payoff_ratio  expectancy  break_even_win_rate
strategy_a    10.0           0.8       0.0099        0.0450        0.2194     -0.0011               0.8200
strategy_b    10.0           0.2       0.0550        0.0109        5.0575      0.0023               0.1651
```

### 4.6 代码逻辑解释

1. `validate_returns()` 保证输入是一维、非空且全部为有限数值。
2. `wins`、`losses` 和 `flats` 使用同一个零收益容差分类。
3. `win_rate_all` 使用全部已平仓交易作为分母。
4. `win_rate_decisive` 只使用明确盈利和明确亏损的交易。
5. 平均亏损通过对负收益均值取负号得到正的亏损幅度。
6. 盈亏比、盈利因子和保本胜率只在同时存在盈利与亏损时计算。
7. 单笔期望收益直接使用全部净交易收益的算术平均值。

### 4.7 综合结果分析

#### 指标关系

策略 A：

- 胜率为 80%。
- 盈亏比约为 0.2194。
- 保本胜率约为 82.00%。
- 实际胜率低于保本胜率。
- 单笔期望收益约为 -0.11%。

策略 B：

- 胜率为 20%。
- 盈亏比约为 5.0575。
- 保本胜率约为 16.51%。
- 实际胜率高于保本胜率。
- 单笔期望收益约为 0.23%。

#### 综合结果

- 策略 A 虽然 10 笔中赢了 8 笔，但两次亏损幅度过大，最终形成负期望。
- 策略 B 虽然只有 2 笔盈利，但盈利幅度足以覆盖 8 笔小额亏损，最终形成正期望。
- 胜率必须与盈亏比共同解释。
- 单笔期望收益可以作为两者是否匹配的直接检查结果。

#### 量化意义

一个可持续的交易系统不一定追求最高胜率，而是追求在交易成本、市场约束和风险控制之后仍然稳定为正的期望收益。策略优化时，不能只提高胜率，还要检查这种提升是否以牺牲平均盈利、扩大平均亏损或增加尾部风险为代价。

#### 案例限制

- 每个策略只有 10 笔交易，样本过小。
- 没有分析交易收益的时间顺序和连续亏损。
- 没有考虑不同交易的持仓时间与资金占用。
- 没有检验不同市场状态下指标是否稳定。
- 历史正期望不保证未来仍为正期望。

---

## 五、常见错误

### 5.1 概念错误

#### 错误一：把高胜率等同于好策略

错误理解：

> 胜率越高，策略一定越赚钱。

正确理解：

> 策略是否赚钱取决于胜率、平均盈利、平均亏损、交易成本和资金管理的共同作用。

错误原因：胜率只统计次数，不包含每次盈亏幅度。

#### 错误二：混用交易级胜率与周期级胜率

错误理解：

> 日收益为正的天数比例就是策略的交易胜率。

正确理解：

> 日胜率以交易日为观测单位；交易胜率以完整开平仓交易为观测单位，两者不能互相替代。

错误原因：观测单位不同，分母和经济含义也不同。

### 5.2 数学错误

#### 错误一：直接使用负的平均亏损计算盈亏比

错误公式：

\[
B
=
\frac{\bar g}{\overline{r}_{\text{loss}}}
\]

因为 \(\overline{r}_{\text{loss}}<0\)，该结果会变成负数。

正确公式：

\[
B
=
\frac{\bar g}{\bar\ell}
\]

其中：

\[
\bar\ell
=
-\overline{r}_{\text{loss}}
>0
\]

错误原因：盈亏比的分母应是平均亏损幅度，而不是带符号的平均亏损收益。

#### 错误二：把盈亏比当作盈利因子

错误公式：

\[
B
=
\frac{\sum \text{盈利}}{|\sum \text{亏损}|}
\]

正确公式：

\[
B
=
\frac{\text{平均盈利}}{\text{平均亏损幅度}}
\]

而：

\[
PF
=
\frac{\sum \text{盈利}}{|\sum \text{亏损}|}
\]

错误原因：盈亏比比较平均幅度，盈利因子比较总量。

#### 错误三：零收益交易存在时直接比较错误口径

错误做法：使用包含零收益交易的全部交易胜率，与基于 \(q=1-p\) 推导的保本胜率直接比较。

正确做法：将保本胜率与排除零收益后的有效胜率比较，或使用完整的 \(p\bar g-q\bar\ell\) 公式计算期望收益。

### 5.3 Python 错误

#### 错误一：用精确等于零判断浮点收益

错误代码：

```python
flats = returns[returns == 0]
```

正确代码：

```python
zero_tol = 1e-12
flats = returns[np.abs(returns) <= zero_tol]
```

错误原因：浮点计算结果可能非常接近零但不精确等于零。

#### 错误二：静默删除缺失值

错误代码：

```python
returns = returns[~np.isnan(returns)]
```

正确代码：

```python
if not np.isfinite(returns).all():
    raise ValueError("returns 包含非法数值")
```

错误原因：静默删除数据可能掩盖交易记录不完整或对齐错误。

#### 错误三：无亏损样本时返回无穷大盈亏比

错误代码：

```python
payoff_ratio = average_win / 0
```

正确代码：

```python
payoff_ratio = float("nan")
```

错误原因：短样本中没有观察到亏损，不代表真实亏损风险为零。

### 5.4 量化研究错误

#### 错误一：使用毛收益而不是净收益

错误做法：先用未扣成本的交易收益计算胜率和盈亏比，再假设成本影响很小。

正确做法：先扣除佣金、印花税、滑点和其他可识别成本，再计算全部交易指标。

#### 错误二：把订单当作交易

错误做法：每次加仓、减仓或部分成交都单独统计为一笔交易。

正确做法：先定义交易聚合规则，再把同一持仓周期中的订单合并为经济意义一致的完整交易。

#### 其他常见问题

- 只报告胜率，不报告交易数量。
- 使用未平仓交易的浮动盈亏参与胜率统计。
- 不同策略使用不同的零收益容差。
- 用收益金额与收益率混合计算盈亏比。
- 忽略极端交易对平均盈利和平均亏损的影响。
- 只在最优参数上报告指标，忽略样本外表现。
- 用正期望代替风险控制和最大回撤分析。

---

## 六、今日总结

### 6.1 今日新名词总结

- 胜率：盈利观测数量占指定样本总数量的比例。
- 盈亏比：平均盈利与平均亏损幅度之比。
- 单笔期望收益：全部净交易收益摊到每笔交易后的平均值。
- 保本胜率：给定盈亏比下，使期望收益为零的最低有效胜率。
- 盈利因子：总盈利除以总亏损绝对值。

### 6.2 核心概念总结

- 计算胜率前必须先固定交易级或周期级口径。
- 零收益交易是否进入分母会改变胜率。
- 盈亏比补充了胜率缺失的盈亏幅度信息。
- 盈利因子与盈亏比不是同一个指标。
- 单笔期望收益把胜率与盈亏比统一起来。
- 高胜率不等于正期望，低胜率也不等于负期望。

### 6.3 核心公式总结

全部交易胜率：

\[
p_{\text{all}}
=
\frac{N_+}{N_++N_-+N_0}
\]

有效胜率：

\[
p_{\text{decisive}}
=
\frac{N_+}{N_++N_-}
\]

盈亏比：

\[
B
=
\frac{\bar g}{\bar\ell}
\]

盈利因子：

\[
PF
=
\frac{N_+}{N_-}B
\]

按全部交易计算的单笔期望收益：

\[
\hat E
=
p\bar g-q\bar\ell
\]

无零收益条件下的期望收益：

\[
E
=
p\bar g-(1-p)\bar\ell
\]

保本胜率：

\[
p_{\text{BE}}
=
\frac{1}{1+B}
\]

正期望条件：

\[
p>p_{\text{BE}}
\]

### 6.4 Python 能力总结

今天应掌握以下实现能力：

- 使用 `np.asarray()` 统一输入类型。
- 使用 `np.isfinite()` 检查非法数据。
- 使用布尔索引划分盈利、亏损和零收益交易。
- 使用 `np.count_nonzero()` 计算交易数量。
- 使用 `np.mean()` 计算平均盈利、平均亏损和单笔期望。
- 使用 `pd.Series` 与 `pd.DataFrame` 输出统一绩效结果。
- 对无盈利、无亏损和全零收益样本返回明确的未定义结果。

### 6.5 今日最终结论

胜率回答“赢得多不多”，盈亏比回答“赢一次和亏一次相比幅度如何”，单笔期望收益回答“频率和幅度合在一起后平均是否赚钱”。完整评价策略时，至少应同时报告样本数量、胜率、平均盈利、平均亏损、盈亏比、单笔期望收益、交易成本口径和观测单位。
