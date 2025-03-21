# apps/notifications/tests/test_reminders.py
from django.test import TestCase
from django.utils import timezone
import datetime
from apps.users.models import User
from apps.events.models import Event
from apps.rsvp.models import RSVP
from apps.notifications.models import Notification
from apps.notifications.tasks import send_event_reminders

class EventReminderTests(TestCase):
    def setUp(self):
        # Create test users
        self.host = User.objects.create_user(
            username='host@example.com',
            email='host@example.com',
            name='Host User',
            password='hostpass123',
            role='HOST'
        )
        
        self.guest = User.objects.create_user(
            username='guest@example.com',
            email='guest@example.com',
            name='Guest User',
            password='guestpass123',
            role='GUEST'
        )
        
        # Create upcoming event
        self.event = Event.objects.create(
            title='Upcoming Test Event',
            description='This is a test event',
            date=timezone.now() + datetime.timedelta(hours=12),
            location='Test Location',
            privacy='PUBLIC',
            created_by=self.host
        )
        
        # Create RSVP for the guest
        self.rsvp = RSVP.objects.create(
            event=self.event,
            user=self.guest,
            status='YES',
            plus_ones=0,
            is_approved=True
        )
        
        # Create past event (should not trigger reminders)
        self.past_event = Event.objects.create(
            title='Past Test Event',
            description='This is a past test event',
            date=timezone.now() - datetime.timedelta(days=1),
            location='Test Location',
            privacy='PUBLIC',
            created_by=self.host
        )
    
    def test_event_reminders(self):
        # Clear any existing notifications
        Notification.objects.all().delete()
        
        # Run the reminder task
        event_count = send_event_reminders()
        
        # Should find 1 upcoming event
        self.assertEqual(event_count, 1)
        
        # Check that notification was created for the guest
        reminders = Notification.objects.filter(
            user=self.guest,
            event=self.event,
            type='EVENT_REMINDER'
        )
        
        self.assertEqual(reminders.count(), 1)
        self.assertEqual(reminders.first().title, 'Event Reminder')