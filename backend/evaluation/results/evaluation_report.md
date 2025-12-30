# SMS Parsing Evaluation Report
Generated: 2025-12-30 12:33:27

## Dataset Summary
- **Total Samples**: 93
- **SMS Types**: UPI, CREDIT_CARD, DEBIT_CARD, SUBSCRIPTION, NET_BANKING, OTHER
- **Categories**: 9

## Results Summary

### 1. SMS Type Classification
| Metric | Value |
|--------|-------|
| Accuracy | 68.82% |
| Precision | 77.73% |
| Recall | 68.82% |
| F1-Score | 67.73% |

### 2. Category Classification
| Metric | Value |
|--------|-------|
| Accuracy | 34.41% |
| Precision | 41.15% |
| Recall | 34.41% |
| F1-Score | 31.06% |

### 3. Amount Extraction
| Metric | Value |
|--------|-------|
| Exact Match | 98.92% |
| Close Match (±1%) | 98.92% |

### 4. Processing Performance
- Average Time: 0.02ms per SMS

## Generated Plots
1. `confusion_matrix_type.png` - Type classification confusion matrix
2. `confusion_matrix_category.png` - Category classification confusion matrix  
3. `accuracy_comparison.png` - Overall accuracy comparison
4. `f1_scores_by_type.png` - F1 scores by SMS type
5. `processing_time_histogram.png` - Processing time distribution

## Conclusion
The AI Finance Manager demonstrates moderate performance 
in SMS parsing with an overall type classification accuracy of 68.82%.
