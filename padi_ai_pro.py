"""
Padi AI Pro - Enhanced Smart Farming System
==========================================
Features:
- Image upload for disease detection (AI-powered)
- Ranked solutions (S/A/B/C ratings)
- Product recommendations with cost analysis
- Website purchase links
- Money/Quality/Time trade-offs
"""

import os
import json
import requests
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# DATA MODELS
# =============================================================================


class SolutionRank(Enum):
    S = "S"  # Best overall
    A = "A"  # Excellent
    B = "B"  # Good
    C = "C"  # Acceptable
    D = "D"  # Not recommended


class PriceTier(Enum):
    BUDGET = "budget"
    STANDARD = "standard"
    PREMIUM = "premium"


@dataclass
class ProductOption:
    """A purchasable product with full details."""

    rank: SolutionRank
    name: str
    product_type: str
    brand: str
    price_rm: float
    unit: str
    quantity_needed: float
    total_cost_rm: float
    effectiveness_score: float  # 0-100
    speed_score: float  # 0-100
    ease_score: float  # 0-100
    overall_score: float  # Weighted score
    purchase_url: str
    purchase_source: str
    pros: List[str]
    cons: List[str]
    best_for: str
    delivery_days: int
    in_stock: bool = True

    def to_dict(self) -> Dict:
        return {
            "rank": self.rank.value,
            "name": self.name,
            "product_type": self.product_type,
            "brand": self.brand,
            "price_rm": self.price_rm,
            "unit": self.unit,
            "quantity_needed": self.quantity_needed,
            "total_cost_rm": self.total_cost_rm,
            "effectiveness_score": self.effectiveness_score,
            "speed_score": self.speed_score,
            "ease_score": self.ease_score,
            "overall_score": self.overall_score,
            "purchase_url": self.purchase_url,
            "purchase_source": self.purchase_source,
            "pros": self.pros,
            "cons": self.cons,
            "best_for": self.best_for,
            "delivery_days": self.delivery_days,
            "in_stock": self.in_stock,
        }


@dataclass
class SolutionOption:
    """A complete solution with multiple product options."""

    rank: SolutionRank
    solution_name: str
    solution_type: str  # chemical, biological, cultural, integrated
    description: str
    effectiveness: float  # 0-100
    speed: float  # 0-100
    cost: float  # 0-100 (lower is cheaper)
    overall_score: float
    products: List[ProductOption]
    total_estimated_cost_rm: float
    time_to_effect_days: int
    safety_level: str  # high, medium, low
    environmental_impact: str  # low, medium, high
    pros: List[str]
    cons: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            "rank": self.rank.value,
            "solution_name": self.solution_name,
            "solution_type": self.solution_type,
            "description": self.description,
            "effectiveness": self.effectiveness,
            "speed": self.speed,
            "cost": self.cost,
            "overall_score": self.overall_score,
            "products": [p.to_dict() for p in self.products],
            "total_estimated_cost_rm": self.total_estimated_cost_rm,
            "time_to_effect_days": self.time_to_effect_days,
            "safety_level": self.safety_level,
            "environmental_impact": self.environmental_impact,
            "pros": self.pros,
            "cons": self.cons,
            "recommendations": self.recommendations,
        }


@dataclass
class CostAnalysis:
    """Complete cost breakdown analysis."""

    initial_cost_rm: float
    recurring_cost_rm: float
    labor_cost_rm: float
    equipment_cost_rm: float
    total_first_season_rm: float
    cost_per_hectare_rm: float
    expected_yield_increase_percent: float
    additional_revenue_rm: float
    net_benefit_rm: float
    roi_percent: float
    payback_months: int
    cost_tier: PriceTier
    budget_friendly: bool


@dataclass
class DiagnosisResult:
    """Complete diagnosis with solutions."""

    disease_name: str
    confidence: float
    severity: str
    affected_area: str
    spread_risk: str
    image_url: Optional[str]
    solutions: List[SolutionOption]
    ranked_solutions: List[Dict]  # Pre-sorted for display
    cost_analysis: CostAnalysis
    quick_actions: List[str]
    monitoring_tips: List[str]
    prevention_tips: List[str]


# =============================================================================
# PRODUCT DATABASE (Real Malaysian Products)
# =============================================================================


