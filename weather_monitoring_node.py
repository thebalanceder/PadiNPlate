"""
Weather Monitoring Node
======================
Comprehensive weather monitoring and alerting system for padi farming.

Features:
- Multi-source weather data integration
- 7-day forecast with agricultural insights
- Proactive threshold-based alerts
- Disease risk forecasting
- Historical comparison analysis
- Irrigation scheduling recommendations
"""

import os
import json
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Tuple, Any, Callable
from enum import Enum
from pathlib import Path
import math
import random
import threading
import time
from collections import defaultdict
import logging

# =============================================================================
# DATA MODELS
# =============================================================================


class WeatherCondition(Enum):
    """Weather condition classification."""

    SUNNY = "sunny"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    HEAVY_RAIN = "heavy_rain"
    STORMY = "stormy"
    WINDY = "windy"
    HOT = "hot"
    COLD = "cold"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


class WeatherDataSource(Enum):
    """Weather data source types."""

    OPENWEATHER = "openweather"
    MALAYSIA_MET = "malaysia_met"
    AGRI_WEATHER = "agri_weather"
    LOCAL_STATION = "local_station"
    SIMULATED = "simulated"


@dataclass
class GeoLocation:
    """GPS coordinates for weather lookup."""

    latitude: float
    longitude: float
    altitude: Optional[float] = None


@dataclass
class CurrentWeather:
    """Current weather conditions."""

    timestamp: datetime
    temperature_c: float
    temperature_min_c: float
    temperature_max_c: float
    humidity_percent: float
    rainfall_mm: float
    rainfall_probability: float
    wind_speed_kmh: float
    wind_direction_deg: float
    wind_direction_cardinal: str
    solar_radiation_wm2: Optional[float] = None
    pressure_hpa: Optional[float] = None
    visibility_km: Optional[float] = None
    uv_index: Optional[float] = None
    cloud_cover_percent: Optional[float] = None
    condition: WeatherCondition = WeatherCondition.SUNNY
    source: WeatherDataSource = WeatherDataSource.SIMULATED

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        d["condition"] = self.condition.value
        d["source"] = self.source.value
        return d


@dataclass
class HourlyForecast:
    """Hourly weather forecast."""

    timestamp: datetime
    temperature_c: float
    humidity_percent: float
    rainfall_mm: float
    rainfall_probability: float
    wind_speed_kmh: float
    wind_direction_cardinal: str
    solar_radiation_wm2: Optional[float] = None
    condition: WeatherCondition = WeatherCondition.SUNNY

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        d["condition"] = self.condition.value
        return d


@dataclass
class DailyForecast:
    """Daily weather forecast (24-hour summary)."""

    date: date
    temperature_min_c: float
    temperature_max_c: float
    temperature_avg_c: float
    humidity_min_percent: float
    humidity_max_percent: float
    humidity_avg_percent: float
    rainfall_mm: float
    rainfall_probability: float
    rainfall_duration_hours: float
    wind_speed_max_kmh: float
    wind_speed_avg_kmh: float
    solar_radiation_mjm2: Optional[float] = None
    evapotranspiration_mm: Optional[float] = None
    condition: WeatherCondition = WeatherCondition.SUNNY
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["date"] = self.date.isoformat()
        d["condition"] = self.condition.value
        return d


@dataclass
class WeatherAlert:
    """Weather-based alert for farming activities."""

    id: str
    timestamp: datetime
    severity: AlertSeverity
    category: str
    title: str
    message: str
    recommendation: str
    source_data: Dict[str, Any] = field(default_factory=dict)
    is_read: bool = False
    is_dismissed: bool = False

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "category": self.category,
            "title": self.title,
            "message": self.message,
            "recommendation": self.recommendation,
            "is_read": self.is_read,
            "is_dismissed": self.is_dismissed,
        }


@dataclass
class DiseaseRiskAssessment:
    """Disease risk assessment based on weather conditions."""

    disease: str
    risk_level: str  # "low", "moderate", "high", "very_high"
    risk_score: float  # 0.0 - 1.0
    contributing_factors: List[str] = field(default_factory=list)
    recommendation: str = ""
    preventive_actions: List[str] = field(default_factory=list)


@dataclass
class IrrigationRecommendation:
    """Irrigation scheduling recommendation."""

    timestamp: datetime
    water_deficit_mm: float
    water_surplus_mm: float
    recommended_action: str  # "irrigate", "drain", "maintain", "no_action"
    recommended_amount_mm: float
    next_irrigation_estimate: Optional[datetime] = None
    confidence: float = 0.0
    factors: List[str] = field(default_factory=list)


@dataclass
class FarmingActivityRecommendation:
    """Recommended farming activity based on weather."""

    activity: str
    suitability: str  # "ideal", "suitable", "marginal", "not_recommended"
    timing: str  # "now", "later_today", "tomorrow", "this_week"
    hours_window: Optional[Tuple[int, int]] = None
    confidence: float = 0.0
    reason: str = ""
    alternative_timing: Optional[str] = None


@dataclass
class WeatherSummary:
    """Comprehensive weather summary for a period."""

    location: GeoLocation
    period_start: datetime
    period_end: datetime
    current: Optional[CurrentWeather] = None
    hourly_forecast: List[HourlyForecast] = field(default_factory=list)
    daily_forecast: List[DailyForecast] = field(default_factory=list)
    alerts: List[WeatherAlert] = field(default_factory=list)
    disease_risks: List[DiseaseRiskAssessment] = field(default_factory=list)
    irrigation_recommendation: Optional[IrrigationRecommendation] = None
    activity_recommendations: List[FarmingActivityRecommendation] = field(
        default_factory=list
    )


# =============================================================================
# WEATHER THRESHOLDS
# =============================================================================


class WeatherThresholds:
    """Configurable thresholds for weather-based alerts."""

    # Temperature thresholds (Celsius)
    TEMP_HIGH_DANGER = 38
    TEMP_HIGH_WARNING = 35
    TEMP_OPTIMAL_MIN = 20
    TEMP_OPTIMAL_MAX = 32
    TEMP_LOW_WARNING = 15
    TEMP_LOW_DANGER = 10

    # Rainfall thresholds (mm)
    RAINFALL_LIGHT = 5
    RAINFALL_MODERATE = 25
    RAINFALL_HEAVY = 50
    RAINFALL_VERY_HEAVY = 100

    # Wind thresholds (km/h)
    WIND_SPRAY_DANGER = 15
    WIND_SPRAY_WARNING = 12
    WIND_STRONG = 30
    WIND_SEVERE = 50

    # Humidity thresholds (%)
    HUMIDITY_HIGH_DISEASE = 85
    HUMIDITY_HIGH_WARNING = 80
    HUMIDITY_LOW_WARNING = 40

    # Disease risk thresholds
    BLAST_TEMP_MIN = 22
    BLAST_TEMP_MAX = 30
    BLAST_HUMIDITY = 85
    BLAST_DURATION_HOURS = 8

    BLAST_NECK_TEMP_MIN = 20
    BLAST_NECK_TEMP_MAX = 28
    BLAST_NECK_HUMIDITY = 90

    SHEATH_BLIGHT_TEMP_MIN = 25
    SHEATH_BLIGHT_TEMP_MAX = 32
    SHEATH_BLIGHT_HUMIDITY = 80

    # Leaf wetness duration for disease (hours)
    LEAF_WETNESS_CRITICAL = 10
    LEAF_WETNESS_WARNING = 6

    @classmethod
    def set_regional_thresholds(cls, region: str):
        """Adjust thresholds based on region."""
        if region == "southern_malaysia":
            cls.TEMP_HIGH_WARNING = 34
            cls.HUMIDITY_HIGH_DISEASE = 88


