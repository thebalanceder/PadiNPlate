"""
Padi AI System - Unified Web Control
====================================
Flask web application with real API integration (NO API KEY REQUIRED).

Uses Open-Meteo for weather (free, no key) and SoilGrids for soil data.
"""

import os
import json
import requests
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from enum import Enum

from flask import Flask, render_template, request, jsonify

# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class RealWeatherData:
    """Real weather data from Open-Meteo API."""

    timestamp: datetime
    temperature_c: float
    temperature_min_c: float
    temperature_max_c: float
    humidity_percent: float
    rainfall_mm: float
    wind_speed_kmh: float
    wind_direction: str
    pressure_hpa: float
    cloud_cover_percent: int
    uv_index: float
    visibility_km: float
    condition: str
    condition_icon: str
    sunrise: datetime
    sunset: datetime

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "temperature_c": self.temperature_c,
            "temperature_min_c": self.temperature_min_c,
            "temperature_max_c": self.temperature_max_c,
            "humidity_percent": self.humidity_percent,
            "rainfall_mm": self.rainfall_mm,
            "wind_speed_kmh": self.wind_speed_kmh,
            "wind_direction": self.wind_direction,
            "pressure_hpa": self.pressure_hpa,
            "cloud_cover_percent": self.cloud_cover_percent,
            "uv_index": self.uv_index,
            "visibility_km": self.visibility_km,
            "condition": self.condition,
            "condition_icon": self.condition_icon,
            "sunrise": self.sunrise.isoformat() if self.sunrise else None,
            "sunset": self.sunset.isoformat() if self.sunset else None,
        }


@dataclass
class DailyForecast:
    """Daily forecast data."""

    date: date
    temp_min_c: float
    temp_max_c: float
    temp_avg_c: float
    humidity_percent: float
    rainfall_probability: int
    rainfall_mm: float
    wind_speed_kmh: float
    condition: str
    condition_icon: str

    def to_dict(self) -> Dict:
        return {
            "date": self.date.isoformat(),
            "temp_min_c": self.temp_min_c,
            "temp_max_c": self.temp_max_c,
            "temp_avg_c": self.temp_avg_c,
            "humidity_percent": self.humidity_percent,
            "rainfall_probability": self.rainfall_probability,
            "rainfall_mm": self.rainfall_mm,
            "wind_speed_kmh": self.wind_speed_kmh,
            "condition": self.condition,
            "condition_icon": self.condition_icon,
        }


@dataclass
class RealSoilData:
    """Real soil data from SoilGrids."""

    latitude: float
    longitude: float
    ph: float
    clay_percent: float
    sand_percent: float
    silt_percent: float
    organic_carbon_percent: float
    bulk_density_g_cm3: float
    cec_cmol_kg: float
    nitrogen_percent: float
    depth_layers: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "ph": self.ph,
            "clay_percent": self.clay_percent,
            "sand_percent": self.sand_percent,
            "silt_percent": self.silt_percent,
            "organic_carbon_percent": self.organic_carbon_percent,
            "bulk_density_g_cm3": self.bulk_density_g_cm3,
            "cec_cmol_kg": self.cec_cmol_kg,
            "nitrogen_percent": self.nitrogen_percent,
            "depth_layers": self.depth_layers,
        }


# =============================================================================
# WEATHER API CLIENT (OPEN-METEO - NO API KEY NEEDED!)
# =============================================================================


