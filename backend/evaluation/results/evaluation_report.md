# SMS Parsing Evaluation Report
Generated: 2025-12-30 13:34:20

## Dataset Summary
- **Total Samples**: 286
- **SMS Types**: UPI, CREDIT_CARD, DEBIT_CARD, SUBSCRIPTION, NET_BANKING, OTHER, NO_TRANSACTION, BANK_CHARGE
- **Categories**: 43

## Results Summary

### 1. SMS Type Classification
| Metric | Value |
|--------|-------|
| Accuracy | 59.09% |
| Precision | 62.05% |
| Recall | 59.09% |
| F1-Score | 55.33% |

### 2. Category Classification
| Metric | Value |
|--------|-------|
| Accuracy | 27.27% |
| Precision | 30.38% |
| Recall | 27.27% |
| F1-Score | 24.57% |

### 3. Amount Extraction
| Metric | Value |
|--------|-------|
| Exact Match | 83.57% |
| Close Match (±1%) | 83.57% |

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
in SMS parsing with an overall type classification accuracy of 59.09%.
