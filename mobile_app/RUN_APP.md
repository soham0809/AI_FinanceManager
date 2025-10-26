# 📱 Mobile App Startup Guide

## Prerequisites
1. Backend services must be running (use `START_ALL.ps1` in parent directory)
2. Flutter SDK installed
3. Android device/emulator connected

## Quick Start

### 1. Start Backend Services
```powershell
# From the parent directory (final_year/)
.\START_ALL.ps1
```

### 2. Run Mobile App
```bash
# From this directory (mobile_app/)
flutter run
```

## Network Configuration

The app is configured to use **Cloudflare URL only**:
- **Production URL**: `https://ai-finance.sohamm.xyz`
- **No localhost fallback** - ensures consistent behavior

## Troubleshooting

### App Can't Connect to Backend
1. Check if Cloudflare tunnel is running (green status in tunnel window)
2. Verify backend is running on port 8000
3. Test the URL in browser: https://ai-finance.sohamm.xyz/health

### Graphics/Buffer Errors
The `BLASTBufferQueue` and `mali_gralloc` errors are Android graphics warnings that don't affect functionality. They occur during:
- Heavy UI updates (batch processing)
- Screen transitions
- These are cosmetic warnings, not actual errors

### Authentication Issues
1. Login with test credentials:
   - Username: `testuser`
   - Password: `testpass123`
2. Or register a new account

## Build APK
```bash
# Build release APK
flutter build apk --release

# APK location: build/app/outputs/flutter-apk/app-release.apk
```

## Important Notes
- ✅ User isolation is enforced - each user sees only their data
- ✅ Duplicate detection prevents same SMS from being processed twice
- ✅ All network traffic goes through secure Cloudflare tunnel
- ❌ Never commit sensitive data or API keys
