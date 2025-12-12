# Test Cases Document
## Bank Management System

---

## 1. Authentication Module Test Cases

### TC-AUTH-001: User Registration - Valid Data
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-001 |
| **Title** | User Registration with Valid Data |
| **Module** | Authentication |
| **Priority** | High |
| **Preconditions** | User is not logged in, on registration page |
| **Test Data** | Username: testuser, Email: test@example.com, Password: ValidPass123 |
| **Steps** | 1. Navigate to /auth/register<br>2. Enter username<br>3. Enter email<br>4. Enter password<br>5. Enter confirm password<br>6. Click Register |
| **Expected Result** | User is registered successfully and redirected to login page with success message |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Functional, Integration |

### TC-AUTH-002: User Registration - Duplicate Username
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-002 |
| **Title** | Registration with Existing Username |
| **Module** | Authentication |
| **Priority** | High |
| **Preconditions** | User "testuser" already exists |
| **Test Data** | Username: testuser (duplicate) |
| **Steps** | 1. Navigate to /auth/register<br>2. Enter existing username<br>3. Fill other fields<br>4. Click Register |
| **Expected Result** | Error message "Username already exists" is displayed |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Negative Testing |

### TC-AUTH-003: User Registration - Password Mismatch
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-003 |
| **Title** | Registration with Mismatched Passwords |
| **Module** | Authentication |
| **Priority** | High |
| **Preconditions** | User is on registration page |
| **Test Data** | Password: Pass123, Confirm: Different456 |
| **Steps** | 1. Enter password<br>2. Enter different confirm password<br>3. Click Register |
| **Expected Result** | Error message "Passwords do not match" |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Negative Testing |

### TC-AUTH-004: User Registration - Short Password (Boundary)
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-004 |
| **Title** | Registration with 7-character Password (Below Minimum) |
| **Module** | Authentication |
| **Priority** | High |
| **Preconditions** | User is on registration page |
| **Test Data** | Password: "1234567" (7 characters) |
| **Expected Result** | Error message "Password must be at least 8 characters" |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Boundary Value Analysis |

### TC-AUTH-005: User Registration - Minimum Valid Password (Boundary)
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-005 |
| **Title** | Registration with 8-character Password (At Minimum) |
| **Module** | Authentication |
| **Priority** | High |
| **Test Data** | Password: "12345678" (8 characters) |
| **Expected Result** | Registration succeeds |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Boundary Value Analysis |

### TC-AUTH-006: User Login - Valid Credentials
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-006 |
| **Title** | Login with Valid Credentials |
| **Module** | Authentication |
| **Priority** | High |
| **Preconditions** | User account exists |
| **Test Data** | Username: testuser, Password: TestPassword123 |
| **Steps** | 1. Navigate to /auth/login<br>2. Enter username<br>3. Enter password<br>4. Click Login |
| **Expected Result** | User is logged in and redirected to dashboard |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Functional |

### TC-AUTH-007: User Login - Invalid Password
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-007 |
| **Title** | Login with Wrong Password |
| **Module** | Authentication |
| **Priority** | High |
| **Test Data** | Username: testuser, Password: WrongPassword |
| **Expected Result** | Error message "Invalid username or password" |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Negative Testing |

### TC-AUTH-008: User Login - Non-existent User
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-008 |
| **Title** | Login with Non-existent Username |
| **Module** | Authentication |
| **Priority** | High |
| **Test Data** | Username: nonexistent, Password: anypassword |
| **Expected Result** | Error message "Invalid username or password" |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Negative Testing |

### TC-AUTH-009: User Logout
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-009 |
| **Title** | User Logout |
| **Module** | Authentication |
| **Priority** | High |
| **Preconditions** | User is logged in |
| **Steps** | 1. Click Logout |
| **Expected Result** | User is logged out and redirected to login page |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Functional |

