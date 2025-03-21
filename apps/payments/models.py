import uuid
from django.db import models
from apps.users.models import User
from apps.events.models import Event

class Payment(models.Model):
    """
    Payment model for tracking event payments
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    payment_link = models.URLField(blank=True, null=True, help_text="External payment link (UPI/Paytm/GPay)")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    
    # Payment status
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    # For the Alpha version, payments are manually confirmed
    manually_confirmed = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_payments')
    confirmation_notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.event} - {self.status}"
