# AI Financial Co-Pilot Backend API Documentation

## Overview
This API provides endpoints for SMS transaction parsing, ML-powered categorization, analytics, and AI predictive insights for personal finance management.

**Base URL:** `http://localhost:8000`

## Authentication
Currently no authentication required. In production, implement JWT or API key authentication.

## Health Check

### GET /health
Check if the API server is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "timestamp": "2025-09-11T01:30:52.005649"
}
```

## SMS Parsing & Transaction Management

### POST /v1/parse-sms
Parse transaction SMS and extract structured data.

**Request Body:**
```json
{
  "sms_text": "Your account debited by Rs.250 at Zomato on 2025-01-10"
}
```

**Response (Success):**
```json
{
  "vendor": "Zomato",
  "amount": 250.0,
  "date": "2025-09-11T01:31:59.509139",
  "transaction_type": "debit",
  "category": "Food & Dining",
  "success": true,
  "raw_text": "Your account debited by Rs.250 at Zomato on 2025-01-10",
  "confidence": 0.95
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "No matching transaction pattern found",
  "error_type": "PATTERN_NOT_FOUND",
  "raw_text": "Invalid SMS text",
  "suggestions": [
    "Check if SMS contains transaction keywords (debited, credited, paid)",
    "Verify amount format (Rs. or INR)",
    "Ensure vendor/merchant name is present"
  ]
}
```

### GET /v1/transactions
Get all transactions with optional filtering.

**Query Parameters:**
- `limit` (optional): Maximum number of transactions (default: 50)
- `category` (optional): Filter by category
- `transaction_type` (optional): Filter by type (debit/credit)

**Response:**
```json
{
  "transactions": [
    {
      "id": 1,
      "vendor": "Zomato",
      "amount": 250.0,
      "date": "2025-01-10",
      "transaction_type": "debit",
      "category": "Food & Dining"
    }
  ],
  "total": 1
}
```

### GET /v1/transactions/{id}
Get a specific transaction by ID.

### PUT /v1/transactions/{id}
Update a transaction.

**Request Body:**
```json
{
  "vendor": "Updated Vendor",
  "amount": 300.0,
  "category": "Shopping"
}
```

### DELETE /v1/transactions/{id}
Delete a transaction.

## ML Categorization

### POST /v1/categorize
Categorize a vendor using the ML model.

**Query Parameters:**
- `vendor`: Vendor name to categorize

**Response:**
```json
{
  "vendor": "Zomato",
  "predicted_category": "Food & Dining",
  "confidence": 0.95,
  "all_probabilities": {
    "Food & Dining": 0.95,
    "Shopping": 0.03,
    "Transportation": 0.01,
    "Entertainment": 0.01
  }
}
```

### GET /v1/ml/model-info
Get information about the ML categorization model.

**Response:**
```json
{
  "model_type": "MultinomialNB",
  "categories": ["Food & Dining", "Shopping", "Transportation", "Entertainment", "Healthcare"],
  "accuracy": 0.92,
  "training_samples": 150,
  "last_trained": "2025-09-11T01:00:00"
}
```

## Analytics

### GET /v1/analytics/spending-by-category
Get spending breakdown by category.

**Response:**
```json
{
  "categories": [
    {
      "category": "Food & Dining",
      "total_amount": 2500.0,
      "percentage": 45.5,
      "transaction_count": 12
    }
  ],
  "total_spending": 5500.0
}
```

### GET /v1/analytics/monthly-trends
Get monthly spending trends.

**Response:**
```json
{
  "trends": [
    {
      "month": "2025-01",
      "total_amount": 5500.0,
      "transaction_count": 25
    }
  ]
}
```

### GET /v1/analytics/spending-insights
Get AI-generated spending insights.

**Response:**
```json
{
  "insights": {
    "total_transactions": 50,
    "total_spending": 15000.0,
    "average_transaction": 300.0,
    "top_category": "Food & Dining",
    "spending_trend": "increasing"
  }
}
```

### GET /v1/analytics/top-vendors
Get top spending vendors.

**Query Parameters:**
- `limit` (optional): Number of vendors to return (default: 10)

**Response:**
```json
{
  "vendors": [
    {
      "vendor": "Zomato",
      "total_amount": 2500.0,
      "transaction_count": 12,
      "category": "Food & Dining"
    }
  ]
}
```

## AI Predictive Analytics

### POST /v1/predictions/train-models
Train AI prediction models using historical data.

**Response:**
```json
{
  "message": "Models trained successfully",
  "categories_trained": ["Food & Dining", "Shopping", "Transportation"],
  "model_scores": {
    "Food & Dining": 10.0,
    "Shopping": 5.5
  }
}
```

### GET /v1/predictions/spending-forecast
Get AI spending forecasts.

**Query Parameters:**
- `category` (optional): Get forecast for specific category

**Response:**
```json
{
  "forecasts": [
    {
      "category": "Food & Dining",
      "current_month_prediction": 450.0,
      "next_month_prediction": 472.5,
      "confidence_score": 0.79,
      "trend": "increasing",
      "recommendation": "Consider setting a budget limit for food expenses"
    }
  ]
}
```

### POST /v1/predictions/savings-goal
Create and analyze a savings goal.

**Request Body:**
```json
{
  "target_amount": 100000,
  "target_months": 12,
  "current_income": 50000,
  "current_expenses": 35000
}
```

**Response:**
```json
{
  "target_amount": 100000,
  "target_months": 12,
  "monthly_required": 8333.33,
  "achievable": true,
  "recommendation": "You can achieve this goal by saving 55.6% of your surplus income"
}
```

### POST /v1/predictions/budget-alerts
Get budget alerts based on spending limits.

**Request Body:**
```json
{
  "limits": {
    "Food & Dining": 5000,
    "Shopping": 15000,
    "Transportation": 3000
  }
}
```

**Response:**
```json
{
  "alerts": [
    {
      "category": "Food & Dining",
      "current_spending": 4500.0,
      "budget_limit": 5000.0,
      "percentage_used": 90.0,
      "alert_level": "warning",
      "message": "You've used 90% of your Food & Dining budget"
    }
  ]
}
```

### GET /v1/predictions/financial-insights
Get AI-generated financial insights and recommendations.

**Response:**
```json
{
  "insights": {
    "top_category": "Your highest spending is in Food & Dining (45% of total)",
    "avg_transaction": "Your average transaction is Rs.300",
    "frequency": "You make 2.5 transactions per day on average",
    "weekend_pattern": "Weekend spending is 40% higher than weekdays"
  }
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

Error responses follow this format:
```json
{
  "detail": "Error message description",
  "error_type": "ERROR_TYPE",
  "suggestions": ["Helpful suggestion"]
}
```

## Rate Limiting
Currently no rate limiting implemented. In production, implement rate limiting based on IP or API key.

## Data Models

### Transaction
```json
{
  "id": "integer",
  "vendor": "string",
  "amount": "float",
  "date": "string (ISO format)",
  "transaction_type": "string (debit/credit)",
  "category": "string",
  "raw_text": "string"
}
```

### Categories
- Food & Dining
- Shopping
- Transportation
- Entertainment
- Healthcare
- Bills & Utilities
- Financial
- Travel
- Education
- Other

## Integration Examples

### Flutter/Dart Example
```dart
// Parse SMS
final response = await http.post(
  Uri.parse('$baseUrl/v1/parse-sms'),
  headers: {'Content-Type': 'application/json'},
  body: json.encode({'sms_text': smsText}),
);

if (response.statusCode == 200) {
  final data = json.decode(response.body);
  if (data['success']) {
    // Handle successful parsing
    print('Amount: ${data['amount']}');
    print('Vendor: ${data['vendor']}');
    print('Category: ${data['category']}');
  }
}
```

### cURL Examples
```bash
# Parse SMS
curl -X POST "http://localhost:8000/v1/parse-sms" \
  -H "Content-Type: application/json" \
  -d '{"sms_text": "Your account debited by Rs.250 at Zomato"}'

# Get spending forecast
curl -X GET "http://localhost:8000/v1/predictions/spending-forecast"

# Train ML models
curl -X POST "http://localhost:8000/v1/predictions/train-models"
```

## Security Considerations

1. **Input Validation**: All inputs are validated and sanitized
2. **SQL Injection**: Using SQLAlchemy ORM prevents SQL injection
3. **CORS**: Configured for Flutter app integration
4. **Error Handling**: Structured error responses without sensitive data exposure

## Performance Notes

1. **ML Model Loading**: Models are loaded once at startup
2. **Database**: SQLite for development, consider PostgreSQL for production
3. **Caching**: Consider implementing Redis for frequently accessed data
4. **Async**: FastAPI handles requests asynchronously

## Future Enhancements

1. **Authentication**: JWT token-based authentication
2. **Real-time Updates**: WebSocket support for live transaction updates
3. **Export Features**: PDF/CSV export of transaction data
4. **Multi-user Support**: User accounts and data isolation
5. **Advanced Analytics**: More sophisticated ML models and insights
