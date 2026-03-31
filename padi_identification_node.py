"""
Padi Identification Node
========================
AI-powered padi (rice) variety identification system with multi-method detection.

Features:
- Image-based identification using CNN
- Farmer selection interface
- GPS + season inference
- Characteristic-based fallback identification
- Growth stage tracking
- Location-based variety suggestions
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

# =============================================================================
# DATA MODELS
# =============================================================================


class FarmType(Enum):
    """Types of farming based on water source and topography."""

    LOWLAND_IRRIGATED = "lowland_irrigated"
    LOWLAND_RAINFED = "lowland_rainfed"
    UPLAND = "upland"
    FLOOD_PRONE = "flood_prone"
    SALINE = "saline"


class GrainType(Enum):
    """Rice grain classification."""

    LONG = "long"
    MEDIUM = "medium"
    SHORT = "short"
    AROMATIC = "aromatic"


class GrowthStage(Enum):
    """Rice growth stages from sowing to harvest."""

    GERMINATION = "germination"
    SEEDLING = "seedling"
    TILLERING = "tillering"
    PANICLE_INITIATION = "panicle_initiation"
    BOOTING = "booting"
    FLOWERING = "flowering"
    GRAIN_FILLING = "grain_filling"
    MATURITY = "maturity"


class IdentificationMethod(Enum):
    """Methods used to identify padi variety."""

    IMAGE_RECOGNITION = "image_recognition"
    FARMER_SELECTION = "farmer_selection"
    GPS_SEASON_INFERENCE = "gps_season_inference"
    CHARACTERISTIC_FALLBACK = "characteristic_fallback"
    CONFIDENCE_BASED = "confidence_based"


@dataclass
class GeoLocation:
    """GPS coordinates and derived information."""

    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None

    def calculate_distance(self, other: "GeoLocation") -> float:
        """Calculate distance between two points in km using Haversine formula."""
        R = 6371  # Earth's radius in km

        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    def get_climate_zone(self) -> str:
        """Infer climate zone from coordinates (simplified for Malaysia)."""
        # Malaysia approximation
        if self.latitude > 6.5:
            return "north_malaysia"  # Kedah, Perlis, Penang
        elif self.latitude > 5.0:
            return "central_malaysia"  # Perak, Selangor
        else:
            return "east_malaysia"  # Sabah, Sarawak


@dataclass
class PlantCharacteristics:
    """Physical characteristics of the padi plant."""

    plant_height_cm: Optional[float] = None
    leaf_color: Optional[str] = None
    leaf_width: Optional[str] = None  # narrow, medium, wide
    tillering_capacity: Optional[str] = None  # low, medium, high
    plant_architecture: Optional[str] = None  # erect, semi-erect, spreading
    grain_length: Optional[str] = None
    grain_awns: Optional[bool] = None
    straw_strength: Optional[str] = None  # weak, medium, strong


@dataclass
class PadiVariety:
    """Complete information about a padi variety."""

    id: str
    name: str
    synonyms: List[str] = field(default_factory=list)

    # Physical characteristics
    duration_days: int = 0
    plant_height_cm: Tuple[float, float] = (0, 0)
    grain_type: GrainType = GrainType.MEDIUM
    amylose_content: str = "medium"

    # Performance
    yield_range_t_ha: Tuple[float, float] = (0, 0)

    # Tolerances
    drought_tolerance: str = "moderate"
    flood_tolerance: str = "moderate"
    salinity_tolerance: str = "low"

    # Disease susceptibility (low, moderate, high)
    blast_susceptibility: str = "moderate"
    blight_susceptibility: str = "moderate"
    tungro_susceptibility: str = "moderate"
    sheath_blight_susceptibility: str = "moderate"

    # Agronomic requirements
    nitrogen_requirement_kg_ha: Tuple[int, int] = (0, 0)
    water_requirement_mm: Tuple[int, int] = (0, 0)

    # Preferred regions
    primary_regions: List[str] = field(default_factory=list)
    preferred_seasons: List[str] = field(default_factory=list)
    preferred_farm_types: List[FarmType] = field(default_factory=list)

    # Market/Commercial
    seed_price_per_50kg: float = 0
    seed_source: str = ""

    # Special characteristics
    photoperiod_sensitive: bool = False

    # Image features for ML
    image_features: Optional[Dict[str, Any]] = None

    def matches_farm_type(self, farm_type: FarmType) -> float:
        """Return match score (0-1) for farm type."""
        if farm_type in self.preferred_farm_types:
            return 1.0

        # Partial matches based on tolerances
        if farm_type == FarmType.UPLAND and self.drought_tolerance != "low":
            return 0.7
        if farm_type == FarmType.FLOOD_PRONE and self.flood_tolerance != "low":
            return 0.7
        if farm_type == FarmType.SALINE and self.salinity_tolerance != "low":
            return 0.6

        return 0.3

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        d = asdict(self)
        d["grain_type"] = self.grain_type.value
        d["preferred_farm_types"] = [ft.value for ft in self.preferred_farm_types]
        return d


@dataclass
class IdentificationResult:
    """Result of variety identification process."""

    variety: Optional[PadiVariety] = None
    confidence: float = 0.0
    method: IdentificationMethod = IdentificationMethod.CONFIDENCE_BASED
    alternative_matches: List[Tuple[PadiVariety, float]] = field(default_factory=list)
    growth_stage: Optional[GrowthStage] = None
    days_to_maturity_estimate: Optional[int] = None
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IdentificationRequest:
    """Request for variety identification."""

    # At least one identification method should be provided
    image_path: Optional[str] = None
    image_features: Optional[Dict[str, Any]] = None
    farmer_selection: Optional[str] = None
    location: Optional[GeoLocation] = None
    planting_date: Optional[date] = None
    characteristics: Optional[PlantCharacteristics] = None
    farm_type: Optional[FarmType] = None

    # Additional context
    target_yield_t_ha: Optional[float] = None
    season: Optional[str] = None  # "main" or "off"


# =============================================================================
# VARIETY DATABASE
# =============================================================================


class VarietyDatabase:
    """Database of padi varieties with search capabilities."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "padi_varieties.db"
        self.varieties: Dict[str, PadiVariety] = {}
        self._initialize_default_varieties()
        if db_path and os.path.exists(db_path):
            self._load_from_db()

    def _initialize_default_varieties(self):
        """Initialize with Malaysian varieties."""

        # High-Yielding Varieties
        self.add_variety(
            PadiVariety(
                id="MR219",
                name="MR219",
                synonyms=["MR 219", "MR219-9"],
                duration_days=125,
                plant_height_cm=(95, 105),
                grain_type=GrainType.LONG,
                amylose_content="high",
                yield_range_t_ha=(7, 9),
                drought_tolerance="moderate",
                flood_tolerance="moderate",
                salinity_tolerance="low",
                blast_susceptibility="moderate",
                blight_susceptibility="high",
                tungro_susceptibility="moderate",
                nitrogen_requirement_kg_ha=(120, 150),
                water_requirement_mm=(1200, 1500),
                primary_regions=["Kedah", "Perlis", "Perak", "Kelantan"],
                preferred_seasons=["main"],
                preferred_farm_types=[FarmType.LOWLAND_IRRIGATED],
                seed_price_per_50kg=180,
                seed_source="MARDI, KADA",
            )
        )

        self.add_variety(
            PadiVariety(
                id="MR220",
                name="MR220",
                synonyms=["MR 220"],
                duration_days=120,
                plant_height_cm=(90, 100),
                grain_type=GrainType.LONG,
                yield_range_t_ha=(6, 8),
                drought_tolerance="moderate",
                blast_susceptibility="low",
                blight_susceptibility="moderate",
                nitrogen_requirement_kg_ha=(100, 130),
                water_requirement_mm=(1100, 1400),
                primary_regions=["Kedah", "Perlis", "Perak"],
                preferred_seasons=["main", "off"],
                preferred_farm_types=[FarmType.LOWLAND_IRRIGATED],
                seed_price_per_50kg=175,
                seed_source="MARDI",
            )
        )

        self.add_variety(
            PadiVariety(
                id="MR263",
                name="MR263",
                synonyms=["MR 263"],
                duration_days=110,
                plant_height_cm=(85, 95),
                grain_type=GrainType.MEDIUM,
                yield_range_t_ha=(5, 7),
                drought_tolerance="high",
                blast_susceptibility="moderate",
                nitrogen_requirement_kg_ha=(80, 110),
                water_requirement_mm=(900, 1200),
                primary_regions=["Kedah", "Perlis", "Pahang"],
                preferred_seasons=["off"],
                preferred_farm_types=[FarmType.LOWLAND_RAINFED, FarmType.UPLAND],
                seed_price_per_50kg=160,
                seed_source="MARDI",
            )
        )

        self.add_variety(
            PadiVariety(
                id="MR269",
                name="MR269",
                synonyms=["MR 269"],
                duration_days=115,
                plant_height_cm=(90, 100),
                grain_type=GrainType.LONG,
                yield_range_t_ha=(6, 8),
                blast_susceptibility="low",
                blight_susceptibility="moderate",
                nitrogen_requirement_kg_ha=(100, 130),
                water_requirement_mm=(1000, 1300),
                primary_regions=["Kedah", "Perlis", "Perak"],
                preferred_seasons=["main", "off"],
                preferred_farm_types=[FarmType.LOWLAND_IRRIGATED],
                seed_price_per_50kg=170,
                seed_source="MARDI",
            )
        )

        self.add_variety(
            PadiVariety(
                id="MR297",
                name="MR297",
                synonyms=["MR 297"],
                duration_days=120,
                plant_height_cm=(95, 105),
                grain_type=GrainType.LONG,
                amylose_content="high",
                yield_range_t_ha=(6, 8),
                blast_susceptibility="low",
                drought_tolerance="moderate",
                nitrogen_requirement_kg_ha=(110, 140),
                water_requirement_mm=(1100, 1400),
                primary_regions=["Kedah", "Perlis", "Perak", "Selangor"],
                preferred_seasons=["main"],
                preferred_farm_types=[FarmType.LOWLAND_IRRIGATED],
                seed_price_per_50kg=185,
                seed_source="MARDI",
            )
        )

        self.add_variety(
            PadiVariety(
                id="MR232",
                name="MR232",
                synonyms=["MR 232"],
                duration_days=105,
                plant_height_cm=(80, 90),
                grain_type=GrainType.MEDIUM,
                yield_range_t_ha=(4, 6),
                drought_tolerance="high",
                blast_susceptibility="moderate",
                nitrogen_requirement_kg_ha=(60, 90),
                water_requirement_mm=(800, 1000),
                primary_regions=["Sabah", "Sarawak"],
                preferred_seasons=["main", "off"],
                preferred_farm_types=[FarmType.UPLAND, FarmType.LOWLAND_RAINFED],
                seed_price_per_50kg=150,
                seed_source="MARDI",
            )
        )

        # Traditional/Local Varieties
        self.add_variety(
            PadiVariety(
                id="KOSHIHIKARI",
                name="Koshihikari",
                synonyms=["Japanese rice"],
                duration_days=135,
                plant_height_cm=(100, 120),
                grain_type=GrainType.SHORT,
                amylose_content="low",
                yield_range_t_ha=(4, 5),
                drought_tolerance="low",
                flood_tolerance="low",
                salinity_tolerance="low",
                blast_susceptibility="high",
                nitrogen_requirement_kg_ha=(40, 60),
                water_requirement_mm=(1000, 1300),
                primary_regions=["Cameron Highlands"],
                preferred_seasons=["main"],
                preferred_farm_types=[FarmType.UPLAND],
                seed_price_per_50kg=250,
                seed_source="Specialty suppliers",
            )
        )

        self.add_variety(
            PadiVariety(
                id="PUTAH",
                name="Putah",
                synonyms=["Padi Putah", "Beras Putah"],
                duration_days=140,
                plant_height_cm=(130, 160),
                grain_type=GrainType.LONG,
                amylose_content="high",
                yield_range_t_ha=(3, 4),
                drought_tolerance="high",
                flood_tolerance="moderate",
                salinity_tolerance="moderate",
                blast_susceptibility="low",
                nitrogen_requirement_kg_ha=(50, 70),
                water_requirement_mm=(800, 1100),
                primary_regions=["Kelantan", "Terengganu", "Pahang"],
                preferred_seasons=["main"],
                preferred_farm_types=[FarmType.UPLAND, FarmType.LOWLAND_RAINFED],
                seed_price_per_50kg=120,
                seed_source="Local farmers",
            )
        )

        self.add_variety(
            PadiVariety(
                id="BORNE",
                name="Borneo",
                synonyms=["Padi Borneo"],
                duration_days=150,
                plant_height_cm=(120, 150),
                grain_type=GrainType.LONG,
                amylose_content="high",
                yield_range_t_ha=(3, 4),
                drought_tolerance="high",
                photoperiod_sensitive=True,
                nitrogen_requirement_kg_ha=(40, 60),
                water_requirement_mm=(700, 1000),
                primary_regions=["Sabah", "Sarawak"],
                preferred_seasons=["main"],
                preferred_farm_types=[FarmType.UPLAND],
                seed_price_per_50kg=100,
                seed_source="Local seed savers",
            )
        )

        # Specialty Varieties
        self.add_variety(
            PadiVariety(
                id="BASMATI_MY",
                name="Basmati Malaysia",
                synonyms=["Malaysia Basmati"],
                duration_days=135,
                plant_height_cm=(100, 115),
                grain_type=GrainType.AROMATIC,
                amylose_content="low",
                yield_range_t_ha=(3, 4),
                drought_tolerance="moderate",
                blast_susceptibility="moderate",
                nitrogen_requirement_kg_ha=(60, 80),
                water_requirement_mm=(900, 1200),
                primary_regions=["Selangor"],
                preferred_seasons=["main"],
                preferred_farm_types=[FarmType.LOWLAND_IRRIGATED],
                seed_price_per_50kg=300,
                seed_source="Specialty growers",
            )
        )

    def add_variety(self, variety: PadiVariety):
        """Add a variety to the database."""
        self.varieties[variety.id] = variety
        for synonym in variety.synonyms:
            self.varieties[synonym.upper()] = variety

    def get_variety(self, variety_id: str) -> Optional[PadiVariety]:
        """Get a variety by ID or synonym."""
        return self.varieties.get(variety_id.upper())

    def search_varieties(
        self,
        farm_type: Optional[FarmType] = None,
        region: Optional[str] = None,
        season: Optional[str] = None,
        min_yield: Optional[float] = None,
        max_duration: Optional[int] = None,
        grain_type: Optional[GrainType] = None,
    ) -> List[PadiVariety]:
        """Search varieties based on criteria."""
        results = list(self.varieties.values())

        # Remove duplicates from synonyms
        seen_ids = set()
        unique_results = []
        for v in results:
            if v.id not in seen_ids:
                seen_ids.add(v.id)
                unique_results.append(v)

        filtered = []
        for v in unique_results:
            if farm_type and v.matches_farm_type(farm_type) < 0.3:
                continue
            if region and region not in v.primary_regions:
                continue
            if season and season not in v.preferred_seasons:
                continue
            if min_yield and v.yield_range_t_ha[0] < min_yield:
                continue
            if max_duration and v.duration_days > max_duration:
                continue
            if grain_type and v.grain_type != grain_type:
                continue
            filtered.append(v)

        return filtered

    def _load_from_db(self):
        """Load varieties from SQLite database."""
        # Implementation for loading from existing database
        pass


