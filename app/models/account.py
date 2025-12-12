from app import db
from datetime import datetime
import random
import string

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_number = db.Column(db.String(12), unique=True, nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with transactions
    transactions = db.relationship('Transaction', backref='account', lazy=True)
    
    def __init__(self, user_id, account_number, account_type, balance=0.0, status='active'):
        self.user_id = user_id
        self.account_number = account_number
        self.account_type = account_type
        self.balance = balance
        self.status = status
    
    @staticmethod
    def generate_account_number():
        """Generate a unique 12-digit account number"""
        return ''.join(random.choices(string.digits, k=12))
    
    def deposit(self, amount):
        """Deposit money into account"""
        if amount > 0:
            self.balance += amount
            return True
        return False
    
    def withdraw(self, amount):
        """Withdraw money from account"""
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            return True
        return False
    
    def __repr__(self):
        return f'<Account {self.account_number}>'