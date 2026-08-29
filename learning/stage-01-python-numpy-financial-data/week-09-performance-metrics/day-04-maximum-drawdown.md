# 第九周 · 第四天

## 最大回撤：历史高点、回撤序列与峰谷区间

---

## 1. 今日学习目标

完成今天的学习后，你需要能够：

- 理解最大回撤衡量的核心风险
- 区分收益率、波动率与回撤
- 理解净值、历史高点和回撤序列之间的关系
- 从净值序列逐期计算历史高点
- 从历史高点计算每一期回撤
- 区分带符号最大回撤与正数形式的最大回撤幅度
- 找出最大回撤的峰值、谷底与修复时点
- 理解回撤深度、下跌时长和修复时长的区别
- 推导亏损后的回本收益率
- 理解最大回撤的路径依赖性和尺度不变性
- 识别日频数据无法观察盘中最大回撤的问题
- 从收益率序列构造净值序列
- 编写最大回撤函数和最大回撤区间函数
- 编写滚动最大回撤函数
- 使用已知样例验证函数结果

---

## 2. 今日学习顺序

建议学习时间：约 120—150 分钟。

| 阶段 | 内容 | 建议时间 |
|---|---|---:|
| 1 | 最大回撤的直觉 | 20 分钟 |
| 2 | 历史高点与回撤公式 | 30 分钟 |
| 3 | 峰值、谷底与修复区间 | 25 分钟 |
| 4 | 数学性质与常见误区 | 25 分钟 |
| 5 | Python 实现与测试 | 35 分钟 |
| 6 | 练习与复盘 | 15 分钟 |

---

# 一、为什么需要最大回撤

## 3. 投资者真正经历的是一条净值路径

年化收益率回答：

> 策略长期赚了多少？

年化波动率回答：

> 策略的周期收益波动有多大？

夏普比率回答：

> 策略每承担一单位波动风险，获得了多少超额收益？

但真实投资者还会关心：

> 从曾经达到的最高资产值开始，最严重时亏了多少？

这个问题由最大回撤回答。

最大回撤关注的不是单个周期收益，而是整条净值路径中的最严重峰谷损失。

---

## 4. 一个直观例子

假设策略净值依次为：

```text
100, 110, 120, 108, 90, 99, 130
```

策略先从 \(100\) 上涨到 \(120\)，随后下跌到 \(90\)，最后上涨到 \(130\)。

从历史高点 \(120\) 到谷底 \(90\) 的损失比例为：

\[
\frac{90-120}{120}
\]

先计算分子：

\[
90-120=-30
\]

再除以峰值：

\[
\frac{-30}{120}=-0.25
\]

所以这段回撤为：

\[
-25\%
\]

若用正数表示最大回撤幅度，则为：

\[
25\%
\]

---

## 5. 最大回撤与单日最大跌幅不同

假设净值从 \(120\) 依次下降为：

```text
120, 114, 108, 102, 96, 90
```

每一期都只下跌约 \(5\%\)，但连续下跌后，净值从 \(120\) 下降到 \(90\)。

累计回撤仍然是：

\[
\frac{90}{120}-1=-25\%
\]

因此：

- 单日最大跌幅只观察某一个周期
- 最大回撤观察从历史峰值到后续谷底的累计损失
- 多个较小亏损可以累积成很大的回撤

---

## 6. 最大回撤与波动率不同

波动率主要衡量收益围绕均值的离散程度。

它通常同时把上涨偏离和下跌偏离计入风险。

最大回撤只关心净值从历史高点向下偏离的最严重程度。

因此，两者回答的问题不同：

- 波动率是分布型风险指标
- 最大回撤是路径型风险指标
- 波动率不记录收益发生的先后顺序
- 最大回撤高度依赖收益发生的顺序

---

# 二、净值与历史高点

## 7. 净值序列

设策略在第 \(t\) 期结束时的净值为：

\[
V_t
\]

净值可以是：

- 资金账户价值
- 累计收益指数
- 归一化后的策略净值
- 投资组合总资产

常见初始净值可以设为：

\[
V_0=1
\]

或：

\[
V_0=100
\]

最大回撤只依赖相对比例，因此初始净值设为 \(1\) 或 \(100\) 不会改变回撤结果。

---

## 8. 从简单收益率构造净值

设第 \(t\) 期简单收益率为：

\[
r_t
\]

净值递推关系为：

\[
V_t=V_{t-1}(1+r_t)
\]

继续展开：

\[
V_1=V_0(1+r_1)
\]

\[
V_2=V_1(1+r_2)
\]

代入 \(V_1\)：

\[
V_2=V_0(1+r_1)(1+r_2)
\]

一般地：

\[
V_t
=
V_0\prod_{i=1}^{t}(1+r_i)
\]

这说明净值来自收益率的连乘，而不是简单相加。

---

## 9. 历史高点

截至第 \(t\) 期的历史最高净值定义为：

\[
H_t
=
\max_{0\le s\le t}V_s
\]

其中：

- \(V_s\) 是第 \(s\) 期净值
- \(H_t\) 是截至第 \(t\) 期出现过的最高净值

