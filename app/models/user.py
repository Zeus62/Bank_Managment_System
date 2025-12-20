from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    """
    User Model
    ----------
    Represents a registered user in the banking system.
    
    Attributes:
        id: Unique identifier (auto-generated)
        username: User's chosen username (must be unique)
        email: User's email address (must be unique)
        password_hash: Encrypted password (never store plain text!)
        is_admin: Boolean flag for admin privileges
        created_at: Timestamp of registration
        accounts: Relationship to user's bank accounts
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='customer')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with accounts
    # Relationship: One user can have many accounts
    # backref creates a reverse reference (account.owner returns the user)
    # lazy='dynamic' means accounts aren't loaded until accessed
    accounts = db.relationship('Account', backref='owner', lazy=True)
    
    def __init__(self, username, email, role='customer', is_active=True):
        self.username = username
        self.email = email
        self.role = role
        self.is_active = is_active
    
    def set_password(self, password):
        """
        Hash and store the password
        
        WHY HASH PASSWORDS?
        - If database is compromised, hackers can't see real passwords
        - Hashing is one-way (can't reverse to get original)
        - Uses salt (random data) to prevent rainbow table attacks
        
        Args:
            password: Plain text password
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'