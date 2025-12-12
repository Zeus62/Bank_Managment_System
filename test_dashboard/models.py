from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TestRun(db.Model):
    """Represents a single test execution run"""
    __tablename__ = 'test_runs'
    
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.String(50), unique=True, nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_tests = db.Column(db.Integer, default=0)
    passed = db.Column(db.Integer, default=0)
    failed = db.Column(db.Integer, default=0)
    skipped = db.Column(db.Integer, default=0)
    errors = db.Column(db.Integer, default=0)
    duration = db.Column(db.Float, default=0.0)
    coverage = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='running')  # running, passed, failed
    
    # Relationship with test results
    results = db.relationship('TestResult', backref='test_run', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, run_id):
        self.run_id = run_id
        self.start_time = datetime.utcnow()
    
    @property
    def pass_rate(self):
        if self.total_tests > 0:
            return round((self.passed / self.total_tests) * 100, 2)
        return 0
    
    def __repr__(self):
        return f'<TestRun {self.run_id}>'


class TestResult(db.Model):
    """Represents individual test case result"""
    __tablename__ = 'test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('test_runs.id'), nullable=False)
    test_name = db.Column(db.String(300), nullable=False)
    test_file = db.Column(db.String(200))
    test_class = db.Column(db.String(100))
    status = db.Column(db.String(20), nullable=False)  # passed, failed, skipped, error
    duration = db.Column(db.Float, default=0.0)
    error_message = db.Column(db.Text)
    stack_trace = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, run_id, test_name, status, duration=0.0, test_file=None, 
                 test_class=None, error_message=None, stack_trace=None):
        self.run_id = run_id
        self.test_name = test_name
        self.status = status
        self.duration = duration
        self.test_file = test_file
        self.test_class = test_class
        self.error_message = error_message
        self.stack_trace = stack_trace
    
    def __repr__(self):
        return f'<TestResult {self.test_name}: {self.status}>'


class CoverageReport(db.Model):
    """Stores coverage information per module"""
    __tablename__ = 'coverage_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('test_runs.id'), nullable=False)
    module_name = db.Column(db.String(200), nullable=False)
    statements = db.Column(db.Integer, default=0)
    missing = db.Column(db.Integer, default=0)
    coverage_percent = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<CoverageReport {self.module_name}: {self.coverage_percent}%>'