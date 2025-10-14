@echo off
echo Starting AI Financial Co-Pilot Mobile App...
echo.

cd mobile_app

echo Getting Flutter dependencies...
flutter pub get

echo.
echo Available devices:
flutter devices

echo.
echo Starting Flutter app...
echo Note: Make sure your device/emulator is connected
echo.

flutter run