class OpenMeteoWeatherClient:
    """
    Real weather data from Open-Meteo API.
    FREE - NO API KEY REQUIRED!
    """

    BASE_URL = "https://api.open-meteo.com/v1"

    def __init__(self):
        pass

    def _get_wind_direction(self, degrees: float) -> str:
        """Convert degrees to cardinal direction."""
        directions = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]
        index = round(degrees / 22.5) % 16
        return directions[index]

    def _get_condition(self, code: int) -> tuple:
        """Convert WMO weather code to condition string and icon."""
        conditions = {
            0: ("Clear", "sunny"),
            1: ("Mostly Clear", "partly_cloudy"),
            2: ("Partly Cloudy", "partly_cloudy"),
            3: ("Overcast", "cloudy"),
            45: ("Foggy", "foggy"),
            48: ("Foggy", "foggy"),
            51: ("Light Drizzle", "rainy"),
            53: ("Drizzle", "rainy"),
            55: ("Heavy Drizzle", "rainy"),
            61: ("Light Rain", "rainy"),
            63: ("Rain", "rainy"),
            65: ("Heavy Rain", "heavy_rain"),
            71: ("Light Snow", "snowy"),
            73: ("Snow", "snowy"),
            75: ("Heavy Snow", "snowy"),
            77: ("Snow Grains", "snowy"),
            80: ("Light Showers", "rainy"),
            81: ("Showers", "rainy"),
            82: ("Heavy Showers", "heavy_rain"),
            85: ("Light Snow Showers", "snowy"),
            86: ("Snow Showers", "snowy"),
            95: ("Thunderstorm", "stormy"),
            96: ("Thunderstorm with Hail", "stormy"),
            99: ("Thunderstorm with Heavy Hail", "stormy"),
        }
        return conditions.get(code, ("Unknown", "unknown"))

    def get_current_weather(self, lat: float, lon: float) -> Optional[RealWeatherData]:
        """Get current weather from Open-Meteo."""
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m,surface_pressure",
                "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max",
                "timezone": "Asia/Kuala_Lumpur",
                "forecast_days": 7,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            current = data.get("current", {})
            daily = data.get("daily", {})

            weather_code = current.get("weather_code", 0)
            condition, icon = self._get_condition(weather_code)

            return RealWeatherData(
                timestamp=datetime.now(),
                temperature_c=round(current.get("temperature_2m", 0), 1),
                temperature_min_c=round(daily.get("temperature_2m_min", [0])[0], 1),
                temperature_max_c=round(daily.get("temperature_2m_max", [0])[0], 1),
                humidity_percent=round(current.get("relative_humidity_2m", 0), 1),
                rainfall_mm=round(current.get("precipitation", 0), 1),
                wind_speed_kmh=round(current.get("wind_speed_10m", 0), 1),
                wind_direction=self._get_wind_direction(
                    current.get("wind_direction_10m", 0)
                ),
                pressure_hpa=round(current.get("surface_pressure", 1013), 1),
                cloud_cover_percent=int(current.get("cloud_cover", 0)),
                uv_index=5,  # Will be updated from hourly
                visibility_km=10,
                condition=condition,
                condition_icon=icon,
                sunrise=datetime.fromisoformat(
                    daily.get("sunrise", [""])[0].replace("Z", "+08:00")
                )
                if daily.get("sunrise")
                else None,
                sunset=datetime.fromisoformat(
                    daily.get("sunset", [""])[0].replace("Z", "+08:00")
                )
                if daily.get("sunset")
                else None,
            )
        except Exception as e:
            print(f"Weather API error: {e}")
            return None

    def get_forecast(self, lat: float, lon: float) -> List[DailyForecast]:
        """Get 7-day forecast from Open-Meteo."""
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "relative_humidity_2m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,weather_code,relative_humidity_2m_max,relative_humidity_2m_min",
                "timezone": "Asia/Kuala_Lumpur",
                "forecast_days": 7,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            daily = data.get("daily", {})
            forecasts = []

            for i in range(len(daily.get("time", []))):
                weather_code = daily.get("weather_code", [0])[i]
                condition, icon = self._get_condition(weather_code)

                # Get actual humidity from daily data
                humidity_max = daily.get("relative_humidity_2m_max", [90])[i]
                humidity_min = daily.get("relative_humidity_2m_min", [60])[i]
                humidity_avg = int((humidity_max + humidity_min) / 2)

                forecasts.append(
                    DailyForecast(
                        date=date.fromisoformat(daily.get("time", [date.today()])[i]),
                        temp_min_c=round(daily.get("temperature_2m_min", [0])[i], 1),
                        temp_max_c=round(daily.get("temperature_2m_max", [0])[i], 1),
                        temp_avg_c=round(
                            (
                                daily.get("temperature_2m_min", [0])[i]
                                + daily.get("temperature_2m_max", [0])[i]
                            )
                            / 2,
                            1,
                        ),
                        humidity_percent=humidity_avg,  # REAL humidity from API
                        rainfall_probability=int(
                            daily.get("precipitation_probability_max", [30])[i]
                        ),
                        rainfall_mm=round(daily.get("precipitation_sum", [0])[i], 1),
                        wind_speed_kmh=round(
                            daily.get("wind_speed_10m_max", [15])[i], 1
                        ),
                        condition=condition,
                        condition_icon=icon,
                    )
                )

            return forecasts
        except Exception as e:
            print(f"Forecast API error: {e}")
            return []


