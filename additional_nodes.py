"""
Padi AI System - Additional Nodes
================================
Contains Water Source, Plantation Method, and Harvest-PostHarvest nodes.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import random


# =============================================================================
# WATER SOURCE NODE
# =============================================================================


class WaterSource(Enum):
    RAINFED = "rainfed"
    IRRIGATION_SCHEME = "irrigation_scheme"
    PUMP_RIVER = "pump_river"
    PUMP_WELL = "pump_well"
    RESERVOIR = "reservoir"


class IrrigationMethod(Enum):
    CONTINUOUS_FLOODING = "continuous_flooding"
    AWD = "alternate_wetting_drying"
    DRIP = "drip"
    SPRINKLER = "sprinkler"


@dataclass
class WaterSourceAnalysis:
    source_type: WaterSource
    reliability_score: float  # 0-1
    cost_per_ha_per_season: float
    water_availability_mm: float
    recommendations: List[str]
    risks: List[str]


class WaterSourceNode:
    """Water source analysis and recommendations."""

    def __init__(self):
        self.water_requirements = {
            "seedling": 2,
            "tillering": 5,
            "panicle_init": 6,
            "flowering": 8,
            "grain_fill": 6,
            "maturity": 2,
        }

    def analyze(
        self,
        source_type: WaterSource,
        pump_capacity_lpm: Optional[float] = None,
        irrigation_fee: Optional[float] = None,
        pump_fuel_cost_per_hour: Optional[float] = None,
    ) -> WaterSourceAnalysis:
        """Analyze water source and provide recommendations."""

        if source_type == WaterSource.RAINFED:
            return WaterSourceAnalysis(
                source_type=source_type,
                reliability_score=0.4,
                cost_per_ha_per_season=0,
                water_availability_mm=800,
                recommendations=[
                    "Plant early to capture monsoon",
                    "Use drought-tolerant varieties",
                    "Consider water harvesting",
                    "AWD can save water in good rainfall years",
                ],
                risks=["Drought risk", "Monsoon failure", "Limited crop options"],
            )

        elif source_type == WaterSource.IRRIGATION_SCHEME:
            return WaterSourceAnalysis(
                source_type=source_type,
                reliability_score=0.85,
                cost_per_ha_per_season=irrigation_fee or 150,
                water_availability_mm=1500,
                recommendations=[
                    "Follow scheme water schedule",
                    "Apply AWD for water savings",
                    "Coordinate with neighboring farmers",
                    "Maintain on-farm canals",
                ],
                risks=["Schedule conflicts", "End-of-season water shortage"],
            )

        elif source_type == WaterSource.PUMP_RIVER:
            pump_hours_per_ha = 4
            fuel_cost_per_ha = (pump_fuel_cost_per_hour or 5) * pump_hours_per_ha

            return WaterSourceAnalysis(
                source_type=source_type,
                reliability_score=0.7,
                cost_per_ha_per_season=fuel_cost_per_ha + 50,
                water_availability_mm=1200,
                recommendations=[
                    "Use AWD to reduce pumping costs by 20-30%",
                    "Pump during off-peak hours",
                    "Regular maintenance of pump",
                    "Consider solar pump for long-term savings",
                ],
                risks=["Fuel cost volatility", "River water level", "Pump breakdown"],
            )

        elif source_type == WaterSource.PUMP_WELL:
            return WaterSourceAnalysis(
                source_type=source_type,
                reliability_score=0.6,
                cost_per_ha_per_season=200,
                water_availability_mm=1000,
                recommendations=[
                    "Monitor groundwater levels",
                    "Use AWD to conserve water",
                    "Check water quality regularly",
                    "Avoid over-extraction",
                ],
                risks=["Groundwater depletion", "Salinity intrusion", "Quality issues"],
            )

        else:
            return WaterSourceAnalysis(
                source_type=source_type,
                reliability_score=0.8,
                cost_per_ha_per_season=100,
                water_availability_mm=1200,
                recommendations=["Maintain reservoir", "Regular water testing"],
                risks=["Evaporation losses", "Overflow during heavy rain"],
            )

    def get_awd_schedule(self, growth_stage: str, field_capacity: float = 100) -> Dict:
        """Get AWD schedule based on growth stage."""
        schedules = {
            "seedling": {"depth_mm": 5, "dry_days": 1, "flood_before": True},
            "tillering": {"depth_mm": 5, "dry_days": 3, "flood_before": True},
            "panicle_init": {"depth_mm": 10, "dry_days": 2, "flood_before": True},
            "flowering": {"depth_mm": 10, "dry_days": 1, "flood_before": True},
            "grain_fill": {"depth_mm": 5, "dry_days": 3, "flood_before": True},
            "maturity": {"depth_mm": 0, "dry_days": 14, "flood_before": False},
        }
        return schedules.get(growth_stage, schedules["tillering"])


# =============================================================================
# PLANTATION METHOD NODE
# =============================================================================


class PlantingMethod(Enum):
    TRANSPLANTING_MANUAL = "transplanting_manual"
    TRANSPLANTING_MECHANICAL = "transplanting_mechanical"
    DIRECT_SEEDING_BROADCAST = "direct_seeding_broadcast"
    DIRECT_SEEDING_LINE = "direct_seeding_line"
    DIRECT_SEEDING_DRUM = "direct_seeding_drum"


@dataclass
class MethodComparison:
    method: PlantingMethod
    seed_rate_kg_ha: float
    labor_man_days_ha: float
    labor_cost_rm_ha: float
    yield_potential_t_ha: Tuple[float, float]
    weed_management_difficulty: str
    pros: List[str]
    cons: List[str]
    best_for: str
    cost_per_ha: float


class PlantationMethodNode:
    """Compare and recommend planting methods."""

    def compare_methods(self) -> List[MethodComparison]:
        """Compare all planting methods."""
        return [
            MethodComparison(
                method=PlantingMethod.TRANSPLANTING_MANUAL,
                seed_rate_kg_ha=25,
                labor_man_days_ha=30,
                labor_cost_rm_ha=1500,
                yield_potential_t_ha=(6, 8),
                weed_management_difficulty="easy",
                pros=[
                    "Good stand establishment",
                    "Less seed required",
                    "Earlier maturity",
                ],
                cons=["High labor", "Labor shortage risk", "Nursery management needed"],
                best_for="Small farms with available labor",
                cost_per_ha=500,
            ),
            MethodComparison(
                method=PlantingMethod.TRANSPLANTING_MECHANICAL,
                seed_rate_kg_ha=30,
                labor_man_days_ha=8,
                labor_cost_rm_ha=400,
                yield_potential_t_ha=(6, 8),
                weed_management_difficulty="easy",
                pros=["Consistent spacing", "Less labor", "Good establishment"],
                cons=[
                    "Mat preparation needed",
                    "Equipment cost",
                    "Small plot limitations",
                ],
                best_for="Medium to large farms",
                cost_per_ha=800,
            ),
            MethodComparison(
                method=PlantingMethod.DIRECT_SEEDING_BROADCAST,
                seed_rate_kg_ha=100,
                labor_man_days_ha=10,
                labor_cost_rm_ha=500,
                yield_potential_t_ha=(4, 6),
                weed_management_difficulty="difficult",
                pros=["Very fast", "Low labor", "No nursery needed"],
                cons=["High seed rate", "Weed pressure", "Uneven stand"],
                best_for="Large farms, limited labor",
                cost_per_ha=300,
            ),
            MethodComparison(
                method=PlantingMethod.DIRECT_SEEDING_LINE,
                seed_rate_kg_ha=80,
                labor_man_days_ha=12,
                labor_cost_rm_ha=600,
                yield_potential_t_ha=(5, 7),
                weed_management_difficulty="moderate",
                pros=["Better spacing", "Weeding possible", "Moderate seed rate"],
                cons=["Line marking needed", "Skill required"],
                best_for="Medium farms",
                cost_per_ha=350,
            ),
            MethodComparison(
                method=PlantingMethod.DIRECT_SEEDING_DRUM,
                seed_rate_kg_ha=60,
                labor_man_days_ha=8,
                labor_cost_rm_ha=400,
                yield_potential_t_ha=(5, 7),
                weed_management_difficulty="moderate",
                pros=["Row spacing consistent", "Lower seed rate", "Weeding possible"],
                cons=["Equipment needed", "Land leveling required"],
                best_for="Medium to large farms",
                cost_per_ha=400,
            ),
        ]

    def recommend(
        self,
        farm_size_ha: float,
        labor_available: int,
        labor_cost_per_day: float,
        equipment_available: List[str],
        budget_level: str,  # "low", "medium", "high"
    ) -> MethodComparison:
        """Recommend planting method based on farm characteristics."""
        comparisons = self.compare_methods()

        scores = {}
        for comp in comparisons:
            score = 0

            # Farm size scoring
            if comp.method == PlantingMethod.TRANSPLANTING_MANUAL:
                score += 30 if farm_size_ha < 2 else 10
            elif comp.method in [
                PlantingMethod.TRANSPLANTING_MECHANICAL,
                PlantingMethod.DIRECT_SEEDING_DRUM,
            ]:
                score += 30 if farm_size_ha >= 2 else 5

            # Labor scoring
            labor_needed = comp.labor_man_days_ha
            if labor_available >= labor_needed:
                score += 20
            elif labor_available >= labor_needed * 0.5:
                score += 10

            # Equipment scoring
            if comp.method == PlantingMethod.TRANSPLANTING_MECHANICAL:
                if "transplanter" in equipment_available:
                    score += 25
            elif comp.method in [
                PlantingMethod.DIRECT_SEEDING_DRUM,
                PlantingMethod.DIRECT_SEEDING_LINE,
            ]:
                if (
                    "drum_seeder" in equipment_available
                    or "seeder" in equipment_available
                ):
                    score += 20

            # Budget scoring
            if budget_level == "low" and comp.cost_per_ha < 400:
                score += 15
            elif budget_level == "high":
                score += 10

            scores[comp.method] = score

        best_method = max(scores, key=scores.get)
        return next(c for c in comparisons if c.method == best_method)


# =============================================================================
# HARVEST-POSTHARVEST NODE
# =============================================================================


class HarvestCondition(Enum):
    OPTIMAL = "optimal"
    ACCEPTABLE = "acceptable"
    TOO_WET = "too_wet"
    TOO_DRY = "too_dry"


@dataclass
class HarvestRecommendation:
    moisture_content_percent: float
    condition: HarvestCondition
    days_after_50_flowering: int
    timing_advice: str
    harvesting_method: str
    estimated_labor: float
    estimated_cost_rm_ha: float


@dataclass
class DryingRecommendation:
    method: str
    target_moisture_percent: float
    time_required: str
    cost_rm_per_ton: float
    quality_preservation: str
    tips: List[str]


@dataclass
class StorageRecommendation:
    method: str
    capacity_remarks: str
    moisture_control: str
    pest_control: List[str]
    max_storage_months: int
    cost_rm_per_ton: float


class HarvestPostHarvestNode:
    """Harvest timing and post-harvest management."""

    def get_harvest_timing(
        self, variety_duration_days: int, planting_date: str, current_date: str
    ) -> HarvestRecommendation:
        """Recommend harvest timing."""
        # Simplified calculation
        from datetime import datetime, timedelta

        plant_date = datetime.strptime(planting_date, "%Y-%m-%d")
        curr_date = datetime.strptime(current_date, "%Y-%m-%d")
        days_grown = (curr_date - plant_date).days

        days_to_flowering = int(variety_duration_days * 0.6)
        days_after_flowering = days_grown - days_to_flowering

        # Optimal harvest: 30-35 days after 50% flowering
        if 28 <= days_after_flowering <= 38:
            condition = HarvestCondition.OPTIMAL
            advice = "Harvest now for best quality"
        elif 20 <= days_after_flowering <= 45:
            condition = HarvestCondition.ACCEPTABLE
            advice = "Can harvest - quality may be slightly reduced"
        elif days_after_flowering < 20:
            condition = HarvestCondition.TOO_WET
            advice = "Too early - grains not fully developed"
        else:
            condition = HarvestCondition.TOO_DRY
            advice = "Delayed - shattering losses likely"

        # Estimate moisture content based on days after flowering
        base_moisture = 30 - (days_after_flowering * 0.4)
        moisture = max(14, min(30, base_moisture + random.uniform(-2, 2)))

        return HarvestRecommendation(
            moisture_content_percent=round(moisture, 1),
            condition=condition,
            days_after_50_flowering=days_after_flowering,
            timing_advice=advice,
            harvesting_method="Manual (sickle) or Combine",
            estimated_labor=15,  # man-days per ha for manual
            estimated_cost_rm_ha=400,
        )

    def get_drying_recommendation(
        self,
        moisture_content: float,
        sun_availability: str,  # "good", "moderate", "poor"
        scale: str,  # "small", "medium", "large"
    ) -> List[DryingRecommendation]:
        """Recommend drying methods."""
        recommendations = []

        if moisture_content > 20:
            recommendations.append(
                DryingRecommendation(
                    method="Mechanical Dryer"
                    if scale != "small"
                    else "Sun + Mechanical",
                    target_moisture_percent=14,
                    time_required="4-8 hours (mechanical)",
                    cost_rm_per_ton=40 if scale != "small" else 60,
                    quality_preservation="Excellent - uniform drying",
                    tips=[
                        "Monitor temperature",
                        "Don't exceed 50°C for seed",
                        "Stir periodically",
                    ],
                )
            )

        if sun_availability in ["good", "moderate"]:
            recommendations.append(
                DryingRecommendation(
                    method="Sun Drying",
                    target_moisture_percent=14,
                    time_required="2-3 days",
                    cost_rm_per_ton=20,
                    quality_preservation="Good - requires attention",
                    tips=[
                        "Dry on tarp/cement",
                        "Rake regularly",
                        "Cover at night",
                        "Monitor weather",
                    ],
                )
            )

        return recommendations

    def get_storage_recommendation(
        self, storage_duration_months: int, quantity_tons: float, budget: str
    ) -> List[StorageRecommendation]:
        """Recommend storage methods."""
        recommendations = []

        if storage_duration_months <= 1:
            recommendations.append(
                StorageRecommendation(
                    method="Farm Storage (bags)",
                    capacity_remarks="Suitable for small quantities",
                    moisture_control="Ensure 14% moisture, check weekly",
                    pest_control=["Rat guards", "Inspect for insects"],
                    max_storage_months=1,
                    cost_rm_per_ton=30,
                )
            )

        if budget in ["medium", "high"]:
            recommendations.append(
                StorageRecommendation(
                    method="Metal Silo/Bin",
                    capacity_remarks=f"Capacity: {int(quantity_tons * 2)}+ tons",
                    moisture_control="Sealed storage maintains moisture",
                    pest_control=["Hermetic seal", "No chemical needed"],
                    max_storage_months=12,
                    cost_rm_per_ton=50,
                )
            )

        if budget == "high":
            recommendations.append(
                StorageRecommendation(
                    method="Cold Storage (if premium rice)",
                    capacity_remarks="For specialty/seed rice",
                    moisture_control="Optimal at 12%",
                    pest_control=["None needed", "Temperature controlled"],
                    max_storage_months=24,
                    cost_rm_per_ton=200,
                )
            )

        return recommendations


# =============================================================================
# API INTERFACE
# =============================================================================


class CombinedAPI:
    """Combined API for water, plantation, and harvest nodes."""

    def __init__(self):
        self.water_node = WaterSourceNode()
        self.plantation_node = PlantationMethodNode()
        self.harvest_node = HarvestPostHarvestNode()

    # Water Source
    def analyze_water_source(self, source_type: str, **kwargs) -> Dict:
        source = WaterSource(source_type)
        analysis = self.water_node.analyze(source, **kwargs)
        return {
            "source_type": analysis.source_type.value,
            "reliability_score": f"{analysis.reliability_score:.0%}",
            "cost_per_ha": f"RM {analysis.cost_per_ha_per_season:.0f}",
            "recommendations": analysis.recommendations,
            "risks": analysis.risks,
        }

    # Plantation Method
    def compare_planting_methods(self) -> List[Dict]:
        comparisons = self.plantation_node.compare_methods()
        return [
            {
                "method": c.method.value,
                "seed_rate_kg_ha": c.seed_rate_kg_ha,
                "labor_man_days_ha": c.labor_man_days_ha,
                "yield_range": f"{c.yield_potential_t_ha[0]}-{c.yield_potential_t_ha[1]}",
                "pros": c.pros[:2],
                "cons": c.cons[:2],
                "best_for": c.best_for,
                "cost_per_ha": c.cost_per_ha,
            }
            for c in comparisons
        ]

    def recommend_planting_method(
        self, farm_size_ha: float, labor_available: int, **kwargs
    ) -> Dict:
        rec = self.plantation_node.recommend(farm_size_ha, labor_available, **kwargs)
        return {
            "recommended_method": rec.method.value,
            "seed_rate_kg_ha": rec.seed_rate_kg_ha,
            "labor_man_days_ha": rec.labor_man_days_ha,
            "yield_range": f"{rec.yield_potential_t_ha[0]}-{rec.yield_potential_t_ha[1]} t/ha",
            "pros": rec.pros,
            "cons": rec.cons,
        }

    # Harvest
    def get_harvest_timing(self, variety: str, planting_date: str) -> Dict:
        # Use default duration for variety
        durations = {
            "MR219": 125,
            "MR220": 120,
            "MR263": 110,
            "MR269": 115,
            "MR297": 120,
        }
        duration = durations.get(variety, 120)

        from datetime import date

        today = date.today().isoformat()

        rec = self.harvest_node.get_harvest_timing(duration, planting_date, today)
        return {
            "variety": variety,
            "moisture_content": f"{rec.moisture_content_percent}%",
            "condition": rec.condition.value,
            "days_after_flowering": rec.days_after_50_flowering,
            "advice": rec.timing_advice,
            "method": rec.harvesting_method,
            "estimated_cost": f"RM {rec.estimated_cost_rm_ha}/ha",
        }


def main():
    api = CombinedAPI()

    print("=" * 70)
    print("COMBINED NODES - CLI")
    print("=" * 70)

    # Water Source
    print("\n💧 WATER SOURCE ANALYSIS")
    print("-" * 70)
    result = api.analyze_water_source("pump_river", pump_fuel_cost_per_hour=4)
    print(f"Source: {result['source_type']}")
    print(f"Reliability: {result['reliability_score']}")
    print(f"Cost: {result['cost_per_ha']}")
    print("Recommendations:", ", ".join(result["recommendations"][:2]))

    # Plantation Method
    print("\n🌱 PLANTING METHOD COMPARISON")
    print("-" * 70)
    methods = api.compare_planting_methods()
    for m in methods[:3]:
        print(f"• {m['method']}: {m['yield_range']} t/ha")
        print(
            f"  Seed: {m['seed_rate_kg_ha']} kg/ha | Labor: {m['labor_man_days_ha']} days"
        )

    # Harvest
    print("\n🌾 HARVEST TIMING")
    print("-" * 70)
    result = api.get_harvest_timing("MR219", "2025-12-01")
    print(f"Moisture Content: {result['moisture_content']}")
    print(f"Condition: {result['condition']}")
    print(f"Advice: {result['advice']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
