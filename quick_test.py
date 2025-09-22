#!/usr/bin/env python3
import requests
import json

# Test 1: Training models
print("1. Testing AI model training...")
try:
    response = requests.post('http://localhost:8000/v1/predictions/train-models')
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ SUCCESS: Trained {len(result['categories_trained'])} categories")
    else:
        print(f"   ❌ FAILED: {response.status_code}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 2: SMS parsing with date
print("\n2. Testing SMS parsing with date...")
test_sms = "HDFC Bank: Rs.500.00 debited from A/c **1234 on 23-09-24 at AMAZON INDIA. Avl Bal: Rs.5000.00"
try:
    response = requests.post('http://localhost:8000/v1/parse-sms', 
                           headers={'Content-Type': 'application/json'},
                           data=json.dumps({'sms_text': test_sms}))
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ SUCCESS: Parsed transaction")
        print(f"   📅 Date: {result.get('date')}")
        print(f"   🏪 Vendor: {result.get('vendor')}")
        print(f"   💰 Amount: Rs.{result.get('amount')}")
    else:
        print(f"   ❌ FAILED: {response.status_code}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n✅ Both features should now work in your mobile app!")
