# 个人量化研究学习路线

> 目标：用 36 个月完成从 Python 与金融数据基础，到 A 股研究、因子模型、机器学习、组合管理、模拟实盘、Agent 研究系统和个人量化平台的完整能力建设。

## 仓库结构

```text
Quant/
├── README.md
├── DAILY-LEARNING-TEMPLATE.md
├── stage-01-python-numpy-financial-data/
│   ├── README.md
│   ├── week-01-python-environment-basics/
│   │   ├── README.md
│   │   ├── day-01-python-environment.md
│   │   └── ...
│   └── ...
├── stage-02-a-share-data-backtesting/
│   ├── README.md
│   └── week-01-data-sources-field-dictionary-calendar/
│       ├── README.md
│       └── ...
└── stage-12-personal-quant-platform/
    ├── README.md
    ├── week-01/
    │   ├── README.md
    │   └── ...
    └── week-12/
        └── README.md
```

## 36 个月阶段路线

| 阶段 | 时间 | 主题 | 入口 |
|---|---:|---|---|
| 01 | 第 1—3 个月 | Python、NumPy 与金融数据基础 | [进入](stage-01-python-numpy-financial-data/) |
| 02 | 第 4—6 个月 | A 股数据处理与日频回测系统 | [进入](stage-02-a-share-data-backtesting/) |
| 03 | 第 7—9 个月 | 统计检验与因子研究 | [进入](stage-03-statistical-testing-factor-research/) |
| 04 | 第 10—12 个月 | 多因子组合与完整研究项目 | [进入](stage-04-multifactor-portfolio-project/) |
| 05 | 第 13—15 个月 | 机器学习量化基础 | [进入](stage-05-machine-learning-quant-basics/) |
| 06 | 第 16—18 个月 | 截面选股模型与滚动训练 | [进入](stage-06-cross-sectional-model-rolling-training/) |
| 07 | 第 19—21 个月 | 组合优化与风险模型 | [进入](stage-07-portfolio-optimization-risk-model/) |
| 08 | 第 22—24 个月 | 模拟交易与小资金实盘验证 | [进入](stage-08-paper-and-small-capital-trading/) |
| 09 | 第 25—27 个月 | Agent 量化研究系统 | [进入](stage-09-agent-quant-research-system/) |
| 10 | 第 28—30 个月 | 自动实验、审计与策略淘汰机制 | [进入](stage-10-automated-experiment-audit-elimination/) |
| 11 | 第 31—33 个月 | 多策略平台与容量管理 | [进入](stage-11-multi-strategy-platform-capacity/) |
| 12 | 第 34—36 个月 | 个人量化研究平台定型 | [进入](stage-12-personal-quant-platform/) |

## 阶段周数规则

1. 每个阶段固定为 12 周。
2. 每月按 4 个教学周规划，因此每个三个月阶段共 12 周。
3. 第 12 周同时承担阶段项目、验收、总结和下一阶段准备，不另设第 13 周。

## 第 1—3 个月周学习路线

| 周次 | 主题 | 周成果 |
|---:|---|---|
| 第 1 周 | Python 开发环境与基础语法 | 创建研究仓库并编写第一个收益率函数 |
| 第 2 周 | NumPy 与单资产收益率 | 完成收益率计算模块及单元测试 |
| 第 3 周 | NumPy 二维数组与多资产计算 | 完成多股票收益率和波动率程序 |
| 第 4 周 | pandas 基础与金融时间序列 | 整理标准行情表 |
| 第 5 周 | pandas 分组与滚动计算 | 计算收益、均线、波动率与截面排名 |
| 第 6 周 | SQL、DuckDB 与数据存储 | 建立本地行情数据库 |
| 第 7 周 | 描述统计与收益分布 | 完成收益分布分析报告 |
| 第 8 周 | 概率、抽样与假设检验 | 完成简单事件研究 |
| 第 9 周 | 策略绩效指标 | 编写统一绩效评价模块 |
| 第 10 周 | A 股价格、复权与公司行为 | 比较不同复权方式的收益差异 |
| 第 11 周 | A 股股票池与交易规则 | 建立股票可交易状态字段 |
| 第 12 周 | 数据质量与阶段项目 | 完成数据质量报告和阶段总结 |

## 学习执行规则

1. 每周以一个可验证成果结束。
2. 每日课程必须严格按照 [每日学习内容标准模板](DAILY-LEARNING-TEMPLATE.md) 输出，一级章节固定为“今日新名词解释、今日学习目标、核心知识教学、综合案例、常见错误、今日总结”六部分。
3. 不得增加、删除、合并或调换每日课程的六个一级章节；如果某次课程无法严格按照模板生成，必须在输出课程前向学习者说明原因并确认。
4. 每日课程必须在“今日学习目标”之前设置“今日新名词解释”；当天首次出现的新名词分别用一句话解释，已经解释过的名词除非需要深化，否则不重复解释。
5. 第三部分中的每个核心概念必须依次包含“概念解释、数学解释、Python 代码、量化应用”。
6. 第四部分必须解释第三部分各概念之间的关系，给出综合使用场景和示例 Python 代码。
7. 所有研究明确数据口径、时间对齐、复权方式与交易成本。
8. 数学内容使用 LaTeX：行内公式使用 `\( ... \)`，独立公式使用 `\[ ... \]`；数学证明和公式推导必须逐行展开。
9. 每日课程文件直接保存在对应周目录，不再创建 `days/` 中间目录。
10. 每进行一天的学习，都将当天课程保存到项目对应周目录。
11. 每周最后一天完成测试、复盘与 Git 提交。
12. 每个阶段第 12 周必须完成阶段项目、验收清单和阶段总结。

## 当前阶段

从 [阶段 01](stage-01-python-numpy-financial-data/) 开始。
