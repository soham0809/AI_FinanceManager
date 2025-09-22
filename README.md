# AI Financial Co-Pilot for Students

An intelligent financial assistant that automatically tracks expenses through SMS parsing using **Gemini AI** and provides predictive insights for better financial management.

## Key Features

- **Zero-Touch Expense Tracking**: Automatically captures spending data by parsing transaction SMS alerts from banks and UPI apps
- **Gemini AI-Powered SMS Parsing**: Uses Google's Gemini AI for intelligent transaction extraction and categorization
- **Smart Duplicate Detection**: Prevents duplicate transactions from multiple SMS notifications
- **Promotional Message Filtering**: Automatically filters out non-transaction promotional messages
- **Real-time Analytics**: Visual insights with charts and spending analytics using live transaction data
- **Confidence-based Filtering**: Only processes high-confidence transactions (70%+ accuracy)

## Tech Stack

- **Frontend**: Flutter (Cross-platform mobile app)
- **Backend**: Python FastAPI with Gemini AI integration
- **Database**: SQLite with SQLAlchemy ORM
- **AI/ML**: Google Gemini AI, scikit-learn for ML categorization
- **SMS Processing**: Advanced regex patterns + AI-powered parsing
- **Analytics**: Real-time transaction analysis and insights

## Project Structure

```
final_year/
├── mobile_app/          # Flutter mobile application
│   ├── lib/
│   │   ├── models/      # Data models (Transaction, etc.)
│   │   ├── providers/   # State management
│   │   ├── screens/     # UI screens
│   │   ├── services/    # API services
│   │   └── widgets/     # Reusable UI components
├── backend/             # Python FastAPI server
│   ├── main.py          # FastAPI application
│   ├── database.py      # Database models and operations
│   ├── gemini_integration.py  # Gemini AI SMS parsing
│   ├── transaction_deduplicator.py  # Duplicate detection
│   ├── sms_parser.py    # Regex-based SMS parsing (fallback)
│   └── requirements.txt # Python dependencies
└── README.md
```

## Complete Setup Instructions

### Prerequisites

- **Flutter SDK** (latest stable version)
- **Python 3.8+**
- **Git**
- **Gemini API Key** (already configured: `AIzaSyCzL3_QfDj9PKBGGoycG8KqQWiuOEqnAnE`)

### Step-by-Step Setup

#### 1. Clone and Navigate
```bash
git clone <repository-url>
cd final_year
```

#### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend will be available at:** `http://localhost:8000`

#### 3. Mobile App Setup
```bash
# Navigate to mobile app directory (from project root)
cd mobile_app

# Get Flutter dependencies
flutter pub get

# Generate model files
flutter packages pub run build_runner build

# Run on physical device (recommended) or emulator
flutter run
```

#### 4. Network Configuration

**For Physical Device Testing:**
- Ensure your computer and phone are on the same WiFi network
- Update `baseUrl` in `lib/services/api_service.dart` with your computer's IP address
- Current configuration: `http://192.168.0.102:8000`

**For Windows Firewall (if needed):**
```cmd
# Run as Administrator
netsh advfirewall firewall add rule name="Python Backend" dir=in action=allow protocol=TCP localport=8000
```

### Running the Complete System

1. **Start Backend Server:**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Mobile App:**
   ```bash
   cd mobile_app
   flutter run
   ```

3. **Test SMS Parsing:**
   ```bash
   # Test with real transaction SMS
   curl -X POST "http://localhost:8000/v1/parse-sms" \
   -H "Content-Type: application/json" \
   -d '{"sms_text":"HDFC Bank: Rs.1,250.50 debited from A/c **1234 at AMAZON PAY INDIA on 15-09-2024"}'
   ```

## Features Implemented

- [x] **Phase 1**: SMS Data Capture & Gemini AI Parsing
- [x] **Phase 2**: Database & Transaction History with SQLAlchemy
- [x] **Phase 3**: AI Smart Categorization with Gemini AI
- [x] **Phase 4**: UI/UX & Real-time Data Visualization
- [x] **Phase 5**: Duplicate Detection & Promotional Message Filtering
- [x] **Phase 6**: Confidence-based Transaction Validation

## API Endpoints

- `GET /health` - Health check
- `POST /v1/parse-sms` - Parse SMS transaction with Gemini AI
- `GET /v1/transactions` - Get all transactions
- `GET /v1/analytics/*` - Various analytics endpoints

## Key Components

### Gemini AI Integration
- **File**: `backend/gemini_integration.py`
- **Purpose**: Intelligent SMS parsing and transaction validation
- **Features**: Promotional message filtering, confidence scoring

### Duplicate Detection
- **File**: `backend/transaction_deduplicator.py`
- **Purpose**: Prevent duplicate transactions from multiple SMS
- **Methods**: Transaction ID matching, hash-based detection, similarity analysis

### Mobile App Architecture
- **State Management**: Provider pattern
- **API Communication**: HTTP service with offline fallback
- **UI**: Material Design with custom widgets

## Contributors

Built as a final year project for AI-powered financial management.
