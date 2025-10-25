# 🚀 AI Finance Manager - Startup Guide

## Database Status
✅ **Your database is SAFE!** 
- Found existing data in `backend/financial_copilot.db` (98KB)
- Contains your previously parsed messages from 40 minutes of work
- **NO database reset will occur** - all your data is preserved

## Quick Start Commands (In Order)

### 1. Start Ollama Server
```bash
ollama serve
```
*Keep this terminal open*

### 2. Start Backend Server
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Keep this terminal open*

### 3. Start Cloudflare Tunnel
```bash
C:\cloudflared\cloudflared.exe tunnel run ai-finance
```
*Keep this terminal open*

### 4. Start Flutter App
```bash
cd mobile_app
flutter run
```

## Alternative: Use Automated Script
```bash
# This will NOT reset your database anymore
python start_app.py
```

## New Features Added

### 🚀 NLP Quick Parse (Fast)
- Uses regex-based local parsing
- No AI/LLM required
- Very fast processing
- Good for bulk SMS processing

### 🤖 LLM Detailed Parse (Accurate)  
- Uses Ollama AI for detailed analysis
- More accurate categorization
- Slower but more intelligent
- Better for complex transactions

## API Endpoints

### Local/Fast Parsing
- `POST /v1/parse-sms-local-public` - Single SMS (no auth)
- `POST /v1/quick/parse-sms-batch-local` - Batch SMS (auth required)

### LLM/Detailed Parsing  
- `POST /v1/parse-sms-public` - Single SMS (no auth)
- `POST /v1/quick/parse-sms-batch` - Batch SMS (auth required)

## Flutter UI Changes
- **SMS Test Card**: Choose between "🚀 NLP Quick Parse (Fast)" or "🤖 LLM Detailed Parse (Accurate)"
- **Auto SMS Scanner**: Batch mode selection with descriptions
- Both preserve your existing parsing logic

## Database Protection
- `start_app.py` now preserves your database by default
- To force reset (if needed): `RESET_DB=1 python start_app.py` or `python start_app.py --reset-db`
- Your 40 minutes of parsed data is completely safe

## Troubleshooting
- If backend fails to start, check if port 8000 is free
- If Ollama fails, ensure it's installed from https://ollama.ai
- If Flutter fails, ensure device/emulator is connected
- Check `test_cloudflare.py` to verify tunnel connectivity
