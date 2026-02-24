from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthenticationTests(TestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/auth/register/'
        self.login_url = '/api/v1/auth/login/'
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'TestPassword123!',
            'password_confirm': 'TestPassword123!',
        }
    
    def test_user_registration(self):
        """Test user can register"""
        response = self.client.post(
            self.register_url,
            self.user_data
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.json()['success'])
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
    
    def test_registration_duplicate_email(self):
        """Test cannot register with duplicate email"""
        # Create first user
        self.client.post(self.register_url, self.user_data)
        
        # Try to create second user with same email
        response = self.client.post(
            self.register_url,
            self.user_data
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.json()['success'])
    
    def test_registration_password_mismatch(self):
        """Test registration fails if passwords don't match"""
        invalid_data = self.user_data.copy()
        invalid_data['password_confirm'] = 'DifferentPassword123!'
        
        response = self.client.post(
            self.register_url,
            invalid_data
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Test user can login"""
        # Register user
        self.client.post(self.register_url, self.user_data)
        
        # Login
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!',
        }
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['success'])
        self.assertIn('access_token', response.json()['data'])
        self.assertIn('refresh_token', response.json()['data'])
    
    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'WrongPassword123!',
        }
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.json()['success'])