# 第九周 · 第三天

## 夏普比率：超额收益、无风险利率与频率一致性

---

## 1. 今日学习目标

完成今天的学习后，你需要能够：

- 理解夏普比率衡量的核心问题
- 从“收益”和“风险”两个维度解释夏普比率
- 区分总收益、超额收益和风险溢价
- 理解无风险利率在夏普比率中的作用
- 将年化无风险利率转换为日频、周频或月频利率
- 推导周期夏普比率与年化夏普比率的关系
- 理解为什么夏普比率通常使用算术平均收益，而不是 CAGR
- 正确处理收益率频率、无风险利率频率与年化因子
- 识别零波动、短样本、自相关和非正态分布等问题
- 编写可复用的夏普比率函数
- 编写滚动夏普比率函数
- 使用已知样例验证计算结果

---

## 2. 今日学习顺序

建议学习时间：约 120—150 分钟。

| 阶段 | 内容 | 建议时间 |
|---|---|---:|
| 1 | 夏普比率的直觉 | 20 分钟 |
| 2 | 超额收益与无风险利率 | 25 分钟 |
| 3 | 公式与年化推导 | 35 分钟 |
| 4 | 口径、假设与局限 | 25 分钟 |
| 5 | Python 实现与测试 | 35 分钟 |
| 6 | 练习与复盘 | 15 分钟 |

---

# 一、为什么需要夏普比率

## 3. 只看收益率不够

假设两个策略的年化收益分别为：

- 策略 A：\(12\%\)
- 策略 B：\(18\%\)

只看收益，策略 B 更高。

但如果它们的年化波动率分别为：

- 策略 A：\(8\%\)
- 策略 B：\(30\%\)

那么策略 B 为获得更高收益，承担了远高于策略 A 的波动。

因此，评价策略时不能只问：

> 策略赚了多少？

还需要问：

> 策略每承担一单位风险，获得了多少额外收益？

夏普比率就是用来回答这个问题的。

---

## 4. 夏普比率的直觉

夏普比率的核心结构是：

\[
\text{夏普比率}
=
\frac{\text{超额收益}}{\text{收益波动率}}
\]

分子表示策略相对于无风险资产多获得了多少收益。

分母表示为了获得这些超额收益，策略承担了多大的收益波动。

因此：

- 分子越大，夏普比率越高
- 分母越小，夏普比率越高
- 超额收益为负时，夏普比率通常为负
- 波动率接近零时，夏普比率可能不稳定

---

## 5. 一个简单比较

假设：

- 策略 A 年化收益为 \(12\%\)
- 策略 A 年化波动率为 \(10\%\)
- 策略 B 年化收益为 \(18\%\)
- 策略 B 年化波动率为 \(25\%\)
- 年化无风险利率为 \(2\%\)

策略 A 的夏普比率为：

\[
Sharpe_A
=
\frac{12\%-2\%}{10\%}
\]

\[
Sharpe_A
=
\frac{10\%}{10\%}
\]

\[
Sharpe_A=1.0
\]

策略 B 的夏普比率为：

\[
Sharpe_B
=
\frac{18\%-2\%}{25\%}
\]

\[
Sharpe_B
=
\frac{16\%}{25\%}
\]

\[
Sharpe_B=0.64
\]

虽然策略 B 的年化收益更高，但策略 A 的单位风险超额收益更高。

这说明：

> 高收益策略不一定具有更高的风险调整后收益。

---

# 二、总收益、超额收益与风险溢价

## 6. 总收益率

设策略在第 \(t\) 期的收益率为：

\[
r_t
\]

这个收益率是策略本身的总收益率。

它没有扣除投资者即使不承担策略风险，也可能获得的低风险收益。

---

## 7. 无风险收益率

设第 \(t\) 期无风险收益率为：

\[
r_{f,t}
\]

无风险利率不是绝对意义上的“完全没有任何风险”。

在绩效评价中，它通常代表：

> 投资者不承担策略风险时，可以获得的基准资金收益。

实际研究中可根据研究目的选择：

- 短期国债收益率
- 同期限政策性利率或货币市场利率
- 现金管理类收益率
- 研究中预先规定的固定资金成本
- 在简化教学中使用 \(0\%\)

关键不是唯一选择某一个利率，而是：

1. 明确所选利率
2. 明确利率期限
3. 明确利率频率
4. 在不同策略之间保持一致

---

## 8. 单期超额收益

策略第 \(t\) 期的超额收益为：

