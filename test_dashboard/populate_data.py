"""
Populate the dashboard with test data
utility script that fills the test dashboard with fake/sample data for demonstration and development purposes
"""
import os
import sys
import uuid
from datetime import datetime, timedelta
import random

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from test_dashboard.app import create_dashboard_app
from test_dashboard.models import db, TestRun, TestResult, CoverageReport

def populate_sample_data():
    """Populate dashboard with sample test data"""
    app = create_dashboard_app()
    
    with app.app_context():
        # Clear existing data
        TestResult.query.delete()
        CoverageReport.query.delete()
        TestRun.query.delete()
        db.session.commit()
        
        print("🗑️  Cleared existing data")
        
        # Test case names
        test_cases = [
            # Unit Tests - Models
            ("tests/unit/test_models.py::TestUserModel::test_create_user", "passed"),
            ("tests/unit/test_models.py::TestUserModel::test_password_hashing", "passed"),
            ("tests/unit/test_models.py::TestUserModel::test_password_hash_is_unique", "passed"),
            ("tests/unit/test_models.py::TestUserModel::test_user_default_role", "passed"),
            ("tests/unit/test_models.py::TestUserModel::test_user_default_active_status", "passed"),
            ("tests/unit/test_models.py::TestAccountModel::test_create_account", "passed"),
            ("tests/unit/test_models.py::TestAccountModel::test_generate_account_number", "passed"),
            ("tests/unit/test_models.py::TestAccountModel::test_deposit", "passed"),
            ("tests/unit/test_models.py::TestAccountModel::test_withdraw", "passed"),
            ("tests/unit/test_models.py::TestAccountModel::test_withdraw_insufficient_funds", "passed"),
            ("tests/unit/test_models.py::TestTransactionModel::test_create_transaction", "passed"),
            ("tests/unit/test_models.py::TestTransactionModel::test_generate_reference", "passed"),
            
            # Unit Tests - Validators
            ("tests/unit/test_validators.py::TestPasswordValidation::test_ec1_password_too_short", "passed"),
            ("tests/unit/test_validators.py::TestPasswordValidation::test_ec2_password_valid_length", "passed"),
            ("tests/unit/test_validators.py::TestPasswordValidation::test_boundary_8_characters", "passed"),
            ("tests/unit/test_validators.py::TestAmountValidation::test_ec1_negative_amount", "passed"),
            ("tests/unit/test_validators.py::TestAmountValidation::test_ec3_valid_amount", "passed"),
            ("tests/unit/test_validators.py::TestAmountValidation::test_boundary_zero", "passed"),
            ("tests/unit/test_validators.py::TestAccountNumberValidation::test_valid_account_number", "passed"),
            
            # Integration Tests - Auth
            ("tests/integration/test_auth_routes.py::TestAuthRoutes::test_register_page_loads", "passed"),
            ("tests/integration/test_auth_routes.py::TestAuthRoutes::test_register_success", "passed"),
            ("tests/integration/test_auth_routes.py::TestAuthRoutes::test_login_page_loads", "passed"),
            ("tests/integration/test_auth_routes.py::TestAuthRoutes::test_login_success", "passed"),
            ("tests/integration/test_auth_routes.py::TestAuthRoutes::test_login_wrong_password", "passed"),
            ("tests/integration/test_auth_routes.py::TestAuthRoutes::test_logout", "passed"),
            
            # Integration Tests - Accounts
            ("tests/integration/test_account_routes.py::TestAccountRoutes::test_accounts_page_loads", "passed"),
            ("tests/integration/test_account_routes.py::TestAccountRoutes::test_create_account_page_loads", "passed"),
            ("tests/integration/test_account_routes.py::TestAccountRoutes::test_create_savings_account_success", "passed"),
            ("tests/integration/test_account_routes.py::TestAccountRoutes::test_view_account_success", "passed"),
            ("tests/integration/test_account_routes.py::TestAccountRoutes::test_close_account_with_zero_balance", "passed"),
            
            # Integration Tests - Transactions
            ("tests/integration/test_transaction_routes.py::TestTransactionRoutes::test_deposit_page_loads", "passed"),
            ("tests/integration/test_transaction_routes.py::TestTransactionRoutes::test_deposit_success", "passed"),
            ("tests/integration/test_transaction_routes.py::TestTransactionRoutes::test_withdraw_success", "passed"),
            ("tests/integration/test_transaction_routes.py::TestTransactionRoutes::test_transfer_success", "passed"),
            ("tests/integration/test_transaction_routes.py::TestTransactionRoutes::test_transfer_insufficient_funds", "passed"),
            ("tests/integration/test_transaction_routes.py::TestTransactionRoutes::test_history_page_loads", "passed"),
        ]
        
        # Create test runs for the last 10 days
        for days_ago in range(10, -1, -1):
            run_date = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 12))
            
            # Create test run
            run = TestRun(run_id=str(uuid.uuid4()))
            run.start_time = run_date
            run.end_time = run_date + timedelta(seconds=random.uniform(10, 25))
            run.total_tests = len(test_cases)
            
            # Simulate some variation - mostly passing
            num_failed = random.choices([0, 1, 2, 3], weights=[60, 25, 10, 5])[0]
            run.passed = len(test_cases) - num_failed
            run.failed = num_failed
            run.skipped = 0
            run.duration = random.uniform(12, 20)
            run.coverage = random.uniform(76, 82)
            run.status = 'passed' if run.failed == 0 else 'failed'
            
            db.session.add(run)
            db.session.commit()
            
            # Select which tests to fail
            failed_indices = random.sample(range(len(test_cases)), num_failed) if num_failed > 0 else []
            
            # Add test results
            for i, (test_name, _) in enumerate(test_cases):
                status = 'failed' if i in failed_indices else 'passed'
                error_msg = None
                if status == 'failed':
                    error_msg = "AssertionError: Expected value did not match actual value"
                
                test_result = TestResult(
                    run_id=run.id,
                    test_name=test_name,
                    status=status,
                    duration=random.uniform(0.01, 0.5),
                    test_file=test_name.split('::')[0],
                    error_message=error_msg
                )
                db.session.add(test_result)
            
            # Add coverage data for latest run
            if days_ago == 0:
                coverage_data = [
                    ("app/__init__.py", 32, 0, 100.0),
                    ("app/models/__init__.py", 3, 0, 100.0),
                    ("app/models/account.py", 36, 1, 97.2),
                    ("app/models/transaction.py", 27, 1, 96.3),
                    ("app/models/user.py", 26, 1, 96.2),
                    ("app/routes/__init__.py", 4, 0, 100.0),
                    ("app/routes/accounts.py", 65, 5, 92.3),
                    ("app/routes/admin.py", 112, 64, 42.9),
                    ("app/routes/auth.py", 82, 19, 76.8),
                    ("app/routes/dashboard.py", 13, 0, 100.0),
                    ("app/routes/transactions.py", 130, 20, 84.6),
                ]
                
                for module, stmts, miss, cov in coverage_data:
                    coverage = CoverageReport(
                        run_id=run.id,
                        module_name=module,
                        statements=stmts,
                        missing=miss,
                        coverage_percent=cov
                    )
                    db.session.add(coverage)
            
            db.session.commit()
            status_icon = "✅" if run.failed == 0 else "❌"
            print(f"{status_icon} Created run for {run_date.strftime('%Y-%m-%d %H:%M')}: {run.passed} passed, {run.failed} failed")
        
        print("\n" + "=" * 50)
        print("🎉 Dashboard populated with sample data!")
        print("📊 Run 'python run_dashboard.py' to view the dashboard")
        print("=" * 50)


if __name__ == '__main__':
    populate_sample_data()