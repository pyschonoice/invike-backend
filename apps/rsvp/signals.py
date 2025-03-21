# apps/rsvp/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import RSVP
from apps.notifications.services import NotificationService

@receiver(post_save, sender=RSVP)
def handle_rsvp_save(sender, instance, created, **kwargs):
    """
    Signal handler for RSVP creation and updates
    """
    if created:
        # New RSVP created - send notification
        NotificationService.notify_rsvp_created(instance)
    else:
        # Updated RSVP - check what changed
        # This is handled through the pre_save signal below
        pass

@receiver(pre_save, sender=RSVP)
def handle_rsvp_pre_save(sender, instance, **kwargs):
    """
    Signal handler to track changes before saving
    """
    if instance.pk:  # If this is an update
        try:
            old_instance = RSVP.objects.get(pk=instance.pk)
            
            # Check if status changed
            if old_instance.status != instance.status:
                # Status was updated
                NotificationService.notify_rsvp_updated(instance)
            
            # Check if approval status changed
            if old_instance.is_approved != instance.is_approved:
                # Approval status changed
                NotificationService.notify_rsvp_approval(instance, instance.is_approved)
                
        except RSVP.DoesNotExist:
            # This should not happen, but we'll handle it just in case
            pass