# apps/notifications/services.py
from django.db import transaction
from .models import Notification

class NotificationService:
    """
    Service for creating and managing notifications related to RSVPs and events
    """
    
    @staticmethod
    def create_notification(user, event, notification_type, title, message, action_link=None, action_text=None):
        """
        Create a notification for a user
        """
        return Notification.objects.create(
            user=user,
            event=event,
            type=notification_type,
            title=title,
            message=message,
            action_link=action_link,
            action_text=action_text
        )
    
    @classmethod
    def notify_rsvp_created(cls, rsvp):
        """
        Send notifications when a new RSVP is created
        """
        event = rsvp.event
        host = event.created_by
        guest = rsvp.user
        
        # Notify host
        cls.create_notification(
            user=host,
            event=event,
            notification_type='RSVP_CONFIRMATION',
            title='New RSVP for your event',
            message=f"{guest.name} has RSVP'd {rsvp.get_status_display()} to your event '{event.title}'.",
            action_link=f'/events/{event.id}/guests',
            action_text='View Guest List'
        )
        
        # Notify guest
        cls.create_notification(
            user=guest,
            event=event,
            notification_type='RSVP_CONFIRMATION',
            title='RSVP Confirmation',
            message=f"You have RSVP'd {rsvp.get_status_display()} to '{event.title}'.",
            action_link=f'/events/{event.id}',
            action_text='View Event'
        )
    
    @classmethod
    def notify_rsvp_updated(cls, rsvp):
        """
        Send notifications when an RSVP is updated
        """
        event = rsvp.event
        host = event.created_by
        guest = rsvp.user
        
        # Notify host
        cls.create_notification(
            user=host,
            event=event,
            notification_type='RSVP_UPDATE',
            title='RSVP Updated',
            message=f"{guest.name} has updated their RSVP to {rsvp.get_status_display()} for your event '{event.title}'.",
            action_link=f'/events/{event.id}/guests',
            action_text='View Guest List'
        )
        
        # Notify guest
        cls.create_notification(
            user=guest,
            event=event,
            notification_type='RSVP_UPDATE',
            title='RSVP Update Confirmation',
            message=f"You have updated your RSVP to {rsvp.get_status_display()} for '{event.title}'.",
            action_link=f'/events/{event.id}',
            action_text='View Event'
        )
    
    @classmethod
    def notify_rsvp_approval(cls, rsvp, is_approved):
        """
        Send notifications when an RSVP is approved or rejected
        """
        event = rsvp.event
        guest = rsvp.user
        
        status_text = "approved" if is_approved else "rejected"
        
        cls.create_notification(
            user=guest,
            event=event,
            notification_type='RSVP_UPDATE',
            title=f'RSVP {status_text.capitalize()}',
            message=f"Your RSVP to '{event.title}' has been {status_text}.",
            action_link=f'/events/{event.id}',
            action_text='View Event'
        )
    
    @classmethod
    def send_event_reminder(cls, event):
        """
        Send reminders to all approved guests for an upcoming event
        """
        # Get all approved RSVPs
        rsvps = event.rsvps.filter(status='YES', is_approved=True)
        
        for rsvp in rsvps:
            cls.create_notification(
                user=rsvp.user,
                event=event,
                notification_type='EVENT_REMINDER',
                title='Event Reminder',
                message=f"Reminder: '{event.title}' is starting soon!",
                action_link=f'/events/{event.id}',
                action_text='View Event'
            )