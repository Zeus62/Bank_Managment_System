import pytest
from app.models.account import Account
from app.models.transaction import Transaction

class TestTransactionRoutes:
    """Integration tests for transaction routes"""
    
    # ==================== DEPOSIT TESTS ====================
    
    @pytest.mark.integration
    def test_deposit_page_loads(self, authenticated_client):
        """Test that deposit page loads"""
        response = authenticated_client.get('/transactions/deposit')
        
        assert response.status_code == 200
        assert b'Deposit' in response.data
    
    @pytest.mark.integration
    def test_deposit_success(self, authenticated_client, test_account, app):
        """Test successful deposit"""
        initial_balance = test_account.balance
        
        response = authenticated_client.post('/transactions/deposit', data={
            'account_id': test_account.id,
            'amount': '250.00',
            'description': 'Test deposit'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Successfully deposited' in response.data
        
        # Verify balance updated
        with app.app_context():
            account = Account.query.get(test_account.id)
            assert account.balance == initial_balance + 250.00
    
    @pytest.mark.integration
    def test_deposit_zero_amount_fails(self, authenticated_client, test_account):
        """Test deposit with zero amount fails"""
        response = authenticated_client.post('/transactions/deposit', data={
            'account_id': test_account.id,
            'amount': '0',
            'description': 'Test'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'must be positive' in response.data
    
    @pytest.mark.integration
    def test_deposit_negative_amount_fails(self, authenticated_client, test_account):
        """Test deposit with negative amount fails"""
        response = authenticated_client.post('/transactions/deposit', data={
            'account_id': test_account.id,
            'amount': '-100',
            'description': 'Test'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'must be positive' in response.data
    
    # ==================== WITHDRAW TESTS ====================
    
    @pytest.mark.integration
    def test_withdraw_page_loads(self, authenticated_client):
        """Test that withdraw page loads"""
        response = authenticated_client.get('/transactions/withdraw')
        
        assert response.status_code == 200
        assert b'Withdraw' in response.data
    
    @pytest.mark.integration
    def test_withdraw_success(self, authenticated_client, test_account, app):
        """Test successful withdrawal"""
        initial_balance = test_account.balance
        
        response = authenticated_client.post('/transactions/withdraw', data={
            'account_id': test_account.id,
            'amount': '200.00',
            'description': 'Test withdrawal'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Successfully withdrew' in response.data
        
        # Verify balance updated
        with app.app_context():
            account = Account.query.get(test_account.id)
            assert account.balance == initial_balance - 200.00
    
    @pytest.mark.integration
    def test_withdraw_insufficient_funds(self, authenticated_client, test_account):
        """Test withdrawal with insufficient funds fails"""
        response = authenticated_client.post('/transactions/withdraw', data={
            'account_id': test_account.id,
            'amount': '999999.00',
            'description': 'Test'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Insufficient funds' in response.data
    
    @pytest.mark.integration
    def test_withdraw_zero_amount_fails(self, authenticated_client, test_account):
        """Test withdrawal with zero amount fails"""
        response = authenticated_client.post('/transactions/withdraw', data={
            'account_id': test_account.id,
            'amount': '0',
            'description': 'Test'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'must be positive' in response.data
    
    # ==================== TRANSFER TESTS ====================
    
    @pytest.mark.integration
    def test_transfer_page_loads(self, authenticated_client):
        """Test that transfer page loads"""
        response = authenticated_client.get('/transactions/transfer')
        
        assert response.status_code == 200
        assert b'Transfer' in response.data
    
    @pytest.mark.integration
    def test_transfer_success(self, authenticated_client, test_account, second_account, app):
        """Test successful transfer between accounts"""
        initial_from_balance = test_account.balance
        initial_to_balance = second_account.balance
        transfer_amount = 300.00
        
        response = authenticated_client.post('/transactions/transfer', data={
            'from_account_id': test_account.id,
            'to_account_number': second_account.account_number,
            'amount': str(transfer_amount),
            'description': 'Test transfer'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Successfully transferred' in response.data
        
        # Verify balances updated
        with app.app_context():
            from_account = Account.query.get(test_account.id)
            to_account = Account.query.get(second_account.id)
            
            assert from_account.balance == initial_from_balance - transfer_amount
            assert to_account.balance == initial_to_balance + transfer_amount
    
    @pytest.mark.integration
    def test_transfer_insufficient_funds(self, authenticated_client, test_account, second_account):
        """Test transfer with insufficient funds fails"""
        response = authenticated_client.post('/transactions/transfer', data={
            'from_account_id': test_account.id,
            'to_account_number': second_account.account_number,
            'amount': '999999.00',
            'description': 'Test'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Insufficient funds' in response.data
    
    @pytest.mark.integration
    def test_transfer_to_nonexistent_account(self, authenticated_client, test_account):
        """Test transfer to non-existent account fails"""
        response = authenticated_client.post('/transactions/transfer', data={
            'from_account_id': test_account.id,
            'to_account_number': '000000000000',
            'amount': '100.00',
            'description': 'Test'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'not found' in response.data
    
    @pytest.mark.integration
    def test_transfer_to_same_account(self, authenticated_client, test_account):
        """Test transfer to same account fails"""
        response = authenticated_client.post('/transactions/transfer', data={
            'from_account_id': test_account.id,
            'to_account_number': test_account.account_number,
            'amount': '100.00',
            'description': 'Test'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'same account' in response.data
    
    # ==================== HISTORY TESTS ====================
    
    @pytest.mark.integration
    def test_history_page_loads(self, authenticated_client):
        """Test that transaction history page loads"""
        response = authenticated_client.get('/transactions/history')
        
        assert response.status_code == 200
        assert b'History' in response.data or b'Transaction' in response.data
    
    @pytest.mark.integration
    def test_history_shows_transactions(self, authenticated_client, test_account, app):
        """Test that history shows user's transactions"""
        # Create a transaction
        with app.app_context():
            from app import db
            transaction = Transaction(
                account_id=test_account.id,
                transaction_type='deposit',
                amount=100.00,
                description='Test transaction'
            )
            db.session.add(transaction)
            db.session.commit()
        
        response = authenticated_client.get('/transactions/history')
        
        assert response.status_code == 200
        assert b'deposit' in response.data.lower()
    
    # ==================== SEARCH TESTS ====================
    
    @pytest.mark.integration
    def test_search_transactions_page_loads(self, authenticated_client):
        """Test that transaction search page loads"""
        response = authenticated_client.get('/transactions/search')
        
        assert response.status_code == 200
        assert b'Search' in response.data
    
    @pytest.mark.integration
    def test_search_by_transaction_type(self, authenticated_client, test_account, app):
        """Test searching transactions by type"""
        # Create transactions
        with app.app_context():
            from app import db
            deposit = Transaction(
                account_id=test_account.id,
                transaction_type='deposit',
                amount=100.00
            )
            db.session.add(deposit)
            db.session.commit()
        
        response = authenticated_client.get('/transactions/search?type=deposit')
        
        assert response.status_code == 200