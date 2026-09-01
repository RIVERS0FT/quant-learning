from __future__ import annotations

from dataclasses import dataclass
import re

import pandas as pd


@dataclass(frozen=True)
class TaxonomyResult:
    sector_l1: str
    sector_l2: str
    rule: str


CANONICAL_L1 = (
    "Technology",
    "Communication",
    "Financials",
    "Healthcare",
    "Consumer",
    "Industrials",
    "Energy",
    "Materials",
    "Utilities",
    "RealEstate",
    "Transportation",
    "Agriculture",
    "Other",
)


# Ordered from specific to general. Each pattern is searched against
# "source_sector | source_industry" after normalization.
_RULES: tuple[tuple[str, str, str], ...] = (
    (r"半导体|semiconductor|chip|integrated circuit", "Technology", "Semiconductor"),
    (r"软件|software|application|saas|database|programming", "Technology", "Software"),
    (r"互联网服务|internet service|internet information|cloud|data processing", "Technology", "Internet"),
    (r"计算机设备|消费电子|电子元件|电子设备|光学光电子|元件|computer|hardware|electronic components|computer manufacturing", "Technology", "Hardware"),
    (r"电池|battery", "Technology", "Battery"),
    (r"光伏|太阳能|solar|photovoltaic|风电设备|wind equipment", "Energy", "RenewableEnergy"),
    (r"通信服务|电信|telecommunication|telecom|wireless", "Communication", "Telecom"),
    (r"通信设备|communications equipment|radio and television transmitting", "Communication", "TelecomEquipment"),
    (r"传媒|媒体|出版|广播|电视|电影|游戏|广告|media|broadcast|publishing|movie|gaming|advertising", "Communication", "Media"),
    (r"银行|bank", "Financials", "Bank"),
    (r"证券|broker|investment banker|investment managers|securities", "Financials", "Broker"),
    (r"保险|insurance", "Financials", "Insurance"),
    (r"金融科技|fintech", "Financials", "FinTech"),
    (r"多元金融|finance|financial services|consumer finance", "Financials", "DiversifiedFinancials"),
    (r"生物制品|生物科技|biotech|biotechnology", "Healthcare", "Biotech"),
    (r"医疗器械|medical device|medical specialties|medical/dental instruments", "Healthcare", "MedicalDevice"),
    (r"医疗服务|医院|healthcare service|hospital|medical nursing", "Healthcare", "HealthcareService"),
    (r"中药|化学制药|制药|医药|pharmaceutical|major pharmaceuticals", "Healthcare", "Pharma"),
    (r"白酒|食品|饮料|乳品|food|beverage|soft drinks|packaged foods", "Consumer", "FoodBeverage"),
    (r"零售|百货|超市|电商|retail|catalog/specialty distribution", "Consumer", "Retail"),
    (r"汽车|乘用车|商用车|auto|automotive|motor vehicles", "Consumer", "Auto"),
    (r"家电|appliance", "Consumer", "HomeAppliance"),
    (r"纺织|服装|家居|家具|珠宝|personal services|apparel|home furnishings|consumer specialties", "Consumer", "ConsumerDurables"),
    (r"旅游|酒店|餐饮|美容|休闲|entertainment|hotels|restaurants|recreation", "Consumer", "Leisure"),
    (r"航天|航空装备|军工|aerospace|defense", "Industrials", "Defense"),
    (r"工程建设|建筑|construction|building operators|engineering", "Industrials", "Construction"),
    (r"专用设备|通用设备|工程机械|机械|machine|machinery|industrial machinery", "Industrials", "Machinery"),
    (r"电机|电网设备|电气设备|electrical products|electrical equipment", "Industrials", "ElectricalEquipment"),
    (r"商业服务|business services|professional services|commercial services", "Industrials", "BusinessServices"),
    (r"天然气配送|natural gas distribution|gas distribution", "Utilities", "Utilities"),
    (r"石油|油气|天然气|oil|gas|petroleum", "Energy", "OilGas"),
    (r"煤炭|coal", "Energy", "Coal"),
    (r"新能源|renewable energy|alternative energy", "Energy", "RenewableEnergy"),
    (r"有色|小金属|贵金属|钢铁|metal|steel|aluminum|copper|mining", "Materials", "Metals"),
    (r"化工|化学|chemical", "Materials", "Chemicals"),
    (r"水泥|建材|玻璃|building materials|forest products|paper", "Materials", "BuildingMaterials"),
    (r"电力|水务|燃气|环保|public utilities|electric utilities|water supply", "Utilities", "Utilities"),
    (r"房地产|real estate|reit", "RealEstate", "RealEstate"),
    (r"物流|快递|logistics|trucking|air freight", "Transportation", "Logistics"),
    (r"航空机场|铁路|公路|航运|港口|transportation|railroads|marine transportation|air transportation", "Transportation", "Transportation"),
    (r"农牧|农业|种植|养殖|渔业|agriculture|farming|livestock", "Agriculture", "Agriculture"),
)


