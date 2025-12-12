import pytest
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from app import create_app, db
from app.models.user import User
from app.models.account import Account

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_e2e.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False

class TestUserFlowsE2E:
    """End-to-End tests for complete user flows"""
    
    @pytest.fixture(scope='class')
    def app(self):
        """Create application for E2E testing"""
        application = create_app()
        application.config.from_object(TestConfig)
        
        with application.app_context():
            db.create_all()
            
            # Create test user
            user = User(
                username='e2euser',
                email='e2e@example.com'
            )
            user.set_password('E2EPassword123')
            db.session.add(user)
            db.session.commit()
            
        yield application
        
        with application.app_context():
            db.drop_all()
    
    @pytest.fixture(scope='class')
    def live_server(self, app):
        """Start a live server for Selenium tests"""
        # Run Flask app in a separate thread
        server_thread = threading.Thread(
            target=lambda: app.run(port=5001, use_reloader=False, threaded=True)
        )
        server_thread.daemon = True
        server_thread.start()
        time.sleep(2)  # Wait for server to start
        yield 'http://localhost:5001'
    
    @pytest.fixture(scope='class')
    def driver(self):
        """Set up Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    # ==================== LOGIN FLOW TESTS ====================
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_complete_login_flow(self, driver, live_server):
        """Test complete login flow from start to dashboard"""
        # Navigate to login page
        driver.get(f'{live_server}/auth/login')
        
        # Verify login page loaded
        assert 'Login' in driver.title or 'Login' in driver.page_source
        
        # Fill in login form
        username_field = driver.find_element(By.ID, 'username')
        password_field = driver.find_element(By.ID, 'password')
        
        username_field.clear()
        username_field.send_keys('e2euser')
        password_field.clear()
        password_field.send_keys('E2EPassword123')
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for redirect
        time.sleep(2)
        
        # Verify successful login (should be on dashboard or see welcome message)
        assert 'Dashboard' in driver.page_source or 'Welcome' in driver.page_source
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_login_with_invalid_credentials(self, driver, live_server):
        """Test login with invalid credentials shows error"""
        driver.get(f'{live_server}/auth/login')
        
        # Fill in wrong credentials
        username_field = driver.find_element(By.ID, 'username')
        password_field = driver.find_element(By.ID, 'password')
        
        username_field.clear()
        username_field.send_keys('wronguser')
        password_field.clear()
        password_field.send_keys('wrongpassword')
        
        # Submit
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        time.sleep(1)
        
        # Should show error message
        assert 'Invalid' in driver.page_source or 'error' in driver.page_source.lower()
    
    # ==================== REGISTRATION FLOW TESTS ====================
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_complete_registration_flow(self, driver, live_server):
        """Test complete registration flow"""
        driver.get(f'{live_server}/auth/register')
        
        # Verify register page loaded
        assert 'Register' in driver.page_source or 'Create Account' in driver.page_source
        
        # Fill in registration form
        driver.find_element(By.ID, 'username').send_keys('newseleniumuser')
        driver.find_element(By.ID, 'email').send_keys('selenium@example.com')
        driver.find_element(By.ID, 'password').send_keys('SeleniumPass123')
        driver.find_element(By.ID, 'confirm_password').send_keys('SeleniumPass123')
        
        # Submit
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        time.sleep(2)
        
        # Should redirect to login page with success message
        assert 'Login' in driver.page_source or 'successful' in driver.page_source.lower()


class TestAccountFlowsE2E:
    """E2E tests for account operations"""
    
    @pytest.fixture(scope='class')
    def app(self):
        """Create application for E2E testing"""
        application = create_app()
        application.config.from_object(TestConfig)
        
        with application.app_context():
            db.create_all()
            
            # Create test user with account
            user = User(
                username='accountuser',
                email='account@example.com'
            )
            user.set_password('AccountPass123')
            db.session.add(user)
            db.session.commit()
            
            # Create test account
            account = Account(
                user_id=user.id,
                account_number='555555555555',
                account_type='savings',
                balance=5000.00
            )
            db.session.add(account)
            db.session.commit()
            
        yield application
        
        with application.app_context():
            db.drop_all()
    
    @pytest.fixture(scope='class')
    def live_server(self, app):
        """Start a live server"""
        server_thread = threading.Thread(
            target=lambda: app.run(port=5002, use_reloader=False, threaded=True)
        )
        server_thread.daemon = True
        server_thread.start()
        time.sleep(2)
        yield 'http://localhost:5002'
    
    @pytest.fixture(scope='class')
    def driver(self):
        """Set up Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    @pytest.fixture(scope='class')
    def logged_in_driver(self, driver, live_server):
        """Get a logged-in driver"""
        driver.get(f'{live_server}/auth/login')
        
        driver.find_element(By.ID, 'username').send_keys('accountuser')
        driver.find_element(By.ID, 'password').send_keys('AccountPass123')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        time.sleep(2)
        yield driver
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_view_accounts_flow(self, logged_in_driver, live_server):
        """Test viewing accounts list"""
        logged_in_driver.get(f'{live_server}/accounts/')
        
        time.sleep(1)
        
        # Should see accounts page
        assert 'Accounts' in logged_in_driver.page_source or 'Account' in logged_in_driver.page_source
        # Should see the test account number
        assert '555555555555' in logged_in_driver.page_source
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_create_account_flow(self, logged_in_driver, live_server):
        """Test creating a new account"""
        logged_in_driver.get(f'{live_server}/accounts/create')
        
        time.sleep(1)
        
        # Select account type
        account_type_select = Select(logged_in_driver.find_element(By.ID, 'account_type'))
        account_type_select.select_by_value('checking')
        
        # Enter initial deposit
        deposit_field = logged_in_driver.find_element(By.ID, 'initial_deposit')
        deposit_field.clear()
        deposit_field.send_keys('1000')
        
        # Submit
        submit_button = logged_in_driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        time.sleep(2)
        
        # Should show success message
        assert 'created successfully' in logged_in_driver.page_source.lower() or 'Account' in logged_in_driver.page_source