class ProductDatabase:
    """Database of real agricultural products available in Malaysia."""

    def __init__(self):
        self.products = {
            # FUNGICIDES - RICE BLAST
            "fungicide_tricyclazole": {
                "name": "Tricyclazole 250EC",
                "brand": "Various",
                "price_rm": 85,
                "unit": "250ml",
                "concentration": "250g/L",
                "effective_for": ["rice_blast"],
                "effectiveness": 92,
                "speed": 85,
                "safety": "medium",
                "sources": [
                    {
                        "name": "KADA Cooperative",
                        "url": "https://www.kada.gov.my",
                        "price": 85,
                    },
                    {
                        "name": "Tractors Malaysia",
                        "url": "https://www.tractors.com.my",
                        "price": 90,
                    },
                    {
                        "name": "Agro concept",
                        "url": "https://www.agroconcept.my",
                        "price": 82,
                    },
                ],
            },
            "fungicide_hexaconazole": {
                "name": "Hexaconazole 5SC",
                "brand": "Various",
                "price_rm": 75,
                "unit": "500ml",
                "concentration": "50g/L",
                "effective_for": ["rice_blast", "sheath_blight"],
                "effectiveness": 88,
                "speed": 80,
                "safety": "medium",
                "sources": [
                    {
                        "name": "KADA Store",
                        "url": "https://www.kada.gov.my",
                        "price": 75,
                    },
                    {
                        "name": "GlobalAgri",
                        "url": "https://globalagri.com.my",
                        "price": 78,
                    },
                ],
            },
            "fungicide_isoprothiolane": {
                "name": "Isoprothiolane 40EC",
                "brand": "FMC",
                "price_rm": 120,
                "unit": "500ml",
                "concentration": "400g/L",
                "effective_for": ["rice_blast", "sheath_blight"],
                "effectiveness": 95,
                "speed": 90,
                "safety": "high",
                "sources": [
                    {
                        "name": "Tractors Malaysia",
                        "url": "https://www.tractors.com.my",
                        "price": 120,
                    },
                    {
                        "name": "Kedah Agro",
                        "url": "https://www.kedahagro.com",
                        "price": 115,
                    },
                ],
            },
            # FUNGICIDES - SHEATH BLIGHT
            "fungicide_validamycin": {
                "name": "Validamycin 3L",
                "brand": "Various",
                "price_rm": 65,
                "unit": "500ml",
                "concentration": "30g/L",
                "effective_for": ["sheath_blight"],
                "effectiveness": 82,
                "speed": 75,
                "safety": "high",
                "sources": [
                    {
                        "name": "KADA Store",
                        "url": "https://www.kada.gov.my",
                        "price": 65,
                    },
                    {
                        "name": "MADA Store",
                        "url": "https://www.mada.gov.my",
                        "price": 68,
                    },
                ],
            },
            "fungicide_carbendazim": {
                "name": "Carbendazim 50WP",
                "brand": "Various",
                "price_rm": 70,
                "unit": "500g",
                "concentration": "500g/kg",
                "effective_for": ["sheath_blight", "brown_spot"],
                "effectiveness": 85,
                "speed": 78,
                "safety": "medium",
                "sources": [
                    {"name": "AgroMall", "url": "https://www.agromall.my", "price": 70},
                    {"name": "FarmFresh", "url": "https://farmfresh.my", "price": 72},
                ],
            },
            # INSECTICIDES
            "insecticide_imidacloprid": {
                "name": "Imidacloprid 200SL",
                "brand": "Bayer",
                "price_rm": 95,
                "unit": "250ml",
                "concentration": "200g/L",
                "effective_for": ["tungro_vector", "leafhopper", "brown_planthopper"],
                "effectiveness": 94,
                "speed": 92,
                "safety": "medium",
                "sources": [
                    {
                        "name": "Tractors Malaysia",
                        "url": "https://www.tractors.com.my",
                        "price": 95,
                    },
                    {
                        "name": "Bayer CropScience",
                        "url": "https://www.bayer.com.my",
                        "price": 100,
                    },
                ],
            },
            "insecticide_thiamethoxam": {
                "name": "Thiamethoxam 25WG",
                "brand": "Syngenta",
                "price_rm": 110,
                "unit": "100g",
                "concentration": "250g/kg",
                "effective_for": ["tungro_vector", "leafhopper"],
                "effectiveness": 96,
                "speed": 95,
                "safety": "medium",
                "sources": [
                    {
                        "name": "Syngenta Malaysia",
                        "url": "https://www.syngenta.com.my",
                        "price": 110,
                    },
                    {
                        "name": "Tractors Malaysia",
                        "url": "https://www.tractors.com.my",
                        "price": 115,
                    },
                ],
            },
            # BACTERICIDES
            "bactericide_copper": {
                "name": "Copper Hydroxide 77WP",
                "brand": "Various",
                "price_rm": 80,
                "unit": "500g",
                "concentration": "770g/kg",
                "effective_for": ["bacterial_blight"],
                "effectiveness": 65,
                "speed": 60,
                "safety": "medium",
                "sources": [
                    {
                        "name": "KADA Store",
                        "url": "https://www.kada.gov.my",
                        "price": 80,
                    },
                    {"name": "AgroMall", "url": "https://www.agromall.my", "price": 75},
                ],
            },
            # HERBICIDES
            "herbicide_butachlor": {
                "name": "Butachlor 60EC",
                "brand": "Various",
                "price_rm": 55,
                "unit": "500ml",
                "concentration": "600g/L",
                "effective_for": ["grassy_weeds"],
                "effectiveness": 88,
                "speed": 85,
                "safety": "medium",
                "sources": [
                    {
                        "name": "KADA Store",
                        "url": "https://www.kada.gov.my",
                        "price": 55,
                    },
                    {
                        "name": "MADA Store",
                        "url": "https://www.mada.gov.my",
                        "price": 58,
                    },
                ],
            },
            "herbicide_pretilachlor": {
                "name": "Pretilachlor 600EC",
                "brand": "Syngenta",
                "price_rm": 70,
                "unit": "500ml",
                "concentration": "600g/L",
                "effective_for": ["grassy_weeds", "sedges"],
                "effectiveness": 90,
                "speed": 88,
                "safety": "medium",
                "sources": [
                    {
                        "name": "Syngenta Malaysia",
                        "url": "https://www.syngenta.com.my",
                        "price": 70,
                    },
                    {
                        "name": "Tractors Malaysia",
                        "url": "https://www.tractors.com.my",
                        "price": 75,
                    },
                ],
            },
            # FERTILIZERS
            "fert_urea": {
                "name": "Urea 46% N",
                "brand": "Various",
                "price_rm": 90,
                "unit": "50kg",
                "concentration": "46% N",
                "effective_for": ["nitrogen_deficiency"],
                "effectiveness": 95,
                "speed": 90,
                "safety": "high",
                "sources": [
                    {
                        "name": "KADA Cooperative",
                        "url": "https://www.kada.gov.my",
                        "price": 90,
                    },
                    {
                        "name": "Petronas Fertilizer",
                        "url": "https://www.petronas.com.my",
                        "price": 88,
                    },
                ],
            },
            "fert_npk_blue": {
                "name": "NPK Blue 12-12-17-2",
                "brand": "Various",
                "price_rm": 115,
                "unit": "50kg",
                "concentration": "12-12-17 + 2S",
                "effective_for": ["general_npk"],
                "effectiveness": 92,
                "speed": 85,
                "safety": "high",
                "sources": [
                    {
                        "name": "KADA Store",
                        "url": "https://www.kada.gov.my",
                        "price": 115,
                    },
                    {
                        "name": "MADA Store",
                        "url": "https://www.mada.gov.my",
                        "price": 118,
                    },
                ],
            },
            "fert_organic": {
                "name": "Organic Compost (Premium)",
                "brand": "GreenGrow",
                "price_rm": 45,
                "unit": "25kg",
                "concentration": "NPK ~2-1-2",
                "effective_for": ["organic_farming", "soil_health"],
                "effectiveness": 75,
                "speed": 50,
                "safety": "high",
                "sources": [
                    {
                        "name": "GreenLife Organic",
                        "url": "https://greenlifeorganic.my",
                        "price": 45,
                    },
                    {"name": "EcoFarm", "url": "https://ecofarm.my", "price": 42},
                ],
            },
            # EQUIPMENT
            "equip_sprayer_knapsack": {
                "name": "Knapsack Sprayer 16L",
                "brand": "Glory / Marion",
                "price_rm": 180,
                "unit": "each",
                "effective_for": ["spraying"],
                "effectiveness": 85,
                "speed": 80,
                "safety": "high",
                "sources": [
                    {
                        "name": "Tractors Malaysia",
                        "url": "https://www.tractors.com.my",
                        "price": 180,
                    },
                    {
                        "name": "Hardware shops",
                        "url": "https://www.hardwareshops.my",
                        "price": 150,
                    },
                ],
            },
            "equip_motorized_sprayer": {
                "name": "Motorized Mistblower 4-Stroke",
                "brand": "Taizhou",
                "price_rm": 850,
                "unit": "each",
                "effective_for": ["large_area_spraying"],
                "effectiveness": 95,
                "speed": 95,
                "safety": "high",
                "sources": [
                    {
                        "name": "Tractors Malaysia",
                        "url": "https://www.tractors.com.my",
                        "price": 850,
                    },
                    {
                        "name": "Agricultural Machinery",
                        "url": "https://www.agmachine.my",
                        "price": 800,
                    },
                ],
            },
        }

    def get_products(self, disease_type: str, max_results: int = 10) -> List[Dict]:
        """Get products for a specific disease/purpose."""
        results = []
        for pid, pdata in self.products.items():
            if disease_type in pdata.get("effective_for", []):
                # Get best source (cheapest)
                sources = sorted(
                    pdata.get("sources", []), key=lambda x: x.get("price", 999)
                )
                best_source = (
                    sources[0]
                    if sources
                    else {"name": "Local Store", "url": "#", "price": pdata["price_rm"]}
                )

                results.append({"product_id": pid, **pdata, "best_source": best_source})

        return sorted(results, key=lambda x: x.get("effectiveness", 0), reverse=True)[
            :max_results
        ]


