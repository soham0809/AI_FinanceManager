#!/usr/bin/env python3
"""Verify database schema"""
import sqlite3

conn = sqlite3.connect('financial_copilot.db')
cursor = conn.cursor()

# Check transactions table
print("📋 Transaction Table Schema:\n")
cursor.execute('PRAGMA table_info(transactions)')
columns = cursor.fetchall()

for col in columns:
    col_id, name, type_, notnull, default, pk = col
    nullable = "NOT NULL" if notnull else "NULL"
    default_str = f"DEFAULT: {default}" if default else ""
    print(f"  {name:25} {type_:15} {nullable:10} {default_str}")

print(f"\n✅ Total columns: {len(columns)}")

# Check for critical fields
critical_fields = ['transaction_type', 'date', 'user_id', 'sms_text']
existing_fields = [col[1] for col in columns]

print("\n🔍 Critical Field Check:")
for field in critical_fields:
    if field in existing_fields:
        print(f"  ✅ {field} exists")
    else:
        print(f"  ❌ {field} MISSING!")

# Check users table
print("\n\n📋 Users Table Schema:\n")
cursor.execute('PRAGMA table_info(users)')
user_columns = cursor.fetchall()

for col in user_columns:
    col_id, name, type_, notnull, default, pk = col
    nullable = "NOT NULL" if notnull else "NULL"
    default_str = f"DEFAULT: {default}" if default else ""
    print(f"  {name:25} {type_:15} {nullable:10} {default_str}")

print(f"\n✅ Total columns: {len(user_columns)}")

conn.close()
print("\n✅ Schema verification complete!")