因为历史高点只会保持不变或上升，所以：

\[
H_t\ge H_{t-1}
\]

历史高点序列是一个单调不下降序列。

---

## 10. 历史高点的递推关系

历史高点可以逐期更新：

\[
H_t
=
\max(H_{t-1},V_t)
\]

若当前净值创新高，即：

\[
V_t>H_{t-1}
\]

则：

\[
H_t=V_t
\]

若当前净值没有创新高，即：

\[
V_t\le H_{t-1}
\]

则：

\[
H_t=H_{t-1}
\]

在 pandas 中，这个过程对应累计最大值 `cummax()`。

---

# 三、回撤序列

## 11. 带符号回撤定义

第 \(t\) 期回撤定义为：

\[
D_t
=
\frac{V_t-H_t}{H_t}
\]

将分式拆开：

\[
D_t
=
\frac{V_t}{H_t}-\frac{H_t}{H_t}
\]

因为：

\[
\frac{H_t}{H_t}=1
\]

所以：

\[
D_t
=
\frac{V_t}{H_t}-1
\]

这两种写法完全等价。

---

## 12. 为什么回撤不会大于零

根据历史高点定义：

\[
H_t
=
\max_{0\le s\le t}V_s
\]

因此当前净值一定满足：

\[
V_t\le H_t
\]

两边同时除以正数 \(H_t\)：

\[
\frac{V_t}{H_t}\le 1
\]

两边同时减去 \(1\)：

\[
\frac{V_t}{H_t}-1\le 0
\]

因此：

\[
D_t\le 0
\]

当净值处于历史新高时：

\[
V_t=H_t
\]

所以：

\[
D_t=0
\]

当净值低于历史高点时：

\[
D_t<0
\]

---

## 13. 正数形式的回撤幅度

有些系统不使用负数回撤，而是定义回撤幅度：

\[
L_t
=
1-\frac{V_t}{H_t}
\]

因为：

\[
D_t
=
\frac{V_t}{H_t}-1
\]

所以：

\[
L_t=-D_t
\]

此时：

\[
L_t\ge 0
\]

例如：

- 带符号回撤为 \(-25\%\)
- 正数回撤幅度为 \(25\%\)

两种口径都可以使用，但输出时必须明确符号约定。

---

## 14. 手工计算回撤序列

给定净值：

```text
100, 110, 120, 108, 90, 99, 130
```

第一期净值为 \(100\)。

历史高点为：

\[
H_0=100
\]

回撤为：

\[
D_0
=
\frac{100}{100}-1
=0
\]

第二期净值为 \(110\)，创出新高。

\[
H_1=110
\]

\[
D_1
=
\frac{110}{110}-1
=0
\]

第三期净值为 \(120\)，再次创新高。

\[
H_2=120
\]

\[
D_2
=
\frac{120}{120}-1
=0
\]

第四期净值下降到 \(108\)，历史高点仍为 \(120\)。

\[
H_3=120
\]

\[
D_3
=
\frac{108}{120}-1
\]

\[
D_3
=0.9-1
\]

\[
D_3=-0.1
\]

所以回撤为：

\[
-10\%
\]

第五期净值下降到 \(90\)。

\[
H_4=120
\]

\[
D_4
=
\frac{90}{120}-1
\]

\[
D_4=0.75-1
\]

\[
D_4=-0.25
\]

所以回撤为：

\[
-25\%
\]

第六期净值恢复到 \(99\)，但仍未回到历史高点。

\[
H_5=120
\]

\[
D_5
=
\frac{99}{120}-1
\]

\[
D_5=0.825-1
\]

\[
D_5=-0.175
\]

所以回撤为：

\[
-17.5\%
\]

第七期净值上涨到 \(130\)，创出新高。

\[
H_6=130
\]

\[
D_6
=
\frac{130}{130}-1
=0
\]

最终回撤序列为：

```text
0%, 0%, 0%, -10%, -25%, -17.5%, 0%
```

---

# 四、最大回撤

## 15. 带符号最大回撤

给定整个样本期的回撤序列：

\[
D_0,D_1,\ldots,D_T
\]

带符号最大回撤定义为：

\[
MDD_{signed}
=
\min_{0\le t\le T}D_t
\]

因为每一期回撤都不大于零，所以最小值就是最严重的负回撤。

在前面的例子中：

\[
MDD_{signed}=-25\%
\]

---

## 16. 正数最大回撤幅度

正数形式可以定义为：

\[
MDD
=
-\min_{0\le t\le T}D_t
\]

也可以直接写为：

\[
MDD
=
\max_{0\le t\le T}
\left(
1-\frac{V_t}{H_t}
\right)
\]

在前面的例子中：

\[
MDD=25\%
\]

---

## 17. 峰谷形式的定义

最大回撤还可以写成峰值与后续谷底的优化问题：

\[
MDD_{signed}
=
\min_{0\le s\le t\le T}
\left(
\frac{V_t}{V_s}-1
\right)
\]

约束：

\[
s\le t
\]

非常重要。

