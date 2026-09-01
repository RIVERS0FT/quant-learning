# -*- coding: utf-8 -*-
"""Stock Capital Migration Model（股票资本迁移模型）

把股票视为“城市”、资金视为“人口”，使用 Gravity Model 推断资金从股票 i
向股票 j 的迁移：

    Flow(i -> j) ∝ Capital_i^alpha * Attractiveness_j^beta / D_ij^gamma

这里无法直接观察真实 A -> B，因此使用“主力净流出”作为源端可迁移资金预算，
再由金融距离和目标股票吸引力决定这部分资金的推断去向。

数据来源：
- AkShare stock_zh_a_hist：A 股日线
- AkShare stock_individual_fund_flow：个股主力资金流
- AkShare stock_value_em：历史 PE(TTM)、PB、PS、市值

估值数据按交易日向后对齐（merge_asof direction="backward"），因此任意历史时点
只使用该日或更早已经存在的估值记录，避免未来数据泄漏。

模块结构：
- config：默认股票池、参数、数据/输出目录
- data：数据获取与本地增量缓存（含东财限流重试）
- features：特征工程与多周期前瞻收益
- model：引力模型与迁移矩阵
- backtest：有效截面、多周期 Rank IC、Top-N 组合与消融实验
- report：结果落盘与摘要打印

运行（在 code/ 目录下）：
    python -m stock_capital_migration
    python -m stock_capital_migration --offline --skip-ablation
    python -m stock_capital_migration --refresh-cache

输出：
- 所有结果文件统一写入 code/outputs/（可用 --output-dir 覆盖）：
  stock_capital_migration_snapshot.csv
  stock_capital_migration_edges.csv
  stock_capital_migration_predictions.csv
  stock_capital_migration_multi_ic.csv
  stock_capital_migration_multi_ic_summary.csv
  stock_capital_migration_ablation.csv
  stock_capital_migration_ablation_daily_ic.csv
  stock_capital_migration_ablation_portfolio.csv
  stock_capital_migration_valuation.csv
  stock_capital_migration_data_coverage.csv
"""

from .backtest import (
    multi_horizon_test,
    rank_ic,
    run_ablation,
    summarize_ic,
    valid_dates,
)
from .config import (
    Config,
    DEFAULT_DATA_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_UNIVERSE,
    HORIZONS,
)
from .data import load_data
from .features import add_features, add_forward_returns, attraction_score
from .model import build_distance, build_snapshot, flow_edges, gravity_flows
from .report import print_summary, save_results

__all__ = [
    "Config",
    "DEFAULT_DATA_DIR",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_UNIVERSE",
    "HORIZONS",
    "add_features",
    "add_forward_returns",
    "attraction_score",
    "build_distance",
    "build_snapshot",
    "flow_edges",
    "gravity_flows",
    "load_data",
    "multi_horizon_test",
    "print_summary",
    "rank_ic",
    "run_ablation",
    "save_results",
    "summarize_ic",
    "valid_dates",
]
