# Language & Accessibility

Designing for farmers with varying literacy levels and language preferences.

## Language Support

### Primary Languages
- [ ] Bahasa Malaysia (primary for Malaysian farmers)
- [ ] English (secondary)
- [ ] Mandarin (for Chinese farmers)
- [ ] Tamil (for Indian farmers)
- [ ] Local dialects (e.g., Kelantanese, Terengganu)

### Translation Quality
- Simple, clear translations
- Avoid technical jargon in local language
- Test with actual farmers from target demographics

## Visual Design Principles

### Iconography
Use intuitive icons for:
- Weather conditions
- Cost indicators
- Action buttons
- Disease/pest identification
- Navigation

### Color Coding
| Meaning | Color |
|---------|-------|
| Warning/Alert | Orange |
| Danger/Critical | Red |
| Success/Good | Green |
| Information | Blue |
| Cost (High) | Red |
| Cost (Medium) | Yellow |
| Cost (Low) | Green |

## Simple Language Guidelines

### Do's
- Use short sentences
- Active voice
- Concrete examples
- Step-by-step instructions
- Positive framing

### Don'ts
- Avoid technical terms without explanation
- No lengthy paragraphs
- Avoid conditional complexity
- No ambiguous instructions

### Example Transformations

**Technical:**
"Apply NPK 15-15-15 at rate of 200kg/ha as basal dressing 7 days before transplanting"

**Simple:**
"Grow bigger rice: Mix 4 bags of fertilizer (50kg each) with soil before planting"

## Voice Input/Output

### Voice Recognition
- Farmers can speak commands
- Report symptoms verbally
- Ask questions by voice

### Voice Output (Text-to-Speech)
- Read recommendations aloud
- Works while farmer is working in field
- Multiple language support

### Implementation
- Use on-device voice recognition (works offline)
- Cloud ASR for better accuracy
- Local TTS for responses

## Accessibility Features

### Font Size
- Default: 18-20pt minimum
- Adjustable up to 28pt
- High contrast mode

### Navigation
- Large touch targets (48dp minimum)
- Simple, linear navigation
- Back button always visible
- Progress indicators

### Offline-First Design
- Core features work without internet
- Sync when connection available
- Clear offline/online status indicators

## Testing with Real Users

### User Testing Sessions
- Conduct with 5-10 farmers per target demographic
- Observe actual usage
- Gather feedback on clarity
- Iterate based on findings

### Feedback Mechanisms
- Easy way to report confusion
- Suggestion submission
- Rating system for recommendations

## Related Categories

- [[Data-Privacy-Offline]] - Offline functionality
- [[Stakeholder-Integration]] - Extension officer support
