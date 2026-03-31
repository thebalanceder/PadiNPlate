"""
Fertilizer Recommendations Node
===============================
Comprehensive fertilizer management system with cost-benefit analysis.

Features:
- Soil-based fertilizer recommendations
- Growth stage timing
- Cost comparison tools
- Organic vs synthetic options
- Malaysian subsidy integration
"""

import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Tuple, Any
from enum import Enum
import random

# =============================================================================
# DATA MODELS
# =============================================================================


class NutrientType(Enum):
    NITROGEN = "N"
    PHOSPHORUS = "P"
    POTASSIUM = "K"
    ZINC = "Zn"
    IRON = "Fe"
    SULFUR = "S"
    CALCIUM = "Ca"
    MAGNESIUM = "Mg"


class FertilizerType(Enum):
    UREA = "urea"
    NPK_COMPOUND = "npk"
    ORGANIC = "organic"
    FOLIAR = "foliar"
    SLOW_RELEASE = "slow_release"


@dataclass
class FertilizerProduct:
    """A fertilizer product with properties and pricing."""

    id: str
    name: str
    nutrient_content: Dict[str, float]  # e.g., {"N": 46, "P": 0, "K": 0}
    product_type: FertilizerType
    form: str = "granular"  # granular, liquid, powder
    solubility: str = "high"
    price_per_50kg: float = 0
    price_per_bag: float = 0
    bag_size_kg: float = 50
    manufacturer: str = ""
    available_subsidy: bool = False
    subsidy_per_50kg: float = 0
    local_suppliers: List[str] = field(default_factory=list)
    notes: str = ""

    @property
    def price_per_kg(self) -> float:
        return self.price_per_bag / self.bag_size_kg

    def get_nutrient_price(self, nutrient: str) -> float:
        """Get price per kg of specific nutrient."""
        content = self.nutrient_content.get(nutrient, 0)
        if content == 0:
            return float("inf")
        return (self.price_per_bag / self.bag_size_kg) / (content / 100)


@dataclass
class FertilizerApplication:
    """A single fertilizer application."""

    stage: str
    timing_days: int  # Days after sowing
    product: str
    rate_kg_ha: float
    nutrient_amounts: Dict[str, float] = field(default_factory=dict)
    cost_rm_ha: float = 0
    cost_after_subsidy_rm_ha: float = 0
    notes: str = ""
    method: str = "broadcast"  # broadcast, basal, foliar, side-dress


@dataclass
class FertilizerProgram:
    """Complete fertilizer program for a season."""

    variety: str
    target_yield_t_ha: float
    soil_n_status: str  # "very_low", "low", "medium", "high"
    soil_p_status: str = "medium"
    soil_k_status: str = "medium"
    applications: List[FertilizerApplication] = field(default_factory=list)
    total_n_kg_ha: float = 0
    total_p_kg_ha: float = 0
    total_k_kg_ha: float = 0
    total_cost_rm_ha: float = 0
    total_cost_after_subsidy_rm_ha: float = 0
    expected_yield_increase_t_ha: float = 0


@dataclass
class FertilizerComparison:
    """Comparison of different fertilizer strategies."""

    strategy_name: str
    program: FertilizerProgram
    cost_rm_ha: float
    cost_after_subsidy_rm_ha: float
    expected_yield_t_ha: float
    net_return_rm_ha: float
    roi_percent: float
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class SubsidyInfo:
    """Government subsidy information."""

    program_name: str
    provider: str  # KADA, MADA, Federal, etc.
    subsidy_per_unit: float
    unit: str  # per 50kg, per hectare, etc.
    max_claim_per_ha: float
    eligible_fertilizers: List[str] = field(default_factory=list)
    application_deadline: Optional[date] = None
    requirements: List[str] = field(default_factory=list)


# =============================================================================
# FERTILIZER DATABASE
# =============================================================================


