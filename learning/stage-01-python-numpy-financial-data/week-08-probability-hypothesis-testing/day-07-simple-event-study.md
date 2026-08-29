# 第八周 · 第七天

## 简单事件研究：异常收益、累计异常收益与显著性检验

---

## 1. 今日学习目标

完成今天的学习后，你需要能够：

- 解释事件研究要回答的核心问题
- 区分事件日、估计窗口、间隔窗口和事件窗口
- 正确处理盘中公告、盘后公告和非交易日公告的日期对齐
- 理解正常收益、异常收益和累计异常收益
- 掌握市场调整模型和市场模型
- 计算单只股票的异常收益 \(AR_t\) 与累计异常收益 \(CAR\)
- 计算多个事件的平均异常收益 \(AAR_\tau\) 与累计平均异常收益 \(CAAR\)
- 为事件研究写出原假设和备择假设
- 对单日异常收益和事件窗累计异常收益进行显著性检验
- 同时报告效应大小、置信区间和 p 值
- 识别事件时间错位、前视偏差、混杂事件和多重检验问题
- 使用 pandas、NumPy 和 SciPy 完成一个可复用的简单事件研究
- 输出一份结构完整的事件研究报告

---

## 2. 今日学习顺序

建议学习时间：约 150—190 分钟。

| 阶段 | 内容 | 建议时间 |
|---|---|---:|
| 1 | 理解事件研究问题 | 15 分钟 |
| 2 | 定义事件日与研究窗口 | 25 分钟 |
| 3 | 正常收益与异常收益 | 30 分钟 |
| 4 | CAR、AAR 与 CAAR | 25 分钟 |
| 5 | 显著性检验 | 30 分钟 |
| 6 | Python 实践 | 45 分钟 |
| 7 | 报告、练习与复盘 | 20 分钟 |

---

# 一、事件研究在研究什么

## 3. 核心问题

事件研究用于回答：

> 某个明确事件发生后，证券价格是否出现了超过正常市场波动的收益变化？

常见事件包括：

- 上市公司发布业绩预告
- 年报或季报披露
- 分红方案公告
- 股票回购公告
- 并购重组公告
- 监管处罚公告
- 高管增减持公告
- 指数成分股调整
- 政策发布
- 行业重大新闻

事件研究不是简单比较“事件后股价涨没涨”。

因为股票上涨可能只是市场整体上涨，股票下跌也可能只是市场整体下跌。

真正需要衡量的是：

\[
\text{异常收益}
=
\text{实际收益}
-
\text{正常情况下应有的收益}
\]

---

## 4. 一个直观例子

假设某股票在公告日上涨 \(3\%\)，同期市场上涨 \(2.2\%\)。

若使用最简单的市场调整模型，则异常收益为：

\[
AR_0
=
3\%-2.2\%
\]

\[
AR_0
=
0.8\%
\]

这里的 \(0.8\%\) 才是相对于市场基准的额外表现。

如果只报告股票上涨 \(3\%\)，会把市场整体上涨误认为事件效应。

---

## 5. 事件研究的逻辑链条

完整事件研究可以写成：

\[
\text{定义事件}
\rightarrow
\text{确定事件日}
\rightarrow
\text{确定窗口}
\rightarrow
\text{估计正常收益}
\rightarrow
\text{计算异常收益}
\rightarrow
\text{聚合}
\rightarrow
\text{显著性检验}
\rightarrow
\text{经济解释}
\]

任何一步定义不清，最终结论都可能失真。

---

# 二、事件日与窗口设计

## 6. 事件时间

事件研究通常不直接使用自然日期差，而是使用相对于事件日的交易日编号。

令事件日为：

\[
\tau=0
\]

事件日前一个交易日为：

\[
\tau=-1
\]

事件后一个交易日为：

\[
\tau=1
\]

因此事件窗口 \([-2,2]\) 表示：

- 事件前 2 个交易日
- 事件日
- 事件后 2 个交易日

总共包含 5 个交易日。

---

## 7. 四个关键日期区间

### 7.1 估计窗口

估计窗口用于估计股票在“正常情况下”与市场之间的关系。

例如：

\[
[-120,-21]
\]

表示使用事件日前第 120 个交易日到第 21 个交易日的数据估计正常收益模型。

### 7.2 间隔窗口

估计窗口和事件窗口之间通常留出一段间隔。

例如：

\[
[-20,-6]
\]

这段间隔可以减少事件信息提前泄露对正常收益模型的污染。

### 7.3 事件窗口

事件窗口用于测量事件影响。

例如：

\[
[-1,1]
\]

或者：

\[
[-3,3]
\]

### 7.4 事后窗口

如果研究事件影响是否持续，可以继续观察：

\[
[2,20]
\]

但窗口越长，混杂事件越多，因果解释越弱。

---

## 8. 为什么估计窗口不能与事件窗口重叠

若使用事件期数据估计正常收益模型，那么事件造成的异常波动会被模型当作“正常关系”。

结果会使异常收益被低估。

因此通常要求：

\[
\text{估计窗口结束日}
<
\text{事件窗口开始日}
\]

并在两者之间保留若干交易日的间隔。

---

## 9. 事件日对齐规则

公告日期不能机械地直接作为 \(\tau=0\)。

必须先判断信息何时能够被市场交易。

### 盘中公告

若公告在交易时段发布，公告当天可能已经包含价格反应。

通常可将公告当日作为事件日。

### 收盘后公告

若公告在收盘后发布，市场首次完整反应通常发生在下一交易日。

因此应将下一交易日设为：

\[
\tau=0
\]

### 周末或节假日公告

若公告发生在非交易日，应将下一个交易日设为事件日。

### 日期对齐原则

> 事件日应代表市场第一次可以充分交易该信息的交易日，而不是公告文件上的自然日期。

---

## 10. 信息泄露与延迟反应

如果市场在公告前已经出现异常收益，可能存在：

- 信息提前泄露
- 市场预期
- 媒体预热
- 相关公告提前披露
- 研究者事件日对齐错误

