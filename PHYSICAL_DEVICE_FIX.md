# Physical Android Device Connection Fix

## Current Issue
- Physical Android device showing: "network error client exception with socket Exception connection refused OS.error connection refused address 192.168.0.102:8000"
- Backend is running correctly on `192.168.0.105:8000`

## ✅ Fixes Applied

### 1. Updated API Service Configuration
Changed `mobile_app/lib/services/api_service.dart` to use correct IP:
```dart
return 'http://192.168.0.105:8000';  // Your computer's correct IP
```

### 2. Added Fallback URLs
The app will now try multiple URLs if the primary fails:
- `http://192.168.0.105:8000` (correct IP)
- `http://192.168.0.102:8000` (old IP as fallback)
- Other alternatives

## 🔧 Steps to Fix Connection

### Step 1: Ensure Backend is Running
```bash
cd c:\Users\soham\Desktop\final_year
.\start_backend.bat
```

### Step 2: Verify Backend Accessibility
Backend is confirmed working on:
- ✅ `http://localhost:8000`
- ✅ `http://192.168.0.105:8000`

### Step 3: Clear App Cache & Restart
1. **Stop the Flutter app completely**
2. **Clear build cache**:
   ```bash
   cd mobile_app
   flutter clean
   flutter pub get
   ```
3. **Restart the app**:
   ```bash
   flutter run
   ```

### Step 4: Check Windows Firewall (If Still Failing)
If connection still fails, temporarily disable Windows Firewall:
1. Open Windows Security
2. Go to Firewall & network protection
3. Temporarily turn off firewall for Private networks
4. Test the app
5. Re-enable firewall after testing

### Step 5: Alternative - Add Firewall Rule
Instead of disabling firewall, add a rule:
```cmd
# Run as Administrator
netsh advfirewall firewall add rule name="Flutter Backend" dir=in action=allow protocol=TCP localport=8000
```

## 🔍 Debugging Steps

### Check Console Logs
After restarting the app, look for these messages in Flutter console:
```
🔍 Attempting to connect to: http://192.168.0.105:8000/health
🔍 Platform: android
✅ Health check successful
```

If it fails, you'll see:
```
❌ Network error in healthCheck: [error]
🔍 Trying alternative URLs...
🔍 Trying: http://192.168.0.102:8000/health
✅ Alternative URL works: http://192.168.0.105:8000
```

### Manual Network Test
From your phone's browser, try accessing:
`http://192.168.0.105:8000/health`

You should see:
```json
{"status":"healthy","message":"All systems operational","timestamp":"..."}
```

## 🚨 Common Issues & Solutions

### Issue 1: Still Getting 192.168.0.102
**Cause**: App cache or old configuration
**Solution**: 
```bash
flutter clean
flutter pub get
flutter run
```

### Issue 2: Connection Timeout
**Cause**: Windows Firewall blocking
**Solution**: Add firewall rule or temporarily disable

### Issue 3: Wrong Network
**Cause**: Phone and computer on different networks
**Solution**: Ensure both are on same WiFi network

### Issue 4: IP Address Changed
**Cause**: Router assigned new IP to computer
**Solution**: Check current IP and update:
```bash
python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print('Current IP:', s.getsockname()[0]); s.close()"
```

## 📱 Expected Behavior After Fix

1. **App starts** → Shows connection attempt in console
2. **Health check succeeds** → "✅ Health check successful"
3. **Dashboard loads** → Shows real transaction data
4. **Analytics work** → Real-time updates when parsing SMS

## 🔧 Quick Test

After making changes, test immediately:
1. Open the app
2. Check console for connection messages
3. Try parsing an SMS message
4. Verify analytics dashboard updates

## Current Configuration Summary
- **Computer IP**: `192.168.0.105`
- **Backend URL**: `http://192.168.0.105:8000`
- **Mobile App Config**: Updated to use correct IP
- **Firewall**: May need rule for port 8000
- **Network**: Both devices must be on same WiFi

---
**Status**: Configuration updated, restart app to apply changes
**Next**: Clear cache, restart app, check console logs
