# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**AI Finance Manager** - An AI-powered financial assistant that automatically parses SMS transactions, provides analytics, and enables natural language queries about spending patterns.

**Stack:**
- Backend: FastAPI + SQLAlchemy + Ollama (LLM)
- Mobile: Flutter
- Database: SQLite
- Infrastructure: Cloudflare Tunnel for global access

## Essential Commands

### Starting the System

**One-click startup (all services):**
```powershell
.\START_ALL.ps1
```

**Start backend only:**
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Start Cloudflare Tunnel:**
```powershell
C:\cloudflared\cloudflared.exe tunnel run ai-finance
```

**Start Ollama (LLM service):**
```powershell
ollama serve
```

### Mobile App

**Run on device/emulator:**
```powershell
cd mobile_app
flutter run
```

**Build production APK:**
```powershell
cd mobile_app
flutter build apk --release
```

### Testing & Development

**Run all tests:**
```powershell
python test_complete_flow.py
```

**Test authentication:**
```powershell
python test_auth.py
```

**Test chatbot:**
```powershell
python test_chatbot.py
```

**Test SMS parsing:**
```powershell
cd backend
python test_parse.py
```

**Access API docs:**
- Local: http://localhost:8000/docs
- Production: https://ai-finance.sohamm.xyz/docs

## Architecture

### Backend Structure (FastAPI)

The backend follows a modular MVC-like architecture:

```
backend/app/
├── main.py                    # FastAPI app entry point, router registration
├── config/
│   ├── settings.py            # Central configuration (env vars, CORS, URLs)
│   └── database.py            # SQLAlchemy engine and session management
├── models/
│   ├── user.py                # User model with JWT authentication
│   └── transaction.py         # Transaction model with enhanced fields
├── controllers/
│   ├── auth_controller.py     # Authentication business logic
│   ├── transaction_controller.py  # Transaction processing & creation
│   └── chatbot_controller.py # Natural language query processing
├── routes/
│   ├── auth_routes.py         # /auth endpoints (login, register, refresh)
│   ├── transaction_routes.py # /v1/transactions endpoints
│   ├── analytics_routes.py    # /v1/analytics endpoints
│   ├── chatbot_routes.py      # /v1/chatbot endpoints
│   ├── batch_routes.py        # Batch SMS processing
│   └── enhanced_*.py          # Enhanced versions with more features
└── utils/
    ├── sms_parser.py          # Rule-based SMS parsing (fast, local)
    ├── ollama_integration.py  # LLM-based parsing (intelligent, slower)
    ├── transaction_deduplicator.py  # Prevents duplicate SMS processing
    ├── intelligent_sms_filter.py    # Filters promotional/non-transaction SMS
    └── spending_analytics.py  # Analytics calculations
```

### Key Architectural Patterns

**Dual SMS Parsing Strategy:**
- Primary: Rule-based NLP parser (`sms_parser.py`) - fast, offline
- Fallback: Ollama LLM parser (`ollama_integration.py`) - intelligent, requires Ollama

**User Isolation:**
- All queries filtered by `user_id`
- Duplicate detection scoped per user
- JWT authentication on all protected endpoints

**Transaction Model:**
- Amounts always stored as **positive** values
- `transaction_type` field distinguishes 'debit' vs 'credit'
- `date` stored as DateTime (not TEXT)
- Enhanced fields: `payment_method`, `is_subscription`, `upi_transaction_id`, etc.

**Deduplication:**
- Checks `sms_text` hash per user
- Prevents same SMS from being processed twice
- Uses `transaction_deduplicator.py`

### Mobile App Structure (Flutter)

```
mobile_app/lib/
├── main.dart                  # App entry point
├── config/
│   └── network_config.dart    # Cloudflare/local mode switching
├── models/
│   └── transaction.dart       # Transaction data model
├── providers/
│   └── transaction_provider.dart  # State management (Provider pattern)
├── services/
│   ├── api_service.dart       # HTTP client wrapper
│   ├── auth_service.dart      # JWT token management
│   ├── sms_service.dart       # Android SMS reading
│   └── sms_filter_service.dart # Client-side SMS filtering
├── screens/
│   ├── auth/                  # Login & registration
│   ├── home_screen.dart       # Dashboard with quick actions
│   ├── analytics_screen.dart  # Charts and insights
│   ├── chatbot_screen.dart    # Natural language queries
│   └── main_navigation.dart   # Bottom nav bar
└── widgets/
    ├── auto_sms_scanner.dart  # Background SMS monitoring
    ├── enhanced_analytics_dashboard.dart  # Spending visualizations
    └── transaction_list.dart  # Transaction display
```

