"""
Soil Analysis Node
==================
Comprehensive soil analysis and recommendations for padi farming.

Features:
- Multi-source soil data acquisition
- Soil property analysis
- Nutrient deficiency detection
- Fertilizer recommendations based on soil
- Soil health scoring
- Regional soil database
"""

import os
import json
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Optional, List, Dict, Tuple, Any
from enum import Enum
from pathlib import Path
import math
import random
from collections import defaultdict

# =============================================================================
# DATA MODELS
# =============================================================================


class SoilType(Enum):
    """Soil type classification."""

    CLAY = "clay"
    SANDY_CLAY = "sandy_clay"
    SILT_CLAY = "silt_clay"
    SANDY_LOAM = "sandy_loam"
    SILT_LOAM = "silt_loam"
    CLAY_LOAM = "clay_loam"
    LOAM = "loam"
    PEAT = "peat"
    ALLUVIAL = "alluvial"
    SALINE = "saline"


class SoilTexture(Enum):
    """Soil texture classification."""

    SAND = "sand"
    LOAMY_SAND = "loamy_sand"
    SANDY_LOAM = "sandy_loam"
    LOAM = "loam"
    SILT_LOAM = "silt_loam"
    SILT = "silt"
    SANDY_CLAY_LOAM = "sandy_clay_loam"
    CLAY_LOAM = "clay_loam"
    SILTY_CLAY_LOAM = "silty_clay_loam"
    SANDY_CLAY = "sandy_clay"
    SILTY_CLAY = "silty_clay"
    CLAY = "clay"


class NutrientLevel(Enum):
    """Nutrient level classification."""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DrainageClass(Enum):
    """Soil drainage classification."""

    EXCESSIVE = "excessive"
    SOMEWHAT_EXCESSIVE = "somewhat_excessive"
    WELL = "well"
    MODERATELY_WELL = "moderately_well"
    SOMEWHAT_POOR = "somewhat_poor"
    POOR = "poor"
    VERY_POOR = "very_poor"


@dataclass
class GeoLocation:
    """GPS coordinates for soil data lookup."""

    latitude: float
    longitude: float
    altitude: Optional[float] = None


@dataclass
class SoilTestResult:
    """Results from soil testing."""

    # Sampling information
    sample_id: str
    sample_date: date
    location: GeoLocation

    # Basic properties
    soil_type: Optional[SoilType] = None
    soil_texture: Optional[SoilTexture] = None
    color: Optional[str] = None

    # pH and organic matter
    ph: Optional[float] = None
    organic_matter_percent: Optional[float] = None
    organic_carbon_percent: Optional[float] = None

    # Primary nutrients (ppm or mg/kg)
    nitrogen_total_percent: Optional[float] = None
    nitrogen_available_ppm: Optional[float] = None
    phosphorus_ppm: Optional[float] = None
    potassium_ppm: Optional[float] = None

    # Secondary nutrients (meq/100g or ppm)
    calcium_ppm: Optional[float] = None
    magnesium_ppm: Optional[float] = None
    sulfur_ppm: Optional[float] = None

    # Micronutrients (ppm)
    zinc_ppm: Optional[float] = None
    iron_ppm: Optional[float] = None
    manganese_ppm: Optional[float] = None
    copper_ppm: Optional[float] = None
    boron_ppm: Optional[float] = None

    # Other properties
    electrical_conductivity_ds_m: Optional[float] = None  # dS/m
    cation_exchange_capacity: Optional[float] = None  # meq/100g
    base_saturation_percent: Optional[float] = None

    # Physical properties
    sand_percent: Optional[float] = None
    silt_percent: Optional[float] = None
    clay_percent: Optional[float] = None
    bulk_density: Optional[float] = None  # g/cm3
    water_holding_capacity_percent: Optional[float] = None

    # Additional notes
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["sample_date"] = self.sample_date.isoformat()
        if self.soil_type:
            d["soil_type"] = self.soil_type.value
        if self.soil_texture:
            d["soil_texture"] = self.soil_texture.value
        return d


