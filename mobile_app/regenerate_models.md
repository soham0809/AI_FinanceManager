# Regenerate Flutter Models

Since we updated the Transaction model with new fields, you need to regenerate the JSON serialization code.

## Steps to regenerate:

1. **Open terminal in the mobile_app directory**:
   ```bash
   cd mobile_app
   ```

2. **Run the build runner**:
   ```bash
   flutter packages pub run build_runner build --delete-conflicting-outputs
   ```

This will regenerate the `transaction.g.dart` file with the new fields we added to the Transaction model.

## Alternative if the above doesn't work:

If you encounter any issues, you can also try:

```bash
flutter packages pub get
flutter packages pub run build_runner build
```

## What this does:

- Updates the `_$TransactionFromJson` and `_$TransactionToJson` methods
- Ensures all new fields (paymentMethod, isSubscription, etc.) are properly serialized
- Maintains compatibility with the backend API responses

## After regeneration:

The app should be able to:
- Parse the enhanced transaction data from the backend
- Display payment method badges (UPI, Credit Card, etc.)
- Show subscription indicators
- Display enriched transaction details
- Use the new chatbot functionality

Make sure to run this before testing the Flutter integration!
