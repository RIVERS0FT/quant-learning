# quant-learning

个人量化学习与 A 股策略实验仓库。数据源以 AkShare（东方财富/新浪）为主，
代码在 `code/`，课程笔记在 `learning/`。

## 目录结构

```
quant-learning/
├── .venv/                       # 本地虚拟环境（Python 3.14）
├── code/
│   ├── stock_capital_migration/ # 股票资金迁移模型（包，见下）
│   ├── maotai.py                # 贵州茅台单资产回测（新浪日线）
│   ├── maotai_multi_strategy.py # 茅台多策略对比
│   ├── maotai_multi_strategy_momentum.py  # 茅台多策略+动量窗口
│   ├── outputs/                 # 所有脚本输出（gitignore，不入库）
│   └── data/                    # 本地市场数据缓存（gitignore，不入库）
└── learning/                    # Python/NumPy/Pandas 金融数据课程笔记
```

## 环境

- Windows + PowerShell，Python 3.14（`.venv`）
- 关键依赖版本（对兼容性敏感）：akshare 1.18.91、pandas 3.0.5、numpy 2.5.2、matplotlib
- 运行方式：仓库根目录下 `.venv\Scripts\python.exe ...`，或在 `code/` 下 `..\.venv\Scripts\python.exe -m <模块>`

## 股票资金迁移模型（code/stock_capital_migration/）

把股票视为"城市"、资金视为"人口"，用 Gravity Model 推断资金从股票 i 向股票 j 的迁移：

```
Flow(i -> j) ∝ OutflowBudget_i^alpha × Attractiveness_j^beta / Distance_ij^gamma
```

无法直接观察真实 A→B 流向，因此用"主力净流出"作为源端可迁移预算，
由金融距离（相关性/行业/因子/估值）和目标吸引力（动量/资金流/流动性/低波动/便宜度）
决定推断去向。估值用 `merge_asof backward` 对齐，不引入未来数据。

### 模块结构

| 模块 | 职责 |
|---|---|
| `config.py` | 默认股票池（10 只蓝筹）、Config 参数、输出目录 |
| `data.py` | AkShare 行情/资金流/历史估值获取，含东财限流重试 |
| `features.py` | 动量/波动/流动性/资金流强度/估值标准分 |
| `model.py` | 金融距离、引力迁移矩阵、截面快照 |
| `backtest.py` | Rank IC 与 Top-N 组合回测 |
| `report.py` | CSV/PNG 落盘与终端摘要 |
| `research.py` | 研究增强版：本地缓存、1/3/5/10/20 日多周期 IC、A-G 七组消融实验 |

### 用法（在 `code/` 目录下）

```powershell
# 基线模型
..\.venv\Scripts\python.exe -m stock_capital_migration [--top-n 3] [--no-plot] [--output-dir DIR]

# 研究版（缓存 + 多周期 IC + 消融）
..\.venv\Scripts\python.exe -m stock_capital_migration.research [--offline] [--refresh-cache] [--skip-ablation]
```

输出统一写入 `code/outputs/`（已 gitignore）；研究版数据缓存写入 `code/data/`（已 gitignore），
联网运行时增量累积——资金流接口窗口只有约 120 个交易日，缓存是把回测期拉长的唯一办法。

### 已知限制（重要）

1. **有效回测期远短于请求区间**：`stock_individual_fund_flow` 只返回近期约 120 个交易日，
   前段会被静默丢弃（基线版无提示；研究版有 coverage 报告）。
2. **横截面只有 10 只手选蓝筹**，存在幸存者偏差；IC 在该样本量下无统计意义。
3. **引力结构未证明有增量**：当日主力净流入同时进入源端预算与目标吸引力，
   需看 research 的消融实验（A-G 组）对比纯因子排序。
4. **回测不可交易**：无手续费/滑点/T+1/涨跌停约束，日频调仓换手未计入成本。
5. 2026-08-31 实测：基线平均 Rank IC ≈ -0.006，Top-3 跑输等权，当前无预测力。

## 输出与缓存约定

- 所有脚本生成物（CSV/PNG）一律写入 `code/outputs/`，不散落在脚本目录
- 市场数据缓存写入 `code/data/`
- `code/outputs/`、`code/data/`、`__pycache__/` 均已在 `.gitignore` 中排除

## 数据源注意事项

- 东财 `push2his` 端点存在**突发限流**：连续请求会触发 60 秒级"直接断连"封锁窗，
  `data.py` 已内置重试+退避+限速（5 次重试、5s 起步、0.8s 间隔）；仍失败时等几分钟再跑
- 本机若开着系统代理（如 127.0.0.1:7897）且代理不转发东财，需设置
  `$env:NO_PROXY='eastmoney.com'` 后再运行
- 控制台中文乱码时设置 `$env:PYTHONIOENCODING='utf-8'`
