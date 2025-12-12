from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import func
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from test_dashboard.models import db, TestRun, TestResult, CoverageReport


def create_dashboard_app():
    app = Flask(__name__)
    
    # Configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = 'dashboard-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "test_dashboard.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    # ==================== ROUTES ====================
    
    @app.route('/')
    def dashboard():
        """Main dashboard page"""
        # Get latest test run
        latest_run = TestRun.query.order_by(TestRun.start_time.desc()).first()
        
        # Get last 10 test runs for trend
        recent_runs = TestRun.query.order_by(TestRun.start_time.desc()).limit(10).all()
        recent_runs.reverse()  # Oldest first for chart
        
        # Get recent failures
        recent_failures = []
        if latest_run:
            recent_failures = TestResult.query.filter_by(
                run_id=latest_run.id,
                status='failed'
            ).order_by(TestResult.timestamp.desc()).limit(10).all()
        
        # Calculate stats
        total_runs = TestRun.query.count()
        
        # Average pass rate (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_runs_stats = TestRun.query.filter(
            TestRun.start_time >= thirty_days_ago
        ).all()
        
        avg_pass_rate = 0
        if recent_runs_stats:
            avg_pass_rate = sum(r.pass_rate for r in recent_runs_stats) / len(recent_runs_stats)
        
        return render_template('dashboard/index.html',
                             latest_run=latest_run,
                             recent_runs=recent_runs,
                             recent_failures=recent_failures,
                             total_runs=total_runs,
                             avg_pass_rate=round(avg_pass_rate, 2))
    
    @app.route('/runs')
    def test_runs():
        """List all test runs"""
        page = request.args.get('page', 1, type=int)
        runs = TestRun.query.order_by(TestRun.start_time.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        return render_template('dashboard/runs.html', runs=runs)
    
    @app.route('/runs/<int:run_id>')
    def run_details(run_id):
        """View details of a specific test run"""
        run = TestRun.query.get_or_404(run_id)
        
        # Get all results for this run
        results = TestResult.query.filter_by(run_id=run_id).order_by(
            TestResult.status.desc(),  # Failed first
            TestResult.test_name
        ).all()
        
        # Get coverage for this run
        coverage = CoverageReport.query.filter_by(run_id=run_id).all()
        
        # Group by status
        passed_tests = [r for r in results if r.status == 'passed']
        failed_tests = [r for r in results if r.status == 'failed']
        skipped_tests = [r for r in results if r.status == 'skipped']
        
        return render_template('dashboard/run_details.html',
                             run=run,
                             results=results,
                             coverage=coverage,
                             passed_tests=passed_tests,
                             failed_tests=failed_tests,
                             skipped_tests=skipped_tests)
    
    @app.route('/failures')
    def failures():
        """View all recent failures"""
        page = request.args.get('page', 1, type=int)
        failures = TestResult.query.filter_by(status='failed').order_by(
            TestResult.timestamp.desc()
        ).paginate(page=page, per_page=50, error_out=False)
        
        return render_template('dashboard/failures.html', failures=failures)
    
    @app.route('/trends')
    def trends():
        """View test trends over time"""
        # Get runs from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        runs = TestRun.query.filter(
            TestRun.start_time >= thirty_days_ago
        ).order_by(TestRun.start_time).all()
        
        return render_template('dashboard/trends.html', runs=runs)
    
    # ==================== API ENDPOINTS ====================
    
    @app.route('/api/summary')
    def api_summary():
        """Get summary statistics"""
        latest_run = TestRun.query.order_by(TestRun.start_time.desc()).first()
        
        if not latest_run:
            return jsonify({
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'pass_rate': 0,
                'coverage': 0
            })
        
        return jsonify({
            'total_tests': latest_run.total_tests,
            'passed': latest_run.passed,
            'failed': latest_run.failed,
            'skipped': latest_run.skipped,
            'pass_rate': latest_run.pass_rate,
            'coverage': latest_run.coverage,
            'duration': latest_run.duration,
            'last_run': latest_run.start_time.isoformat()
        })
    
    @app.route('/api/trends')
    def api_trends():
        """Get trend data for charts"""
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        runs = TestRun.query.filter(
            TestRun.start_time >= start_date
        ).order_by(TestRun.start_time).all()
        
        return jsonify({
            'dates': [r.start_time.strftime('%Y-%m-%d %H:%M') for r in runs],
            'passed': [r.passed for r in runs],
            'failed': [r.failed for r in runs],
            'total': [r.total_tests for r in runs],
            'pass_rate': [r.pass_rate for r in runs],
            'coverage': [r.coverage for r in runs],
            'duration': [r.duration for r in runs]
        })
    
    @app.route('/api/recent-failures')
    def api_recent_failures():
        """Get recent test failures"""
        limit = request.args.get('limit', 10, type=int)
        
        failures = TestResult.query.filter_by(status='failed').order_by(
            TestResult.timestamp.desc()
        ).limit(limit).all()
        
        return jsonify([{
            'test_name': f.test_name,
            'test_file': f.test_file,
            'error_message': f.error_message,
            'timestamp': f.timestamp.isoformat(),
            'duration': f.duration
        } for f in failures])
    
    @app.route('/api/coverage')
    def api_coverage():
        """Get latest coverage data"""
        latest_run = TestRun.query.order_by(TestRun.start_time.desc()).first()
        
        if not latest_run:
            return jsonify([])
        
        coverage = CoverageReport.query.filter_by(run_id=latest_run.id).all()
        
        return jsonify([{
            'module': c.module_name,
            'statements': c.statements,
            'missing': c.missing,
            'coverage': c.coverage_percent
        } for c in coverage])
    
    return app


# Create app instance
app = create_dashboard_app()

if __name__ == '__main__':
    app.run(debug=True, port=5050)