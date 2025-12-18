# utils/promo.py
import secrets
import string

def generate_promo_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))