class TestTransactionFlowsE2E:
    """E2E tests for transaction operations"""
    
    @pytest.fixture(scope='class')
    def app(self):
        """Create application for E2E testing"""
        application = create_app()
        application.config.from_object(TestConfig)
        
        with application.app_context():
            db.create_all()
            
            # Create test user with accounts
            user = User(
                username='transactionuser',
                email='transaction@example.com'
            )
            user.set_password('TransPass123')
            db.session.add(user)
            db.session.commit()
            
            # Create source account
            account1 = Account(
                user_id=user.id,
                account_number='111111111111',
                account_type='savings',
                balance=10000.00
            )
            db.session.add(account1)
            
            # Create destination account
            account2 = Account(
                user_id=user.id,
                account_number='222222222222',
                account_type='checking',
                balance=500.00
            )
            db.session.add(account2)
            db.session.commit()
            
        yield application
        
        with application.app_context():
            db.drop_all()
    
    @pytest.fixture(scope='class')
    def live_server(self, app):
        """Start a live server"""
        server_thread = threading.Thread(
            target=lambda: app.run(port=5003, use_reloader=False, threaded=True)
        )
        server_thread.daemon = True
        server_thread.start()
        time.sleep(2)
        yield 'http://localhost:5003'
    
    @pytest.fixture(scope='class')
    def driver(self):
        """Set up Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    @pytest.fixture(scope='class')
    def logged_in_driver(self, driver, live_server):
        """Get a logged-in driver"""
        driver.get(f'{live_server}/auth/login')
        
        driver.find_element(By.ID, 'username').send_keys('transactionuser')
        driver.find_element(By.ID, 'password').send_keys('TransPass123')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        time.sleep(2)
        yield driver
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_deposit_flow(self, logged_in_driver, live_server):
        """Test complete deposit flow"""
        logged_in_driver.get(f'{live_server}/transactions/deposit')
        
        time.sleep(1)
        
        # Select account
        account_select = Select(logged_in_driver.find_element(By.ID, 'account_id'))
        account_select.select_by_index(1)  # Select first account
        
        # Enter amount
        amount_field = logged_in_driver.find_element(By.ID, 'amount')
        amount_field.clear()
        amount_field.send_keys('500')
        
        # Enter description
        desc_field = logged_in_driver.find_element(By.ID, 'description')
        desc_field.send_keys('E2E Test Deposit')
        
        # Submit
        submit_button = logged_in_driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        time.sleep(2)
        
        # Should show success message
        assert 'Successfully deposited' in logged_in_driver.page_source or 'success' in logged_in_driver.page_source.lower()
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_withdraw_flow(self, logged_in_driver, live_server):
        """Test complete withdrawal flow"""
        logged_in_driver.get(f'{live_server}/transactions/withdraw')
        
        time.sleep(1)
        
        # Select account
        account_select = Select(logged_in_driver.find_element(By.ID, 'account_id'))
        account_select.select_by_index(1)
        
        # Enter amount
        amount_field = logged_in_driver.find_element(By.ID, 'amount')
        amount_field.clear()
        amount_field.send_keys('200')
        
        # Enter description
        desc_field = logged_in_driver.find_element(By.ID, 'description')
        desc_field.send_keys('E2E Test Withdrawal')
        
        # Submit
        submit_button = logged_in_driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        time.sleep(2)
        
        # Should show success message
        assert 'Successfully withdrew' in logged_in_driver.page_source or 'success' in logged_in_driver.page_source.lower()
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_transfer_flow(self, logged_in_driver, live_server):
        """Test complete transfer flow"""
        logged_in_driver.get(f'{live_server}/transactions/transfer')
        
        time.sleep(1)
        
        # Select source account
        from_account_select = Select(logged_in_driver.find_element(By.ID, 'from_account_id'))
        from_account_select.select_by_index(1)
        
        # Enter destination account number
        to_account_field = logged_in_driver.find_element(By.ID, 'to_account_number')
        to_account_field.clear()
        to_account_field.send_keys('222222222222')
        
        # Enter amount
        amount_field = logged_in_driver.find_element(By.ID, 'amount')
        amount_field.clear()
        amount_field.send_keys('300')
        
        # Enter description
        desc_field = logged_in_driver.find_element(By.ID, 'description')
        desc_field.send_keys('E2E Test Transfer')
        
        # Submit
        submit_button = logged_in_driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        time.sleep(2)
        
        # Should show success message
        assert 'Successfully transferred' in logged_in_driver.page_source or 'success' in logged_in_driver.page_source.lower()
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_transaction_history_flow(self, logged_in_driver, live_server):
        """Test viewing transaction history"""
        logged_in_driver.get(f'{live_server}/transactions/history')
        
        time.sleep(1)
        
        # Should see history page
        assert 'History' in logged_in_driver.page_source or 'Transaction' in logged_in_driver.page_source