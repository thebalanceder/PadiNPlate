# 🌾 Padi AI Pro - Smart Farming System

**AI-powered farming assistant with ranked solutions and real purchase links.**

## Features

### 🏆 Ranked Solutions (S/A/B/C Ratings)
- **S Rank**: Best overall solution based on your priorities
- **A Rank**: Excellent alternative
- **B Rank**: Good value option
- **C Rank**: Budget option

### 💰 Cost Analysis
- Money perspective (total cost, cost per hectare)
- Quality perspective (effectiveness %)
- Time perspective (speed, payback period)
- ROI calculation

### 🛒 Real Purchase Links
- Specific products from Malaysian suppliers
- Price comparison
- Delivery information
- Multiple source options

### 🔬 AI-Powered Diagnosis
- Symptom-based disease identification
- Confidence scoring
- Severity assessment

## Quick Start

```bash
cd Padi-AI-System

# Run Basic System (Weather + Soil)
python main.py
# Open: http://localhost:5000

# Run Enhanced System (Disease + Solutions + Purchase Links)
python padi_pro_web.py
# Open: http://localhost:5001
```

## Two Systems

### 1. Basic System (port 5000)
- Real weather from Open-Meteo API
- Real soil data from SoilGrids
- Fertilizer recommendations
- Disease risk assessment

### 2. Pro System (port 5001)
- Symptom-based disease diagnosis
- Ranked solutions (S/A/B/C)
- Product purchase links
- Cost-benefit analysis
- Action plans

## Example Usage

### Pro System - Disease Diagnosis

```
1. User selects symptoms: "diamond-shaped lesions", "gray center"
2. AI diagnoses: Rice Blast (92% confidence)
3. System shows ranked solutions:
   
   [S] Chemical Treatment (Premium)
       Effectiveness: 95% | Speed: 90% | Cost: RM 108
       Products:
         - Isoprothiolane 40EC (RM 58) from Kedah Agro
           🔗 https://www.kedahagro.com
       
   [A] Integrated Pest Management
       Effectiveness: 82% | Speed: 70% | Cost: RM 88
       ...
   
   [B] Organic/Biological Treatment
       Effectiveness: 65% | Speed: 35% | Cost: RM 90
       ...
   
   [C] Cultural Practices Only
       Effectiveness: 45% | Speed: 30% | Cost: RM 0
       ...
```

## API Endpoints

```bash
# Pro System - Full Diagnosis
curl -X POST http://localhost:5001/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["diamond-shaped lesions"], "budget": "medium"}'

# Pro System - Rank Solutions
curl -X POST http://localhost:5001/api/rank-solutions \
  -H "Content-Type: application/json" \
  -d '{"disease": "rice_blast", "budget": "medium"}'
```

## File Structure

```
Padi-AI-System/
├── main.py                    # Basic system (weather + soil)
├── padi_ai_pro.py            # Pro engine (ranked solutions)
├── padi_pro_web.py            # Pro web interface
├── templates/
│   ├── index.html            # Basic UI
│   └── pro.html              # Pro UI
├── requirements.txt
└── README.md
```

## Real Data Sources

| Component | Source | URL |
|-----------|--------|-----|
| Weather | Open-Meteo | api.open-meteo.com |
| Soil | SoilGrids | rest.isric.org |
| Products | Malaysian Suppliers | Various |

## Disease Database

| Disease | Symptoms | Products |
|---------|----------|----------|
| Rice Blast | Diamond lesions, gray center | Tricyclazole, Hexaconazole |
| Sheath Blight | Oval lesions, sheath rot | Validamycin, Carbendazim |
| Bacterial Blight | Yellow tip, ooze | Copper-based |
| Tungro Virus | Yellow-orange, stunting | Imidacloprid |
| Brown Spot | Brown elliptical spots | Mancozeb |

## Cost Tiers

| Tier | Cost/ha | Options |
|------|---------|----------|
| Budget | < RM 150 | Cultural + Organic |
| Standard | RM 150-300 | IPM approach |
| Premium | > RM 300 | Chemical + Equipment |

## Development

```bash
# Install dependencies
pip install flask requests python-dotenv

# Run tests
python padi_ai_pro.py

# Run web
python padi_pro_web.py
```

## License

MIT - Free for agricultural use
