# 🚀 AI Finance Manager

## One-Click Startup

Run this single command to start everything:

```bash
python start_app.py
```

## What This App Does

🤖 **AI Financial Assistant**: Ask questions like "How much did I spend on food delivery?"
📱 **Smart SMS Parsing**: Automatically categorizes UPI, Credit Card, and Subscription transactions
📊 **Rich Analytics**: Visual insights with payment method indicators
💬 **Natural Language Queries**: Chat with your financial data

## Features

- ✅ **Automatic IP Configuration**: Works on any network
- ✅ **Fresh Database**: Resets database on each startup
- ✅ **Ollama Integration**: Local AI processing for privacy
- ✅ **Flutter Mobile App**: Modern, responsive UI
- ✅ **FastAPI Backend**: High-performance API server

## Requirements

- Python 3.8+
- Flutter SDK
- Ollama (for AI features)
- Android/iOS device or emulator

## Quick Start

1. **Install Ollama**: Download from https://ollama.ai
2. **Run the app**: `python start_app.py`
3. **Test features**: Use the mobile app to parse SMS and chat with AI

## API Endpoints

- Health: `/health`
- SMS Parsing: `/v1/parse-sms-public`
- Chatbot: `/v1/chatbot/query-public`
- Transactions: `/v1/transactions-public`
- Analytics: `/v1/analytics/*-public`

## Architecture

```
AI Finance Manager/
├── backend/           # FastAPI server
├── mobile_app/        # Flutter mobile app
└── start_app.py      # One-click startup script
```

## Support

If you encounter issues:
1. Ensure Ollama is installed and running
2. Check that your device is connected for Flutter
3. Verify network connectivity
4. Check console output for specific errors

**Built with ❤️ for intelligent financial management**
