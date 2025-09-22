# Mobile App Connection Troubleshooting Guide

## Current Status
- ✅ Backend running on: `http://localhost:8000` and `http://192.168.0.105:8000`
- ✅ All API endpoints working correctly
- ⚠️ Mobile app showing "server disconnected"

## Connection Configuration by Device Type

### 1. Android Emulator (Most Common)
**Use**: `http://10.0.2.2:8000`

In `mobile_app/lib/services/api_service.dart`, line 22:
```dart
return 'http://10.0.2.2:8000';  // ✅ Current setting
```

### 2. Physical Android Device
**Use**: `http://192.168.0.105:8000`

Change line 22 to:
```dart
return 'http://192.168.0.105:8000';  // Your computer's IP
```

### 3. iOS Simulator
**Use**: `http://localhost:8000`
```dart
return 'http://localhost:8000';  // ✅ Current setting for iOS
```

## Troubleshooting Steps

### Step 1: Identify Your Setup
Run this command to check:
```bash
flutter devices
```

Look for:
- `Android SDK built for x86_64 (emulator)` → Use `10.0.2.2:8000`
- `Your Phone Name (mobile)` → Use `192.168.0.105:8000`
- `iPhone Simulator` → Use `localhost:8000`

### Step 2: Update Configuration
Based on your device type, update the IP address in:
`mobile_app/lib/services/api_service.dart` line 22

### Step 3: Restart Everything
```bash
# Stop the mobile app
# Then restart with:
flutter run

# Or hot restart:
# Press 'R' in the terminal where flutter run is running
```

### Step 4: Check Console Logs
Look for these debug messages in your Flutter console:
```
🔍 Attempting to connect to: http://10.0.2.2:8000/health
🔍 Platform: android
✅ Health check successful
```

If you see connection errors, the logs will show which alternative URLs are being tried.

## Quick Test Commands

### Test Backend Accessibility
```bash
# Test localhost (should work)
curl http://localhost:8000/health

# Test your IP (should work)
curl http://192.168.0.105:8000/health

# Test emulator IP (will only work from Android emulator)
curl http://10.0.2.2:8000/health
```

## Common Issues & Solutions

### Issue 1: "Connection Refused"
**Solution**: Make sure backend is running
```bash
cd c:\Users\soham\Desktop\final_year
.\start_backend.bat
```

### Issue 2: "Network Unreachable" on Physical Device
**Solutions**:
1. Ensure phone and computer are on same WiFi network
2. Update IP address to `192.168.0.105:8000`
3. Check Windows Firewall settings

### Issue 3: Emulator Can't Connect
**Solutions**:
1. Use `10.0.2.2:8000` (not localhost)
2. Restart emulator
3. Check if emulator has internet access

### Issue 4: iOS Simulator Issues
**Solutions**:
1. Use `localhost:8000`
2. Try `127.0.0.1:8000`
3. Restart simulator

## Debug Mode

The app now includes automatic URL testing. Check your Flutter console for:
```
🔍 Attempting to connect to: [URL]
🔍 Platform: [platform]
🔍 Trying alternative URLs...
✅ Alternative URL works: [working_url]
```

## Current Backend Status
- Server: ✅ Running
- Health endpoint: ✅ Working
- SMS parsing: ✅ Working  
- Analytics: ✅ Working
- Database: ✅ 39 transactions available

## Next Steps
1. Identify your device type (emulator vs physical)
2. Update the IP address accordingly
3. Restart the mobile app
4. Check console logs for connection status
5. If still failing, try the alternative IP addresses shown in logs

---
**Your Computer's IP**: `192.168.0.105`
**Backend URLs**: 
- Local: `http://localhost:8000`
- Network: `http://192.168.0.105:8000`
- Emulator: `http://10.0.2.2:8000`
