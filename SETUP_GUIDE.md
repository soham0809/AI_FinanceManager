# Complete Setup Guide - AI Financial Co-Pilot

## 🚀 Quick Start Guide

### Prerequisites
1. **Python 3.8+** installed
2. **Flutter SDK** installed
3. **Ollama** installed with `llama3.1:latest` model
4. **Android Studio** or **VS Code** with Flutter extension

---

## 📱 **Step 1: Start Ollama (Required)**
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, verify model is available
ollama list
# Should show: llama3.1:latest
```

---

## 🖥️ **Step 2: Start Backend Server**

### Option A: Using Batch File (Recommended)
```bash
# Navigate to project directory
cd c:\Users\soham\Desktop\BASIC_CODES\final_year

# Run the startup script
start_backend.bat
```

### Option B: Manual Start
```bash
cd c:\Users\soham\Desktop\BASIC_CODES\final_year\backend

# Activate virtual environment
venv\Scripts\activate

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:**
- Local: `http://localhost:8000`
- Network: `http://YOUR_IP:8000` (for mobile devices)
- API Docs: `http://localhost:8000/docs`

---

## 🔍 **Step 3: Get Your IP Address**

### Find Your Computer's IP for Mobile Connection
```bash
# Run the IP detection script
python get_ip_address.py
```

This will show:
- Your local IP address (e.g., `192.168.1.100`)
- Connection test results
- Configuration instructions for different devices

---

## 📱 **Step 4: Configure Mobile App**

### Update API Service Configuration
Edit: `mobile_app/lib/services/api_service.dart`

```dart
static String get baseUrl {
  if (Platform.isAndroid) {
    // For Android Emulator: use 'http://10.0.2.2:8000'
    // For Physical Android Device: use your computer's IP
    return 'http://YOUR_COMPUTER_IP:8000';  // Replace with actual IP
  } else if (Platform.isIOS) {
    // For iOS Simulator
    return 'http://localhost:8000';
  } else {
    return 'http://localhost:8000';
  }
}
```

### Device-Specific URLs:
- **Android Emulator**: `http://10.0.2.2:8000`
- **Physical Android Device**: `http://192.168.1.100:8000` (your actual IP)
- **iOS Simulator**: `http://localhost:8000`
- **Physical iPhone**: `http://192.168.1.100:8000` (your actual IP)

---

## 📱 **Step 5: Start Mobile App**

### Using Android Studio/VS Code
1. Open `mobile_app` folder in your IDE
2. Select your device/emulator
3. Run the app (`F5` or Run button)

### Using Command Line
```bash
cd mobile_app

# Get dependencies
flutter pub get

# Run on connected device/emulator
flutter run

# Or run on specific device
flutter devices  # List available devices
flutter run -d DEVICE_ID
```

---

## 🧪 **Step 6: Test the Connection**

### Backend Health Check
Visit: `http://localhost:8000/health`
Should return:
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "app": "AI Financial Co-Pilot",
  "version": "1.0.0"
}
```

### Mobile App Connection Test
1. Open the mobile app
2. Check console logs for connection attempts
3. Look for messages like:
   - `🔍 Attempting to connect to: http://YOUR_IP:8000/health`
   - `✅ Health check successful`

---

## 🔧 **Step 7: Run Batch Processing (Optional)**

### Process Existing Transactions with Ollama
```bash
# Interactive batch processing
python run_batch_processing.py

# Or use API endpoints
curl -X POST "http://localhost:8000/v1/batch/process-transactions" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "batch_size": 3}'
```

---

## 🛠️ **Troubleshooting**

### Backend Issues
1. **Port 8000 already in use**:
   ```bash
   # Kill process using port 8000
   netstat -ano | findstr :8000
   taskkill /PID <PID_NUMBER> /F
   ```

2. **Virtual environment not found**:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Mobile App Issues
1. **Connection refused**:
   - Verify backend is running
   - Check IP address in `api_service.dart`
   - Ensure firewall allows port 8000

2. **Android Emulator can't connect**:
   - Use `http://10.0.2.2:8000` for emulator
   - Use your computer's IP for physical device

3. **iOS Simulator issues**:
   - Use `http://localhost:8000`
   - Check iOS simulator network settings

### Ollama Issues
1. **Model not found**:
   ```bash
   ollama pull llama3.1:latest
   ```

2. **Ollama not responding**:
   ```bash
   # Restart Ollama
   ollama serve
   ```

---

## 📊 **Available Features**

### Backend API Endpoints
- **Health**: `GET /health`
- **SMS Parsing**: `POST /v1/parse-sms`
- **Transactions**: `GET/POST /v1/transactions`
- **Analytics**: `GET /v1/analytics/*`
- **Batch Processing**: `POST /v1/batch/process-transactions`
- **API Documentation**: `GET /docs`

### Mobile App Features
- SMS transaction parsing
- Transaction history
- Analytics and charts
- Category management
- Spending insights

---

## 🎯 **Next Steps**

1. **Test SMS Parsing**: Send a bank SMS to the mobile app
2. **Run Batch Processing**: Process existing transactions with Ollama
3. **Explore Analytics**: View spending insights and charts
4. **Customize Categories**: Add/modify transaction categories

---

## 📞 **Support**

If you encounter issues:
1. Check console logs in both backend and mobile app
2. Verify network connectivity
3. Ensure all services (Ollama, Backend) are running
4. Check firewall settings for port 8000