\[
e_t
=
r_t-r_{f,t}
\]

其中：

- \(r_t\) 是策略单期收益率
- \(r_{f,t}\) 是同一周期的无风险收益率
- \(e_t\) 是策略单期超额收益

如果：

\[
r_t>r_{f,t}
\]

则：

\[
e_t>0
\]

如果：

\[
r_t<r_{f,t}
\]

则：

\[
e_t<0
\]

---

## 9. 为什么必须扣除无风险利率

假设某策略年化收益为 \(4\%\)，年化波动率为 \(5\%\)。

如果无风险利率为 \(0\%\)，则：

\[
Sharpe
=
\frac{4\%-0\%}{5\%}
\]

\[
Sharpe=0.8
\]

如果无风险利率为 \(3\%\)，则：

\[
Sharpe
=
\frac{4\%-3\%}{5\%}
\]

\[
Sharpe=0.2
\]

策略本身没有变化，但它相对于低风险资产的吸引力发生了变化。

当无风险利率上升时，投资者对风险策略的机会成本也会上升。

---

# 三、夏普比率的基础公式

## 10. 总体定义

从理论上说，夏普比率可写为：

\[
Sharpe
=
\frac{\mathbb{E}[R_p-R_f]}{\sigma(R_p-R_f)}
\]

其中：

- \(R_p\) 是投资组合收益
- \(R_f\) 是无风险收益
- \(\mathbb{E}[R_p-R_f]\) 是期望超额收益
- \(\sigma(R_p-R_f)\) 是超额收益标准差

若无风险利率在每一期是常数，则：

\[
\sigma(R_p-R_f)
=
\sigma(R_p)
\]

原因是常数不会改变方差。

逐步推导如下。

设无风险收益为常数 \(c\)：

\[
R_f=c
\]

则：

\[
\operatorname{Var}(R_p-c)
=
\mathbb{E}
\left[
(R_p-c-\mathbb{E}[R_p-c])^2
\right]
\]

因为：

\[
\mathbb{E}[R_p-c]
=
\mathbb{E}[R_p]-c
\]

所以：

\[
R_p-c-\mathbb{E}[R_p-c]
=
R_p-c-(\mathbb{E}[R_p]-c)
\]

展开括号：

\[
R_p-c-\mathbb{E}[R_p]+c
\]

合并常数项：

\[
R_p-\mathbb{E}[R_p]
\]

因此：

\[
\operatorname{Var}(R_p-c)
=
\mathbb{E}
\left[
(R_p-\mathbb{E}[R_p])^2
\right]
\]

所以：

\[
\operatorname{Var}(R_p-c)
=
\operatorname{Var}(R_p)
\]

两边开平方：

\[
\sigma(R_p-c)
=
\sigma(R_p)
\]

因此，在无风险利率为常数时，夏普比率常写为：

\[
Sharpe
=
\frac{\mathbb{E}[R_p]-R_f}{\sigma(R_p)}
\]

---

## 11. 样本夏普比率

实际研究中，我们没有完整的未来收益分布，只能使用历史样本估计。

给定 \(N\) 个周期收益率：

\[
r_1,r_2,\ldots,r_N
\]

给定对应的无风险收益率：

\[
r_{f,1},r_{f,2},\ldots,r_{f,N}
\]

定义超额收益：

\[
e_t=r_t-r_{f,t}
\]

样本平均超额收益为：

\[
\bar e
=
\frac{1}{N}
\sum_{t=1}^{N}e_t
\]

样本标准差为：

\[
s_e
=
\sqrt{
\frac{1}{N-1}
\sum_{t=1}^{N}
(e_t-\bar e)^2
}
\]

周期夏普比率为：

\[
Sharpe_{\text{period}}
=
\frac{\bar e}{s_e}
\]

---

# 四、夏普比率如何年化

## 12. 周期夏普比率不能直接跨频率比较

日频夏普比率、周频夏普比率和月频夏普比率的时间尺度不同。

例如，一个日频平均超额收益为 \(0.05\%\) 的策略，不能直接与一个月频平均超额收益为 \(1\%\) 的策略比较。

需要将它们转换到统一的年度尺度。

---

## 13. 收益均值的年化

设单期平均超额收益为：

\[
\bar e
\]

一年包含 \(A\) 个同频周期。

在算术近似下，年化平均超额收益为：

\[
\bar e_{\text{annual}}
=
A\bar e
\]

这里使用的是算术平均收益的线性缩放。

---