class FertilizerDatabase:
    """Database of fertilizer products."""

    def __init__(self):
        self.products: Dict[str, FertilizerProduct] = {}
        self._initialize_products()

    def _initialize_products(self):
        """Initialize common fertilizers in Malaysia."""

        # Urea
        self.add_product(
            FertilizerProduct(
                id="UREA_46",
                name="Urea 46% N",
                nutrient_content={"N": 46},
                product_type=FertilizerType.UREA,
                price_per_50kg=90,
                price_per_bag=90,
                manufacturer="various",
                available_subsidy=True,
                subsidy_per_50kg=20,
                local_suppliers=[
                    "KADA Cooperative",
                    "MADA Cooperative",
                    "Local Agrovet",
                ],
            )
        )

        self.add_product(
            FertilizerProduct(
                id="UREA_GOLD",
                name="Urea Gold ( stabilizer)",
                nutrient_content={"N": 46},
                product_type=FertilizerType.SLOW_RELEASE,
                form="granular",
                solubility="slow",
                price_per_50kg=120,
                price_per_bag=120,
                manufacturer="SFCO",
                notes="Nitrogen stabilizer reduces volatilization loss",
            )
        )

        # NPK Compounds
        self.add_product(
            FertilizerProduct(
                id="NPK_151515",
                name="NPK 15-15-15",
                nutrient_content={"N": 15, "P": 15, "K": 15},
                product_type=FertilizerType.NPK_COMPOUND,
                price_per_50kg=105,
                price_per_bag=105,
                manufacturer="various",
                available_subsidy=True,
                subsidy_per_50kg=15,
                local_suppliers=["KADA", "MADA", "Agrovet"],
            )
        )

        self.add_product(
            FertilizerProduct(
                id="NPK_BLUE_12217",
                name="NPK Blue 12-12-17-2",
                nutrient_content={"N": 12, "P": 12, "K": 17, "S": 2},
                product_type=FertilizerType.NPK_COMPOUND,
                price_per_50kg=115,
                price_per_bag=115,
                manufacturer="various",
                available_subsidy=True,
                subsidy_per_50kg=15,
                local_suppliers=["KADA", "MADA", "Local Agrovet"],
                notes="Popular for rice panicle initiation stage",
            )
        )

        self.add_product(
            FertilizerProduct(
                id="NPK_201010",
                name="NPK 20-10-10",
                nutrient_content={"N": 20, "P": 10, "K": 10},
                product_type=FertilizerType.NPK_COMPOUND,
                price_per_50kg=95,
                price_per_bag=95,
                manufacturer="various",
                available_subsidy=True,
                subsidy_per_50kg=15,
            )
        )

        # DAP
        self.add_product(
            FertilizerProduct(
                id="DAP",
                name="DAP (Di-ammonium Phosphate)",
                nutrient_content={"N": 18, "P": 46},
                product_type=FertilizerType.NPK_COMPOUND,
                price_per_50kg=110,
                price_per_bag=110,
                manufacturer="various",
                available_subsidy=True,
                subsidy_per_50kg=15,
                notes="Good for basal phosphorus application",
            )
        )

        # MOP
        self.add_product(
            FertilizerProduct(
                id="MOP",
                name="Muriate of Potash (MOP)",
                nutrient_content={"K": 60},
                product_type=FertilizerType.NPK_COMPOUND,
                price_per_50kg=85,
                price_per_bag=85,
                manufacturer="various",
                available_subsidy=True,
                subsidy_per_50kg=15,
                notes="Primary potassium source for rice",
            )
        )

        # Organic fertilizers
        self.add_product(
            FertilizerProduct(
                id="CHICKEN_MANURE",
                name="Chicken Manure (Bulk)",
                nutrient_content={"N": 2.5, "P": 2.0, "K": 2.0},
                product_type=FertilizerType.ORGANIC,
                form="powder",
                price_per_50kg=25,
                price_per_bag=25,
                bag_size_kg=50,
                local_suppliers=["Local farms", "Poultry farms"],
                notes="Check quality - nutrient content varies",
            )
        )

        self.add_product(
            FertilizerProduct(
                id="COMPOST",
                name="Compost (General)",
                nutrient_content={"N": 1.5, "P": 1.0, "K": 1.5},
                product_type=FertilizerType.ORGANIC,
                form="powder",
                price_per_50kg=15,
                price_per_bag=15,
                bag_size_kg=50,
                notes="Improves soil organic matter",
            )
        )

        self.add_product(
            FertilizerProduct(
                id="FISH_EMULSION",
                name="Fish Emulsion (Liquid)",
                nutrient_content={"N": 5, "P": 2, "K": 2},
                product_type=FertilizerType.FOLIAR,
                form="liquid",
                price_per_bag=45,
                bag_size_kg=20,
                notes="Good for foliar feeding, quick absorption",
            )
        )

        # Zinc sulfate
        self.add_product(
            FertilizerProduct(
                id="ZINC_SULFATE",
                name="Zinc Sulfate 35% Zn",
                nutrient_content={"Zn": 35},
                product_type=FertilizerType.NPK_COMPOUND,
                price_per_50kg=150,
                price_per_bag=150,
                notes="Corrects zinc deficiency",
            )
        )

    def add_product(self, product: FertilizerProduct):
        """Add a fertilizer product."""
        self.products[product.id] = product

    def get_product(self, product_id: str) -> Optional[FertilizerProduct]:
        """Get a product by ID."""
        return self.products.get(product_id)

    def search_products(
        self,
        contains_nutrient: Optional[str] = None,
        min_n_percent: Optional[float] = None,
        product_type: Optional[FertilizerType] = None,
        organic_only: bool = False,
    ) -> List[FertilizerProduct]:
        """Search for products matching criteria."""
        results = []
        for p in self.products.values():
            if organic_only and p.product_type != FertilizerType.ORGANIC:
                continue
            if product_type and p.product_type != product_type:
                continue
            if min_n_percent and p.nutrient_content.get("N", 0) < min_n_percent:
                continue
            if contains_nutrient and contains_nutrient not in p.nutrient_content:
                continue
            results.append(p)
        return results


