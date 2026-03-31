# Padi AI Agent System

A comprehensive agentic AI system for padi (rice) farming recommendations.

## System Architecture

### Agentic Workflow

1. **Identification Agent** - Determines padi type via image, farmer input, or geolocation + season
2. **Context Aggregator** - Pulls soil data (historical or sensor), weather forecast, water availability
3. **Recommendation Engine** - Generates ranked solutions with cost tiers
4. **Output Formatter** - Presents results in simple language with local units (ringgit per acre, kg/ha)

### Agent Types

- Single orchestrator agent that calls specialized sub-agents
- Separate agents per category that collaborate
- Conversational interface that guides farmers step-by-step

## Categories

1. [[Padi-Identification]] - Identifying Padi Type
2. [[Weather-Monitoring]] - Real-Time Weather Monitoring
3. [[Soil-Analysis]] - Soil Analysis
4. [[Fertilizer-Recommendations]] - Fertilizer Management
5. [[Water-Source]] - Water Source & Management
6. [[Plantation-Method]] - Plantation Method
7. [[Disease-Management]] - Disease Management
8. [[Harvest-PostHarvest]] - Harvest & Post-Harvest

## Critical Components

- [[Costing-Economic-Viability]] - Costing & Economic Viability
- [[Platform-Items]] - Platform of Items Needed
- [[Labor-Considerations]] - Labor Considerations
- [[Language-Accessibility]] - Language & Accessibility
- [[Data-Privacy-Offline]] - Data Privacy & Offline Capability
- [[Stakeholder-Integration]] - Stakeholder Integration

## Related

- [[Padi-Variety-Database]] - Localized Padi Variety Database
- [[Disease-Library]] - Common Padi Diseases Library
- [[Fertilizer-Calculator]] - Fertilizer Calculator