# =============================================================================
# WEATHER DATA PROVIDER (Base Class)
# =============================================================================


class WeatherDataProvider:
    """Base class for weather data providers."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.name = "base"

    def get_current_weather(self, location: GeoLocation) -> CurrentWeather:
        """Get current weather conditions."""
        raise NotImplementedError

    def get_hourly_forecast(
        self, location: GeoLocation, hours: int = 48
    ) -> List[HourlyForecast]:
        """Get hourly forecast."""
        raise NotImplementedError

    def get_daily_forecast(
        self, location: GeoLocation, days: int = 7
    ) -> List[DailyForecast]:
        """Get daily forecast."""
        raise NotImplementedError

    def get_historical_weather(
        self, location: GeoLocation, start_date: date, end_date: date
    ) -> List[Dict]:
        """Get historical weather data."""
        raise NotImplementedError


# =============================================================================
# SIMULATED WEATHER PROVIDER (For Development)
# =============================================================================


class SimulatedWeatherProvider(WeatherDataProvider):
    """Simulated weather provider for development and testing."""

    def __init__(self, seed: Optional[int] = None):
        super().__init__()
        self.name = "simulated"
        self.rng = random.Random(seed)

        # Base climate for Malaysia (tropical)
        self.base_temp = 28
        self.base_humidity = 75
        self.monsoon_season = True  # Simulate monsoon

    def _generate_condition(
        self, humidity: float, rainfall_prob: float
    ) -> WeatherCondition:
        """Generate weather condition from parameters."""
        if rainfall_prob > 80:
            return WeatherCondition.HEAVY_RAIN
        elif rainfall_prob > 50:
            return WeatherCondition.RAINY
        elif humidity > 85:
            return WeatherCondition.CLOUDY
        elif humidity > 70:
            return WeatherCondition.PARTLY_CLOUDY
        else:
            return WeatherCondition.SUNNY

    def _get_cardinal_direction(self, degrees: float) -> str:
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

    def get_current_weather(self, location: GeoLocation) -> CurrentWeather:
        """Generate simulated current weather."""
        hour = datetime.now().hour

        # Daily temperature variation
        temp_variation = 5 * math.sin((hour - 6) * math.pi / 12)

        # Humidity inversely related to temperature
        base_humidity = 80 - (hour - 12) * 2 if 6 <= hour <= 18 else 70
        humidity = max(50, min(95, base_humidity + self.rng.gauss(0, 5)))

        # Rainfall more likely in afternoon
        rainfall_prob = 30 + (10 if 14 <= hour <= 16 else 0) + self.rng.randint(-10, 20)
        rainfall_prob = max(0, min(100, rainfall_prob))

        rainfall_mm = 0
        if rainfall_prob > 60:
            rainfall_mm = self.rng.uniform(0.5, 15)

        # Wind with occasional gusts
        wind_speed = self.rng.uniform(5, 20)
        wind_direction = self.rng.uniform(0, 360)

        return CurrentWeather(
            timestamp=datetime.now(),
            temperature_c=round(
                self.base_temp + temp_variation + self.rng.gauss(0, 2), 1
            ),
            temperature_min_c=round(self.base_temp - 3, 1),
            temperature_max_c=round(self.base_temp + temp_variation + 5, 1),
            humidity_percent=round(humidity, 1),
            rainfall_mm=round(rainfall_mm, 1),
            rainfall_probability=round(rainfall_prob, 1),
            wind_speed_kmh=round(wind_speed, 1),
            wind_direction_deg=round(wind_direction, 0),
            wind_direction_cardinal=self._get_cardinal_direction(wind_direction),
            solar_radiation_wm2=self.rng.randint(200, 900) if 7 <= hour <= 18 else 0,
            pressure_hpa=self.rng.randint(1008, 1015),
            visibility_km=self.rng.uniform(5, 20)
            if rainfall_mm < 5
            else self.rng.uniform(2, 8),
            uv_index=self.rng.uniform(5, 11)
            if 10 <= hour <= 15
            else self.rng.uniform(1, 5),
            cloud_cover_percent=self.rng.randint(20, 80),
            condition=self._generate_condition(humidity, rainfall_prob),
            source=WeatherDataSource.SIMULATED,
        )

    def get_hourly_forecast(
        self, location: GeoLocation, hours: int = 48
    ) -> List[HourlyForecast]:
        """Generate simulated hourly forecast."""
        forecasts = []
        base_time = datetime.now().replace(minute=0, second=0, microsecond=0)

        for i in range(1, hours + 1):
            forecast_time = base_time + timedelta(hours=i)
            hour = forecast_time.hour

            # Temperature cycle
            temp_cycle = 6 * math.sin((hour - 6) * math.pi / 12)
            temp = self.base_temp + temp_cycle + self.rng.gauss(0, 1.5)

            # Humidity cycle
            humidity_cycle = -15 * math.sin((hour - 14) * math.pi / 12)
            humidity = 75 + humidity_cycle + self.rng.gauss(0, 5)

            # Rainfall pattern (afternoon thunderstorms common in Malaysia)
            rainfall_prob = (
                30 + (20 if 13 <= hour <= 17 else 0) + self.rng.randint(-15, 25)
            )
            rainfall_prob = max(0, min(100, rainfall_prob))

            rainfall_mm = 0
            if rainfall_prob > 70:
                rainfall_mm = self.rng.uniform(1, 20)

            wind_speed = self.rng.uniform(5, 25)
            wind_direction = self.rng.uniform(0, 360)

            forecasts.append(
                HourlyForecast(
                    timestamp=forecast_time,
                    temperature_c=round(temp, 1),
                    humidity_percent=round(max(40, min(98, humidity)), 1),
                    rainfall_mm=round(rainfall_mm, 1),
                    rainfall_probability=round(rainfall_prob, 1),
                    wind_speed_kmh=round(wind_speed, 1),
                    wind_direction_cardinal=self._get_cardinal_direction(
                        wind_direction
                    ),
                    solar_radiation_wm2=self.rng.randint(100, 850)
                    if 7 <= hour <= 18
                    else 0,
                    condition=self._generate_condition(humidity, rainfall_prob),
                )
            )

        return forecasts

    def get_daily_forecast(
        self, location: GeoLocation, days: int = 7
    ) -> List[DailyForecast]:
        """Generate simulated daily forecast."""
        forecasts = []
        today = date.today()

        for i in range(days):
            forecast_date = today + timedelta(days=i)

            # Seasonal variation
            month = forecast_date.month
            is_monsoon = month in [9, 10, 11, 12, 1, 2]

            # Higher rainfall during monsoon
            base_rainfall_prob = 70 if is_monsoon else 40

            temp_min = self.base_temp - 4 + self.rng.gauss(0, 1)
            temp_max = self.base_temp + 8 + self.rng.gauss(0, 2)
            humidity_min = 60 + self.rng.randint(-10, 10)
            humidity_max = 90 + self.rng.randint(-5, 5)

            rainfall_prob = base_rainfall_prob + self.rng.randint(-20, 30)
            rainfall_mm = 0
            if rainfall_prob > 50:
                rainfall_mm = self.rng.uniform(5, 40)
            elif rainfall_prob > 70:
                rainfall_mm = self.rng.uniform(20, 80)

            wind_speed_avg = self.rng.uniform(8, 18)
            wind_speed_max = wind_speed_avg + self.rng.uniform(5, 15)

            # Sunrise/sunset for Malaysia
            sunrise_hour = 7 if month in [3, 4, 5, 6, 7, 8, 9] else 7.5
            sunset_hour = 19 if month in [3, 4, 5, 6, 7, 8, 9] else 18.5

            forecasts.append(
                DailyForecast(
                    date=forecast_date,
                    temperature_min_c=round(temp_min, 1),
                    temperature_max_c=round(temp_max, 1),
                    temperature_avg_c=round((temp_min + temp_max) / 2, 1),
                    humidity_min_percent=round(max(40, humidity_min), 1),
                    humidity_max_percent=round(min(98, humidity_max), 1),
                    humidity_avg_percent=round((humidity_min + humidity_max) / 2, 1),
                    rainfall_mm=round(rainfall_mm, 1),
                    rainfall_probability=round(max(0, min(100, rainfall_prob)), 1),
                    rainfall_duration_hours=round(rainfall_mm / 10, 1),
                    wind_speed_max_kmh=round(wind_speed_max, 1),
                    wind_speed_avg_kmh=round(wind_speed_avg, 1),
                    solar_radiation_mjm2=round(self.rng.uniform(15, 25), 1),
                    evapotranspiration_mm=round(self.rng.uniform(3, 6), 1),
                    condition=self._generate_condition(humidity_max, rainfall_prob),
                    sunrise=datetime.combine(
                        forecast_date,
                        datetime.min.time().replace(
                            hour=int(sunrise_hour), minute=int((sunrise_hour % 1) * 60)
                        ),
                    ),
                    sunset=datetime.combine(
                        forecast_date,
                        datetime.min.time().replace(
                            hour=int(sunset_hour), minute=int((sunset_hour % 1) * 60)
                        ),
                    ),
                )
            )

        return forecasts

    def get_historical_weather(
        self, location: GeoLocation, start_date: date, end_date: date
    ) -> List[Dict]:
        """Generate simulated historical weather."""
        data = []
        current = start_date

        while current <= end_date:
            month = current.month
            is_monsoon = month in [9, 10, 11, 12, 1, 2]

            base_rainfall = 15 if is_monsoon else 5
            rainfall = max(0, base_rainfall + self.rng.gauss(0, 10))

            data.append(
                {
                    "date": current.isoformat(),
                    "temperature_avg": round(self.base_temp + self.rng.gauss(0, 3), 1),
                    "temperature_min": round(self.base_temp - 4, 1),
                    "temperature_max": round(self.base_temp + 8, 1),
                    "humidity_avg": round(75 + self.rng.gauss(0, 10), 1),
                    "rainfall_mm": round(rainfall, 1),
                    "wind_speed_avg": round(self.rng.uniform(5, 20), 1),
                    "solar_radiation": round(self.rng.uniform(12, 22), 1),
                }
            )
            current += timedelta(days=1)

        return data


# =============================================================================
# WEATHER ALERT ENGINE
# =============================================================================


class WeatherAlertEngine:
    """Generate alerts based on weather thresholds and conditions."""

    def __init__(self, thresholds: type = WeatherThresholds):
        self.thresholds = thresholds
        self.alert_counter = 0

    def check_weather_alerts(
        self,
        current: CurrentWeather,
        hourly: List[HourlyForecast],
        daily: List[DailyForecast],
    ) -> List[WeatherAlert]:
        """Check current and forecasted conditions for alerts."""
        alerts = []

        # Check current conditions
        alerts.extend(self._check_current_conditions(current))

        # Check next 24 hours
        next_24h = hourly[:24]
        alerts.extend(self._check_hourly_forecast(next_24h))

        # Check daily forecast
        alerts.extend(self._check_daily_forecast(daily[:3]))

        return sorted(
            alerts, key=lambda a: (self._severity_order(a.severity), a.timestamp)
        )

    def _severity_order(self, severity: AlertSeverity) -> int:
        """Return sort order for severity (lower = more severe)."""
        order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.DANGER: 1,
            AlertSeverity.WARNING: 2,
            AlertSeverity.INFO: 3,
        }
        return order.get(severity, 99)

    def _check_current_conditions(self, current: CurrentWeather) -> List[WeatherAlert]:
        """Check current weather for alert conditions."""
        alerts = []

        # Temperature alerts
        if current.temperature_c >= self.thresholds.TEMP_HIGH_DANGER:
            alerts.append(
                WeatherAlert(
                    id=f"alert_{self.alert_counter}",
                    timestamp=current.timestamp,
                    severity=AlertSeverity.DANGER,
                    category="temperature",
                    title="Extreme Heat Warning",
                    message=f"Temperature is {current.temperature_c}°C - dangerously high!",
                    recommendation="Suspend all field work. Ensure adequate hydration. Increase irrigation immediately.",
                    source_data={"temperature": current.temperature_c},
                )
            )
        elif current.temperature_c >= self.thresholds.TEMP_HIGH_WARNING:
            alerts.append(
                WeatherAlert(
                    id=f"alert_{self.alert_counter}",
                    timestamp=current.timestamp,
                    severity=AlertSeverity.WARNING,
                    category="temperature",
                    title="Heat Advisory",
                    message=f"Temperature is {current.temperature_c}°C - take precautions.",
                    recommendation="Limit outdoor activities. Apply pesticides early morning or late afternoon.",
                    source_data={"temperature": current.temperature_c},
                )
            )

        # Wind for spraying
        if current.wind_speed_kmh >= self.thresholds.WIND_SPRAY_DANGER:
            alerts.append(
                WeatherAlert(
                    id=f"alert_{self.alert_counter}",
                    timestamp=current.timestamp,
                    severity=AlertSeverity.DANGER,
                    category="spraying",
                    title="Do Not Spray - High Wind",
                    message=f"Wind speed is {current.wind_speed_kmh} km/h - pesticide drift risk.",
                    recommendation="Delay pesticide application until wind speed drops below 15 km/h.",
                    source_data={"wind_speed": current.wind_speed_kmh},
                )
            )
        elif current.wind_speed_kmh >= self.thresholds.WIND_SPRAY_WARNING:
            alerts.append(
                WeatherAlert(
                    id=f"alert_{self.alert_counter}",
                    timestamp=current.timestamp,
                    severity=AlertSeverity.WARNING,
                    category="spraying",
                    title="Caution When Spraying",
                    message=f"Wind speed is {current.wind_speed_kmh} km/h - moderate drift risk.",
                    recommendation="Consider using nozzle shields or waiting for calmer conditions.",
                    source_data={"wind_speed": current.wind_speed_kmh},
                )
            )

        # Rain currently
        if current.rainfall_mm > self.thresholds.RAINFALL_MODERATE:
            alerts.append(
                WeatherAlert(
                    id=f"alert_{self.alert_counter}",
                    timestamp=current.timestamp,
                    severity=AlertSeverity.INFO,
                    category="rain",
                    title="Rainfall Ongoing",
                    message=f"Currently raining at {current.rainfall_mm} mm/hour.",
                    recommendation="Do not apply fertilizers or pesticides. Check drainage systems.",
                    source_data={"rainfall": current.rainfall_mm},
                )
            )

        self.alert_counter += len(alerts)
        return alerts

    def _check_hourly_forecast(
        self, hourly: List[HourlyForecast]
    ) -> List[WeatherAlert]:
        """Check hourly forecast for upcoming conditions."""
        alerts = []
        base_time = datetime.now()

        # Check for upcoming rain during spraying hours
        spraying_hours = range(7, 11)  # 7am - 11am ideal
        rain_during_spray = [
            h
            for h in hourly[:8]
            if h.timestamp.hour in spraying_hours and h.rainfall_probability > 60
        ]

        if rain_during_spray:
            earliest_rain = rain_during_spray[0]
            alerts.append(
                WeatherAlert(
                    id=f"alert_{self.alert_counter}",
                    timestamp=earliest_rain.timestamp,
                    severity=AlertSeverity.WARNING,
                    category="spraying",
                    title="Rain Expected During Spraying Hours",
                    message=f"Rain ({earliest_rain.rainfall_probability}% chance) expected at {earliest_rain.timestamp.strftime('%H:%M')}.",
                    recommendation="Apply pesticides before rain or postpone to tomorrow.",
                    source_data={"timestamp": earliest_rain.timestamp.isoformat()},
                )
            )

        # Check for heavy rain
        heavy_rain_hours = [h for h in hourly if h.rainfall_probability > 80]
        if heavy_rain_hours:
            hr = heavy_rain_hours[0]
            alerts.append(
                WeatherAlert(
                    id=f"alert_{self.alert_counter}",
                    timestamp=hr.timestamp,
                    severity=AlertSeverity.WARNING,
                    category="rain",
                    title="Heavy Rain Forecast",
                    message=f"High chance ({hr.rainfall_probability}%) of heavy rain at {hr.timestamp.strftime('%H:%M')}.",
                    recommendation="Check drainage. Avoid fertilizing. Prepare for flood risk.",
                    source_data={"rainfall_probability": hr.rainfall_probability},
                )
            )

        self.alert_counter += len(alerts)
        return alerts

    def _check_daily_forecast(self, daily: List[DailyForecast]) -> List[WeatherAlert]:
        """Check daily forecast for extended conditions."""
        alerts = []

        for day in daily:
            # Multi-day heavy rain
            if day.rainfall_mm > self.thresholds.RAINFALL_HEAVY:
                alerts.append(
                    WeatherAlert(
                        id=f"alert_{self.alert_counter}",
                        timestamp=datetime.combine(day.date, datetime.min.time()),
                        severity=AlertSeverity.WARNING,
                        category="rain",
                        title="Heavy Rain Warning",
                        message=f"{day.rainfall_mm} mm rainfall expected on {day.date}.",
                        recommendation="Ensure good drainage. Do not apply pesticides or fertilizers.",
                        source_data={
                            "date": day.date.isoformat(),
                            "rainfall_mm": day.rainfall_mm,
                        },
                    )
                )

            # Extended high humidity
            if day.humidity_max_percent > self.thresholds.HUMIDITY_HIGH_DISEASE:
                alerts.append(
                    WeatherAlert(
                        id=f"alert_{self.alert_counter}",
                        timestamp=datetime.combine(day.date, datetime.min.time()),
                        severity=AlertSeverity.WARNING,
                        category="disease",
                        title="High Disease Risk Day",
                        message=f"High humidity ({day.humidity_max_percent}%) expected - disease risk elevated.",
                        recommendation="Monitor for blast and sheath blight. Consider preventive fungicide.",
                        source_data={
                            "date": day.date.isoformat(),
                            "humidity": day.humidity_max_percent,
                        },
                    )
                )

            # Strong wind day
            if day.wind_speed_max_kmh > self.thresholds.WIND_STRONG:
                alerts.append(
                    WeatherAlert(
                        id=f"alert_{self.alert_counter}",
                        timestamp=datetime.combine(day.date, datetime.min.time()),
                        severity=AlertSeverity.INFO,
                        category="spraying",
                        title="Windy Day Expected",
                        message=f"Wind gusts up to {day.wind_speed_max_kmh} km/h expected.",
                        recommendation="Plan spraying for calmer days.",
                        source_data={
                            "date": day.date.isoformat(),
                            "wind": day.wind_speed_max_kmh,
                        },
                    )
                )

        self.alert_counter += len(alerts)
        return alerts


# =============================================================================
# DISEASE RISK CALCULATOR
# =============================================================================


class DiseaseRiskCalculator:
    """Calculate disease risks based on weather conditions."""

    def __init__(self, thresholds: type = WeatherThresholds):
        self.thresholds = thresholds

    def assess_disease_risks(
        self,
        current: CurrentWeather,
        hourly: List[HourlyForecast],
        daily: List[DailyForecast],
    ) -> List[DiseaseRiskAssessment]:
        """Assess disease risks from weather conditions."""
        risks = []

        risks.append(self._assess_blast_risk(current, hourly))
        risks.append(self._assess_sheath_blight_risk(current, hourly))
        risks.append(self._assess_bacterial_blight_risk(current, hourly))
        risks.append(self._assess_brown_spot_risk(current, daily))
        risks.append(self._assess_tungro_vector_risk(hourly))

        return sorted(risks, key=lambda r: r.risk_score, reverse=True)

    def _assess_blast_risk(
        self, current: CurrentWeather, hourly: List[HourlyForecast]
    ) -> DiseaseRiskAssessment:
        """Assess rice blast disease risk."""
        t = self.thresholds
        factors = []
        score = 0.0

        # Current conditions
        temp_ok = t.BLAST_TEMP_MIN <= current.temperature_c <= t.BLAST_TEMP_MAX
        humidity_high = current.humidity_percent >= t.BLAST_HUMIDITY

        if temp_ok:
            score += 0.2
            factors.append(f"Temperature ({current.temperature_c}°C) favorable")
        else:
            factors.append(
                f"Temperature ({current.temperature_c}°C) {'too low' if current.temperature_c < t.BLAST_TEMP_MIN else 'too high'}"
            )

        if humidity_high:
            score += 0.3
            factors.append("High humidity (>85%)")

        # Leaf wetness from rain
        wet_hours = sum(1 for h in hourly[:24] if h.rainfall_mm > 0)
        if wet_hours >= t.BLAST_DURATION_HOURS:
            score += 0.4
            factors.append(f"Extended leaf wetness ({wet_hours} hours)")
        elif wet_hours >= t.BLAST_DURATION_HOURS / 2:
            score += 0.2
            factors.append(f"Moderate leaf wetness ({wet_hours} hours)")

        # Night temperature (critical for neck blast)
        night_hours = [h for h in hourly if 22 <= h.timestamp.hour <= 6]
        if night_hours:
            night_temp_ok = all(
                t.BLAST_NECK_TEMP_MIN <= h.temperature_c <= t.BLAST_NECK_TEMP_MAX
                for h in night_hours
            )
            night_humidity = all(
                h.humidity_percent >= t.BLAST_NECK_HUMIDITY for h in night_hours
            )
            if night_temp_ok and night_humidity:
                score += 0.2
                factors.append("Night conditions favorable for neck blast")

        # Determine risk level
        risk_level = self._score_to_level(score)

        return DiseaseRiskAssessment(
            disease="Rice Blast",
            risk_level=risk_level,
            risk_score=min(score, 1.0),
            contributing_factors=factors,
            recommendation=self._get_blast_recommendation(risk_level),
            preventive_actions=[
                "Apply preventive fungicide if risk is high",
                "Use tricyclazole or hexaconazole",
                "Reduce nitrogen fertilization",
                "Improve field drainage",
            ],
        )

    def _assess_sheath_blight_risk(
        self, current: CurrentWeather, hourly: List[HourlyForecast]
    ) -> DiseaseRiskAssessment:
        """Assess sheath blight disease risk."""
        t = self.thresholds
        factors = []
        score = 0.0

        # Temperature
        if (
            t.SHEATH_BLIGHT_TEMP_MIN
            <= current.temperature_c
            <= t.SHEATH_BLIGHT_TEMP_MAX
        ):
            score += 0.25
            factors.append(f"Temperature ({current.temperature_c}°C) favorable")

        # Humidity
        if current.humidity_percent >= t.SHEATH_BLIGHT_HUMIDITY:
            score += 0.25
            factors.append("High humidity favorable")

        # Continuous rain/overcast
        cloudy_hours = sum(
            1
            for h in hourly[:24]
            if h.rainfall_mm > 0
            or h.condition in [WeatherCondition.CLOUDY, WeatherCondition.RAINY]
        )
        if cloudy_hours >= 12:
            score += 0.3
            factors.append(f"Prolonged cloudy/rainy conditions ({cloudy_hours}h)")
        elif cloudy_hours >= 6:
            score += 0.15

        # Dense canopy factor (would need crop data)
        score += 0.2  # Assume moderate canopy

        risk_level = self._score_to_level(score)

        return DiseaseRiskAssessment(
            disease="Sheath Blight",
            risk_level=risk_level,
            risk_score=min(score, 1.0),
            contributing_factors=factors,
            recommendation=self._get_sheath_blight_recommendation(risk_level),
            preventive_actions=[
                "Apply fungicide (hexaconazole, validamycin)",
                "Reduce plant density",
                "Balance nitrogen application",
                "Drain field periodically",
            ],
        )

    def _assess_bacterial_blight_risk(
        self, current: CurrentWeather, hourly: List[HourlyForecast]
    ) -> DiseaseRiskAssessment:
        """Assess bacterial leaf blight risk."""
        factors = []
        score = 0.0

        # Warm, humid conditions
        if 25 <= current.temperature_c <= 32:
            score += 0.3
            factors.append("Temperature favorable (25-32°C)")

        if current.humidity_percent >= 80:
            score += 0.3
            factors.append("High humidity")

        # Rain with wind (splashes bacteria)
        if current.rainfall_probability > 50 and current.wind_speed_kmh > 10:
            score += 0.3
            factors.append("Rain with wind - bacterial spread likely")

        # Recent storm damage
        if hourly[:6]:
            heavy_rain = any(h.rainfall_mm > 10 for h in hourly[:6])
            if heavy_rain:
                score += 0.1
                factors.append("Recent heavy rain may cause wound infection")

        risk_level = self._score_to_level(score)

        return DiseaseRiskAssessment(
            disease="Bacterial Leaf Blight",
            risk_level=risk_level,
            risk_score=min(score, 1.0),
            contributing_factors=factors,
            recommendation=self._get_blight_recommendation(risk_level),
            preventive_actions=[
                "Use certified clean seed",
                "Avoid wound infection",
                "Control insect vectors",
                "Apply balanced fertilization",
            ],
        )

    def _assess_brown_spot_risk(
        self, current: CurrentWeather, daily: List[DailyForecast]
    ) -> DiseaseRiskAssessment:
        """Assess brown spot risk (often associated with nutrient deficiency + stress)."""
        factors = []
        score = 0.0

        # Drought stress
        recent_rain = sum(d.rainfall_mm for d in daily[:3])
        if recent_rain < 5:
            score += 0.4
            factors.append("Dry conditions - drought stress")

        # High temperature stress
        if daily and daily[0].temperature_max_c > 35:
            score += 0.3
            factors.append("High temperature stress")

        # Low humidity
        if daily and daily[0].humidity_min_percent < 50:
            score += 0.2
            factors.append("Low humidity - dry conditions")

        risk_level = self._score_to_level(score)

        return DiseaseRiskAssessment(
            disease="Brown Spot",
            risk_level=risk_level,
            risk_score=min(score, 1.0),
            contributing_factors=factors,
            recommendation=self._get_brown_spot_recommendation(risk_level),
            preventive_actions=[
                "Ensure adequate irrigation",
                "Apply balanced fertilization",
                "Use silicon nutrition",
                "Address soil nutrient deficiencies",
            ],
        )

    def _assess_tungro_vector_risk(
        self, hourly: List[HourlyForecast]
    ) -> DiseaseRiskAssessment:
        """Assess tungro virus vector (leafhopper) activity risk."""
        factors = []
        score = 0.0

        # Warm conditions favor leafhoppers
        avg_temp = sum(h.temperature_c for h in hourly[:12]) / 12
        if 25 <= avg_temp <= 32:
            score += 0.4
            factors.append("Temperature favorable for leafhopper activity")

        # Dry spell followed by rain can trigger outbreaks
        dry_hours = sum(1 for h in hourly[:24] if h.rainfall_mm < 1)
        if dry_hours > 18:
            score += 0.3
            factors.append("Dry conditions favor leafhopper breeding")

        # Light rain may attract hoppers
        light_rain_hours = sum(1 for h in hourly[:12] if 0 < h.rainfall_mm < 5)
        if 2 <= light_rain_hours <= 6:
            score += 0.2
            factors.append("Light rain may increase leafhopper activity")

        risk_level = self._score_to_level(score)

        return DiseaseRiskAssessment(
            disease="Tungro Virus (Vector Risk)",
            risk_level=risk_level,
            risk_score=min(score, 1.0),
            contributing_factors=factors,
            recommendation=self._get_tungro_recommendation(risk_level),
            preventive_actions=[
                "Monitor for leafhopper populations",
                "Apply insecticide if vector activity high",
                "Use resistant varieties",
                "Remove infected plants",
            ],
        )

    def _score_to_level(self, score: float) -> str:
        """Convert score to risk level string."""
        if score >= 0.7:
            return "very_high"
        elif score >= 0.5:
            return "high"
        elif score >= 0.3:
            return "moderate"
        else:
            return "low"

    def _get_blast_recommendation(self, risk_level: str) -> str:
        recommendations = {
            "very_high": "URGENT: Apply preventive fungicide immediately. Consider hexaconazole or tricyclazole.",
            "high": "Apply preventive fungicide within 48 hours. Reduce nitrogen if possible.",
            "moderate": "Monitor closely. Prepare fungicide for application if conditions persist.",
            "low": "Low risk. Continue regular monitoring.",
        }
        return recommendations.get(risk_level, "")

    def _get_sheath_blight_recommendation(self, risk_level: str) -> str:
        recommendations = {
            "very_high": "Apply fungicide (hexaconazole or validamycin) immediately. Improve air circulation.",
            "high": "Apply fungicide within 2-3 days. Reduce canopy density if possible.",
            "moderate": "Monitor for lesions. Consider preventive application.",
            "low": "Low risk. Continue regular scouting.",
        }
        return recommendations.get(risk_level, "")

    def _get_blight_recommendation(self, risk_level: str) -> str:
        recommendations = {
            "very_high": "No effective cure. Focus on prevention: remove infected material, avoid spreading.",
            "high": "Apply copper-based bactericide. Control vectors. Improve drainage.",
            "moderate": "Monitor for symptoms. Prepare for intervention if spread occurs.",
            "low": "Low risk. Maintain good field sanitation.",
        }
        return recommendations.get(risk_level, "")

    def _get_brown_spot_recommendation(self, risk_level: str) -> str:
        recommendations = {
            "very_high": "Address water stress immediately. Apply foliar fertilizer with micronutrients.",
            "high": "Increase irrigation frequency. Apply balanced fertilizer with potassium.",
            "moderate": "Monitor soil moisture. Plan for supplemental irrigation.",
            "low": "Conditions favorable. Maintain current management.",
        }
        return recommendations.get(risk_level, "")

    def _get_tungro_recommendation(self, risk_level: str) -> str:
        recommendations = {
            "very_high": "Apply insecticide to control leafhopper vectors. Remove infected plants.",
            "high": "Monitor leafhopper populations. Consider preventive insecticide.",
            "moderate": "Scout for leafhoppers. Prepare for intervention if detected.",
            "low": "Low vector activity. Continue monitoring.",
        }
        return recommendations.get(risk_level, "")


# =============================================================================
# IRRIGATION RECOMMENDATION ENGINE
# =============================================================================


class IrrigationRecommendationEngine:
    """Generate irrigation recommendations based on weather and crop needs."""

    def __init__(self):
        # Daily water requirement for rice (mm)
        self.daily_requirement_mm = 5  # Average for tropical rice

        # Soil water holding capacity (mm per cm depth)
        self.soil_whc_mm_per_cm = 2.0

        # Effective root zone depth (cm)
        self.root_zone_depth_cm = 20

    def get_recommendation(
        self,
        current: CurrentWeather,
        hourly: List[HourlyForecast],
        daily: List[DailyForecast],
        current_soil_moisture: float = 100,  # % saturation
        growth_stage: str = "tillering",
    ) -> IrrigationRecommendation:
        """
        Calculate irrigation recommendation.

        Args:
            current: Current weather conditions
            hourly: Hourly forecast
            daily: Daily forecast
            current_soil_moisture: Soil moisture as percentage (0-100)
            growth_stage: Current growth stage of rice
        """
        factors = []
        water_balance = 0.0

        # Calculate water requirement based on growth stage
        stage_requirement = self._get_stage_requirement(growth_stage)

        # Today's water balance
        today = daily[0] if daily else None

        # Expected rainfall
        expected_rainfall = today.rainfall_mm if today else 0
        if expected_rainfall > 0:
            factors.append(f"Expected rainfall: {expected_rainfall:.1f} mm")

        # Actual evaporation (if ET data available)
        if today and today.evapotranspiration_mm:
            et_loss = today.evapotranspiration_mm
            water_balance += expected_rainfall - et_loss
            factors.append(f"ET loss: {et_loss:.1f} mm")
        else:
            # Simplified calculation
            et_loss = 4 if current.temperature_c > 30 else 3
            water_balance += expected_rainfall - et_loss
            factors.append(f"Estimated ET: ~{et_loss} mm")

        # Soil moisture contribution
        available_water = (
            (current_soil_moisture / 100)
            * self.root_zone_depth_cm
            * self.soil_whc_mm_per_cm
        )
        factors.append(f"Soil moisture: {available_water:.1f} mm available")

        # Future rainfall prediction
        future_rain_3d = sum(d.rainfall_mm for d in daily[1:4]) if len(daily) > 1 else 0
        if future_rain_3d > 10:
            factors.append(f"3-day forecast rain: {future_rain_3d:.1f} mm")

        # Calculate net water deficit/surplus
        net_balance = water_balance + available_water - stage_requirement

        # Determine action
        if net_balance < -10:
            action = "irrigate"
            recommended_amount = (
                abs(net_balance) + 10
            )  # Fill to field capacity + buffer
            confidence = 0.85
        elif net_balance < 0:
            action = "irrigate"
            recommended_amount = abs(net_balance)
            confidence = 0.75
        elif net_balance > 30:
            action = "drain"
            recommended_amount = 0
            confidence = 0.8
            factors.append("Water surplus - consider drainage")
        elif future_rain_3d > 40:
            action = "maintain"
            recommended_amount = 0
            confidence = 0.7
            factors.append("Heavy rain expected - hold off irrigation")
        else:
            action = "no_action"
            recommended_amount = 0
            confidence = 0.9

        # Estimate next irrigation
        if action == "no_action" and future_rain_3d < 20:
            days_until_irrigation = (
                int(available_water / stage_requirement) if stage_requirement > 0 else 3
            )
            next_irrigation = datetime.now() + timedelta(
                days=min(days_until_irrigation, 5)
            )
        else:
            next_irrigation = None

        return IrrigationRecommendation(
            timestamp=datetime.now(),
            water_deficit_mm=max(0, -net_balance),
            water_surplus_mm=max(0, net_balance - 30),
            recommended_action=action,
            recommended_amount_mm=round(recommended_amount, 1),
            next_irrigation_estimate=next_irrigation,
            confidence=confidence,
            factors=factors,
        )

    def _get_stage_requirement(self, growth_stage: str) -> float:
        """Get daily water requirement by growth stage (mm)."""
        requirements = {
            "germination": 2,
            "seedling": 3,
            "tillering": 5,
            "panicle_initiation": 6,
            "booting": 7,
            "flowering": 8,
            "grain_filling": 6,
            "maturity": 3,
        }
        return requirements.get(growth_stage, 5)


# =============================================================================
# FARMING ACTIVITY RECOMMENDATIONS
# =============================================================================


class ActivityRecommendationEngine:
    """Recommend farming activities based on weather."""

    def __init__(self):
        self.thresholds = WeatherThresholds()

    def get_recommendations(
        self,
        current: CurrentWeather,
        hourly: List[HourlyForecast],
        daily: List[DailyForecast],
    ) -> List[FarmingActivityRecommendation]:
        """Get activity recommendations for the day."""
        recommendations = []

        recommendations.append(self._check_spraying(current, hourly))
        recommendations.append(self._check_fertilizing(current, daily))
        recommendations.append(self._check_harvesting(current, daily))
        recommendations.append(self._check_transplanting(current, daily))
        recommendations.append(self._check_land_preparation(current))

        return [r for r in recommendations if r is not None]

    def _check_spraying(
        self, current: CurrentWeather, hourly: List[HourlyForecast]
    ) -> FarmingActivityRecommendation:
        """Check spraying suitability."""

        # Ideal conditions: calm wind, no rain, moderate temp
        wind_ok = current.wind_speed_kmh < self.thresholds.WIND_SPRAY_DANGER
        no_rain_current = current.rainfall_mm < 1
        temp_ok = 20 <= current.temperature_c <= 32

        # Check next 6 hours
        next_6h = hourly[:6]
        rain_soon = any(h.rainfall_probability > 50 for h in next_6h)
        wind_ok_6h = all(
            h.wind_speed_kmh < self.thresholds.WIND_SPRAY_DANGER for h in next_6h
        )

        # Find best window today
        best_window = None
        for h in next_6h:
            if (
                h.wind_speed_kmh < self.thresholds.WIND_SPRAY_WARNING
                and h.rainfall_probability < 40
                and 7 <= h.timestamp.hour <= 17
            ):
                best_window = (h.timestamp.hour, h.timestamp.hour + 1)
                break

        if wind_ok and no_rain_current and temp_ok and not rain_soon and wind_ok_6h:
            return FarmingActivityRecommendation(
                activity="Pesticide/Fungicide Application",
                suitability="ideal" if best_window else "suitable",
                timing="now" if best_window else "later_today",
                hours_window=best_window,
                confidence=0.85 if best_window else 0.7,
                reason="Conditions favorable for spraying"
                + (
                    f". Best time: {best_window[0]}:00-{best_window[1]}:00"
                    if best_window
                    else ""
                ),
                alternative_timing="tomorrow early morning"
                if not best_window
                else None,
            )
        elif current.wind_speed_kmh >= self.thresholds.WIND_SPRAY_DANGER:
            return FarmingActivityRecommendation(
                activity="Pesticide/Fungicide Application",
                suitability="not_recommended",
                timing="this_week",
                confidence=0.9,
                reason=f"Wind too strong ({current.wind_speed_kmh} km/h) - high drift risk",
                alternative_timing="tomorrow"
                if hourly[24].wind_speed_kmh < 15
                else "next favorable day",
            )
        elif rain_soon:
            return FarmingActivityRecommendation(
                activity="Pesticide/Fungicide Application",
                suitability="not_recommended",
                timing="tomorrow",
                confidence=0.85,
                reason="Rain expected within 6 hours",
                alternative_timing="after rain clears",
            )
        elif current.temperature_c > 35:
            return FarmingActivityRecommendation(
                activity="Pesticide/Fungicide Application",
                suitability="not_recommended",
                timing="early_morning" if current.temperature_c < 38 else "tomorrow",
                confidence=0.8,
                reason="Temperature too high - risk of crop burn",
                alternative_timing="early morning (6-8 AM)",
            )
        else:
            return FarmingActivityRecommendation(
                activity="Pesticide/Fungicide Application",
                suitability="marginal",
                timing="later_today",
                hours_window=best_window,
                confidence=0.6,
                reason="Conditions borderline - consider waiting",
                alternative_timing="tomorrow",
            )

    def _check_fertilizing(
        self, current: CurrentWeather, daily: List[DailyForecast]
    ) -> FarmingActivityRecommendation:
        """Check fertilizing suitability."""

        # Heavy rain not expected today
        heavy_rain_today = daily[0].rainfall_mm > 15 if daily else False

        # No heavy rain in next 24h
        rain_next_24h = sum(h.rainfall_mm for h in daily[:1]) if daily else 0

        if not heavy_rain_today and rain_next_24h < 20:
            return FarmingActivityRecommendation(
                activity="Fertilizer Application",
                suitability="suitable",
                timing="now",
                confidence=0.8,
                reason="Good conditions for fertilizer application",
            )
        elif heavy_rain_today:
            return FarmingActivityRecommendation(
                activity="Fertilizer Application",
                suitability="not_recommended",
                timing="after_rain",
                confidence=0.85,
                reason=f"Heavy rain expected ({daily[0].rainfall_mm:.0f}mm) - fertilizer will be washed away",
                alternative_timing="after 1-2 dry days",
            )
        else:
            return FarmingActivityRecommendation(
                activity="Fertilizer Application",
                suitability="marginal",
                timing="later_today",
                confidence=0.65,
                reason="Rain possible - may affect absorption",
                alternative_timing="tomorrow if dry",
            )

    def _check_harvesting(
        self, current: CurrentWeather, daily: List[DailyForecast]
    ) -> FarmingActivityRecommendation:
        """Check harvesting suitability."""

        # Need dry conditions for harvesting
        rain_today = daily[0].rainfall_mm if daily else 0
        rain_tomorrow = daily[1].rainfall_mm if len(daily) > 1 else 0

        if rain_today < 5 and rain_tomorrow < 10:
            return FarmingActivityRecommendation(
                activity="Harvesting",
                suitability="ideal",
                timing="now" if current.rainfall_mm < 1 else "later_today",
                confidence=0.9,
                reason="Dry conditions - good for harvesting and drying",
            )
        elif rain_today > 20:
            return FarmingActivityRecommendation(
                activity="Harvesting",
                suitability="not_recommended",
                timing="this_week",
                confidence=0.85,
                reason=f"Heavy rain today - field too wet",
                alternative_timing="after field dries",
            )
        else:
            return FarmingActivityRecommendation(
                activity="Harvesting",
                suitability="suitable" if current.rainfall_mm < 1 else "marginal",
                timing="later_today",
                confidence=0.7,
                reason="Check field conditions before harvesting",
                alternative_timing="tomorrow if rain continues",
            )

    def _check_transplanting(
        self, current: CurrentWeather, daily: List[DailyForecast]
    ) -> FarmingActivityRecommendation:
        """Check transplanting suitability."""

        # Need cloudy or mild conditions, no heavy rain
        rain_today = daily[0].rainfall_mm if daily else 0
        temp_ok = 22 <= current.temperature_c <= 32

        if rain_today < 10 and temp_ok:
            return FarmingActivityRecommendation(
                activity="Transplanting",
                suitability="suitable",
                timing="now",
                confidence=0.75,
                reason="Good conditions for transplanting",
            )
        elif rain_today > 30:
            return FarmingActivityRecommendation(
                activity="Transplanting",
                suitability="not_recommended",
                timing="tomorrow",
                confidence=0.8,
                reason="Heavy rain will damage seedlings",
                alternative_timing="after rain",
            )
        else:
            return FarmingActivityRecommendation(
                activity="Transplanting",
                suitability="marginal",
                timing="early_morning",
                confidence=0.6,
                reason="Cloudy day okay but monitor seedlings",
                alternative_timing="overcast day preferred",
            )

    def _check_land_preparation(
        self, current: CurrentWeather
    ) -> FarmingActivityRecommendation:
        """Check land preparation suitability."""

        # Land prep can handle some rain but not extreme
        if current.rainfall_mm < 20:
            return FarmingActivityRecommendation(
                activity="Land Preparation",
                suitability="suitable",
                timing="now",
                confidence=0.8,
                reason="Good conditions for land preparation",
            )
        else:
            return FarmingActivityRecommendation(
                activity="Land Preparation",
                suitability="marginal",
                timing="later" if current.rainfall_mm < 40 else "tomorrow",
                confidence=0.6,
                reason="Heavy rain may make field too wet for machinery",
                alternative_timing="after rain",
            )


# =============================================================================
# WEATHER MONITORING ENGINE
# =============================================================================


class WeatherMonitoringEngine:
    """
    Main engine coordinating weather data, alerts, and recommendations.
    """

    def __init__(
        self,
        weather_provider: Optional[WeatherDataProvider] = None,
        alert_engine: Optional[WeatherAlertEngine] = None,
        disease_calculator: Optional[DiseaseRiskCalculator] = None,
        irrigation_engine: Optional[IrrigationRecommendationEngine] = None,
        activity_engine: Optional[ActivityRecommendationEngine] = None,
    ):
        self.provider = weather_provider or SimulatedWeatherProvider()
        self.alert_engine = alert_engine or WeatherAlertEngine()
        self.disease_calculator = disease_calculator or DiseaseRiskCalculator()
        self.irrigation_engine = irrigation_engine or IrrigationRecommendationEngine()
        self.activity_engine = activity_engine or ActivityRecommendationEngine()

        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.cache_ttl_seconds = 900  # 15 minutes

    def get_weather_summary(
        self, location: GeoLocation, use_cache: bool = True
    ) -> WeatherSummary:
        """Get comprehensive weather summary for a location."""

        cache_key = f"summary_{location.latitude}_{location.longitude}"

        # Check cache
        if use_cache and cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.cache_ttl_seconds:
                return cached_data

        # Fetch fresh data
        current = self.provider.get_current_weather(location)
        hourly = self.provider.get_hourly_forecast(location, hours=48)
        daily = self.provider.get_daily_forecast(location, days=7)

        # Generate alerts
        alerts = self.alert_engine.check_weather_alerts(current, hourly, daily)

        # Calculate disease risks
        disease_risks = self.disease_calculator.assess_disease_risks(
            current, hourly, daily
        )

        # Irrigation recommendation
        irrigation = self.irrigation_engine.get_recommendation(current, hourly, daily)

        # Activity recommendations
        activities = self.activity_engine.get_recommendations(current, hourly, daily)

        # Compile summary
        summary = WeatherSummary(
            location=location,
            period_start=datetime.now(),
            period_end=datetime.now() + timedelta(days=7),
            current=current,
            hourly_forecast=hourly,
            daily_forecast=daily,
            alerts=alerts,
            disease_risks=disease_risks,
            irrigation_recommendation=irrigation,
            activity_recommendations=activities,
        )

        # Cache result
        self.cache[cache_key] = (summary, datetime.now())

        return summary

    def get_disease_alerts_only(self, location: GeoLocation) -> List[WeatherAlert]:
        """Get only disease-related alerts."""
        summary = self.get_weather_summary(location)
        return [a for a in summary.alerts if a.category == "disease"]

    def get_irrigation_only(
        self, location: GeoLocation, growth_stage: str = "tillering"
    ) -> IrrigationRecommendation:
        """Get irrigation recommendation only."""
        current = self.provider.get_current_weather(location)
        hourly = self.provider.get_hourly_forecast(location, hours=48)
        daily = self.provider.get_daily_forecast(location, days=7)

        return self.irrigation_engine.get_recommendation(
            current, hourly, daily, growth_stage=growth_stage
        )


# =============================================================================
# API INTERFACE
# =============================================================================


class WeatherMonitoringAPI:
    """REST API interface for weather monitoring."""

    def __init__(self):
        self.engine = WeatherMonitoringEngine()

    def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get complete weather summary."""
        location = GeoLocation(latitude=latitude, longitude=longitude)
        summary = self.engine.get_weather_summary(location)

        return {
            "current": summary.current.to_dict() if summary.current else None,
            "daily_forecast": [d.to_dict() for d in summary.daily_forecast],
            "alerts": [a.to_dict() for a in summary.alerts],
            "disease_risks": [
                {
                    "disease": r.disease,
                    "risk_level": r.risk_level,
                    "risk_score": r.risk_score,
                    "factors": r.contributing_factors,
                    "recommendation": r.recommendation,
                }
                for r in summary.disease_risks
            ],
            "irrigation": {
                "action": summary.irrigation_recommendation.recommended_action,
                "amount_mm": summary.irrigation_recommendation.recommended_amount_mm,
                "confidence": summary.irrigation_recommendation.confidence,
                "factors": summary.irrigation_recommendation.factors,
            }
            if summary.irrigation_recommendation
            else None,
            "activities": [
                {
                    "activity": a.activity,
                    "suitability": a.suitability,
                    "timing": a.timing,
                    "reason": a.reason,
                }
                for a in summary.activity_recommendations
            ],
        }

    def get_alerts(self, latitude: float, longitude: float) -> List[Dict]:
        """Get weather alerts only."""
        location = GeoLocation(latitude=latitude, longitude=longitude)
        summary = self.engine.get_weather_summary(location)
        return [a.to_dict() for a in summary.alerts]

    def get_irrigation(
        self, latitude: float, longitude: float, growth_stage: str = "tillering"
    ) -> Dict:
        """Get irrigation recommendation."""
        location = GeoLocation(latitude=latitude, longitude=longitude)
        current = self.engine.provider.get_current_weather(location)
        hourly = self.engine.provider.get_hourly_forecast(location)
        daily = self.engine.provider.get_daily_forecast(location)

        rec = self.engine.irrigation_engine.get_recommendation(
            current, hourly, daily, growth_stage=growth_stage
        )

        return {
            "action": rec.recommended_action,
            "amount_mm": rec.recommended_amount_mm,
            "deficit_mm": rec.water_deficit_mm,
            "surplus_mm": rec.water_surplus_mm,
            "next_irrigation": rec.next_irrigation_estimate.isoformat()
            if rec.next_irrigation_estimate
            else None,
            "confidence": rec.confidence,
            "factors": rec.factors,
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================


def main():
    """Command-line interface for testing."""
    api = WeatherMonitoringAPI()

    print("=" * 70)
    print("WEATHER MONITORING SYSTEM - CLI")
    print("=" * 70)

    # Test location: Kedah, Malaysia
    lat, lon = 6.0, 100.4

    print(f"\nLocation: Kedah, Malaysia ({lat}, {lon})")
    print("-" * 70)

    # Get complete weather
    weather = api.get_weather(lat, lon)

    # Current conditions
    if weather["current"]:
        c = weather["current"]
        print(f"\n📍 CURRENT CONDITIONS ({c['timestamp']})")
        print(
            f"   Temperature: {c['temperature_c']}°C (min: {c['temperature_min_c']}, max: {c['temperature_max_c']})"
        )
        print(f"   Humidity: {c['humidity_percent']}%")
        print(f"   Rainfall: {c['rainfall_mm']} mm")
        print(f"   Wind: {c['wind_speed_kmh']} km/h {c['wind_direction_cardinal']}")
        print(f"   Condition: {c['condition']}")

    # 7-day forecast
    print(f"\n📅 7-DAY FORECAST")
    print(f"   {'Date':<12} {'Temp':<10} {'Rain':<10} {'Humidity':<10} {'Condition'}")
    print(f"   {'-' * 60}")
    for day in weather["daily_forecast"]:
        print(
            f"   {day['date']:<12} "
            f"{day['temperature_min_c']}-{day['temperature_max_c']}°C  "
            f"{day['rainfall_mm']:.0f}mm({day['rainfall_probability']:.0f}%)  "
            f"{day['humidity_avg_percent']:.0f}%  "
            f"{day['condition']}"
        )

    # Disease risks
    print(f"\n🦠 DISEASE RISK ASSESSMENT")
    for risk in weather["disease_risks"]:
        emoji = {"very_high": "🔴", "high": "🟠", "moderate": "🟡", "low": "🟢"}.get(
            risk["risk_level"], "⚪"
        )
        print(
            f"   {emoji} {risk['disease']}: {risk['risk_level'].upper()} ({risk['risk_score']:.0%})"
        )
        if risk["recommendation"]:
            print(f"      → {risk['recommendation']}")

    # Irrigation
    if weather["irrigation"]:
        irr = weather["irrigation"]
        action_icon = {
            "irrigate": "💧",
            "drain": "🚿",
            "maintain": "➡️",
            "no_action": "✅",
        }.get(irr["action"], "❓")
        print(f"\n{action_icon} IRRIGATION RECOMMENDATION")
        print(f"   Action: {irr['action'].upper()}")
        print(f"   Amount: {irr['amount_mm']} mm")
        print(f"   Confidence: {irr['confidence']:.0%}")

    # Activity recommendations
    print(f"\n🌾 FARMING ACTIVITIES")
    for act in weather["activities"]:
        suit_icon = {
            "ideal": "✅",
            "suitable": "👍",
            "marginal": "⚠️",
            "not_recommended": "❌",
        }.get(act["suitability"], "❓")
        print(f"   {suit_icon} {act['activity']}: {act['suitability'].upper()}")
        print(f"      {act['reason']}")

    # Alerts
    if weather["alerts"]:
        print(f"\n⚠️ WEATHER ALERTS")
        for alert in weather["alerts"]:
            sev_icon = {
                "critical": "🚨",
                "danger": "⚠️",
                "warning": "📢",
                "info": "ℹ️",
            }.get(alert["severity"], "•")
            print(f"   {sev_icon} [{alert['severity'].upper()}] {alert['title']}")
            print(f"      {alert['message']}")

    print("\n" + "=" * 70)
    print("Demo complete!")


if __name__ == "__main__":
    main()
