# 第八周 · 第六天

## 双样本检验、错误类型与多重检验

---

## 1. 今日学习目标

完成今天的学习后，你需要能够：

- 判断研究问题应使用独立双样本检验还是配对样本检验
- 理解两组均值差异检验的原假设和备择假设
- 掌握 Welch 独立双样本 t 检验的统计量
- 理解等方差 t 检验与 Welch t 检验的区别
- 掌握配对 t 检验与“对差值做单样本 t 检验”的等价关系
- 理解第一类错误、第二类错误、显著性水平与检验功效
- 认识样本量、效应大小、波动率与检验功效之间的关系
- 理解多重检验为什么会提高错误发现概率
- 掌握 Bonferroni 修正的基本原理
- 同时报告均值差、置信区间、效应大小和 p 值
- 使用 NumPy 与 SciPy 完成双样本检验
- 编写一个可复用的多重检验演示程序
- 识别量化研究中的数据窥探与策略筛选偏差

---

## 2. 今日学习顺序

建议学习时间：约 140—170 分钟。

| 阶段 | 内容 | 建议时间 |
|---|---|---:|
| 1 | 回顾单样本 t 检验 | 15 分钟 |
| 2 | 独立双样本检验 | 30 分钟 |
| 3 | 配对样本检验 | 25 分钟 |
| 4 | 第一类与第二类错误 | 25 分钟 |
| 5 | 多重检验与 Bonferroni 修正 | 25 分钟 |
| 6 | Python 实践 | 35 分钟 |
| 7 | 练习与复盘 | 15 分钟 |

---

# 一、从单样本检验进入双样本检验

## 3. 昨天解决的问题

昨天学习的单样本 t 检验用于判断一个总体均值是否等于某个基准值。

例如，检验某策略的平均日收益是否为 0：

\[
H_0:\mu=0
\]

\[
H_1:\mu\neq0
\]

单样本 t 统计量为：

\[
t=\frac{\bar{x}-\mu_0}{s/\sqrt{n}}
\]

其中：

- \(\bar{x}\) 是样本均值
- \(\mu_0\) 是原假设中的总体均值
- \(s\) 是样本标准差
- \(n\) 是样本量

---

## 4. 今天解决的问题

今天不再只比较“一个样本与一个固定值”，而是比较两个样本。

量化研究中的典型问题包括：

- 策略 A 的平均收益是否高于策略 B？
- 高市值组与低市值组的平均收益是否不同？
- 事件发生前后的平均收益是否变化？
- 同一批股票采用新旧信号后的收益是否不同？
- 牛市样本与熊市样本中的因子收益是否不同？

这些问题都在研究两个均值之间的差异。

令两个总体均值分别为：

\[
\mu_1
\]

和：

\[
\mu_2
\]

最常见的双侧检验为：

\[
H_0:\mu_1-\mu_2=0
\]

\[
H_1:\mu_1-\mu_2\neq0
\]

也可以写成：

\[
H_0:\mu_1=\mu_2
\]

\[
H_1:\mu_1\neq\mu_2
\]

---

# 二、先判断样本关系

## 5. 独立样本与配对样本

在选择检验方法之前，最重要的问题不是先看均值，而是判断两个样本之间是否存在一一对应关系。

### 独立样本

两个样本中的观测对象彼此不同，并且没有自然配对关系。

例如：

- 一组是 100 只高市值股票，另一组是 100 只低市值股票
- 一组是策略 A 的独立交易，另一组是策略 B 的独立交易
- 一组来自行业 A，另一组来自行业 B

独立样本常使用：

> 独立双样本 t 检验，通常优先使用 Welch t 检验。

### 配对样本

两个样本中的观测值可以一一配对。

例如：

- 同一只股票在事件前与事件后的收益
- 同一交易日在策略 A 与策略 B 下的收益
- 同一批股票使用新模型和旧模型的预测误差
- 同一个组合在调整交易成本前后的净收益

配对样本常使用：

> 配对 t 检验。

---

## 6. 判断规则

可以按以下顺序判断：

1. 两组数据是否来自相同对象？
2. 每个第一组观测值是否都有唯一对应的第二组观测值？
3. 配对关系是否具有研究含义？
4. 两组样本长度是否相同？

如果答案基本都是“是”，通常应使用配对检验。

如果两组观测来自不同对象，而且不存在稳定的一一对应关系，通常使用独立双样本检验。

注意：

> 两组样本长度相同，不代表它们一定是配对样本。

只有存在真实、明确、有意义的一一对应关系时，才能使用配对检验。

---

# 三、独立双样本 t 检验

## 7. 研究目标

设第一组样本为：

\[
x_1,x_2,\ldots,x_{n_1}
\]

第二组样本为：

\[
y_1,y_2,\ldots,y_{n_2}
\]

两个总体均值分别为：

\[
\mu_x
\]

和：

\[
\mu_y
\]

双侧检验为：

\[
H_0:\mu_x-\mu_y=0
\]

\[
H_1:\mu_x-\mu_y\neq0
\]

右侧检验可以写为：

\[
H_0:\mu_x-\mu_y\leq0
\]

\[
H_1:\mu_x-\mu_y>0
\]

例如，检验策略 A 的平均收益是否高于策略 B。

---

## 8. 两组样本均值

第一组样本均值为：

\[
\bar{x}=\frac{1}{n_1}\sum_{i=1}^{n_1}x_i
\]

第二组样本均值为：

\[
\bar{y}=\frac{1}{n_2}\sum_{j=1}^{n_2}y_j
\]

样本均值差为：

\[
\widehat{\Delta}=\bar{x}-\bar{y}
\]

这里的 \(\widehat{\Delta}\) 是总体均值差：

\[
\Delta=\mu_x-\mu_y
\]

的点估计。

---

## 9. 均值差的标准误

如果两组样本相互独立，则有：

\[
\operatorname{Var}(\bar{x}-\bar{y})
=\operatorname{Var}(\bar{x})+\operatorname{Var}(\bar{y})
\]

