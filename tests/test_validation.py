"""
Tests for Input Validation
===========================

Tests for validation functions.
"""

import unittest
from horecabot.core.validation import (
    validate_phone, validate_email, validate_date, validate_time,
    validate_integer, validate_float, validate_rating,
    sanitize_input, ValidationError, ErrorHandler, ErrorType
)
from datetime import date, time


class TestPhoneValidation(unittest.TestCase):
    """Tests for phone validation"""
    
    def test_valid_phone_formats(self):
        """Test various valid phone formats"""
        valid_phones = [
            "+79991234567",
            "89991234567",
            "79991234567",
            "+7 999 123 45 67",
            "8 (999) 123-45-67",
        ]
        
        for phone in valid_phones:
            valid, error = validate_phone(phone)
            self.assertTrue(valid, f"Phone {phone} should be valid")
            self.assertIsNone(error)
    
    def test_invalid_phone_formats(self):
        """Test invalid phone formats"""
        invalid_phones = [
            "invalid",
            "123",
            "+1234567890",  # Wrong country code
            "79991234",     # Too short
        ]
        
        for phone in invalid_phones:
            valid, error = validate_phone(phone)
            self.assertFalse(valid, f"Phone {phone} should be invalid")
            self.assertIsNotNone(error)


class TestEmailValidation(unittest.TestCase):
    """Tests for email validation"""
    
    def test_valid_emails(self):
        """Test valid email addresses"""
        valid_emails = [
            "user@example.com",
            "test.user@example.co.uk",
            "user+tag@example.com",
        ]
        
        for email in valid_emails:
            valid, error = validate_email(email)
            self.assertTrue(valid, f"Email {email} should be valid")
            self.assertIsNone(error)
    
    def test_invalid_emails(self):
        """Test invalid email addresses"""
        invalid_emails = [
            "invalid",
            "@example.com",
            "user@",
            "user @example.com",
        ]
        
        for email in invalid_emails:
            valid, error = validate_email(email)
            self.assertFalse(valid, f"Email {email} should be invalid")
            self.assertIsNotNone(error)


class TestDateValidation(unittest.TestCase):
    """Tests for date validation"""
    
    def test_valid_future_date(self):
        """Test valid future date"""
        from datetime import datetime, timedelta
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
        
        valid, error, parsed_date = validate_date(tomorrow)
        self.assertTrue(valid)
        self.assertIsNone(error)
        self.assertIsNotNone(parsed_date)
    
    def test_invalid_past_date(self):
        """Test that past dates are invalid"""
        from datetime import datetime, timedelta
        
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
        
        valid, error, parsed_date = validate_date(yesterday)
        self.assertFalse(valid)
        self.assertIsNotNone(error)
    
    def test_invalid_date_format(self):
        """Test invalid date format"""
        valid, error, parsed_date = validate_date("invalid")
        self.assertFalse(valid)
        self.assertIsNotNone(error)


class TestIntegerValidation(unittest.TestCase):
    """Tests for integer validation"""
    
    def test_valid_integer(self):
        """Test valid integer"""
        valid, error, value = validate_integer("42")
        self.assertTrue(valid)
        self.assertIsNone(error)
        self.assertEqual(value, 42)
    
    def test_integer_range(self):
        """Test integer range validation"""
        valid, error, value = validate_integer("5", min_value=1, max_value=10)
        self.assertTrue(valid)
        self.assertEqual(value, 5)
        
        valid, error, value = validate_integer("15", min_value=1, max_value=10)
        self.assertFalse(valid)
        self.assertIsNotNone(error)
    
    def test_invalid_integer(self):
        """Test invalid integer"""
        valid, error, value = validate_integer("not a number")
        self.assertFalse(valid)
        self.assertIsNotNone(error)


class TestFloatValidation(unittest.TestCase):
    """Tests for float validation"""
    
    def test_valid_float(self):
        """Test valid float"""
        valid, error, value = validate_float("42.5")
        self.assertTrue(valid)
        self.assertEqual(value, 42.5)
    
    def test_float_with_comma(self):
        """Test float with comma separator"""
        valid, error, value = validate_float("42,5")
        self.assertTrue(valid)
        self.assertEqual(value, 42.5)
    
    def test_float_range(self):
        """Test float range validation"""
        valid, error, value = validate_float("5.5", min_value=1.0, max_value=10.0)
        self.assertTrue(valid)
        
        valid, error, value = validate_float("15.5", min_value=1.0, max_value=10.0)
        self.assertFalse(valid)


class TestRatingValidation(unittest.TestCase):
    """Tests for rating validation"""
    
    def test_valid_ratings(self):
        """Test valid ratings"""
        for rating in ["1", "2", "3", "4", "5"]:
            valid, error, value = validate_rating(rating)
            self.assertTrue(valid, f"Rating {rating} should be valid")
            self.assertIsNone(error)
    
    def test_invalid_ratings(self):
        """Test invalid ratings"""
        for rating in ["0", "6", "10", "invalid"]:
            valid, error, value = validate_rating(rating)
            self.assertFalse(valid, f"Rating {rating} should be invalid")
            self.assertIsNotNone(error)


class TestSanitizeInput(unittest.TestCase):
    """Tests for input sanitization"""
    
    def test_sanitize_html(self):
        """Test HTML tag removal"""
        input_text = "<script>alert('xss')</script>Hello"
        sanitized = sanitize_input(input_text)
        self.assertNotIn("<script>", sanitized)
        self.assertIn("Hello", sanitized)
    
    def test_sanitize_whitespace(self):
        """Test whitespace trimming"""
        input_text = "  Hello  "
        sanitized = sanitize_input(input_text)
        self.assertEqual(sanitized, "Hello")


class TestErrorHandler(unittest.TestCase):
    """Tests for ErrorHandler"""
    
    def test_format_error(self):
        """Test error formatting"""
        message = ErrorHandler.format_error(ErrorType.INVALID_FORMAT)
        self.assertIn("❌", message)
        
        message = ErrorHandler.format_error(
            ErrorType.INVALID_FORMAT,
            details="Provide DD.MM.YYYY"
        )
        self.assertIn("DD.MM.YYYY", message)
    
    def test_handle_validation_error(self):
        """Test validation error handling"""
        error = ValidationError("Invalid input", field="phone")
        message = ErrorHandler.handle_validation_error(error)
        self.assertIn("❌", message)
        self.assertIn("Invalid input", message)


if __name__ == '__main__':
    unittest.main()
