# 第 7 周：描述统计与收益分布

## 本周目标

- 掌握均值、中位数、方差、标准差和分位数。
- 理解偏度、峰度、相关系数与异常值。
- 用图表和统计量描述收益分布。

## 核心成果

完成多股票收益分布分析报告。

## 每日安排

每日学习内容与索引均直接保存在当前周目录。

## 完成标准

- 报告包含统计表、分布图和异常值说明。
- 能解释均值与中位数差异。
- 能识别厚尾和偏态。

## 每日学习路径

| 天 | 主题 | 学习与实践 | 当天输出 |
|---:|---|---|---|
| 1 | [均值、中位数与收益率中心位置](day-01-mean-median.md) | 均值、中位数、上涨比例、极端值影响 | 收益中心统计表 |
| 2 | [方差、标准差与年化波动率](day-02-variance-volatility.md) | 样本方差、年化波动率、滚动波动率、下行波动率 | 波动与离散度表 |
| 3 | [分位数、四分位距与尾部风险](day-03-quantiles-tail-risk.md) | 分位数、IQR、箱线图、最差 5% 收益 | 分位数与尾部分析 |
| 4 | [偏度、峰度与非正态收益分布](day-04-skewness-kurtosis.md) | 偏态、尖峰厚尾、Q-Q 图、极端频率 | 分布形态说明 |
| 5 | [协方差、相关系数与滚动相关性](day-05-covariance-correlation.md) | Pearson、Spearman、共同样本数、条件相关 | 多股票相关矩阵 |
| 6 | [异常收益识别与数据质量检查](day-06-outliers-data-quality.md) | Z 分数、IQR、MAD、业务规则与异常核验 | 异常收益检查表 |
| 7 | [多股票收益分布分析阶段项目](day-07-return-distribution-project.md) | 汇总统计、图表、异常审计、测试与报告 | 完整收益分布报告 |

## 本周检查清单

- [ ] 统计口径和样本区间明确。
- [ ] 收益率、价格和复权口径明确。
- [ ] 均值与中位数同时报告。
- [ ] 年化波动率与滚动波动率均已计算。
- [ ] 1%、5%、95%、99% 分位数均已计算。
- [ ] 偏度、超额峰度和 3σ 事件比例均已解释。
- [ ] 相关系数配合共同有效样本数报告。
- [ ] 已检查滚动相关性和压力时期相关性。
- [ ] 异常值处理前后结果均保留。
- [ ] 真实极端行情没有被未经核验地删除。
- [ ] 不把相关性解释为因果性。
- [ ] 报告可以由脚本重新生成。
- [ ] 尚未学习、补写或重新生成的每日课程严格使用 [每日学习内容标准模板](../../DAILY-LEARNING-TEMPLATE.md)。
- [ ] 数学内容使用 LaTeX：行内公式使用 `\( ... \)`，独立公式使用 `\[ ... \]`。

## 本周最终成果

```text
notebooks/week07_day07_return_distribution_project.ipynb
src/statistics.py
src/data_quality.py
reports/week07_return_distribution_report.md
reports/tables/week07_summary_statistics.csv
reports/tables/week07_correlation_matrix.csv
reports/tables/week07_outlier_review.csv
```
