# quant-learning

个人量化学习与 A 股策略实验仓库。数据源以 AkShare（东方财富/新浪）为主，
代码在 `code/`，课程笔记在 `learning/`。

## 目录结构

```
quant-learning/
├── .venv/                       # 本地虚拟环境（Python 3.14）
├── code/
│   ├── stock_capital_migration/ # 股票资本迁移模型（包，见下）
│   ├── maotai.py                # 贵州茅台单资产回测（新浪日线）
│   ├── maotai_multi_strategy.py # 茅台多策略对比
│   ├── maotai_multi_strategy_momentum.py  # 茅台多策略+动量窗口
│   ├── outputs/                 # 所有脚本输出（gitignore，不入库）
│   └── data/                    # 本地市场数据缓存（gitignore，不入库）
└── learning/                    # Python/NumPy/Pandas 金融数据课程笔记
```

## 环境

- Windows + PowerShell，Python 3.14（`.venv`）
- 关键依赖版本：akshare 1.18.91、pandas 3.0.5、numpy 2.5.2、matplotlib
- 运行方式：仓库根目录下 `.venv\Scripts\python.exe ...`，或在 `code/` 下 `..\.venv\Scripts\python.exe -m <模块>`

## 股票资本迁移模型（code/stock_capital_migration/）

把股票视为“城市”、资本视为“人口”。当前模型不再把主力净流出当作必需的源端预算，而是先从价格与成交状态估计每只股票的资本供给与需求：

```
CapitalSupply_i = f(收益、动量、相对成交强度、价格冲击[, 主力资金辅助])
CapitalDemand_j = f(收益、动量、相对成交强度、价格冲击、估值[, 主力资金辅助])
```

再构造股票之间的 Gravity 迁移先验：

```
Prior(i -> j) ∝ Attractiveness_j^beta / Distance_ij^gamma
```

其中金融距离综合收益相关性、行业、状态因子和历史估值。最后使用 Sinkhorn 最优传输求完整股票到股票迁移矩阵 `F_ij`：

```
sum_j F_ij = CapitalSupply_i
sum_i F_ij = CapitalDemand_j
F_ij >= 0
F_ii = 0
```

每日推断迁移总量默认设为股票池当日总成交额的 5%。这是模型尺度参数，不能解释成真实可观察的 A→B 成交金额。

主力资金现在是**可选辅助信息**：默认完全不请求、不使用；只有显式传入 `--use-main-flow` 时，才参与供需特征和迁移总量的小比例校准。因此模型可以只依赖行情、成交和估值运行。

历史估值继续使用 `merge_asof(direction="backward")` 对齐，历史时点只读取当日或更早数据，避免未来数据泄漏。

### 模块结构

| 模块 | 职责 |
|---|---|
| `config.py` | 默认股票池、供需/距离/OT 参数、数据与输出目录 |
| `data.py` | AkShare 行情、历史估值、本地增量缓存；主力资金为可选辅助源 |
| `features.py` | 收益/动量/波动/成交强度/价格冲击/估值与资本供需特征 |
| `model.py` | 金融距离、Gravity 先验、Sinkhorn OT、完整 `F_ij` 迁移矩阵 |
| `backtest.py` | 1/3/5/10/20 日 Rank IC、Top-N、节点信号 A-G 消融 |
| `report.py` | 迁移矩阵、关键边、节点快照、IC/消融结果落盘与终端摘要 |

### 用法（在 `code/` 目录下）

```powershell
# 默认：不使用主力资金
..\.venv\Scripts\python.exe -m stock_capital_migration

# 只用本地行情/估值缓存
..\.venv\Scripts\python.exe -m stock_capital_migration --offline

# 可选：把主力净流入作为辅助信息
..\.venv\Scripts\python.exe -m stock_capital_migration --use-main-flow

# 快速运行，跳过节点信号消融
..\.venv\Scripts\python.exe -m stock_capital_migration --skip-ablation
```

主要输出统一写入 `code/outputs/`：

```
stock_capital_migration_matrix.csv          # 完整 source × target 迁移矩阵
stock_capital_migration_edges.csv           # 最重要的股票 -> 股票迁移边
stock_capital_migration_snapshot.csv        # 节点资本供需/净迁移
stock_capital_migration_predictions.csv
stock_capital_migration_multi_ic.csv
stock_capital_migration_multi_ic_summary.csv
stock_capital_migration_ablation.csv
stock_capital_migration_ablation_daily_ic.csv
stock_capital_migration_ablation_portfolio.csv
stock_capital_migration_valuation.csv
stock_capital_migration_data_coverage.csv
```

### 已知限制（重要）

1. **`F_ij` 仍是潜变量推断，不是真实可观察资金流水**。当前最重要的后续工作是接入 ETF/基金持仓变化等数据，对 A→B pair topology 做监督或事后验证。
2. **节点 Rank IC 不能证明迁移路径正确**。由于 OT 明确约束供给与需求边际，节点净迁移检验主要评价供需状态；股票对之间的路径需要 pair 级标签验证。
3. **迁移总量存在尺度假设**。默认使用股票池成交额的 5%，适合比较相对路径和份额，不宜把绝对金额直接当成真实资金流。
4. **横截面目前只有 10 只手选股票**，存在样本量和幸存者偏差；应扩展到沪深 300/中证 500 后再评价稳定性。
5. **回测仍不是完整可交易系统**：尚未加入手续费、滑点、T+1、涨跌停和容量约束。

## 输出与缓存约定

- 所有脚本生成物（CSV/PNG）一律写入 `code/outputs/`
- 市场数据缓存写入 `code/data/`
- `code/outputs/`、`code/data/`、`__pycache__/` 均已在 `.gitignore` 中排除
- 默认模式不会请求主力资金接口；`--use-main-flow` 开启后才读写 `code/data/fund_flow/`

## 数据源注意事项

- 东财端点存在突发限流，`data.py` 已内置重试+退避+限速；估值或可选主力资金请求失败时会自动降级
- 本机若开着系统代理（如 127.0.0.1:7897）且代理不转发东财，可设置 `$env:NO_PROXY='eastmoney.com'` 后重跑
- 控制台中文乱码时设置 `$env:PYTHONIOENCODING='utf-8'`
