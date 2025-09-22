# 📱 Physical Device Setup Guide

## Required Changes for Physical Device Testing

### 1. **Enable Developer Options & USB Debugging**
```bash
# On your Android device:
1. Go to Settings > About Phone
2. Tap "Build Number" 7 times to enable Developer Options
3. Go to Settings > Developer Options
4. Enable "USB Debugging"
5. Enable "Install via USB" (if available)
```

### 2. **Connect Device & Verify**
```bash
# Connect device via USB and run:
flutter devices

# Should show your device listed
# If not, install ADB drivers for your device
```

### 3. **Network Configuration**
- **Current API URL**: `http://192.168.0.103:8000`
- **Your computer's IP**: `192.168.0.103` (Wi-Fi)
- **Ensure both devices are on same Wi-Fi network**

### 4. **Firewall Settings** ⚠️ **CRITICAL FOR DEVICE TESTING**
```bash
# Method 1: Command Line (Run as Administrator)
netsh advfirewall firewall add rule name="Python HTTP Server" dir=in action=allow protocol=TCP localport=8000

# Method 2: Windows Security GUI
1. Windows Security > Firewall & network protection
2. Allow an app through firewall
3. Click "Change Settings" > "Allow another app"
4. Browse to Python.exe (usually C:\Users\soham\AppData\Local\Programs\Python\Python312\python.exe)
5. Check both "Private" and "Public" network boxes
6. Click "Add" and "OK"
```

**Current Network Configuration:**
- **Computer IP**: `192.168.0.103` (Wi-Fi)
- **Device**: `motorola edge 60 pro` (Connected)
- **Backend URL**: `http://192.168.0.103:8000`

### 5. **Backend Server Configuration**
```bash
# Start backend server (already configured):
cd C:\Users\soham\Desktop\final_year\backend
python main.py

# Server will run on: http://0.0.0.0:8000
# Accessible from device at: http://192.168.0.103:8000
```

### 6. **Build & Deploy to Device**
```bash
cd C:\Users\soham\Desktop\final_year\mobile_app

# Clean build
flutter clean
flutter pub get

# Build and install on connected device
flutter run

# Or build APK for manual installation
flutter build apk --release
# APK location: build/app/outputs/flutter-apk/app-release.apk
```

## Troubleshooting

### Network Issues
- **Connection timeout**: Verify both devices on same network
- **Firewall blocking**: Add Python to Windows Firewall exceptions
- **Wrong IP**: Update API_SERVICE.dart with correct computer IP

### Device Recognition
- **Device not found**: Install device-specific ADB drivers
- **Permission denied**: Enable USB debugging and authorize computer
- **Build fails**: Run `flutter doctor` to check setup

### App Crashes
- **Check logs**: `flutter logs` or `adb logcat`
- **Permission issues**: Grant SMS permissions manually in device settings
- **API errors**: Verify backend server is running and accessible

## Testing Checklist

- [ ] Device connected and recognized by Flutter
- [ ] Backend server running on computer
- [ ] Both devices on same Wi-Fi network
- [ ] Firewall configured to allow connections
- [ ] App builds and installs successfully
- [ ] API connectivity working (check health endpoint)
- [ ] SMS parsing functionality working with mock data
- [ ] Analytics screens loading without errors