_US_SECTOR_FALLBACK = {
    "technology": ("Technology", "TechnologyOther"),
    "finance": ("Financials", "DiversifiedFinancials"),
    "financials": ("Financials", "DiversifiedFinancials"),
    "health care": ("Healthcare", "HealthcareOther"),
    "healthcare": ("Healthcare", "HealthcareOther"),
    "consumer discretionary": ("Consumer", "ConsumerOther"),
    "consumer staples": ("Consumer", "ConsumerOther"),
    "consumer services": ("Consumer", "ConsumerOther"),
    "consumer durables": ("Consumer", "ConsumerDurables"),
    "consumer non-durables": ("Consumer", "ConsumerOther"),
    "capital goods": ("Industrials", "IndustrialsOther"),
    "industrials": ("Industrials", "IndustrialsOther"),
    "energy": ("Energy", "EnergyOther"),
    "basic industries": ("Materials", "MaterialsOther"),
    "basic materials": ("Materials", "MaterialsOther"),
    "public utilities": ("Utilities", "Utilities"),
    "utilities": ("Utilities", "Utilities"),
    "real estate": ("RealEstate", "RealEstate"),
    "transportation": ("Transportation", "Transportation"),
    "telecommunications": ("Communication", "Telecom"),
    "communication services": ("Communication", "CommunicationOther"),
    "miscellaneous": ("Other", "Other"),
}


def _norm(value: object) -> str:
    text = "" if value is None else str(value)
    text = text.strip().lower()
    return re.sub(r"\s+", " ", text)


def map_to_unified(
    market: str,
    source_sector: object = "",
    source_industry: object = "",
) -> TaxonomyResult:
    sector = _norm(source_sector)
    industry = _norm(source_industry)
    haystack = f"{sector} | {industry}"

    for pattern, l1, l2 in _RULES:
        if re.search(pattern, haystack, flags=re.IGNORECASE):
            return TaxonomyResult(l1, l2, pattern)

    if str(market).upper() == "US" and sector in _US_SECTOR_FALLBACK:
        l1, l2 = _US_SECTOR_FALLBACK[sector]
        return TaxonomyResult(l1, l2, f"us-sector:{sector}")

    cn_fallback = (
        ("电子", "Technology", "Hardware"),
        ("计算机", "Technology", "Software"),
        ("通信", "Communication", "CommunicationOther"),
        ("非银金融", "Financials", "DiversifiedFinancials"),
        ("医药生物", "Healthcare", "HealthcareOther"),
        ("食品饮料", "Consumer", "FoodBeverage"),
        ("家用电器", "Consumer", "HomeAppliance"),
        ("机械设备", "Industrials", "Machinery"),
        ("公用事业", "Utilities", "Utilities"),
        ("交通运输", "Transportation", "Transportation"),
        ("基础化工", "Materials", "Chemicals"),
        ("建筑材料", "Materials", "BuildingMaterials"),
        ("农林牧渔", "Agriculture", "Agriculture"),
    )
    for needle, l1, l2 in cn_fallback:
        if needle in haystack:
            return TaxonomyResult(l1, l2, f"cn-fallback:{needle}")

    return TaxonomyResult("Other", "Other", "unmapped")


def apply_unified_taxonomy(master: pd.DataFrame) -> pd.DataFrame:
    df = master.copy()
    for col in ["source_sector", "source_industry"]:
        if col not in df.columns:
            df[col] = ""

    mapped = [
        map_to_unified(row.market, row.source_sector, row.source_industry)
        for row in df[["market", "source_sector", "source_industry"]].itertuples(index=False)
    ]
    df["sector_l1"] = [x.sector_l1 for x in mapped]
    df["sector_l2"] = [x.sector_l2 for x in mapped]
    df["taxonomy_rule"] = [x.rule for x in mapped]
    return df


def taxonomy_coverage(master: pd.DataFrame) -> pd.DataFrame:
    if "sector_l1" not in master.columns:
        master = apply_unified_taxonomy(master)
    return (
        master.groupby(["market", "sector_l1", "sector_l2"], dropna=False)
        .size()
        .rename("securities")
        .reset_index()
        .sort_values(["market", "securities"], ascending=[True, False])
    )
