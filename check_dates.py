import requests
from datetime import datetime

# Get transactions from backend
response = requests.get('http://localhost:8000/v1/transactions-public')
data = response.json()

print("=== TRANSACTION DATE ANALYSIS ===")
print(f"Total transactions: {len(data)}")
print("\nSample transactions with dates:")

# Check for date issues
future_dates = []
current_year = datetime.now().year

for i, t in enumerate(data[:10]):
    date_str = t.get('date', 'N/A')
    vendor = t.get('vendor', 'N/A')
    amount = t.get('amount', 'N/A')
    
    print(f"{i+1}. ID: {t.get('id', 'N/A')}, Date: {date_str}, Vendor: {vendor}, Amount: {amount}")
    
    # Check for future dates
    if date_str != 'N/A':
        try:
            date_obj = datetime.fromisoformat(date_str.replace('T', ' ').split('.')[0])
            if date_obj.year > current_year:
                future_dates.append((t.get('id'), date_str, vendor))
        except:
            pass

print(f"\n=== FUTURE DATE ISSUES ===")
print(f"Found {len(future_dates)} transactions with future dates:")
for tid, date, vendor in future_dates[:5]:
    print(f"ID: {tid}, Date: {date}, Vendor: {vendor}")