### TC-AUTH-010: Protected Route Access
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-AUTH-010 |
| **Title** | Access Dashboard Without Login |
| **Module** | Authentication |
| **Priority** | High |
| **Preconditions** | User is not logged in |
| **Steps** | 1. Navigate directly to / (dashboard) |
| **Expected Result** | Redirected to login page with message |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Security |

---

## 2. Account Management Test Cases

### TC-ACC-001: Create Savings Account
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-ACC-001 |
| **Title** | Create Savings Account with Initial Deposit |
| **Module** | Account Management |
| **Priority** | High |
| **Preconditions** | User is logged in |
| **Test Data** | Type: Savings, Initial Deposit: $500 |
| **Steps** | 1. Navigate to /accounts/create<br>2. Select Savings<br>3. Enter initial deposit<br>4. Click Create |
| **Expected Result** | Account created with success message, 12-digit account number generated |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Functional |

### TC-ACC-002: Create Account - Zero Deposit
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-ACC-002 |
| **Title** | Create Account with Zero Initial Deposit |
| **Module** | Account Management |
| **Priority** | Medium |
| **Test Data** | Type: Checking, Initial Deposit: $0 |
| **Expected Result** | Account created successfully with $0 balance |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Boundary |

### TC-ACC-003: Create Account - Negative Deposit
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-ACC-003 |
| **Title** | Create Account with Negative Deposit |
| **Module** | Account Management |
| **Priority** | High |
| **Test Data** | Initial Deposit: -$100 |
| **Expected Result** | Error message "cannot be negative" |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Negative, Equivalence Partitioning |

### TC-ACC-004: View Account Details
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-ACC-004 |
| **Title** | View Account Details |
| **Module** | Account Management |
| **Priority** | High |
| **Preconditions** | User has at least one account |
| **Steps** | 1. Navigate to /accounts/<br>2. Click on account |
| **Expected Result** | Account details displayed with balance and recent transactions |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Functional |

### TC-ACC-005: Access Other User's Account
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-ACC-005 |
| **Title** | Attempt to View Another User's Account |
| **Module** | Account Management |
| **Priority** | High |
| **Preconditions** | Another user's account exists |
| **Steps** | 1. Navigate to /accounts/{other_user_account_id} |
| **Expected Result** | Access denied message |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Security |

### TC-ACC-006: Close Account - Zero Balance
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-ACC-006 |
| **Title** | Close Account with Zero Balance |
| **Module** | Account Management |
| **Priority** | Medium |
| **Preconditions** | Account balance is $0 |
| **Expected Result** | Account closed successfully |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Functional |

### TC-ACC-007: Close Account - With Balance
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-ACC-007 |
| **Title** | Close Account with Remaining Balance |
| **Module** | Account Management |
| **Priority** | High |
| **Preconditions** | Account has balance > $0 |
| **Expected Result** | Error message "withdraw all funds before closing" |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Negative |

---

## 3. Transaction Test Cases

### TC-TRX-001: Deposit - Valid Amount
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-TRX-001 |
| **Title** | Deposit Valid Amount |
| **Module** | Transactions |
| **Priority** | High |
| **Preconditions** | User has active account |
| **Test Data** | Amount: $250 |
| **Steps** | 1. Navigate to /transactions/deposit<br>2. Select account<br>3. Enter amount<br>4. Click Deposit |
| **Expected Result** | Balance increases by $250, success message shown |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Functional |

### TC-TRX-002: Deposit - Zero Amount
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-TRX-002 |
| **Title** | Deposit Zero Amount |
| **Module** | Transactions |
| **Priority** | High |
| **Test Data** | Amount: $0 |
| **Expected Result** | Error message "Amount must be positive" |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Boundary, Equivalence Partitioning |

### TC-TRX-003: Deposit - Negative Amount
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-TRX-003 |
| **Title** | Deposit Negative Amount |
| **Module** | Transactions |
| **Priority** | High |
| **Test Data** | Amount: -$100 |
| **Expected Result** | Error message "Amount must be positive" |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Equivalence Partitioning |