## 14. 波动率的年化

设单期超额收益标准差为：

\[
s_e
\]

在收益独立同分布或至少不存在显著自相关的近似条件下：

\[
s_{e,\text{annual}}
=
s_e\sqrt{A}
\]

---

## 15. 年化夏普比率的逐步推导

年化夏普比率定义为：

\[
Sharpe_{\text{annual}}
=
\frac{\bar e_{\text{annual}}}{s_{e,\text{annual}}}
\]

代入年化平均超额收益：

\[
Sharpe_{\text{annual}}
=
\frac{A\bar e}{s_{e,\text{annual}}}
\]

再代入年化波动率：

\[
Sharpe_{\text{annual}}
=
\frac{A\bar e}{s_e\sqrt{A}}
\]

将 \(A\) 写为：

\[
A
=
\sqrt{A}\sqrt{A}
\]

因此：

\[
Sharpe_{\text{annual}}
=
\frac{\sqrt{A}\sqrt{A}\bar e}{s_e\sqrt{A}}
\]

约去分子和分母中的一个 \(\sqrt{A}\)：

\[
Sharpe_{\text{annual}}
=
\sqrt{A}
\frac{\bar e}{s_e}
\]

因为：

\[
Sharpe_{\text{period}}
=
\frac{\bar e}{s_e}
\]

所以：

\[
Sharpe_{\text{annual}}
=
Sharpe_{\text{period}}\sqrt{A}
\]

这就是夏普比率常用的年化公式。

---

## 16. 常用年化因子

| 收益频率 | 一年周期数 \(A\) | 夏普年化倍数 |
|---|---:|---:|
| 日频 | 252 | \(\sqrt{252}\) |
| 周频 | 52 | \(\sqrt{52}\) |
| 月频 | 12 | \(\sqrt{12}\) |
| 季度 | 4 | \(2\) |
| 年频 | 1 | \(1\) |

日频使用 252 是常见市场惯例，不是不可改变的数学常数。

实际项目必须明确年化因子。

---

# 五、无风险利率的频率转换

## 17. 最常见的频率错误

假设策略输入是日收益率，但无风险利率输入的是年化利率。

若直接计算：

\[
r_t-r_{f,\text{annual}}
\]

就是把日收益与年收益相减。

这在量纲上不一致。

正确做法是先将年化无风险利率转换为日频无风险利率。

---

## 18. 有效年利率转换为周期利率

设有效年化无风险利率为：

\[
r_{f,a}
\]

一年有 \(A\) 个复利周期。

设单期无风险利率为：

\[
r_{f,p}
\]

一年复利后的增长因子为：

\[
(1+r_{f,p})^A
\]

它应等于年化增长因子：

\[
1+r_{f,a}
\]

因此：

\[
(1+r_{f,p})^A
=
1+r_{f,a}
\]

两边同时取 \(A\) 次方根：

\[
1+r_{f,p}
=
(1+r_{f,a})^{1/A}
\]

两边减去 1：

\[
r_{f,p}
=
(1+r_{f,a})^{1/A}-1
\]

这是一种严格的有效利率转换。

---

## 19. 线性近似

在利率较低时，常见近似为：

\[
r_{f,p}
\approx
\frac{r_{f,a}}{A}
\]

例如，年化无风险利率为 \(2\%\)，日频年化因子为 252。

线性近似为：

\[
r_{f,d}
\approx
\frac{2\%}{252}
\]

\[
r_{f,d}
\approx
0.0079365\%
\]

严格复利转换为：

\[
r_{f,d}
=
(1+2\%)^{1/252}-1
\]

\[
r_{f,d}
\approx
0.0078585\%
\]

两者非常接近，但并不完全相同。

研究代码应明确使用哪一种口径。

---

## 20. 连续复利利率

若输入的是连续复利年利率 \(y\)，一年增长因子为：

\[
e^y
\]

单期连续复利利率可以直接写为：

\[
y_p
=
\frac{y}{A}
\]

对应的单期简单收益率为：

\[
r_{f,p}
=
e^{y/A}-1
\]

不要把连续复利利率和有效年利率混为一谈。

---

# 六、一个完整计算示例

## 21. 已知条件

某策略的日收益统计如下：

- 日均收益率：\(0.05\%\)
- 日收益样本标准差：\(1.20\%\)
- 年化无风险利率：\(2\%\)
- 年化因子：252

将百分数写成小数：

\[
\bar r_d=0.0005
\]

\[
s_d=0.012
\]

