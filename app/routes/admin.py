from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_users = User.query.count()
    total_accounts = Account.query.count()
    total_transactions = Transaction.query.count()
    total_balance = db.session.query(db.func.sum(Account.balance)).scalar() or 0
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Recent transactions
    recent_transactions = Transaction.query.order_by(
        Transaction.timestamp.desc()
    ).limit(10).all()
    
    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_accounts=total_accounts,
                          total_transactions=total_transactions,
                          total_balance=total_balance,
                          recent_users=recent_users,
                          recent_transactions=recent_transactions)

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    accounts = Account.query.filter_by(user_id=user_id).all()
    return render_template('admin/user_detail.html', user=user, accounts=accounts)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.list_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role not in ['customer', 'teller', 'admin']:
        flash('Invalid role.', 'danger')
        return redirect(url_for('admin.view_user', user_id=user_id))
    
    # Prevent admin from changing their own role
    if user.id == current_user.id:
        flash('You cannot change your own role.', 'danger')
        return redirect(url_for('admin.view_user', user_id=user_id))
    
    user.role = new_role
    db.session.commit()
    
    flash(f'User {user.username} role changed to {new_role}.', 'success')
    return redirect(url_for('admin.view_user', user_id=user_id))

@admin_bp.route('/accounts')
@login_required
@admin_required
def list_accounts():
    accounts = Account.query.order_by(Account.created_at.desc()).all()
    return render_template('admin/accounts.html', accounts=accounts)

@admin_bp.route('/accounts/<int:account_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_account_status(account_id):
    account = Account.query.get_or_404(account_id)
    
    if account.status == 'active':
        account.status = 'frozen'
        flash(f'Account {account.account_number} has been frozen.', 'warning')
    elif account.status == 'frozen':
        account.status = 'active'
        flash(f'Account {account.account_number} has been unfrozen.', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.list_accounts'))

@admin_bp.route('/transactions')
@login_required
@admin_required
def list_transactions():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.order_by(
        Transaction.timestamp.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/transactions.html', transactions=transactions)

@admin_bp.route('/search')
@login_required
@admin_required
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'users')
    results = []
    
    if query:
        if search_type == 'users':
            results = User.query.filter(
                User.username.contains(query) | 
                User.email.contains(query)
            ).all()
        elif search_type == 'accounts':
            results = Account.query.filter(
                Account.account_number.contains(query)
            ).all()
        elif search_type == 'transactions':
            results = Transaction.query.filter(
                Transaction.reference_number.contains(query)
            ).all()
    
    return render_template('admin/search.html', 
                          results=results, 
                          query=query, 
                          search_type=search_type)