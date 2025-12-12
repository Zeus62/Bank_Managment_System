import pytest
from app.models.user import User

class TestAuthRoutes:
    """Integration tests for authentication routes"""
    
    # ==================== REGISTER TESTS ====================
    
    @pytest.mark.integration
    def test_register_page_loads(self, client):
        """Test that register page loads successfully"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data or b'Create Account' in response.data
    
    @pytest.mark.integration
    def test_register_success(self, client, app):
        """Test successful user registration"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data or b'Login' in response.data
        
        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
    
    @pytest.mark.integration
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with existing username fails"""
        response = client.post('/auth/register', data={
            'username': 'testuser',  # Already exists from fixture
            'email': 'different@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username already exists' in response.data
    
    @pytest.mark.integration
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails"""
        response = client.post('/auth/register', data={
            'username': 'differentuser',
            'email': 'testuser@example.com',  # Already exists from fixture
            'password': 'Password123',
            'confirm_password': 'Password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Email already registered' in response.data
    
    @pytest.mark.integration
    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords fails"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123',
            'confirm_password': 'DifferentPassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Passwords do not match' in response.data
    
    @pytest.mark.integration
    def test_register_short_password(self, client):
        """Test registration with short password fails"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'short',
            'confirm_password': 'short'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'at least 8 characters' in response.data
    
    # ==================== LOGIN TESTS ====================
    
    @pytest.mark.integration
    def test_login_page_loads(self, client):
        """Test that login page loads successfully"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    @pytest.mark.integration
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Login successful' in response.data or b'Dashboard' in response.data or b'Welcome' in response.data
    
    @pytest.mark.integration
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'WrongPassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    @pytest.mark.integration
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails"""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'Password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    @pytest.mark.integration
    def test_login_inactive_user(self, client, app):
        """Test login with inactive user fails"""
        # Create inactive user
        with app.app_context():
            user = User(
                username='inactiveuser',
                email='inactive@example.com',
                is_active=False
            )
            user.set_password('Password123')
            from app import db
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/auth/login', data={
            'username': 'inactiveuser',
            'password': 'Password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'deactivated' in response.data
    
    # ==================== LOGOUT TESTS ====================
    
    @pytest.mark.integration
    def test_logout(self, authenticated_client):
        """Test successful logout"""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'logged out' in response.data or b'Login' in response.data
    
    @pytest.mark.integration
    def test_logout_redirects_to_login(self, authenticated_client):
        """Test logout redirects to login page"""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        
        assert response.status_code == 200
        # Should be on login page after logout
        assert b'Login' in response.data
    
    # ==================== PROTECTED ROUTE TESTS ====================
    
    @pytest.mark.integration
    def test_dashboard_requires_login(self, client):
        """Test that dashboard requires authentication"""
        response = client.get('/', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Please log in' in response.data or b'Login' in response.data
    
    @pytest.mark.integration
    def test_authenticated_user_can_access_dashboard(self, authenticated_client):
        """Test that authenticated user can access dashboard"""
        response = authenticated_client.get('/')
        
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Welcome' in response.data
    
    # ==================== PROFILE TESTS ====================
    
    @pytest.mark.integration
    def test_profile_page_loads(self, authenticated_client):
        """Test that profile page loads for authenticated user"""
        response = authenticated_client.get('/auth/profile')
        
        assert response.status_code == 200
        assert b'Profile' in response.data
    
    @pytest.mark.integration
    def test_profile_requires_login(self, client):
        """Test that profile page requires authentication"""
        response = client.get('/auth/profile', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Please log in' in response.data or b'Login' in response.data