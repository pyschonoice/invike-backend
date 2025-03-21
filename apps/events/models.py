import uuid
from django.db import models
from apps.users.models import User


class EventCategory(models.Model):
    """Category for events (e.g., Party, Conference, Workshop)"""
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Event Categories"
    
    def __str__(self):
        return self.name
    
class Event(models.Model):
    """
    Event model for storing event information
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    categories = models.ManyToManyField(EventCategory, blank=True, related_name='events')
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    capacity = models.PositiveIntegerField(null=True, blank=True, 
                                         help_text="Maximum number of guests (leave blank for unlimited)")
    
    # Privacy settings
    PRIVACY_CHOICES = (
        ('PUBLIC', 'Public'),
        ('PRIVATE', 'Private'),
        ('SEMI_PRIVATE', 'Semi-Private'),
    )
    privacy = models.CharField(max_length=12, choices=PRIVACY_CHOICES, default='PUBLIC')
    
    # Relations
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    
    # Media
    cover_image = models.URLField(blank=True, null=True)
    
    # Location coordinates (optional, for map integration)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'events'
        ordering = ['-date']
    
    def __str__(self):
        return self.title
    
    # Add a property to get current RSVP count
    @property
    def rsvp_count(self):
        # In a real implementation, this would count RSVPs from the RSVP model
        # For now, we'll use a placeholder
        from django.db.models import Sum
        return self.rsvps.filter(status='YES').aggregate(
            total=Sum('plus_ones', default=0)
        )['total'] + self.rsvps.filter(status='YES').count()
    
    @property
    def remaining_capacity(self):
        if self.capacity is None:
            return None  # Unlimited capacity
        return max(0, self.capacity - self.rsvp_count)
    
    @property
    def has_payment_link(self):
        """Check if this event has a payment link"""
        return self.payments.filter(
            user=self.created_by,
            payment_link__isnull=False
        ).exists()
    
    @property
    def payment_info(self):
        """Get payment details for this event"""
        payment = self.payments.filter(
            user=self.created_by,
            payment_link__isnull=False
        ).first()
        
        if not payment:
            return None
            
        return {
            'amount': payment.amount,
            'payment_link': payment.payment_link,
            'description': payment.description
        }
    
    @property
    def payment_stats(self):
        """Get payment statistics for this event"""
        confirmed_count = self.payments.filter(status='PAID').count()
        pending_count = self.payments.filter(status='PENDING').count()
        
        return {
            'confirmed_count': confirmed_count,
            'pending_count': pending_count,
            'total_amount': self.payments.filter(status='PAID').aggregate(
                total=models.Sum('amount', default=0)
            )['total']
        }
    

class RecurringEventRule(models.Model):
    """Rules for recurring events"""
    FREQUENCY_CHOICES = (
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    )
    
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='recurring_rule')
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    interval = models.PositiveIntegerField(default=1, help_text="Repeat every X days/weeks/months/years")
    end_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_frequency_display()} event: {self.event.title}"
