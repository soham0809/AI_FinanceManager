"""
Test Phase 5 - AI Predictive Analytics functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_predictive_analytics():
    """Test all predictive analytics endpoints"""
    print("=" * 70)
    print("PHASE 5 TEST - AI Predictive Analytics")
    print("=" * 70)
    
    # Test 1: Train Predictive Models
    print("\n1. Testing Model Training...")
    try:
        response = requests.post(f"{BASE_URL}/v1/predictions/train-models")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Models trained for {len(data['categories_trained'])} categories")
            print(f"   Categories: {', '.join(data['categories_trained'])}")
            for category, score in data['model_scores'].items():
                print(f"     {category}: MAE = {score:.2f}")
        else:
            print(f"   [FAIL] Training failed: {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 2: Spending Forecasts
    print("\n2. Testing Spending Forecasts...")
    try:
        response = requests.get(f"{BASE_URL}/v1/predictions/spending-forecast")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Generated forecasts for {len(data['forecasts'])} categories")
            for forecast in data['forecasts'][:3]:  # Show first 3
                print(f"     {forecast['category']}: Rs.{forecast['current_month_prediction']:.0f} "
                      f"({forecast['trend']}, confidence: {forecast['confidence_score']:.2f})")
                print(f"       Recommendation: {forecast['recommendation'][:60]}...")
        else:
            print(f"   [FAIL] Forecast failed: {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 3: Specific Category Forecast
    print("\n3. Testing Category-Specific Forecast...")
    try:
        response = requests.get(f"{BASE_URL}/v1/predictions/spending-forecast?category=Food & Dining")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Food & Dining forecast: ₹{data['current_month_prediction']:.0f}")
            print(f"       Trend: {data['trend']}, Confidence: {data['confidence_score']:.2f}")
            print(f"       Recommendation: {data['recommendation']}")
        else:
            print(f"   [FAIL] Category forecast failed: {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 4: Savings Goal Creation
    print("\n4. Testing Savings Goal Creation...")
    try:
        goal_data = {
            "target_amount": 50000,
            "target_months": 12,
            "current_income": 25000,
            "current_expenses": 20000
        }
        response = requests.post(f"{BASE_URL}/v1/predictions/savings-goal", json=goal_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Savings goal created: ₹{data['target_amount']} in {goal_data['target_months']} months")
            print(f"       Monthly required: ₹{data['monthly_required']:.0f}")
            print(f"       Achievable: {data['achievable']}")
            print(f"       Recommendation: {data['recommendation']}")
        else:
            print(f"   [FAIL] Savings goal failed: {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 5: Budget Alerts
    print("\n5. Testing Budget Alerts...")
    try:
        budget_data = {
            "limits": {
                "Food & Dining": 3000,
                "Shopping": 5000,
                "Transportation": 1000,
                "Entertainment": 2000
            }
        }
        response = requests.post(f"{BASE_URL}/v1/predictions/budget-alerts", json=budget_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Generated {len(data['alerts'])} budget alerts")
            for alert in data['alerts']:
                print(f"     {alert['category']}: {alert['percentage_used']:.1f}% used "
                      f"({alert['alert_level']} alert)")
                print(f"       {alert['message']}")
        else:
            print(f"   [FAIL] Budget alerts failed: {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 6: Financial Insights
    print("\n6. Testing Financial Insights...")
    try:
        response = requests.get(f"{BASE_URL}/v1/predictions/financial-insights")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Generated {len(data['insights'])} insights")
            for key, insight in data['insights'].items():
                print(f"     {key}: {insight}")
        else:
            print(f"   [FAIL] Financial insights failed: {response.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print("\n" + "=" * 70)
    print("Phase 5 Predictive Analytics Test Completed!")
    print("=" * 70)

if __name__ == "__main__":
    test_predictive_analytics()