它表示：

- 峰值必须先发生
- 谷底必须后发生
- 不能拿未来高点与过去低点进行比较

最大回撤是一项有时间顺序约束的路径指标。

---

## 18. 为什么不能直接用全局最高值和全局最低值

假设净值序列为：

```text
80, 100, 130, 120
```

全局最低值是 \(80\)，全局最高值是 \(130\)。

但最低值 \(80\) 出现在最高值 \(130\) 之前。

不能将 \(130\) 到 \(80\) 视为策略经历过的回撤，因为时间顺序相反。

真正的最大回撤来自 \(130\) 到 \(120\)：

\[
\frac{120}{130}-1
\]

\[
=-0.076923\ldots
\]

约为：

\[
-7.69\%
\]

因此，下面这种算法通常是错误的：

```python
nav.min() / nav.max() - 1
```

它没有保证最高点发生在最低点之前。

---

# 五、峰值、谷底与修复

## 19. 峰值时点

设最大回撤发生在谷底时点 \(t^\ast\)。

截至该谷底时点的历史最高净值为：

\[
H_{t^\ast}
\]

对应的峰值时点记为：

\[
s^\ast
\]

满足：

\[
V_{s^\ast}=H_{t^\ast}
\]

并且：

\[
s^\ast\le t^\ast
\]

---

## 20. 谷底时点

谷底时点是回撤序列达到最小值的位置：

\[
t^\ast
=
\arg\min_t D_t
\]

最大回撤为：

\[
MDD_{signed}=D_{t^\ast}
\]

---

## 21. 修复时点

设最大回撤峰值净值为：

\[
V_{s^\ast}
\]

谷底之后，第一次重新达到或超过峰值净值的时点记为：

\[
u^\ast
=
\min
\left\{
u>t^\ast:V_u\ge V_{s^\ast}
\right\}
\]

若样本结束时仍未恢复到原峰值，则修复时点不存在。

代码中可以使用：

```text
None
```

或缺失值表示尚未修复。

---

## 22. 下跌时长与修复时长

最大回撤区间可以拆成两个阶段。

下跌阶段：

\[
s^\ast\rightarrow t^\ast
\]

下跌时长为：

\[
T_{decline}=t^\ast-s^\ast
\]

修复阶段：

\[
t^\ast\rightarrow u^\ast
\]

修复时长为：

\[
T_{recovery}=u^\ast-t^\ast
\]

完整水下时长为：

\[
T_{underwater}=u^\ast-s^\ast
\]

在日频交易数据中，可以用交易日数量表示；也可以用自然日差值表示。

两者必须明确区分。

---

## 23. 回撤深度和回撤时长是不同风险

两个策略都可能有 \(20\%\) 最大回撤。

但：

- 策略 A 在 10 个交易日内修复
- 策略 B 在 500 个交易日后仍未修复

两者最大回撤深度相同，但资金占用和心理压力完全不同。

因此，完整的回撤分析至少应记录：

- 最大回撤深度
- 峰值时点
- 谷底时点
- 是否修复
- 修复时点
- 下跌时长
- 修复时长
- 最长水下时长

---

# 六、亏损后的回本收益率

## 24. 为什么亏损比例和回本收益率不对称

假设初始净值为：

\[
V_0
\]

发生比例为 \(m\) 的亏损，其中：

\[
0<m<1
\]

亏损后的净值为：

\[
V_1=V_0(1-m)
\]

设需要获得比例为 \(g\) 的收益才能回到原净值。

则：

\[
V_1(1+g)=V_0
\]

代入 \(V_1\)：

\[
V_0(1-m)(1+g)=V_0
\]

两边同时除以 \(V_0\)：

\[
(1-m)(1+g)=1
\]

两边同时除以 \(1-m\)：

\[
1+g=\frac{1}{1-m}
\]

两边同时减去 \(1\)：

\[
g=\frac{1}{1-m}-1
\]

通分：

\[
g
=
\frac{1-(1-m)}{1-m}
\]

化简分子：

\[
g
=
\frac{m}{1-m}
\]

所以回本所需收益率为：

\[
\boxed{
g=\frac{m}{1-m}
}
\]

---

## 25. 回本收益率示例

若最大回撤幅度为：

\[
m=25\%
\]

则：

\[
g
=
\frac{25\%}{1-25\%}
\]

\[
g
=
\frac{25\%}{75\%}
\]

\[
g=33.33\%\ldots
\]

因此亏损 \(25\%\) 后，需要上涨约 \(33.33\%\) 才能回本。

若亏损 \(50\%\)：

\[
g
=
\frac{50\%}{1-50\%}
\]

\[
g
=
\frac{50\%}{50\%}
\]

\[
g=100\%
\]

亏损越大，回本难度增长越快。

---

# 七、最大回撤的数学性质

## 26. 尺度不变性

假设把全部净值乘以正常数 \(c\)：

\[
V'_t=cV_t
\]

新的历史高点为：

\[
H'_t
=
\max_{s\le t}V'_s
\]

