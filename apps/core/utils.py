import uuid
import hashlib
import random
import string

def generate_unique_id():
    """
    Generate a unique ID for resources
    """
    return str(uuid.uuid4())

def generate_short_code(length=8):
    """
    Generate a short code for invites, etc.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def hash_password(password, salt=None):
    """
    Hash a password for secure storage
    """
    if salt is None:
        salt = ''.join(random.choice(string.ascii_letters) for _ in range(16))
    
    hash_obj = hashlib.sha256(f"{password}{salt}".encode())
    return hash_obj.hexdigest(), salt