# =============================================================================
# SOLUTION RANKING ENGINE
# =============================================================================


class SolutionRankingEngine:
    """Rank solutions based on effectiveness, cost, speed, and user needs."""

    WEIGHTS = {
        "effectiveness": 0.35,
        "cost": 0.25,
        "speed": 0.20,
        "safety": 0.10,
        "environmental": 0.10,
    }

    def __init__(self):
        self.db = ProductDatabase()

    def rank_solutions(
        self,
        disease: str,
        severity: str,
        budget: str,  # "low", "medium", "high"
        urgency: str,  # "low", "medium", "high"
        preference: str,  # "effectiveness", "cost", "speed", "balanced"
    ) -> List[SolutionOption]:
        """Generate and rank solutions for a disease."""

        # Adjust weights based on preference
        weights = self._adjust_weights(preference)

        # Get products for this disease
        products = self.db.get_products(disease)

        solutions = []

        # Solution 1: Chemical (Fastest, Most Effective)
        chem_sol = self._create_chemical_solution(
            disease, severity, products, weights, budget
        )
        solutions.append(chem_sol)

        # Solution 2: Integrated Pest Management
        ipm_sol = self._create_ipm_solution(disease, severity, products, weights)
        solutions.append(ipm_sol)

        # Solution 3: Biological/Organic
        bio_sol = self._create_biological_solution(disease, severity, products, weights)
        solutions.append(bio_sol)

        # Solution 4: Cultural Only (Budget)
        cult_sol = self._create_cultural_solution(disease, severity, weights, budget)
        solutions.append(cult_sol)

        # Rank all solutions
        ranked = self._calculate_rankings(solutions, urgency, budget)

        return ranked

    def _adjust_weights(self, preference: str) -> Dict:
        """Adjust scoring weights based on user preference."""
        weights = self.WEIGHTS.copy()

        if preference == "effectiveness":
            weights["effectiveness"] = 0.50
            weights["cost"] = 0.15
        elif preference == "cost":
            weights["cost"] = 0.45
            weights["effectiveness"] = 0.20
        elif preference == "speed":
            weights["speed"] = 0.40
            weights["effectiveness"] = 0.25

        return weights

    def _create_chemical_solution(
        self, disease, severity, products, weights, budget
    ) -> SolutionOption:
        """Create premium chemical solution."""
        # Select best fungicide
        fungicides = [p for p in products if "fungicide" in p.get("product_id", "")]

        if not fungicides:
            fungicides = products[:1] if products else []

        best_fungicide = fungicides[0] if fungicides else None

        # Create product options
        product_options = []
        if best_fungicide:
            # Calculate needed quantity (assuming 500ml/ha for EC formulations)
            qty = 1.0 if severity in ["severe", "high"] else 0.5
            cost = best_fungicide["best_source"]["price"] * qty

            product_options.append(
                ProductOption(
                    rank=SolutionRank.A,
                    name=best_fungicide["name"],
                    product_type="Chemical Fungicide",
                    brand=best_fungicide["brand"],
                    price_rm=best_fungicide["best_source"]["price"],
                    unit=best_fungicide["unit"],
                    quantity_needed=qty,
                    total_cost_rm=cost,
                    effectiveness_score=best_fungicide["effectiveness"],
                    speed_score=best_fungicide["speed"],
                    ease_score=90,
                    overall_score=best_fungicide["effectiveness"] * 0.8,
                    purchase_url=best_fungicide["best_source"]["url"],
                    purchase_source=best_fungicide["best_source"]["name"],
                    pros=["Fast acting", "High effectiveness", "Easy to apply"],
                    cons=["Chemical残留", "Need PPE"],
                    best_for="Quick results",
                    delivery_days=1,
                )
            )

        # Calculate overall scores
        effectiveness = (
            sum(p.effectiveness_score for p in product_options) / len(product_options)
            if product_options
            else 70
        )
        speed = (
            sum(p.speed_score for p in product_options) / len(product_options)
            if product_options
            else 75
        )
        cost = sum(p.total_cost_rm for p in product_options) if product_options else 150
        overall = (
            effectiveness * weights["effectiveness"]
            + (100 - min(cost / 3, 100)) * weights["cost"]
            + speed * weights["speed"]
        )

        return SolutionOption(
            rank=SolutionRank.A,
            solution_name="Chemical Treatment (Premium)",
            solution_type="chemical",
            description="Fast-acting chemical solution for immediate disease control",
            effectiveness=effectiveness,
            speed=speed,
            cost=cost,
            overall_score=overall,
            products=product_options,
            total_estimated_cost_rm=cost + 50,  # + sprayer cost
            time_to_effect_days=3,
            safety_level="medium",
            environmental_impact="high",
            pros=["Fastest results", "Highest effectiveness", "Proven track record"],
            cons=[
                "Chemical input",
                "Safety precautions needed",
                "May affect beneficial organisms",
            ],
            recommendations=[
                "Apply in early morning or late afternoon",
                "Use protective equipment",
                "Follow PHI instructions",
            ],
        )

    def _create_ipm_solution(
        self, disease, severity, products, weights
    ) -> SolutionOption:
        """Create integrated pest management solution."""
        product_options = []

        # Combine cultural + reduced chemical
        product_options.append(
            ProductOption(
                rank=SolutionRank.A,
                name="NPK Blue + Micronutrients",
                product_type="Fertilizer",
                brand="Various",
                price_rm=115,
                unit="50kg",
                quantity_needed=0.5,
                total_cost_rm=57.50,
                effectiveness_score=75,
                speed_score=60,
                ease_score=95,
                overall_score=75,
                purchase_url="https://www.kada.gov.my",
                purchase_source="KADA Store",
                pros=["Improves plant immunity", "Safe", "Builds long-term health"],
                cons=["Slower acting"],
                best_for="Sustainable approach",
                delivery_days=1,
            )
        )

        # Add mild fungicide if severe
        if severity in ["severe", "high"]:
            product_options.append(
                ProductOption(
                    rank=SolutionRank.B,
                    name="Validamycin 3L",
                    product_type="Biological Fungicide",
                    brand="Various",
                    price_rm=65,
                    unit="500ml",
                    quantity_needed=0.5,
                    total_cost_rm=32.50,
                    effectiveness_score=78,
                    speed_score=72,
                    ease_score=90,
                    overall_score=76,
                    purchase_url="https://www.kada.gov.my",
                    purchase_source="KADA Store",
                    pros=["Biological", "Safer", "Good for IPM"],
                    cons=["Moderate effectiveness"],
                    best_for="IPM programs",
                    delivery_days=1,
                )
            )

        total_cost = sum(p.total_cost_rm for p in product_options)
        effectiveness = 82
        speed = 70
        overall = effectiveness * 0.35 + (100 - total_cost / 3) * 0.25 + speed * 0.2

        return SolutionOption(
            rank=SolutionRank.B,
            solution_name="Integrated Pest Management (IPM)",
            solution_type="integrated",
            description="Balanced approach combining cultural practices with minimal chemical use",
            effectiveness=effectiveness,
            speed=speed,
            cost=total_cost,
            overall_score=overall,
            products=product_options,
            total_estimated_cost_rm=total_cost + 30,
            time_to_effect_days=7,
            safety_level="high",
            environmental_impact="medium",
            pros=["Balanced approach", "Environmentally friendly", "Sustainable"],
            cons=["Takes longer to see results", "Requires more monitoring"],
            recommendations=[
                "Combine with proper water management",
                "Remove infected plant parts",
                "Improve field sanitation",
            ],
        )

    def _create_biological_solution(
        self, disease, severity, products, weights
    ) -> SolutionOption:
        """Create organic/biological solution."""
        product_options = []

        # Organic inputs
        product_options.append(
            ProductOption(
                rank=SolutionRank.B,
                name="Organic Compost Premium",
                product_type="Organic Amendment",
                brand="GreenGrow",
                price_rm=45,
                unit="25kg",
                quantity_needed=2,
                total_cost_rm=90,
                effectiveness_score=70,
                speed_score=40,
                ease_score=85,
                overall_score=65,
                purchase_url="https://greenlifeorganic.my",
                purchase_source="GreenLife Organic",
                pros=["100% Organic", "Improves soil health", "Safe for environment"],
                cons=["Slow acting", "May not be sufficient for severe cases"],
                best_for="Organic farming",
                delivery_days=3,
            )
        )

        total_cost = sum(p.total_cost_rm for p in product_options)

        return SolutionOption(
            rank=SolutionRank.C,
            solution_name="Organic/Biological Treatment",
            solution_type="biological",
            description="Purely organic approach using compost, biocontrol agents, and cultural practices",
            effectiveness=65,
            speed=35,
            cost=total_cost,
            overall_score=50,
            products=product_options,
            total_estimated_cost_rm=total_cost,
            time_to_effect_days=14,
            safety_level="very_high",
            environmental_impact="very_low",
            pros=[
                "Completely organic",
                "No chemical残留",
                "Safe for beneficial insects",
            ],
            cons=[
                "Slow results",
                "May not control severe outbreaks",
                "Requires patience",
            ],
            recommendations=[
                "Use as prevention",
                "Apply early",
                "Combine with cultural controls",
            ],
        )

    def _create_cultural_solution(
        self, disease, severity, weights, budget
    ) -> SolutionOption:
        """Create cultural-only solution (no products needed)."""
        return SolutionOption(
            rank=SolutionRank.D,
            solution_name="Cultural Practices Only",
            solution_type="cultural",
            description="No-product approach using sanitation, water management, and natural resistance",
            effectiveness=45,
            speed=30,
            cost=0,
            overall_score=35,
            products=[],
            total_estimated_cost_rm=0,
            time_to_effect_days=21,
            safety_level="very_high",
            environmental_impact="very_low",
            pros=["Free", "No chemicals", "Sustainable"],
            cons=[
                "May not control disease",
                "Takes longest time",
                "Best for prevention",
            ],
            recommendations=[
                "Remove and burn infected plants",
                "Improve drainage",
                "Reduce plant density",
                "Adjust nitrogen levels",
            ],
        )

    def _calculate_rankings(
        self, solutions: List[SolutionOption], urgency: str, budget: str
    ) -> List[SolutionOption]:
        """Calculate final rankings based on context."""
        # Sort by overall score
        sorted_sols = sorted(solutions, key=lambda x: x.overall_score, reverse=True)

        # Assign ranks
        rank_map = {
            0: SolutionRank.S,
            1: SolutionRank.A,
            2: SolutionRank.B,
            3: SolutionRank.C,
        }

        for i, sol in enumerate(sorted_sols):
            # Adjust rank based on context
            if urgency == "high" and sol.solution_type == "chemical":
                sol.rank = SolutionRank.S if i == 0 else SolutionRank.A
            elif budget == "low" and sol.cost < 100:
                sol.rank = SolutionRank.S if i <= 1 else SolutionRank.A
            else:
                sol.rank = rank_map.get(i, SolutionRank.D)

        return sorted_sols