# =============================================================================
# IMAGE FEATURE EXTRACTOR (SIMULATION)
# =============================================================================


class ImageFeatureExtractor:
    """
    Extract features from rice plant images for variety identification.

    In production, this would use a trained CNN model (e.g., MobileNet, EfficientNet).
    This implementation provides the interface and simulated features.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path
        self.feature_dimensions = 1280  # Standard for MobileNetV2

    def load_model(self):
        """Load the trained model from disk."""
        if self.model_path and os.path.exists(self.model_path):
            # In production: load actual model
            # self.model = tf.keras.models.load_model(self.model_path)
            pass

    def extract_features(self, image_path: str) -> Dict[str, Any]:
        """
        Extract visual features from an image.

        Returns a dictionary of extracted features.
        """
        # Simulated feature extraction
        # In production, this would:
        # 1. Preprocess image (resize, normalize)
        # 2. Run through CNN model
        # 3. Extract features from penultimate layer

        features = {
            # Leaf characteristics
            "leaf_color_score": random.uniform(0.3, 0.9),  # Green intensity
            "leaf_width_score": random.uniform(0.2, 0.8),  # Leaf width
            "leaf_angle_score": random.uniform(0.4, 0.8),  # Erectness
            # Plant morphology
            "plant_height_estimate_cm": random.uniform(70, 130),
            "tillering_estimate": random.randint(8, 25),
            "plant_density_score": random.uniform(0.3, 0.9),
            # Grain characteristics (if panicle visible)
            "grain_length_estimate_mm": random.uniform(6, 10),
            "grain_shape_score": random.uniform(0.3, 0.9),
            "awn_presence_score": random.uniform(0, 0.3),
            # Health indicators
            "health_score": random.uniform(0.6, 1.0),
            "disease_indicator": random.uniform(0, 0.3),
            # Confidence and metadata
            "confidence": random.uniform(0.7, 0.95),
            "image_quality": "good",
            "detected_growth_stage": random.choice(
                [
                    GrowthStage.TILLERING.value,
                    GrowthStage.FLOWERING.value,
                    GrowthStage.GRAIN_FILLING.value,
                ]
            ),
        }

        return features

    def extract_from_multiple_images(self, image_paths: List[str]) -> Dict[str, Any]:
        """Extract features from multiple images and aggregate."""
        all_features = [self.extract_features(p) for p in image_paths]

        # Average continuous features
        aggregated = {
            "leaf_color_score": sum(f["leaf_color_score"] for f in all_features)
            / len(all_features),
            "leaf_width_score": sum(f["leaf_width_score"] for f in all_features)
            / len(all_features),
            "plant_height_estimate_cm": sum(
                f["plant_height_estimate_cm"] for f in all_features
            )
            / len(all_features),
            "grain_length_estimate_mm": sum(
                f["grain_length_estimate_mm"] for f in all_features
            )
            / len(all_features),
            "confidence": sum(f["confidence"] for f in all_features)
            / len(all_features),
            "image_count": len(image_paths),
            "consistent_detections": True,
        }

        return aggregated


# =============================================================================
# IDENTIFICATION ENGINE
# =============================================================================


class PadiIdentificationEngine:
    """
    Main engine for identifying padi varieties using multiple methods.
    """

    def __init__(
        self,
        variety_db: Optional[VarietyDatabase] = None,
        image_extractor: Optional[ImageFeatureExtractor] = None,
    ):
        self.variety_db = variety_db or VarietyDatabase()
        self.image_extractor = image_extractor or ImageFeatureExtractor()
        self.identification_history: List[IdentificationResult] = []

    def identify(self, request: IdentificationRequest) -> IdentificationResult:
        """
        Identify padi variety using available information.

        Combines multiple identification methods based on available data.
        """
        result = IdentificationResult()
        scores: Dict[str, Tuple[PadiVariety, float]] = {}

        # Method 1: Farmer Selection (highest confidence if provided)
        if request.farmer_selection:
            variety = self.variety_db.get_variety(request.farmer_selection)
            if variety:
                scores["farmer_selection"] = (variety, 0.95)
                result.method = IdentificationMethod.FARMER_SELECTION

        # Method 2: Image Recognition
        if request.image_path:
            features = self.image_extractor.extract_features(request.image_path)
            image_matches = self._match_by_image_features(features)
            for variety, score in image_matches:
                scores[f"image_{variety.id}"] = (variety, score * 0.85)

        if request.image_features:
            image_matches = self._match_by_image_features(request.image_features)
            for variety, score in image_matches:
                scores[f"image_{variety.id}"] = (variety, score * 0.85)

        # Method 3: GPS + Season Inference
        if request.location:
            location_matches = self._match_by_location(
                request.location, request.season, request.farm_type
            )
            for variety, score in location_matches:
                scores[f"location_{variety.id}"] = (variety, score * 0.6)

        # Method 4: Characteristic Fallback
        if request.characteristics:
            char_matches = self._match_by_characteristics(request.characteristics)
            for variety, score in char_matches:
                scores[f"char_{variety.id}"] = (variety, score * 0.5)

        # Aggregate scores and find best match
        if not scores:
            # No identification data provided - return default
            result.variety = self._get_default_variety(request.farm_type)
            result.confidence = 0.3
            result.method = IdentificationMethod.CONFIDENCE_BASED
            result.recommendations = [
                "Unable to identify variety. Using default recommendation.",
                "Please provide more information (image, location, or selection).",
            ]
            return result

        # Combine scores for each variety
        variety_scores: Dict[str, Tuple[PadiVariety, float, List[str]]] = {}
        for key, (variety, score) in scores.items():
            method_type = key.split("_")[0]
            if variety.id not in variety_scores:
                variety_scores[variety.id] = (variety, 0, [])
            v, total, methods = variety_scores[variety.id]
            variety_scores[variety.id] = (v, total + score, methods + [method_type])

        # Find best match
        best_id = max(variety_scores.keys(), key=lambda k: variety_scores[k][1])
        best_variety, total_score, methods = variety_scores[best_id]

        result.variety = best_variety
        result.confidence = min(total_score / len(scores), 1.0)
        result.metadata["methods_used"] = list(set(methods))

        # Generate alternatives
        alternatives = [
            (v, s)
            for v, s, _ in sorted(
                variety_scores.values(), key=lambda x: x[1], reverse=True
            )[1:4]  # Top 3 alternatives
        ]
        result.alternative_matches = alternatives

        # Estimate growth stage
        result.growth_stage = self._estimate_growth_stage(
            request.planting_date, result.variety
        )

        # Generate recommendations
        result.recommendations = self._generate_recommendations(
            result.variety, result.growth_stage, request.farm_type
        )

        # Store in history
        self.identification_history.append(result)

        return result

    def _match_by_image_features(
        self, features: Dict[str, Any]
    ) -> List[Tuple[PadiVariety, float]]:
        """Match varieties based on extracted image features."""
        matches = []

        height = features.get("plant_height_estimate_cm", 100)

        for variety in self.variety_db.varieties.values():
            if variety.id in [v.id for v, _ in matches]:
                continue

            score = 0.0

            # Height matching
            min_h, max_h = variety.plant_height_cm
            if min_h <= height <= max_h:
                score += 0.4
            elif abs(height - (min_h + max_h) / 2) < 20:
                score += 0.2

            # Grain length matching
            grain_mm = features.get("grain_length_estimate_mm")
            if grain_mm:
                expected_mm = 6 if variety.grain_type == GrainType.LONG else 5
                if abs(grain_mm - expected_mm) < 1.5:
                    score += 0.3

            # Add small random factor for simulation
            score += random.uniform(0, 0.2)

            if score > 0.3:
                matches.append((variety, min(score, 1.0)))

        return sorted(matches, key=lambda x: x[1], reverse=True)

    def _match_by_location(
        self,
        location: GeoLocation,
        season: Optional[str],
        farm_type: Optional[FarmType],
    ) -> List[Tuple[PadiVariety, float]]:
        """Match varieties based on GPS location and season."""
        matches = []

        climate_zone = location.get_climate_zone()

        for variety in self.variety_db.varieties.values():
            if variety.id in [v.id for v, s in matches]:
                continue

            score = 0.0

            # Region matching
            for region in variety.primary_regions:
                region_lower = region.lower()
                if climate_zone == "north_malaysia" and region_lower in [
                    "kedah",
                    "perlis",
                    "perak",
                ]:
                    score += 0.4
                elif climate_zone == "central_malaysia" and region_lower in [
                    "perak",
                    "selangor",
                ]:
                    score += 0.3
                elif climate_zone == "east_malaysia" and region_lower in [
                    "sabah",
                    "sarawak",
                ]:
                    score += 0.5

            # Season matching
            if season and season in variety.preferred_seasons:
                score += 0.3

            # Farm type matching
            if farm_type:
                score += variety.matches_farm_type(farm_type) * 0.3

            if score > 0.2:
                matches.append((variety, min(score, 1.0)))

        return sorted(matches, key=lambda x: x[1], reverse=True)

    def _match_by_characteristics(
        self, characteristics: PlantCharacteristics
    ) -> List[Tuple[PadiVariety, float]]:
        """Match varieties based on plant characteristics."""
        matches = []

        for variety in self.variety_db.varieties.values():
            if variety.id in [v.id for v, s in matches]:
                continue

            score = 0.0
            comparisons = 0

            # Height matching
            if characteristics.plant_height_cm:
                comparisons += 1
                min_h, max_h = variety.plant_height_cm
                if min_h <= characteristics.plant_height_cm <= max_h:
                    score += 1.0

            # Tillering capacity
            if characteristics.tillering_capacity:
                comparisons += 1
                expected = "high" if variety.yield_range_t_ha[1] > 6 else "moderate"
                if characteristics.tillering_capacity.lower() == expected:
                    score += 1.0

            # Straw strength
            if characteristics.straw_strength:
                comparisons += 1
                if characteristics.straw_strength.lower() == "strong":
                    score += 0.5

            if comparisons > 0 and score / comparisons > 0.4:
                matches.append((variety, score / comparisons))

        return sorted(matches, key=lambda x: x[1], reverse=True)

    def _get_default_variety(self, farm_type: Optional[FarmType]) -> PadiVariety:
        """Get default variety when no identification data available."""
        if farm_type == FarmType.UPLAND:
            return self.variety_db.get_variety("PUTAH")
        return self.variety_db.get_variety("MR219")

    def _estimate_growth_stage(
        self, planting_date: Optional[date], variety: PadiVariety
    ) -> GrowthStage:
        """Estimate current growth stage based on planting date."""
        if not planting_date:
            return GrowthStage.TILLERING  # Default assumption

        days_since_planting = (date.today() - planting_date).days
        total_days = variety.duration_days

        # Growth stage thresholds (approximate percentages)
        thresholds = {
            GrowthStage.GERMINATION: 0.05,
            GrowthStage.SEEDLING: 0.15,
            GrowthStage.TILLERING: 0.30,
            GrowthStage.PANICLE_INITIATION: 0.40,
            GrowthStage.BOOTING: 0.55,
            GrowthStage.FLOWERING: 0.70,
            GrowthStage.GRAIN_FILLING: 0.85,
            GrowthStage.MATURITY: 0.95,
        }

        progress = days_since_planting / total_days

        for stage, threshold in sorted(
            thresholds.items(), key=lambda x: x[1], reverse=True
        ):
            if progress >= threshold:
                return stage

        return GrowthStage.GERMINATION

    def _generate_recommendations(
        self,
        variety: PadiVariety,
        growth_stage: GrowthStage,
        farm_type: Optional[FarmType],
    ) -> List[str]:
        """Generate recommendations based on identified variety and growth stage."""
        recommendations = []

        # Variety-specific recommendations
        recommendations.append(
            f"Identified as {variety.name}. "
            f"Expected yield: {variety.yield_range_t_ha[0]}-{variety.yield_range_t_ha[1]} t/ha."
        )

        # Growth stage recommendations
        stage_recommendations = {
            GrowthStage.GERMINATION: "Monitor for proper germination. Ensure adequate moisture.",
            GrowthStage.SEEDLING: "Apply light basal fertilizer. Protect from pests.",
            GrowthStage.TILLERING: f"Apply first top-dressing with {variety.nitrogen_requirement_kg_ha[0] // 3} kg N/ha.",
            GrowthStage.PANICLE_INITIATION: "Second top-dressing recommended. Monitor for disease.",
            GrowthStage.BOOTING: "Ensure adequate water. Check for pest infestation.",
            GrowthStage.FLOWERING: "Maintain water levels. Avoid pesticide application.",
            GrowthStage.GRAIN_FILLING: "Reduce nitrogen. Monitor for grain-filling diseases.",
            GrowthStage.MATURITY: "Prepare for harvest. Drain field 2-3 weeks before.",
        }
        recommendations.append(stage_recommendations.get(growth_stage, ""))

        # Disease susceptibility warnings
        if variety.blast_susceptibility == "high":
            recommendations.append(
                "Warning: High blast susceptibility. Monitor weather conditions."
            )
        if variety.tungro_susceptibility == "high":
            recommendations.append(
                "Warning: Monitor for leafhopper vectors to prevent tungro."
            )

        return recommendations

    def get_variety_comparison(self, variety_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple varieties side by side."""
        varieties = [self.variety_db.get_variety(vid) for vid in variety_ids]
        varieties = [v for v in varieties if v is not None]

        comparison = {
            "varieties": [v.name for v in varieties],
            "duration_days": [v.duration_days for v in varieties],
            "yield_range": [v.yield_range_t_ha for v in varieties],
            "nitrogen_requirement": [v.nitrogen_requirement_kg_ha for v in varieties],
            "disease_profile": {
                "blast": [v.blast_susceptibility for v in varieties],
                "blight": [v.blight_susceptibility for v in varieties],
                "tungro": [v.tungro_susceptibility for v in varieties],
            },
            "tolerance_profile": {
                "drought": [v.drought_tolerance for v in varieties],
                "flood": [v.flood_tolerance for v in varieties],
                "salinity": [v.salinity_tolerance for v in varieties],
            },
            "seed_cost": [v.seed_price_per_50kg for v in varieties],
        }

        return comparison


