from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.events.models import Event
from apps.payments.models import Payment
import datetime
import uuid
from django.utils import timezone

class PaymentViewSetTests(APITestCase):
    """
    Comprehensive test cases for payment endpoints
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
        
        self.another_user = User.objects.create_user(
            username='another@example.com',
            email='another@example.com',
            name='Another User',
            password='anotherpass123',
            role='GUEST'
        )
        
        # Create test events with timezone-aware dates
        self.event = Event.objects.create(
            title='Test Event With Payment',
            description='This event requires payment',
            date=timezone.now() + datetime.timedelta(days=7),
            location='Test Location',
            privacy='PUBLIC',
            created_by=self.host_user
        )
        
        self.private_event = Event.objects.create(
            title='Private Test Event',
            description='This is a private event',
            date=timezone.now() + datetime.timedelta(days=14),
            location='Private Location',
            privacy='PRIVATE',
            created_by=self.host_user
        )
        
        # Create sample payment link
        self.payment_link = Payment.objects.create(
            event=self.event,
            user=self.host_user,
            payment_link='https://upi.example.com/pay/host123',
            amount=500.00,
            description='Event contribution'
        )
    
    def test_add_payment_link(self):
        """
        Test adding a payment link to an event
        """
        url = '/api/payments/add-link/'
        self.client.force_authenticate(user=self.host_user)
        
        data = {
            'event_id': str(self.private_event.id),
            'payment_link': 'https://paytm.example.com/pay/host456',
            'amount': '750.00',
            'description': 'Private event fee'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['payment']['payment_link'], 'https://paytm.example.com/pay/host456')
        self.assertEqual(response.data['payment']['amount'], '750.00')
        
        # Verify in database
        payment_exists = Payment.objects.filter(
            event=self.private_event,
            payment_link='https://paytm.example.com/pay/host456'
        ).exists()
        self.assertTrue(payment_exists)
    
    def test_non_host_cannot_add_payment_link(self):
        """
        Test that non-hosts cannot add payment links
        """
        url = '/api/payments/add-link/'
        self.client.force_authenticate(user=self.guest_user)
        
        data = {
            'event_id': str(self.event.id),
            'payment_link': 'https://upi.example.com/pay/guest123',
            'amount': '100.00',
            'description': 'Invalid payment link'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify no payment was created
        invalid_payment = Payment.objects.filter(
            event=self.event,
            payment_link='https://upi.example.com/pay/guest123'
        ).exists()
        self.assertFalse(invalid_payment)
    
    def test_add_payment_link_for_nonexistent_event(self):
        """
        Test adding a payment link to a non-existent event
        """
        url = '/api/payments/add-link/'
        self.client.force_authenticate(user=self.host_user)
        
        data = {
            'event_id': str(uuid.uuid4()),  # Random UUID that doesn't exist
            'payment_link': 'https://upi.example.com/pay/invalid',
            'amount': '200.00',
            'description': 'Invalid event payment'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_confirm_payment(self):
        """
        Test confirming payment for an event
        """
        url = '/api/payments/confirm/'
        self.client.force_authenticate(user=self.guest_user)
        
        data = {
            'event_id': str(self.event.id),
            'status': 'PAID',
            'confirmation_notes': 'Paid via UPI'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['payment']['status'], 'PAID')
        self.assertTrue(response.data['payment']['manually_confirmed'])
        
        # Verify in database
        payment = Payment.objects.get(
            event=self.event,
            user=self.guest_user,
            status='PAID'
        )
        self.assertEqual(payment.confirmation_notes, 'Paid via UPI')
    
    def test_confirm_payment_twice(self):
        """
        Test confirming payment twice (should update existing instead of creating new)
        """
        # First confirmation
        Payment.objects.create(
            event=self.event,
            user=self.guest_user,
            status='PENDING',
            manually_confirmed=False
        )
        
        url = '/api/payments/confirm/'
        self.client.force_authenticate(user=self.guest_user)
        
        data = {
            'event_id': str(self.event.id),
            'status': 'PAID',
            'confirmation_notes': 'Updated payment confirmation'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify only one payment exists for this user/event
        payment_count = Payment.objects.filter(
            event=self.event,
            user=self.guest_user
        ).count()
        self.assertEqual(payment_count, 1)
        
        # Verify the payment was updated
        payment = Payment.objects.get(
            event=self.event,
            user=self.guest_user
        )
        self.assertEqual(payment.status, 'PAID')
        self.assertEqual(payment.confirmation_notes, 'Updated payment confirmation')
    
    def test_confirm_payment_without_payment_link(self):
        """
        Test confirming payment for an event without a payment link
        """
        # Create an event without a payment link
        event_without_payment = Event.objects.create(
            title='Event Without Payment',
            description='This event has no payment link',
            date=timezone.now() + datetime.timedelta(days=10),
            location='No Payment Location',
            privacy='PUBLIC',
            created_by=self.host_user
        )
        
        url = '/api/payments/confirm/'
        self.client.force_authenticate(user=self.guest_user)
        
        data = {
            'event_id': str(event_without_payment.id),
            'status': 'PAID',
            'confirmation_notes': 'Should fail'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_event_payment_status(self):
        """
        Test getting payment status for an event
        """
        # Create a few confirmed payments
        Payment.objects.create(
            event=self.event,
            user=self.guest_user,
            status='PAID',
            manually_confirmed=True,
            confirmation_notes='Paid via UPI'
        )
        
        Payment.objects.create(
            event=self.event,
            user=self.another_user,
            status='PENDING',
            manually_confirmed=False
        )
        
        url = '/api/payments/event-status/'
        self.client.force_authenticate(user=self.host_user)
        
        response = self.client.get(f"{url}?event_id={self.event.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue(response.data['has_payment_link'])
        self.assertEqual(response.data['confirmed_payments'], 1)
        self.assertIn(response.data['pending_payments'], [1, 2])
        self.assertFalse(response.data['user_has_paid'])  # Host hasn't paid
    
    def test_guest_accessing_event_payment_status(self):
        """
        Test a guest accessing payment status for an event they're part of
        """
        # Add guest to event via payment
        Payment.objects.create(
            event=self.event,
            user=self.guest_user,
            status='PAID',
            manually_confirmed=True
        )
        
        url = '/api/payments/event-status/'
        self.client.force_authenticate(user=self.guest_user)
        
        response = self.client.get(f"{url}?event_id={self.event.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['user_has_paid'])
    
    def test_unauthorized_user_accessing_private_event_payment_status(self):
        """
        Test an unauthorized user accessing payment status for a private event
        """
        # Create payment link for private event
        Payment.objects.create(
            event=self.private_event,
            user=self.host_user,
            payment_link='https://upi.example.com/private',
            amount=1000.00
        )
        
        url = '/api/payments/event-status/'
        self.client.force_authenticate(user=self.another_user)  # User not invited
        
        response = self.client.get(f"{url}?event_id={self.private_event.id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_payment_status(self):
        """
        Test host updating a guest's payment status
        """
        # Create a pending payment
        payment = Payment.objects.create(
            event=self.event,
            user=self.guest_user,
            status='PENDING',
            manually_confirmed=False
        )
        
        url = f'/api/payments/{payment.id}/update_status/'
        self.client.force_authenticate(user=self.host_user)
        
        data = {
            'status': 'PAID',
            'confirmation_notes': 'Verified payment receipt'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify payment was updated
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'PAID')
        self.assertEqual(payment.confirmation_notes, 'Verified payment receipt')
    
    def test_non_host_cannot_update_payment_status(self):
        """
        Test that non-hosts cannot update payment status
        """
        # Create a pending payment
        payment = Payment.objects.create(
            event=self.event,
            user=self.guest_user,
            status='PENDING',
            manually_confirmed=False
        )
        
        # Standard REST URL pattern for the payment instance
        url = f'/api/payments/{payment.id}/'
        self.client.force_authenticate(user=self.another_user)  # Not the host
        
        data = {
            'status': 'PAID',
            'confirmation_notes': 'Should fail'
        }
        
        response = self.client.patch(url, data, format='json')
        
        # Since our permission class should prevent non-hosts from updating,
        # we should get a 403 Forbidden response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Most importantly, verify the payment was not updated
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'PENDING')

    def test_list_payments_for_host(self):
        """
        Test listing payments for a host (should see all payments for their events)
        """
        # Create additional payments
        Payment.objects.create(
            event=self.event,
            user=self.guest_user,
            status='PAID',
            manually_confirmed=True
        )
        
        Payment.objects.create(
            event=self.event,
            user=self.another_user,
            status='PENDING',
            manually_confirmed=False
        )
        
        url = '/api/payments/'
        self.client.force_authenticate(user=self.host_user)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Host should see all payments (their own payment link + guest payments)
        self.assertGreaterEqual(len(response.data['results']), 3)
    
    def test_list_payments_for_guest(self):
        """
        Test listing payments for a guest (should only see their own payments)
        """
        # Create payments for multiple guests
        Payment.objects.create(
            event=self.event,
            user=self.guest_user,
            status='PAID',
            manually_confirmed=True
        )
        
        Payment.objects.create(
            event=self.private_event,
            user=self.guest_user,
            status='PENDING',
            manually_confirmed=False
        )
        
        Payment.objects.create(
            event=self.event,
            user=self.another_user,
            status='PAID',
            manually_confirmed=True
        )
        
        url = '/api/payments/'
        self.client.force_authenticate(user=self.guest_user)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Guest should only see their own payments
        self.assertEqual(len(response.data['results']), 2)
        
        # Verify all payments belong to the guest
        for payment in response.data['results']:
            self.assertEqual(payment['user']['email'], 'guest@example.com')