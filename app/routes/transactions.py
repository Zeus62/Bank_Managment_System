from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.account import Account
from app.models.transaction import Transaction

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@transactions_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    accounts = Account.query.filter_by(
        user_id=current_user.id, 
        status='active'
    ).all()
    
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = request.form.get('amount')
        description = request.form.get('description', 'Deposit')
        
        try:
            account_id = int(account_id)
            amount = float(amount)
        except (ValueError, TypeError):
            flash('Invalid input.', 'danger')
            return render_template('transactions/deposit.html', accounts=accounts)
        
        # Validate
        account = Account.query.get(account_id)
        
        if not account or account.user_id != current_user.id:
            flash('Invalid account.', 'danger')
            return render_template('transactions/deposit.html', accounts=accounts)
        
        if amount <= 0:
            flash('Amount must be positive.', 'danger')
            return render_template('transactions/deposit.html', accounts=accounts)
        
        # Perform deposit
        account.balance += amount
        
        transaction = Transaction(
            account_id=account_id,
            transaction_type='deposit',
            amount=amount,
            description=description,
            reference_number=Transaction.generate_reference()
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Successfully deposited ${amount:.2f}', 'success')
        return redirect(url_for('accounts.view_account', account_id=account_id))
    
    return render_template('transactions/deposit.html', accounts=accounts)

@transactions_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    accounts = Account.query.filter_by(
        user_id=current_user.id, 
        status='active'
    ).all()
    
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = request.form.get('amount')
        description = request.form.get('description', 'Withdrawal')
        
        try:
            account_id = int(account_id)
            amount = float(amount)
        except (ValueError, TypeError):
            flash('Invalid input.', 'danger')
            return render_template('transactions/withdraw.html', accounts=accounts)
        
        # Validate
        account = Account.query.get(account_id)
        
        if not account or account.user_id != current_user.id:
            flash('Invalid account.', 'danger')
            return render_template('transactions/withdraw.html', accounts=accounts)
        
        if amount <= 0:
            flash('Amount must be positive.', 'danger')
            return render_template('transactions/withdraw.html', accounts=accounts)
        
        if account.balance < amount:
            flash('Insufficient funds.', 'danger')
            return render_template('transactions/withdraw.html', accounts=accounts)
        
        # Perform withdrawal
        account.balance -= amount
        
        transaction = Transaction(
            account_id=account_id,
            transaction_type='withdrawal',
            amount=amount,
            description=description,
            reference_number=Transaction.generate_reference()
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Successfully withdrew ${amount:.2f}', 'success')
        return redirect(url_for('accounts.view_account', account_id=account_id))
    
    return render_template('transactions/withdraw.html', accounts=accounts)

@transactions_bp.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    accounts = Account.query.filter_by(
        user_id=current_user.id, 
        status='active'
    ).all()
    
    if request.method == 'POST':
        from_account_id = request.form.get('from_account_id')
        to_account_number = request.form.get('to_account_number')
        amount = request.form.get('amount')
        description = request.form.get('description', 'Transfer')
        
        try:
            from_account_id = int(from_account_id)
            amount = float(amount)
        except (ValueError, TypeError):
            flash('Invalid input.', 'danger')
            return render_template('transactions/transfer.html', accounts=accounts)
        
        # Validate source account
        from_account = Account.query.get(from_account_id)
        
        if not from_account or from_account.user_id != current_user.id:
            flash('Invalid source account.', 'danger')
            return render_template('transactions/transfer.html', accounts=accounts)
        
        # Validate destination account
        to_account = Account.query.filter_by(account_number=to_account_number).first()
        
        if not to_account:
            flash('Recipient account not found.', 'danger')
            return render_template('transactions/transfer.html', accounts=accounts)
        
        if to_account.status != 'active':
            flash('Recipient account is not active.', 'danger')
            return render_template('transactions/transfer.html', accounts=accounts)
        
        if amount <= 0:
            flash('Amount must be positive.', 'danger')
            return render_template('transactions/transfer.html', accounts=accounts)
        
        if from_account.balance < amount:
            flash('Insufficient funds.', 'danger')
            return render_template('transactions/transfer.html', accounts=accounts)
        
        if from_account.id == to_account.id:
            flash('Cannot transfer to the same account.', 'danger')
            return render_template('transactions/transfer.html', accounts=accounts)
        
        # Perform transfer
        reference = Transaction.generate_reference()
        
        from_account.balance -= amount
        to_account.balance += amount
        
        # Outgoing transaction
        outgoing = Transaction(
            account_id=from_account_id,
            transaction_type='transfer',
            amount=-amount,
            description=f'Transfer to {to_account_number}: {description}',
            recipient_account=to_account_number,
            reference_number=reference
        )
        
        # Incoming transaction
        incoming = Transaction(
            account_id=to_account.id,
            transaction_type='transfer',
            amount=amount,
            description=f'Transfer from {from_account.account_number}: {description}',
            recipient_account=from_account.account_number,
            reference_number=reference + '-IN'
        )
        
        db.session.add(outgoing)
        db.session.add(incoming)
        db.session.commit()
        
        flash(f'Successfully transferred ${amount:.2f}', 'success')
        return redirect(url_for('accounts.view_account', account_id=from_account_id))
    
    return render_template('transactions/transfer.html', accounts=accounts)

@transactions_bp.route('/history')
@login_required
def history():
    # Get all user's account IDs
    account_ids = [a.id for a in current_user.accounts]
    
    # Get all transactions
    transactions = Transaction.query.filter(
        Transaction.account_id.in_(account_ids)
    ).order_by(Transaction.timestamp.desc()).all()
    
    return render_template('transactions/history.html', transactions=transactions)

@transactions_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    transaction_type = request.args.get('type', '')
    
    account_ids = [a.id for a in current_user.accounts]
    
    transactions_query = Transaction.query.filter(
        Transaction.account_id.in_(account_ids)
    )
    
    if query:
        transactions_query = transactions_query.filter(
            (Transaction.reference_number.contains(query)) |
            (Transaction.description.contains(query))
        )
    
    if transaction_type:
        transactions_query = transactions_query.filter(
            Transaction.transaction_type == transaction_type
        )
    
    transactions = transactions_query.order_by(
        Transaction.timestamp.desc()
    ).all()
    
    return render_template('transactions/search.html', 
                          transactions=transactions, 
                          query=query,
                          transaction_type=transaction_type)