# =============================================================================
# API INTERFACE
# =============================================================================


class PadiIdentificationAPI:
    """REST API interface for the identification system."""

    def __init__(self):
        self.engine = PadiIdentificationEngine()
        self.db = self.engine.variety_db

    def identify_from_image(self, image_path: str) -> Dict[str, Any]:
        """Identify variety from image upload."""
        request = IdentificationRequest(image_path=image_path)
        result = self.engine.identify(request)
        return self._result_to_dict(result)

    def identify_from_selection(
        self,
        variety_name: str,
        location: Optional[Dict] = None,
        planting_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Identify from farmer's variety selection."""
        request = IdentificationRequest(farmer_selection=variety_name)

        if location:
            request.location = GeoLocation(**location)
        if planting_date:
            request.planting_date = datetime.fromisoformat(planting_date).date()

        result = self.engine.identify(request)
        return self._result_to_dict(result)

    def identify_from_location(
        self,
        latitude: float,
        longitude: float,
        season: str = "main",
        farm_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Identify recommended varieties for a location."""
        request = IdentificationRequest(
            location=GeoLocation(latitude=latitude, longitude=longitude),
            season=season,
            farm_type=FarmType(farm_type) if farm_type else None,
        )
        result = self.engine.identify(request)
        return self._result_to_dict(result)

    def suggest_varieties(
        self,
        farm_type: Optional[str] = None,
        region: Optional[str] = None,
        min_yield: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Get suggested varieties based on criteria."""
        varieties = self.db.search_varieties(
            farm_type=FarmType(farm_type) if farm_type else None,
            region=region,
            min_yield=min_yield,
        )
        return [v.to_dict() for v in varieties]

    def _result_to_dict(self, result: IdentificationResult) -> Dict[str, Any]:
        """Convert result to dictionary for JSON response."""
        return {
            "variety": result.variety.to_dict() if result.variety else None,
            "confidence": result.confidence,
            "method": result.method.value,
            "growth_stage": result.growth_stage.value if result.growth_stage else None,
            "days_to_maturity_estimate": result.days_to_maturity_estimate,
            "recommendations": result.recommendations,
            "alternatives": [
                {"name": v.name, "confidence": s} for v, s in result.alternative_matches
            ],
            "metadata": result.metadata,
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================


def main():
    """Command-line interface for testing."""
    api = PadiIdentificationAPI()

    print("=" * 60)
    print("PADI IDENTIFICATION SYSTEM - CLI")
    print("=" * 60)

    # Demo: Identify from location
    print("\n1. Varieties for Kedah region:")
    suggestions = api.suggest_varieties(region="Kedah")
    for v in suggestions[:3]:
        print(
            f"   - {v['name']}: {v['yield_range_t_ha'][0]}-{v['yield_range_t_ha'][1]} t/ha"
        )

    # Demo: Identify from selection
    print("\n2. Identify by farmer selection (MR219):")
    result = api.identify_from_selection("MR219")
    print(f"   Variety: {result['variety']['name']}")
    print(f"   Confidence: {result['confidence']:.0%}")
    print(f"   Method: {result['method']}")
    print(f"   Recommendations: {result['recommendations'][0]}")

    # Demo: Identify from location
    print("\n3. Identify by GPS (Kedah):")
    result = api.identify_from_location(
        latitude=6.0, longitude=100.4, season="main", farm_type="lowland_irrigated"
    )
    print(f"   Recommended Variety: {result['variety']['name']}")
    print(f"   Confidence: {result['confidence']:.0%}")

    # Demo: Compare varieties
    print("\n4. Compare varieties MR219 vs MR263:")
    comparison = api.engine.get_variety_comparison(["MR219", "MR263"])
    print(f"   Duration: {comparison['duration_days']}")
    print(f"   Yield: {comparison['yield_range']}")
    print(f"   Blast susceptibility: {comparison['disease_profile']['blast']}")

    print("\n" + "=" * 60)
    print("Demo complete!")


if __name__ == "__main__":
    main()
