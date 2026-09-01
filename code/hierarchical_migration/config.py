from dataclasses import dataclass

CORE_FEATURES = (
    "return_1d_z",
    "momentum_z",
    "volatility_z",
    "liquidity_z",
    "valuation_cheapness_z",
)


@dataclass(frozen=True)
class HierarchicalConfig:
    momentum_window: int = 20
    volatility_window: int = 20
    liquidity_window: int = 20
    min_history: int = 20
    beta: float = 1.0
    gamma: float = 1.5
    min_distance: float = 0.10

    inferred_supply_fraction: float = 0.03
    inferred_demand_fraction: float = 0.03
    supply_w_negative_return: float = 0.60
    supply_w_volatility: float = 0.25
    supply_w_negative_momentum: float = 0.15
    demand_w_return: float = 0.30
    demand_w_momentum: float = 0.35
    demand_w_liquidity: float = 0.15
    demand_w_valuation: float = 0.20

    same_market_friction: float = 0.35
    cross_market_friction: float = 0.80
    same_sector_friction: float = 0.20
    cross_sector_friction: float = 0.55

    sector_top_k: int = 5
    stock_top_k: int = 30
    stock_block_size: int = 256
    min_edge_probability: float = 0.0

    include_outside: bool = False
    outside_name: str = "OUTSIDE"
    outside_attractiveness: float = 0.35
    outside_distance: float = 0.90