@dataclass
class SoilAnalysisResult:
    """Analysis result with interpretations and recommendations."""

    # Soil test data
    soil_test: SoilTestResult

    # Interpretations
    ph_interpretation: str = ""
    ph_status: NutrientLevel = NutrientLevel.MEDIUM

    nitrogen_status: NutrientLevel = NutrientLevel.MEDIUM
    phosphorus_status: NutrientLevel = NutrientLevel.MEDIUM
    potassium_status: NutrientLevel = NutrientLevel.MEDIUM

    # Micronutrient status
    zinc_status: NutrientLevel = NutrientLevel.MEDIUM
    iron_status: NutrientLevel = NutrientLevel.MEDIUM
    manganese_status: NutrientLevel = NutrientLevel.MEDIUM
    boron_status: NutrientLevel = NutrientLevel.MEDIUM

    # Overall health
    soil_health_score: float = 0.0  # 0-100
    soil_health_grade: str = ""  # A, B, C, D, F

    # Deficiencies identified
    deficiencies: List[str] = field(default_factory=list)
    toxicities: List[str] = field(default_factory=list)

    # Recommendations
    amendments: List[Dict] = field(default_factory=list)
    fertilizer_recommendations: List[Dict] = field(default_factory=list)

    # Regional context
    soil_suitability: str = ""
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "ph_interpretation": self.ph_interpretation,
            "ph_status": self.ph_status.value,
            "nitrogen_status": self.nitrogen_status.value,
            "phosphorus_status": self.phosphorus_status.value,
            "potassium_status": self.potassium_status.value,
            "micronutrients": {
                "zinc": self.zinc_status.value,
                "iron": self.iron_status.value,
                "manganese": self.manganese_status.value,
                "boron": self.boron_status.value,
            },
            "soil_health_score": self.soil_health_score,
            "soil_health_grade": self.soil_health_grade,
            "deficiencies": self.deficiencies,
            "toxicities": self.toxicities,
            "amendments": self.amendments,
            "fertilizer_recommendations": self.fertilizer_recommendations,
            "soil_suitability": self.soil_suitability,
            "limitations": self.limitations,
        }


@dataclass
class FertilizerRecommendation:
    """Fertilizer recommendation for a nutrient."""

    nutrient: str
    current_level: float
    target_level: float
    unit: str
    recommendation_type: str  # "organic", "synthetic", "both"
    product_suggestion: str
    rate_kg_ha: float
    timing: str
    cost_estimate_rm_ha: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class SoilAmendment:
    """Soil amendment recommendation."""

    amendment_type: str
    purpose: str
    product: str
    rate_kg_ha: float
    timing: str
    expected_duration: str
    cost_estimate_rm_ha: Optional[float] = None


# =============================================================================
# SOIL INTERPRETATION STANDARDS (Malaysia Context)
# =============================================================================


class SoilStandards:
    """
    Soil nutrient interpretation standards.
    Values are typical ranges for Malaysian rice soils.
    """

    # pH ranges for rice
    PH_OPTIMAL = (5.5, 7.0)
    PH_ACIDIC_CRITICAL = 5.0
    PH_ALKALINE_CRITICAL = 8.0

    # Nitrogen (Total N %)
    N_VERY_LOW = 0.05
    N_LOW = 0.1
    N_MEDIUM = 0.15
    N_HIGH = 0.25

    # Available N (ppm) - using Min N method
    N_AVAILABLE_VERY_LOW = 20
    N_AVAILABLE_LOW = 40
    N_AVAILABLE_MEDIUM = 60
    N_AVAILABLE_HIGH = 100

    # Phosphorus (Bray II, ppm)
    P_VERY_LOW = 5
    P_LOW = 10
    P_MEDIUM = 20
    P_HIGH = 40

    # Potassium (NH4OAc, ppm)
    K_VERY_LOW = 50
    K_LOW = 100
    K_MEDIUM = 150
    K_HIGH = 250

    # Micronutrients (DTPA, ppm)
    ZN_CRITICAL = 1.0
    FE_CRITICAL = 4.0
    MN_CRITICAL = 3.0
    B_CRITICAL = 0.5

    # Organic matter (%)
    OM_VERY_LOW = 1.0
    OM_LOW = 2.0
    OM_MEDIUM = 3.0
    OM_HIGH = 5.0

    # Electrical conductivity (dS/m) - salinity
    EC_SALINE_THRESHOLD = 4.0

    @classmethod
    def interpret_ph(cls, ph: float) -> Tuple[str, NutrientLevel]:
        """Interpret pH value."""
        if ph < 4.5:
            return (
                "Very strongly acidic - lime required immediately",
                NutrientLevel.VERY_LOW,
            )
        elif ph < 5.0:
            return "Strongly acidic - lime recommended", NutrientLevel.LOW
        elif ph < 5.5:
            return "Moderately acidic - lime may be needed", NutrientLevel.LOW
        elif ph < 6.0:
            return "Slightly acidic - suitable for rice", NutrientLevel.MEDIUM
        elif ph < 6.5:
            return "Slightly acidic - optimal for most nutrients", NutrientLevel.HIGH
        elif ph < 7.0:
            return "Neutral - optimal for rice", NutrientLevel.HIGH
        elif ph < 7.5:
            return (
                "Slightly alkaline - monitor for iron deficiency",
                NutrientLevel.MEDIUM,
            )
        elif ph < 8.0:
            return (
                "Moderately alkaline - may affect nutrient availability",
                NutrientLevel.LOW,
            )
        else:
            return (
                "Strongly alkaline - major nutrient issues likely",
                NutrientLevel.VERY_LOW,
            )

    @classmethod
    def interpret_nitrogen(cls, n_ppm: float) -> NutrientLevel:
        """Interpret available nitrogen."""
        if n_ppm < cls.N_AVAILABLE_VERY_LOW:
            return NutrientLevel.VERY_LOW
        elif n_ppm < cls.N_AVAILABLE_LOW:
            return NutrientLevel.LOW
        elif n_ppm < cls.N_AVAILABLE_MEDIUM:
            return NutrientLevel.MEDIUM
        elif n_ppm < cls.N_AVAILABLE_HIGH:
            return NutrientLevel.HIGH
        else:
            return NutrientLevel.VERY_HIGH

    @classmethod
    def interpret_phosphorus(cls, p_ppm: float) -> NutrientLevel:
        """Interpret phosphorus (Bray II)."""
        if p_ppm < cls.P_VERY_LOW:
            return NutrientLevel.VERY_LOW
        elif p_ppm < cls.P_LOW:
            return NutrientLevel.LOW
        elif p_ppm < cls.P_MEDIUM:
            return NutrientLevel.MEDIUM
        elif p_ppm < cls.P_HIGH:
            return NutrientLevel.HIGH
        else:
            return NutrientLevel.VERY_HIGH

    @classmethod
    def interpret_potassium(cls, k_ppm: float) -> NutrientLevel:
        """Interpret potassium."""
        if k_ppm < cls.K_VERY_LOW:
            return NutrientLevel.VERY_LOW
        elif k_ppm < cls.K_LOW:
            return NutrientLevel.LOW
        elif k_ppm < cls.K_MEDIUM:
            return NutrientLevel.MEDIUM
        elif k_ppm < cls.K_HIGH:
            return NutrientLevel.HIGH
        else:
            return NutrientLevel.VERY_HIGH

    @classmethod
    def interpret_zinc(cls, zn_ppm: float) -> NutrientLevel:
        """Interpret zinc (DTPA)."""
        if zn_ppm < cls.ZN_CRITICAL:
            return NutrientLevel.LOW
        elif zn_ppm < 2.0:
            return NutrientLevel.MEDIUM
        else:
            return NutrientLevel.HIGH

    @classmethod
    def interpret_iron(cls, fe_ppm: float) -> NutrientLevel:
        """Interpret iron (DTPA)."""
        if fe_ppm < cls.FE_CRITICAL:
            return NutrientLevel.LOW
        elif fe_ppm < 10:
            return NutrientLevel.MEDIUM
        else:
            return NutrientLevel.HIGH


