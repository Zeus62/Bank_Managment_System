from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.account import Account
from app.models.transaction import Transaction

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Get user's accounts
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    
    # Calculate total balance
    total_balance = sum(account.balance for account in accounts)
    
    # Get recent transactions (last 5)
    account_ids = [account.id for account in accounts]
    recent_transactions = Transaction.query.filter(
        Transaction.account_id.in_(account_ids)
    ).order_by(Transaction.timestamp.desc()).limit(5).all()
    
    return render_template('dashboard/index.html',
                          accounts=accounts,
                          total_balance=total_balance,
                          recent_transactions=recent_transactions)