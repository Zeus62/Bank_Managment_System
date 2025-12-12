# Test Plan Document
## Bank Management System

---

### 1. Introduction

#### 1.1 Purpose
This document describes the test plan for the Bank Management System, a web application built with Flask and SQLite. The purpose of this test plan is to outline the testing strategy, scope, resources, and schedule for testing activities.

#### 1.2 Project Overview
The Bank Management System is a web-based application that allows users to:
- Register and authenticate
- Create and manage bank accounts
- Perform transactions (deposits, withdrawals, transfers)
- View transaction history
- Admin users can manage users and accounts

#### 1.3 References
- Project Requirements Document
- Flask Documentation
- SQLite Documentation
- Selenium Documentation

---

### 2. Test Strategy

#### 2.1 Testing Levels

| Level | Description | Tools |
|-------|-------------|-------|
| Unit Testing | Test individual functions and methods | pytest |
| Integration Testing | Test route handlers and database interactions | pytest, Flask test client |
| End-to-End Testing | Test complete user workflows | Selenium WebDriver |

#### 2.2 Testing Types

| Type | Description | Coverage Target |
|------|-------------|-----------------|
| Functional Testing | Verify features work as expected | 100% of requirements |
| Boundary Value Testing | Test edge cases and limits | All input fields |
| Equivalence Partitioning | Test representative values from each class | All input validations |
| Security Testing | Test authentication and authorization | All protected routes |
| Regression Testing | Ensure new changes don't break existing features | Full test suite |

#### 2.3 Test Design Techniques Applied

1. **Equivalence Partitioning**
   - Password validation (too short, valid, too long)
   - Amount validation (negative, zero, valid, exceeds limit)
   - Account number validation

2. **Boundary Value Analysis**
   - Password length: 7, 8, 9, 127, 128, 129 characters
   - Transaction amounts: -0.01, 0, 0.01, 999999.99, 1000000, 1000000.01

3. **Decision Table Testing**
   - Login scenarios (valid/invalid username, valid/invalid password)
   - Transfer scenarios (sufficient funds, valid recipient, etc.)

4. **State Transition Testing**
   - Account states: active → frozen → active, active → closed

---

### 3. Test Scope

#### 3.1 Features to be Tested

| Module | Features | Priority |
|--------|----------|----------|
| Authentication | Register, Login, Logout, Profile | High |
| Account Management | Create, View, Close, Search | High |
| Transactions | Deposit, Withdraw, Transfer, History | High |
| Admin Panel | User Management, Account Management | Medium |
| Search | Account Search, Transaction Search | Medium |

#### 3.2 Features Not to be Tested
- Performance testing (out of scope)
- Load testing (out of scope)
- Mobile responsiveness (manual testing only)

---

### 4. Test Environment

#### 4.1 Hardware Requirements
- Computer with minimum 4GB RAM
- 500MB free disk space

#### 4.2 Software Requirements
| Software | Version |
|----------|---------|
| Python | 3.13.0 |
| Flask | 3.x |
| SQLite | 3.x |
| pytest | 9.x |
| Selenium | 4.x |
| Chrome Browser | Latest |
| ChromeDriver | Latest |

#### 4.3 Test Database
- SQLite database for testing
- Separate test database: `test_bank.db`
- Database is reset before each test run

---

### 5. Test Schedule

| Phase | Activities | Duration |
|-------|------------|----------|
| Test Planning | Create test plan, identify test cases | 1 day |
| Test Case Development | Write test cases, create test scripts | 2 days |
| Test Environment Setup | Configure tools, create fixtures | 1 day |
| Test Execution | Run all tests, document results | 2 days |
| Test Reporting | Generate reports, analyze coverage | 1 day |

---

### 6. Test Deliverables

1. ✅ Test Plan Document (this document)
2. ✅ Test Cases Document
3. ✅ Test Scripts (pytest files)
4. ✅ Test Execution Report
5. ✅ Code Coverage Report
6. ✅ Defect Report (if any)

---

### 7. Entry and Exit Criteria

#### 7.1 Entry Criteria
- All code is committed to repository
- Test environment is set up
- Test data is prepared

#### 7.2 Exit Criteria
- All planned test cases executed
- Code coverage >= 75%
- No critical or high severity bugs open
- All test documentation complete

---

### 8. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Browser compatibility issues | Medium | Medium | Use headless browser for CI |
| Database connection issues | Low | High | Use separate test database |
| Flaky E2E tests | High | Medium | Add proper waits and retries |
| Insufficient test coverage | Medium | High | Regular coverage reports |

---

### 9. Approvals

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Project Lead | _____________ | _____________ | _____________ |
| QA Lead | _____________ | _____________ | _____________ |
| Developer | _____________ | _____________ | _____________ |

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Author:** Bank Management System Team