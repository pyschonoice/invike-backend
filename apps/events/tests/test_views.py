from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.events.models import Event
import datetime
from django.utils import timezone

class EventViewSetTests(APITestCase):
    """
    Test cases for event endpoints
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
        
        # Create test events
        self.public_event = Event.objects.create(
            title='Public Test Event',
            description='This is a public test event',
            date=timezone.now() + datetime.timedelta(days=7),
            location='Test Location',
            privacy='PUBLIC',
            created_by=self.host_user
        )
        
        self.private_event = Event.objects.create(
            title='Private Test Event',
            description='This is a private test event',
            date=timezone.now() + datetime.timedelta(days=14),
            location='Secret Location',
            privacy='PRIVATE',
            created_by=self.host_user
        )
    
    def test_list_events_unauthenticated(self):
        """
        Test listing events when unauthenticated (should see only public)
        """
        # First, let's clear the cache to avoid any caching issues
        from django.core.cache import cache
        cache.clear()
        
        url = reverse('event-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Debug: Print privacy values of all events to check filter matches
        event_data = [
            {'title': e['title'], 'privacy': e['privacy']} 
            for e in response.data['results']
        ]
        print("Events with privacy values:", event_data)
        
        # Manual check to ensure only public events are returned
        for event in response.data['results']:
            self.assertEqual(
                event['privacy'], 
                'PUBLIC', 
                f"Non-public event {event['title']} visible to unauthenticated user"
            )
        
        # Should only see 1 event (the public one)
        self.assertEqual(len(response.data['results']), 1)
        
        # The only visible event should be the public one
        self.assertEqual(response.data['results'][0]['title'], 'Public Test Event')
    
    def test_list_events_authenticated_as_host(self):
        """
        Test listing events when authenticated as event host (should see both)
        """
        url = reverse('event-list')
        self.client.force_authenticate(user=self.host_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if pagination is enabled
        self.assertEqual(len(response.data['results']), 2)  # Both events
        
        # Verify both events are in the results
        titles = {event['title'] for event in response.data['results']}
        self.assertIn('Public Test Event', titles)
        self.assertIn('Private Test Event', titles)
    
    def test_create_event(self):
        """
        Test creating a new event
        """
        url = reverse('event-list')
        self.client.force_authenticate(user=self.host_user)
        
        data = {
            'title': 'New Test Event',
            'description': 'This is a new test event',
            'date': (timezone.now() + datetime.timedelta(days=10)).isoformat(),
            'location': 'New Location',
            'privacy': 'PUBLIC'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['event']['title'], 'New Test Event')
        self.assertTrue('shareable_link' in response.data)
    
    def test_retrieve_public_event(self):
        """
        Test retrieving a public event
        """
        url = reverse('event-detail', kwargs={'pk': self.public_event.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Public Test Event')
    
    def test_retrieve_private_event_as_host(self):
        """
        Test retrieving a private event as the host
        """
        url = reverse('event-detail', kwargs={'pk': self.private_event.id})
        self.client.force_authenticate(user=self.host_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Private Test Event')
    
    def test_update_event_as_host(self):
        """
        Test updating an event as the host
        """
        url = reverse('event-detail', kwargs={'pk': self.public_event.id})
        self.client.force_authenticate(user=self.host_user)
        
        data = {
            'title': 'Updated Event Title',
            'description': 'Updated event description'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Event Title')
        self.assertEqual(response.data['description'], 'Updated event description')
    
    def test_delete_event_as_host(self):
        """
        Test deleting an event as the host
        """
        url = reverse('event-detail', kwargs={'pk': self.public_event.id})
        self.client.force_authenticate(user=self.host_user)
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify it's gone
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_share_event(self):
        """
        Test sharing an event
        """
        url = reverse('event-share', kwargs={'pk': self.public_event.id})
        self.client.force_authenticate(user=self.host_user)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue('sharing_options' in response.data)
        self.assertTrue('link' in response.data['sharing_options'])
        self.assertTrue('qr_code_data' in response.data['sharing_options'])
    
    def test_get_guests(self):
        """
        Test getting guest list as host
        """
        url = reverse('event-guests', kwargs={'pk': self.public_event.id})
        self.client.force_authenticate(user=self.host_user)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue('guests' in response.data)
        self.assertTrue('total_guests' in response.data)
        
    def test_retrieve_private_event_as_guest(self):
        """
        Test that a guest user cannot access a private event they don't have access to
        """
        url = reverse('event-detail', kwargs={'pk': self.private_event.id})
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(url)
        
        # Should get 404 for private events not created by the user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_event_as_non_owner(self):
        """
        Test that a non-owner cannot update an event
        """
        url = reverse('event-detail', kwargs={'pk': self.public_event.id})
        self.client.force_authenticate(user=self.guest_user)
        
        data = {
            'title': 'Unauthorized Update',
            'description': 'This update should fail'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify the event remains unchanged
        self.client.force_authenticate(user=self.host_user)
        response = self.client.get(url)
        self.assertEqual(response.data['title'], 'Public Test Event')

    def test_delete_event_as_non_owner(self):
        """
        Test that a non-owner cannot delete an event
        """
        url = reverse('event-detail', kwargs={'pk': self.public_event.id})
        self.client.force_authenticate(user=self.guest_user)
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify the event still exists
        self.client.force_authenticate(user=self.host_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_event_unauthenticated(self):
        """
        Test that an unauthenticated user cannot create an event
        """
        url = reverse('event-list')
        # Ensure not authenticated
        self.client.force_authenticate(user=None)
        
        data = {
            'title': 'Unauthorized Event',
            'description': 'This should fail',
            'date': (timezone.now() + datetime.timedelta(days=10)).isoformat(),
            'location': 'Somewhere',
            'privacy': 'PUBLIC'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_guests(self):
        """
        Test exporting guest list as host
        """
        url = reverse('event-export-guests', kwargs={'pk': self.public_event.id})
        
        # Non-owner should not be able to export guests
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Owner should be able to export guests
        self.client.force_authenticate(user=self.host_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue('download_link' in response.data)