逐步推导如下。

第一步：

\[
\operatorname{Var}(\bar{x})=\frac{\sigma_x^2}{n_1}
\]

第二步：

\[
\operatorname{Var}(\bar{y})=\frac{\sigma_y^2}{n_2}
\]

第三步，因为两组样本独立，所以协方差为 0：

\[
\operatorname{Cov}(\bar{x},\bar{y})=0
\]

第四步：

\[
\operatorname{Var}(\bar{x}-\bar{y})
=\operatorname{Var}(\bar{x})
+\operatorname{Var}(\bar{y})
-2\operatorname{Cov}(\bar{x},\bar{y})
\]

第五步，代入协方差为 0：

\[
\operatorname{Var}(\bar{x}-\bar{y})
=\frac{\sigma_x^2}{n_1}+\frac{\sigma_y^2}{n_2}
\]

第六步，对方差开平方，得到均值差的标准误：

\[
SE(\bar{x}-\bar{y})
=\sqrt{\frac{\sigma_x^2}{n_1}+\frac{\sigma_y^2}{n_2}}
\]

由于总体方差未知，实际计算中用样本方差代替：

\[
SE(\bar{x}-\bar{y})
=\sqrt{\frac{s_x^2}{n_1}+\frac{s_y^2}{n_2}}
\]

---

## 10. Welch t 统计量

Welch t 检验不要求两个总体方差相等。

统计量为：

\[
t
=\frac{(\bar{x}-\bar{y})-\Delta_0}
{\sqrt{\frac{s_x^2}{n_1}+\frac{s_y^2}{n_2}}}
\]

通常原假设中的均值差为：

\[
\Delta_0=0
\]

因此：

\[
t
=\frac{\bar{x}-\bar{y}}
{\sqrt{\frac{s_x^2}{n_1}+\frac{s_y^2}{n_2}}}
\]

统计量的含义是：

> 观测到的两组均值差，相当于多少个“均值差标准误”。

当 \(|t|\) 较大时，样本均值差相对于随机误差更大，原假设更难解释当前数据。

---

## 11. Welch 自由度

Welch 检验使用近似自由度：

\[
\nu
=
\frac{
\left(\frac{s_x^2}{n_1}+\frac{s_y^2}{n_2}\right)^2
}
{
\frac{\left(s_x^2/n_1\right)^2}{n_1-1}
+
\frac{\left(s_y^2/n_2\right)^2}{n_2-1}
}
\]

这个自由度通常不是整数。

实际编程时一般不需要手工计算，SciPy 会自动完成。

---

## 12. 为什么优先使用 Welch 检验

传统独立双样本 t 检验可能假设两组总体方差相等。

但在金融数据中，两组收益的波动率经常不同，例如：

- 小市值股票波动率可能高于大市值股票
- 高换手策略波动率可能高于低换手策略
- 牛市样本与熊市样本的波动率可能明显不同
- 不同行业收益分布可能具有不同离散程度

Welch 检验：

- 不要求两组方差相等
- 可以处理两组样本量不相等
- 在方差确实相等时通常也不会产生严重效率损失

因此，在没有充分理由确信等方差时，实践中通常优先使用 Welch 检验。

SciPy 中应设置：

```python
stats.ttest_ind(x, y, equal_var=False)
```

---

## 13. 等方差 t 检验

若假设两个总体方差相等，可以先计算合并方差：

\[
s_p^2
=
\frac{(n_1-1)s_x^2+(n_2-1)s_y^2}
{n_1+n_2-2}
\]

均值差标准误为：

\[
SE_p
=s_p\sqrt{\frac{1}{n_1}+\frac{1}{n_2}}
\]

统计量为：

\[
t
=\frac{\bar{x}-\bar{y}}{SE_p}
\]

自由度为：

\[
df=n_1+n_2-2
\]

但如果真实方差不相等，特别是样本量也不相等时，等方差检验可能产生不可靠结果。

本课程默认建议：

> 独立样本均值比较优先使用 Welch t 检验。

---

## 14. 独立双样本检验的主要假设

### 假设一：组内观测具有合理独立性

每组中的观测不应存在强烈依赖。

金融时间序列常存在：

- 自相关
- 波动率聚集
- 同一市场因子驱动
- 同一股票重复出现

因此直接把每日收益当作完全独立样本，可能低估标准误。

### 假设二：两组样本相互独立

第一组观测不能与第二组观测存在未处理的配对关系。

若两组数据来自同一日期、同一股票或同一事件，往往应考虑配对结构。

### 假设三：均值与方差具有有限值

极端重尾分布会使小样本 t 检验不稳定。

### 假设四：小样本时分布不应严重偏离正态

当样本量较大时，中心极限定理通常能改善均值近似正态性。

但“样本量大”不能自动解决强依赖和结构性偏差。

---

# 四、配对 t 检验

## 15. 配对检验的核心思想

设每个研究对象都有两个观测值：

\[
(x_1,y_1),(x_2,y_2),\ldots,(x_n,y_n)
\]

定义每一对的差值：

\[
d_i=x_i-y_i
\]

配对 t 检验不是分别比较两组总体，而是研究差值总体的均值是否为 0。

令差值总体均值为：

\[
\mu_d
\]

原假设为：

\[
H_0:\mu_d=0
\]

备择假设为：

\[
H_1:\mu_d\neq0
\]

---

## 16. 配对 t 统计量

差值样本均值为：

\[
\bar{d}=\frac{1}{n}\sum_{i=1}^{n}d_i
\]

差值样本标准差为：

\[
s_d
=
\sqrt{
\frac{1}{n-1}
\sum_{i=1}^{n}(d_i-\bar{d})^2
}
\]

差值均值的标准误为：

\[
SE(\bar{d})=\frac{s_d}{\sqrt{n}}
\]

配对 t 统计量为：

\[
t=\frac{\bar{d}-0}{s_d/\sqrt{n}}
\]