# =============================================================================
# SUBSIDY DATABASE
# =============================================================================


class SubsidyDatabase:
    """Database of fertilizer subsidies."""

    def __init__(self):
        self.subsidies: Dict[str, SubsidyInfo] = {}
        self._initialize_subsidies()

    def _initialize_subsidies(self):
        """Initialize Malaysian fertilizer subsidies."""

        self.subsidies["KADA_FERT"] = SubsidyInfo(
            program_name="KADA Fertilizer Subsidy",
            provider="KADA (Kedah)",
            eligible_fertilizers=["UREA_46", "NPK_151515", "NPK_BLUE_12217", "MOP"],
            subsidy_per_unit=20,
            unit="per 50kg",
            max_claim_per_ha=200,  # 10 bags per ha max
            application_deadline=date(2026, 6, 30),
            requirements=[
                "Registered with KADA",
                "Cultivating in KADA area",
                "Minimum 0.5 hectare",
            ],
        )

        self.subsidies["MADA_FERT"] = SubsidyInfo(
            program_name="MADA Fertilizer Subsidy",
            provider="MADA (Kedah)",
            eligible_fertilizers=["UREA_46", "NPK_151515", "NPK_BLUE_12217"],
            subsidy_per_unit=20,
            unit="per 50kg",
            max_claim_per_ha=200,
            application_deadline=date(2026, 6, 30),
            requirements=[
                "Registered with MADA",
                "Cultivating in MADA area",
                "Minimum 0.5 hectare",
            ],
        )

        self.subsidies["FEDERAL_FERT"] = SubsidyInfo(
            program_name="Federal Fertilizer Subsidy",
            provider="Federal Government",
            eligible_fertilizers=["UREA_46", "NPK_151515", "NPK_201010", "MOP"],
            subsidy_per_unit=15,
            unit="per 50kg",
            max_claim_per_ha=150,
            application_deadline=date(2026, 12, 31),
            requirements=[
                "Malaysian citizen",
                "Registered farmer",
                "Minimum 0.2 hectare",
            ],
        )


# =============================================================================
# FERTILIZER RECOMMENDATION ENGINE
# =============================================================================


