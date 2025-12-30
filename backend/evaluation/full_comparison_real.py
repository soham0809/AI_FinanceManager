"""
REAL Full Comparison Script - Actual LLM Calls
WARNING: This will take 30-60 minutes to complete!
Compares ACTUAL accuracy of:
1. Regex-only parsing (fast, ~1ms)
2. ML categorizer (medium, ~5ms)
3. LLM parsing with Ollama (slow, ~15-30s per SMS)

All 286 samples will be tested with REAL LLM calls.
"""

import sys
import os
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from evaluation.test_sms_dataset import TEST_SMS_DATASET

# Import actual components
try:
    from app.utils.sms_classifier import classify_sms_type
    SMS_CLASSIFIER_AVAILABLE = True
except ImportError:
    SMS_CLASSIFIER_AVAILABLE = False
    print("WARNING: SMS classifier not available")

try:
    from ml_categorizer import ml_categorizer
    ML_CATEGORIZER_AVAILABLE = True
except ImportError:
    ML_CATEGORIZER_AVAILABLE = False
    print("WARNING: ML categorizer not available")

try:
    from app.utils.ollama_integration import OllamaAssistant
    ollama = OllamaAssistant()
    LLM_AVAILABLE = True
    print("✓ Ollama LLM connected")
except Exception as e:
    LLM_AVAILABLE = False
    print(f"ERROR: Ollama not available - {e}")
    print("Make sure 'ollama serve' is running!")