# =============================================================================
# SOIL DATA PROVIDERS
# =============================================================================


class SoilDataProvider:
    """Base class for soil data sources."""

    def __init__(self):
        self.name = "base"

    def get_soil_data(self, location: GeoLocation) -> Optional[Dict]:
        """Get soil data for a location."""
        raise NotImplementedError

    def get_soil_series(self, location: GeoLocation) -> Optional[str]:
        """Get soil series name for a location."""
        raise NotImplementedError


class SoilGridsProvider(SoilDataProvider):
    """
    SoilGrids API integration.
    Provides global soil property predictions.
    """

    def __init__(self):
        super().__init__()
        self.name = "soilgrids"
        self.base_url = "https://rest.isric.org/soilgrids/v2"

    def get_soil_data(self, location: GeoLocation) -> Optional[Dict]:
        """
        Get predicted soil properties from SoilGrids.

        In production, this would call the SoilGrids API.
        """
        # Simulated response
        return {
            "clay_mean": random.uniform(20, 50),
            "silt_mean": random.uniform(20, 40),
            "sand_mean": random.uniform(30, 60),
            "ph_water": random.uniform(4.5, 7.5),
            "organic_carbon": random.uniform(0.5, 3.0),
            "cec": random.uniform(10, 30),
            "bulk_density": random.uniform(1.2, 1.6),
            "awc": random.uniform(0.1, 0.3),
            "depth_layers": [0, 5, 15, 30, 60, 100],
        }


