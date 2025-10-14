# AI Financial Co-Pilot

A comprehensive financial management application with AI-powered SMS transaction parsing using local Ollama LLM, expense tracking, and intelligent financial insights.

## Features

### Core Features
- **AI-Powered SMS Parsing**: Automatically extract transaction details from bank SMS messages using local Ollama LLM
- **Smart Transaction Categorization**: Intelligent categorization of expenses and income
- **Real-time Analytics**: Comprehensive financial analytics and insights
- **Expense Tracking**: Track and manage personal and group expenses
- **Duplicate Detection**: Advanced duplicate transaction detection and prevention
- **Local AI Processing**: Privacy-focused local LLM processing with Ollama

### Advanced Features
- **Group Expense Management**: Split bills and manage shared expenses
- **Predictive Analytics**: ML-powered spending predictions and trends
- **Financial Health Score**: Comprehensive financial wellness assessment
- **Multi-platform Support**: Web dashboard and mobile app
- **Secure Authentication**: JWT-based secure user authentication

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping
- **SQLite**: Lightweight database for development
- **Ollama**: Local LLM for intelligent SMS parsing (llama3.1:latest)
- **Scikit-learn**: Machine learning for categorization and predictions
- **Pandas**: Data manipulation and analysis

### Frontend (Mobile App)
- **Flutter**: Cross-platform mobile development framework
- **Dart**: Programming language for Flutter
- **HTTP Package**: For API communication

## Installation & Setup

### Prerequisites
- Python 3.8+
- Flutter SDK (for mobile app)
- Ollama with llama3.1:latest model

### Ollama Setup
1. Install Ollama from [https://ollama.ai](https://ollama.ai)
2. Pull the required model: `ollama pull llama3.1:latest`
3. Start Ollama: `ollama serve`

### Backend Setup
1. Clone the repository
2. Navigate to backend directory
3. Create virtual environment: `python -m venv venv`
4. Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
5. Install dependencies: `pip install -r requirements.txt`
6. Run the server: `python -m uvicorn app.main:app --reload`

### Mobile App Setup
1. Navigate to mobile_app directory
2. Install dependencies: `flutter pub get`
3. Run the app: `flutter run`

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints
- `POST /v1/parse-sms`: Parse SMS transaction using Ollama AI
- `GET /v1/transactions`: Get user transactions
- `POST /v1/transactions`: Create new transaction
- `GET /v1/analytics/summary`: Get financial summary
- `POST /v1/auth/register`: User registration
- `POST /v1/auth/login`: User login

## Testing

Test the Ollama integration:
```bash
python test_ollama_integration.py
python test_database_data.py
```

## Configuration

### Environment Variables
- `OLLAMA_HOST`: Ollama server URL (default: http://localhost:11434)
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: Database connection string

### Settings
Configure settings in `backend/app/config/settings.py`

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── config/          # Configuration files
│   │   ├── controllers/     # Business logic
│   │   ├── models/          # Database models
│   │   ├── routes/          # API routes
│   │   ├── utils/           # Utility functions (including Ollama integration)
│   │   └── main.py          # FastAPI application
│   └── requirements.txt
├── mobile_app/              # Flutter mobile application
├── test_ollama_integration.py
├── test_database_data.py
└── README.md
```

## Usage Example

```bash
# Test SMS parsing
curl -X POST "http://localhost:8000/v1/parse-sms" \
  -H "Content-Type: application/json" \
  -d '{"sms_text":"HDFC Bank: Rs.1,250.50 debited from A/c **1234 at AMAZON PAY INDIA on 15-09-2024"}'
```

## License

This project is licensed under the MIT License.