# =============================================================================
# COST ANALYSIS ENGINE
# =============================================================================


class CostAnalysisEngine:
    """Perform detailed cost-benefit analysis."""

    def analyze(
        self,
        solutions: List[SolutionOption],
        farm_size_ha: float,
        current_yield_t_ha: float,
        expected_yield_loss_percent: float,
        paddy_price_rm_t: float,
    ) -> CostAnalysis:
        """Calculate cost analysis for solutions."""

        best_solution = solutions[0] if solutions else None
        if not best_solution:
            return None

        sol = best_solution
        size = farm_size_ha

        # Calculate costs
        initial = sol.total_estimated_cost_rm * size
        equipment = 0 if sol.products else 200  # Buy sprayer if needed
        labor = 50 * size  # RM 50 per hectare for application
        recurring = initial * 0.3  # 30% for follow-up

        total_first = initial + equipment + labor

        # Calculate benefits
        loss_prevented = current_yield_t_ha * (expected_yield_loss_percent / 100) * size
        additional_revenue = loss_prevented * paddy_price_rm_t

        net_benefit = additional_revenue - total_first
        roi = (net_benefit / total_first) * 100 if total_first > 0 else 0
        payback = (
            int(total_first / (additional_revenue / 12))
            if additional_revenue > 0
            else 0
        )

        # Determine budget tier
        cost_per_ha = total_first / size
        if cost_per_ha < 150:
            tier = PriceTier.BUDGET
        elif cost_per_ha < 300:
            tier = PriceTier.STANDARD
        else:
            tier = PriceTier.PREMIUM

        return CostAnalysis(
            initial_cost_rm=initial,
            recurring_cost_rm=recurring,
            labor_cost_rm=labor,
            equipment_cost_rm=equipment,
            total_first_season_rm=total_first,
            cost_per_hectare_rm=cost_per_ha,
            expected_yield_increase_percent=expected_yield_loss_percent,
            additional_revenue_rm=additional_revenue,
            net_benefit_rm=net_benefit,
            roi_percent=roi,
            payback_months=payback,
            cost_tier=tier,
            budget_friendly=cost_per_ha < 200,
        )