即：

\[
t=\frac{\bar{d}}{s_d/\sqrt{n}}
\]

自由度为：

\[
df=n-1
\]

---

## 17. 配对检验与单样本检验的等价关系

配对 t 检验可以逐步转换为单样本 t 检验。

第一步，构造差值：

\[
d_i=x_i-y_i
\]

第二步，把差值视为一个新样本：

\[
d_1,d_2,\ldots,d_n
\]

第三步，检验差值总体均值：

\[
H_0:\mu_d=0
\]

第四步，对差值样本执行单样本 t 检验：

\[
t=\frac{\bar{d}}{s_d/\sqrt{n}}
\]

因此：

> 配对 t 检验本质上就是对“成对差值”做单样本 t 检验。

Python 中以下两种写法应得到相同或极接近的结果：

```python
stats.ttest_rel(x, y)
```

和：

```python
stats.ttest_1samp(x - y, popmean=0.0)
```

---

## 18. 配对检验为什么可能更有力

假设两个配对观测之间存在较强正相关。

差值的方差为：

\[
\operatorname{Var}(X-Y)
=\operatorname{Var}(X)+\operatorname{Var}(Y)-2\operatorname{Cov}(X,Y)
\]

如果：

\[
\operatorname{Cov}(X,Y)>0
\]

则：

\[
-2\operatorname{Cov}(X,Y)<0
\]

因此差值方差可能小于两个独立方差之和。

差值方差更小会使：

\[
SE(\bar{d})=\frac{s_d}{\sqrt{n}}
\]

更小。

在平均差相同的情况下，标准误更小会使 \(|t|\) 更大，从而提高发现真实差异的能力。

这就是配对设计能够控制个体差异、日期差异或股票差异的原因。

---

## 19. 量化研究中的配对示例

### 示例一：同日比较两个策略

同一批交易日上，记录策略 A 和策略 B 的日收益。

因为每个日期都同时对应两个策略收益，所以可以按日期配对。

差值为：

\[
d_t=r_{A,t}-r_{B,t}
\]

检验：

\[
H_0:E(d_t)=0
\]

### 示例二：事件前后比较

对每个事件，计算事件前收益和事件后收益。

每个事件形成一对观测。

差值为：

\[
d_i=r_{i,\text{after}}-r_{i,\text{before}}
\]

### 示例三：同一股票的新旧模型比较

对每只股票分别计算新模型和旧模型的预测误差。

每只股票构成一个配对单位。

---

# 五、效应大小与置信区间

## 20. 不能只看 p 值

假设某次检验得到：

\[
p=0.003
\]

这只能说明，在原假设成立时，当前结果较极端。

它不能直接说明：

- 差异是否足够大
- 差异是否能够覆盖交易成本
- 差异是否稳定
- 差异是否具有投资价值

因此，报告双样本检验时至少应包含：

- 第一组均值
- 第二组均值
- 均值差
- 均值差置信区间
- t 统计量
- 自由度
- p 值
- 效应大小
- 样本量

---

## 21. Welch 均值差置信区间

均值差估计为：

\[
\widehat{\Delta}=\bar{x}-\bar{y}
\]

标准误为：

\[
SE
=\sqrt{\frac{s_x^2}{n_1}+\frac{s_y^2}{n_2}}
\]

置信区间为：

\[
\widehat{\Delta}
\pm
t_{1-\alpha/2,\nu}\times SE
\]

其中 \(\nu\) 为 Welch 近似自由度。

如果 95% 置信区间不包含 0，则对应双侧显著性水平 5% 的检验通常会拒绝原假设。

---

## 22. Cohen's d

效应大小用于描述差异相对于数据波动的大小。

对于独立样本，一种常见定义为：

\[
d=\frac{\bar{x}-\bar{y}}{s_p}
\]

其中 \(s_p\) 是合并标准差。

对于配对样本，可以使用差值标准差：

\[
d_z=\frac{\bar{d}}{s_d}
\]

需要注意：

> 效应大小的经验阈值只能作为粗略参考，不能替代金融意义判断。

在量化研究中，更应关注：

- 均值差的绝对数值
- 年化后的经济意义
- 交易成本后的净差异
- 风险调整后的差异
- 样本外稳定性

---

# 六、第一类错误与第二类错误

## 23. 假设检验的四种结果

统计决策只有两种：

- 拒绝原假设
- 未拒绝原假设

真实世界也有两种状态：

- 原假设真实
- 原假设不真实

组合后产生四种情况。

| 真实状态 | 未拒绝原假设 | 拒绝原假设 |
|---|---|---|
| 原假设真实 | 正确决策 | 第一类错误 |
| 原假设不真实 | 第二类错误 | 正确发现 |

---

## 24. 第一类错误

第一类错误是：

> 原假设真实，但检验错误地拒绝了原假设。

记为：

\[
P(\text{拒绝 }H_0\mid H_0\text{ 为真})=\alpha
\]

例如，策略实际上没有超额收益，但研究结果错误地宣称策略有效。

在量化研究中，第一类错误对应：

- 假因子
- 假策略
- 假事件效应
- 假预测能力
- 随机波动被误认为市场规律

显著性水平 \(\alpha\) 控制的是检验程序的长期第一类错误率。

---

## 25. 第二类错误

第二类错误是：

> 原假设不真实，但检验没有拒绝原假设。

记为：

\[
P(\text{未拒绝 }H_0\mid H_0\text{ 不真实})=\beta
\]

例如，策略实际上具有正收益，但由于样本太少、波动太大，检验没有识别出来。

第二类错误对应“漏报”。

---

## 26. 检验功效

检验功效定义为：

\[
\text{Power}=1-\beta
\]

它表示：

> 当真实效应存在时，检验能够正确拒绝原假设的概率。

检验功效越高，发现真实效应的能力越强。

---

## 27. 影响检验功效的因素

### 样本量

样本量增加时，标准误通常下降。

以单样本均值为例：