## Important Implementation Details

### Database Schema

**Transaction Table Critical Fields:**
- `amount`: Float (always positive)
- `transaction_type`: VARCHAR(50) - 'debit' or 'credit' (default: 'debit')
- `date`: DateTime (not TEXT)
- `sms_text`: Text - used for duplicate detection
- `user_id`: Integer (FK to users.id) - for user isolation

**Never assume:**
- Negative amounts mean debits (amounts are always positive)
- Date is stored as TEXT (it's DateTime)

### Network Configuration

**Cloudflare Tunnel:**
- Production URL: https://ai-finance.sohamm.xyz
- Configured in `mobile_app/lib/config/network_config.dart`
- Set `useCloudflare = true` for production, `false` for local development

**Backend Ports:**
- Default: 8000
- Cloudflare: 8001 (sometimes used)

### Environment Variables

Backend requires `.env` file in `backend/` directory with:
```
JWT_SECRET_KEY=<your-secret-key>
DATABASE_URL=sqlite:///./financial_copilot.db
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:latest
```

Copy from `.env.example` and customize.

### Common Pitfalls

**SMS Parsing:**
- Always use both parsers (NLP first, LLM fallback)
- Filter promotional messages before parsing
- Check `is_transaction` flag from LLM response

**Analytics Queries:**
- Filter by `transaction_type` field, NOT amount sign
- Use `strftime()` for date extraction (SQLite compatible)
- All queries must filter by `user_id` for isolation

**Transaction Creation:**
- Extract `transaction_type` from parsed data
- Convert date strings to DateTime objects
- Use `abs(amount)` to ensure positive values

## Dependencies

### Backend
Install from `backend/requirements.txt`:
- fastapi==0.104.1
- uvicorn==0.24.0
- sqlalchemy==2.0.23
- python-jose (JWT)
- passlib (password hashing)
- requests (Ollama API calls)

### Mobile
Install via Flutter:
```powershell
cd mobile_app
flutter pub get
```

Key packages: http, provider, fl_chart, permission_handler, shared_preferences

## Testing Credentials

```
Username: testuser
Password: testpass123
```

## Database Management

**Reset database (fresh start):**
```python
from app.config.database import engine, Base
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
```

**Verify schema:**
```powershell
cd backend
python verify_schema.py
```

## Production Workflow

1. Start Ollama: `ollama serve`
2. Start Backend: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001`
3. Start Cloudflare Tunnel: `C:\cloudflared\cloudflared.exe tunnel run ai-finance`
4. App is live at: https://ai-finance.sohamm.xyz

## Key Files to Read First

When working on specific features, start with:
- **SMS Parsing:** `backend/app/utils/sms_parser.py` and `ollama_integration.py`
- **Authentication:** `backend/app/auth/security.py` and `auth_controller.py`
- **Analytics:** `backend/app/routes/analytics_routes.py`
- **Chatbot:** `backend/app/controllers/chatbot_controller.py`
- **Transaction Model:** `backend/app/models/transaction.py`

## Code Patterns to Follow

**Controller Pattern:**
- Controllers contain business logic
- Routes handle HTTP request/response
- Models define database schema
- Utils provide reusable functionality

**Error Handling:**
- Return structured JSON with `success: bool` field
- Include descriptive error messages
- Log errors to console (print statements are acceptable)

**User Context:**
- Always retrieve `user_id` from JWT token via `get_current_user` dependency
- Never trust client-provided user_id in request body
- Filter all database queries by user_id

## Windows-Specific Notes

- Use PowerShell (not bash) for scripts
- Cloudflared.exe location: `C:\cloudflared\`
- Backslashes in paths (or double backslashes in strings)
- Use `python` (not `python3`)
