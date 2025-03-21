import re
from django.core.exceptions import ValidationError

def validate_phone_number(value):
    """
    Validate phone number format
    """
    if not value:
        return value
        
    pattern = r'^\+?[0-9]{10,15}$'
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid phone number")
    return value

def validate_password_strength(password):
    """
    Validate password strength
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one digit")
    
    if not any(char.isalpha() for char in password):
        raise ValidationError("Password must contain at least one letter")
    
    return password