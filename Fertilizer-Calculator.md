# Fertilizer Calculator

Interactive tool for fertilizer recommendations and trade-off analysis.

## Calculator Features

### 1. Basic Recommendation
Input:
- Soil test results (N, P, K, pH)
- Padi variety
- Target yield
- Farm size (hectare/relong)

Output:
- Recommended fertilizer types
- Application rates
- Timing schedule
- Estimated cost

### 2. Cost Comparison Mode

Compare different fertilizer strategies:

| Strategy | Cost (RM/ha) | Expected Yield | Net Return |
|----------|-------------|----------------|------------|
| Minimum | 400 | 4 t/ha | 4,000 |
| Standard | 800 | 6 t/ha | 7,200 |
| Premium | 1,400 | 7.5 t/ha | 8,600 |

### 3. Organic vs. Synthetic

| Factor | Organic | Synthetic |
|--------|---------|----------|
| Cost | Lower (if on-farm) | Higher |
| Availability | Variable | Consistent |
| Release speed | Slow | Fast |
| Soil health | Improves | Neutral |
| Yield (short-term) | Lower | Higher |
| Yield (long-term) | Comparable | May decline |

### 4. Split Application Optimizer

Minimize nitrogen loss through split applications:

**Single Application**
- Higher N loss
- Higher luxury consumption
- Higher lodging risk

**Split Application (Recommended)**
- Basal: 30-40% N
- Tillering: 30-40% N
- Panicle initiation: 20-30% N
- Lower loss, better utilization

## Standard Recommendations (Malaysia)

### For MR219 @ 6 t/ha Target

| Growth Stage | Fertilizer | Rate (kg/ha) | Timing |
|--------------|-----------|--------------|--------|
| Basal | NPK 15-15-15 | 100 | 7 days before planting |
| Tillering | Urea 46% N | 100 | 21 DAP |
| Panicle Initiation | NPK Blue 12-12-17-2 | 100 | 45 DAP |
| **Total N** | | 97 kg N/ha | |

### Adjustment by Soil Test

**If Soil N is LOW:**
- Increase basal N by 20%
- Consider foliar N at tillering

**If Soil P is LOW:**
- Increase basal P2O5
- Use DAP or TSP as basal

**If Soil K is LOW:**
- Increase K2O at panicle initiation
- Use NPK Blue or SOP

## Cost-Benefit Analysis

### Fertilizer Investment Returns

| Investment | Additional Cost | Yield Increase | Net Benefit |
|-------------|----------------|----------------|-------------|
| +50kg N/ha | RM 100 | +0.5 t/ha | +RM 900 |
| +25kg P2O5/ha | RM 80 | +0.3 t/ha | +RM 520 |
| +25kg K2O/ha | RM 75 | +0.2 t/ha | +RM 325 |

*Assumes paddy price: RM 2,000/t*

## Subsidy Integration

### Malaysia Fertilizer Subsidies
- Federal subsidy program
- State-specific programs (KADA, MADA)
- Maximum claim limits
- Eligible fertilizer types

### Calculator Features
- [ ] Show subsidy eligibility
- [ ] Calculate net cost after subsidy
- [ ] List application requirements

## Related Categories

- [[Fertilizer-Recommendations]] - Detailed recommendations
- [[Soil-Analysis]] - Soil-based adjustments
- [[Padi-Identification]] - Variety-specific needs
- [[Costing-Economic-Viability]] - Cost analysis
