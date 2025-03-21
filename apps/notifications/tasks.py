import datetime
from django.utils import timezone
from apps.events.models import Event
from .services import NotificationService

def send_event_reminders():
    """
    Task to send reminders for upcoming events
    
    This function should be scheduled to run periodically, e.g., every hour
    through a task scheduler like Celery or Django's built-in scheduler
    """
    # Get events happening in the next 24 hours
    tomorrow = timezone.now() + datetime.timedelta(hours=24)
    today = timezone.now()
    
    upcoming_events = Event.objects.filter(
        date__gt=today,
        date__lte=tomorrow
    )
    
    # Send reminders for each event
    for event in upcoming_events:
        NotificationService.send_event_reminder(event)
    
    return len(upcoming_events)