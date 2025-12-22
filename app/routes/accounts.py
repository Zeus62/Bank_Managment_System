from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.account import Account
from app.models.transaction import Transaction

# WHAT IS A DECORATOR? A function that wraps another function to add behavior.

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')

@accounts_bp.route('/')
@login_required
def list_accounts():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('accounts/list.html', accounts=accounts)

@accounts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_account():
    if request.method == 'POST':
        account_type = request.form.get('account_type')
        initial_deposit = request.form.get('initial_deposit', 0)
        
        try:
            initial_deposit = float(initial_deposit)
        except ValueError:
            initial_deposit = 0
        
        if initial_deposit < 0:
            flash('Initial deposit cannot be negative.', 'danger')
            return render_template('accounts/create.html')
        
        # Create new account
        account = Account(
            user_id=current_user.id,
            account_number=Account.generate_account_number(),
            account_type=account_type,
            balance=initial_deposit
        )
        
        db.session.add(account)
        db.session.commit()
        
        # If initial deposit, create a transaction record
        if initial_deposit > 0:
            transaction = Transaction(
                account_id=account.id,
                transaction_type='deposit',
                amount=initial_deposit,
                description='Initial deposit',
                reference_number=Transaction.generate_reference()
            )
            db.session.add(transaction)
            db.session.commit()
        
        flash(f'Account created successfully! Account Number: {account.account_number}', 'success')
        return redirect(url_for('accounts.list_accounts'))
    
    return render_template('accounts/create.html')


@accounts_bp.route('/<int:account_id>')
@login_required
def view_account(account_id):

    account = Account.query.get_or_404(account_id)
    
    # Check if user owns this account
    if account.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('accounts.list_accounts'))
    
    # Get transactions for this account
    transactions = Transaction.query.filter_by(account_id=account_id)\
        .order_by(Transaction.timestamp.desc()).limit(10).all()
    
    return render_template('accounts/view.html', 
                          account=account, 
                          transactions=transactions)

@accounts_bp.route('/<int:account_id>/close', methods=['POST'])
@login_required
def close_account(account_id):
    account = Account.query.get_or_404(account_id)
    
    # Check if user owns this account
    if account.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('accounts.list_accounts'))
    
    # Check if balance is zero
    if account.balance > 0:
        flash('Please withdraw all funds before closing the account.', 'warning')
        return redirect(url_for('accounts.view_account', account_id=account_id))
    
    account.status = 'closed'
    db.session.commit()
    
    flash('Account closed successfully.', 'success')
    return redirect(url_for('accounts.list_accounts'))

@accounts_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    
    if query:
        accounts = Account.query.filter(
            Account.user_id == current_user.id,
            (Account.account_number.contains(query) | 
             Account.account_type.ilike(f'%{query}%'))
        ).all()
    else:
        accounts = []
    
    return render_template('accounts/search.html', accounts=accounts, query=query)