\[
r_{f,a}=0.02
\]

---

## 22. 第一步：转换日无风险利率

\[
r_{f,d}
=
(1+r_{f,a})^{1/252}-1
\]

代入：

\[
r_{f,d}
=
(1+0.02)^{1/252}-1
\]

\[
r_{f,d}
=
1.02^{1/252}-1
\]

\[
r_{f,d}
\approx
0.0000785849
\]

转换为百分比：

\[
r_{f,d}
\approx
0.00785849\%
\]

---

## 23. 第二步：计算日均超额收益

\[
\bar e_d
=
\bar r_d-r_{f,d}
\]

代入：

\[
\bar e_d
=
0.0005-0.0000785849
\]

\[
\bar e_d
=
0.0004214151
\]

转换为百分比：

\[
\bar e_d
\approx
0.04214151\%
\]

---

## 24. 第三步：计算日频夏普比率

\[
Sharpe_d
=
\frac{\bar e_d}{s_d}
\]

代入：

\[
Sharpe_d
=
\frac{0.0004214151}{0.012}
\]

\[
Sharpe_d
\approx
0.0351179
\]

---

## 25. 第四步：年化夏普比率

\[
Sharpe_a
=
Sharpe_d\sqrt{252}
\]

代入：

\[
Sharpe_a
=
0.0351179\times\sqrt{252}
\]

因为：

\[
\sqrt{252}
\approx
15.8745
\]

所以：

\[
Sharpe_a
\approx
0.0351179\times15.8745
\]

\[
Sharpe_a
\approx
0.5575
\]

该策略的年化夏普比率约为：

\[
0.56
\]

---

# 七、为什么通常不用 CAGR 直接计算夏普比率

## 26. 夏普比率的分子是平均周期超额收益

经典样本夏普比率使用：

\[
\bar e
=
\frac{1}{N}
\sum_{t=1}^{N}(r_t-r_{f,t})
\]

这是一组周期超额收益的算术平均值。

而 CAGR 或几何年化收益为：

\[
R_{\text{geo}}
=
\left(
\prod_{t=1}^{N}(1+r_t)
\right)^{A/N}-1
\]

两者回答的问题不同。

---

## 27. 算术平均与几何平均的差异

假设两期收益分别为：

\[
r_1=50\%
\]

\[
r_2=-50\%
\]

算术平均收益为：

\[
\bar r
=
\frac{50\%-50\%}{2}
\]

\[
\bar r=0
\]

累计增长因子为：

\[
(1+50\%)(1-50\%)
\]

\[
=1.5\times0.5
\]

\[
=0.75
\]

两期累计收益为：

\[
R_{\text{cum}}
=
0.75-1
\]

\[
R_{\text{cum}}
=-25\%
\]

每期几何平均收益满足：

\[
(1+g)^2=0.75
\]

两边开平方：

\[
1+g=\sqrt{0.75}
\]

\[
g=\sqrt{0.75}-1
\]

\[
g\approx-13.40\%
\]

算术平均为 \(0\%\)，几何平均约为 \(-13.40\%\)。

夏普比率研究的是周期收益分布的均值与标准差，因此通常使用算术平均周期收益。

---

## 28. 不推荐的混合口径

以下写法在报告中很常见，但需要谨慎：

\[
\frac{\text{CAGR}-r_f}{\text{年化波动率}}
\]

它不是经典的样本夏普比率，因为：

- 分子是几何复合增长率
- 分母来自周期收益率的标准差
- 两者统计口径并不完全一致

这种指标可以作为自定义风险收益指标，但应明确命名和说明，不应不加解释地称为标准夏普比率。

---

# 八、夏普比率的解释

## 29. 夏普比率大于零

若：

\[
Sharpe>0
\]

说明样本期平均收益高于无风险收益。

但大于零不等于策略优秀。

还需要考察：

- 样本是否足够长
- 收益是否稳定
- 是否存在极端回撤
- 是否存在收益平滑
- 是否存在数据挖掘偏差
- 是否扣除了交易成本

---

## 30. 夏普比率等于零

若：

\[
Sharpe=0
\]

通常表示：

\[
\bar r=r_f
\]

策略承担了波动，却没有获得高于无风险资产的平均收益。

---

## 31. 夏普比率小于零

若：

\[
Sharpe<0
\]

说明样本期平均收益低于无风险收益。

此时不能简单认为数值“越负越接近零越好”或“波动越大越差”。

