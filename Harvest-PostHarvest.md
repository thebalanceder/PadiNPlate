# Category 8: Harvest & Post-Harvest

End-to-end value addition from harvest timing to market access.

## Harvest Timing

### Indicators for Harvest
- Grain moisture content (20-25%)
- Days after flowering (30-35 days for most varieties)
- Leaf color (80% yellowing)
- Grain hardness (firm when pressed)
- Panicle appearance (90% of grains turned golden)

### Harvest Windows
- Optimal: 7-10 days from maturity
- Too early: Low grain weight, high immature grains
- Too late: Lodging risk, shattering losses

## Harvesting Methods

### Manual Harvesting
- Sickle cutting
- Lower capital cost
- Higher labor requirement
- Suitable for small plots
- Man-days: 15-25 per hectare

### Mechanical Harvesting
- Combine harvester
- Higher efficiency
- Capital/lease cost
- Suitable for large areas
- Capacity: 2-4 hectares per day

## Post-Harvest Operations

### 1. Threshing
| Method | Efficiency | Grain Damage |
|--------|------------|--------------|
| Manual (trampling) | 95-98% | Low |
| Mechanical thresher | 98-99% | Low |
| Combine harvester | 99%+ | Minimal |

### 2. Drying

#### Sun Drying
- Traditional method
- 2-3 days for moisture to 14%
- Requires labor for raking
- Weather dependent
- Risk of cracking if over-dried

#### Mechanical Drying
- Batch dryer or flatbed dryer
- 4-8 hours for drying
- Better grain quality
- Operating cost (fuel/electricity)
- RM 30-50 per ton

#### Moisture Content Targets
| Purpose | Moisture Content |
|---------|-----------------|
| Storage (>3 months) | 12-13% |
| Short-term storage | 14% |
| Milling immediately | 14-15% |

### 3. Storage

#### Storage Methods
- [ ] Traditional barn (elevated)
- [ ] Metal silos
- [ ] Pusa bins
- [ ] Hermetic storage bags
- [ ] Cold storage (premium)

#### Storage Best Practices
- Clean, dry storage facility
- Moisture-proof flooring
- Pest control (rats, insects)
- Regular monitoring
- First-in-first-out rotation

### 4. Milling

#### Options
- Village rice mill
- Commercial rice mill
- Custom milling service

#### Quality Factors
- Head rice recovery percentage
- Whiteness/clarity
- Broken rice percentage
- Foreign matter content

## Selling Options

### Price Considerations
- Farm gate price vs. market price
- Paddy vs. milled rice
- Quality grades
- Seasonal price trends

### Market Channels

| Channel | Advantages | Disadvantages |
|---------|------------|---------------|
| Direct to miller | Immediate payment | Lower price |
| Collector/middleman | Convenience | Lower price |
| Cooperative | Better prices | Quality requirements |
| Direct to consumer | Highest price | Marketing effort |
| Government (Beras) | Guaranteed price | Quality standards |

### Price Enhancement
- Quality sorting
- Proper drying and storage
- Off-season selling
- Value-added products (organic, specialty rice)

## Related Categories

- [[Padi-Identification]] - Variety affects harvest timing
- [[Weather-Monitoring]] - Weather affects harvest scheduling
- [[Labor-Considerations]] - Labor for harvesting operations
- [[Costing-Economic-Viability]] - Post-harvest cost analysis

---

# Implementation: Harvest-PostHarvest Node

## ✅ Features Implemented

### Node ID: `HARVEST-001`

- [x] Harvest timing calculation
- [x] Moisture content estimation
- [x] Condition assessment
- [x] Drying method recommendations
- [x] Storage method recommendations
- [x] Cost estimation

## Code: `additional_nodes.py`
