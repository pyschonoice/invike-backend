import uuid
import random
import string
from datetime import datetime, timedelta

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

def format_datetime(dt):
    """
    Format datetime object for API responses
    """
    if not dt:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def calculate_event_status(event_date):
    """
    Calculate event status (upcoming, ongoing, past)
    """
    now = datetime.now()
    
    if event_date > now + timedelta(hours=1):
        return "UPCOMING"
    elif event_date < now - timedelta(hours=3):
        return "PAST"
    else:
        return "ONGOING"