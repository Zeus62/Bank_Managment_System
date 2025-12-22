import pytest
import time
import uuid
import os
import sys
from datetime import datetime
#How Pytest Discovers This Plugin

try:
    import coverage
except ImportError:
    coverage = None

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from app import create_app, db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction


# ============================================================
# TEST DASHBOARD COLLECTOR
# ============================================================

class TestResultCollector:
    """Collects test results to save to dashboard"""
    
    def __init__(self):
        self.run_id = str(uuid.uuid4())
        self.start_time = None
        self.results = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0
    
    def reset(self):
        self.run_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.results = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0

# Global collector
collector = TestResultCollector()


def get_actual_coverage(session=None):
    """
    Extract coverage percentage by running coverage report and parsing output.
    This is simpler and more reliable than accessing coverage internals.
    """
    if coverage is None:
        return 0.0
    
    try:
        # Look for .coverage file in the project root
        coverage_file = os.path.join(project_root, '.coverage')
        
        if not os.path.exists(coverage_file):
            return 0.0
        
        # Load the coverage data and generate report
        cov = coverage.Coverage(data_file=coverage_file, auto_data=False)
        cov.load()
        
        # Use the coverage report method to get summary
        # The report method returns a float that is the total coverage percentage
        import io
        from contextlib import redirect_stdout
        
        # Capture report output
        report_output = io.StringIO()
        with redirect_stdout(report_output):
            cov.report(include=['app/*'])
        
        output_text = report_output.getvalue()
        
        # Parse the TOTAL line from coverage report output
        # Format: "TOTAL   531   295    44%"
        import re
        match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output_text)
        if match:
            percentage = float(match.group(1))
            return percentage
        
        # If regex didn't match, return 0
        return 0.0
    
    except Exception as e:
        # Silently fail and return 0
        return 0.0


def pytest_sessionstart(session):
    """Called when test session starts"""
    collector.reset()
    print(f"\nTest Dashboard: Recording results (Run ID: {collector.run_id[:8]}...)")


def pytest_runtest_logreport(report):
    """Called for each test"""
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


def pytest_sessionfinish(session, exitstatus):
    """Called when test session finishes - saves results to dashboard"""
    if not collector.results:
        return
    
    duration = time.time() - collector.start_time if collector.start_time else 0
    
    # Calculate actual coverage
    coverage_percentage = get_actual_coverage(session)
    
    try:
        from test_dashboard.app import create_dashboard_app
        from test_dashboard.models import db as dashboard_db, TestRun, TestResult
        
        app = create_dashboard_app()
        
        with app.app_context():
            # Create test run record
            test_run = TestRun(run_id=collector.run_id)
            test_run.end_time = datetime.utcnow()
            test_run.total_tests = len(collector.results)
            test_run.passed = collector.passed
            test_run.failed = collector.failed
            test_run.skipped = collector.skipped
            test_run.duration = duration
            test_run.status = 'passed' if collector.failed == 0 else 'failed'
            test_run.coverage = coverage_percentage
            
            dashboard_db.session.add(test_run)
            dashboard_db.session.commit()
            
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
                dashboard_db.session.add(test_result)
            
            dashboard_db.session.commit()
            
            print(f"\n{'='*60}")
            print(f"TEST DASHBOARD: Results Saved!")
            print(f"   Run ID: {collector.run_id[:8]}...")
            print(f"   Total: {test_run.total_tests} | PASSED: {test_run.passed} | FAILED: {test_run.failed}")
            print(f"   Duration: {duration:.2f}s | Pass Rate: {test_run.pass_rate}%")
            print(f"   Coverage: {test_run.coverage}%")
            print(f"   View at: http://localhost:5050")
            print(f"{'='*60}\n")
            
    except Exception as e:
        print(f"\nDashboard save skipped: {e}")


# ============================================================
# TEST FIXTURES
# ============================================================

class TestConfig:
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_bank.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False


@pytest.fixture(scope='function')
def app():
    """Create application for testing"""
    application = create_app()
    application.config.from_object(TestConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def admin_user(app):
    """Create an admin user"""
    with app.app_context():
        admin = User(
            username='adminuser',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('AdminPassword123')
        db.session.add(admin)
        db.session.commit()
        
        db.session.refresh(admin)
        yield admin

@pytest.fixture(scope='function')
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(
            username='testuser',
            email='testuser@example.com',
            role='customer'
        )
        user.set_password('TestPassword123')
        db.session.add(user)
        db.session.commit()
        
        db.session.refresh(user)
        yield user

@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def init_database(app):
    """Initialize database with test data"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def test_account(app, test_user):
    """Create a test account"""
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        
        account = Account(
            user_id=user.id,
            account_number='123456789012',
            account_type='savings',
            balance=1000.00,
            status='active'
        )
        db.session.add(account)
        db.session.commit()
        
        db.session.refresh(account)
        yield account


@pytest.fixture(scope='function')
def second_account(app, test_user):
    """Create a second test account for transfers"""
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        
        account = Account(
            user_id=user.id,
            account_number='987654321098',
            account_type='checking',
            balance=500.00,
            status='active'
        )
        db.session.add(account)
        db.session.commit()
        
        db.session.refresh(account)
        yield account


@pytest.fixture(scope='function')
def authenticated_client(client, test_user):
    """Create an authenticated client"""
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'TestPassword123'
    }, follow_redirects=True)
    yield client


@pytest.fixture(scope='function')
def admin_client(client, admin_user):
    """Create an authenticated admin client"""
    client.post('/auth/login', data={
        'username': 'adminuser',
        'password': 'AdminPassword123'
    }, follow_redirects=True)
    yield client