class MalaysianSoilDatabaseProvider(SoilDataProvider):
    """
    Malaysian soil series database.
    Contains information about common Malaysian soil series.
    """

    def __init__(self):
        super().__init__()
        self.name = "malaysia_soil_db"
        self._initialize_database()

    def _initialize_database(self):
        """Initialize Malaysian soil series database."""
        self.soil_series = {
            "SERDANG": {
                "name": "Serdang Series",
                "soil_type": SoilType.ALLUVIAL,
                "texture": SoilTexture.CLAY_LOAM,
                "ph_range": (5.0, 6.5),
                "drainage": DrainageClass.WELL,
                "suitability": "Good for rice, general agriculture",
                "limitations": ["Flooding risk in low areas"],
                "region": ["Selangor", "Negeri Sembilan"],
            },
            "KANGKAR": {
                "name": "Kangkong Series",
                "soil_type": SoilType.ALLUVIAL,
                "texture": SoilTexture.CLAY,
                "ph_range": (5.5, 7.0),
                "drainage": DrainageClass.POOR,
                "suitability": "Excellent for rice",
                "limitations": ["Poor drainage", "Waterlogging"],
                "region": ["Kedah", "Perlis", "Perak"],
            },
            "MALACCA": {
                "name": "Malacca Series",
                "soil_type": SoilType.SANDY_LOAM,
                "texture": SoilTexture.SANDY_LOAM,
                "ph_range": (4.5, 5.5),
                "drainage": DrainageClass.SOMEWHAT_EXCESSIVE,
                "suitability": "Moderate for rice, better for crops",
                "limitations": ["Acidic", "Low fertility", "Drought prone"],
                "region": ["Melaka", "Johor"],
            },
            "BUNGUR": {
                "name": "Bungur Series",
                "soil_type": SoilType.CLAY,
                "texture": SoilTexture.CLAY,
                "ph_range": (5.5, 6.5),
                "drainage": DrainageClass.POOR,
                "suitability": "Good for rice",
                "limitations": ["Poor drainage", "Cracking when dry"],
                "region": ["Kedah", "Kelantan", "Terengganu"],
            },
            "TEKAM": {
                "name": "Tekam Series",
                "soil_type": SoilType.CLAY,
                "texture": SoilTexture.SANDY_CLAY,
                "ph_range": (4.5, 5.5),
                "drainage": DrainageClass.MODERATELY_WELL,
                "suitability": "Moderate for rice",
                "limitations": ["Acidic", "Al toxicity risk"],
                "region": ["Pahang", "Terengganu"],
            },
            "PEAT": {
                "name": "Peat Soil",
                "soil_type": SoilType.PEAT,
                "texture": SoilTexture.CLAY,
                "ph_range": (3.0, 4.5),
                "drainage": DrainageClass.VERY_POOR,
                "suitability": "Limited for rice, some crops possible",
                "limitations": ["Very acidic", "Subsidence", "Fire risk", "Low P, K"],
                "region": ["Sarawak", "Sabah", "Pahang"],
            },
            "RUBBE": {
                "name": "Rubbe Series",
                "soil_type": SoilType.ALLUVIAL,
                "texture": SoilTexture.SILT_LOAM,
                "ph_range": (6.0, 7.5),
                "drainage": DrainageClass.WELL,
                "suitability": "Excellent for rice",
                "limitations": ["None significant"],
                "region": ["Sarawak"],
            },
            "KEDAH": {
                "name": "Kedah Series",
                "soil_type": SoilType.ALLUVIAL,
                "texture": SoilTexture.CLAY,
                "ph_range": (5.0, 6.0),
                "drainage": DrainageClass.SOMEWHAT_POOR,
                "suitability": "Good for rice",
                "limitations": ["Slightly acidic"],
                "region": ["Kedah", "Perlis"],
            },
        }

    def get_soil_data(self, location: GeoLocation) -> Optional[Dict]:
        """Get soil data based on location."""
        series = self.get_soil_series(location)
        if series and series in self.soil_series:
            return self.soil_series[series]
        return None

    def get_soil_series(self, location: GeoLocation) -> Optional[str]:
        """Determine soil series based on location."""
        lat, lon = location.latitude, location.longitude

        # Simplified regional determination
        if lat > 6.3 and lon < 100.6:  # Kedah/Perlis
            return "KANGKAR" if lat > 6.5 else "KEDAH"
        elif lat < 2.5:  # Sarawak/Sabah
            return "RUBBE"
        elif lat < 4.0:  # Johor/Melaka
            return "MALACCA"
        elif 4.0 <= lat < 5.5:  # Pahang
            return "TEKAM"
        else:  # Default
            return "SERDANG"


class FarmerInputProvider(SoilDataProvider):
    """
    Provider for farmer-provided soil test data.
    """

    def __init__(self):
        super().__init__()
        self.name = "farmer_input"
        self.stored_tests: Dict[str, SoilTestResult] = {}

    def store_test(self, test: SoilTestResult):
        """Store a soil test result."""
        self.stored_tests[test.sample_id] = test

    def get_test(self, sample_id: str) -> Optional[SoilTestResult]:
        """Retrieve a soil test result."""
        return self.stored_tests.get(sample_id)

    def get_recent_tests(
        self, location: GeoLocation, max_age_days: int = 365
    ) -> List[SoilTestResult]:
        """Get recent soil tests for a location."""
        cutoff = date.today() - timedelta(days=max_age_days)
        return [
            test
            for test in self.stored_tests.values()
            if test.location
            and self._is_near(test.location, location)
            and test.sample_date >= cutoff
        ]

    def _is_near(
        self, loc1: GeoLocation, loc2: GeoLocation, threshold_km: float = 1.0
    ) -> bool:
        """Check if two locations are within threshold distance."""
        # Simplified calculation
        lat_diff = abs(loc1.latitude - loc2.latitude)
        lon_diff = abs(loc1.longitude - loc2.longitude)
        return (lat_diff < 0.01) and (lon_diff < 0.01)


