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


# 所有输出文件统一写入该目录；目录整体被 .gitignore 排除，不参与提交。
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"


@dataclass(frozen=True)
class Config:
    momentum_window: int = 20
    volatility_window: int = 20
    liquidity_window: int = 20
    flow_window: int = 5
    corr_window: int = 60

    alpha: float = 1.0
    beta: float = 1.0
    gamma: float = 1.5

    # 金融距离权重。估值距离已经接入历史 PE/PB/PS。
    distance_w_corr: float = 0.40
    distance_w_sector: float = 0.15
    distance_w_factor: float = 0.25
    distance_w_valuation: float = 0.20
    min_distance: float = 0.05

    # 估值数据允许使用最近一个历史值，但不能向未来取值。
    valuation_max_staleness_days: int = 10
    valuation_min_coverage: float = 0.60

    attraction_w_momentum: float = 0.35
    attraction_w_flow: float = 0.35
    attraction_w_liquidity: float = 0.15
    attraction_w_volatility: float = -0.15
    # 估值越便宜，吸引力越高。设为 0 可只把估值用于“距离”。
    attraction_w_valuation: float = 0.15

    top_n: int = 3
    min_cross_section: int = 5
    impact_lambda: float = 1.0
