# Batch Processing System for Transaction Verification

## Overview
The batch processing system allows you to re-process all existing transactions with Ollama AI to verify and update transaction details like vendor names, amounts, categories, and confidence scores.

## Key Features
- **Part-by-part processing**: Processes transactions in small batches to avoid overwhelming Ollama
- **Automatic verification**: Compares Ollama results with existing data and updates only when necessary
- **Progress tracking**: Real-time progress reporting with detailed logs
- **Database updates**: Automatically updates transaction records with improved data
- **Error handling**: Robust error handling with detailed error reporting

## Usage Options

### 1. Command Line Script
```bash
python run_batch_processing.py
```
- Interactive mode with user confirmation
- Configurable batch size and limits
- Detailed progress reporting

### 2. FastAPI Endpoints
```bash
# Preview transactions to be processed
GET /v1/batch/preview?limit=10

# Start batch processing job
POST /v1/batch/process-transactions
{
    "limit": 50,
    "batch_size": 3,
    "delay_between_batches": 5
}

# Check job status
GET /v1/batch/job-status/{job_id}
```

## Configuration
- **Batch Size**: 3-5 transactions per batch (recommended)
- **Delay Between Batches**: 3-5 seconds (prevents Ollama overload)
- **Processing Time**: ~15-45 seconds per transaction
- **Ollama Host**: http://localhost:11434 (configurable)

## What Gets Updated
The system verifies and updates:
- **Vendor names**: Cleans up formatting, removes extra characters
- **Transaction amounts**: Ensures accuracy
- **Categories**: Improves categorization based on AI analysis
- **Confidence scores**: Updates based on AI confidence
- **Transaction IDs**: Extracts UPI refs and transaction IDs
- **Dates**: Verifies and corrects transaction dates

## Example Results
```
Processing 1/2: Transaction ID 216
Processing time: 46.43s
Ollama Results:
  Vendor: AMAZON RETAIL
  Amount: Rs.1234.56
  Category: Shopping
  Confidence: 0.9

[SUCCESS] Updated transaction with 2 changes:
  • vendor: 'AMAZON RETAIL.' -> 'AMAZON RETAIL'
  • confidence: 0.95 -> 0.9
```

## Benefits
1. **Data Quality**: Improves accuracy of existing transaction data
2. **Consistency**: Standardizes vendor names and categories
3. **Completeness**: Fills in missing transaction IDs and details
4. **Analytics Ready**: Ensures data is ready for visualization and analytics
5. **Privacy**: All processing happens locally with Ollama

## Monitoring
- Real-time progress updates
- Success/failure statistics
- Processing time metrics
- Detailed update logs
- Error reporting and recovery

The batch processing system ensures all your historical transaction data is verified and enhanced with AI, providing a solid foundation for financial analytics and visualizations.