### TC-TRX-004: Withdrawal - Valid Amount
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-TRX-004 |
| **Title** | Withdraw Valid Amount |
| **Module** | Transactions |
| **Priority** | High |
| **Preconditions** | Account balance: $1000 |
| **Test Data** | Amount: $200 |
| **Expected Result** | Balance decreases by $200, success message |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Functional |

### TC-TRX-005: Withdrawal - Insufficient Funds
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-TRX-005 |
| **Title** | Withdraw More Than Balance |
| **Module** | Transactions |
| **Priority** | High |
| **Preconditions** | Account balance: $100 |
| **Test Data** | Amount: $500 |
| **Expected Result** | Error message "Insufficient funds" |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Negative |

### TC-TRX-006: Transfer - Valid Transfer
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-TRX-006 |
| **Title** | Transfer Between Accounts |
| **Module** | Transactions |
| **Priority** | High |
| **Preconditions** | Source account has sufficient funds |
| **Test Data** | Amount: $300 |
| **Expected Result** | Source balance decreases, destination increases |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Functional |

### TC-TRX-007: Transfer - Non-existent Recipient
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-TRX-007 |
| **Title** | Transfer to Invalid Account Number |
| **Module** | Transactions |
| **Priority** | High |
| **Test Data** | To Account: 000000000000 |
| **Expected Result** | Error message "Recipient account not found" |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Negative |

### TC-TRX-008: Transfer - Same Account
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-TRX-008 |
| **Title** | Transfer to Same Account |
| **Module** | Transactions |
| **Priority** | Medium |
| **Steps** | Transfer from account to itself |
| **Expected Result** | Error message "Cannot transfer to same account" |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Negative |

---

## 4. Model Unit Test Cases

### TC-MODEL-001: Password Hashing
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-MODEL-001 |
| **Title** | Password is Properly Hashed |
| **Module** | User Model |
| **Priority** | High |
| **Steps** | 1. Create user<br>2. Set password<br>3. Verify hash differs from plain text |
| **Expected Result** | password_hash != plain password |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Unit |

### TC-MODEL-002: Password Verification
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-MODEL-002 |
| **Title** | Password Check Works Correctly |
| **Module** | User Model |
| **Priority** | High |
| **Steps** | 1. Set password<br>2. Check correct password<br>3. Check wrong password |
| **Expected Result** | Correct returns True, wrong returns False |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Unit |

### TC-MODEL-003: Account Number Generation
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-MODEL-003 |
| **Title** | Generate Valid Account Number |
| **Module** | Account Model |
| **Priority** | High |
| **Expected Result** | 12-digit numeric string |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Unit |

### TC-MODEL-004: Transaction Reference Generation
| Field | Value |
|-------|-------|
| **Test Case ID** | TC-MODEL-004 |
| **Title** | Generate Unique Reference Numbers |
| **Module** | Transaction Model |
| **Priority** | Medium |
| **Steps** | Generate 100 reference numbers |
| **Expected Result** | All references are unique |
| **Actual Result** | ✅ PASSED |
| **Test Type** | Unit |

---

## 5. Test Summary

| Module | Total Tests | Passed | Failed | Pass Rate |
|--------|-------------|--------|--------|-----------|
| Authentication | 17 | 17 | 0 | 100% |
| Account Management | 15 | 15 | 0 | 100% |
| Transactions | 17 | 17 | 0 | 100% |
| Models (Unit) | 16 | 16 | 0 | 100% |
| Validators | 27 | 27 | 0 | 100% |
| E2E Tests | 9 | 7 | 2 | 78% |
| **TOTAL** | **101** | **99** | **2** | **98%** |

---

## 6. Coverage Summary

| Module | Statements | Covered | Coverage |
|--------|------------|---------|----------|
| app/__init__.py | 32 | 32 | 100% |
| app/models/ | 89 | 86 | 97% |
| app/routes/ | 406 | 298 | 73% |
| **TOTAL** | **530** | **419** | **79%** |

---

**Document Version:** 1.0  
**Last Updated:** December 2025