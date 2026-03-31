# Padi AI System - Smart Farming Assistant

**100% Real Data** - No simulation, no hardcoding. All recommendations based on live APIs.

## Data Sources

| Data | Source | Type |
|------|--------|------|
| Weather | **Open-Meteo API** | REAL |
| Soil Properties | **SoilGrids ISRIC** | REAL |
| Disease Risks | **Calculated from real weather** | DYNAMIC |
| Fertilizer | **Calculated from real soil** | DYNAMIC |

## How to Run

```bash
cd "/mnt/c/Users/USER-PC/Downloads/test/created_lib/test/hi/Padi-AI-System"
python main.py
```

Then open: **http://localhost:5000**

## What's Dynamic?

### Weather (Open-Meteo - FREE, No API Key)
- ✅ Current temperature (real)
- ✅ Current humidity (real)
- ✅ Wind speed & direction (real)
- ✅ Rainfall (real)
- ✅ 7-day forecast (real)
- ✅ Humidity forecast (real)

### Soil (SoilGrids - FREE, No API Key)
- ✅ pH level (real predicted value)
- ✅ Clay percentage (real)
- ✅ Sand percentage (real)
- ✅ Organic carbon (real)
- ✅ CEC (real)
- ✅ Bulk density (real)

### Fertilizer Recommendations (Fully Dynamic)
Based on **your actual soil data**:
- Lime rate calculated from **actual pH**
- N rate calculated from **actual organic carbon**
- P rate calculated from **actual clay content**
- K rate calculated from **actual CEC**
- Zinc recommendation based on **actual pH + clay**

### Disease Risks (Fully Dynamic)
Calculated from **your actual weather**:
- Rice Blast risk from real temperature + humidity
- Sheath Blight risk from real conditions
- Bacterial Blight risk from real wind + rain

## No API Keys Needed

Everything works with **FREE APIs**:
- Open-Meteo: api.open-meteo.com
- SoilGrids: rest.isric.org/soilgrids

## Files

```
Padi-AI-System/
├── main.py              # Flask web app
├── templates/index.html # Web UI
├── requirements.txt    # Dependencies
└── README.md
```

## API Endpoints

```bash
# Get full analysis
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"latitude": 6.0, "longitude": 100.4}'
```
