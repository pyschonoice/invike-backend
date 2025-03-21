import uuid
from django.db import models
from apps.users.models import User
from apps.events.models import Event

class RSVP(models.Model):
    """
    RSVP model for tracking event responses
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rsvps')
    
    # RSVP status
    STATUS_CHOICES = (
        ('YES', 'Yes'),
        ('NO', 'No'),
        ('MAYBE', 'Maybe'),
    )
    status = models.CharField(max_length=5, choices=STATUS_CHOICES)
    
    # Additional guests
    plus_ones = models.PositiveIntegerField(default=0)
    
    # For private events, host approval may be required
    is_approved = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rsvps'
        unique_together = ('event', 'user')  # A user can RSVP to an event only once
    
    def __str__(self):
        return f"{self.user} - {self.event} - {self.status}"
    
    @property
    def payment_status(self):
        """Get the payment status for this RSVP"""
        from apps.payments.models import Payment
        
        payment = Payment.objects.filter(
            event=self.event,
            user=self.user
        ).first()
        
        if not payment:
            return "NOT_STARTED"
        
        return payment.status
    
    @property
    def has_paid(self):
        """Check if this RSVP has been paid"""
        return self.payment_status == "PAID"