# =============================================================================
# DISEASE DIAGNOSIS ENGINE (Image Analysis Simulation)
# =============================================================================


class DiseaseDiagnosisEngine:
    """AI-powered disease diagnosis from images."""

    def __init__(self):
        self.db = ProductDatabase()
        self.ranking_engine = SolutionRankingEngine()
        self.cost_engine = CostAnalysisEngine()

        # Disease symptom database
        self.diseases = {
            "rice_blast": {
                "name": "Rice Blast",
                "symptoms": [
                    "diamond-shaped lesions",
                    "gray center",
                    "yellow halo",
                    "neck rot",
                ],
                "severity_indicators": [
                    "number of lesions",
                    "leaf area affected",
                    "neck infection",
                ],
                "causes": ["High humidity", "Excess nitrogen", "Drought stress"],
            },
            "sheath_blight": {
                "name": "Sheath Blight",
                "symptoms": [
                    "oval lesions",
                    "gray center",
                    "brown border",
                    "basal rotting",
                ],
                "severity_indicators": ["lesion size", "number of lesions", "lodging"],
                "causes": ["Dense canopy", "High nitrogen", "Warm humid"],
            },
            "bacterial_blight": {
                "name": "Bacterial Leaf Blight",
                "symptoms": [
                    "water-soaked lesions",
                    "yellow from tip",
                    "bacterial ooze",
                ],
                "severity_indicators": [
                    "lesion length",
                    "spreading pattern",
                    "wilting",
                ],
                "causes": ["Rain with wind", "Wound infection", "High nitrogen"],
            },
            "brown_spot": {
                "name": "Brown Spot",
                "symptoms": ["brown elliptical spots", "yellow halo", "leaf death"],
                "severity_indicators": [
                    "number of spots",
                    "leaf area",
                    "grain infection",
                ],
                "causes": ["Nutrient deficiency", "Drought", "Poor soil"],
            },
            "tungro": {
                "name": "Tungro Virus",
                "symptoms": [
                    "yellow-orange",
                    "stunted",
                    "reduced tillering",
                    "mottling",
                ],
                "severity_indicators": [
                    "discoloration extent",
                    "stunting severity",
                    "population spread",
                ],
                "causes": ["Leafhopper vector", "Infected seed", "Continuous rice"],
            },
        }

    def diagnose_from_image(
        self, image_data: str, symptoms: List[str]
    ) -> DiagnosisResult:
        """Diagnose disease from image and symptoms."""

        # Simulate AI analysis (in production, use actual ML model)
        detected_disease = self._match_symptoms(symptoms)

        # Get solutions ranked
        solutions = self.ranking_engine.rank_solutions(
            disease=detected_disease["disease_id"],
            severity="moderate",
            budget="medium",
            urgency="medium",
            preference="balanced",
        )

        # Cost analysis
        cost_analysis = self.cost_engine.analyze(
            solutions=solutions,
            farm_size_ha=1.0,
            current_yield_t_ha=5.0,
            expected_yield_loss_percent=30,
            paddy_price_rm_t=2000,
        )

        # Build ranked display
        ranked_display = []
        for i, sol in enumerate(solutions):
            ranked_display.append({"position": i + 1, **sol.to_dict()})

        return DiagnosisResult(
            disease_name=detected_disease["name"],
            confidence=detected_disease["confidence"],
            severity="moderate",
            affected_area="15-20% of field",
            spread_risk="Medium - can spread with rain",
            image_url=None,
            solutions=solutions,
            ranked_solutions=ranked_display,
            cost_analysis=cost_analysis,
            quick_actions=[
                "Remove infected leaves",
                "Apply fungicide within 48 hours",
                "Reduce nitrogen fertilization",
                "Improve field drainage",
            ],
            monitoring_tips=[
                "Check daily for 1 week",
                "Photo document progression",
                "Scout neighboring fields",
            ],
            prevention_tips=[
                "Use certified seed",
                "Balanced NPK fertilization",
                "Proper plant spacing",
                "Avoid water stress",
            ],
        )

    def _match_symptoms(self, symptoms: List[str]) -> Dict:
        """Match symptoms to diseases."""
        symptom_text = " ".join(symptoms).lower()

        # Pattern matching
        if any(
            w in symptom_text for w in ["diamond", "lesion", "gray", "halo", "neck"]
        ):
            return {
                "disease_id": "rice_blast",
                "name": "Rice Blast",
                "confidence": 0.92,
            }
        elif any(w in symptom_text for w in ["oval", "sheath", "basal", "lodging"]):
            return {
                "disease_id": "sheath_blight",
                "name": "Sheath Blight",
                "confidence": 0.88,
            }
        elif any(
            w in symptom_text
            for w in ["bacterial", "ooze", "yellow", "tip", "water-soak"]
        ):
            return {
                "disease_id": "bacterial_blight",
                "name": "Bacterial Leaf Blight",
                "confidence": 0.85,
            }
        elif any(
            w in symptom_text for w in ["brown", "spot", "elliptical", "deficiency"]
        ):
            return {
                "disease_id": "brown_spot",
                "name": "Brown Spot",
                "confidence": 0.80,
            }
        elif any(w in symptom_text for w in ["yellow", "stunt", "orange", "tungro"]):
            return {"disease_id": "tungro", "name": "Tungro Virus", "confidence": 0.78}

        return {"disease_id": "unknown", "name": "Unknown", "confidence": 0.50}


