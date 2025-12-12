import pytest

class TestPasswordValidation:
    """
    Password Validation Tests using Equivalence Partitioning and Boundary Value Analysis
    
    Rules:
    - Minimum length: 8 characters
    - Maximum length: 128 characters
    
    Equivalence Classes:
    - EC1: Invalid (too short) - length < 8
    - EC2: Valid - 8 <= length <= 128
    - EC3: Invalid (too long) - length > 128
    """
    
    def validate_password_length(self, password):
        """Simple password length validator"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if len(password) > 128:
            return False, "Password must not exceed 128 characters"
        return True, "Valid password"
    
    # Equivalence Partitioning Tests
    @pytest.mark.unit
    def test_ec1_password_too_short(self):
        """EC1: Password too short (invalid)"""
        result, message = self.validate_password_length("short")
        assert result == False
        assert "at least 8" in message
    
    @pytest.mark.unit
    def test_ec2_password_valid_length(self):
        """EC2: Password valid length"""
        result, message = self.validate_password_length("validpassword123")
        assert result == True
    
    @pytest.mark.unit
    def test_ec3_password_too_long(self):
        """EC3: Password too long (invalid)"""
        long_password = "a" * 129
        result, message = self.validate_password_length(long_password)
        assert result == False
        assert "not exceed 128" in message
    
    # Boundary Value Analysis Tests
    @pytest.mark.unit
    def test_boundary_7_characters(self):
        """Boundary: 7 characters (just below minimum)"""
        result, _ = self.validate_password_length("1234567")
        assert result == False
    
    @pytest.mark.unit
    def test_boundary_8_characters(self):
        """Boundary: 8 characters (at minimum)"""
        result, _ = self.validate_password_length("12345678")
        assert result == True
    
    @pytest.mark.unit
    def test_boundary_9_characters(self):
        """Boundary: 9 characters (just above minimum)"""
        result, _ = self.validate_password_length("123456789")
        assert result == True
    
    @pytest.mark.unit
    def test_boundary_127_characters(self):
        """Boundary: 127 characters (just below maximum)"""
        result, _ = self.validate_password_length("a" * 127)
        assert result == True
    
    @pytest.mark.unit
    def test_boundary_128_characters(self):
        """Boundary: 128 characters (at maximum)"""
        result, _ = self.validate_password_length("a" * 128)
        assert result == True
    
    @pytest.mark.unit
    def test_boundary_129_characters(self):
        """Boundary: 129 characters (just above maximum)"""
        result, _ = self.validate_password_length("a" * 129)
        assert result == False


class TestAmountValidation:
    """
    Amount Validation Tests using Equivalence Partitioning and Boundary Value Analysis
    
    Rules:
    - Minimum amount: $0.01
    - Maximum amount: $1,000,000
    
    Equivalence Classes:
    - EC1: Invalid (negative) - amount < 0
    - EC2: Invalid (zero) - amount = 0
    - EC3: Valid - 0.01 <= amount <= 1,000,000
    - EC4: Invalid (too large) - amount > 1,000,000
    """
    
    def validate_amount(self, amount):
        """Simple amount validator"""
        if amount < 0:
            return False, "Amount cannot be negative"
        if amount == 0:
            return False, "Amount must be greater than zero"
        if amount < 0.01:
            return False, "Minimum amount is $0.01"
        if amount > 1000000:
            return False, "Maximum amount is $1,000,000"
        return True, "Valid amount"
    
    # Equivalence Partitioning Tests
    @pytest.mark.unit
    def test_ec1_negative_amount(self):
        """EC1: Negative amount (invalid)"""
        result, message = self.validate_amount(-100)
        assert result == False
        assert "negative" in message
    
    @pytest.mark.unit
    def test_ec2_zero_amount(self):
        """EC2: Zero amount (invalid)"""
        result, message = self.validate_amount(0)
        assert result == False
        assert "greater than zero" in message
    
    @pytest.mark.unit
    def test_ec3_valid_amount(self):
        """EC3: Valid amount"""
        result, _ = self.validate_amount(500)
        assert result == True
    
    @pytest.mark.unit
    def test_ec4_amount_too_large(self):
        """EC4: Amount too large (invalid)"""
        result, message = self.validate_amount(1000001)
        assert result == False
        assert "Maximum" in message
    
    # Boundary Value Analysis Tests
    @pytest.mark.unit
    def test_boundary_negative_one_cent(self):
        """Boundary: -$0.01 (invalid)"""
        result, _ = self.validate_amount(-0.01)
        assert result == False
    
    @pytest.mark.unit
    def test_boundary_zero(self):
        """Boundary: $0.00 (invalid)"""
        result, _ = self.validate_amount(0)
        assert result == False
    
    @pytest.mark.unit
    def test_boundary_one_cent(self):
        """Boundary: $0.01 (minimum valid)"""
        result, _ = self.validate_amount(0.01)
        assert result == True
    
    @pytest.mark.unit
    def test_boundary_two_cents(self):
        """Boundary: $0.02 (just above minimum)"""
        result, _ = self.validate_amount(0.02)
        assert result == True
    
    @pytest.mark.unit
    def test_boundary_just_below_max(self):
        """Boundary: $999,999.99 (just below maximum)"""
        result, _ = self.validate_amount(999999.99)
        assert result == True
    
    @pytest.mark.unit
    def test_boundary_at_max(self):
        """Boundary: $1,000,000 (at maximum)"""
        result, _ = self.validate_amount(1000000)
        assert result == True
    
    @pytest.mark.unit
    def test_boundary_above_max(self):
        """Boundary: $1,000,000.01 (just above maximum)"""
        result, _ = self.validate_amount(1000000.01)
        assert result == False


class TestAccountNumberValidation:
    """
    Account Number Validation Tests
    
    Rules:
    - Must be exactly 12 digits
    - Must contain only numbers
    """
    
    def validate_account_number(self, account_number):
        """Validate account number format"""
        if not account_number:
            return False, "Account number is required"
        if not account_number.isdigit():
            return False, "Account number must contain only digits"
        if len(account_number) != 12:
            return False, "Account number must be exactly 12 digits"
        return True, "Valid account number"
    
    @pytest.mark.unit
    def test_valid_account_number(self):
        """Test valid 12-digit account number"""
        result, _ = self.validate_account_number("123456789012")
        assert result == True
    
    @pytest.mark.unit
    def test_account_number_too_short(self):
        """Test account number with less than 12 digits"""
        result, message = self.validate_account_number("12345678901")
        assert result == False
        assert "12 digits" in message
    
    @pytest.mark.unit
    def test_account_number_too_long(self):
        """Test account number with more than 12 digits"""
        result, message = self.validate_account_number("1234567890123")
        assert result == False
        assert "12 digits" in message
    
    @pytest.mark.unit
    def test_account_number_with_letters(self):
        """Test account number containing letters"""
        result, message = self.validate_account_number("12345678901a")
        assert result == False
        assert "only digits" in message
    
    @pytest.mark.unit
    def test_account_number_with_special_chars(self):
        """Test account number with special characters"""
        result, message = self.validate_account_number("123456-78901")
        assert result == False
    
    @pytest.mark.unit
    def test_empty_account_number(self):
        """Test empty account number"""
        result, message = self.validate_account_number("")
        assert result == False
    
    @pytest.mark.unit
    def test_none_account_number(self):
        """Test None account number"""
        result, message = self.validate_account_number(None)
        assert result == False