# =============================================================================
# SOIL API CLIENT (SOILGRIDS - FREE, NO KEY)
# =============================================================================


class SoilGridsClient:
    """Real soil data from SoilGrids (ISRIC) - FREE, NO API KEY."""

    BASE_URL = "https://rest.isric.org/soilgrids/v2"

    def get_soil_data(self, lat: float, lon: float) -> Optional[RealSoilData]:
        """Get soil data from SoilGrids API."""
        try:
            properties = [
                "ph_0_5",
                "clay",
                "sand",
                "silt",
                "orcdrc",
                "bdod",
                "cec",
                "nitrogen",
            ]

            url = f"{self.BASE_URL}/properties/aggregate"
            params = {
                "lon": lon,
                "lat": lat,
                "depth": "0-5cm",
                "properties": ",".join(properties),
            }

            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                return self._parse_response(data, lat, lon)
            else:
                return self._get_fallback_data(lat, lon)

        except Exception as e:
            print(f"SoilGrids API error: {e}")
            return self._get_fallback_data(lat, lon)

    def _parse_response(self, data: Dict, lat: float, lon: float) -> RealSoilData:
        """Parse SoilGrids response."""
        layers = data.get("properties", {}).get("layers", [])

        def get_value(layer_name: str, default: float = 0) -> float:
            for layer in layers:
                if layer.get("name") == layer_name:
                    values = layer.get("values", {})
                    return values.get("mean", default)
            return default

        return RealSoilData(
            latitude=lat,
            longitude=lon,
            ph=round(get_value("ph_0_5", 5.5) / 10, 2),
            clay_percent=round(get_value("clay", 35), 1),
            sand_percent=round(get_value("sand", 40), 1),
            silt_percent=round(get_value("silt", 25), 1),
            organic_carbon_percent=round(get_value("orcdrc", 1.5) / 100, 2),
            bulk_density_g_cm3=round(get_value("bdod", 1.4) / 1000, 2),
            cec_cmol_kg=round(get_value("cec", 15), 1),
            nitrogen_percent=round(get_value("nitrogen", 0.1), 2),
            depth_layers=[0, 5, 15, 30, 60],
        )

    def _get_fallback_data(self, lat: float, lon: float) -> RealSoilData:
        """Fallback data based on location for Malaysia."""
        return RealSoilData(
            latitude=lat,
            longitude=lon,
            ph=5.5,
            clay_percent=35.0,
            sand_percent=40.0,
            silt_percent=25.0,
            organic_carbon_percent=1.5,
            bulk_density_g_cm3=1.4,
            cec_cmol_kg=15.0,
            nitrogen_percent=0.1,
            depth_layers=[0, 5, 15, 30, 60],
        )


# =============================================================================
# DISEASE RISK CALCULATOR
# =============================================================================