例如，当超额收益为负时，增加分母可能让比率在数值上更接近零，但这不代表策略质量改善。

因此负夏普比率应结合原始收益和波动率共同解释。

---

## 32. 常见经验区间只能作为参考

研究中经常看到类似经验判断：

- 夏普比率低于 0：超额收益为负
- 0 到 1：单位风险收益一般
- 1 到 2：风险调整后表现较好
- 2 以上：历史表现非常强

这些区间不是数学定律。

不同市场、策略频率、交易成本、样本长度和估值平滑程度都会影响夏普比率。

不能脱离研究环境机械使用阈值。

---

# 九、频率一致性

## 33. 三个频率必须一致

计算夏普比率时，至少需要保持以下三项一致：

1. 策略收益率频率
2. 无风险利率频率
3. 年化因子

例如，输入为日收益率时：

- 策略收益必须是日收益率
- 无风险利率必须转换成日收益率
- 年化因子通常使用 252

---

## 34. 日历对齐

若无风险利率是随时间变化的序列，需要与策略收益按日期对齐。

设策略收益日期集合为：

\[
D_p
\]

无风险利率日期集合为：

\[
D_f
\]

有效样本日期应为两者交集：

\[
D
=
D_p\cap D_f
\]

不能让某一天的策略收益错误地减去另一日期的无风险收益。

---

## 35. 缺失值处理

如果策略收益或无风险收益存在缺失值，应先对齐，再删除无效配对。

正确顺序是：

1. 按索引对齐
2. 组成同一张表
3. 对成对数据执行缺失值删除
4. 计算超额收益

不能分别删除缺失值后再按位置相减，因为日期可能错位。

---

# 十、夏普比率依赖的假设

## 36. 平方根时间法则

夏普比率乘以 \(\sqrt{A}\) 年化，继承了波动率平方根时间法则的假设。

若收益之间相互独立，并且每期方差相同：

\[
\operatorname{Var}
\left(
\sum_{t=1}^{A}e_t
\right)
=
\sum_{t=1}^{A}
\operatorname{Var}(e_t)
\]

若每期方差为：

\[
\operatorname{Var}(e_t)=\sigma_e^2
\]

则：

\[
\operatorname{Var}
\left(
\sum_{t=1}^{A}e_t
\right)
=
A\sigma_e^2
\]

两边开平方：

\[
\operatorname{Std}
\left(
\sum_{t=1}^{A}e_t
\right)
=
\sqrt{A}\sigma_e
\]

---

## 37. 存在自相关时

若收益存在自相关，则总方差不仅包含各期方差，还包含协方差项。

两期收益之和的方差为：

\[
\operatorname{Var}(e_1+e_2)
\]

展开：

\[
\operatorname{Var}(e_1+e_2)
=
\operatorname{Var}(e_1)
+
\operatorname{Var}(e_2)
+
2\operatorname{Cov}(e_1,e_2)
\]

如果：

\[
\operatorname{Cov}(e_1,e_2)\neq0
\]

则：

\[
\operatorname{Var}(e_1+e_2)
\neq
\operatorname{Var}(e_1)+\operatorname{Var}(e_2)
\]

因此，简单乘以 \(\sqrt{A}\) 可能高估或低估真实的长期风险。

---

## 38. 收益平滑问题

某些低流动性资产、估值型净值或人工平滑的收益序列可能表现为：

- 单期波动率很低
- 收益自相关较高
- 价格调整滞后
- 账面净值变化缓慢

这会使分母偏低，从而机械地抬高夏普比率。

高夏普比率不一定代表真实可交易风险很低。

---

## 39. 非正态分布问题

夏普比率只使用：

- 均值
- 标准差

它没有直接描述：

- 偏度
- 峰度
- 极端尾部损失
- 最大回撤
- 连续亏损长度
- 跳空风险

两个策略可以具有相同夏普比率，但其中一个可能存在更严重的左尾风险。

因此后续还需要学习最大回撤和 Calmar 比率。

---

# 十一、常见错误

## 40. 错误一：直接用年利率减日收益率

错误写法：

```python
excess_returns = daily_returns - 0.02
```

这里的 `0.02` 表示年化 \(2\%\)，却被当作每日 \(2\%\)。

正确做法是先转换：

```python
daily_rf = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
excess_returns = daily_returns - daily_rf
```

---

## 41. 错误二：使用 CAGR 代替算术平均收益

错误或至少口径不标准的写法：

```python
sharpe = (cagr - annual_rf) / annual_volatility
```

