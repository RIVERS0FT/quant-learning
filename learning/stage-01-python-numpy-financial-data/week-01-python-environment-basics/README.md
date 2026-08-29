# 第 1 周：Python 开发环境与基础语法

## 本周目标

完成从 Python 环境搭建到第一个可测试量化函数的完整入门流程。

本周结束时应能够：

- 创建并激活 Python 虚拟环境；
- 理解变量、数据类型、条件判断和循环；
- 编写带类型提示、文档字符串和参数校验的函数；
- 使用 `pathlib` 和异常处理安全读取文件；
- 使用 Git 检查、暂存和提交变化；
- 完成一个单资产收益率工具及基础测试。

## 本周学习安排

| 天 | 内容 | 预期产出 | 状态 |
|---:|---|---|---|
| 1 | Python 开发环境 | 可重复创建的项目环境 | [已完成](day-01-python-environment.md) |
| 2 | 变量与数据类型 | 股票基础数据脚本 | [已完成](day-02-variables-and-data-types.md) |
| 3 | 条件判断与循环 | 价格变化统计程序 | [已完成](day-03-conditionals-and-loops.md) |
| 4 | 函数 | 带校验的收益率函数 | [已完成](day-04-functions-and-return-calculation.md) |
| 5 | 异常、路径与文件 | 安全价格文件读取器 | [已完成](day-05-exceptions-paths-and-files.md) |
| 6 | Git 基础 | 首次规范提交 | [已完成](day-06-git-basics.md) |
| 7 | 综合项目 | 单资产收益率工具和测试 | [已完成](day-07-week-project.md) |

## 核心公式

简单收益率：

$$
R_t=\frac{P_t}{P_{t-1}}-1
$$

累计收益率：

$$
R_{cum}=\prod_{t=1}^{n}(1+R_t)-1
$$

## 核心成果

建立一个包含以下内容的基础量化研究项目：

```text
quant-research/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
├── src/
└── tests/
```

并完成：

- 价格文件读取；
- 简单收益率计算；
- 涨跌天数统计；
- 累计收益率计算；
- 输入校验和错误提示；
- 基础 `pytest` 测试。

## 每日入口

[查看第一周每日学习路径](README.md)

## 完成标准

- [x] 能独立创建、激活和退出虚拟环境；
- [x] 能解释基础 Python 数据类型；
- [x] 能使用条件和循环处理价格序列；
- [x] 能编写带参数校验的收益率函数；
- [x] 能安全读取价格文件并处理异常；
- [x] 能完成一次规范 Git 提交；
- [x] 综合项目通过基础单元测试。

## 每日学习路径

| 天 | 主题 | 学习与实践 | 当天输出 | 课程正文 |
|---:|---|---|---|---|
| 1 | Python 环境 | Python、虚拟环境、`pip`、编辑器和项目目录 | 可重复创建的项目环境 | [查看](day-01-python-environment.md) |
| 2 | 变量与数据类型 | 数值、字符串、布尔值、列表、元组、字典和类型转换 | 股票基础数据脚本 | [查看](day-02-variables-and-data-types.md) |
| 3 | 条件与循环 | `if`、`for`、`while`、`range`、`enumerate`、`zip` | 价格变化统计程序 | [查看](day-03-conditionals-and-loops.md) |
| 4 | 函数 | 参数、返回值、类型提示、文档字符串和输入校验 | 第一个收益率函数 | [查看](day-04-functions-and-return-calculation.md) |
| 5 | 异常与路径 | `try/except`、`pathlib`、上下文管理器和文件读写 | 安全价格文件读取器 | [查看](day-05-exceptions-paths-and-files.md) |
| 6 | Git 基础 | 工作区、暂存区、提交、差异检查和 `.gitignore` | 首次规范提交 | [查看](day-06-git-basics.md) |
| 7 | 综合项目 | 整合函数、文件输入、统计汇总、测试和 README | 单资产收益率工具 | [查看](day-07-week-project.md) |

## 本周核心公式

简单收益率：

$$
R_t=\frac{P_t}{P_{t-1}}-1
$$

累计收益率：

$$
R_{cum}=\prod_{t=1}^{n}(1+R_t)-1
$$

在无分红、拆股等公司行为时：

$$
R_{cum}=\frac{P_n}{P_0}-1
$$

## 完成状态

- [x] Python 环境与虚拟环境课程已完成；
- [x] Python 基础数据类型课程已完成；
- [x] 条件、循环与价格遍历课程已完成；
- [x] 收益率函数与参数校验课程已完成；
- [x] 异常、文件路径与读写课程已完成；
- [x] Git 基础与规范提交课程已完成；
- [x] 第一周综合项目与基础测试已完成。