\[
SE=\frac{s}{\sqrt{n}}
\]

当 \(n\) 增大时：

\[
\sqrt{n}\text{ 增大}
\]

所以：

\[
SE\text{ 减小}
\]

标准误减小会使同样的真实效应更容易被识别。

### 效应大小

真实均值差越大，t 统计量的绝对值通常越大，检验功效越高。

### 数据波动

标准差越大，标准误越大，真实效应越难被识别。

### 显著性水平

提高 \(\alpha\) 会扩大拒绝域，通常提高功效，但也会增加第一类错误风险。

降低 \(\alpha\) 会减少第一类错误，但通常降低功效。

### 检验方向

在方向事先明确且方向确实正确时，单侧检验可能具有更高功效。

但不能根据观察到的数据临时选择单侧方向。

---

## 28. 第一类错误与第二类错误的权衡

在样本量固定时，降低第一类错误通常会提高第二类错误。

例如，把显著性水平从：

\[
\alpha=0.05
\]

降低到：

\[
\alpha=0.01
\]

拒绝原假设会变得更困难。

结果是：

- 假发现减少
- 真实效应也更容易被漏掉

更好的解决方式通常不是只调整阈值，而是：

- 增加有效样本量
- 改进研究设计
- 降低噪声
- 使用合理配对
- 提高数据质量
- 预先定义假设
- 进行样本外验证

---

# 七、多重检验问题

## 29. 什么是多重检验

当研究者同时检验许多假设时，就发生了多重检验。

量化研究中非常常见：

- 同时测试 100 个技术指标
- 同时测试 50 个因子
- 同时测试多个持有期
- 同时测试多个参数组合
- 同时测试多个行业
- 同时测试多个事件窗口
- 同时测试多个股票池

每个检验单独使用 5% 显著性水平，并不意味着整个研究只承担 5% 的误报风险。

---

## 30. 预期假阳性数量

假设同时检验 \(m\) 个完全无效的假设，每个检验显著性水平为 \(\alpha\)。

单个检验产生假阳性的概率为：

\[
\alpha
\]

假阳性数量记为：

\[
V
\]

在简单条件下，假阳性数量的期望为：

\[
E(V)=m\alpha
\]

例如：

\[
m=100
\]

\[
\alpha=0.05
\]

则：

\[
E(V)=100\times0.05=5
\]

也就是说，即使 100 个策略全部无效，平均仍可能出现约 5 个“显著策略”。

---

## 31. 至少一次假阳性的概率

若各检验相互独立，单个检验不产生第一类错误的概率为：

\[
1-\alpha
\]

\(m\) 个检验都不产生第一类错误的概率为：

\[
(1-\alpha)^m
\]

因此，至少出现一次第一类错误的概率为：

\[
1-(1-\alpha)^m
\]

例如：

\[
\alpha=0.05
\]

\[
m=20
\]

代入：

\[
1-(1-0.05)^{20}
\]

\[
=1-0.95^{20}
\]

\[
\approx1-0.3585
\]

\[
\approx0.6415
\]

即至少出现一个假阳性的概率约为 64.15%。

这说明：

> “每个检验控制在 5%”并不等于“整个研究的误报概率是 5%”。

---

## 32. 家族错误率

家族错误率通常记为 FWER，表示在一组检验中至少出现一次第一类错误的概率。

\[
\operatorname{FWER}
=P(V\geq1)
\]

当检验数量增加时，未修正的 FWER 通常快速上升。

---

# 八、Bonferroni 修正

## 33. 基本思想

如果希望整个检验家族的错误率不超过 \(\alpha\)，可以把单个检验的阈值调整为：

\[
\alpha_{\text{single}}=\frac{\alpha}{m}
\]

其中：

- \(\alpha\) 是目标家族错误率
- \(m\) 是检验数量

例如，同时检验 20 个策略，希望整体错误率控制在 5%。

则每个检验的阈值为：

\[
\alpha_{\text{single}}
=\frac{0.05}{20}
\]

\[
=0.0025
\]

只有满足：

\[
p_i<0.0025
\]

的策略才被判定为显著。

---

## 34. Bonferroni 为什么能够控制 FWER

设第 \(i\) 个检验发生第一类错误的事件为：

\[
A_i
\]

至少发生一次第一类错误的事件为：

\[
A_1\cup A_2\cup\cdots\cup A_m
\]

根据并集上界：

\[
P(A_1\cup A_2\cup\cdots\cup A_m)
\leq
\sum_{i=1}^{m}P(A_i)
\]

如果每个检验使用：

\[
P(A_i)\leq\frac{\alpha}{m}
\]

则：

\[
\sum_{i=1}^{m}P(A_i)
\leq
\sum_{i=1}^{m}\frac{\alpha}{m}
\]

逐项相加：

\[
\sum_{i=1}^{m}\frac{\alpha}{m}
=m\times\frac{\alpha}{m}
\]

所以：

\[
m\times\frac{\alpha}{m}=\alpha
\]

因此：

\[
P(A_1\cup A_2\cup\cdots\cup A_m)
\leq\alpha
\]

即：

\[
\operatorname{FWER}\leq\alpha
\]

这个结论不要求各检验相互独立，因此 Bonferroni 方法非常稳健。

---

## 35. 调整 p 值

除了调整显著性阈值，也可以调整 p 值。

Bonferroni 调整后的 p 值为：

\[
p_i^{\text{adj}}=\min(mp_i,1)
\]

然后仍与原始显著性水平比较：

\[
p_i^{\text{adj}}<\alpha
\]

例如：

\[
p_i=0.003
\]

\[
m=10
\]

则：

\[
p_i^{\text{adj}}
=\min(10\times0.003,1)
\]

\[
=0.03
\]

因为：

\[
0.03<0.05
\]

所以修正后仍显著。

---

## 36. Bonferroni 的优点与缺点

优点：

- 简单
- 易于解释
- 不要求检验相互独立
- 能严格控制家族错误率

缺点：