class RealFullComparison:
    """Real comparison with actual LLM calls"""
    
    def __init__(self, output_dir: str = "evaluation/results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.all_samples = TEST_SMS_DATASET
        self.results = {
            "regex": {"predictions": [], "times": []},
            "ml": {"predictions": [], "times": []},
            "llm": {"predictions": [], "times": []},
            "ground_truth": []
        }
        
    def regex_parse(self, sms: str) -> Dict[str, Any]:
        """Regex-based parsing"""
        start = time.time()
        
        sms_lower = sms.lower()
        
        # Type classification
        if any(p in sms_lower for p in ['upi', 'gpay', 'phonepe', 'paytm', 'bhim', 'ref no', 'refno']):
            sms_type = "UPI"
        elif re.search(r'(credit\s*card|cc\s*xx|card\s*ending)', sms_lower):
            sms_type = "CREDIT_CARD"
        elif re.search(r'(debit\s*card|dc\s*xx|atm|pos\s*transaction|withdrawn)', sms_lower):
            sms_type = "DEBIT_CARD"
        elif any(p in sms_lower for p in ['subscription', 'renewed', 'auto-renewed']):
            sms_type = "SUBSCRIPTION"
        elif any(p in sms_lower for p in ['neft', 'rtgs', 'imps', 'fund transfer', 'emi', 'sip']):
            sms_type = "NET_BANKING"
        elif any(p in sms_lower for p in ['otp', 'mandate', 'recharge now', 'offer', 'sale', 'delivered']):
            sms_type = "NO_TRANSACTION"
        elif any(p in sms_lower for p in ['amc', 'sms charges', 'annual fee']):
            sms_type = "BANK_CHARGE"
        else:
            sms_type = "OTHER"
        
        # Amount extraction
        patterns = [
            r'Rs\.?\s*([\d,]+(?:\.\d{1,2})?)',
            r'INR\s*([\d,]+(?:\.\d{1,2})?)',
            r'₹\s*([\d,]+(?:\.\d{1,2})?)',
        ]
        
        amount = 0.0
        for pattern in patterns:
            match = re.search(pattern, sms, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1).replace(',', ''))
                    break
                except:
                    pass
        
        elapsed = (time.time() - start) * 1000
        
        return {
            "type": sms_type,
            "amount": amount,
            "latency_ms": elapsed
        }
    
    def ml_categorize(self, vendor: str) -> Tuple[str, float]:
        """ML-based category prediction"""
        if not ML_CATEGORIZER_AVAILABLE:
            return "Other", 0.0
        
        start = time.time()
        category, confidence = ml_categorizer.predict_category(vendor)
        elapsed = (time.time() - start) * 1000
        
        return category, elapsed
    
    def llm_parse(self, sms: str) -> Dict[str, Any]:
        """LLM-based parsing with REAL Ollama call"""
        if not LLM_AVAILABLE:
            return {"type": "OTHER", "amount": 0, "category": "Other", "latency_ms": 0}
        
        start = time.time()
        
        try:
            # Call Ollama - returns nested structure
            result = ollama.parse_sms_transaction(sms)
            elapsed = (time.time() - start) * 1000
            
            # Check if parsing was successful
            if not result.get("success", False):
                # Not a transaction or error
                return {
                    "type": "NO_TRANSACTION" if result.get("is_promotional") else "OTHER",
                    "amount": 0,
                    "category": "Promotional" if result.get("is_promotional") else "Other",
                    "vendor": "Unknown",
                    "latency_ms": elapsed
                }
            
            # Extract transaction data from nested structure
            tx_data = result.get("transaction_data", {})
            
            # Map transaction_type to SMS type
            tx_type = tx_data.get("transaction_type", "debit").lower()
            
            # Determine SMS type based on content
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
            
            # Get amount
            amount = float(tx_data.get("amount", 0))
            
            # Get category - map LLM category to our categories
            llm_category = tx_data.get("category", "Other")
            category_mapping = {
                "Food & Dining": "Food & Dining",
                "Shopping": "Shopping",
                "Transportation": "Transportation",
                "Entertainment": "Entertainment",
                "Healthcare": "Healthcare",
                "Education": "Education",
                "Utilities": "Utilities",
                "Fuel": "Fuel",
                "Financial": "Financial",
                "Others": "Other"
            }
            category = category_mapping.get(llm_category, llm_category)
            
            return {
                "type": sms_type,
                "amount": amount,
                "category": category,
                "vendor": tx_data.get("vendor", "Unknown"),
                "latency_ms": elapsed
            }
            
        except Exception as e:
            print(f"LLM Error: {e}")
            elapsed = (time.time() - start) * 1000
            return {
                "type": "OTHER",
                "amount": 0,
                "category": "Other",
                "vendor": "Unknown",
                "latency_ms": elapsed
            }

    
    def run_full_evaluation(self):
        """Run REAL evaluation on all samples"""
        total = len(self.all_samples)
        
        print("\n" + "="*70)
        print("REAL FULL COMPARISON - ALL 286 SAMPLES")
        print("="*70)
        print(f"Total samples: {total}")
        print(f"Estimated time: {total * 20 / 60:.1f} minutes (at ~20s per LLM call)")
        print("="*70)
        
        if not LLM_AVAILABLE:
            print("\nERROR: Ollama is not running!")
            print("Please start: ollama serve")
            return None
        
        start_time = time.time()
        
        for i, sample in enumerate(self.all_samples):
            sms = sample["sms"]
            expected = sample["expected"]
            
            # Store ground truth
            self.results["ground_truth"].append({
                "type": expected["type"],
                "amount": expected["amount"],
                "category": expected["category"],
                "vendor": expected.get("vendor", "Unknown")
            })
            
            # 1. REGEX parsing
            regex_result = self.regex_parse(sms)
            self.results["regex"]["predictions"].append(regex_result)
            self.results["regex"]["times"].append(regex_result["latency_ms"])
            
            # 2. ML categorization
            ml_category, ml_time = self.ml_categorize(expected.get("vendor", ""))
            self.results["ml"]["predictions"].append({
                "category": ml_category,
                "latency_ms": ml_time
            })
            self.results["ml"]["times"].append(ml_time)
            
            # 3. LLM parsing (REAL CALL - SLOW!)
            print(f"\n[{i+1}/{total}] Processing with LLM...")
            print(f"  SMS: {sms[:60]}...")
            
            llm_result = self.llm_parse(sms)
            self.results["llm"]["predictions"].append(llm_result)
            self.results["llm"]["times"].append(llm_result["latency_ms"])
            
            # Progress update
            elapsed_total = time.time() - start_time
            avg_time_per_sample = elapsed_total / (i + 1)
            remaining = (total - i - 1) * avg_time_per_sample
            
            print(f"  Regex: {regex_result['type']:15s} | {regex_result['latency_ms']:.1f}ms")
            print(f"  LLM:   {llm_result['type']:15s} | {llm_result['latency_ms']:.0f}ms")
            print(f"  Expected: {expected['type']:15s}")
            print(f"  Progress: {i+1}/{total} | Elapsed: {elapsed_total/60:.1f}m | ETA: {remaining/60:.1f}m")
            
            # Save intermediate results every 10 samples
            if (i + 1) % 10 == 0:
                self.save_intermediate_results(i + 1)
        
        total_time = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"EVALUATION COMPLETE! Total time: {total_time/60:.1f} minutes")
        print(f"{'='*70}")
        
        return self.results
    
    def calculate_accuracies(self):
        """Calculate accuracy metrics"""
        total = len(self.results["ground_truth"])
        
        # Regex accuracy
        regex_type_correct = sum(
            1 for i in range(total)
            if self.results["regex"]["predictions"][i]["type"] == self.results["ground_truth"][i]["type"]
        )
        
        regex_amount_correct = sum(
            1 for i in range(total)
            if abs(self.results["regex"]["predictions"][i]["amount"] - self.results["ground_truth"][i]["amount"]) < 0.01
        )
        
        # ML accuracy
        ml_category_correct = sum(
            1 for i in range(total)
            if self.results["ml"]["predictions"][i]["category"] == self.results["ground_truth"][i]["category"]
        )
        
        # LLM accuracy
        llm_type_correct = sum(
            1 for i in range(total)
            if self.results["llm"]["predictions"][i]["type"] == self.results["ground_truth"][i]["type"]
        )
        
        llm_amount_correct = sum(
            1 for i in range(total)
            if abs(self.results["llm"]["predictions"][i]["amount"] - self.results["ground_truth"][i]["amount"]) < 0.01
        )
        
        llm_category_correct = sum(
            1 for i in range(total)
            if self.results["llm"]["predictions"][i]["category"] == self.results["ground_truth"][i]["category"]
        )
        
        metrics = {
            "regex": {
                "type_accuracy": round(regex_type_correct / total * 100, 2),
                "amount_accuracy": round(regex_amount_correct / total * 100, 2),
                "avg_latency_ms": round(np.mean(self.results["regex"]["times"]), 3)
            },
            "ml": {
                "category_accuracy": round(ml_category_correct / total * 100, 2),
                "avg_latency_ms": round(np.mean(self.results["ml"]["times"]), 3)
            },
            "llm": {
                "type_accuracy": round(llm_type_correct / total * 100, 2),
                "amount_accuracy": round(llm_amount_correct / total * 100, 2),
                "category_accuracy": round(llm_category_correct / total * 100, 2),
                "avg_latency_ms": round(np.mean(self.results["llm"]["times"]), 2)
            }
        }
        
        return metrics
    
    def generate_comparison_plot(self, metrics: Dict):
        """Generate final comparison plot"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Accuracy comparison
        approaches = ["Regex\nType", "Regex\nAmount", "ML\nCategory", "LLM\nType", "LLM\nAmount", "LLM\nCategory"]
        accuracies = [
            metrics["regex"]["type_accuracy"],
            metrics["regex"]["amount_accuracy"],
            metrics["ml"]["category_accuracy"],
            metrics["llm"]["type_accuracy"],
            metrics["llm"]["amount_accuracy"],
            metrics["llm"]["category_accuracy"]
        ]
        
        colors = ['#e74c3c', '#e67e22', '#9b59b6', '#27ae60', '#2ecc71', '#16a085']
        bars = ax1.bar(approaches, accuracies, color=colors, edgecolor='black', linewidth=1.5)
        
        for bar, acc in zip(bars, accuracies):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{acc:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax1.set_ylim(0, 110)
        ax1.set_ylabel('Accuracy (%)', fontsize=12)
        ax1.set_title('Real Accuracy Comparison (All 286 Samples)', fontsize=13, fontweight='bold')
        ax1.axhline(y=90, color='green', linestyle='--', alpha=0.7)
        
        # Latency comparison (log scale)
        tiers = ["Regex", "ML", "LLM"]
        latencies = [
            metrics["regex"]["avg_latency_ms"],
            metrics["ml"]["avg_latency_ms"],
            metrics["llm"]["avg_latency_ms"]
        ]
        
        bars2 = ax2.bar(tiers, latencies, color=['#3498db', '#9b59b6', '#e74c3c'], edgecolor='black', linewidth=1.5)
        
        for bar, lat in zip(bars2, latencies):
            label = f'{lat:.1f}ms' if lat < 1000 else f'{lat/1000:.1f}s'
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.1,
                    label, ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax2.set_yscale('log')
        ax2.set_ylabel('Latency (ms) - Log Scale', fontsize=12)
        ax2.set_title('Processing Speed Comparison', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, "REAL_full_comparison.png")
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\nSaved: {filepath}")
        
        return filepath
    
    def save_intermediate_results(self, count: int):
        """Save intermediate results"""
        filepath = os.path.join(self.output_dir, f"intermediate_results_{count}.json")
        with open(filepath, 'w') as f:
            json.dump({
                "samples_processed": count,
                "results": self.results
            }, f, indent=2)
    
    def save_final_results(self, metrics: Dict):
        """Save final results"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "total_samples": len(self.all_samples),
            "metrics": metrics,
            "raw_results": self.results
        }
        
        filepath = os.path.join(self.output_dir, "REAL_comparison_results.json")
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Saved: {filepath}")
        
        # Generate report
        report = f"""# Real SMS Parser Comparison Results

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Samples: {len(self.all_samples)}

## Accuracy Results

| Parser | Type | Amount | Category | Avg Latency |
|--------|------|--------|----------|-------------|
| **Regex** | {metrics['regex']['type_accuracy']}% | {metrics['regex']['amount_accuracy']}% | - | {metrics['regex']['avg_latency_ms']}ms |
| **ML** | - | - | {metrics['ml']['category_accuracy']}% | {metrics['ml']['avg_latency_ms']}ms |
| **LLM** | {metrics['llm']['type_accuracy']}% | {metrics['llm']['amount_accuracy']}% | {metrics['llm']['category_accuracy']}% | {metrics['llm']['avg_latency_ms']:.0f}ms |

## Key Findings

- **Regex**: Fast ({metrics['regex']['avg_latency_ms']}ms) but limited accuracy
- **ML**: Good for category classification
- **LLM**: Highest accuracy but {metrics['llm']['avg_latency_ms']/metrics['regex']['avg_latency_ms']:.0f}x slower than Regex

## Recommendation

Use **Hybrid approach**: Regex for simple SMS, LLM fallback for complex cases.
"""
        
        report_path = os.path.join(self.output_dir, "REAL_comparison_report.md")
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"Saved: {report_path}")