class FertilizerRecommendationEngine:
    """Generate fertilizer recommendations."""

    def __init__(
        self,
        fertilizer_db: Optional[FertilizerDatabase] = None,
        subsidy_db: Optional[SubsidyDatabase] = None,
    ):
        self.fertilizer_db = fertilizer_db or FertilizerDatabase()
        self.subsidy_db = subsidy_db or SubsidyDatabase()

    def generate_recommendation(
        self,
        variety: str,
        target_yield_t_ha: float,
        soil_n_status: str,
        soil_p_status: str = "medium",
        soil_k_status: str = "medium",
        organic_preferred: bool = False,
    ) -> FertilizerProgram:
        """Generate fertilizer program based on inputs."""

        program = FertilizerProgram(
            variety=variety,
            target_yield_t_ha=target_yield_t_ha,
            soil_n_status=soil_n_status,
            soil_p_status=soil_p_status,
            soil_k_status=soil_k_status,
        )

        # Calculate nutrient requirements
        n_required = self._calculate_n_requirement(target_yield_t_ha, soil_n_status)
        p_required = self._calculate_p_requirement(target_yield_t_ha, soil_p_status)
        k_required = self._calculate_k_requirement(target_yield_t_ha, soil_k_status)

        # Generate applications
        if organic_preferred:
            applications = self._generate_organic_program(
                n_required, p_required, k_required
            )
        else:
            applications = self._generate_standard_program(
                n_required, p_required, k_required
            )

        program.applications = applications

        # Calculate totals
        for app in applications:
            program.total_n_kg_ha += app.nutrient_amounts.get("N", 0)
            program.total_p_kg_ha += app.nutrient_amounts.get("P", 0)
            program.total_k_kg_ha += app.nutrient_amounts.get("K", 0)
            program.total_cost_rm_ha += app.cost_rm_ha
            program.total_cost_after_subsidy_rm_ha += app.cost_after_subsidy_rm_ha

        # Expected yield increase
        program.expected_yield_increase_t_ha = self._estimate_yield_increase(
            target_yield_t_ha, soil_n_status, soil_p_status, soil_k_status
        )

        return program

    def _calculate_n_requirement(self, target_yield: float, soil_status: str) -> float:
        """Calculate N requirement in kg/ha."""
        base_n = target_yield * 20  # 20 kg N per ton of rice

        # Adjust for soil status
        multipliers = {"very_low": 1.4, "low": 1.2, "medium": 1.0, "high": 0.8}

        return base_n * multipliers.get(soil_status, 1.0)

    def _calculate_p_requirement(self, target_yield: float, soil_status: str) -> float:
        """Calculate P2O5 requirement in kg/ha."""
        base_p = target_yield * 8  # 8 kg P2O5 per ton

        multipliers = {"very_low": 1.5, "low": 1.2, "medium": 1.0, "high": 0.7}

        return base_p * multipliers.get(soil_status, 1.0)

    def _calculate_k_requirement(self, target_yield: float, soil_status: str) -> float:
        """Calculate K2O requirement in kg/ha."""
        base_k = target_yield * 15  # 15 kg K2O per ton

        multipliers = {"very_low": 1.4, "low": 1.2, "medium": 1.0, "high": 0.8}

        return base_k * multipliers.get(soil_status, 1.0)

    def _generate_standard_program(
        self, n_required: float, p_required: float, k_required: float
    ) -> List[FertilizerApplication]:
        """Generate standard synthetic fertilizer program."""
        applications = []

        # Basal application (Day 7 before transplanting or Day 0 for direct seeding)
        basal_n = n_required * 0.3
        basal_p = p_required * 1.0  # All P as basal
        basal_k = k_required * 0.5

        basal_app = FertilizerApplication(
            stage="Basal",
            timing_days=-7,
            product="NPK 15-15-15 + Urea",
            rate_kg_ha=300,
            nutrient_amounts={"N": basal_n, "P": basal_p, "K": basal_k},
            cost_rm_ha=315,
            cost_after_subsidy_rm_ha=270,
            method="broadcast and incorporate",
        )
        applications.append(basal_app)

        # First top-dressing - Tillering (21 DAP)
        td1_n = n_required * 0.4
        td1_k = k_required * 0.25

        td1_app = FertilizerApplication(
            stage="Tillering (First Top-dress)",
            timing_days=21,
            product="Urea 46%",
            rate_kg_ha=td1_n / 0.46,  # Convert N to urea
            nutrient_amounts={"N": td1_n, "K": td1_k},
            cost_rm_ha=(td1_n / 0.46) * 1.8,  # 90/50 = 1.8 per kg
            cost_after_subsidy_rm_ha=(td1_n / 0.46) * 1.4,
            method="broadcast",
        )
        applications.append(td1_app)

        # Second top-dressing - Panicle Initiation (45 DAP)
        td2_n = n_required * 0.3
        td2_k = k_required * 0.25

        td2_app = FertilizerApplication(
            stage="Panicle Initiation (Second Top-dress)",
            timing_days=45,
            product="NPK Blue 12-12-17-2",
            rate_kg_ha=(td2_n / 0.12 + td2_k / 0.17) / 2,  # Simplified
            nutrient_amounts={"N": td2_n, "K": td2_k},
            cost_rm_ha=115,
            cost_after_subsidy_rm_ha=100,
            method="broadcast",
        )
        applications.append(td2_app)

        return applications

    def _generate_organic_program(
        self, n_required: float, p_required: float, k_required: float
    ) -> List[FertilizerApplication]:
        """Generate organic fertilizer program."""
        applications = []

        # Basal - Compost during land prep
        basal_app = FertilizerApplication(
            stage="Land Preparation",
            timing_days=-14,
            product="Compost",
            rate_kg_ha=5000,  # 5 t/ha
            nutrient_amounts={
                "N": n_required * 0.2,
                "P": p_required * 0.5,
                "K": k_required * 0.3,
            },
            cost_rm_ha=1500,
            cost_after_subsidy_rm_ha=1500,
            notes="Organic matter improves soil health",
            method="incorporated during plowing",
        )
        applications.append(basal_app)

        # Top-dressing - Chicken manure
        td_app = FertilizerApplication(
            stage="Tillering",
            timing_days=21,
            product="Chicken Manure",
            rate_kg_ha=3000,  # 3 t/ha
            nutrient_amounts={"N": n_required * 0.4, "K": k_required * 0.3},
            cost_rm_ha=1500,
            cost_after_subsidy_rm_ha=1500,
            method="broadcast",
        )
        applications.append(td_app)

        # Supplement with urea if N still low
        if n_required * 0.4 > 50:  # If still need significant N
            supp_app = FertilizerApplication(
                stage="Panicle Initiation",
                timing_days=45,
                product="Urea 46% (supplement)",
                rate_kg_ha=50,
                nutrient_amounts={
                    "N": 23  # 46% of 50kg
                },
                cost_rm_ha=90,
                cost_after_subsidy_rm_ha=70,
                notes="Supplement to meet N requirement",
                method="broadcast",
            )
            applications.append(supp_app)

        return applications

    def _estimate_yield_increase(
        self, target_yield: float, n_status: str, p_status: str, k_status: str
    ) -> float:
        """Estimate potential yield increase."""
        base_increase = 0.5  # Baseline increase

        if n_status in ["very_low", "low"]:
            base_increase += 1.0
        elif n_status == "medium":
            base_increase += 0.5

        if p_status in ["very_low", "low"]:
            base_increase += 0.3

        if k_status in ["very_low", "low"]:
            base_increase += 0.2

        return base_increase

    def compare_strategies(
        self,
        variety: str,
        target_yield: float,
        soil_n_status: str,
        soil_p_status: str,
        soil_k_status: str,
        paddy_price_rm_t: float = 2000,
    ) -> List[FertilizerComparison]:
        """Compare different fertilizer strategies."""
        comparisons = []

        # Strategy 1: Standard synthetic
        std_program = self.generate_recommendation(
            variety, target_yield, soil_n_status, soil_p_status, soil_k_status
        )

        std_comparison = FertilizerComparison(
            strategy_name="Standard Synthetic",
            program=std_program,
            cost_rm_ha=std_program.total_cost_rm_ha,
            cost_after_subsidy_rm_ha=std_program.total_cost_after_subsidy_rm_ha,
            expected_yield_t_ha=target_yield + std_program.expected_yield_increase_t_ha,
            net_return_rm_ha=0,  # Calculated below
            roi_percent=0,
            pros=["Proven effectiveness", "Quick nutrient release", "Easy application"],
            cons=["Higher cost", "Environmental concerns"],
            recommendation="",
        )
        std_comparison.net_return_rm_ha = (
            std_comparison.expected_yield_t_ha * paddy_price_rm_t
        ) - std_comparison.cost_after_subsidy_rm_ha
        std_comparison.roi_percent = (
            std_comparison.net_return_rm_ha / std_comparison.cost_after_subsidy_rm_ha
        ) * 100
        comparisons.append(std_comparison)

        # Strategy 2: Organic
        org_program = self.generate_recommendation(
            variety,
            target_yield,
            soil_n_status,
            soil_p_status,
            soil_k_status,
            organic_preferred=True,
        )

        org_comparison = FertilizerComparison(
            strategy_name="Organic",
            program=org_program,
            cost_rm_ha=org_program.total_cost_rm_ha,
            cost_after_subsidy_rm_ha=org_program.total_cost_after_subsidy_rm_ha,
            expected_yield_t_ha=target_yield
            + org_program.expected_yield_increase_t_ha * 0.8,
            net_return_rm_ha=0,
            roi_percent=0,
            pros=["Soil health improvement", "Sustainable", "Lower input cost"],
            cons=["Slower nutrient release", "Higher labor", "Inconsistent nutrients"],
        )
        org_comparison.net_return_rm_ha = (
            org_comparison.expected_yield_t_ha * paddy_price_rm_t
        ) - org_comparison.cost_after_subsidy_rm_ha
        org_comparison.roi_percent = (
            org_comparison.net_return_rm_ha / org_comparison.cost_after_subsidy_rm_ha
        ) * 100
        comparisons.append(org_comparison)

        # Strategy 3: Integrated (synthetic + organic)
        int_program = self.generate_recommendation(
            variety, target_yield, soil_n_status, soil_p_status, soil_k_status
        )
        # Reduce synthetic by 30%, add organic
        int_program.total_cost_rm_ha *= 0.8
        int_program.total_cost_after_subsidy_rm_ha *= 0.8
        int_program.expected_yield_increase_t_ha *= 0.95

        int_comparison = FertilizerComparison(
            strategy_name="Integrated (Synthetic + Organic)",
            program=int_program,
            cost_rm_ha=int_program.total_cost_rm_ha,
            cost_after_subsidy_rm_ha=int_program.total_cost_after_subsidy_rm_ha,
            expected_yield_t_ha=target_yield + int_program.expected_yield_increase_t_ha,
            net_return_rm_ha=0,
            roi_percent=0,
            pros=["Balance of benefits", "Good ROI", "Improved sustainability"],
            cons=["More complex management"],
        )
        int_comparison.net_return_rm_ha = (
            int_comparison.expected_yield_t_ha * paddy_price_rm_t
        ) - int_comparison.cost_after_subsidy_rm_ha
        int_comparison.roi_percent = (
            int_comparison.net_return_rm_ha / int_comparison.cost_after_subsidy_rm_ha
        ) * 100
        comparisons.append(int_comparison)

        # Add recommendations
        best = max(comparisons, key=lambda c: c.net_return_rm_ha)
        for c in comparisons:
            if c == best:
                c.recommendation = "BEST VALUE - Highest net return"
            else:
                c.recommendation = "Alternative option"

        return comparisons


