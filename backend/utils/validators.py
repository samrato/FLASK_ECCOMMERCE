import re
from werkzeug.security import check_password_hash

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False, 'Password must be at least 8 characters'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'
    if not re.search(r'[0-9]', password):
        return False, 'Password must contain at least one number'
    return True, ''

def validate_credit_card(number):
    # Simple Luhn algorithm check
    num = [int(x) for x in str(number)]
    checksum = num.pop()
    num.reverse()
    doubled = [x*2 if i%2 == 0 else x for i, x in enumerate(num)]
    total = sum(x-9 if x > 9 else x for x in doubled) + checksum
    return total % 10 == 0