代入 \(V'_s=cV_s\)：

\[
H'_t
=
\max_{s\le t}(cV_s)
\]

因为 \(c>0\)，所以：

\[
H'_t
=
c\max_{s\le t}V_s
\]

因此：

\[
H'_t=cH_t
\]

新的回撤为：

\[
D'_t
=
\frac{V'_t}{H'_t}-1
\]

代入：

\[
D'_t
=
\frac{cV_t}{cH_t}-1
\]

约去 \(c\)：

\[
D'_t
=
\frac{V_t}{H_t}-1
\]

所以：

\[
D'_t=D_t
\]

因此，把净值从 \(1\) 放大到 \(100\) 或 \(1{,}000{,}000\)，最大回撤不变。

---

## 27. 路径依赖性

考虑两条净值路径。

路径 A：

```text
100, 120, 80, 110
```

路径 B：

```text
100, 80, 120, 110
```

两条路径的起点都是 \(100\)，终点都是 \(110\)，包含的中间净值集合也相同。

路径 A 的历史高点先达到 \(120\)，随后下降到 \(80\)。

其回撤为：

\[
\frac{80}{120}-1
\]

\[
=-\frac{1}{3}
\]

约为：

\[
-33.33\%
\]

路径 B 先下降到 \(80\)，此时历史高点仍为 \(100\)。

其回撤为：

\[
\frac{80}{100}-1
\]

\[
=-20\%
\]

因此，改变收益发生顺序会改变最大回撤。

最大回撤不是只由收益集合决定，而是由收益顺序和净值路径共同决定。

---

## 28. 最大回撤不具有简单可加性

两个时间区间的最大回撤不能简单相加。

若第一段最大回撤为 \(10\%\)，第二段最大回撤为 \(15\%\)，全样本最大回撤不一定是：

\[
10\%+15\%=25\%
\]

全样本最大回撤可能：

- 等于其中较大的一段
- 跨越两个区间
- 在区间连接处形成更大回撤

原因是历史高点会跨区间延续。

---

## 29. 最大回撤不是未来损失上限

历史最大回撤只描述已经观察到的样本。

它不表示未来回撤不会超过该数值。

如果样本较短、市场状态单一或回测存在过拟合，历史最大回撤可能严重低估真实风险。

因此，最大回撤必须与以下信息一起解释：

- 样本长度
- 市场阶段
- 交易成本
- 杠杆水平
- 数据频率
- 样本内与样本外表现
- 压力测试结果

---

# 八、数据频率与口径

## 30. 日频最大回撤只观察收盘路径

使用日收盘净值计算的最大回撤，只能观察日与日之间的收盘变化。

它无法识别：

- 盘中大幅下跌后收回
- 开盘跳空和盘中极端价格
- 日内强平风险
- 实际成交造成的盘中资金低点

因此：

\[
MDD_{daily\ close}
\]

不一定等于：

\[
MDD_{intraday}
\]

通常更高频的数据能够观察到更多路径细节，也可能得到更深的最大回撤。

---

## 31. 缺失值处理

净值序列中的缺失值可能来自：

- 非交易日
- 数据源缺口
- 策略尚未开始
- 标的停牌
- 计算失败

不能不加判断地使用前值填充。

前值填充意味着假设缺失期间净值完全不变。

这种假设可能：

- 改变回撤持续时间
- 掩盖真实波动
- 影响修复时点

基础函数可以先删除缺失值，但研究报告必须记录处理方式。

---

## 32. 净值必须为正数

标准回撤公式包含：

\[
\frac{V_t}{H_t}
\]

若净值为零或负数，传统比例回撤的经济解释会出现问题。

因此，基础实现通常要求：

\[
V_t>0
\]

若策略可能出现负权益，应另行定义风险指标，而不能直接沿用普通净值回撤公式。

---

## 33. 收益率不能小于或等于 \(-100\%\)

从简单收益率构造净值时：

\[
V_t=V_{t-1}(1+r_t)
\]

若：

\[
r_t=-100\%
\]

则：

\[
1+r_t=0
\]

净值归零。

若：

\[
r_t<-100\%
\]

则普通无杠杆资产的简单收益解释通常不成立，并会产生负净值。

因此，基础函数应检查：

\[
r_t>-1
\]

---

# 九、常见错误

## 34. 错误一：直接对收益率调用最小值

错误写法：

```python
maximum_drawdown = returns.min()
```

这得到的是最差单期收益，而不是最大回撤。

正确过程是：

1. 从收益率构造净值
2. 计算历史高点
3. 计算回撤序列
4. 取回撤最小值

---

## 35. 错误二：使用全局最低值除以全局最高值

错误写法：

```python
maximum_drawdown = nav.min() / nav.max() - 1
```

该方法没有保证最高点出现在最低点之前。

正确方法必须使用逐期历史高点：

```python
running_peak = nav.cummax()
drawdown = nav / running_peak - 1
maximum_drawdown = drawdown.min()
```

---

## 36. 错误三：混淆负数和正数口径

函数 A 返回：

```text
-0.25
```

函数 B 返回：

```text
0.25
```

两者都可能表示 \(25\%\) 最大回撤。

若不说明口径，后续计算 Calmar 比率时可能出现符号错误。

建议：

- 底层回撤序列保留负数
- 报表可额外输出正数幅度
- 字段名明确使用 `max_drawdown_signed` 和 `max_drawdown_magnitude`

---

## 37. 错误四：把未修复回撤当作已经结束

如果样本结束时净值仍低于峰值，则该回撤仍在持续。

此时：

- 可以确定峰值和当前谷底
- 不能给出真实修复时点
- 修复时长仍是未知的

不能把样本结束日期自动写成修复日期。

---

## 38. 错误五：忽略复权、现金流和费用

若净值由股票价格直接构造，需要明确：

- 是否前复权或后复权
- 是否包含分红
- 是否包含手续费
- 是否包含滑点
- 是否存在申购赎回等外部现金流

外部现金流若未正确调整，会造成虚假的净值跳变和回撤。

---

# 十、Python 实现

## 39. 今天需要掌握的 Python 函数

今天重点掌握：

```text
pd.Series()
dropna()
to_numpy()
np.isfinite()
any()
cumprod()
cummax()
min()
idxmin()
np.flatnonzero()
rolling()
apply()
np.maximum.accumulate()
np.isclose()
```

理解用途比死记参数更重要。

---

## 40. 导入依赖

```python
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
```

---

## 41. 从收益率构造净值

```python
def nav_from_returns(
    returns: pd.Series,
    initial_nav: float = 1.0,
) -> pd.Series:
    """从简单收益率序列构造净值序列。"""
    clean = pd.Series(returns, dtype="float64").dropna()

    if clean.empty:
        raise ValueError("收益率序列不能为空")

    if not np.isfinite(clean.to_numpy()).all():
        raise ValueError("收益率必须为有限数")

    if initial_nav <= 0.0 or not np.isfinite(initial_nav):
        raise ValueError("initial_nav 必须为有限正数")

    if (clean <= -1.0).any():
        raise ValueError("简单收益率必须大于 -100%")

    nav = initial_nav * (1.0 + clean).cumprod()
    nav.name = "nav"
    return nav
```

核心代码是：

```python
(1.0 + clean).cumprod()
```

它对应数学公式：

\[
\prod_{i=1}^{t}(1+r_i)
\]

---

## 42. 计算回撤序列

```python
def drawdown_series(nav: pd.Series) -> pd.Series:
    """根据正净值序列计算带符号回撤序列。"""
    clean = pd.Series(nav, dtype="float64").dropna()

    if clean.empty:
        raise ValueError("净值序列不能为空")

    if not np.isfinite(clean.to_numpy()).all():
        raise ValueError("净值必须为有限数")

    if (clean <= 0.0).any():
        raise ValueError("净值必须全部大于零")

    running_peak = clean.cummax()
    drawdown = clean / running_peak - 1.0
    drawdown.name = "drawdown"
    return drawdown
```

其中：

```python
running_peak = clean.cummax()
```

对应：

\[
H_t=\max_{s\le t}V_s
\]

而：

```python
drawdown = clean / running_peak - 1.0
```

对应：

\[
D_t=\frac{V_t}{H_t}-1
\]

---

## 43. 计算最大回撤

```python
def maximum_drawdown(
    nav: pd.Series,
    as_positive: bool = False,
) -> float:
    """计算最大回撤；默认返回负数，as_positive=True 时返回正数幅度。"""
    drawdown = drawdown_series(nav)
    signed_mdd = float(drawdown.min())

    if as_positive:
        return -signed_mdd

    return signed_mdd
```

示例：

```python
nav = pd.Series([100, 110, 120, 108, 90, 99, 130])

signed = maximum_drawdown(nav)
magnitude = maximum_drawdown(nav, as_positive=True)

print(signed)
print(magnitude)
```

预期结果：

```text
-0.25
0.25
```

---

## 44. 查找最大回撤峰谷区间

```python
def maximum_drawdown_info(nav: pd.Series) -> dict[str, Any]:
    """返回最大回撤深度、峰值、谷底和修复信息。"""
    clean = pd.Series(nav, dtype="float64").dropna()

    if clean.empty:
        raise ValueError("净值序列不能为空")

    if not np.isfinite(clean.to_numpy()).all():
        raise ValueError("净值必须为有限数")

    if (clean <= 0.0).any():
        raise ValueError("净值必须全部大于零")

    running_peak = clean.cummax()
    drawdown = clean / running_peak - 1.0

    trough_label = drawdown.idxmin()
    trough_position = clean.index.get_loc(trough_label)

    history_to_trough = clean.iloc[: trough_position + 1]
    peak_label = history_to_trough.idxmax()
    peak_position = clean.index.get_loc(peak_label)

    peak_value = float(clean.loc[peak_label])
    trough_value = float(clean.loc[trough_label])
    signed_mdd = float(drawdown.loc[trough_label])

    future = clean.iloc[trough_position + 1 :]
    recovered = future >= peak_value

    if recovered.any():
        recovery_relative_position = int(
            np.flatnonzero(recovered.to_numpy())[0]
        )
        recovery_position = (
            trough_position + 1 + recovery_relative_position
        )
        recovery_label = clean.index[recovery_position]
        recovery_periods = recovery_position - trough_position
        underwater_periods = recovery_position - peak_position
    else:
        recovery_label = None
        recovery_position = None
        recovery_periods = None
        underwater_periods = None

    return {
        "max_drawdown_signed": signed_mdd,
        "max_drawdown_magnitude": -signed_mdd,
        "peak": peak_label,
        "trough": trough_label,
        "recovery": recovery_label,
        "peak_value": peak_value,
        "trough_value": trough_value,
        "decline_periods": trough_position - peak_position,
        "recovery_periods": recovery_periods,
        "underwater_periods": underwater_periods,
        "is_recovered": recovery_position is not None,
    }
```

---

## 45. 为什么峰值只能在谷底之前查找

代码中使用：

```python
history_to_trough = clean.iloc[: trough_position + 1]
peak_label = history_to_trough.idxmax()
```

而不是：

```python
peak_label = clean.idxmax()
```

因为全样本最高点可能出现在谷底之后。

峰值必须满足：

\[
s^\ast\le t^\ast
\]

所以只能在谷底及其之前的历史区间寻找峰值。

---

## 46. 从收益率直接计算最大回撤

```python
def maximum_drawdown_from_returns(
    returns: pd.Series,
    initial_nav: float = 1.0,
    as_positive: bool = False,
) -> float:
    """先构造净值，再计算最大回撤。"""
    nav = nav_from_returns(
        returns=returns,
        initial_nav=initial_nav,
    )

    return maximum_drawdown(
        nav=nav,
        as_positive=as_positive,
    )
```

这个函数仍然遵循正确顺序：

```text
收益率 → 净值 → 历史高点 → 回撤 → 最大回撤
```

---

## 47. 计算滚动最大回撤

```python
def rolling_maximum_drawdown(
    nav: pd.Series,
    window: int = 60,
) -> pd.Series:
    """计算每个滚动窗口内部的带符号最大回撤。"""
    clean = pd.Series(nav, dtype="float64")

    if window < 2:
        raise ValueError("window 至少为 2")

    def window_mdd(values: np.ndarray) -> float:
        running_peak = np.maximum.accumulate(values)
        drawdowns = values / running_peak - 1.0
        return float(drawdowns.min())

    result = clean.rolling(
        window=window,
        min_periods=window,
    ).apply(
        window_mdd,
        raw=True,
    )

    result.name = "rolling_max_drawdown"
    return result
```

滚动最大回撤回答：

> 截至每个时点，最近一个窗口内部最严重的回撤是多少？

注意，窗口开始之前的历史高点不会进入当前窗口。

因此，滚动最大回撤与全历史扩展最大回撤的含义不同。

---

## 48. 扩展窗口最大回撤

若要观察截至每个时点的历史最大回撤，可以直接对回撤序列取累计最小值：

```python
def expanding_maximum_drawdown(nav: pd.Series) -> pd.Series:
    """计算截至每个时点的历史带符号最大回撤。"""
    drawdowns = drawdown_series(nav)
    result = drawdowns.cummin()
    result.name = "expanding_max_drawdown"
    return result
```

其数学形式为：

\[
MDD_t
=
\min_{0\le u\le t}D_u
\]

这个序列只会保持不变或变得更负。

---

# 十一、函数验证

## 49. 验证一：已知净值样例

```python
nav = pd.Series(
    [100, 110, 120, 108, 90, 99, 130],
    index=pd.date_range("2026-01-01", periods=7, freq="D"),
)

result = maximum_drawdown(nav)

assert np.isclose(result, -0.25)
```

因为峰值为 \(120\)，谷底为 \(90\)：

\[
\frac{90}{120}-1=-0.25
\]

---

## 50. 验证二：检查完整区间

```python
info = maximum_drawdown_info(nav)

assert np.isclose(info["max_drawdown_signed"], -0.25)
assert np.isclose(info["max_drawdown_magnitude"], 0.25)
assert info["peak"] == nav.index[2]
assert info["trough"] == nav.index[4]
assert info["recovery"] == nav.index[6]
assert info["decline_periods"] == 2
assert info["recovery_periods"] == 2
assert info["underwater_periods"] == 4
assert info["is_recovered"] is True
```

---

## 51. 验证三：单调上涨净值

```python
rising_nav = pd.Series([100, 101, 103, 105, 110])

result = maximum_drawdown(rising_nav)

assert np.isclose(result, 0.0)
```

单调上涨净值每一期都处于历史高点，因此回撤始终为零。

---

## 52. 验证四：尚未修复的回撤

```python
unrecovered_nav = pd.Series(
    [100, 120, 110, 90, 95, 100]
)

info = maximum_drawdown_info(unrecovered_nav)

assert np.isclose(info["max_drawdown_signed"], -0.25)
assert info["recovery"] is None
assert info["recovery_periods"] is None
assert info["underwater_periods"] is None
assert info["is_recovered"] is False
```

样本结束时净值为 \(100\)，仍低于峰值 \(120\)，所以尚未修复。

---

## 53. 验证五：尺度不变性

```python
nav_small = pd.Series([1.0, 1.2, 0.9, 1.3])
nav_large = nav_small * 1_000_000

mdd_small = maximum_drawdown(nav_small)
mdd_large = maximum_drawdown(nav_large)

assert np.isclose(mdd_small, mdd_large)
```

因为比例回撤不会受到净值单位影响。

---

## 54. 验证六：错误输入

```python
try:
    maximum_drawdown(pd.Series([100, 0, 110]))
except ValueError as exc:
    print(exc)
```

净值为零时应触发异常。

```python
try:
    nav_from_returns(pd.Series([0.01, -1.0, 0.02]))
except ValueError as exc:
    print(exc)
```

简单收益率等于 \(-100\%\) 时，净值归零，因此基础函数应拒绝该输入。

---

# 十二、结果解释

## 55. 最大回撤越小越好吗

在其他条件相同的情况下，最大回撤幅度越小通常越好。

但不能单独根据最大回撤选择策略。

例如：

- 策略 A 年化收益 \(5\%\)，最大回撤 \(3\%\)
- 策略 B 年化收益 \(20\%\)，最大回撤 \(10\%\)

不能只因为策略 A 回撤较小，就断定策略 A 更优。

需要结合：

- 年化收益
- 年化波动率
- 夏普比率
- 最大回撤
- 回撤时长
- Calmar 比率
- 稳定性与交易成本

明天将学习如何用 Calmar 比率连接年化收益与最大回撤。

---

## 56. 最大回撤对样本长度敏感

样本越长，经历极端市场环境的概率通常越高，观察到更大回撤的可能性也越高。

因此：

- 1 年策略的最大回撤
- 5 年策略的最大回撤
- 15 年策略的最大回撤

不能脱离样本长度直接比较。

比较不同策略时，应尽量使用相同时间区间和相同数据频率。

---

## 57. 最大回撤对起止日期敏感

改变回测起点，可能改变：

- 初始历史高点
- 最大回撤峰值
- 回撤持续时间
- 是否已经修复

因此，应避免只选择对策略最有利的起止日期。

推荐同时观察：

- 全样本最大回撤
- 分年度最大回撤
- 滚动窗口最大回撤
- 样本外最大回撤

---

## 58. 杠杆与最大回撤

杠杆通常会放大收益和亏损，但最大回撤不一定按照固定倍数简单变化。

原因包括：

- 收益连续复利
- 杠杆可能随净值变化
- 交易成本随换手变化
- 极端亏损可能触发减仓或强平
- 收益率接近 \(-100\%\) 时存在非线性边界

因此，不能简单认为两倍杠杆一定等于两倍最大回撤。

必须重新构造杠杆后的净值路径并计算。

---

# 十三、练习

## 59. 练习一：手工计算回撤序列

给定净值：

```text
100, 125, 115, 90, 100, 130
```

计算：

1. 历史高点序列
2. 回撤序列
3. 带符号最大回撤
4. 正数最大回撤幅度

### 解答

历史高点序列为：

```text
100, 125, 125, 125, 125, 130
```

前三个关键回撤依次为：

\[
\frac{115}{125}-1=-8\%
\]

\[
\frac{90}{125}-1=-28\%
\]

\[
\frac{100}{125}-1=-20\%
\]

完整回撤序列为：

```text
0%, 0%, -8%, -28%, -20%, 0%
```

因此带符号最大回撤为：

\[
-28\%
\]

正数最大回撤幅度为：

\[
28\%
\]

---

## 60. 练习二：计算回本收益率

某策略最大回撤幅度为 \(40\%\)。

从谷底恢复到原峰值需要上涨多少？

### 解答

使用公式：

\[
g=\frac{m}{1-m}
\]

代入：

\[
g
=
\frac{40\%}{1-40\%}
\]

\[
g
=
\frac{40\%}{60\%}
\]

\[
g=66.67\%\ldots
\]

因此需要上涨约：

\[
66.67\%
\]

---

## 61. 练习三：识别错误算法

下面代码是否正确？

```python
mdd = nav.min() / nav.max() - 1
```

### 解答

不一定正确。

它没有保证最高点发生在最低点之前。

正确写法为：

```python
running_peak = nav.cummax()
drawdowns = nav / running_peak - 1
mdd = drawdowns.min()
```

---

## 62. 练习四：判断回撤是否修复

给定净值：

```text
100, 120, 90, 105, 118
```

最大回撤是否已经修复？

### 解答

最大回撤峰值为：

\[
120
\]

样本结束净值为：

\[
118
\]

因为：

\[
118<120
\]

所以最大回撤尚未修复。

不能把最后一个时点当作修复时点。

---

## 63. 练习五：证明尺度不变性

设：

\[
V'_t=10V_t
\]

证明新净值序列与原净值序列的回撤相同。

### 解答

新的历史高点为：

\[
H'_t
=
\max_{s\le t}(10V_s)
\]

提出正常数 \(10\)：

\[
H'_t
=
10\max_{s\le t}V_s
\]

所以：

\[
H'_t=10H_t
\]

新的回撤为：

\[
D'_t
=
\frac{V'_t}{H'_t}-1
\]

代入：

\[
D'_t
=
\frac{10V_t}{10H_t}-1
\]

约去 \(10\)：

\[
D'_t
=
\frac{V_t}{H_t}-1
\]

所以：

\[
D'_t=D_t
\]

证毕。

---

## 64. 练习六：编程练习

使用以下收益率序列：

```python
returns = pd.Series([
    0.05,
    0.10,
    -0.08,
    -0.15,
    0.06,
    0.20,
])
```

完成：

1. 构造初始净值为 \(100\) 的净值序列
2. 计算回撤序列
3. 计算最大回撤
4. 输出峰值、谷底和修复状态
5. 用断言检查带符号回撤不大于零

参考断言：

```python
nav = nav_from_returns(returns, initial_nav=100.0)
drawdowns = drawdown_series(nav)
info = maximum_drawdown_info(nav)

assert (drawdowns <= 0.0).all()
assert np.isclose(drawdowns.iloc[0], 0.0)
assert info["max_drawdown_signed"] <= 0.0
assert info["max_drawdown_magnitude"] >= 0.0
```

---

# 十四、今日输出

## 65. 最小可复用版本

今天至少应保留三个函数：

```python
nav_from_returns()
drawdown_series()
maximum_drawdown()
```

推荐继续保留：

```python
maximum_drawdown_info()
maximum_drawdown_from_returns()
rolling_maximum_drawdown()
expanding_maximum_drawdown()
```

---

## 66. 推荐指标输出字段

后续统一绩效评价模块中，回撤部分建议输出：

```text
max_drawdown_signed
max_drawdown_magnitude
max_drawdown_peak
max_drawdown_trough
max_drawdown_recovery
peak_value
trough_value
decline_periods
recovery_periods
underwater_periods
is_recovered
```

只输出一个最大回撤数值，会丢失大量路径信息。

---

## 67. 今日应完成的代码结构

建议将今天的函数暂时整理为：

```text
performance_metrics.py
├── nav_from_returns
├── drawdown_series
├── maximum_drawdown
├── maximum_drawdown_info
├── maximum_drawdown_from_returns
├── rolling_maximum_drawdown
└── expanding_maximum_drawdown
```

第七天再统一整理整个绩效评价模块的接口、返回字段和测试。

---

# 十五、今日检查清单

完成学习后，检查自己能否回答：

- [ ] 最大回撤衡量的核心问题是什么
- [ ] 为什么最大回撤必须基于净值路径
- [ ] 历史高点如何定义
- [ ] 回撤序列如何定义
- [ ] 为什么带符号回撤不大于零
- [ ] 带符号最大回撤与正数回撤幅度有什么区别
- [ ] 为什么不能直接使用全局最低净值除以全局最高净值
- [ ] 峰值和谷底必须满足什么时间顺序
- [ ] 如何寻找最大回撤的峰值时点
- [ ] 如何寻找最大回撤的谷底时点
- [ ] 什么条件表示回撤已经修复
- [ ] 下跌时长、修复时长和水下时长有什么区别
- [ ] 为什么亏损 \(25\%\) 后需要上涨 \(33.33\%\) 才能回本
- [ ] 如何逐行推导回本收益率公式
- [ ] 为什么最大回撤具有尺度不变性
- [ ] 为什么最大回撤具有路径依赖性
- [ ] 为什么最大回撤不能简单跨区间相加
- [ ] 日频收盘最大回撤遗漏了哪些风险
- [ ] 缺失值处理为什么可能影响回撤时长
- [ ] 为什么净值必须为正数
- [ ] 如何从收益率构造净值
- [ ] `cumprod()` 在净值计算中有什么作用
- [ ] `cummax()` 在回撤计算中有什么作用
- [ ] 如何编写最大回撤函数
- [ ] 如何返回峰值、谷底和修复信息
- [ ] 滚动最大回撤与扩展最大回撤有什么区别
- [ ] 为什么历史最大回撤不是未来损失上限

---

# 十六、今日总结

今天最重要的历史高点公式是：

\[
H_t
=
\max_{0\le s\le t}V_s
\]

最重要的回撤公式是：

\[
D_t
=
\frac{V_t}{H_t}-1
\]

带符号最大回撤为：

\[
MDD_{signed}
=
\min_t D_t
\]

正数最大回撤幅度为：

\[
MDD
=
-\min_t D_t
\]

亏损幅度为 \(m\) 时，回本所需收益率为：

\[
g
=
\frac{m}{1-m}
\]

今天最核心的认识是：

> 最大回撤不是最差单日收益，也不是全局最高值与最低值的简单比例。它是遵守时间顺序的净值峰谷损失，是一个具有路径依赖性的风险指标。

下一天将学习 Calmar 比率与超额收益，把年化收益、最大回撤和基准表现连接起来。