# =============================================================================
# API INTERFACE
# =============================================================================


class FertilizerAPI:
    """API for fertilizer recommendations."""

    def __init__(self):
        self.engine = FertilizerRecommendationEngine()

    def get_recommendation(
        self,
        variety: str,
        target_yield_t_ha: float,
        soil_n_status: str,
        soil_p_status: str = "medium",
        soil_k_status: str = "medium",
        organic_preferred: bool = False,
    ) -> Dict:
        """Get fertilizer recommendation."""
        program = self.engine.generate_recommendation(
            variety,
            target_yield_t_ha,
            soil_n_status,
            soil_p_status,
            soil_k_status,
            organic_preferred,
        )

        return {
            "variety": program.variety,
            "target_yield": program.target_yield_t_ha,
            "total_n_kg_ha": program.total_n_kg_ha,
            "total_p_kg_ha": program.total_p_kg_ha,
            "total_k_kg_ha": program.total_k_kg_ha,
            "total_cost_rm_ha": program.total_cost_rm_ha,
            "cost_after_subsidy_rm_ha": program.total_cost_after_subsidy_rm_ha,
            "expected_yield_increase_t_ha": program.expected_yield_increase_t_ha,
            "applications": [
                {
                    "stage": a.stage,
                    "timing_days": a.timing_days,
                    "product": a.product,
                    "rate_kg_ha": a.rate_kg_ha,
                    "nutrients": a.nutrient_amounts,
                    "cost_rm_ha": a.cost_rm_ha,
                    "method": a.method,
                }
                for a in program.applications
            ],
        }

    def compare_strategies(
        self,
        variety: str,
        target_yield_t_ha: float,
        soil_n_status: str,
        soil_p_status: str = "medium",
        soil_k_status: str = "medium",
    ) -> List[Dict]:
        """Compare fertilizer strategies."""
        comparisons = self.engine.compare_strategies(
            variety, target_yield_t_ha, soil_n_status, soil_p_status, soil_k_status
        )

        return [
            {
                "strategy": c.strategy_name,
                "cost_rm_ha": c.cost_rm_ha,
                "cost_after_subsidy": c.cost_after_subsidy_rm_ha,
                "expected_yield": c.expected_yield_t_ha,
                "net_return": c.net_return_rm_ha,
                "roi_percent": c.roi_percent,
                "pros": c.pros,
                "cons": c.cons,
                "recommendation": c.recommendation,
            }
            for c in comparisons
        ]