# =============================================================================
# MAIN API CLASS
# =============================================================================


class PadiAIPro:
    """Main API for Padi AI Pro system."""

    def __init__(self):
        self.diagnosis_engine = DiseaseDiagnosisEngine()
        self.ranking_engine = SolutionRankingEngine()
        self.product_db = ProductDatabase()

    def analyze_disease(
        self,
        symptoms: List[str],
        budget: str = "medium",
        urgency: str = "medium",
        preference: str = "balanced",
        farm_size_ha: float = 1.0,
    ) -> Dict:
        """Full disease analysis with ranked solutions."""

        # Diagnose
        diagnosis = self.diagnosis_engine.diagnose_from_image("", symptoms)

        # Re-rank based on user preferences
        disease_id = diagnosis.disease_name.lower().replace(" ", "_")
        solutions = self.ranking_engine.rank_solutions(
            disease=disease_id,
            severity=diagnosis.severity,
            budget=budget,
            urgency=urgency,
            preference=preference,
        )

        # Cost analysis
        cost = self.diagnosis_engine.cost_engine.analyze(
            solutions=solutions,
            farm_size_ha=farm_size_ha,
            current_yield_t_ha=5.0,
            expected_yield_loss_percent=30,
            paddy_price_rm_t=2000,
        )

        return {
            "diagnosis": {
                "disease": diagnosis.disease_name,
                "confidence": diagnosis.confidence,
                "severity": diagnosis.severity,
                "affected_area": diagnosis.affected_area,
                "spread_risk": diagnosis.spread_risk,
            },
            "ranked_solutions": [
                {
                    "rank": s.rank.value,
                    "name": s.solution_name,
                    "type": s.solution_type,
                    "effectiveness": f"{s.effectiveness}%",
                    "speed": f"{s.speed}%",
                    "cost_rm": f"RM {s.total_estimated_cost_rm:.0f}",
                    "time_to_effect": f"{s.time_to_effect_days} days",
                    "safety": s.safety_level,
                    "products": [
                        {
                            "name": p.name,
                            "price": f"RM {p.total_cost_rm:.0f}",
                            "source": p.purchase_source,
                            "url": p.purchase_url,
                        }
                        for p in s.products
                    ],
                    "pros": s.pros,
                    "cons": s.cons,
                    "recommendation": s.recommendations[0] if s.recommendations else "",
                }
                for s in solutions
            ],
            "cost_analysis": {
                "total_cost_rm": f"RM {cost.total_first_season_rm:.0f}"
                if cost
                else "N/A",
                "cost_per_ha": f"RM {cost.cost_per_hectare_rm:.0f}" if cost else "N/A",
                "expected_benefit_rm": f"RM {cost.additional_revenue_rm:.0f}"
                if cost
                else "N/A",
                "net_benefit_rm": f"RM {cost.net_benefit_rm:.0f}" if cost else "N/A",
                "roi": f"{cost.roi_percent:.0f}%" if cost else "N/A",
                "payback": f"{cost.payback_months} months" if cost else "N/A",
                "budget_tier": cost.cost_tier.value if cost else "N/A",
                "budget_friendly": cost.budget_friendly if cost else False,
            },
            "action_plan": {
                "immediate": diagnosis.quick_actions,
                "monitoring": diagnosis.monitoring_tips,
                "prevention": diagnosis.prevention_tips,
            },
        }


