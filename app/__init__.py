# app/__init__.py
# ===============
# Application factory - creates and configures the Flask app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions
# Create database instance (not bound to app yet)
db = SQLAlchemy()
login_manager = LoginManager()
# Tracking who is logged in , managing sessions, protecting routes that require login

def create_app():

    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'grpwoubg421fweqfqegwrg'  
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # If someone tries to access a protected page without logging in,redirect them to the 'auth.login' route
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.accounts import accounts_bp
    from app.routes.transactions import transactions_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(admin_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))
# This decorator registers the function with Flask-Login                    
# Flask-Login will call this function to load a user from the database