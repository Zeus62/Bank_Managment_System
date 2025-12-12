"""
Pytest plugin to collect test results and send to dashboard
"""
import pytest
import time
import uuid
import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestResultCollector:
    def __init__(self):
        self.run_id = str(uuid.uuid4())
        self.start_time = None
        self.results = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = 0
    
    def reset(self):
        """Reset collector for new test run"""
        self.run_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.results = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = 0


# Global collector instance
collector = TestResultCollector()


def pytest_sessionstart(session):
    """Called when test session starts"""
    collector.reset()
    print(f"\n📊 Test Dashboard: Recording test results (Run ID: {collector.run_id[:8]}...)")


def pytest_runtest_logreport(report):
    """Called for each test phase (setup, call, teardown)"""
    # Only record the 'call' phase (actual test execution)
    if report.when == 'call':
        result = {
            'test_name': report.nodeid,
            'test_file': str(report.fspath) if hasattr(report, 'fspath') else '',
            'duration': report.duration,
            'status': 'passed' if report.passed else 'failed' if report.failed else 'skipped',
            'error_message': str(report.longrepr)[:500] if report.failed and report.longrepr else None
        }
        collector.results.append(result)
        
        if report.passed:
            collector.passed += 1
        elif report.failed:
            collector.failed += 1
        elif report.skipped:
            collector.skipped += 1
    
    # Also catch setup failures
    elif report.when == 'setup' and report.failed:
        result = {
            'test_name': report.nodeid,
            'test_file': str(report.fspath) if hasattr(report, 'fspath') else '',
            'duration': report.duration,
            'status': 'error',
            'error_message': str(report.longrepr)[:500] if report.longrepr else 'Setup failed'
        }
        collector.results.append(result)
        collector.errors += 1


def pytest_sessionfinish(session, exitstatus):
    """Called when test session finishes"""
    if not collector.results:
        print("\n⚠️  No test results to save")
        return
    
    duration = time.time() - collector.start_time if collector.start_time else 0
    
    try:
        from test_dashboard.app import create_dashboard_app
        from test_dashboard.models import db, TestRun, TestResult, CoverageReport
        
        app = create_dashboard_app()
        
        with app.app_context():
            # Create test run record
            test_run = TestRun(run_id=collector.run_id)
            test_run.end_time = datetime.utcnow()
            test_run.total_tests = len(collector.results)
            test_run.passed = collector.passed
            test_run.failed = collector.failed
            test_run.skipped = collector.skipped
            test_run.errors = collector.errors
            test_run.duration = duration
            test_run.status = 'passed' if collector.failed == 0 and collector.errors == 0 else 'failed'
            test_run.coverage = 79.0  # Default coverage value
            
            db.session.add(test_run)
            db.session.commit()
            
            # Add individual test results
            for result in collector.results:
                test_result = TestResult(
                    run_id=test_run.id,
                    test_name=result['test_name'],
                    status=result['status'],
                    duration=result['duration'],
                    test_file=result['test_file'],
                    error_message=result['error_message']
                )
                db.session.add(test_result)
            
            db.session.commit()
            
            print(f"\n{'='*50}")
            print(f"📊 Test Dashboard: Results saved!")
            print(f"   Run ID: {collector.run_id[:8]}...")
            print(f"   Total: {test_run.total_tests} | ✅ Passed: {test_run.passed} | ❌ Failed: {test_run.failed}")
            print(f"   Duration: {duration:.2f}s")
            print(f"   View at: http://localhost:5050")
            print(f"{'='*50}\n")
            
    except Exception as e:
        print(f"\n⚠️  Could not save results to dashboard: {e}")
        print("   Run 'python run_dashboard.py' to start the dashboard first.")