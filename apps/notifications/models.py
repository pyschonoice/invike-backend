import uuid
from django.db import models
from apps.users.models import User
from apps.events.models import Event

class Notification(models.Model):
    """
    Notification model for tracking user notifications
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    
    # Notification details
    NOTIFICATION_TYPES = (
        ('EVENT_INVITE', 'Event Invitation'),
        ('RSVP_CONFIRMATION', 'RSVP Confirmation'),
        ('RSVP_UPDATE', 'RSVP Status Update'),
        ('EVENT_REMINDER', 'Event Reminder'),
        ('PAYMENT_CONFIRMATION', 'Payment Confirmation'),
        ('HOST_MESSAGE', 'Host Message'),
        ('EVENT_UPDATE', 'Event Update'),
        ('SYSTEM', 'System Notification'),
    )
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # For action links, e.g., "View Event" button
    action_link = models.CharField(max_length=255, blank=True, null=True)
    action_text = models.CharField(max_length=50, blank=True, null=True)
    
    # Read status
    is_read = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} - {self.title}"
