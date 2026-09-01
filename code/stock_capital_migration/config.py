# -*- coding: utf-8 -*-
"""模型配置：默认股票池、参数与输出目录。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_UNIVERSE: dict[str, dict[str, str]] = {
    "600519": {"name": "贵州茅台", "sector": "白酒"},
    "600036": {"name": "招商银行", "sector": "银行"},
    "600030": {"name": "中信证券", "sector": "证券"},
    "600584": {"name": "长电科技", "sector": "半导体"},
    "603986": {"name": "兆易创新", "sector": "半导体"},
    "300750": {"name": "宁德时代", "sector": "新能源"},
    "000333": {"name": "美的集团", "sector": "家电"},
    "002230": {"name": "科大讯飞", "sector": "AI"},
    "601857": {"name": "中国石油", "sector": "能源"},
    "600276": {"name": "恒瑞医药", "sector": "医药"},
}

VALUATION_RATIO_COLS = ["pe_ttm", "pb", "ps_ttm"]
VALUATION_DATA_COLS = [
    "valuation_date",
    "pe_ttm",
    "pb",
    "ps_ttm",
    "total_market_cap",
    "float_market_cap",
]
HORIZONS = (1, 3, 5, 10, 20)
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"


@dataclass(frozen=True)
class Config:
    momentum_window: int = 20
    volatility_window: int = 20
    liquidity_window: int = 20
    flow_window: int = 5
    corr_window: int = 60

    # 主力资金只作为可选辅助数据；默认关闭，模型可只靠价格/成交/估值运行。
    use_auxiliary_main_flow: bool = False

    # 原 Gravity 指数：alpha/beta 同时控制供给/需求边际的集中度，
    # beta 也控制目标吸引力对迁移先验的影响；gamma 控制金融距离衰减。
    alpha: float = 1.0
    beta: float = 1.0
    gamma: float = 1.5

    distance_w_corr: float = 0.40
    distance_w_sector: float = 0.15
    distance_w_factor: float = 0.25
    distance_w_valuation: float = 0.20
    min_distance: float = 0.05

    valuation_max_staleness_days: int = 10
    valuation_min_coverage: float = 0.60

    attraction_w_momentum: float = 0.35
    attraction_w_flow: float = 0.35
    attraction_w_liquidity: float = 0.15
    attraction_w_volatility: float = -0.15
    attraction_w_valuation: float = 0.15

    # 资本供给 O_i：弱收益/弱动量、高活跃、高冲击表示更强的潜在迁出压力。
    supply_w_return: float = 0.45
    supply_w_momentum: float = 0.20
    supply_w_turnover: float = 0.25
    supply_w_impact: float = 0.10
    supply_w_aux_flow: float = 0.15

    # 资本需求 I_j：强收益/强动量/高活跃、较低冲击、较便宜估值表示更强迁入需求。
    demand_w_return: float = 0.35
    demand_w_momentum: float = 0.25
    demand_w_turnover: float = 0.20
    demand_w_impact: float = 0.10
    demand_w_valuation: float = 0.10
    demand_w_aux_flow: float = 0.15

    # 每日可迁移资本总量：默认取股票池当日成交额的 5%。
    # 这是推断规模参数，不应被解释为真实可观察的 A->B 成交金额。
    transport_mass_fraction: float = 0.05
    # 开启主力资金辅助时，可用其净流入/流出规模校准总迁移量；默认仅小比例融合。
    transport_aux_mass_blend: float = 0.20
    # 边际分布加入均匀成分并限制单节点份额，保证禁止自迁移时 OT 问题可行。
    transport_uniform_mix: float = 0.05
    transport_max_node_share: float = 0.45
    transport_temperature: float = 1.0
    sinkhorn_max_iter: int = 1000
    sinkhorn_tol: float = 1e-8

    top_n: int = 3
    min_cross_section: int = 5