- 检验数量较多时非常保守
- 可能显著降低检验功效
- 容易漏掉真实但较弱的效应

因此，Bonferroni 适合：

- 假发现代价很高
- 检验数量不太大
- 研究处于确认阶段
- 希望严格控制任何一次错误发现

后续因子研究阶段还会学习：

- Holm 方法
- Benjamini–Hochberg 方法
- 错误发现率
- 数据窥探偏差
- 样本外验证

---

# 九、量化研究中的多重检验陷阱

## 37. 参数搜索也是多重检验

假设测试以下参数：

- 5 种均线长度
- 4 种持有期
- 3 种止损阈值
- 4 个股票池

总组合数量为：

\[
5\times4\times3\times4=240
\]

即使最终只展示表现最好的一个策略，研究过程实际上已经进行了 240 次比较。

如果忽略这些失败尝试，最终策略的 p 值会显得过于乐观。

---

## 38. 数据窥探偏差

数据窥探偏差是指反复使用同一份数据：

- 发现规则
- 调整规则
- 重新检验
- 删除失败结果
- 保留最好结果

最终的“显著性”可能主要来自对历史噪声的拟合。

量化研究中必须记录：

- 测试过多少个假设
- 调整过多少组参数
- 删除过哪些版本
- 最终规则何时确定
- 样本外数据何时开始

---

## 39. 幸存者展示偏差

研究报告常只展示成功策略，而不展示失败策略。

例如，实际测试 100 个因子，只报告其中 3 个显著因子。

读者若只看到 3 个结果，会错误地把它们当成 3 次独立研究，而不是 100 次筛选后的幸存者。

正确做法包括：

- 报告总测试数量
- 进行多重检验修正
- 预先注册核心假设
- 保留完整实验日志
- 使用独立样本外数据
- 将探索性研究与确认性研究分开

---

# 十、Python 实践：双样本检验

## 40. 准备环境

```python
import numpy as np
from scipy import stats
```

---

## 41. 独立双样本 Welch t 检验

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(42)

strategy_a = rng.normal(loc=0.0012, scale=0.012, size=120)
strategy_b = rng.normal(loc=0.0003, scale=0.018, size=90)

result = stats.ttest_ind(
    strategy_a,
    strategy_b,
    equal_var=False,
    alternative="two-sided",
)

print("t statistic:", result.statistic)
print("p value:", result.pvalue)
```

关键参数：

- `equal_var=False`：使用 Welch t 检验
- `alternative="two-sided"`：双侧检验
- `alternative="greater"`：检验第一组均值是否更大
- `alternative="less"`：检验第一组均值是否更小

---

## 42. 手工计算 Welch t 统计量

```python
import numpy as np

x = strategy_a
y = strategy_b

n_x = x.size
n_y = y.size

mean_x = np.mean(x)
mean_y = np.mean(y)

var_x = np.var(x, ddof=1)
var_y = np.var(y, ddof=1)

standard_error = np.sqrt(var_x / n_x + var_y / n_y)

t_stat = (mean_x - mean_y) / standard_error

numerator = (var_x / n_x + var_y / n_y) ** 2

denominator = (
    (var_x / n_x) ** 2 / (n_x - 1)
    + (var_y / n_y) ** 2 / (n_y - 1)
)

df = numerator / denominator

p_value = 2 * stats.t.sf(np.abs(t_stat), df=df)

print("mean difference:", mean_x - mean_y)
print("standard error:", standard_error)
print("t statistic:", t_stat)
print("degrees of freedom:", df)
print("p value:", p_value)
```

---

## 43. Welch 均值差置信区间

```python
alpha = 0.05

critical_value = stats.t.ppf(1 - alpha / 2, df=df)
margin = critical_value * standard_error

mean_difference = mean_x - mean_y

ci_lower = mean_difference - margin
ci_upper = mean_difference + margin

print("95% CI:", (ci_lower, ci_upper))
```

---

## 44. 配对 t 检验

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(7)

market_component = rng.normal(loc=0.0002, scale=0.010, size=100)

strategy_old = market_component + rng.normal(
    loc=0.0001,
    scale=0.004,
    size=100,
)

strategy_new = market_component + rng.normal(
    loc=0.0007,
    scale=0.004,
    size=100,
)

paired_result = stats.ttest_rel(
    strategy_new,
    strategy_old,
    alternative="two-sided",
)

print("paired t statistic:", paired_result.statistic)
print("paired p value:", paired_result.pvalue)
```

这里两个策略共享同一个 `market_component`，代表同一交易日的市场环境。

按日期配对可以消除一部分共同市场波动。

---

## 45. 验证配对检验等价关系

```python
differences = strategy_new - strategy_old

one_sample_result = stats.ttest_1samp(
    differences,
    popmean=0.0,
    alternative="two-sided",
)

print("ttest_rel:", paired_result)
print("ttest_1samp on differences:", one_sample_result)
```

两个结果应相同或只存在浮点误差。

---

# 十一、编写可复用检验函数

## 46. 清洗一维数值数组

```python
import numpy as np


def clean_1d_array(values):
    array = np.asarray(values, dtype=float)

    if array.ndim != 1:
        raise ValueError("输入必须是一维数组")

    array = array[np.isfinite(array)]

    if array.size < 2:
        raise ValueError("有效样本量必须至少为 2")

    return array
```

---

## 47. Welch 检验函数

