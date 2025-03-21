from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.events.models import Event
from apps.rsvp.models import RSVP
import datetime

class RSVPViewSetTests(APITestCase):
    """
    Test cases for RSVP endpoints
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
        
        self.other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            name='Other User',
            password='otherpass123',
            role='GUEST'
        )
        
        # Create test events
        self.public_event = Event.objects.create(
            title='Public Test Event',
            description='This is a public test event',
            date=datetime.datetime.now() + datetime.timedelta(days=7),
            location='Test Location',
            privacy='PUBLIC',
            created_by=self.host_user
        )
        
        self.private_event = Event.objects.create(
            title='Private Test Event',
            description='This is a private test event',
            date=datetime.datetime.now() + datetime.timedelta(days=14),
            location='Secret Location',
            privacy='PRIVATE',
            created_by=self.host_user
        )
        
        # Create test RSVPs
        self.guest_rsvp = RSVP.objects.create(
            event=self.public_event,
            user=self.guest_user,
            status='YES',
            plus_ones=1,
            is_approved=True
        )
    
    def test_create_rsvp(self):
        """
        Test creating a new RSVP
        """
        url = reverse('rsvp-list')
        self.client.force_authenticate(user=self.other_user)
        
        data = {
            'event_id': str(self.public_event.id),
            'status': 'YES',
            'plus_ones': 2
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['rsvp']['status'], 'YES')
        self.assertEqual(response.data['rsvp']['plus_ones'], 2)
    
    def test_create_duplicate_rsvp(self):
        """
        Test creating a duplicate RSVP (should fail)
        """
        url = reverse('rsvp-list')
        self.client.force_authenticate(user=self.guest_user)
        
        data = {
            'event_id': str(self.public_event.id),
            'status': 'MAYBE',
            'plus_ones': 0
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_rsvp(self):
        """
        Test updating an RSVP
        """
        url = reverse('rsvp-detail', kwargs={'pk': self.guest_rsvp.id})
        self.client.force_authenticate(user=self.guest_user)
        
        data = {
            'status': 'MAYBE',
            'plus_ones': 0
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'MAYBE')
        self.assertEqual(response.data['plus_ones'], 0)
    
    def test_get_guest_list_as_host(self):
        """
        Test getting guest list as event host
        """
        url = reverse('event-guests', kwargs={'event_id': self.public_event.id})
        self.client.force_authenticate(user=self.host_user)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user']['email'], 'guest@example.com')
    
    def test_export_guest_list(self):
        """
        Test exporting guest list as CSV
        """
        url = reverse('export-guests', kwargs={'event_id': self.public_event.id})
        self.client.force_authenticate(user=self.host_user)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue('attachment; filename=' in response['Content-Disposition'])
    
    def test_approve_rsvp(self):
        """
        Test approving an RSVP as host
        """
        # First create an unapproved RSVP
        unapproved_rsvp = RSVP.objects.create(
            event=self.private_event,
            user=self.other_user,
            status='YES',
            plus_ones=0,
            is_approved=False
        )
        
        url = reverse('rsvp-approve', kwargs={'pk': unapproved_rsvp.id})
        self.client.force_authenticate(user=self.host_user)
        
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Verify the RSVP is now approved
        unapproved_rsvp.refresh_from_db()
        self.assertTrue(unapproved_rsvp.is_approved)