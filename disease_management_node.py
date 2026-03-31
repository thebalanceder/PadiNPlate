"""
Disease Management Node
======================
Comprehensive disease identification and management system for padi.

Features:
- Disease identification from symptoms
- Disease library with treatments
- IPM recommendations
- Chemical and organic treatments
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from enum import Enum
import random


class DiseaseSeverity(Enum):
    EARLY = "early"
    MODERATE = "moderate"
    SEVERE = "severe"


class TreatmentType(Enum):
    CULTURAL = "cultural"
    BIOLOGICAL = "biological"
    CHEMICAL = "chemical"


@dataclass
class DiseaseInfo:
    name: str
    scientific_name: str
    pathogen_type: str
    affected_parts: List[str]
    symptoms: Dict[str, str]
    conditions_favored: Dict[str, Any]
    susceptibility_by_variety: Dict[str, str]

    cultural_control: List[str]
    biological_control: List[str]
    chemical_control: List[Dict]

    risk_factors: List[str]
    prevention_tips: List[str]


@dataclass
class DiagnosisRequest:
    visible_symptoms: List[str]
    plant_part_affected: str
    growth_stage: str
    weather_recent: Optional[Dict] = None
    image_features: Optional[Dict] = None


@dataclass
class DiseaseDiagnosis:
    disease: str
    confidence: float
    severity: DiseaseSeverity
    alternative_diagnoses: List[Dict]
    management_plan: Dict


@dataclass
class TreatmentRecommendation:
    treatment_type: TreatmentType
    product_name: str
    active_ingredient: str
    application_rate: str
    pre_harvest_interval_days: int
    safety_notes: str
    cost_rm_per_application: float


class DiseaseDatabase:
    """Database of padi diseases."""

    def __init__(self):
        self.diseases = {}
        self._initialize_diseases()

    def _initialize_diseases(self):
        self.diseases["RICE_BLAST"] = DiseaseInfo(
            name="Rice Blast",
            scientific_name="Magnaporthe oryzae",
            pathogen_type="Fungus",
            affected_parts=["Leaves", "Stems", "Panicles"],
            symptoms={
                "leaf": "Diamond-shaped lesions with gray centers, yellow halos",
                "neck": "Dark brown rot at panicle neck, white fungal growth",
                "node": "Dark lesions on stem nodes",
            },
            conditions_favored={
                "temperature": "25-28°C",
                "humidity": ">90%",
                "nitrogen": "Excess N increases susceptibility",
            },
            susceptibility_by_variety={
                "MR219": "moderate",
                "MR220": "moderate",
                "MR263": "low",
                "Koshihikari": "high",
                "Putah": "low",
            },
            cultural_control=[
                "Use resistant varieties",
                "Balanced fertilization",
                "Avoid water stress",
                "Proper plant spacing",
            ],
            biological_control=["Bacillus subtilis", "Trichoderma harzianum"],
            chemical_control=[
                {
                    "name": "Tricyclazole 250EC",
                    "ai": "Tricyclazole",
                    "rate": "250ml/ha",
                    "phi": 30,
                },
                {
                    "name": "Hexaconazole 5SC",
                    "ai": "Hexaconazole",
                    "rate": "500ml/ha",
                    "phi": 21,
                },
                {
                    "name": "Isoprothiolane 40EC",
                    "ai": "Isoprothiolane",
                    "rate": "1L/ha",
                    "phi": 30,
                },
            ],
            risk_factors=["High humidity", "Excess nitrogen", "Drought stress"],
            prevention_tips=[
                "Use certified seed",
                "Apply balanced N",
                "Monitor weather",
            ],
        )

        self.diseases["BACTERIAL_LEAF_BLIGHT"] = DiseaseInfo(
            name="Bacterial Leaf Blight",
            scientific_name="Xanthomonas oryzae pv. oryzae",
            pathogen_type="Bacteria",
            affected_parts=["Leaves"],
            symptoms={
                "early": "Water-soaked lesions from leaf tip",
                "severe": "Yellow to white lesions, bacterial ooze",
                "kresek": "Seedling wilting and death",
            },
            conditions_favored={
                "temperature": "25-30°C",
                "rain": "Spread by rain and wind",
                "wounds": "Infection through wounds",
            },
            susceptibility_by_variety={
                "MR219": "high",
                "MR220": "moderate",
                "MR263": "moderate",
            },
            cultural_control=[
                "Use certified clean seed",
                "Remove infected crop residues",
                "Avoid wound infection",
                "Control insect vectors",
            ],
            biological_control=["Copper-based treatments (limited effectiveness)"],
            chemical_control=[
                {
                    "name": "Streptomycin 90SP",
                    "ai": "Streptomycin",
                    "rate": "200g/ha",
                    "phi": 14,
                },
                {
                    "name": "Copper hydroxide 77WP",
                    "ai": "Copper hydroxide",
                    "rate": "1.5kg/ha",
                    "phi": 7,
                },
            ],
            risk_factors=["Heavy rain", "Strong wind", "High N"],
            prevention_tips=["Clean seed", "Resistant varieties", "Vector control"],
        )

        self.diseases["SHEATH_BLIGHT"] = DiseaseInfo(
            name="Sheath Blight",
            scientific_name="Rhizoctonia solani",
            pathogen_type="Fungus",
            affected_parts=["Leaf sheath", "Stems"],
            symptoms={
                "sheath": "Oval lesions with gray center, brown border",
                "stem": "Basal rotting, lodging in severe cases",
                "spread": "Lesions can reach leaves",
            },
            conditions_favored={
                "temperature": "28-32°C",
                "humidity": "High",
                "canopy": "Dense canopy favors spread",
            },
            susceptibility_by_variety={
                "MR219": "moderate",
                "MR220": "low",
                "MR297": "moderate",
            },
            cultural_control=[
                "Wide plant spacing",
                "Balanced N fertilization",
                "Remove infected debris",
                "Avoid excessive vegetation",
            ],
            biological_control=["Bacillus subtilis", "Pseudomonas fluorescens"],
            chemical_control=[
                {
                    "name": "Hexaconazole 75WDG",
                    "ai": "Hexaconazole",
                    "rate": "200g/ha",
                    "phi": 30,
                },
                {
                    "name": "Validamycin 3L",
                    "ai": "Validamycin",
                    "rate": "1L/ha",
                    "phi": 14,
                },
                {
                    "name": "Carbendazim 50WP",
                    "ai": "Carbendazim",
                    "rate": "500g/ha",
                    "phi": 30,
                },
            ],
            risk_factors=["Dense planting", "High N", "Warm humid weather"],
            prevention_tips=[
                "Wider spacing",
                "Split N application",
                "Field sanitation",
            ],
        )

        self.diseases["BROWN_SPOT"] = DiseaseInfo(
            name="Brown Spot",
            scientific_name="Bipolaris oryzae",
            pathogen_type="Fungus",
            affected_parts=["Leaves", "Grains"],
            symptoms={
                "leaf": "Small brown elliptical spots with yellow halos",
                "grain": "Dark spots on lemma/palea",
                "severe": "Extensive leaf death",
            },
            conditions_favored={
                "nutrition": "Nutrient deficiency (especially K)",
                "drought": "Drought stress",
                "temperature": "High temperature",
            },
            susceptibility_by_variety={
                "MR219": "low",
                "MR220": "low",
                "Koshihikari": "moderate",
            },
            cultural_control=[
                "Balanced fertilization",
                "Adequate irrigation",
                "Use certified seed",
                "Soil health improvement",
            ],
            biological_control=["Silicon supplementation"],
            chemical_control=[
                {
                    "name": "Mancozeb 80WP",
                    "ai": "Mancozeb",
                    "rate": "2kg/ha",
                    "phi": 14,
                },
                {
                    "name": "Chlorothalonil 75WP",
                    "ai": "Chlorothalonil",
                    "rate": "1.5kg/ha",
                    "phi": 14,
                },
            ],
            risk_factors=["K deficiency", "Drought", "Poor soil"],
            prevention_tips=["Balanced NPK", "Adequate K", "Irrigation"],
        )

        self.diseases["TUNGRO"] = DiseaseInfo(
            name="Tungro Virus",
            scientific_name="Rice Tungro Bacilliform Virus",
            pathogen_type="Virus",
            affected_parts=["Whole plant"],
            symptoms={
                "color": "Yellow-orange discoloration",
                "growth": "Stunted growth, reduced tillering",
                "leaves": "Mottling and yellowing",
            },
            conditions_favored={
                "vector": "High green leafhopper population",
                "season": "Early planting when vectors abundant",
                "virus_source": "Presence of infected plants",
            },
            susceptibility_by_variety={
                "MR219": "moderate",
                "MR220": "high",
                "MR263": "low",
            },
            cultural_control=[
                "Plant early to avoid peak vector period",
                "Remove infected plants",
                "Synchronized planting in area",
                "Use virus-free seed",
            ],
            biological_control=["Natural enemies of leafhoppers"],
            chemical_control=[
                {
                    "name": "Imidacloprid 200SL",
                    "ai": "Imidacloprid",
                    "rate": "125ml/ha",
                    "phi": 21,
                },
                {
                    "name": "Thiamethoxam 25WG",
                    "ai": "Thiamethoxam",
                    "rate": "100g/ha",
                    "phi": 21,
                },
            ],
            risk_factors=["Vector population", "Infected seed", "Continuous rice"],
            prevention_tips=[
                "Resistant varieties",
                "Vector control",
                "Rogue infected plants",
            ],
        )

    def get_disease(self, disease_id: str) -> Optional[DiseaseInfo]:
        return self.diseases.get(disease_id)

    def list_diseases(self) -> List[str]:
        return list(self.diseases.keys())


class DiseaseDiagnosisEngine:
    """Engine for disease diagnosis and recommendations."""

    def __init__(self):
        self.db = DiseaseDatabase()

    def diagnose(self, request: DiagnosisRequest) -> List[DiseaseDiagnosis]:
        """Diagnose disease from symptoms."""
        results = []

        # Symptom-based matching
        for disease_id, disease in self.db.diseases.items():
            score = 0.0
            matched_symptoms = []

            # Check symptom matches
            for symptom_key, symptom_text in disease.symptoms.items():
                for user_symptom in request.visible_symptoms:
                    if any(
                        word in symptom_text.lower()
                        for word in user_symptom.lower().split()
                    ):
                        score += 0.3
                        matched_symptoms.append(symptom_key)

            # Check affected part match
            if request.plant_part_affected in disease.affected_parts:
                score += 0.2

            # Weather-based risk adjustment
            if request.weather_recent:
                temp = request.weather_recent.get("temperature", 28)
                humidity = request.weather_recent.get("humidity", 75)

                fav_temp = disease.conditions_favored.get("temperature", "")
                if "25" in fav_temp or "28" in fav_temp:
                    if 24 <= temp <= 30:
                        score += 0.1

                if humidity > 80:
                    score += 0.1

            if score > 0.3:
                severity = self._estimate_severity(score, disease_id)
                management = self._generate_management_plan(disease_id, severity)

                results.append(
                    DiseaseDiagnosis(
                        disease=disease.name,
                        confidence=min(score, 0.95),
                        severity=severity,
                        alternative_diagnoses=[],
                        management_plan=management,
                    )
                )

        return sorted(results, key=lambda r: r.confidence, reverse=True)[:3]

    def _estimate_severity(self, score: float, disease_id: str) -> DiseaseSeverity:
        if score > 0.7:
            return DiseaseSeverity.SEVERE
        elif score > 0.5:
            return DiseaseSeverity.MODERATE
        else:
            return DiseaseSeverity.EARLY

    def _generate_management_plan(
        self, disease_id: str, severity: DiseaseSeverity
    ) -> Dict:
        disease = self.db.diseases[disease_id]

        plan = {
            "immediate_actions": disease.cultural_control[:3],
            "treatments": [],
            "monitoring": disease.prevention_tips[:3],
            "severity_specific": {},
        }

        # Add chemical treatments
        if severity != DiseaseSeverity.EARLY:
            for chem in disease.chemical_control[:2]:
                plan["treatments"].append(
                    {
                        "type": "chemical",
                        "product": chem["name"],
                        "active_ingredient": chem["ai"],
                        "rate": chem["rate"],
                        "phi": chem["phi"],
                    }
                )

        # Severity-specific advice
        if severity == DiseaseSeverity.SEVERE:
            plan["severity_specific"] = {
                "action": "URGENT: Apply fungicide within 48 hours",
                "additional": "Consider removing severely infected plants",
            }
        elif severity == DiseaseSeverity.MODERATE:
            plan["severity_specific"] = {
                "action": "Apply fungicide within 1 week",
                "additional": "Monitor spread daily",
            }

        return plan


class DiseaseManagementAPI:
    def __init__(self):
        self.engine = DiseaseDiagnosisEngine()

    def diagnose_from_symptoms(
        self,
        symptoms: List[str],
        plant_part: str,
        growth_stage: str = "tillering",
        temperature: float = 28,
        humidity: float = 80,
    ) -> Dict:
        request = DiagnosisRequest(
            visible_symptoms=symptoms,
            plant_part_affected=plant_part,
            growth_stage=growth_stage,
            weather_recent={"temperature": temperature, "humidity": humidity},
        )
        diagnoses = self.engine.diagnose(request)

        return {
            "diagnoses": [
                {
                    "disease": d.disease,
                    "confidence": f"{d.confidence:.0%}",
                    "severity": d.severity.value,
                    "management": d.management_plan,
                }
                for d in diagnoses
            ]
        }

    def get_disease_info(self, disease_name: str) -> Optional[Dict]:
        for disease_id, disease in self.engine.db.diseases.items():
            if disease.name.lower() == disease_name.lower():
                return {
                    "name": disease.name,
                    "scientific_name": disease.scientific_name,
                    "pathogen_type": disease.pathogen_type,
                    "affected_parts": disease.affected_parts,
                    "symptoms": disease.symptoms,
                    "treatments": disease.chemical_control,
                    "cultural_control": disease.cultural_control,
                }
        return None


def main():
    api = DiseaseManagementAPI()

    print("=" * 70)
    print("DISEASE MANAGEMENT SYSTEM - CLI")
    print("=" * 70)

    print("\n📋 DIAGNOSIS FROM SYMPTOMS")
    print("-" * 70)

    result = api.diagnose_from_symptoms(
        symptoms=["diamond-shaped lesions", "gray center", "yellow halo"],
        plant_part="leaves",
        temperature=27,
        humidity=88,
    )

    for diag in result["diagnoses"]:
        print(f"\n🦠 Disease: {diag['disease']}")
        print(f"   Confidence: {diag['confidence']}")
        print(f"   Severity: {diag['severity'].upper()}")

        if diag["management"]["treatments"]:
            print(f"\n💊 Recommended Treatments:")
            for t in diag["management"]["treatments"]:
                print(f"   - {t['product']} ({t['active_ingredient']})")
                print(f"     Rate: {t['rate']} | PHI: {t['phi']} days")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
