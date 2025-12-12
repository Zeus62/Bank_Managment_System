import pytest
from app.models.account import Account

class TestAccountRoutes:
    """Integration tests for account routes"""
    
    # ==================== LIST ACCOUNTS TESTS ====================
    
    @pytest.mark.integration
    def test_accounts_page_requires_login(self, client):
        """Test that accounts page requires authentication"""
        response = client.get('/accounts/', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Please log in' in response.data or b'Login' in response.data
    
    @pytest.mark.integration
    def test_accounts_page_loads(self, authenticated_client):
        """Test that accounts page loads for authenticated user"""
        response = authenticated_client.get('/accounts/')
        
        assert response.status_code == 200
        assert b'Accounts' in response.data or b'My Accounts' in response.data
    
    @pytest.mark.integration
    def test_accounts_page_shows_user_accounts(self, authenticated_client, test_account):
        """Test that accounts page shows user's accounts"""
        response = authenticated_client.get('/accounts/')
        
        assert response.status_code == 200
        assert b'123456789012' in response.data  # Account number from fixture
    
    # ==================== CREATE ACCOUNT TESTS ====================
    
    @pytest.mark.integration
    def test_create_account_page_loads(self, authenticated_client):
        """Test that create account page loads"""
        response = authenticated_client.get('/accounts/create')
        
        assert response.status_code == 200
        assert b'Create' in response.data or b'New Account' in response.data
    
    @pytest.mark.integration
    def test_create_savings_account_success(self, authenticated_client, app):
        """Test successful savings account creation"""
        response = authenticated_client.post('/accounts/create', data={
            'account_type': 'savings',
            'initial_deposit': '500'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Account created successfully' in response.data
        
        # Verify account was created
        with app.app_context():
            account = Account.query.filter_by(account_type='savings').first()
            assert account is not None
            assert account.balance == 500.0
    
    @pytest.mark.integration
    def test_create_checking_account_success(self, authenticated_client, app):
        """Test successful checking account creation"""
        response = authenticated_client.post('/accounts/create', data={
            'account_type': 'checking',
            'initial_deposit': '1000'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Account created successfully' in response.data
    
    @pytest.mark.integration
    def test_create_account_zero_deposit(self, authenticated_client, app):
        """Test account creation with zero initial deposit"""
        response = authenticated_client.post('/accounts/create', data={
            'account_type': 'savings',
            'initial_deposit': '0'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Account created successfully' in response.data
    
    @pytest.mark.integration
    def test_create_account_negative_deposit_fails(self, authenticated_client):
        """Test account creation with negative deposit fails"""
        response = authenticated_client.post('/accounts/create', data={
            'account_type': 'savings',
            'initial_deposit': '-100'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'cannot be negative' in response.data
    
    # ==================== VIEW ACCOUNT TESTS ====================
    
    @pytest.mark.integration
    def test_view_account_success(self, authenticated_client, test_account):
        """Test viewing account details"""
        response = authenticated_client.get(f'/accounts/{test_account.id}')
        
        assert response.status_code == 200
        assert b'123456789012' in response.data
        assert b'savings' in response.data.lower()
    
    @pytest.mark.integration
    def test_view_nonexistent_account(self, authenticated_client):
        """Test viewing non-existent account returns 404"""
        response = authenticated_client.get('/accounts/99999')
        
        assert response.status_code == 404
    
    @pytest.mark.integration
    def test_view_other_user_account_denied(self, client, app, test_account):
        """Test that user cannot view another user's account"""
        # Create and login as different user
        with app.app_context():
            from app.models.user import User
            from app import db
            
            other_user = User(
                username='otheruser',
                email='other@example.com'
            )
            other_user.set_password('Password123')
            db.session.add(other_user)
            db.session.commit()
        
        # Login as other user
        client.post('/auth/login', data={
            'username': 'otheruser',
            'password': 'Password123'
        })
        
        # Try to access test_account (belongs to testuser)
        response = client.get(f'/accounts/{test_account.id}', follow_redirects=True)
        
        assert b'Access denied' in response.data
    
    # ==================== CLOSE ACCOUNT TESTS ====================
    
    @pytest.mark.integration
    def test_close_account_with_zero_balance(self, authenticated_client, app):
        """Test closing account with zero balance"""
        # Create account with zero balance
        with app.app_context():
            from app.models.user import User
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            account = Account(
                user_id=user.id,
                account_number='111111111111',
                account_type='savings',
                balance=0.0
            )
            db.session.add(account)
            db.session.commit()
            account_id = account.id
        
        response = authenticated_client.post(f'/accounts/{account_id}/close', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'closed successfully' in response.data
    
    @pytest.mark.integration
    def test_close_account_with_balance_fails(self, authenticated_client, test_account):
        """Test closing account with remaining balance fails"""
        response = authenticated_client.post(f'/accounts/{test_account.id}/close', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'withdraw all funds' in response.data
    
    # ==================== SEARCH TESTS ====================
    
    @pytest.mark.integration
    def test_search_account_by_number(self, authenticated_client, test_account):
        """Test searching account by account number"""
        response = authenticated_client.get('/accounts/search?q=123456789012')
        
        assert response.status_code == 200
        assert b'123456789012' in response.data
    
    @pytest.mark.integration
    def test_search_account_no_results(self, authenticated_client):
        """Test search with no matching results"""
        response = authenticated_client.get('/accounts/search?q=999999999999')
        
        assert response.status_code == 200
        # Should show no results or empty state