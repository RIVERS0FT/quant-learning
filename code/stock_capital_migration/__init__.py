# -*- coding: utf-8 -*-
"""Stock Capital Migration Model（股票资本迁移模型）。

核心思想：把股票视为节点、资本视为可迁移质量。模型先从价格、成交活跃度、
动量、价格冲击与估值估计每只股票的资本供给 O_i 和资本需求 I_j，再构造：

    Prior(i -> j) ∝ Attractiveness_j^beta / D_ij^gamma

最后使用 Sinkhorn 最优传输，在禁止自迁移的条件下求完整股票到股票矩阵 F_ij：

    sum_j F_ij = O_i
    sum_i F_ij = I_j
    F_ij >= 0

主力资金不是必需输入。默认不请求、不使用；只有 CLI 显式传入 --use-main-flow
时才作为辅助特征和迁移规模校准。

运行（在 code/ 目录下）：
    python -m stock_capital_migration
    python -m stock_capital_migration --offline --skip-ablation
    python -m stock_capital_migration --use-main-flow

主要输出：
- stock_capital_migration_matrix.csv：完整 source x target 预测矩阵
- stock_capital_migration_edges.csv：最重要的股票 -> 股票迁移边
- stock_capital_migration_snapshot.csv：节点资本供需与净迁移
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
from .features import (
    add_features,
    add_forward_returns,
    attraction_score,
    capital_demand_score,
    capital_supply_score,
)
from .model import (
    build_distance,
    build_snapshot,
    build_transport_marginals,
    flow_edges,
    gravity_flows,
    gravity_prior,
    optimal_transport_flows,
    sinkhorn_transport,
)
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
    "capital_demand_score",
    "capital_supply_score",
    "build_distance",
    "build_snapshot",
    "build_transport_marginals",
    "flow_edges",
    "gravity_flows",
    "gravity_prior",
    "optimal_transport_flows",
    "sinkhorn_transport",
    "load_data",
    "multi_horizon_test",
    "print_summary",
    "rank_ic",
    "run_ablation",
    "save_results",
    "summarize_ic",
    "valid_dates",
]
