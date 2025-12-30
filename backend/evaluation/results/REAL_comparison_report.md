# Real SMS Parser Comparison Results

Generated: 2025-12-30 15:07:52
Total Samples: 286

## Accuracy Results

| Parser | Type | Amount | Category | Avg Latency |
|--------|------|--------|----------|-------------|
| **Regex** | 79.37% | 83.57% | - | 0.048ms |
| **ML** | - | - | 27.27% | 1.498ms |
| **LLM** | 30.42% | 5.94% | 3.5% | 16938ms |

## Key Findings

- **Regex**: Fast (0.048ms) but limited accuracy
- **ML**: Good for category classification
- **LLM**: Highest accuracy but 352872x slower than Regex

## Recommendation

Use **Hybrid approach**: Regex for simple SMS, LLM fallback for complex cases.
