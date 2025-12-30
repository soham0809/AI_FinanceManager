"""
Progressive Testing Script
Tests Regex vs ML vs LLM on increasing sample sizes:
- First 10 samples (~3 mins)
- First 20 samples (~6 mins)
- All 286 samples (~40 mins)

Shows results after each batch so you can verify accuracy is improving.
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from evaluation.test_sms_dataset import TEST_SMS_DATASET

# Import components
try:
    from app.utils.ollama_integration import OllamaAssistant
    ollama = OllamaAssistant()
    LLM_AVAILABLE = True
    print("✓ Ollama connected")
except Exception as e:
    LLM_AVAILABLE = False
    print(f"✗ Ollama not available: {e}")
    exit(1)

try:
    from ml_categorizer import ml_categorizer
    ML_AVAILABLE = True
    print("✓ ML categorizer loaded")
except:
    ML_AVAILABLE = False
    print("✗ ML categorizer not available")


class ProgressiveTester:
    """Test with increasing sample sizes"""
    
    def __init__(self):
        self.all_samples = TEST_SMS_DATASET
        
    def regex_parse(self, sms: str) -> Dict[str, Any]:
        """Regex parsing"""
        import re
        sms_lower = sms.lower()
        
        # Type
        if any(p in sms_lower for p in ['upi', 'gpay', 'phonepe', 'paytm', 'bhim', 'ref no']):
            sms_type = "UPI"
        elif 'credit card' in sms_lower or 'cc ' in sms_lower:
            sms_type = "CREDIT_CARD"
        elif 'debit card' in sms_lower or 'dc ' in sms_lower or 'atm' in sms_lower:
            sms_type = "DEBIT_CARD"
        elif any(p in sms_lower for p in ['subscription', 'renewed']):
            sms_type = "SUBSCRIPTION"
        elif any(p in sms_lower for p in ['neft', 'rtgs', 'imps']):
            sms_type = "NET_BANKING"
        elif any(p in sms_lower for p in ['otp', 'mandate', 'offer', 'delivered']):
            sms_type = "NO_TRANSACTION"
        elif 'amc' in sms_lower or 'charges' in sms_lower:
            sms_type = "BANK_CHARGE"
        else:
            sms_type = "OTHER"
        
        # Amount
        patterns = [r'Rs\.?\s*([\d,]+(?:\.\d{1,2})?)', r'INR\s*([\d,]+(?:\.\d{1,2})?)', r'₹\s*([\d,]+(?:\.\d{1,2})?)']
        amount = 0.0
        for pattern in patterns:
            match = re.search(pattern, sms, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1).replace(',', ''))
                    break
                except:
                    pass
        
        return {"type": sms_type, "amount": amount}
    
    def ml_categorize(self, vendor: str) -> str:
        """ML categorization"""
        if not ML_AVAILABLE:
            return "Other"
        category, _ = ml_categorizer.predict_category(vendor)
        return category
    
    def llm_parse(self, sms: str) -> Dict[str, Any]:
        """LLM parsing with proper response handling"""
        try:
            result = ollama.parse_sms_transaction(sms)
            
            # Handle unsuccessful parse
            if not result.get("success", False):
                return {
                    "type": "NO_TRANSACTION" if result.get("is_promotional") else "OTHER",
                    "amount": 0,
                    "category": "Promotional" if result.get("is_promotional") else "Other"
                }
            
            # Extract from nested structure
            tx_data = result.get("transaction_data", {})
            
            # Determine type from SMS content
            sms_lower = sms.lower()
            if any(p in sms_lower for p in ['upi', 'gpay', 'phonepe', 'paytm']):
                sms_type = "UPI"
            elif 'credit card' in sms_lower or 'cc ' in sms_lower:
                sms_type = "CREDIT_CARD"
            elif 'debit card' in sms_lower or 'dc ' in sms_lower or 'atm' in sms_lower:
                sms_type = "DEBIT_CARD"
            elif any(p in sms_lower for p in ['subscription', 'renewed', 'netflix', 'spotify']):
                sms_type = "SUBSCRIPTION"
            elif any(p in sms_lower for p in ['neft', 'rtgs', 'imps']):
                sms_type = "NET_BANKING"
            else:
                sms_type = "OTHER"
            
            return {
                "type": sms_type,
                "amount": float(tx_data.get("amount", 0)),
                "category": tx_data.get("category", "Other")
            }
            
        except Exception as e:
            print(f"  LLM Error: {e}")
            return {"type": "OTHER", "amount": 0, "category": "Other"}
    
    def test_batch(self, num_samples: int):
        """Test first N samples"""
        print(f"\n{'='*70}")
        print(f"TESTING FIRST {num_samples} SAMPLES")
        print(f"{'='*70}")
        
        samples = self.all_samples[:num_samples]
        
        regex_correct_type = 0
        regex_correct_amount = 0
        ml_correct_category = 0
        llm_correct_type = 0
        llm_correct_amount = 0
        llm_correct_category = 0
        
        start_time = time.time()
        
        for i, sample in enumerate(samples):
            sms = sample["sms"]
            expected = sample["expected"]
            
            print(f"\n[{i+1}/{num_samples}] Testing...")
            print(f"  SMS: {sms[:60]}...")
            
            # Regex
            regex_result = self.regex_parse(sms)
            if regex_result["type"] == expected["type"]:
                regex_correct_type += 1
            if abs(regex_result["amount"] - expected["amount"]) < 0.01:
                regex_correct_amount += 1
            
            # ML
            ml_category = self.ml_categorize(expected.get("vendor", ""))
            if ml_category == expected["category"]:
                ml_correct_category += 1
            
            # LLM
            llm_result = self.llm_parse(sms)
            if llm_result["type"] == expected["type"]:
                llm_correct_type += 1
            if abs(llm_result["amount"] - expected["amount"]) < 0.01:
                llm_correct_amount += 1
            if llm_result["category"] == expected["category"]:
                llm_correct_category += 1
            
            print(f"  Expected: Type={expected['type']:15s} Amount=₹{expected['amount']:.2f}")
            print(f"  Regex:    Type={regex_result['type']:15s} Amount=₹{regex_result['amount']:.2f}")
            print(f"  LLM:      Type={llm_result['type']:15s} Amount=₹{llm_result['amount']:.2f}")
        
        elapsed = time.time() - start_time
        
        # Calculate accuracies
        regex_type_acc = regex_correct_type / num_samples * 100
        regex_amount_acc = regex_correct_amount / num_samples * 100
        ml_category_acc = ml_correct_category / num_samples * 100
        llm_type_acc = llm_correct_type / num_samples * 100
        llm_amount_acc = llm_correct_amount / num_samples * 100
        llm_category_acc = llm_correct_category / num_samples * 100
        
        # Print results
        print(f"\n{'='*70}")
        print(f"RESULTS FOR {num_samples} SAMPLES (Time: {elapsed/60:.1f} mins)")
        print(f"{'='*70}")
        
        print(f"\n📊 REGEX:")
        print(f"   Type Accuracy:   {regex_type_acc:.1f}% ({regex_correct_type}/{num_samples})")
        print(f"   Amount Accuracy: {regex_amount_acc:.1f}% ({regex_correct_amount}/{num_samples})")
        
        print(f"\n📊 ML:")
        print(f"   Category Accuracy: {ml_category_acc:.1f}% ({ml_correct_category}/{num_samples})")
        
        print(f"\n📊 LLM:")
        print(f"   Type Accuracy:     {llm_type_acc:.1f}% ({llm_correct_type}/{num_samples})")
        print(f"   Amount Accuracy:   {llm_amount_acc:.1f}% ({llm_correct_amount}/{num_samples})")
        print(f"   Category Accuracy: {llm_category_acc:.1f}% ({llm_correct_category}/{num_samples})")
        
        return {
            "num_samples": num_samples,
            "regex": {"type": regex_type_acc, "amount": regex_amount_acc},
            "ml": {"category": ml_category_acc},
            "llm": {"type": llm_type_acc, "amount": llm_amount_acc, "category": llm_category_acc},
            "time_mins": elapsed / 60
        }


if __name__ == "__main__":
    tester = ProgressiveTester()
    
    print("\n" + "="*70)
    print("PROGRESSIVE ACCURACY TESTING")
    print("="*70)
    print(f"Total samples available: {len(tester.all_samples)}")
    print("\nThis will test in 3 stages:")
    print("  1. First 10 samples  (~3 mins)")
    print("  2. First 20 samples  (~6 mins)")
    print("  3. All 286 samples   (~40 mins)")
    
    # Stage 1: 10 samples
    input("\nPress Enter to test first 10 samples...")
    results_10 = tester.test_batch(10)
    
    # Stage 2: 20 samples
    response = input("\n✓ 10 samples complete! Continue with 20 samples? (yes/no): ")
    if response.lower() == 'yes':
        results_20 = tester.test_batch(20)
        
        # Stage 3: All samples
        response = input("\n✓ 20 samples complete! Continue with ALL 286 samples? (yes/no): ")
        if response.lower() == 'yes':
            results_all = tester.test_batch(286)
            
            # Save final results
            final_results = {
                "timestamp": datetime.now().isoformat(),
                "results_10": results_10,
                "results_20": results_20,
                "results_all": results_all
            }
            
            output_file = "evaluation/results/progressive_test_results.json"
            with open(output_file, 'w') as f:
                json.dump(final_results, f, indent=2)
            
            print(f"\n✓ Results saved to: {output_file}")
            
            # Summary
            print(f"\n{'='*70}")
            print("FINAL SUMMARY")
            print(f"{'='*70}")
            print(f"\nLLM Accuracy Progression:")
            print(f"  10 samples:  {results_10['llm']['type']:.1f}% type, {results_10['llm']['amount']:.1f}% amount")
            print(f"  20 samples:  {results_20['llm']['type']:.1f}% type, {results_20['llm']['amount']:.1f}% amount")
            print(f"  286 samples: {results_all['llm']['type']:.1f}% type, {results_all['llm']['amount']:.1f}% amount")
        else:
            print("\nStopped at 20 samples.")
    else:
        print("\nStopped at 10 samples.")
    
    print("\n✓ Progressive testing complete!")
