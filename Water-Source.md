# Category 5: Water Source & Management

Critical for padi cultivation, especially distinguishing lowland vs. upland farming.

## Water Source Types

### 1. Rain-Fed
- Monsoon-dependent
- No irrigation infrastructure
- High risk in drought years
- Suitable for resilient varieties

### 2. Irrigation Scheme
- Government-managed irrigation
- Scheduled water release
- Annual fees/dues
- Most reliable source

### 3. Pump from River
- Direct river pumping
- Pump and fuel costs
- Electricity/diesel expenses
- Capacity depends on pump size

### 4. Well/Borehole
- Groundwater source
- Pump required
- Water quality testing needed
- Sustainability concerns

### 5. Reservoir/Dam
- On-farm storage
- Gravity-fed distribution
- Infrastructure costs
- Drought buffer

## Water Management Recommendations

### Alternate Wetting and Drying (AWD)
- Water-saving technique
- 15-25% water savings
- Maintain yields with proper timing
- Monitor water table levels

### Recommended Water Depths
| Growth Stage | Water Depth |
|---------------|-------------|
| Land preparation | 5-10 cm |
| Transplanting | 2-3 cm |
| Tillering | 3-5 cm |
| Panicle initiation | 5-7 cm |
| Flowering | 5-10 cm |
| Grain filling | 3-5 cm |
| Maturity | Drain 2-3 weeks before harvest |

## Cost Analysis

### Pump Costs (if applicable)
- Pump purchase/lease cost
- Fuel/electricity cost per hour
- Maintenance costs
- Hose and pipe costs

### Infrastructure Costs (Tiered)
| Tier | Components | Estimated Cost |
|------|------------|----------------|
| Basic | Hose, fittings | RM 200-500 |
| Standard | Pump, pipes, hose | RM 1,000-3,000 |
| Advanced | Motorized pump, pipelines | RM 5,000-15,000 |

## Weather Integration

Link water recommendations with [[Weather-Monitoring]]:
- If rain-fed: Advise on planting timing based on monsoon onset
- Forecast-based irrigation scheduling
- Drainage recommendations before heavy rain

## Variety Water Requirements

| Variety Type | Water Requirement |
|--------------|-------------------|
| Lowland (flood-tolerant) | High, can tolerate 10-50cm flooding |
| Upland (drought-tolerant) | Moderate, some drought resistance |
| Aerobic rice | Low, bred for water-saving |

## Related Categories

- [[Weather-Monitoring]] - Forecast-based scheduling
- [[Padi-Identification]] - Drought tolerance by variety
- [[Plantation-Method]] - Water management affects method choice
- [[Costing-Economic-Viability]] - Water infrastructure costs

---

# Implementation: Water Source Node

## ✅ Features Implemented

### Node ID: `WATER-SOURCE-001`

- [x] Water source type analysis
- [x] Cost calculation
- [x] Reliability scoring
- [x] AWD schedule generator
- [x] Risk identification

## Code: `additional_nodes.py`