```python
import numpy as np
from scipy import stats


def welch_t_test(x, y, alpha=0.05, alternative="two-sided"):
    x = clean_1d_array(x)
    y = clean_1d_array(y)

    n_x = x.size
    n_y = y.size

    mean_x = np.mean(x)
    mean_y = np.mean(y)

    var_x = np.var(x, ddof=1)
    var_y = np.var(y, ddof=1)

    mean_difference = mean_x - mean_y
    standard_error = np.sqrt(var_x / n_x + var_y / n_y)

    if standard_error == 0:
        raise ValueError("标准误为 0，无法执行 t 检验")

    t_stat = mean_difference / standard_error

    numerator = (var_x / n_x + var_y / n_y) ** 2
    denominator = (
        (var_x / n_x) ** 2 / (n_x - 1)
        + (var_y / n_y) ** 2 / (n_y - 1)
    )
    df = numerator / denominator

    if alternative == "two-sided":
        p_value = 2 * stats.t.sf(np.abs(t_stat), df=df)
        critical_value = stats.t.ppf(1 - alpha / 2, df=df)
        ci_lower = mean_difference - critical_value * standard_error
        ci_upper = mean_difference + critical_value * standard_error
    elif alternative == "greater":
        p_value = stats.t.sf(t_stat, df=df)
        ci_lower = mean_difference - stats.t.ppf(1 - alpha, df=df) * standard_error
        ci_upper = np.inf
    elif alternative == "less":
        p_value = stats.t.cdf(t_stat, df=df)
        ci_lower = -np.inf
        ci_upper = mean_difference + stats.t.ppf(1 - alpha, df=df) * standard_error
    else:
        raise ValueError(
            "alternative 必须是 two-sided、greater 或 less"
        )

    pooled_variance = (
        (n_x - 1) * var_x + (n_y - 1) * var_y
    ) / (n_x + n_y - 2)

    pooled_standard_deviation = np.sqrt(pooled_variance)

    if pooled_standard_deviation == 0:
        cohen_d = np.nan
    else:
        cohen_d = mean_difference / pooled_standard_deviation

    return {
        "n_x": n_x,
        "n_y": n_y,
        "mean_x": mean_x,
        "mean_y": mean_y,
        "mean_difference": mean_difference,
        "standard_error": standard_error,
        "t_statistic": t_stat,
        "degrees_of_freedom": df,
        "p_value": p_value,
        "confidence_interval": (ci_lower, ci_upper),
        "cohen_d": cohen_d,
        "alpha": alpha,
        "alternative": alternative,
        "reject_null": bool(p_value < alpha),
    }
```

---

## 48. 配对检验函数

```python
import numpy as np
from scipy import stats


def paired_t_test(x, y, alpha=0.05, alternative="two-sided"):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("输入必须是一维数组")

    if x.size != y.size:
        raise ValueError("配对样本长度必须相同")

    valid_mask = np.isfinite(x) & np.isfinite(y)
    x = x[valid_mask]
    y = y[valid_mask]

    if x.size < 2:
        raise ValueError("有效配对数量必须至少为 2")

    differences = x - y

    result = stats.ttest_1samp(
        differences,
        popmean=0.0,
        alternative=alternative,
    )

    n = differences.size
    mean_difference = np.mean(differences)
    std_difference = np.std(differences, ddof=1)
    standard_error = std_difference / np.sqrt(n)
    df = n - 1

    if alternative == "two-sided":
        critical_value = stats.t.ppf(1 - alpha / 2, df=df)
        ci_lower = mean_difference - critical_value * standard_error
        ci_upper = mean_difference + critical_value * standard_error
    elif alternative == "greater":
        ci_lower = (
            mean_difference
            - stats.t.ppf(1 - alpha, df=df) * standard_error
        )
        ci_upper = np.inf
    elif alternative == "less":
        ci_lower = -np.inf
        ci_upper = (
            mean_difference
            + stats.t.ppf(1 - alpha, df=df) * standard_error
        )
    else:
        raise ValueError(
            "alternative 必须是 two-sided、greater 或 less"
        )

    if std_difference == 0:
        cohen_dz = np.nan
    else:
        cohen_dz = mean_difference / std_difference

    return {
        "n_pairs": n,
        "mean_difference": mean_difference,
        "std_difference": std_difference,
        "standard_error": standard_error,
        "t_statistic": float(result.statistic),
        "degrees_of_freedom": df,
        "p_value": float(result.pvalue),
        "confidence_interval": (ci_lower, ci_upper),
        "cohen_dz": cohen_dz,
        "alpha": alpha,
        "alternative": alternative,
        "reject_null": bool(result.pvalue < alpha),
    }
```

---

# 十二、Python 实践：多重检验演示

## 49. 手工实现 Bonferroni 修正

```python
import numpy as np


def bonferroni_correction(p_values, alpha=0.05):
    p_values = np.asarray(p_values, dtype=float)

    if p_values.ndim != 1:
        raise ValueError("p_values 必须是一维数组")

    if p_values.size == 0:
        raise ValueError("p_values 不能为空")

    if np.any(~np.isfinite(p_values)):
        raise ValueError("p_values 不能包含 NaN 或无穷值")

    if np.any((p_values < 0) | (p_values > 1)):
        raise ValueError("每个 p 值必须位于 0 和 1 之间")

    m = p_values.size
    adjusted_alpha = alpha / m
    adjusted_p_values = np.minimum(p_values * m, 1.0)

    return {
        "number_of_tests": m,
        "family_alpha": alpha,
        "adjusted_alpha": adjusted_alpha,
        "raw_p_values": p_values,
        "adjusted_p_values": adjusted_p_values,
        "reject_by_threshold": p_values < adjusted_alpha,
        "reject_by_adjusted_p": adjusted_p_values < alpha,
    }
```

---

## 50. 模拟全部无效策略

下面模拟 100 个实际上没有真实平均收益的策略。

每个策略都生成 60 个日收益，并执行单样本 t 检验。

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(2026)

number_of_strategies = 100
sample_size = 60
alpha = 0.05

p_values = []

for _ in range(number_of_strategies):
    returns = rng.normal(
        loc=0.0,
        scale=0.02,
        size=sample_size,
    )

    result = stats.ttest_1samp(
        returns,
        popmean=0.0,
        alternative="two-sided",
    )

    p_values.append(result.pvalue)

p_values = np.asarray(p_values)

raw_significant_count = np.sum(p_values < alpha)

bonferroni = bonferroni_correction(
    p_values,
    alpha=alpha,
)