# =============================================================================
# SOIL ANALYSIS ENGINE
# =============================================================================


class SoilAnalysisEngine:
    """
    Main engine for soil analysis and recommendations.
    """

    def __init__(
        self,
        soil_db: Optional[MalaysianSoilDatabaseProvider] = None,
        soil_grids: Optional[SoilGridsProvider] = None,
        farmer_input: Optional[FarmerInputProvider] = None,
    ):
        self.soil_db = soil_db or MalaysianSoilDatabaseProvider()
        self.soil_grids = soil_grids or SoilGridsProvider()
        self.farmer_input = farmer_input or FarmerInputProvider()
        self.standards = SoilStandards()

    def analyze_soil(
        self,
        soil_test: Optional[SoilTestResult] = None,
        location: Optional[GeoLocation] = None,
    ) -> SoilAnalysisResult:
        """
        Perform comprehensive soil analysis.

        Args:
            soil_test: Actual soil test results (if available)
            location: GPS location for soil data lookup (if no test)
        """
        if soil_test:
            return self._analyze_from_test(soil_test)
        elif location:
            return self._analyze_from_location(location)
        else:
            raise ValueError("Either soil_test or location must be provided")

    def _analyze_from_test(self, soil_test: SoilTestResult) -> SoilAnalysisResult:
        """Analyze soil from actual test results."""
        result = SoilAnalysisResult(soil_test=soil_test)

        # pH analysis
        if soil_test.ph:
            result.ph_interpretation, result.ph_status = self.standards.interpret_ph(
                soil_test.ph
            )

        # Primary nutrients
        if soil_test.nitrogen_available_ppm:
            result.nitrogen_status = self.standards.interpret_nitrogen(
                soil_test.nitrogen_available_ppm
            )

        if soil_test.phosphorus_ppm:
            result.phosphorus_status = self.standards.interpret_phosphorus(
                soil_test.phosphorus_ppm
            )

        if soil_test.potassium_ppm:
            result.potassium_status = self.standards.interpret_potassium(
                soil_test.potassium_ppm
            )

        # Micronutrients
        if soil_test.zinc_ppm:
            result.zinc_status = self.standards.interpret_zinc(soil_test.zinc_ppm)

        if soil_test.iron_ppm:
            result.iron_status = self.standards.interpret_iron(soil_test.iron_ppm)

        # Identify deficiencies
        result.deficiencies = self._identify_deficiencies(result)

        # Identify toxicities
        result.toxicities = self._identify_toxicities(result, soil_test)

        # Calculate soil health score
        result.soil_health_score = self._calculate_health_score(result)
        result.soil_health_grade = self._score_to_grade(result.soil_health_score)

        # Generate recommendations
        result.amendments = self._generate_amendments(result, soil_test)
        result.fertilizer_recommendations = self._generate_fertilizer_rec(result)

        # Soil suitability
        result.soil_suitability = self._determine_suitability(result, soil_test)
        result.limitations = self._identify_limitations(result, soil_test)

        return result

    def _analyze_from_location(self, location: GeoLocation) -> SoilAnalysisResult:
        """Analyze soil based on location data (predicted values)."""
        # Create simulated test from database
        soil_data = self.soil_db.get_soil_data(location)
        grids_data = self.soil_grids.get_soil_data(location)

        soil_test = SoilTestResult(
            sample_id=f"PRED_{location.latitude:.4f}_{location.longitude:.4f}",
            sample_date=date.today(),
            location=location,
            soil_type=SoilType(soil_data.get("soil_type", SoilType.ALLUVIAL).value)
            if soil_data
            else None,
            ph=grids_data.get("ph_water") if grids_data else None,
            organic_matter_percent=grids_data.get("organic_carbon", 0) * 1.72
            if grids_data
            else None,
            sand_percent=grids_data.get("sand_mean") if grids_data else None,
            silt_percent=grids_data.get("silt_mean") if grids_data else None,
            clay_percent=grids_data.get("clay_mean") if grids_data else None,
            notes=f"Predicted soil data for location ({location.latitude:.4f}, {location.longitude:.4f})",
        )

        result = self._analyze_from_test(soil_test)
        result.soil_suitability = (
            soil_data.get("suitability", "Unknown") if soil_data else "Unknown"
        )

        if soil_data:
            result.limitations = soil_data.get("limitations", [])

        return result

    def _identify_deficiencies(self, result: SoilAnalysisResult) -> List[str]:
        """Identify nutrient deficiencies."""
        deficiencies = []

        if result.ph_status in [NutrientLevel.VERY_LOW, NutrientLevel.LOW]:
            deficiencies.append("Low pH - reduces nutrient availability")

        if result.nitrogen_status in [NutrientLevel.VERY_LOW, NutrientLevel.LOW]:
            deficiencies.append(f"Nitrogen deficiency ({result.nitrogen_status.value})")

        if result.phosphorus_status in [NutrientLevel.VERY_LOW, NutrientLevel.LOW]:
            deficiencies.append(
                f"Phosphorus deficiency ({result.phosphorus_status.value})"
            )

        if result.potassium_status in [NutrientLevel.VERY_LOW, NutrientLevel.LOW]:
            deficiencies.append(
                f"Potassium deficiency ({result.potassium_status.value})"
            )

        if result.zinc_status == NutrientLevel.LOW:
            deficiencies.append("Zinc deficiency - common in high pH soils")

        if result.iron_status == NutrientLevel.LOW:
            deficiencies.append(
                "Iron deficiency - possible in high pH or waterlogged soils"
            )

        return deficiencies

    def _identify_toxicities(
        self, result: SoilAnalysisResult, soil_test: SoilTestResult
    ) -> List[str]:
        """Identify potential toxicities."""
        toxicities = []

        if soil_test.ph and soil_test.ph > 7.5:
            toxicities.append("High pH - may cause iron and zinc deficiency")

        if (
            soil_test.electrical_conductivity_ds_m
            and soil_test.electrical_conductivity_ds_m > 4
        ):
            toxicities.append("Salinity risk - high EC levels")

        return toxicities

    def _calculate_health_score(self, result: SoilAnalysisResult) -> float:
        """Calculate overall soil health score (0-100)."""
        score = 100.0

        # pH penalty
        if result.ph_status == NutrientLevel.VERY_LOW:
            score -= 25
        elif result.ph_status == NutrientLevel.LOW:
            score -= 15
        elif result.ph_status == NutrientLevel.MEDIUM:
            score -= 5

        # Nutrient penalties
        nutrient_statuses = [
            result.nitrogen_status,
            result.phosphorus_status,
            result.potassium_status,
        ]

        for status in nutrient_statuses:
            if status == NutrientLevel.VERY_LOW:
                score -= 15
            elif status == NutrientLevel.LOW:
                score -= 10
            elif status == NutrientLevel.HIGH:
                score -= 5

        # Micronutrient penalties
        if result.zinc_status == NutrientLevel.LOW:
            score -= 5
        if result.iron_status == NutrientLevel.LOW:
            score -= 5

        return max(0, min(100, score))

    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 75:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 40:
            return "D"
        else:
            return "F"

    def _generate_amendments(
        self, result: SoilAnalysisResult, soil_test: SoilTestResult
    ) -> List[Dict]:
        """Generate soil amendment recommendations."""
        amendments = []

        # Lime recommendation for acidic soils
        if soil_test.ph and soil_test.ph < 5.5:
            ph_deficit = 5.5 - soil_test.ph
            lime_rate = ph_deficit * 1000  # kg/ha of CaCO3

            if soil_test.ph < 4.5:
                amendments.append(
                    {
                        "type": "lime",
                        "product": "Agricultural Lime (CaCO3)",
                        "rate": f"{int(lime_rate * 1.5)} kg/ha",
                        "timing": "3-4 weeks before planting",
                        "purpose": "Correct severe acidity",
                        "notes": f"Current pH: {soil_test.ph}. Target pH: 5.5-6.0",
                    }
                )
            else:
                amendments.append(
                    {
                        "type": "lime",
                        "product": "Agricultural Lime (CaCO3)",
                        "rate": f"{int(lime_rate)} kg/ha",
                        "timing": "2-3 weeks before planting",
                        "purpose": "Raise pH to optimal range",
                        "notes": f"Current pH: {soil_test.ph}. Target pH: 5.5-6.0",
                    }
                )

        # Organic matter for low OM soils
        if soil_test.organic_matter_percent and soil_test.organic_matter_percent < 2.0:
            om_deficit = 2.0 - soil_test.organic_matter_percent
            compost_rate = om_deficit * 10000  # kg/ha assuming 1% OM = 10t/ha

            amendments.append(
                {
                    "type": "organic_matter",
                    "product": "Compost / Farmyard Manure",
                    "rate": f"{int(compost_rate)} kg/ha",
                    "timing": "During land preparation",
                    "purpose": "Improve soil organic matter",
                    "notes": f"Current OM: {soil_test.organic_matter_percent:.1f}%. Target: >2%",
                }
            )

        # Gypsum for sodic soils
        if (
            soil_test.electrical_conductivity_ds_m
            and soil_test.electrical_conductivity_ds_m > 2
        ):
            amendments.append(
                {
                    "type": "gypsum",
                    "product": "Gypsum (CaSO4)",
                    "rate": "2000-4000 kg/ha",
                    "timing": "During land preparation",
                    "purpose": "Improve soil structure, reduce salinity",
                    "notes": "Apply and incorporate into soil",
                }
            )

        return amendments

    def _generate_fertilizer_rec(self, result: SoilAnalysisResult) -> List[Dict]:
        """Generate fertilizer recommendations based on soil analysis."""
        recommendations = []

        # Nitrogen
        if result.nitrogen_status in [NutrientLevel.VERY_LOW, NutrientLevel.LOW]:
            recommendations.append(
                {
                    "nutrient": "Nitrogen",
                    "current_status": result.nitrogen_status.value,
                    "priority": "High",
                    "options": [
                        {
                            "type": "synthetic",
                            "product": "Urea (46% N)",
                            "rate": "100-150 kg/ha",
                            "split": "Basal 30% + Tillering 40% + PI 30%",
                            "notes": "Apply in split doses for efficiency",
                        },
                        {
                            "type": "organic",
                            "product": "Chicken manure",
                            "rate": "2000-3000 kg/ha",
                            "notes": "Incorporate during land prep",
                        },
                    ],
                }
            )

        # Phosphorus
        if result.phosphorus_status in [NutrientLevel.VERY_LOW, NutrientLevel.LOW]:
            recommendations.append(
                {
                    "nutrient": "Phosphorus",
                    "current_status": result.phosphorus_status.value,
                    "priority": "High"
                    if result.phosphorus_status == NutrientLevel.VERY_LOW
                    else "Medium",
                    "options": [
                        {
                            "type": "synthetic",
                            "product": "TSP (46% P2O5) or NPK 15:15:15",
                            "rate": "80-120 kg P2O5/ha as TSP",
                            "split": "All as basal",
                            "notes": "Broadcast and incorporate",
                        },
                        {
                            "type": "organic",
                            "product": "Rock phosphate",
                            "rate": "200-400 kg/ha",
                            "notes": "Slow release, good for long-term",
                        },
                    ],
                }
            )

        # Potassium
        if result.potassium_status in [NutrientLevel.VERY_LOW, NutrientLevel.LOW]:
            recommendations.append(
                {
                    "nutrient": "Potassium",
                    "current_status": result.potassium_status.value,
                    "priority": "High"
                    if result.potassium_status == NutrientLevel.VERY_LOW
                    else "Medium",
                    "options": [
                        {
                            "type": "synthetic",
                            "product": "Muriate of Potash (60% K2O) or NPK Blue 12:12:17:2",
                            "rate": "60-100 kg K2O/ha as MOP",
                            "split": "Basal 50% + Tillering 50%",
                            "notes": "Essential for grain filling",
                        },
                        {
                            "type": "organic",
                            "product": "Wood ash",
                            "rate": "500-1000 kg/ha",
                            "notes": "Also provides micronutrients",
                        },
                    ],
                }
            )

        # Zinc (common deficiency in rice)
        if result.zinc_status == NutrientLevel.LOW:
            recommendations.append(
                {
                    "nutrient": "Zinc",
                    "current_status": result.zinc_status.value,
                    "priority": "Medium",
                    "options": [
                        {
                            "type": "synthetic",
                            "product": "Zinc sulfate (35% Zn)",
                            "rate": "10-15 kg/ha",
                            "split": "Basal application",
                            "notes": "Mix with NPK or broadcast alone",
                        }
                    ],
                }
            )

        return recommendations

    def _determine_suitability(
        self, result: SoilAnalysisResult, soil_test: SoilTestResult
    ) -> str:
        """Determine soil suitability for rice cultivation."""
        score = result.soil_health_score

        # Check critical factors
        critical_issues = []
        if soil_test.ph and soil_test.ph < 4.5:
            critical_issues.append("severe acidity")
        if (
            soil_test.electrical_conductivity_ds_m
            and soil_test.electrical_conductivity_ds_m > 4
        ):
            critical_issues.append("salinity")

        if critical_issues:
            return f"Limited suitability due to: {', '.join(critical_issues)}"

        if score >= 80:
            return "Excellent suitability for rice cultivation"
        elif score >= 65:
            return "Good suitability - minor amendments may improve yields"
        elif score >= 50:
            return "Moderate suitability - improvements recommended"
        else:
            return "Low suitability - significant amendments needed"

    def _identify_limitations(
        self, result: SoilAnalysisResult, soil_test: SoilTestResult
    ) -> List[str]:
        """Identify soil limitations for rice cultivation."""
        limitations = []

        if soil_test.ph:
            if soil_test.ph < 5.0:
                limitations.append("Strongly acidic - Al toxicity risk")
            elif soil_test.ph > 7.5:
                limitations.append("Alkaline - Fe and Zn deficiency risk")

        if soil_test.electrical_conductivity_ds_m:
            if soil_test.electrical_conductivity_ds_m > 4:
                limitations.append("Salinity hazard")
            elif soil_test.electrical_conductivity_ds_m > 2:
                limitations.append("Slight salinity concern")

        if soil_test.organic_matter_percent:
            if soil_test.organic_matter_percent < 1.5:
                limitations.append("Very low organic matter - poor soil structure")

        if soil_test.clay_percent and soil_test.clay_percent > 60:
            limitations.append("Heavy clay - may have drainage issues")

        return limitations


