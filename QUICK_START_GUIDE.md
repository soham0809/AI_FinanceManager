# Quick Start Guide - AI Financial Co-Pilot

## 🚀 Getting Started

### 1. Start the Backend Server
```bash
# Navigate to project root
cd c:\Users\soham\Desktop\final_year

# Start backend server
.\start_backend.bat
```

**Expected Output**:
```
Starting AI Financial Co-Pilot Backend Server...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 2. Verify Backend is Running
Open browser and go to: `http://localhost:8000/health`

**Expected Response**:
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "timestamp": "2025-09-23T01:15:00.000000"
}
```

### 3. Start Mobile App
```bash
# Navigate to mobile app directory
cd mobile_app

# Get dependencies
flutter pub get

# Run the app
flutter run
```

## 🧪 Testing the System

### Test SMS Parsing
Send a POST request to test SMS parsing:
```bash
curl -X POST http://localhost:8000/v1/parse-sms \
  -H "Content-Type: application/json" \
  -d '{"sms_text": "HDFC Bank: Rs.500.00 debited from A/c **1234 on 23-09-24 at AMAZON INDIA. Avl Bal: Rs.5000.00"}'
```

### Test Analytics
Check analytics endpoints:
- Transactions: `http://localhost:8000/v1/transactions`
- Category Spending: `http://localhost:8000/v1/analytics/spending-by-category`
- Monthly Trends: `http://localhost:8000/v1/analytics/monthly-trends`

### Run Automated Tests
```bash
# Run comprehensive test suite
python simple_test.py
```

## 📱 Mobile App Features

### 1. SMS Parsing
- Paste SMS text into the app
- Automatically extracts transaction details
- Stores in database with confidence scores

### 2. Analytics Dashboard
- Real-time spending insights
- Category-wise breakdown
- Monthly trends
- Top vendors

### 3. Transaction Management
- View all transactions
- Search and filter
- Edit categories
- Delete transactions

## 🔧 Configuration

### API Endpoints
- **Health Check**: `GET /health`
- **Parse SMS**: `POST /v1/parse-sms`
- **Get Transactions**: `GET /v1/transactions`
- **Analytics**: `GET /v1/analytics/*`

### Database
- **Location**: `backend/financial_copilot.db`
- **Type**: SQLite
- **Tables**: transactions, categories, users

### AI Integration
- **Gemini API**: Enabled for intelligent SMS parsing
- **ML Categorization**: Trained model for vendor categorization
- **Confidence Scoring**: Quality assessment for parsed data

## 🐛 Troubleshooting

### Backend Won't Start
1. Check if port 8000 is available
2. Ensure Python virtual environment is activated
3. Install dependencies: `pip install -r requirements.txt`

### Mobile App Connection Issues
1. Verify backend is running on `http://localhost:8000`
2. Check API service configuration in `lib/services/api_service.dart`
3. For physical device, update IP address to computer's local IP

### Analytics Not Updating
1. Check if transactions are being saved to database
2. Verify analytics endpoints return data
3. Refresh analytics dashboard manually
4. Check console logs for errors

## 📊 Sample Data

The system comes with sample transactions for testing:
- 38+ transactions across multiple categories
- Various vendors (Amazon, Swiggy, Netflix, etc.)
- Different transaction types (debit/credit)
- Total spending: ~Rs.50,000

## 🔐 Security Notes

- Gemini API key is configured in `main.py`
- Database is local SQLite (no external connections)
- No sensitive data is logged
- API endpoints use CORS for development

## 📈 Performance

- **SMS Parsing**: ~1-2 seconds per message
- **Analytics Calculation**: Real-time
- **Database Queries**: Optimized with indexes
- **Mobile App**: Responsive UI with offline fallback

---

**System Status**: ✅ Fully Operational
**Last Updated**: 2025-09-23 01:15 IST
