from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration Route
    ------------------
    GET: Display registration form
    POST: Process new user registration
    """
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        errors = []
        
        if not username or not email or not password:
            errors.append('All fields are required.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Automatically log in the user after registration
        login_user(user)
        flash('Registration successful! Welcome to Bank Management System.', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login Route
    -----------
    GET: Display login form
    POST: Process login attempt
    
    Flow:
    1. User visits /login
    2. Sees login form
    3. Enters credentials
    4. Clicks submit
    5. Server validates
    6. If valid: redirect to dashboard
    7. If invalid: show error
    """
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    
    # Handle form submission
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Contact support.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            flash('Login successful!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid username or password.', 'danger')

    # GET request: show login form
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        # Update email
        if email and email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already in use.', 'danger')
            else:
                current_user.email = email
                flash('Email updated successfully.', 'success')
        
        # Update password
        if current_password and new_password:
            if current_user.check_password(current_password):
                if len(new_password) >= 8:
                    current_user.set_password(new_password)
                    flash('Password updated successfully.', 'success')
                else:
                    flash('New password must be at least 8 characters.', 'danger')
            else:
                flash('Current password is incorrect.', 'danger')
        
        db.session.commit()
    
    return render_template('auth/profile.html')