如果事件后多日仍持续出现异常收益，可能表示：

- 市场反应不足
- 信息逐步消化
- 流动性限制
- 后续新闻继续释放
- 事件窗口内存在其他信息

事件研究只能描述价格路径，不能自动证明具体机制。

---

# 三、收益率口径

## 11. 简单收益率

简单收益率定义为：

\[
R_t
=
\frac{P_t-P_{t-1}}{P_{t-1}}
\]

也可以写为：

\[
R_t
=
\frac{P_t}{P_{t-1}}-1
\]

---

## 12. 对数收益率

对数收益率定义为：

\[
r_t
=
\ln\left(\frac{P_t}{P_{t-1}}\right)
\]

较短事件窗口中，简单收益率和对数收益率通常数值接近。

但在一个研究中必须保持口径一致：

- 股票收益率与市场收益率使用相同口径
- 估计窗口与事件窗口使用相同口径
- 不要混合前复权、后复权和不复权价格

---

## 13. 复权价格的重要性

公司分红、送股、拆股等行为会造成原始价格跳变。

若直接使用不复权收盘价，可能把公司行为造成的机械价格变化误认为事件异常收益。

因此，在日频事件研究中通常应使用一致口径的复权价格。

但如果研究对象本身就是分红或拆股事件，则需要明确：

- 研究的是价格反应
- 还是股东总回报
- 是否已经将现金分红计入收益

---

# 四、正常收益模型

## 14. 正常收益

正常收益表示：

> 如果事件没有发生，股票在该交易日原本应取得的收益。

正常收益无法被直接观察，只能通过模型估计。

记股票 \(i\) 在事件时间 \(\tau\) 的实际收益为：

\[
R_{i,\tau}
\]

正常收益为：

\[
E(R_{i,\tau}\mid \mathcal{I})
\]

其中 \(\mathcal{I}\) 表示估计正常收益时使用的信息集合。

异常收益定义为：

\[
AR_{i,\tau}
=
R_{i,\tau}
-
E(R_{i,\tau}\mid \mathcal{I})
\]

---

## 15. 模型一：均值调整模型

最简单的正常收益模型是用估计窗口平均收益作为正常收益。

先计算股票 \(i\) 在估计窗口的平均收益：

\[
\bar{R}_i
=
\frac{1}{T}
\sum_{t=1}^{T}R_{i,t}
\]

事件期异常收益为：

\[
AR_{i,\tau}
=
R_{i,\tau}-\bar{R}_i
\]

优点：

- 容易理解
- 容易实现
- 不需要市场指数

缺点：

- 没有控制市场整体涨跌
- 在系统性行情较强时容易误判

---

## 16. 模型二：市场调整模型

市场调整模型假设股票的正常收益等于市场收益。

\[
E(R_{i,\tau}\mid \mathcal{I})
=
R_{m,\tau}
\]

因此：

\[
AR_{i,\tau}
=
R_{i,\tau}-R_{m,\tau}
\]

其中 \(R_{m,\tau}\) 是市场基准收益。

优点：

- 计算简单
- 控制了市场共同波动
- 不需要估计回归参数

缺点：

- 隐含股票市场敏感度等于 1
- 忽略股票自身的长期平均超额收益
- 对高贝塔或低贝塔股票可能不够准确

本周的“简单事件研究”可以先使用该模型完成完整流程。

---

## 17. 模型三：市场模型

市场模型使用估计窗口回归股票收益与市场收益的关系：

\[
R_{i,t}
=
\alpha_i+\beta_i R_{m,t}+\varepsilon_{i,t}
\]

通过估计窗口得到：

\[
\hat{\alpha}_i
\]

和：

\[
\hat{\beta}_i
\]

事件期正常收益为：

\[
\widehat{R}_{i,\tau}
=
\hat{\alpha}_i+\hat{\beta}_iR_{m,\tau}
\]

异常收益为：

\[
AR_{i,\tau}
=
R_{i,\tau}
-
\left(
\hat{\alpha}_i+\hat{\beta}_iR_{m,\tau}
\right)
\]

优点：

- 控制了市场波动
- 允许不同股票具有不同市场敏感度
- 比市场调整模型更灵活

缺点：

- 需要足够长的估计窗口
- 回归关系可能不稳定
- 极端行情下参数可能失真

---

## 18. 市场模型参数的含义

### 截距

\[
\alpha_i
\]

表示在市场收益为 0 时，股票的平均收益部分。

### 市场敏感度

\[
\beta_i
\]

表示市场收益变化 \(1\) 个单位时，股票收益平均变化多少单位。

例如：

\[
\hat{\beta}_i=1.3
\]

表示市场上涨 \(1\%\) 时，该股票正常情况下平均上涨约 \(1.3\%\)，其他条件不变。

---

## 19. 如何选择基准

市场基准应与研究对象尽量匹配。

例如：

- 全市场股票可使用宽基指数
- 沪深 300 成分股可使用沪深 300
- 中小盘股票可使用中证 500 或中证 1000
- 行业事件可考虑行业指数
- 个股研究可同时报告宽基基准和行业基准的稳健性结果

基准选择会影响异常收益。

因此报告中必须写明：

- 基准名称
- 基准代码
- 收益率口径
- 日期范围
- 数据来源

---

# 五、异常收益与累计异常收益

## 20. 单日异常收益

股票 \(i\) 在事件时间 \(\tau\) 的异常收益为：

\[
AR_{i,\tau}
=
R_{i,\tau}
-
\widehat{R}_{i,\tau}
\]

若使用市场调整模型：

\[
AR_{i,\tau}
=
R_{i,\tau}-R_{m,\tau}
\]

---

## 21. 单个事件的累计异常收益

对于事件窗口 \([\tau_1,\tau_2]\)，累计异常收益定义为：

\[
CAR_i(\tau_1,\tau_2)
=
\sum_{\tau=\tau_1}^{\tau_2}
AR_{i,\tau}
\]

例如：

\[
CAR_i(-1,1)
=
AR_{i,-1}
+
AR_{i,0}
+
AR_{i,1}
\]

