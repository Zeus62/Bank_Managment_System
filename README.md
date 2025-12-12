# Bank Management System

A comprehensive Python-based banking application with a modern web interface, automated testing dashboard, and comprehensive account management features.

## 🎯 Features

### Banking Operations
- **User Authentication & Management**
  - Secure login and registration
  - User profile management
  - Role-based access control (Admin/User)

- **Account Management**
  - Create and manage multiple accounts
  - Account balance tracking
  - Account search and filtering
  - Account history

- **Transactions**
  - Deposit funds
  - Withdraw funds
  - Transfer between accounts
  - Transaction history and search
  - Transaction reporting

- **Admin Dashboard**
  - Manage users and accounts
  - View transaction logs
  - Search and filter capabilities
  - Admin-specific controls

### Testing & Quality Assurance
- **Automated Testing Dashboard**
  - Real-time test execution monitoring
  - Pass/fail rate tracking
  - Test coverage analysis
  - Failure tracking and reporting
  - Historical trends and analytics
  - 30-day performance trends

- **Comprehensive Test Suite**
  - Unit tests for models and validators
  - Integration tests for routes
  - End-to-end user flow testing
  - 85%+ code coverage

## 📋 Project Structure

```
Bank_Managment_System/
├── app/
│   ├── models/                 # Database models
│   │   ├── user.py
│   │   ├── account.py
│   │   └── transaction.py
│   ├── routes/                 # API endpoints
│   │   ├── auth.py
│   │   ├── accounts.py
│   │   ├── transactions.py
│   │   ├── admin.py
│   │   ├── dashboard.py
│   │   └── ...
│   ├── services/               # Business logic
│   ├── templates/              # HTML templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── accounts/
│   │   ├── transactions/
│   │   ├── admin/
│   │   ├── dashboard/
│   │   └── ...
│   ├── static/                 # CSS, JS, images
│   │   ├── css/
│   │   └── js/
│   └── __init__.py
├── test_dashboard/             # Testing dashboard application
│   ├── app.py
│   ├── models.py
│   ├── templates/
│   └── static/
├── tests/                      # Test suites
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── conftest.py
│   └── pytest.ini
├── docs/                       # Documentation
│   ├── TEST_PLAN.md
│   ├── TEST_CASES.md
│   └── TEST_REPORT.md
├── requirements.txt            # Python dependencies
├── run.py                      # Main application entry point
├── run_dashboard.py            # Testing dashboard entry point
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Bank_Managment_System.git
   cd Bank_Managment_System
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database** (if needed)
   ```bash
   python create_admin.py
   ```

### Running the Application

**Main Banking Application**
```bash
python run.py
```
Access at: `http://localhost:5000`

**Testing Dashboard**
```bash
python run_dashboard.py
```
Access at: `http://localhost:5050`

## 🧪 Testing

### Running Tests

**Run all tests**
```bash
pytest
```

**Run specific test suite**
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/
```

**Run tests with coverage report**
```bash
pytest --cov=app --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

### Test Dashboard Features
- **Real-time Monitoring**: Watch test execution in progress
- **Pass Rate Tracking**: Visual representation of test success rates
- **Coverage Analysis**: Module-level code coverage statistics
- **Failure Tracking**: Detailed failure information with error messages
- **Historical Trends**: 30-day performance analytics
- **Performance Metrics**: Test execution time tracking

## 📊 Dashboard Features

### Main Dashboard (Banking)
- Account overview
- Recent transactions
- Quick statistics
- Account balance

### Admin Dashboard
- User management
- Account oversight
- Transaction logs
- Search and filtering

### Testing Dashboard
- Test run history
- Pass/fail statistics
- Coverage reports
- Failure analysis
- Trend charts
- Performance metrics

## 🔐 Security Features
- Password hashing and validation
- Role-based access control
- Secure session management
- Input validation
- Transaction logging

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite
- **Testing**: pytest
- **Coverage**: pytest-cov

### Frontend
- **HTML5** with Jinja2 templating
- **Bootstrap 5.3.0** for responsive design
- **Chart.js** for data visualization
- **Vanilla JavaScript** for interactivity

### Tools & Libraries
- SQLAlchemy (ORM)
- WerkzeugSecurity (password hashing)
- Flask-WTF (form handling)
- pytest-fixtures (testing)

## 📈 Key Metrics

- **Test Coverage**: 85%+
- **Total Tests**: 50+
- **Lines of Code**: 2000+
- **Response Time**: <200ms average
- **Database Queries**: Optimized with caching

## 📝 Documentation

Detailed documentation available in the `docs/` directory:
- `TEST_PLAN.md` - Testing strategy and methodology
- `TEST_CASES.md` - Comprehensive test case documentation
- `TEST_REPORT.md` - Detailed testing results and metrics

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Ahmed Esmat**
- GitHub: [@Zeus62](https://github.com/Zeus62)
- Email: ahmed.esmatx@example.com

## 📞 Support

For support, email ahmed.esmatx@gmail.com or open an issue in the repository.

## 🎓 Learning Resources

This project demonstrates:
- Full-stack Python web development
- Modern testing practices
- Dashboard design and implementation
- Database design and ORM usage
- RESTful API design
- Frontend framework integration

---

**Last Updated**: December 2025