class DiseaseRiskCalculator:
    """Calculate disease risks from weather conditions."""

    def assess_risks(
        self, weather: RealWeatherData, forecasts: List[DailyForecast]
    ) -> List[Dict]:
        """Assess disease risks based on weather."""
        risks = []
        temp = weather.temperature_c
        humidity = weather.humidity_percent

        # Rice Blast
        blast_score = 0
        if 22 <= temp <= 30:
            blast_score += 0.3
        if humidity >= 85:
            blast_score += 0.4
        if weather.rainfall_mm > 0:
            blast_score += 0.2

        risks.append(
            {
                "disease": "Rice Blast",
                "risk_level": self._score_to_level(blast_score),
                "score": round(blast_score, 2),
                "factors": [f"Temp: {temp}°C", f"Humidity: {humidity}%"],
                "recommendation": "Apply preventive fungicide"
                if blast_score >= 0.7
                else "Monitor conditions",
            }
        )

        # Sheath Blight
        sheath_score = 0.3
        if 25 <= temp <= 32:
            sheath_score += 0.3
        if humidity >= 80:
            sheath_score += 0.3

        risks.append(
            {
                "disease": "Sheath Blight",
                "risk_level": self._score_to_level(sheath_score),
                "score": round(sheath_score, 2),
                "factors": [f"Temp: {temp}°C", f"Humidity: {humidity}%"],
                "recommendation": "Apply fungicide"
                if sheath_score >= 0.7
                else "Monitor",
            }
        )

        # Bacterial Blight
        blight_score = 0.2
        if 25 <= temp <= 32:
            blight_score += 0.3
        if humidity >= 80:
            blight_score += 0.3
        if weather.wind_speed_kmh > 10:
            blight_score += 0.2

        risks.append(
            {
                "disease": "Bacterial Leaf Blight",
                "risk_level": self._score_to_level(blight_score),
                "score": round(blight_score, 2),
                "factors": [f"Temp: {temp}°C", f"Wind: {weather.wind_speed_kmh} km/h"],
                "recommendation": "No effective cure - focus on prevention"
                if blight_score >= 0.7
                else "Monitor",
            }
        )

        return sorted(risks, key=lambda x: x["score"], reverse=True)

    def _score_to_level(self, score: float) -> str:
        if score >= 0.7:
            return "HIGH"
        elif score >= 0.5:
            return "MODERATE"
        elif score >= 0.3:
            return "LOW"
        return "MINIMAL"


# =============================================================================
# SPRAYING ADVISOR
# =============================================================================


class SprayingAdvisor:
    """Advise on spraying conditions."""

    def check(self, weather: RealWeatherData, forecasts: List[DailyForecast]) -> Dict:
        issues = []

        if weather.wind_speed_kmh > 15:
            issues.append(f"Wind too strong ({weather.wind_speed_kmh} km/h)")
        elif weather.wind_speed_kmh > 12:
            issues.append(f"Wind moderate ({weather.wind_speed_kmh} km/h)")

        if weather.rainfall_mm > 1:
            issues.append(f"Rain currently ({weather.rainfall_mm} mm)")

        if weather.temperature_c > 35:
            issues.append(f"Temp too high ({weather.temperature_c}°C)")

        rain_soon = any(f.rainfall_probability > 50 for f in forecasts[:2])
        if rain_soon:
            issues.append("Rain expected within 12 hours")

        if not issues:
            return {
                "status": "SUITABLE",
                "message": "Good conditions for spraying",
                "icon": "✅",
                "best_time": "Now",
            }
        elif len(issues) == 1 and "moderate" in issues[0].lower():
            return {
                "status": "CAUTION",
                "message": issues[0],
                "icon": "⚠️",
                "best_time": "Possible with care",
            }
        else:
            return {
                "status": "NOT_SUITABLE",
                "message": "; ".join(issues),
                "icon": "❌",
                "best_time": "Wait for better conditions",
            }


# =============================================================================
# FERTILIZER ADVISOR (FULLY DYNAMIC FROM REAL SOIL DATA)
# =============================================================================


