"""
Run the Test Automation Dashboard
"""
import os
import sys

# Add test_dashboard to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'test_dashboard'))

from test_dashboard.app import app

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Test Automation Dashboard")
    print("=" * 50)
    print("📊 Dashboard URL: http://localhost:5050")
    print("=" * 50)
    app.run(debug=True, port=5050)