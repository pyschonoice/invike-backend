from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.events.models import Event
from apps.notifications.models import Notification
import datetime

class NotificationViewSetTests(APITestCase):
    """
    Test cases for notification endpoints
    """
    def setUp(self):
        # Create test users
        self.host_user = User.objects.create_user(
            username='host@example.com',
            email='host@example.com',
            name='Host User',
            password='hostpass123',
            role='HOST'
        )
        
        self.guest_user = User.objects.create_user(
            username='guest@example.com',
            email='guest@example.com',
            name='Guest User',
            password='guestpass123',
            role='GUEST'
        )
        
        # Create test event
        self.event = Event.objects.create(
            title='Test Event',
            description='This is a test event',
            date=datetime.datetime.now() + datetime.timedelta(days=7),
            location='Test Location',
            privacy='PUBLIC',
            created_by=self.host_user
        )
        
        # Create test notifications
        self.notification1 = Notification.objects.create(
            user=self.guest_user,
            event=self.event,
            type='EVENT_INVITE',
            title='You are invited!',
            message='You have been invited to Test Event',
            action_link=f'/events/{self.event.id}',
            action_text='View Event',
            is_read=False
        )
        
        self.notification2 = Notification.objects.create(
            user=self.guest_user,
            event=self.event,
            type='EVENT_REMINDER',
            title='Event Reminder',
            message='Test Event is starting soon',
            action_link=f'/events/{self.event.id}',
            action_text='View Event',
            is_read=False
        )
    
    def test_list_notifications(self):
        """
        Test listing user's notifications
        """
        url = reverse('notification-list')
        self.client.force_authenticate(user=self.guest_user)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_create_notification(self):
        """
        Test creating notifications as a host
        """
        url = reverse('notification-list')
        self.client.force_authenticate(user=self.host_user)
        
        data = {
            'user_ids': [str(self.guest_user.id)],
            'event_id': str(self.event.id),
            'type': 'HOST_MESSAGE',
            'title': 'Important update',
            'message': 'Please bring a gift',
            'action_link': f'/events/{self.event.id}',
            'action_text': 'View Event'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['notification']['title'], 'Important update')
    
    def test_mark_notifications_read(self):
        """
        Test marking notifications as read
        """
        url = reverse('notification-mark-read')
        self.client.force_authenticate(user=self.guest_user)
        
        data = {
            'notification_ids': [str(self.notification1.id), str(self.notification2.id)]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['count'], 2)
        
        # Verify they're marked as read
        self.notification1.refresh_from_db()
        self.notification2.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
        self.assertTrue(self.notification2.is_read)
    
    def test_mark_all_read(self):
        """
        Test marking all notifications as read
        """
        url = reverse('notification-mark-all-read')
        self.client.force_authenticate(user=self.guest_user)
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['count'], 2)
        
        # Verify all are marked as read
        unread_count = Notification.objects.filter(user=self.guest_user, is_read=False).count()
        self.assertEqual(unread_count, 0)
    
    def test_unread_count(self):
        """
        Test getting unread notification count
        """
        url = reverse('notification-unread-count')
        self.client.force_authenticate(user=self.guest_user)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['unread_count'], 2)