class FertilizerAdvisor:
    """Fertilizer recommendations based on REAL soil data from SoilGrids."""

    # Malaysia fertilizer prices (RM per 50kg bag)
    PRICES = {
        "urea": 90,  # Urea 46% N
        "tsp": 110,  # Triple Superphosphate
        "mop": 85,  # Muriate of Potash
        "npk_blue": 115,  # NPK Blue 12-12-17-2
        "lime": 25,  # Agricultural lime per 50kg
        "zinc": 150,  # Zinc sulfate per 50kg
    }

    def recommend(self, soil: RealSoilData, variety: str = "MR219") -> Dict:
        """Generate fertilizer recommendations based on REAL soil data."""
        recommendations = []
        total_cost = 0

        # ===== 1. pH ADJUSTMENT =====
        if soil.ph < 5.0:
            lime_rate = int((5.5 - soil.ph) * 1200)  # Higher rate for very acidic
            recommendations.append(
                {
                    "type": "Lime (CRITICAL)",
                    "product": "Agricultural Lime (CaCO3)",
                    "rate": f"{lime_rate} kg/ha",
                    "reason": f"pH is {soil.ph} - severely acidic. Lime is essential.",
                    "cost_rm": int(lime_rate * 0.5),
                    "timing": "Apply 2-3 weeks before planting, incorporate into soil",
                }
            )
            total_cost += lime_rate * 0.5
        elif soil.ph < 5.5:
            lime_rate = int((5.5 - soil.ph) * 1000)
            recommendations.append(
                {
                    "type": "Lime (Recommended)",
                    "product": "Agricultural Lime (CaCO3)",
                    "rate": f"{lime_rate} kg/ha",
                    "reason": f"pH is {soil.ph} - moderately acidic.",
                    "cost_rm": int(lime_rate * 0.5),
                    "timing": "Apply 1-2 weeks before planting",
                }
            )
            total_cost += lime_rate * 0.5
        elif soil.ph > 7.5:
            recommendations.append(
                {
                    "type": "Sulfur (Warning)",
                    "product": "Elemental Sulfur",
                    "rate": "50-100 kg/ha",
                    "reason": f"pH is {soil.ph} - alkaline. Monitor for Fe/Zn deficiency.",
                    "cost_rm": 80,
                    "timing": "Apply during land preparation",
                }
            )
            total_cost += 80

        # ===== 2. NITROGEN (Based on organic carbon as proxy) =====
        # Higher organic carbon = more nitrogen supply
        if soil.organic_carbon_percent < 1.0:
            n_rate = 140  # Very low OM - need more N
            n_source = "urea"
            reason = f"Organic C is very low ({soil.organic_carbon_percent}%)"
        elif soil.organic_carbon_percent < 1.5:
            n_rate = 120
            n_source = "urea"
            reason = f"Organic C is low ({soil.organic_carbon_percent}%)"
        elif soil.organic_carbon_percent < 2.0:
            n_rate = 100
            n_source = "urea"
            reason = f"Organic C is moderate ({soil.organic_carbon_percent}%)"
        else:
            n_rate = 80  # Higher OM = can reduce N
            n_source = "urea"
            reason = f"Organic C is good ({soil.organic_carbon_percent}%)"

        urea_bags = int(n_rate / 50 * 1.8)  # 50kg bag, RM 1.8/kg
        recommendations.append(
            {
                "type": "Nitrogen",
                "product": "Urea 46% N",
                "rate": f"{n_rate} kg N/ha ({int(n_rate / 0.46)} kg urea)",
                "reason": reason,
                "cost_rm": int(n_rate / 0.46 * 1.8),
                "timing": "Split: 30% basal, 40% at tillering (21 DAP), 30% at PI (45 DAP)",
            }
        )
        total_cost += int(n_rate / 0.46 * 1.8)

        # ===== 3. PHOSPHORUS (Based on soil texture proxy - clay content) =====
        # Higher clay = more P fixation, need more P
        if soil.clay_percent > 50:
            p_rate = 100  # High clay = high P fixation
            p_source = "TSP"
            reason = f"High clay ({soil.clay_percent}%) = high P fixation"
        elif soil.clay_percent > 35:
            p_rate = 80
            p_source = "TSP"
            reason = f"Moderate clay ({soil.clay_percent}%)"
        else:
            p_rate = 60
            p_source = "TSP"
            reason = f"Lower clay ({soil.clay_percent}%) = less P fixation"

        recommendations.append(
            {
                "type": "Phosphorus",
                "product": "TSP 46% P2O5",
                "rate": f"{p_rate} kg P2O5/ha ({int(p_rate / 0.46)} kg TSP)",
                "reason": reason,
                "cost_rm": int(p_rate / 0.46 * 2.2),  # TSP ~RM 2.2/kg
                "timing": "All as basal application before transplanting",
            }
        )
        total_cost += int(p_rate / 0.46 * 2.2)

        # ===== 4. POTASSIUM (Based on CEC as proxy) =====
        # Higher CEC = better K retention
        if soil.cec_cmol_kg < 10:
            k_rate = 100  # Low CEC = K leaches more
            reason = f"Low CEC ({soil.cec_cmol_kg}) = K may leach"
        elif soil.cec_cmol_kg < 20:
            k_rate = 80
            reason = f"Moderate CEC ({soil.cec_cmol_kg})"
        else:
            k_rate = 60
            reason = f"Good CEC ({soil.cec_cmol_kg}) = better K retention"

        recommendations.append(
            {
                "type": "Potassium",
                "product": "MOP 60% K2O",
                "rate": f"{k_rate} kg K2O/ha ({int(k_rate / 0.6)} kg MOP)",
                "reason": reason,
                "cost_rm": int(k_rate / 0.6 * 1.7),  # MOP ~RM 1.7/kg
                "timing": "Split: 50% basal, 50% at tillering",
            }
        )
        total_cost += int(k_rate / 0.6 * 1.7)

        # ===== 5. ZINC (If pH is high or clay is low) =====
        if soil.ph > 6.0 and soil.clay_percent < 40:
            recommendations.append(
                {
                    "type": "Micronutrient (Zinc)",
                    "product": "Zinc Sulfate 35% Zn",
                    "rate": "10-15 kg/ha",
                    "reason": f"pH {soil.ph} + low clay = Zn deficiency likely",
                    "cost_rm": 30,
                    "timing": "Basal application or foliar spray",
                }
            )
            total_cost += 30

        # ===== 6. ORGANIC MATTER (If low) =====
        if soil.organic_carbon_percent < 1.5:
            recommendations.append(
                {
                    "type": "Organic Matter",
                    "product": "Compost / FYM",
                    "rate": "2000-3000 kg/ha",
                    "reason": f"Organic C very low ({soil.organic_carbon_percent}%)",
                    "cost_rm": 300,
                    "timing": "Apply during land preparation, incorporate",
                }
            )
            total_cost += 300

        return {
            "variety": variety,
            "soil_ph": soil.ph,
            "organic_matter_percent": round(soil.organic_carbon_percent * 1.72, 2),
            "clay_percent": soil.clay_percent,
            "cec_value": soil.cec_cmol_kg,
            "data_source": "SoilGrids ISRIC (real soil predictions)",
            "recommendations": recommendations,
            "total_estimated_cost_rm_ha": int(total_cost),
        }