经典样本夏普比率应从周期超额收益的均值与标准差计算。

---

## 42. 错误三：重复年化

错误写法：

```python
annual_excess = excess_returns.mean() * 252
annual_vol = excess_returns.std(ddof=1) * np.sqrt(252)
sharpe = annual_excess / annual_vol * np.sqrt(252)
```

前两步已经将分子和分母年化。

最后再次乘以 \(\sqrt{252}\)，造成重复年化。

正确方式二选一。

方式一：

```python
sharpe = (
    excess_returns.mean()
    / excess_returns.std(ddof=1)
    * np.sqrt(252)
)
```

方式二：

```python
annual_excess = excess_returns.mean() * 252
annual_vol = excess_returns.std(ddof=1) * np.sqrt(252)
sharpe = annual_excess / annual_vol
```

两种方式在相同假设下结果一致。

---

## 43. 错误四：标准差使用了净值序列

错误写法：

```python
sharpe = nav.mean() / nav.std()
```

夏普比率应对收益率或超额收益率计算，而不是对净值水平计算。

正确流程为：

```python
returns = nav.pct_change().dropna()
```

然后再计算超额收益和夏普比率。

---

## 44. 错误五：忽略 `ddof`

`pandas.Series.std()` 默认使用：

```python
ddof=1
```

`numpy.std()` 默认使用：

```python
ddof=0
```

研究代码应显式指定 `ddof`，避免不同库之间结果不一致。

---

## 45. 错误六：波动率为零仍返回无穷大

如果所有收益完全相同：

\[
s_e=0
\]

此时：

\[
Sharpe
=
\frac{\bar e}{0}
\]

数学上不可定义。

代码不应简单返回无穷大，而应抛出异常或返回缺失值，并提醒研究者检查数据。

---

## 46. 错误七：用极短样本解释长期能力

少量观测可以用于测试函数，但不能用于可靠评价策略。

例如，5 个交易日计算出的年化夏普比率可能非常高。

这通常反映：

- 样本均值估计不稳定
- 波动率估计不稳定
- 年化放大了短期偶然结果

不是策略已经被充分验证。

---

# 十二、Python 实现

## 47. 将年化无风险利率转换为周期利率

```python
from __future__ import annotations

import numpy as np
import pandas as pd


def annual_rate_to_period_rate(
    annual_rate: float,
    periods_per_year: int = 252,
) -> float:
    """将有效年利率转换为同频单期有效利率。"""
    if periods_per_year <= 0:
        raise ValueError("periods_per_year 必须为正数")

    if not np.isfinite(annual_rate):
        raise ValueError("annual_rate 必须为有限数")

    if annual_rate <= -1.0:
        raise ValueError("annual_rate 必须大于 -100%")

    return float(
        (1.0 + annual_rate) ** (1.0 / periods_per_year)
        - 1.0
    )
```

---

## 48. 基础夏普比率函数

```python
def sharpe_ratio(
    returns: pd.Series,
    annual_risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
    ddof: int = 1,
) -> float:
    """根据等频简单收益率计算年化夏普比率。"""
    clean = pd.Series(returns, dtype="float64").dropna()

    if periods_per_year <= 0:
        raise ValueError("periods_per_year 必须为正数")

    if ddof < 0:
        raise ValueError("ddof 不能为负数")

    if clean.size <= ddof:
        raise ValueError("有效观测数量必须大于 ddof")

    if not np.isfinite(clean.to_numpy()).all():
        raise ValueError("收益率必须为有限数")

    period_rf = annual_rate_to_period_rate(
        annual_rate=annual_risk_free_rate,
        periods_per_year=periods_per_year,
    )

    excess_returns = clean - period_rf
    excess_std = excess_returns.std(ddof=ddof)

    if np.isclose(excess_std, 0.0):
        raise ValueError("超额收益波动率接近零，夏普比率不可稳定计算")

    period_sharpe = excess_returns.mean() / excess_std

    return float(
        period_sharpe * np.sqrt(periods_per_year)
    )
```

---

## 49. 从净值序列计算夏普比率

