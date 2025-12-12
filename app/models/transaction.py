from app import db
from datetime import datetime
import uuid

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    recipient_account = db.Column(db.String(12))
    reference_number = db.Column(db.String(20), unique=True)
    status = db.Column(db.String(20), default='completed')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, account_id, transaction_type, amount, description=None, 
                 recipient_account=None, reference_number=None, status='completed'):
        self.account_id = account_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description
        self.recipient_account = recipient_account
        self.reference_number = reference_number or self.generate_reference()
        self.status = status
    
    @staticmethod
    def generate_reference():
        """Generate a unique reference number"""
        return str(uuid.uuid4())[:12].upper()
    
    def __repr__(self):
        return f'<Transaction {self.reference_number}>'