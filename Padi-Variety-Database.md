# Padi Variety Database

Localised variety information for the target region.

## Recommended Varieties (Malaysia)

### High-Yielding Varieties

| Variety | Duration | Yield (t/ha) | Characteristics |
|---------|----------|--------------|-----------------|
| MR219 | 120-130 days | 7-9 | Aromatic, long grain |
| MR220 | 115-125 days | 6-8 | Good tillering |
| MR263 | 105-115 days | 5-7 | Early maturing |
| MR269 | 110-120 days | 6-8 | Blast resistant |
| MR297 | 115-125 days | 6-8 | Good grain quality |

### Traditional/Local Varieties

| Variety | Duration | Yield (t/ha) | Characteristics |
|---------|----------|--------------|-----------------|
| Koshihikari | 130-140 days | 4-5 | Premium Japanese |
| Putah | 130-150 days | 3-4 | Aromatic, tall |
| Borneo | 140-160 days | 3-4 | Photoperiod sensitive |

### Specialty Varieties

| Variety | Duration | Yield (t/ha) | Characteristics |
|---------|----------|--------------|-----------------|
| Japonica | 120-130 days | 5-6 | Short grain, cold tolerant |
| Basmati | 130-150 days | 3-4 | Extra long grain, aromatic |

## Data Structure Per Variety

```yaml
variety:
  name: "MR219"
  synonyms: ["MR 219", "MR219-9"]
  
  characteristics:
    duration_days: 125
    plant_height_cm: 95-105
    grain_type: "long"
    amylose_content: "high"
    
  performance:
    yield_range: [7, 9]
    unit: "t/ha"
    
  tolerances:
    drought: "moderate"
    flood: "moderate"
    salinity: "low"
    
  susceptibility:
    blast: "low"
    blight: "moderate"
    tungro: "moderate"
    
  requirements:
    nitrogen_kg_ha: 120-150
    water_mm: 1200-1500
    
  region:
    primary: ["Kedah", "Perlis", "Perak"]
    season: ["main", "off"]
    
  seed_availability:
    source: "MARDI, KADA"
    price_per_50kg: 180
```

## Growth Stage Reference

### Stage Definitions

| Stage | Days After Sowing | Key Activities |
|-------|------------------|----------------|
| Germination | 0-5 | Seed imbibition, radicle emergence |
| Seedling | 5-21 | 3-4 leaf stage, nursery phase |
| Tillering | 21-45 | Vegetative growth, side shoots |
| Panicle Initiation | 45-55 | Reproductive stage begins |
| Booting | 55-70 | Flag leaf emergence |
| Heading/Flowering | 70-85 | Anthesis, pollination |
| Grain Filling | 85-110 | Grain development |
| Maturity | 110-130 | Grain hardening, harvest |

## Selection Guide

### By Farm Type

**Lowland (Irrigated)**
- MR219, MR220, MR297
- Focus on yield and quality

**Upland (Rain-fed)**
- MR263, local varieties
- Focus on drought tolerance

**Flood-prone Areas**
- BR10, Bujang
- Focus on flood tolerance

### By Season

**Main Season (Musim Utama)**
- Longer duration varieties OK
- MR219, MR220

**Off Season (Musim Off)**
- Shorter duration preferred
- MR263, MR269

## Related Categories

- [[Padi-Identification]] - Identification methods
- [[Fertilizer-Recommendations]] - Variety-specific fertilizer
- [[Disease-Management]] - Disease susceptibility
- [[Water-Source]] - Water requirements