bonferroni_significant_count = np.sum(
    bonferroni["reject_by_adjusted_p"]
)

print("raw significant count:", raw_significant_count)
print(
    "Bonferroni significant count:",
    bonferroni_significant_count,
)
print("adjusted alpha:", bonferroni["adjusted_alpha"])
```

在不同随机种子下，未经修正的显著策略数量会变化。

但长期平均约为：

\[
100\times0.05=5
\]

Bonferroni 修正后，假发现数量通常明显下降。

---

## 51. 重复模拟家族错误率

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(20260717)

number_of_experiments = 2000
number_of_tests = 20
sample_size = 40
alpha = 0.05

raw_family_errors = 0
bonferroni_family_errors = 0

for _ in range(number_of_experiments):
    experiment_p_values = []

    for _ in range(number_of_tests):
        sample = rng.normal(
            loc=0.0,
            scale=1.0,
            size=sample_size,
        )

        result = stats.ttest_1samp(
            sample,
            popmean=0.0,
        )

        experiment_p_values.append(result.pvalue)

    experiment_p_values = np.asarray(experiment_p_values)

    if np.any(experiment_p_values < alpha):
        raw_family_errors += 1

    adjusted_alpha = alpha / number_of_tests

    if np.any(experiment_p_values < adjusted_alpha):
        bonferroni_family_errors += 1

raw_fwer = raw_family_errors / number_of_experiments
bonferroni_fwer = (
    bonferroni_family_errors / number_of_experiments
)

theoretical_raw_fwer = 1 - (1 - alpha) ** number_of_tests

print("simulated raw FWER:", raw_fwer)
print("theoretical raw FWER:", theoretical_raw_fwer)
print("simulated Bonferroni FWER:", bonferroni_fwer)
```

预期现象：

- 未修正 FWER 接近 \(1-(1-\alpha)^m\)
- Bonferroni 修正后的 FWER 通常不超过目标 \(\alpha\)
- 模拟结果会因随机性存在小幅波动

---

# 十三、结果解释模板

## 52. 独立样本结果模板

可以按以下结构报告：

> 使用 Welch 独立双样本 t 检验比较策略 A 与策略 B 的平均日收益。策略 A 样本量为 120，策略 B 样本量为 90。两组平均收益差为 0.08 个百分点，95% 置信区间为某一区间。检验得到相应 t 统计量、近似自由度与 p 值。在 5% 显著性水平下，拒绝或未拒绝两组总体均值相等的原假设。除统计显著性外，还需结合交易成本、效应大小与样本外稳定性判断经济意义。

---

## 53. 配对样本结果模板

> 使用配对 t 检验比较同一批交易日上新策略与旧策略的收益。先计算每日收益差，再检验差值总体均值是否为 0。平均收益差、95% 置信区间、t 统计量与 p 值共同反映差异的不确定性。配对设计控制了同一交易日的共同市场波动，但仍需检查收益差序列的自相关和极端值。

---

## 54. 多重检验结果模板

> 本次研究同时检验 20 个假设。若每个检验直接使用 5% 阈值，整体至少出现一次假阳性的概率会明显高于 5%。因此使用 Bonferroni 修正，将单个检验阈值调整为 0.0025，或使用等价的调整后 p 值进行判断。修正后显著结果数量减少，说明部分原始显著性可能来自多重比较。

---

# 十四、常见错误

## 55. 把独立样本错误地当成配对样本

两组长度相同不等于存在配对关系。

错误配对会构造没有意义的差值，导致错误标准误。

---

## 56. 忽略真实配对结构

同一日期、同一股票、同一事件上的两组结果若直接当成独立样本，会丢失配对信息。

如果配对相关性较强，独立样本检验可能效率更低。

---

## 57. 默认使用等方差检验

金融收益的波动率经常不相等。

没有充分依据时，应优先使用：

```python
stats.ttest_ind(x, y, equal_var=False)
```

---

## 58. 只报告 p 值

只写“p 小于 0.05”无法说明差异大小与投资意义。

至少应报告：

- 样本量
- 两组均值
- 均值差
- 置信区间
- 效应大小
- p 值

---

## 59. 把未拒绝原假设写成两组完全相同

未拒绝原假设只能说明证据不足。

它可能来自：

- 真实差异很小
- 样本量不足
- 波动率太高
- 检验功效太低
- 数据质量较差

不能写成“证明两组没有差异”。

---

## 60. 只修正最后展示的结果

多重检验的数量应包括研究过程中真实尝试过的假设，而不是只包括最后保留下来的结果。

---

## 61. 看到结果后才决定单侧检验

先看到策略 A 均值更高，再把双侧检验改为右侧检验，会人为降低 p 值。

检验方向必须在查看结果前确定。

---

## 62. 忽略时间序列依赖

经典 t 检验假设有效独立样本。

金融收益可能存在：

- 自相关
- 波动率聚集
- 横截面相关
- 重叠持有期

这些问题会影响标准误。

当前阶段先掌握经典检验框架；后续将学习稳健标准误、区块抽样和时间序列方法。

---

# 十五、今日练习

## 63. 概念练习

### 练习 1

比较两组不同股票的未来 20 日收益，应优先考虑独立检验还是配对检验？

### 练习 2

比较同一批股票在公告前后 5 日的收益，应优先考虑哪种检验？

### 练习 3

第一类错误在因子研究中代表什么？

### 练习 4

第二类错误在策略研究中代表什么？

### 练习 5

同时检验 100 个完全无效策略，每个检验使用 5% 阈值，预期会出现多少个假阳性？

### 练习 6

同时检验 25 个假设，希望家族错误率控制在 5%，Bonferroni 阈值是多少？

---

## 64. 计算练习

已知两组独立样本：

第一组：

\[
n_1=50
\]

\[
\bar{x}=0.012
\]

\[
s_x=0.020
\]

第二组：

\[
n_2=40
\]

\[
\bar{y}=0.006
\]

\[
s_y=0.018
\]

完成以下计算：

