import pytest
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

class TestUserModel:
    """Unit tests for User model"""
    
    @pytest.mark.unit
    def test_create_user(self, app):
        """Test user creation"""
        with app.app_context():
            user = User(
                username='newuser',
                email='newuser@test.com',
                role='customer'
            )
            assert user.username == 'newuser'
            assert user.email == 'newuser@test.com'
            assert user.role == 'customer'
            assert user.is_active == True
    
    @pytest.mark.unit
    def test_password_hashing(self, app):
        """Test password is properly hashed"""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            user.set_password('mypassword123')
            
            # Password should be hashed, not plain text
            assert user.password_hash != 'mypassword123'
            assert user.check_password('mypassword123') == True
            assert user.check_password('wrongpassword') == False
    
    @pytest.mark.unit
    def test_password_hash_is_unique(self, app):
        """Test that same password produces different hashes"""
        with app.app_context():
            user1 = User(username='user1', email='user1@test.com')
            user2 = User(username='user2', email='user2@test.com')
            
            user1.set_password('samepassword')
            user2.set_password('samepassword')
            
            # Hashes should be different due to salting
            assert user1.password_hash != user2.password_hash
    
    @pytest.mark.unit
    def test_user_default_role(self, app):
        """Test default user role is customer"""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            assert user.role == 'customer'
    
    @pytest.mark.unit
    def test_user_default_active_status(self, app):
        """Test default user is active"""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            assert user.is_active == True
    
    

class TestAccountModel:
    """Unit tests for Account model"""
    
    @pytest.mark.unit
    def test_create_account(self, app, test_user):
        """Test account creation"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            account = Account(
                user_id=user.id,
                account_number='111111111111',
                account_type='savings',
                balance=100.00
            )
            assert account.account_type == 'savings'
            assert account.balance == 100.00
            assert account.status == 'active'
    
    @pytest.mark.unit
    def test_generate_account_number(self, app):
        """Test account number generation"""
        with app.app_context():
            account_number = Account.generate_account_number()
            
            assert len(account_number) == 12
            assert account_number.isdigit()
    
    @pytest.mark.unit
    def test_account_number_uniqueness(self, app):
        """Test generated account numbers are unique"""
        with app.app_context():
            numbers = [Account.generate_account_number() for _ in range(100)]
            unique_numbers = set(numbers)
            
            # All numbers should be unique
            assert len(unique_numbers) == 100
    
    @pytest.mark.unit
    def test_deposit(self, app, test_account):
        """Test deposit functionality"""
        with app.app_context():
            account = Account.query.filter_by(account_number='123456789012').first()
            initial_balance = account.balance
            
            result = account.deposit(500.00)
            
            assert result == True
            assert account.balance == initial_balance + 500.00
    
    @pytest.mark.unit
    def test_deposit_negative_amount(self, app, test_account):
        """Test deposit with negative amount fails"""
        with app.app_context():
            account = Account.query.filter_by(account_number='123456789012').first()
            initial_balance = account.balance
            
            result = account.deposit(-100.00)
            
            assert result == False
            assert account.balance == initial_balance
    
    @pytest.mark.unit
    def test_withdraw(self, app, test_account):
        """Test withdrawal functionality"""
        with app.app_context():
            account = Account.query.filter_by(account_number='123456789012').first()
            initial_balance = account.balance
            
            result = account.withdraw(200.00)
            
            assert result == True
            assert account.balance == initial_balance - 200.00
    
    @pytest.mark.unit
    def test_withdraw_insufficient_funds(self, app, test_account):
        """Test withdrawal with insufficient funds fails"""
        with app.app_context():
            account = Account.query.filter_by(account_number='123456789012').first()
            initial_balance = account.balance
            
            result = account.withdraw(99999.00)
            
            assert result == False
            assert account.balance == initial_balance
    
    @pytest.mark.unit
    def test_withdraw_negative_amount(self, app, test_account):
        """Test withdrawal with negative amount fails"""
        with app.app_context():
            account = Account.query.filter_by(account_number='123456789012').first()
            initial_balance = account.balance
            
            result = account.withdraw(-50.00)
            
            assert result == False
            assert account.balance == initial_balance


class TestTransactionModel:
    """Unit tests for Transaction model"""
    
    @pytest.mark.unit
    def test_create_transaction(self, app, test_account):
        """Test transaction creation"""
        with app.app_context():
            account = Account.query.filter_by(account_number='123456789012').first()
            
            transaction = Transaction(
                account_id=account.id,
                transaction_type='deposit',
                amount=100.00,
                description='Test deposit'
            )
            
            assert transaction.transaction_type == 'deposit'
            assert transaction.amount == 100.00
            assert transaction.status == 'completed'
    
    @pytest.mark.unit
    def test_generate_reference(self, app):
        """Test reference number generation"""
        with app.app_context():
            reference = Transaction.generate_reference()
            
            assert len(reference) == 12
            assert reference.isupper()
    
    @pytest.mark.unit
    def test_reference_uniqueness(self, app):
        """Test generated references are unique"""
        with app.app_context():
            references = [Transaction.generate_reference() for _ in range(100)]
            unique_refs = set(references)
            
            assert len(unique_refs) == 100