---

## 22. 手工计算例子

假设事件窗口 \([-1,1]\) 中：

\[
AR_{-1}=0.004
\]

\[
AR_0=0.018
\]

\[
AR_1=-0.003
\]

则：

\[
CAR(-1,1)
=
0.004+0.018-0.003
\]

\[
CAR(-1,1)
=
0.019
\]

即：

\[
CAR(-1,1)=1.9\%
\]

这表示事件窗口内累计取得约 \(1.9\%\) 的异常收益。

---

## 23. 为什么使用累计异常收益

事件影响不一定集中在单日。

可能出现：

- 事件前提前反应
- 公告日部分反应
- 次日继续反应
- 多日逐步消化

因此 \(CAR\) 可以衡量一个完整事件窗口的总效应。

但窗口越长，其他信息进入窗口的概率越高。

---

# 六、多个事件的聚合

## 24. 为什么需要多个事件

只研究一个事件时，可以描述该股票的价格反应，但统计推断能力很弱。

为了判断某一类事件是否具有稳定影响，通常需要收集多个同类事件。

例如：

- 50 次股票回购公告
- 80 次业绩预增公告
- 40 次监管处罚公告

---

## 25. 平均异常收益

若共有 \(N\) 个事件，在事件时间 \(\tau\) 的平均异常收益为：

\[
AAR_\tau
=
\frac{1}{N}
\sum_{i=1}^{N}
AR_{i,\tau}
\]

\(AAR_\tau\) 描述所有事件在某个相对交易日的平均异常表现。

---

## 26. 累计平均异常收益

累计平均异常收益定义为：

\[
CAAR(\tau_1,\tau_2)
=
\sum_{\tau=\tau_1}^{\tau_2}
AAR_\tau
\]

也可以先计算每个事件的 \(CAR_i\)，再求平均：

\[
CAAR(\tau_1,\tau_2)
=
\frac{1}{N}
\sum_{i=1}^{N}
CAR_i(\tau_1,\tau_2)
\]

在没有缺失值且所有事件窗口一致时，两种计算方式相等。

逐行推导如下。

第一步：

\[
CAAR(\tau_1,\tau_2)
=
\sum_{\tau=\tau_1}^{\tau_2}
AAR_\tau
\]

第二步，代入 \(AAR_\tau\)：

\[
CAAR(\tau_1,\tau_2)
=
\sum_{\tau=\tau_1}^{\tau_2}
\left(
\frac{1}{N}
\sum_{i=1}^{N}
AR_{i,\tau}
\right)
\]

第三步，将常数 \(\frac{1}{N}\) 提出：

\[
CAAR(\tau_1,\tau_2)
=
\frac{1}{N}
\sum_{\tau=\tau_1}^{\tau_2}
\sum_{i=1}^{N}
AR_{i,\tau}
\]

第四步，交换求和顺序：

\[
CAAR(\tau_1,\tau_2)
=
\frac{1}{N}
\sum_{i=1}^{N}
\sum_{\tau=\tau_1}^{\tau_2}
AR_{i,\tau}
\]

第五步，内部求和就是 \(CAR_i\)：

\[
CAAR(\tau_1,\tau_2)
=
\frac{1}{N}
\sum_{i=1}^{N}
CAR_i(\tau_1,\tau_2)
\]

---

# 七、事件研究中的假设检验

## 27. 检验单日平均异常收益

研究某个事件时间 \(\tau\) 的平均异常收益是否为 0。

原假设：

\[
H_0:
\mu_{AR,\tau}=0
\]

双侧备择假设：

\[
H_1:
\mu_{AR,\tau}\neq0
\]

如果研究者在看数据前就提出“事件产生正向影响”，可以使用右侧备择假设：

\[
H_1:
\mu_{AR,\tau}>0
\]

检验方向必须在查看结果前确定。

---

## 28. 单日横截面 t 检验

在事件时间 \(\tau\)，共有 \(N\) 个异常收益：

\[
AR_{1,\tau},
AR_{2,\tau},
\ldots,
AR_{N,\tau}
\]

其样本均值为：

\[
AAR_\tau
=
\frac{1}{N}
\sum_{i=1}^{N}
AR_{i,\tau}
\]

样本标准差为：

\[
s_{AR,\tau}
=
\sqrt{
\frac{
\sum_{i=1}^{N}
\left(
AR_{i,\tau}-AAR_\tau
\right)^2
}{
N-1
}
}
\]

均值标准误为：

\[
SE(AAR_\tau)
=
\frac{s_{AR,\tau}}{\sqrt{N}}
\]

t 统计量为：

\[
t_\tau
=
\frac{AAR_\tau-0}
{SE(AAR_\tau)}
\]

即：

\[
t_\tau
=
\frac{AAR_\tau}
{s_{AR,\tau}/\sqrt{N}}
\]

---

## 29. 检验事件窗累计异常收益

对于每个事件，先计算：

\[
CAR_i(\tau_1,\tau_2)
\]

然后检验所有事件的平均 \(CAR\) 是否为 0。

原假设：

\[
H_0:
\mu_{CAR}=0
\]

备择假设：

\[
H_1:
\mu_{CAR}\neq0
\]

样本平均值：

\[
\overline{CAR}
=
\frac{1}{N}
\sum_{i=1}^{N}
CAR_i
\]

样本标准差：

\[
s_{CAR}
=
\sqrt{
\frac{
\sum_{i=1}^{N}
\left(
CAR_i-\overline{CAR}
\right)^2
}{
N-1
}
}
\]

标准误：

\[
SE(\overline{CAR})
=
\frac{s_{CAR}}{\sqrt{N}}
\]

t 统计量：

\[
t
=
\frac{\overline{CAR}}
{s_{CAR}/\sqrt{N}}
\]

---

## 30. 置信区间

对于平均累计异常收益，可以构造置信区间。

\[
\overline{CAR}
\pm
t_{1-\alpha/2,N-1}
\frac{s_{CAR}}{\sqrt{N}}
\]

例如 \(95\%\) 置信区间对应：

