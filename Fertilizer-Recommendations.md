# Category 4: Fertilizer Recommendations

Fertilizer recommendations must account for variety, soil baseline, growth stage, and farmer preference (organic vs. synthetic).

## Recommendation Components

### 1. Fertilizer Type
- NPK ratio selection
- Urea (46-0-0)
- Compound fertilizers (15-15-15, 20-20-20)
- Organic compost
- Organic supplements (bone meal, fish emulsion)
- Micronutrient blends

### 2. Application Timing
- Basal application (before planting)
- Top-dressing at specific growth stages
  - Tillering stage (21-28 days after sowing)
  - Panicle initiation (45-55 days)
  - Flowering stage

### 3. Quantity Calculation
- Per hectare (ha)
- Per relong ( Malaysian unit = 0.71 acres)
- Per sq meter
- Based on soil test results
- Variety-specific requirements

### 4. Cost Estimation
- Ringgit per hectare
- Ringgit per relong
- Price per 50kg bag
- Seasonal price trends

### 5. Sourcing Information
- Local cooperative contacts
- Agrovet shop locations
- Estimated prices
- Delivery options

## Fertilizer Calculator

See [[Fertilizer-Calculator]] for trade-off analysis.

### Calculator Features
- Compare cheapest option vs. highest yield
- Organic vs. synthetic comparison
- Split application optimizer
- Cost-benefit analysis

## Malaysian Context

### Subsidy Information
- KADA (Kedah) subsidy programs
- MADA (Kedah) fertilizer assistance
- State-specific subsidies
- Federal agriculture aid

### Common Fertilizers in Malaysia
| Fertilizer | N-P-K | Typical Price (50kg) |
|------------|-------|---------------------|
| Urea | 46-0-0 | RM 85-95 |
| NPK 15-15-15 | 15-15-15 | RM 95-110 |
| NPK Blue | 12-12-17-2 | RM 105-120 |
| Compound A | 20-10-10 | RM 90-100 |

## Growth Stage Recommendations

### Seedling Stage (0-21 days)
- Light basal dose
- Focus on phosphorus for root development

### Tillering Stage (21-45 days)
- Nitrogen emphasis
- First top-dressing
- Zinc supplementation if needed

### Panicle Initiation (45-55 days)
- Second top-dressing
- Balanced NPK
- Potassium boost

### Flowering & Grain Fill (55-90 days)
- Reduced nitrogen
- Potassium for grain quality
- Late foliar application optional

## Related Categories

- [[Soil-Analysis]] - Based on soil nutrient status
- [[Padi-Identification]] - Variety-specific N requirements
- [[Water-Source]] - Water availability affects fertilizer timing
- [[Costing-Economic-Viability]] - Cost comparisons

---

# Implementation: Fertilizer Recommendations Node

## ✅ Features Implemented

### Node ID: `FERTILIZER-001`

### 1. Fertilizer Products
- [x] Malaysian fertilizer database
- [x] Urea products
- [x] NPK compounds
- [x] Organic fertilizers
- [x] Micronutrient products

### 2. Recommendations
- [x] Soil-based recommendations
- [x] Growth stage timing
- [x] Split application
- [x] Organic alternatives

### 3. Cost Analysis
- [x] Price per kg calculation
- [x] Cost comparison tools
- [x] ROI calculation
- [x] Strategy comparison

### 4. Subsidy Integration
- [x] KADA subsidy
- [x] MADA subsidy
- [x] Federal subsidy
- [x] Claim calculation

### 5. Comparison Tools
- [x] Synthetic vs organic
- [x] Integrated approach
- [x] Net return calculation

---

## Code Files

| File | Description |
|------|-------------|
| `fertilizer_recommendations_node.py` | Complete implementation |