# =============================================================================
# CLI / TEST
# =============================================================================


def main():
    api = PadiAIPro()

    print("=" * 70)
    print("PADI AI PRO - ENHANCED SYSTEM")
    print("=" * 70)

    # Simulate user input: farmer reports symptoms
    print("\n📸 Farmer uploads image: Diseased rice leaf")
    print("   Symptoms: diamond-shaped lesions, gray center, yellow halo")

    result = api.analyze_disease(
        symptoms=["diamond-shaped lesions", "gray center", "yellow halo"],
        budget="medium",
        preference="balanced",
    )

    print("\n" + "=" * 70)
    print("🔬 DIAGNOSIS RESULT")
    print("=" * 70)
    print(f"\n🦠 Disease: {result['diagnosis']['disease']}")
    print(f"   Confidence: {result['diagnosis']['confidence'] * 100:.0f}%")
    print(f"   Severity: {result['diagnosis']['severity']}")

    print("\n" + "=" * 70)
    print("🏆 RANKED SOLUTIONS")
    print("=" * 70)

    for sol in result["ranked_solutions"]:
        print(f"\n[{sol['rank']}] {sol['name']}")
        print(f"    Effectiveness: {sol['effectiveness']} | Speed: {sol['speed']}")
        print(f"    Cost: {sol['cost_rm']} | Time: {sol['time_to_effect']}")
        print(f"    Safety: {sol['safety']}")
        if sol["products"]:
            print(f"    Products:")
            for p in sol["products"]:
                print(f"      - {p['name']} ({p['price']}) from {p['source']}")
                print(f"        🔗 {p['url']}")
        print(f"    Top Recommendation: {sol['recommendation']}")

    print("\n" + "=" * 70)
    print("💰 COST ANALYSIS")
    print("=" * 70)
    ca = result["cost_analysis"]
    print(f"\n   Total Cost: {ca['total_cost_rm']}")
    print(f"   Cost per Hectare: {ca['cost_per_ha']}")
    print(f"   Expected Benefit: {ca['expected_benefit_rm']}")
    print(f"   Net Benefit: {ca['net_benefit_rm']}")
    print(f"   ROI: {ca['roi']}")
    print(f"   Payback: {ca['payback']}")
    print(f"   Budget Friendly: {'✅ Yes' if ca['budget_friendly'] else '❌ No'}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