# =============================================================================
# API INTERFACE
# =============================================================================


class SoilAnalysisAPI:
    """REST API interface for soil analysis."""

    def __init__(self):
        self.engine = SoilAnalysisEngine()

    def analyze_with_test(
        self,
        sample_id: str,
        ph: float,
        nitrogen_ppm: Optional[float] = None,
        phosphorus_ppm: Optional[float] = None,
        potassium_ppm: Optional[float] = None,
        organic_matter: Optional[float] = None,
        latitude: float = 0,
        longitude: float = 0,
    ) -> Dict[str, Any]:
        """Analyze soil with provided test values."""
        soil_test = SoilTestResult(
            sample_id=sample_id,
            sample_date=date.today(),
            location=GeoLocation(latitude=latitude, longitude=longitude),
            ph=ph,
            nitrogen_available_ppm=nitrogen_ppm,
            phosphorus_ppm=phosphorus_ppm,
            potassium_ppm=potassium_ppm,
            organic_matter_percent=organic_matter,
        )

        result = self.engine.analyze_soil(soil_test=soil_test)
        return result.to_dict()

    def analyze_from_location(
        self, latitude: float, longitude: float
    ) -> Dict[str, Any]:
        """Analyze soil based on location (predicted values)."""
        location = GeoLocation(latitude=latitude, longitude=longitude)
        result = self.engine.analyze_soil(location=location)
        return result.to_dict()

    def get_recommendations(
        self,
        latitude: float,
        longitude: float,
        has_soil_test: bool = False,
        ph: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Get fertilizer and amendment recommendations."""
        if has_soil_test and ph:
            return self.analyze_with_test(
                sample_id="quick_test", ph=ph, latitude=latitude, longitude=longitude
            )
        else:
            return self.analyze_from_location(latitude, longitude)


# =============================================================================
# CLI INTERFACE
# =============================================================================


def main():
    """Command-line interface for testing."""
    api = SoilAnalysisAPI()

    print("=" * 70)
    print("SOIL ANALYSIS SYSTEM - CLI")
    print("=" * 70)

    # Example 1: Analyze from soil test
    print("\n📋 ANALYSIS FROM SOIL TEST")
    print("-" * 70)
    result = api.analyze_with_test(
        sample_id="TEST-001",
        ph=5.2,
        nitrogen_ppm=35,
        phosphorus_ppm=8,
        potassium_ppm=80,
        organic_matter=1.8,
        latitude=6.0,
        longitude=100.4,
    )

    print(
        f"\nSoil Health Score: {result['soil_health_score']:.0f}/100 (Grade: {result['soil_health_grade']})"
    )
    print(f"pH: {result['ph_interpretation']}")
    print(f"\nNutrient Status:")
    print(f"  - Nitrogen: {result['nitrogen_status']}")
    print(f"  - Phosphorus: {result['phosphorus_status']}")
    print(f"  - Potassium: {result['potassium_status']}")

    if result["deficiencies"]:
        print(f"\n⚠️ Deficiencies identified:")
        for d in result["deficiencies"]:
            print(f"   - {d}")

    if result["amendments"]:
        print(f"\n🔧 Recommended Amendments:")
        for a in result["amendments"]:
            print(f"   {a['type'].upper()}: {a['product']}")
            print(f"      Rate: {a['rate']} ({a['timing']})")

    if result["fertilizer_recommendations"]:
        print(f"\n🌾 Fertilizer Recommendations:")
        for rec in result["fertilizer_recommendations"]:
            print(f"   {rec['nutrient']} ({rec['priority']} priority):")
            for opt in rec["options"]:
                print(f"      - {opt['product']}: {opt['rate']}")

    # Example 2: Analyze from location (predicted)
    print("\n\n📍 ANALYSIS FROM LOCATION (Predicted)")
    print("-" * 70)
    result2 = api.analyze_from_location(latitude=6.0, longitude=100.4)

    print(f"\nSoil Suitability: {result2['soil_suitability']}")
    if result2["limitations"]:
        print(f"Limitations: {', '.join(result2['limitations'])}")

    print("\n" + "=" * 70)
    print("Demo complete!")


if __name__ == "__main__":
    main()
