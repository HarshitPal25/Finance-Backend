"""
Tests for the Users app - Authentication and User Management.

Django's test framework provides:
- TestCase: Base class with database setup/teardown
- APIClient: A test HTTP client that can make requests to our views
- setUp(): Runs before each test to set up test data
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import User


class AuthenticationTests(TestCase):
    """Tests for registration and login."""
    
    def setUp(self):
        """Set up test client and create a test user."""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        
        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='viewer',
        )
    
    def test_register_success(self):
        """Test successful user registration."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'role': 'viewer',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data['data'])
        self.assertEqual(User.objects.count(), 2)
    
    def test_register_duplicate_email(self):
        """Test registration with an existing email fails."""
        data = {
            'username': 'another',
            'email': 'test@example.com',  # Already exists
            'password': 'securepass123',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_short_password(self):
        """Test registration with a short password fails."""
        data = {
            'username': 'shortpass',
            'email': 'short@example.com',
            'password': '123',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_missing_fields(self):
        """Test registration with missing fields fails."""
        response = self.client.post(self.register_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_success(self):
        """Test successful login."""
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data['data'])
    
    def test_login_wrong_password(self):
        """Test login with wrong password fails."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_inactive_user(self):
        """Test that inactive users cannot log in."""
        self.test_user.is_active = False
        self.test_user.save()
        
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_authenticated(self):
        """Test that authenticated users can view their profile."""
        self.client.force_authenticate(user=self.test_user)
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['username'], 'testuser')
    
    def test_profile_unauthenticated(self):
        """Test that unauthenticated users cannot view profile."""
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserManagementTests(TestCase):
    """Tests for user management (admin-only endpoints)."""
    
    def setUp(self):
        """Create users with different roles."""
        self.client = APIClient()
        
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='adminpass123', role='admin',
        )
        self.analyst = User.objects.create_user(
            username='analyst', email='analyst@example.com',
            password='analystpass123', role='analyst',
        )
        self.viewer = User.objects.create_user(
            username='viewer', email='viewer@example.com',
            password='viewerpass123', role='viewer',
        )
    
    def test_admin_can_list_users(self):
        """Test that admins can list all users."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
    
    def test_viewer_cannot_list_users(self):
        """Test that viewers cannot list users."""
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_analyst_cannot_list_users(self):
        """Test that analysts cannot list users."""
        self.client.force_authenticate(user=self.analyst)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_change_role(self):
        """Test that admins can change a user's role."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(
            f'/api/users/{self.viewer.id}/role/',
            {'role': 'analyst'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.viewer.refresh_from_db()
        self.assertEqual(self.viewer.role, 'analyst')
    
    def test_admin_cannot_change_own_role(self):
        """Test that admins cannot change their own role."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(
            f'/api/users/{self.admin.id}/role/',
            {'role': 'viewer'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_admin_can_deactivate_user(self):
        """Test that admins can deactivate users."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(
            f'/api/users/{self.viewer.id}/status/',
            {'is_active': False},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.viewer.refresh_from_db()
        self.assertFalse(self.viewer.is_active)
    
    def test_admin_can_delete_user(self):
        """Test that admins can delete users."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/users/{self.viewer.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)
    
    def test_admin_cannot_delete_self(self):
        """Test that admins cannot delete themselves."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/users/{self.admin.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
