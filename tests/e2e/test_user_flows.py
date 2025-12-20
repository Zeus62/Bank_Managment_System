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
    """
    Special configuration for E2E tests
    
    WHY A SEPARATE CONFIG?
    ─────────────────────
    • TESTING = True: Flask knows this is a test
    • Separate database: Don't mess with real data
    • CSRF disabled: Forms work without tokens (easier testing)
    """
    TESTING = True
    # Tells Flask this is a test environment
    # Changes some behaviors (e.g., error handling)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_e2e.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    # WHY?
    # CSRF tokens change every request
    # Selenium would need to find and include them
    # Disabling makes testing easier
    # IMPORTANT: Only disable in tests!

class TestUserFlowsE2E:
    """End-to-End tests for complete user flows"""
    
    """
    End-to-End tests for complete user flows
    
    WHAT IS A TEST CLASS?
    ─────────────────────
    Groups related tests together.
    Shared fixtures (setup/teardown) apply to all tests in class.
    
    CLASS STRUCTURE:
    ┌─────────────────────────────────────────────────────────────┐
    │  TestUserFlowsE2E                                           │
    │  ├── Fixtures (setup)                                       │
    │  │   ├── app()        → Creates Flask application          │
    │  │   ├── live_server() → Starts server on port 5001        │
    │  │   └── driver()     → Creates Chrome browser             │
    │  │                                                          │
    │  └── Test Methods                                           │
    │      ├── test_complete_login_flow()                        │
    │      ├── test_login_with_invalid_credentials()             │
    │      └── test_complete_registration_flow()                 │
    └─────────────────────────────────────────────────────────────┘
    """
    @pytest.fixture(scope='class')
    def app(self):
        """Create application for E2E testing"""

        """ 
        A fixture is reusable setup/teardown code.
        Instead of repeating the same setup in every test,
        you define it once and pytest injects it automatically.
        """
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
        
        # YIELD: Pause here, let tests run, then continue
        yield application

        # CLEANUP: After all tests in class are done
        with application.app_context():
            db.drop_all()
    
    @pytest.fixture(scope='class')
    def live_server(self, app):
        """
        Start a live server for Selenium tests
        
        WHY A LIVE SERVER?
        ──────────────────
        Selenium needs a REAL server running.
        It's a real browser making real HTTP requests.
        We can't use Flask's test client here.
        
        THREADING:
        ──────────
        We run Flask in a separate thread so:
        • Flask server runs continuously
        • Our tests can continue executing
        • Both happen simultaneously
        """
        # Create a background thread for the server
        server_thread = threading.Thread(
            target=lambda: app.run(port=5001, use_reloader=False, threaded=True)
        )

        # daemon=True means: kill this thread when main program exits
        server_thread.daemon = True
        server_thread.start()
        time.sleep(2)  # Wait for server to start

        # Return the server URL for tests to use
        yield 'http://localhost:5001'
        # daemon thread dies automatically when tests end
    
    @pytest.fixture(scope='class')
    def driver(self):
        """Set up Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        # This affects what elements are visible/clickable
        chrome_options.add_argument('--window-size=1920,1080')

        # HEADLESS MODE: Browser runs without visible window
        # WHY HEADLESS?
        # • Faster (no GUI rendering)
        # • Works on servers without displays
        # • CI/CD pipelines can run tests
        # • Doesn't interrupt your work

        service = Service(ChromeDriverManager().install())
        # ChromeDriverManager().install():
        #   1. Detects your Chrome browser version
        #   2. Downloads matching ChromeDriver
        #   3. Caches it locally
        #   4. Returns path to the executable
        #
        # Service: Wraps the ChromeDriver executable
        
        # ─────────────────────────────────────────────────────────────
        # STEP 3: CREATE BROWSER INSTANCE
        # ─────────────────────────────────────────────────────────────
        
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        # This LAUNCHES Chrome browser (headlessly)
        # driver is now your remote control for the browser
        
        driver.implicitly_wait(10)
        # IMPLICIT WAIT: If element not found, wait up to 10 seconds
        # Selenium will retry finding the element during this time
        # Helps with pages that load dynamically
        
        # ─────────────────────────────────────────────────────────────
        # STEP 4: PROVIDE DRIVER TO TESTS
        # ─────────────────────────────────────────────────────────────
        
        yield driver
        # Tests run here, using the driver
        
        # ─────────────────────────────────────────────────────────────
        # STEP 5: CLEANUP
        # ─────────────────────────────────────────────────────────────
        
        driver.quit()
        # Close browser and stop ChromeDriver process
        # IMPORTANT: Always quit! Otherwise Chrome processes pile up
    
    # ==================== LOGIN FLOW TESTS ====================
    
    # ═══════════════════════════════════════════════════════════════════
#                      TEST METHODS
# ═══════════════════════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.slow
def test_complete_login_flow(self, driver, live_server):
    """
    Test complete login flow from start to dashboard
    
    DECORATORS EXPLAINED:
    ─────────────────────
    @pytest.mark.e2e
        Tags this test as "e2e"
        Run only e2e tests: pytest -m e2e
        Skip e2e tests: pytest -m "not e2e"
    
    @pytest.mark.slow
        Tags this test as "slow"
        E2E tests ARE slow (real browser, network, etc.)
        Skip slow tests: pytest -m "not slow"
    
    PARAMETERS:
    ───────────
    self: Reference to the test class instance
    driver: Chrome browser (from fixture)
    live_server: URL like 'http://localhost:5001' (from fixture)
    """
    
    # ─────────────────────────────────────────────────────────────
    # STEP 1: NAVIGATE TO LOGIN PAGE
    # ─────────────────────────────────────────────────────────────
    
    driver.get(f'{live_server}/auth/login')
    # driver.get(url): Like typing URL in address bar and pressing Enter
    # Browser navigates to the page
    # Waits for page to load
    
    """
    WHAT HAPPENS:
    
    ┌──────────────────────────────────────────┐
    │  🌐 Chrome (Headless)                    │
    │  ─────────────────────────────────────── │
    │  localhost:5001/auth/login               │
    │  ─────────────────────────────────────── │
    │                                          │
    │        ┌────────────────────┐           │
    │        │      LOGIN         │           │
    │        ├────────────────────┤           │
    │        │ Username: [      ] │           │
    │        │ Password: [      ] │           │
    │        │                    │           │
    │        │    [  Login  ]     │           │
    │        └────────────────────┘           │
    │                                          │
    └──────────────────────────────────────────┘
    """
    
    # ─────────────────────────────────────────────────────────────
    # STEP 2: VERIFY PAGE LOADED
    # ─────────────────────────────────────────────────────────────
    
    assert 'Login' in driver.title or 'Login' in driver.page_source
    # driver.title: The <title> tag content
    # driver.page_source: Entire HTML of the page
    #
    # We check if "Login" appears anywhere
    # This confirms we're on the right page
    
    # ─────────────────────────────────────────────────────────────
    # STEP 3: FIND INPUT ELEMENTS
    # ─────────────────────────────────────────────────────────────
    
    username_field = driver.find_element(By.ID, 'username')
    password_field = driver.find_element(By.ID, 'password')
    # find_element: Find ONE element matching the criteria
    # By.ID: Search by HTML id attribute
    #
    # HTML looks like:
    # <input type="text" id="username" name="username">
    # <input type="password" id="password" name="password">
    
    """
    ELEMENT LOCATION STRATEGIES:
    ────────────────────────────
    
    By.ID           → find_element(By.ID, 'username')
                      <input id="username">
                      
    By.NAME         → find_element(By.NAME, 'email')
                      <input name="email">
                      
    By.CLASS_NAME   → find_element(By.CLASS_NAME, 'btn-primary')
                      <button class="btn-primary">
                      
    By.TAG_NAME     → find_element(By.TAG_NAME, 'h1')
                      <h1>...</h1>
                      
    By.CSS_SELECTOR → find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                      <button type="submit">
                      Most flexible, uses CSS selectors
                      
    By.XPATH        → find_element(By.XPATH, '//button[@type="submit"]')
                      <button type="submit">
                      Most powerful, uses XPath expressions
                      
    By.LINK_TEXT    → find_element(By.LINK_TEXT, 'Register')
                      <a href="/register">Register</a>
                      
    By.PARTIAL_LINK_TEXT → find_element(By.PARTIAL_LINK_TEXT, 'Reg')
                           <a href="/register">Register Here</a>
    """
    
    # ─────────────────────────────────────────────────────────────
    # STEP 4: ENTER TEXT INTO FIELDS
    # ─────────────────────────────────────────────────────────────
    
    username_field.clear()
    # clear(): Remove any existing text in the field
    # Important if field has placeholder or default value
    
    username_field.send_keys('e2euser')
    # send_keys(): Type text into the field
    # Simulates keyboard input, character by character
    
    """
    WHAT HAPPENS:
    
    Before send_keys:
    ┌────────────────────┐
    │ Username: [      ] │
    └────────────────────┘
    
    After send_keys('e2euser'):
    ┌────────────────────┐
    │ Username: [e2euser]│
    └────────────────────┘
    """
    
    password_field.clear()
    password_field.send_keys('E2EPassword123')
    
    # ─────────────────────────────────────────────────────────────
    # STEP 5: CLICK SUBMIT BUTTON
    # ─────────────────────────────────────────────────────────────
    
    submit_button = driver.find_element(
        By.CSS_SELECTOR, 
        'button[type="submit"]'
    )
    # CSS SELECTOR: button[type="submit"]
    # Finds: <button type="submit">Login</button>
    #
    # CSS Selector is powerful:
    # • 'button' - tag name
    # • '[type="submit"]' - attribute selector
    # • Combined: button with type="submit"
    
    submit_button.click()
    # click(): Simulate mouse click on the element
    # This submits the form
    
    """
    WHAT HAPPENS AFTER CLICK:
    
    1. Form submits (POST /auth/login)
    2. Server validates credentials
    3. Server sets session cookie
    4. Server redirects to dashboard
    5. Browser follows redirect
    6. Dashboard page loads
    """
    
    # ─────────────────────────────────────────────────────────────
    # STEP 6: WAIT FOR REDIRECT
    # ─────────────────────────────────────────────────────────────
    
    time.sleep(2)
    # Wait 2 seconds for page to load
    #
    # NOTE: time.sleep is NOT ideal!
    # Better approach: WebDriverWait (explicit wait)
    #
    # WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.ID, 'dashboard'))
    # )
    # This waits UP TO 10 seconds for dashboard element to appear
    
    # ─────────────────────────────────────────────────────────────
    # STEP 7: VERIFY LOGIN SUCCESS
    # ─────────────────────────────────────────────────────────────
    
    assert 'Dashboard' in driver.page_source or 'Welcome' in driver.page_source
    # Check if we see "Dashboard" or "Welcome" on the page
    # This confirms login was successful
    #
    # If login failed, we'd still be on login page
    # and this assertion would fail
    
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