def main():
    """CLI for testing."""
    api = FertilizerAPI()

    print("=" * 70)
    print("FERTILIZER RECOMMENDATION SYSTEM - CLI")
    print("=" * 70)

    # Get recommendation
    print("\n📋 FERTILIZER RECOMMENDATION")
    print("-" * 70)
    rec = api.get_recommendation(
        variety="MR219",
        target_yield_t_ha=6,
        soil_n_status="low",
        soil_p_status="medium",
        soil_k_status="low",
    )

    print(f"\nVariety: {rec['variety']}")
    print(f"Target Yield: {rec['target_yield']} t/ha")
    print(f"Expected Yield Increase: +{rec['expected_yield_increase_t_ha']:.1f} t/ha")
    print(f"\nTotal Nutrients:")
    print(f"  N: {rec['total_n_kg_ha']:.0f} kg/ha")
    print(f"  P: {rec['total_p_kg_ha']:.0f} kg/ha")
    print(f"  K: {rec['total_k_kg_ha']:.0f} kg/ha")
    print(f"\nTotal Cost: RM {rec['total_cost_rm_ha']:.0f}/ha")
    print(f"Cost after Subsidy: RM {rec['cost_after_subsidy_rm_ha']:.0f}/ha")

    print(f"\n📅 APPLICATION SCHEDULE:")
    for app in rec["applications"]:
        timing = (
            f"Day {app['timing_days']}"
            if app["timing_days"] >= 0
            else f"{abs(app['timing_days'])} days before planting"
        )
        print(f"\n  {app['stage']} ({timing})")
        print(f"    Product: {app['product']}")
        print(f"    Rate: {app['rate_kg_ha']:.0f} kg/ha")
        print(f"    Method: {app['method']}")
        print(f"    Cost: RM {app['cost_rm_ha']:.0f}")

    # Compare strategies
    print("\n\n📊 STRATEGY COMPARISON")
    print("-" * 70)
    comparisons = api.compare_strategies(
        variety="MR219", target_yield_t_ha=6, soil_n_status="low"
    )

    for comp in comparisons:
        print(f"\n{comp['strategy']} {comp['recommendation']}")
        print(f"  Cost: RM {comp['cost_after_subsidy']:.0f}/ha")
        print(f"  Expected Yield: {comp['expected_yield']:.1f} t/ha")
        print(f"  Net Return: RM {comp['net_return']:.0f}/ha")
        print(f"  ROI: {comp['roi_percent']:.0f}%")
        print(f"  Pros: {', '.join(comp['pros'][:2])}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