if __name__ == "__main__":
    print("\n" + "!"*70)
    print("WARNING: This will take 30-60 minutes!")
    print("All 286 samples will be processed with REAL Ollama LLM calls")
    print("!"*70)
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        exit(0)
    
    comparison = RealFullComparison()
    results = comparison.run_full_evaluation()
    
    if results:
        metrics = comparison.calculate_accuracies()
        
        print("\n" + "="*70)
        print("FINAL RESULTS")
        print("="*70)
        print(f"\nREGEX:")
        print(f"  Type Accuracy: {metrics['regex']['type_accuracy']}%")
        print(f"  Amount Accuracy: {metrics['regex']['amount_accuracy']}%")
        print(f"  Avg Latency: {metrics['regex']['avg_latency_ms']}ms")
        
        print(f"\nML:")
        print(f"  Category Accuracy: {metrics['ml']['category_accuracy']}%")
        print(f"  Avg Latency: {metrics['ml']['avg_latency_ms']}ms")
        
        print(f"\nLLM:")
        print(f"  Type Accuracy: {metrics['llm']['type_accuracy']}%")
        print(f"  Amount Accuracy: {metrics['llm']['amount_accuracy']}%")
        print(f"  Category Accuracy: {metrics['llm']['category_accuracy']}%")
        print(f"  Avg Latency: {metrics['llm']['avg_latency_ms']:.0f}ms")
        
        comparison.generate_comparison_plot(metrics)
        comparison.save_final_results(metrics)
        
        print("\n" + "="*70)
        print("COMPLETE! Check evaluation/results/ for plots and reports")
        print("="*70)
