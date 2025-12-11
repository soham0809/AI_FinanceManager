# 🚀 Financial Copilot - Complete Setup Guide

## System Architecture
```
Mobile App (Flutter) → Cloudflare Tunnel → Backend (FastAPI) → Ollama LLM
                    ↓
            https://ai-finance.sohamm.xyz
```

## 🎯 Quick Start (Windows)

### One-Click Start
```powershell
# Run this single command to start everything:
.\START_ALL.ps1
```

This will start:
1. **Ollama** - LLM service for transaction parsing
2. **FastAPI Backend** - Main API server on port 8000
3. **Cloudflare Tunnel** - Secure remote access

## 📱 Mobile App

### Run on Device/Emulator
```bash
cd mobile_app
flutter run
```

### Build APK
```bash
flutter build apk --release
```

## 🔧 Manual Start (if needed)

### 1. Start Ollama
```powershell
ollama serve
```

### 2. Start Backend
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start Cloudflare Tunnel
```powershell
C:\cloudflared\cloudflared.exe tunnel run ai-finance
```

## 🌐 Access Points

- **Mobile App URL**: `https://ai-finance.sohamm.xyz`
- **Local Backend**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `https://ai-finance.sohamm.xyz/health`

## ✅ Features Working

1. **User Isolation**: Each user sees only their own transactions
2. **Duplicate Prevention**: SMS texts are processed only once per user
3. **Dual Parsing**: 
   - NLP (local, fast)
   - LLM (Ollama, intelligent)
4. **Secure Access**: All traffic through Cloudflare tunnel
5. **Batch Processing**: Process multiple SMS at once

## 🔍 Troubleshooting

### Network Errors
- **Issue**: "Connection refused" or timeout errors
- **Solution**: Ensure all services are running (check START_ALL.ps1 output)

### Ollama Errors
- **Issue**: "Max retries exceeded"
- **Solution**: Make sure Ollama is running (`ollama serve`)

### Cloudflare Tunnel Issues
- **Issue**: "Failed to dial edge"
- **Solution**: 
  1. Check internet connection
  2. Restart tunnel: `C:\cloudflared\cloudflared.exe tunnel run ai-finance`

### Database Issues
- **Issue**: Validation errors (vendor=None)
- **Solution**: Already fixed - backend now handles null values

### Mobile App Graphics Warnings
- **Issue**: BLASTBufferQueue or mali_gralloc errors
- **Solution**: These are Android graphics warnings, not actual errors - safe to ignore

## 🔐 Test Credentials

```
Username: testuser
Password: testpass123
```

## 📊 Database Management

### View Transactions
```python
# Run from backend directory
python
>>> import sqlite3
>>> conn = sqlite3.connect('financial_copilot.db')
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT COUNT(*) FROM transactions")
>>> print(f"Total transactions: {cursor.fetchone()[0]}")
```

### Clean Duplicates
```powershell
cd backend
python clean_duplicates.py
```

### Test User Isolation
```powershell
cd backend
python test_user_isolation.py
```

## 🛑 Stopping Services

Close each PowerShell window or press `Ctrl+C` in each window.

## 📝 Important Notes

1. **Always use Cloudflare URL** - The app no longer falls back to localhost
2. **User data is isolated** - No cross-user data leakage
3. **Duplicates are prevented** - Database-level checks ensure no duplicate SMS processing
4. **Backend auto-reloads** - Code changes are applied automatically

## 🆘 Support

If issues persist:
1. Check all service windows for error messages
2. Verify Cloudflare tunnel status
3. Test backend directly: http://localhost:8000/docs
4. Check mobile app logs in Flutter console

---
**Last Updated**: Network errors fixed, always uses Cloudflare URL, duplicate detection restored