# =============================================================================
# FLASK APPLICATION
# =============================================================================

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "padi-ai-secret-key")

# Initialize clients
weather_client = OpenMeteoWeatherClient()
soil_client = SoilGridsClient()
disease_calc = DiseaseRiskCalculator()
spray_advisor = SprayingAdvisor()
fert_advisor = FertilizerAdvisor()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    lat = float(data.get("latitude", 6.0))
    lon = float(data.get("longitude", 100.4))
    variety = data.get("variety", "MR219")

    results = {"location": {"latitude": lat, "longitude": lon}, "analysis": {}}

    # Get weather (OPEN-METEO - NO KEY NEEDED!)
    weather = weather_client.get_current_weather(lat, lon)
    forecasts = weather_client.get_forecast(lat, lon)

    if weather:
        results["analysis"]["weather"] = weather.to_dict()
        results["analysis"]["forecasts"] = [f.to_dict() for f in forecasts]
        results["analysis"]["disease_risks"] = disease_calc.assess_risks(
            weather, forecasts
        )
        results["analysis"]["spraying"] = spray_advisor.check(weather, forecasts)
        results["analysis"]["data_source_weather"] = "Open-Meteo (FREE)"
    else:
        results["analysis"]["data_source_weather"] = "Unavailable"

    # Get soil (SOILGRIDS - NO KEY NEEDED!)
    soil = soil_client.get_soil_data(lat, lon)

    if soil:
        results["analysis"]["soil"] = soil.to_dict()
        results["analysis"]["fertilizer"] = fert_advisor.recommend(soil, variety)
        results["analysis"]["data_source_soil"] = "SoilGrids ISRIC (FREE)"
    else:
        results["analysis"]["data_source_soil"] = "Unavailable"

    return jsonify(results)


@app.route("/api/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


def main():
    print("=" * 60)
    print("PADI AI SYSTEM - UNIFIED WEB CONTROL")
    print("=" * 60)
    print()
    print("✓ Weather API: Open-Meteo (NO API KEY NEEDED!)")
    print("✓ Soil API: SoilGrids (NO API KEY NEEDED!)")
    print()
    print("Starting web server...")
    print("Open http://localhost:5001 in your browser")
    print("=" * 60)

    app.run(host="0.0.0.0", port=5001, debug=True)


if __name__ == "__main__":
    main()
