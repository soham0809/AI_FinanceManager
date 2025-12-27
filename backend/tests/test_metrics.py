"""
Test Metrics Collection for Research Paper
Collects quantitative metrics from test execution
"""
import pytest
import json
import time
from pathlib import Path
from datetime import datetime


class MetricsCollector:
    """Collects and stores test metrics"""
    
    def __init__(self):
        self.metrics = {
            "test_run_timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "test_duration_seconds": 0,
            "endpoints_tested": [],
            "coverage_summary": {},
            "performance_metrics": []
        }
    
    def record_endpoint(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Record endpoint test result"""
        self.metrics["endpoints_tested"].append({
            "endpoint": endpoint,
            "method": method,
            "response_time_ms": round(response_time * 1000, 2),
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        })
    
    def save_metrics(self, filename: str = "test_metrics.json"):
        """Save metrics to JSON file"""
        metrics_path = Path(__file__).parent / filename
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        return str(metrics_path)


# Global metrics collector
metrics_collector = MetricsCollector()


@pytest.fixture(scope="session", autouse=True)
def collect_session_metrics(request):
    """Collect metrics for entire test session"""
    start_time = time.time()
    
    yield
    
    # Calculate duration
    duration = time.time() - start_time
    metrics_collector.metrics["test_duration_seconds"] = round(duration, 2)
    
    # Save metrics
    metrics_file = metrics_collector.save_metrics()
    print(f"\n\n📊 Test Metrics saved to: {metrics_file}")
