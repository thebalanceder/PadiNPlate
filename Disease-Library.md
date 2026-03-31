# Padi Disease Library

Comprehensive database of common padi diseases.

## Disease Structure

```yaml
disease:
  name: "Disease Name"
  local_name: "Common Local Name"
  
  pathogen:
    type: "Fungus/Bacteria/Virus"
    scientific_name: "Scientific Name"
    transmission: "How it spreads"
    
  symptoms:
    early: "Early symptoms description"
    severe: "Severe symptoms description"
    images: ["image_references"]
    
  conditions:
    temperature: "Temperature range"
    humidity: "Humidity conditions"
    spread_factors: ["Factor 1", "Factor 2"]
    
  management:
    cultural:
      - "Practice 1"
      - "Practice 2"
    biological:
      - "Biocontrol agent"
    chemical:
      - product: "Product Name"
        active_ingredient: "AI"
        rate: "Application rate"
        phi: "Pre-harvest interval"
        
  susceptibility_by_variety:
    susceptible: ["Variety A"]
    resistant: ["Variety B"]
```

## 1. Rice Blast (Beras)

| Field | Value |
|-------|-------|
| Scientific Name | Magnaporthe oryzae |
| Type | Fungus |
| Affected Parts | Leaves, stems, panicles |

### Symptoms
- Diamond-shaped lesions with gray centers
- Lesions on leaf sheath
- Neck rot (panicle blast) - most damaging
- Node blast on stems

### Conditions Favoring Disease
- Temperature: 25-28°C
- Humidity: >90% (continuous leaf wetness)
- Prolonged dew
- Excessive nitrogen fertilization
- Water stress followed by humidity

### Management
**Cultural:**
- Use resistant varieties (MR269, MR297)
- Balanced fertilization
- Avoid water stress
- Proper plant spacing

**Chemical:**
| Product | Active Ingredient | Rate | PHI |
|---------|------------------|------|-----|
| Triazole 250EC | Tricyclazole | 250ml/ha | 30 days |
| Amister | Hexaconazole | 500ml/ha | 21 days |

---

## 2. Bacterial Leaf Blight (Haunting)

| Field | Value |
|-------|-------|
| Scientific Name | Xanthomonas oryzae pv. oryzae |
| Type | Bacteria |
| Affected Parts | Leaves |

### Symptoms
- Water-soaked lesions starting from leaf tip
- Lesions turn yellow, then white
- Characteristic "Kresek" symptom (seedling wilt)
- Yellow bacterial ooze on lesions

### Conditions Favoring Disease
- Temperature: 25-30°C
- High humidity with rain
- Flooding
- Wound infection (from insects, wind)
- Excessive nitrogen

### Management
**Cultural:**
- Use certified clean seed
- Plant resistant varieties
- Avoid wound infection
- Proper drainage

**Chemical:**
- No effective chemical control
- Antibiotics (streptomycin) sometimes used
- Focus on prevention

---

## 3. Sheath Blight

| Field | Value |
|-------|-------|
| Scientific Name | Rhizoctonia solani |
| Type | Fungus |
| Affected Parts | Leaf sheath, stems |

### Symptoms
- Oval or irregular lesions on sheath
- Lesions have gray center with brown border
- Lesions can spread to leaves
- "Sheath rotting" at base
- Lodging in severe cases

### Conditions Favoring Disease
- Temperature: 28-32°C
- High humidity
- Dense plant canopy
- Excessive nitrogen
- Close spacing

### Management
**Cultural:**
- Wide plant spacing
- Balanced N fertilization
- Remove infected debris
- Avoid excessive vegetative growth

**Chemical:**
| Product | Active Ingredient | Rate | PHI |
|---------|------------------|------|-----|
| Unix 75WDG | Hexaconazole | 200g/ha | 30 days |
| Companion | Carbendazim | 500ml/ha | 30 days |

---

## 4. Brown Spot

| Field | Value |
|-------|-------|
| Scientific Name | Bipolaris oryzae |
| Type | Fungus |
| Affected Parts | Leaves, lemma/palea |

### Symptoms
- Small brown elliptical spots
- Spots have yellow halo
- Severe infection causes leaf death
- Also affects grains (dirty panicle)

### Conditions Favoring Disease
- Nutrient deficiency (especially potassium)
- Drought stress
- High temperature
- Poor soil conditions

### Management
**Cultural:**
- Use balanced fertilization
- Ensure adequate irrigation
- Use certified seed

**Chemical:**
| Product | Active Ingredient | Rate | PHI |
|---------|------------------|------|-----|
| Daconil | Chlorothalonil | 1-1.5L/ha | 14 days |

---

## 5. Tungro Virus

| Field | Value |
|-------|-------|
| Type | Virus |
| Vector | Green leafhoppers (Nephotettix spp.) |
| Affected Parts | Entire plant |

### Symptoms
- Yellow-orange discoloration
- Stunted growth
- Reduced tillering
- Delayed heading
- Some leaves show mottling

### Conditions Favoring Disease
- High vector population
- Presence of infected plants
- Continuous rice cultivation
- Early planting when vectors abundant

### Management
**Cultural:**
- Plant early (avoid peak vector period)
- Remove infected plants
- Use virus-free seed
- Synchronized planting in area

**Chemical:**
- Vector control with insecticides
- Imidacloprid, thiamethoxam

---

## 6. Bacterial Leaf Streak

| Field | Value |
|-------|-------|
| Scientific Name | Xanthomonas oryzae pv. oryzicola |
| Type | Bacteria |
| Affected Parts | Leaves |

### Symptoms
- Brown streaks between leaf veins
- Streaks become water-soaked
- Yellow bacterial ooze
- Later: streaks dry and turn grayish

### Conditions Favoring Disease
- Heavy rain
- Strong winds
- High humidity
- Young leaves more susceptible

### Management
**Cultural:**
- Use resistant varieties
- Avoid planting during high-risk periods
- Remove crop residues

**Chemical:**
- Similar to bacterial leaf blight
- Focus on vector management

---

## General Disease Prevention

### IPM Principles
1. **Prevention** - Use clean seed, resistant varieties
2. **Monitoring** - Regular field scouting
3. **Threshold-based action** - Don't spray unnecessarily
4. **Integrated approach** - Combine methods
5. **Documentation** - Record disease incidence

### Early Warning System
```python
IF temperature BETWEEN 25-30 AND humidity > 85%:
  SEND alert "Blast risk HIGH"
  
IF nitrogen_applied > recommended AND recent_rain:
  SEND alert "Sheath blight risk elevated"
```

## Related Categories

- [[Disease-Management]] - Management recommendations
- [[Weather-Monitoring]] - Weather-based alerts
- [[Fertilizer-Recommendations]] - Balanced fertilization
- [[Padi-Identification]] - Variety susceptibility