\[
\alpha=0.05
\]

若置信区间不包含 0，则与双侧 \(5\%\) 显著性检验拒绝原假设相对应。

---

## 31. 效应大小与统计显著性

事件研究不能只报告 p 值。

至少同时报告：

- 事件数量
- 平均异常收益
- 平均累计异常收益
- 标准差
- 标准误
- 置信区间
- t 统计量
- p 值
- 正异常收益事件占比
- 中位数异常收益

例如：

> 样本包含 60 个事件，事件窗 \([-1,1]\) 的平均累计异常收益为 \(1.2\%\)，\(95\%\) 置信区间为 \([0.4\%,2.0\%]\)，双侧 p 值为 0.004。

这比只写“结果显著”更完整。

---

# 八、显著性检验的适用条件

## 32. 独立性

经典单样本 t 检验默认事件之间近似独立。

但现实中可能存在：

- 多家公司在同一天发布同类公告
- 同一行业事件高度集中
- 同一只股票重复出现多个事件
- 多个事件共同受市场冲击
- 事件窗口相互重叠

这些情况会造成横截面相关，使普通标准误偏小。

本周先掌握经典方法，但报告中必须说明该限制。

---

## 33. 分布与异常值

t 检验对样本均值进行推断。

当样本量较大时，中心极限定理能够提供一定支持。

但金融异常收益常具有：

- 厚尾
- 偏度
- 极端值
- 波动率差异

因此建议同时检查：

- 直方图
- 箱线图
- 分位数
- 中位数
- 截尾前后结果
- 非参数检验结果

---

## 34. 单个事件不能稳定代表一类事件

一个事件得到：

\[
CAR=5\%
\]

并不表示这种事件通常会产生 \(5\%\) 的异常收益。

它可能来自：

- 事件本身
- 市场噪声
- 同期其他公告
- 行业新闻
- 流动性冲击
- 数据错误

单事件研究更适合案例描述。

多事件样本更适合统计推断。

---

# 九、多重检验问题

## 35. 为什么事件研究容易产生多重检验

研究者可能同时测试：

- \([-1,1]\)
- \([-2,2]\)
- \([-5,5]\)
- \([0,1]\)
- \([0,3]\)
- \([0,5]\)

也可能逐日检验：

\[
\tau=-10,-9,\ldots,10
\]

如果最后只展示最显著的窗口，会产生选择偏差。

---

## 36. 预先定义主窗口

建议在研究前定义一个主事件窗口，例如：

\[
[-1,1]
\]

其他窗口作为稳健性检验。

报告中应区分：

- 主检验
- 补充检验
- 探索性检验

---

## 37. Bonferroni 修正

若同时检验 \(m\) 个假设，并希望家族错误率控制在 \(\alpha\)，可以使用：

\[
\alpha_{\text{single}}
=
\frac{\alpha}{m}
\]

例如同时检验 5 个窗口：

\[
\alpha_{\text{single}}
=
\frac{0.05}{5}
\]

\[
\alpha_{\text{single}}
=
0.01
\]

Bonferroni 修正较保守，但易于理解。

---

# 十、简单事件研究的完整设计

## 38. 研究问题示例

研究问题：

> 某类正面公告是否在公告附近产生正的异常收益？

### 样本

收集 \(N\) 个符合条件的事件。

### 主事件窗口

\[
[-1,1]
\]

### 估计窗口

\[
[-120,-21]
\]

### 正常收益模型

市场模型：

\[
R_{i,t}
=
\alpha_i+\beta_iR_{m,t}+\varepsilon_{i,t}
\]

### 主检验

\[
H_0:
E\left[
CAR_i(-1,1)
\right]=0
\]

\[
H_1:
E\left[
CAR_i(-1,1)
\right]>0
\]

### 补充窗口

\[
[-3,3]
\]

和：

\[
[0,2]
\]

补充窗口应明确标记为稳健性分析。

---

## 39. 数据表结构

建议准备两张表。

### 行情表

| 字段 | 含义 |
|---|---|
| symbol | 股票代码 |
| trade_date | 交易日期 |
| close_adj | 复权收盘价 |
| stock_return | 股票收益率 |
| market_return | 市场收益率 |

### 事件表

| 字段 | 含义 |
|---|---|
| event_id | 事件唯一编号 |
| symbol | 股票代码 |
| announce_time | 公告时间 |
| event_date | 对齐后的事件交易日 |
| event_type | 事件类型 |
| source | 事件来源 |

---

## 40. 数据质量检查

事件研究前至少检查：

- 股票代码是否唯一、格式是否统一
- 日期是否为交易日
- 每个事件是否有足够长估计窗口
- 每个事件是否有完整事件窗口
- 股票收益率和市场收益率是否同日对齐
- 是否存在重复事件
- 同一股票的多个事件窗口是否重叠
- 是否存在停牌
- 是否存在涨跌停导致的延迟反应
- 复权口径是否一致
- 是否存在极端错误价格
- 公告时间是否用于确定事件日

---

# 十一、Python 实践：从模拟数据完成完整事件研究

## 41. 导入库

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import stats
```

---

## 42. 结果结构

```python
@dataclass
class TestResult:
    n: int
    mean: float
    std: float
    se: float
    t_stat: float
    p_value: float
    ci_low: float
    ci_high: float
```

---

## 43. 单样本均值检验函数

```python
def one_sample_mean_test(
    values: Iterable[float],
    null_mean: float = 0.0,
    confidence: float = 0.95,
    alternative: str = "two-sided",
) -> TestResult:
    x = np.asarray(list(values), dtype=float)
    x = x[np.isfinite(x)]

    if x.size < 2:
        raise ValueError("有效样本量至少为 2。")

    if alternative not in {"two-sided", "greater", "less"}:
        raise ValueError(
            "alternative 必须是 two-sided、greater 或 less。"
        )

    n = int(x.size)
    mean = float(np.mean(x))
    std = float(np.std(x, ddof=1))
    se = std / np.sqrt(n)

    if se == 0:
        raise ValueError("样本标准误为 0，无法执行 t 检验。")

    t_stat = (mean - null_mean) / se
    df = n - 1

    if alternative == "two-sided":
        p_value = 2.0 * stats.t.sf(abs(t_stat), df=df)
    elif alternative == "greater":
        p_value = stats.t.sf(t_stat, df=df)
    else:
        p_value = stats.t.cdf(t_stat, df=df)

    alpha = 1.0 - confidence
    critical = stats.t.ppf(1.0 - alpha / 2.0, df=df)

    ci_low = mean - critical * se
    ci_high = mean + critical * se

    return TestResult(
        n=n,
        mean=mean,
        std=std,
        se=float(se),
        t_stat=float(t_stat),
        p_value=float(p_value),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
    )
