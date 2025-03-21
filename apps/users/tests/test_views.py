from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User

class UserAuthTests(APITestCase):
    """
    Test cases for user authentication endpoints
    """
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            name='Test User',
            password='testpass123'
        )
    
    def test_user_registration(self):
        """
        Test user registration endpoint
        """
        url = reverse('user-register')
        data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'newuserpass123',
            'role': 'HOST'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        self.assertEqual(response.data['user']['role'], 'HOST')
        self.assertTrue('tokens' in response.data)
    
    def test_user_login(self):
        """
        Test user login endpoint
        """
        url = reverse('user-login')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')
        self.assertTrue('tokens' in response.data)
    
    def test_user_login_invalid(self):
        """
        Test login with invalid credentials
        """
        url = reverse('user-login')
        data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_profile_authenticated(self):
        """
        Test profile retrieval when authenticated
        """
        # First login to get tokens
        login_url = reverse('user-login')
        login_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        token = login_response.data['tokens']['access']
        
        # Use token to access profile
        profile_url = reverse('user-profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@example.com')
    
    def test_user_profile_unauthenticated(self):
        """
        Test profile retrieval when not authenticated
        """
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_update(self):
        """
        Test profile update endpoint
        """
        # First login to get tokens
        login_url = reverse('user-login')
        login_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        token = login_response.data['tokens']['access']
        
        # Use token to update profile
        update_url = reverse('profile-update')
        update_data = {
            'name': 'Updated Name',
            'avatar': 'https://example.com/avatar.jpg'
        }
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.patch(update_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['user']['name'], 'Updated Name')
        self.assertEqual(response.data['user']['avatar'], 'https://example.com/avatar.jpg')