```python
def sharpe_ratio_from_nav(
    nav: pd.Series,
    annual_risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
    ddof: int = 1,
) -> float:
    """先从净值计算简单收益率，再计算年化夏普比率。"""
    clean_nav = pd.Series(nav, dtype="float64").dropna()

    if clean_nav.size < 3:
        raise ValueError("净值序列至少需要 3 个有效观测")

    if not np.isfinite(clean_nav.to_numpy()).all():
        raise ValueError("净值必须为有限数")

    if (clean_nav <= 0.0).any():
        raise ValueError("净值必须全部大于零")

    returns = clean_nav.pct_change().dropna()

    return sharpe_ratio(
        returns=returns,
        annual_risk_free_rate=annual_risk_free_rate,
        periods_per_year=periods_per_year,
        ddof=ddof,
    )
```

---

## 50. 滚动夏普比率

```python
def rolling_sharpe_ratio(
    returns: pd.Series,
    window: int = 60,
    annual_risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
    ddof: int = 1,
) -> pd.Series:
    """计算滚动年化夏普比率。"""
    clean = pd.Series(returns, dtype="float64")

    if window <= ddof:
        raise ValueError("window 必须大于 ddof")

    if periods_per_year <= 0:
        raise ValueError("periods_per_year 必须为正数")

    period_rf = annual_rate_to_period_rate(
        annual_rate=annual_risk_free_rate,
        periods_per_year=periods_per_year,
    )

    excess_returns = clean - period_rf

    rolling_mean = excess_returns.rolling(
        window=window,
        min_periods=window,
    ).mean()

    rolling_std = excess_returns.rolling(
        window=window,
        min_periods=window,
    ).std(ddof=ddof)

    result = (
        rolling_mean
        / rolling_std
        * np.sqrt(periods_per_year)
    )

    return result.replace([np.inf, -np.inf], np.nan)
```

---

## 51. 为什么滚动夏普比率有用

全样本夏普比率只给出一个汇总值。

滚动夏普比率可以观察：

- 策略是否在不同市场阶段稳定
- 高夏普是否只来自少数时间区间
- 策略是否正在衰减
- 风险调整后收益是否突然恶化
- 参数或市场环境变化是否影响策略

但滚动窗口越短，估计越不稳定。

窗口越长，变化反映越慢。

---

# 十三、函数验证

## 52. 验证一：手工公式与函数结果一致

```python
returns = pd.Series([
    0.010,
    0.005,
    -0.005,
    0.008,
    -0.002,
])

result = sharpe_ratio(
    returns=returns,
    annual_risk_free_rate=0.0,
    periods_per_year=252,
    ddof=1,
)

manual = (
    returns.mean()
    / returns.std(ddof=1)
    * np.sqrt(252)
)

assert np.isclose(result, manual)
```

---

## 53. 验证二：常数收益应触发异常

```python
constant_returns = pd.Series([
    0.001,
    0.001,
    0.001,
    0.001,
])

try:
    sharpe_ratio(constant_returns)
except ValueError as exc:
    print(exc)
```

常数收益的标准差为零，夏普比率不可稳定定义。

---

## 54. 验证三：日频与月频使用不同年化因子

```python
daily_sharpe = sharpe_ratio(
    returns=daily_returns,
    periods_per_year=252,
)

monthly_sharpe = sharpe_ratio(
    returns=monthly_returns,
    periods_per_year=12,
)
```

不能对月收益率使用 252，也不能对日收益率使用 12。

---

# 十四、练习

## 55. 练习一：基础计算

某策略的年化算术收益为 \(14\%\)，年化波动率为 \(12\%\)，年化无风险利率为 \(2\%\)。

计算夏普比率。

### 解答

\[
Sharpe
=
\frac{14\%-2\%}{12\%}
\]

\[
Sharpe
=
\frac{12\%}{12\%}
\]

\[
Sharpe=1
\]

---

## 56. 练习二：频率判断

下面哪一种写法正确？

日收益率均值为 \(0.04\%\)，日波动率为 \(1\%\)，年化无风险利率为 \(2\%\)。

写法 A：

\[
\frac{0.04\%-2\%}{1\%}\sqrt{252}
\]

写法 B：

\[
\frac{0.04\%-r_{f,d}}{1\%}\sqrt{252}
\]

其中：

\[
r_{f,d}
=
(1+2\%)^{1/252}-1
\]

### 解答

写法 B 正确。

写法 A 把日收益与年收益直接相减，频率不一致。

---

## 57. 练习三：推导年化公式

从以下两个关系出发：

\[
\bar e_{\text{annual}}
=A\bar e
\]

\[
s_{\text{annual}}
=s\sqrt{A}
\]

推导年化夏普比率。

### 解答

\[
Sharpe_{\text{annual}}
=
\frac{\bar e_{\text{annual}}}{s_{\text{annual}}}
\]