1. 均值差
2. Welch 标准误
3. t 统计量
4. 判断差异相对于标准误有多大

---

## 65. 编程练习

### 练习 A

生成两组方差不同、样本量不同的随机收益数据，分别执行：

- 等方差 t 检验
- Welch t 检验

比较两者的统计量、自由度和 p 值。

### 练习 B

生成一组共同市场收益，再在其上构造两个策略收益。

分别执行：

- 独立双样本检验
- 配对 t 检验

解释为什么结果可能不同。

### 练习 C

模拟 200 个无效策略，统计未经修正和 Bonferroni 修正后的显著策略数量。

### 练习 D

把 `welch_t_test` 和 `paired_t_test` 函数保存到本周练习代码中，并分别测试：

- 正常输入
- 包含 NaN 的输入
- 样本量不足
- 配对长度不一致
- 零方差数据

---

# 十六、练习参考答案

## 66. 概念练习答案

### 练习 1

如果两组由不同股票组成，且不存在一一对应关系，应优先考虑独立双样本检验。

### 练习 2

同一批股票的公告前后收益具有自然配对关系，应优先考虑配对 t 检验。

### 练习 3

第一类错误代表因子实际上无效，但研究错误地认为因子显著有效。

### 练习 4

第二类错误代表策略实际上有效，但由于样本不足或噪声过大，研究未能识别出真实效应。

### 练习 5

\[
E(V)=m\alpha
\]

代入：

\[
E(V)=100\times0.05
\]

所以：

\[
E(V)=5
\]

预期约有 5 个假阳性。

### 练习 6

\[
\alpha_{\text{single}}=\frac{0.05}{25}
\]

逐步计算：

\[
\frac{0.05}{25}=0.002
\]

因此单个检验阈值为：

\[
0.002
\]

---

## 67. 计算练习答案

第一步，均值差：

\[
\bar{x}-\bar{y}=0.012-0.006
\]

\[
=0.006
\]

第二步，计算第一组均值方差项：

\[
\frac{s_x^2}{n_1}
=\frac{0.020^2}{50}
\]

\[
=\frac{0.0004}{50}
\]

\[
=0.000008
\]

第三步，计算第二组均值方差项：

\[
\frac{s_y^2}{n_2}
=\frac{0.018^2}{40}
\]

\[
=\frac{0.000324}{40}
\]

\[
=0.0000081
\]

第四步，两项相加：

\[
0.000008+0.0000081=0.0000161
\]

第五步，开平方得到标准误：

\[
SE=\sqrt{0.0000161}
\]

\[
SE\approx0.004012
\]

第六步，计算 t 统计量：

\[
t=\frac{0.006}{0.004012}
\]

\[
t\approx1.495
\]

解释：

> 观测到的均值差约为 1.5 个标准误，证据通常还不足以在常用双侧 5% 水平下拒绝均值相等的原假设。

正式结论仍应使用 Welch 自由度计算精确 p 值。

---

# 十七、今日输出任务

## 68. 必须完成的输出

今天完成以下三个输出：

1. 一个 `welch_t_test` 函数
2. 一个 `paired_t_test` 函数
3. 一个多重检验模拟程序

多重检验程序至少输出：

- 检验数量
- 原始显著结果数量
- Bonferroni 阈值
- 修正后显著结果数量
- 未修正 FWER 模拟值
- Bonferroni 修正后 FWER 模拟值

---

## 69. 建议的研究记录

在笔记中回答：

1. 独立检验与配对检验的判断依据是什么？
2. 为什么独立样本通常优先使用 Welch 检验？
3. 第一类错误和第二类错误分别是什么？
4. 检验功效由哪些因素影响？
5. 为什么测试 100 个策略会产生假显著结果？
6. Bonferroni 修正控制的是什么错误率？
7. 为什么统计显著不等于经济显著？
8. 你的量化研究将如何记录所有测试过的策略？

---

# 十八、今日检查清单

完成学习后逐项检查：

- [ ] 能区分独立样本和配对样本
- [ ] 能写出双样本均值检验的原假设与备择假设
- [ ] 能解释 Welch t 统计量
- [ ] 知道 `equal_var=False` 的含义
- [ ] 能解释配对检验为什么等价于差值的单样本检验
- [ ] 能区分第一类错误和第二类错误
- [ ] 能解释检验功效 \(1-\beta\)
- [ ] 能计算预期假阳性数量 \(m\alpha\)
- [ ] 能计算至少一次假阳性的概率
- [ ] 能计算 Bonferroni 阈值 \(\alpha/m\)
- [ ] 能手工调整 p 值
- [ ] 能同时报告效应大小、置信区间和 p 值
- [ ] 能运行多重检验模拟
- [ ] 能说明量化参数搜索为什么属于多重检验

---

# 十九、今日核心结论

1. 两组均值比较前，必须先判断两组数据是独立样本还是配对样本。
2. 独立样本在方差可能不等时，应优先使用 Welch t 检验。
3. 配对 t 检验本质上是对成对差值执行单样本 t 检验。
4. 第一类错误是假发现，概率由 \(\alpha\) 控制。
5. 第二类错误是漏掉真实效应，检验功效等于 \(1-\beta\)。
6. 样本量更大、效应更强、噪声更小，通常能提高检验功效。
7. 同时检验多个假设会显著提高至少出现一次假阳性的概率。
8. Bonferroni 修正通过使用 \(\alpha/m\) 控制家族错误率。
9. 多重检验修正不能替代预先定义假设、完整实验记录和样本外验证。
10. 量化研究不能只报告 p 值，还必须报告效应大小、置信区间和经济意义。

---

## 70. 明日预告

第八周第七天将完成本周综合项目：

> 简单事件研究。

将学习：

- 事件日与事件窗口
- 估计窗口
- 正常收益与异常收益
- 累计异常收益
- 事件样本对齐
- 异常收益显著性检验
- 多事件与多窗口的检验风险
- 简单事件研究报告结构