```

注意：

- 单侧检验的 p 值按指定方向计算
- 这里仍输出双侧置信区间
- 检验方向必须在查看结果前确定

---

## 44. 模拟一组事件面板

下面模拟 60 个事件，每个事件包含事件时间 \(-5\) 到 \(5\)。

```python
def simulate_event_panel(
    n_events: int = 60,
    start_tau: int = -5,
    end_tau: int = 5,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    rows: list[dict[str, float | int | str]] = []

    for event_number in range(1, n_events + 1):
        event_id = f"E{event_number:03d}"

        for tau in range(start_tau, end_tau + 1):
            market_return = rng.normal(loc=0.0002, scale=0.0100)

            alpha = rng.normal(loc=0.00005, scale=0.00010)
            beta = rng.normal(loc=1.0, scale=0.15)
            idiosyncratic = rng.normal(loc=0.0, scale=0.0120)

            event_effect = 0.0

            if tau == -1:
                event_effect = 0.002
            elif tau == 0:
                event_effect = 0.010
            elif tau == 1:
                event_effect = 0.004

            stock_return = (
                alpha
                + beta * market_return
                + idiosyncratic
                + event_effect
            )

            rows.append(
                {
                    "event_id": event_id,
                    "tau": tau,
                    "stock_return": stock_return,
                    "market_return": market_return,
                }
            )

    return pd.DataFrame(rows)
```

这里人为设置了：

- \(\tau=-1\) 有轻微提前反应
- \(\tau=0\) 有主要事件效应
- \(\tau=1\) 有延迟反应

---

## 45. 使用市场调整模型计算异常收益

```python
def add_market_adjusted_abnormal_return(
    panel: pd.DataFrame,
) -> pd.DataFrame:
    required = {
        "event_id",
        "tau",
        "stock_return",
        "market_return",
    }

    missing = required.difference(panel.columns)

    if missing:
        raise ValueError(f"缺少字段：{sorted(missing)}")

    result = panel.copy()

    result["abnormal_return"] = (
        result["stock_return"]
        - result["market_return"]
    )

    return result
```

对应公式：

\[
AR_{i,\tau}
=
R_{i,\tau}-R_{m,\tau}
\]

---

## 46. 计算 AAR

```python
def calculate_aar(panel: pd.DataFrame) -> pd.DataFrame:
    aar = (
        panel.groupby("tau", as_index=False)
        .agg(
            n_events=("abnormal_return", "count"),
            aar=("abnormal_return", "mean"),
            ar_std=("abnormal_return", "std"),
        )
        .sort_values("tau")
    )

    aar["aar_se"] = (
        aar["ar_std"]
        / np.sqrt(aar["n_events"])
    )

    return aar
```

---

## 47. 计算每个事件的 CAR

```python
def calculate_event_car(
    panel: pd.DataFrame,
    window_start: int,
    window_end: int,
) -> pd.DataFrame:
    if window_start > window_end:
        raise ValueError("window_start 不能大于 window_end。")

    window = panel.loc[
        panel["tau"].between(window_start, window_end)
    ].copy()

    expected_days = window_end - window_start + 1

    car = (
        window.groupby("event_id", as_index=False)
        .agg(
            observed_days=("abnormal_return", "count"),
            car=("abnormal_return", "sum"),
        )
    )

    car["is_complete"] = (
        car["observed_days"] == expected_days
    )

    return car
```

建议主分析只使用完整事件窗口：

```python
complete_car = car.loc[car["is_complete"]].copy()
```

---

## 48. 检验主事件窗口

```python
panel = simulate_event_panel()
panel = add_market_adjusted_abnormal_return(panel)

car_table = calculate_event_car(
    panel=panel,
    window_start=-1,
    window_end=1,
)

complete_car = car_table.loc[
    car_table["is_complete"]
].copy()

test_result = one_sample_mean_test(
    values=complete_car["car"],
    null_mean=0.0,
    confidence=0.95,
    alternative="greater",
)

print(test_result)
```

研究假设为：

\[
H_0:
E[CAR(-1,1)]\leq0
\]

\[
H_1:
E[CAR(-1,1)]>0
\]

---

## 49. 输出逐日显著性结果

```python
def test_aar_by_tau(
    panel: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []

    for tau, group in panel.groupby("tau"):
        result = one_sample_mean_test(
            values=group["abnormal_return"],
            null_mean=0.0,
            confidence=0.95,
            alternative="two-sided",
        )

        rows.append(
            {
                "tau": int(tau),
                "n": result.n,
                "aar": result.mean,
                "se": result.se,
                "t_stat": result.t_stat,
                "p_value": result.p_value,
                "ci_low": result.ci_low,
                "ci_high": result.ci_high,
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values("tau")
        .reset_index(drop=True)
    )
```

逐日检验属于多个假设检验。

因此不要只挑出 p 值最小的一天进行展示。

---

## 50. 计算 CAAR 路径

```python
def calculate_caar_path(
    panel: pd.DataFrame,
) -> pd.DataFrame:
    aar = calculate_aar(panel)

    aar = aar.sort_values("tau").copy()
    aar["caar"] = aar["aar"].cumsum()

    return aar
```

这里的累计起点是当前面板中最早的 \(\tau\)。

报告时需要明确：

\[
CAAR(-5,\tau)
\]

而不是笼统写成“累计异常收益”。

---

# 十二、Python 实践：市场模型版本

## 51. 单个事件的市场模型估计

假设输入数据已经包含：

- `tau`
- `stock_return`
- `market_return`

估计窗口设为：

\[
[-120,-21]
\]

事件窗口设为：

\[
[-5,5]
\]

```python
@dataclass
class MarketModelEstimate:
    alpha: float
    beta: float
    residual_std: float
    n_obs: int
```

```python
def fit_market_model(
    data: pd.DataFrame,
    estimation_start: int = -120,
    estimation_end: int = -21,
) -> MarketModelEstimate:
    estimation = data.loc[
        data["tau"].between(
            estimation_start,
            estimation_end,
        ),
        ["stock_return", "market_return"],
    ].dropna()

    if len(estimation) < 30:
        raise ValueError("估计窗口有效样本过少。")

    x = estimation["market_return"].to_numpy(dtype=float)
    y = estimation["stock_return"].to_numpy(dtype=float)

    design = np.column_stack(
        [
            np.ones_like(x),
            x,
        ]
    )

    coefficients, _, _, _ = np.linalg.lstsq(
        design,
        y,
        rcond=None,
    )

    alpha = float(coefficients[0])
    beta = float(coefficients[1])

    fitted = alpha + beta * x
    residuals = y - fitted

    residual_std = float(
        np.std(residuals, ddof=2)
    )

    return MarketModelEstimate(
        alpha=alpha,
        beta=beta,
        residual_std=residual_std,
        n_obs=len(estimation),
    )
```

---

## 52. 计算市场模型异常收益

```python
def add_market_model_abnormal_return(
    data: pd.DataFrame,
    estimate: MarketModelEstimate,
    event_start: int = -5,
    event_end: int = 5,
) -> pd.DataFrame:
    event_window = data.loc[
        data["tau"].between(
            event_start,
            event_end,
        )
    ].copy()

    event_window["expected_return"] = (
        estimate.alpha
        + estimate.beta
        * event_window["market_return"]
    )

    event_window["abnormal_return"] = (
        event_window["stock_return"]
        - event_window["expected_return"]
    )

    event_window["car"] = (
        event_window["abnormal_return"]
        .cumsum()
    )

    return event_window
```

---

## 53. 市场模型计算过程

第一步，估计正常关系：

\[
R_{i,t}
=
\hat{\alpha}_i
+
\hat{\beta}_iR_{m,t}
+
\hat{\varepsilon}_{i,t}
\]

第二步，预测事件期正常收益：

\[
\widehat{R}_{i,\tau}
=
\hat{\alpha}_i
+
\hat{\beta}_iR_{m,\tau}
\]

第三步，计算异常收益：

\[
AR_{i,\tau}
=
R_{i,\tau}
-
\widehat{R}_{i,\tau}
\]

第四步，计算累计异常收益：

\[
CAR_i(\tau_1,\tau_2)
=
\sum_{\tau=\tau_1}^{\tau_2}
AR_{i,\tau}
\]

---

# 十三、结果可视化

## 54. AAR 路径图

```python
import matplotlib.pyplot as plt

aar_table = calculate_aar(panel)

plt.figure(figsize=(9, 5))
plt.plot(
    aar_table["tau"],
    aar_table["aar"],
    marker="o",
)
plt.axhline(0.0)
plt.axvline(0)
plt.xlabel("事件时间")
plt.ylabel("平均异常收益")
plt.title("事件窗口内的 AAR")
plt.tight_layout()
plt.show()
```

图中重点观察：

- \(\tau=0\) 是否出现跳升或跳降
- 事件前是否有提前反应
- 事件后是否有延迟反应
- 异常收益是否快速回归 0

---

## 55. CAAR 路径图

```python
caar_table = calculate_caar_path(panel)

plt.figure(figsize=(9, 5))
plt.plot(
    caar_table["tau"],
    caar_table["caar"],
    marker="o",
)
plt.axhline(0.0)
plt.axvline(0)
plt.xlabel("事件时间")
plt.ylabel("累计平均异常收益")
plt.title("事件窗口内的 CAAR")
plt.tight_layout()
plt.show()
```

CAAR 曲线的解释：

- 持续上升：平均异常收益多为正
- 持续下降：平均异常收益多为负
- 事件日跳升后横盘：价格快速完成反应
- 事件后继续上升：可能存在延迟反应
- 事件前开始变化：可能存在预期或信息泄露

---

# 十四、常见错误

## 56. 把公告自然日直接当作事件日

如果公告发生在收盘后，公告日当天价格不可能反映该信息。

修正方法：

> 根据公告时间和交易日历确定市场首次可交易日期。

---

## 57. 使用未来数据估计正常收益

若估计窗口包含事件之后的数据，会产生前视偏差。

正确顺序：

\[
\text{估计窗口}
<
\text{事件窗口}
\]

---

## 58. 使用事件窗口估计市场模型

事件冲击会污染 \(\alpha\) 和 \(\beta\) 的估计。

应使用事件发生前的独立估计窗口。

---

## 59. 忽略市场整体涨跌

只计算股票实际收益，不能区分事件效应与系统性行情。

至少应使用市场调整收益：

\[
AR_{i,\tau}
=
R_{i,\tau}-R_{m,\tau}
\]

---

## 60. 事件窗口过长

较长窗口会引入更多其他新闻。

窗口越长：

- 事件效应覆盖更完整
- 混杂信息也更多
- 因果解释更困难

---

## 61. 只展示最显著窗口

如果研究者尝试很多窗口，再只报告最显著的一个，会放大假阳性。

必须记录所有尝试过的主窗口和补充窗口。

---

## 62. 忽略同一股票重复事件

同一股票短期内多个事件可能导致窗口重叠。

处理方法包括：

- 删除重叠事件
- 只保留第一个事件
- 缩短事件窗口
- 将重叠事件单独标记
- 使用更稳健的聚类标准误

本周报告中至少要披露处理规则。

---

## 63. 忽略停牌和涨跌停

A 股中，事件发生后股票可能：

- 停牌
- 一字涨停
- 一字跌停
- 流动性不足

这会使价格反应延迟到后续交易日。

因此不能只根据 \(\tau=0\) 的收益判断市场反应是否完成。

---

## 64. 将显著性当作可交易性

统计显著的异常收益不一定可以交易。

还需要考虑：

- 公告发布时间
- 信号是否在交易前可获得
- 涨跌停限制
- 滑点
- 交易成本
- 成交量
- 冲击成本
- 样本外稳定性

事件研究回答的是价格反应问题，不自动等于形成可实施策略。

---

# 十五、事件研究报告模板

## 65. 研究问题

清楚写明：

- 研究哪类事件
- 预期方向是什么
- 主事件窗口是什么
- 为什么选择该窗口

---

## 66. 数据说明

至少写明：

- 样本区间
- 股票范围
- 事件数量
- 事件来源
- 行情来源
- 市场基准
- 收益率口径
- 复权口径
- 缺失值处理
- 重叠事件处理

---

## 67. 方法说明

至少写明：

- 事件日对齐规则
- 估计窗口
- 间隔窗口
- 事件窗口
- 正常收益模型
- 异常收益公式
- CAR 公式
- 显著性检验
- 多重检验处理

---

## 68. 结果表

建议至少包含：

| 指标 | 结果 |
|---|---:|
| 事件数量 |  |
| 主事件窗口 |  |
| 平均 CAR |  |
| CAR 中位数 |  |
| CAR 标准差 |  |
| 标准误 |  |
| t 统计量 |  |
| p 值 |  |
| 置信区间下限 |  |
| 置信区间上限 |  |
| 正 CAR 占比 |  |

---

## 69. 结果解释

结果解释应区分三层。

### 统计结论

是否拒绝原假设。

### 经济结论

平均异常收益是否足够大。

### 交易结论

考虑交易限制和成本后是否可能执行。

不要将三者混写。

---

## 70. 局限性

至少讨论：

- 事件之间可能不独立
- 事件日期可能存在测量误差
- 正常收益模型可能不充分
- 事件窗口可能存在混杂信息
- 样本可能存在选择偏差
- 多重检验可能提高假阳性
- 结果不代表因果机制已经被证明

---

# 十六、今日练习

## 71. 概念练习

### 练习 1

某公告在周五 18:00 发布，下一交易日是周一。事件日应设为哪一天？

### 练习 2

为什么不能用事件窗口内的数据估计市场模型？

### 练习 3

股票事件日上涨 \(4\%\)，市场上涨 \(2.5\%\)。使用市场调整模型时异常收益是多少？

### 练习 4

事件窗口 \([-1,1]\) 的异常收益分别为：

\[
0.3\%
\]

\[
1.4\%
\]

\[
-0.2\%
\]

计算 \(CAR(-1,1)\)。

### 练习 5

为什么只研究一个事件时，不适合对“一类事件的平均影响”作强统计结论？

### 练习 6

同时检验 10 个事件窗口，并希望家族错误率控制在 \(5\%\)，Bonferroni 阈值是多少？

---

## 72. 计算练习

某研究收集 5 个事件，其 \([-1,1]\) 窗口 CAR 分别为：

\[
0.012
\]

\[
0.018
\]

\[
-0.004
\]

\[
0.010
\]

\[
0.014
\]

完成：

1. 计算平均 CAR
2. 计算样本标准差
3. 计算标准误
4. 计算 t 统计量
5. 解释统计量的含义

---

## 73. 编程练习

### 练习 A

运行模拟事件面板，计算：

- 每个事件的 \(CAR(-1,1)\)
- 平均 CAR
- 中位数 CAR
- 正 CAR 占比
- \(95\%\) 置信区间
- t 统计量
- p 值

### 练习 B

比较三个窗口：

- \([-1,1]\)
- \([-3,3]\)
- \([0,2]\)

说明为什么窗口扩大后平均 CAR 和 p 值都可能变化。

### 练习 C

将市场调整模型替换为市场模型，并比较两种方法的异常收益差异。

### 练习 D

人为删除部分事件日数据，检查 `is_complete` 字段能否识别不完整窗口。

### 练习 E

将事件日整体错误地向前移动 1 个交易日，观察 AAR 和 CAAR 路径如何变化。

---

# 十七、练习参考答案

## 74. 概念练习答案

### 练习 1

公告发生在周五收盘后，市场首次可以交易该信息的时间是周一。

因此：

\[
\tau=0
\]

应设置为周一。

### 练习 2

事件窗口包含事件冲击。

如果使用事件窗口估计正常收益模型，模型会把一部分事件效应当作正常收益，从而低估异常收益。

### 练习 3

\[
AR_0
=
4\%-2.5\%
\]

\[
AR_0
=
1.5\%
\]

### 练习 4

\[
CAR(-1,1)
=
0.3\%+1.4\%-0.2\%
\]

\[
CAR(-1,1)
=
1.5\%
\]

### 练习 5

单个事件的价格变化可能受到大量偶然因素影响。

它可以用于案例描述，但不能稳定估计同类事件的平均效应和横截面分布。

### 练习 6

\[
\alpha_{\text{single}}
=
\frac{0.05}{10}
\]

\[
\alpha_{\text{single}}
=
0.005
\]

---

## 75. 计算练习答案

样本为：

\[
0.012,\ 0.018,\ -0.004,\ 0.010,\ 0.014
\]

第一步，计算总和：

\[
0.012+0.018-0.004+0.010+0.014
\]

\[
=0.050
\]

第二步，计算平均值：

\[
\overline{CAR}
=
\frac{0.050}{5}
\]

\[
\overline{CAR}
=
0.010
\]

即平均 CAR 为：

\[
1.0\%
\]

第三步，计算每个观测与均值的差：

\[
0.012-0.010=0.002
\]

\[
0.018-0.010=0.008
\]

\[
-0.004-0.010=-0.014
\]

\[
0.010-0.010=0
\]

\[
0.014-0.010=0.004
\]

第四步，计算离差平方和：

\[
0.002^2
+
0.008^2
+
(-0.014)^2
+
0^2
+
0.004^2
\]

\[
=
0.000004
+
0.000064
+
0.000196
+
0
+
0.000016
\]

\[
=
0.000280
\]

第五步，计算样本方差：

\[
s^2
=
\frac{0.000280}{5-1}
\]

\[
s^2
=
0.000070
\]

第六步，计算样本标准差：

\[
s
=
\sqrt{0.000070}
\]

\[
s
\approx0.008367
\]

第七步，计算标准误：

\[
SE
=
\frac{0.008367}{\sqrt{5}}
\]

\[
SE
\approx0.003742
\]

第八步，计算 t 统计量：

\[
t
=
\frac{0.010}{0.003742}
\]

\[
t
\approx2.672
\]

解释：

> 样本平均 CAR 距离 0 大约为 2.67 个标准误。

由于样本量只有 5，自由度为：

\[
df=4
\]

最终显著性判断应基于自由度为 4 的 t 分布，而不能直接使用正态分布临界值。

---

# 十八、今日输出任务

## 76. 必须完成的输出

今天完成一份简单事件研究报告，至少包含：

1. 研究问题
2. 事件定义
3. 事件日对齐规则
4. 估计窗口
5. 事件窗口
6. 正常收益模型
7. 异常收益公式
8. AAR 路径
9. CAAR 路径
10. 主窗口 CAR 检验
11. 置信区间
12. 多重检验说明
13. 数据质量说明
14. 研究局限性
15. 结论

---

## 77. 建议保存的代码函数

至少保存：

- `one_sample_mean_test`
- `simulate_event_panel`
- `add_market_adjusted_abnormal_return`
- `calculate_aar`
- `calculate_event_car`
- `test_aar_by_tau`
- `calculate_caar_path`
- `fit_market_model`
- `add_market_model_abnormal_return`

---

## 78. 建议的研究记录

在学习笔记中回答：

1. 事件研究真正衡量的是什么？
2. 为什么公告时间比公告日期更重要？
3. 估计窗口和事件窗口为什么必须分开？
4. 市场调整模型与市场模型的区别是什么？
5. \(AR\)、\(CAR\)、\(AAR\) 和 \(CAAR\) 分别表示什么？
6. 为什么单事件案例不能代表一类事件？
7. 如何检验平均 CAR 是否显著不为 0？
8. 为什么必须同时报告效应大小和 p 值？
9. 事件研究中有哪些多重检验风险？
10. A 股停牌和涨跌停如何影响事件反应？
11. 哪些情况会使普通 t 检验标准误偏小？
12. 事件研究结果为什么不自动等于可交易策略？

---

# 十九、今日检查清单

完成学习后逐项检查：

- [ ] 能解释事件研究的核心问题
- [ ] 能正确确定事件日
- [ ] 能区分估计窗口、间隔窗口和事件窗口
- [ ] 能说明为什么不能使用未来数据
- [ ] 能计算简单收益率或对数收益率
- [ ] 能写出市场调整异常收益公式
- [ ] 能写出市场模型
- [ ] 能解释 \(\alpha\) 与 \(\beta\)
- [ ] 能计算单日异常收益
- [ ] 能计算 \(CAR\)
- [ ] 能计算 \(AAR\)
- [ ] 能计算 \(CAAR\)
- [ ] 能写出平均 CAR 的原假设和备择假设
- [ ] 能计算平均 CAR 的标准误
- [ ] 能解释 t 统计量和 p 值
- [ ] 能构造平均 CAR 的置信区间
- [ ] 能同时报告均值、中位数和正收益占比
- [ ] 能说明多重窗口测试的风险
- [ ] 能说明重叠事件的影响
- [ ] 能说明停牌与涨跌停的影响
- [ ] 能运行简单事件研究程序
- [ ] 能输出结构完整的事件研究报告

---

# 二十、本周总结

## 79. 本周知识链条

第八周形成了以下完整路径：

\[
\text{概率}
\rightarrow
\text{随机变量}
\rightarrow
\text{概率分布}
\rightarrow
\text{期望与方差}
\rightarrow
\text{总体与样本}
\rightarrow
\text{抽样分布}
\rightarrow
\text{中心极限定理}
\rightarrow
\text{标准误}
\rightarrow
\text{置信区间}
\rightarrow
\text{假设检验}
\rightarrow
\text{多重检验}
\rightarrow
\text{事件研究}
\]

---

## 80. 本周核心能力

完成本周后，你应具备以下能力：

1. 用概率语言描述随机现象。
2. 区分总体参数和样本统计量。
3. 理解样本均值为什么会波动。
4. 使用标准误衡量估计不确定性。
5. 使用置信区间表达参数可能范围。
6. 正确写出原假设和备择假设。
7. 正确解释 p 值。
8. 区分第一类错误和第二类错误。
9. 识别多重检验导致的假发现。
10. 将统计推断应用到简单事件研究。

---

# 二十一、今日核心结论

1. 事件研究衡量的是实际收益相对于正常收益的偏离，而不是股票是否单纯上涨或下跌。
2. 事件日必须按市场首次能够交易信息的时间确定。
3. 估计窗口用于建立正常收益模型，不能与事件窗口重叠。
4. 异常收益定义为实际收益减去正常收益。
5. 市场调整模型简单直观，市场模型允许不同股票具有不同市场敏感度。
6. \(CAR\) 衡量单个事件窗口的累计异常收益。
7. \(AAR\) 衡量多个事件在同一事件时间的平均异常收益。
8. \(CAAR\) 衡量多个事件在一个窗口内的平均累计影响。
9. 显著性检验应以事件为样本单位，并同时报告效应大小、置信区间和 p 值。
10. 逐日检验和多窗口检验都会产生多重检验问题。
11. 事件重叠、行业集中和共同市场冲击会破坏独立性假设。
12. 统计显著不等于经济显著，更不等于策略可交易。
13. 简单事件研究的价值在于把概率、抽样、标准误、置信区间和假设检验连接到真实量化研究流程中。