代入：

\[
Sharpe_{\text{annual}}
=
\frac{A\bar e}{s\sqrt{A}}
\]

因为：

\[
A=\sqrt{A}\sqrt{A}
\]

所以：

\[
Sharpe_{\text{annual}}
=
\frac{\sqrt{A}\sqrt{A}\bar e}{s\sqrt{A}}
\]

约去一个 \(\sqrt{A}\)：

\[
Sharpe_{\text{annual}}
=
\sqrt{A}\frac{\bar e}{s}
\]

因此：

\[
Sharpe_{\text{annual}}
=
Sharpe_{\text{period}}\sqrt{A}
\]

---

## 58. 练习四：识别重复年化

以下代码有什么问题？

```python
annual_mean = returns.mean() * 252
annual_std = returns.std(ddof=1) * np.sqrt(252)
sharpe = annual_mean / annual_std * np.sqrt(252)
```

### 解答

`annual_mean / annual_std` 已经是年化夏普比率。

最后再次乘以 `np.sqrt(252)`，造成重复年化。

正确写法为：

```python
sharpe = annual_mean / annual_std
```

或者：

```python
sharpe = (
    returns.mean()
    / returns.std(ddof=1)
    * np.sqrt(252)
)
```

---

## 59. 练习五：解释负夏普比率

某策略年化收益为 \(-4\%\)，无风险利率为 \(2\%\)，年化波动率为 \(10\%\)。

### 解答

\[
Sharpe
=
\frac{-4\%-2\%}{10\%}
\]

\[
Sharpe
=
\frac{-6\%}{10\%}
\]

\[
Sharpe=-0.6
\]

这表示策略在承担波动的同时，平均收益还低于无风险收益。

---

# 十五、今日输出

## 60. 最小可复用版本

今天至少应保留两个函数：

```python
annual_rate_to_period_rate()
sharpe_ratio()
```

推荐继续保留：

```python
sharpe_ratio_from_nav()
rolling_sharpe_ratio()
```

---

## 61. 推荐指标输出字段

后续统一绩效评价模块中，夏普部分建议输出：

```text
periods_per_year
annual_risk_free_rate
period_risk_free_rate
mean_period_return
mean_period_excess_return
period_volatility
annualized_excess_return
annualized_volatility
sharpe_ratio
sample_size
```

这样可以避免只输出一个夏普比率，却无法追溯计算口径。

---

# 十六、今日检查清单

完成学习后，检查自己能否回答：

- [ ] 夏普比率的分子和分母分别是什么
- [ ] 为什么需要从策略收益中扣除无风险收益
- [ ] 什么是单期超额收益
- [ ] 为什么日收益不能直接减年化无风险利率
- [ ] 如何将有效年利率转换为日频利率
- [ ] 为什么夏普比率通常使用算术平均周期收益
- [ ] 为什么不应直接使用 CAGR 代替经典夏普分子
- [ ] 周期夏普比率如何年化
- [ ] 为什么年化夏普比率乘以 \(\sqrt{A}\)
- [ ] 自相关为什么会破坏简单年化关系
- [ ] 为什么收益平滑会抬高夏普比率
- [ ] 为什么高夏普比率不代表没有尾部风险
- [ ] `ddof=0` 与 `ddof=1` 有什么区别
- [ ] 波动率为零时为什么不能正常计算夏普比率
- [ ] 如何从净值序列计算夏普比率
- [ ] 如何计算滚动夏普比率

---

# 十七、今日总结

今天最重要的公式是周期超额收益：

\[
e_t
=
r_t-r_{f,t}
\]

样本周期夏普比率为：

\[
Sharpe_{\text{period}}
=
\frac{\bar e}{s_e}
\]

年化夏普比率为：

\[
Sharpe_{\text{annual}}
=
\frac{\bar e}{s_e}\sqrt{A}
\]

有效年化无风险利率转换为单期利率：

\[
r_{f,p}
=
(1+r_{f,a})^{1/A}-1
\]

计算夏普比率时，必须同时明确：

- 收益率类型
- 收益率频率
- 无风险利率来源
- 无风险利率口径
- 年化因子
- 标准差自由度
- 缺失值处理
- 样本长度
- 是否存在自相关
- 是否扣除交易成本

夏普比率把前两天学习的年化收益和年化波动率联系起来，但它不是完整的风险评价。

下一天将学习最大回撤，重点研究净值从历史高点下跌的幅度、回撤序列以及最大回撤区间。