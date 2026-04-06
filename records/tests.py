"""
Tests for Financial Records CRUD operations and access control.
"""

from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from .models import FinancialRecord


class FinancialRecordTests(TestCase):
    """Tests for creating, reading, updating, and deleting records."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.url = '/api/records/'
        
        self.admin = User.objects.create_user(
            username='admin', email='admin@test.com',
            password='adminpass123', role='admin',
        )
        self.analyst = User.objects.create_user(
            username='analyst', email='analyst@test.com',
            password='analystpass123', role='analyst',
        )
        self.viewer = User.objects.create_user(
            username='viewer', email='viewer@test.com',
            password='viewerpass123', role='viewer',
        )
        
        # Create sample records
        self.record1 = FinancialRecord.objects.create(
            amount=Decimal('5000.00'),
            transaction_type='income',
            category='salary',
            date=date.today(),
            description='Monthly salary',
            created_by=self.admin,
        )
        self.record2 = FinancialRecord.objects.create(
            amount=Decimal('200.00'),
            transaction_type='expense',
            category='food',
            date=date.today(),
            description='Groceries',
            created_by=self.admin,
        )
    
    # --- CREATE tests ---
    
    def test_admin_can_create_record(self):
        """Test that admin can create financial records."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'amount': '1500.00',
            'transaction_type': 'expense',
            'category': 'rent',
            'date': date.today().isoformat(),
            'description': 'Monthly rent',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(FinancialRecord.objects.count(), 3)
    
    def test_viewer_cannot_create_record(self):
        """Test that viewers cannot create records."""
        self.client.force_authenticate(user=self.viewer)
        data = {
            'amount': '100.00',
            'transaction_type': 'expense',
            'category': 'food',
            'date': date.today().isoformat(),
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_analyst_cannot_create_record(self):
        """Test that analysts cannot create records."""
        self.client.force_authenticate(user=self.analyst)
        data = {
            'amount': '100.00',
            'transaction_type': 'expense',
            'category': 'food',
            'date': date.today().isoformat(),
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_record_negative_amount(self):
        """Test that negative amounts are rejected."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'amount': '-100.00',
            'transaction_type': 'expense',
            'category': 'food',
            'date': date.today().isoformat(),
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_record_invalid_type(self):
        """Test that invalid transaction type is rejected."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'amount': '100.00',
            'transaction_type': 'invalid',
            'category': 'food',
            'date': date.today().isoformat(),
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # --- READ tests ---
    
    def test_all_roles_can_list_records(self):
        """Test that all authenticated roles can list records."""
        for user in [self.admin, self.analyst, self.viewer]:
            self.client.force_authenticate(user=user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
    
    def test_list_records_with_filters(self):
        """Test filtering records by type and category."""
        self.client.force_authenticate(user=self.viewer)
        
        # Filter by type
        response = self.client.get(f'{self.url}?transaction_type=income')
        self.assertEqual(len(response.data['data']), 1)
        
        # Filter by category
        response = self.client.get(f'{self.url}?category=food')
        self.assertEqual(len(response.data['data']), 1)
    
    def test_list_records_with_search(self):
        """Test searching records by description."""
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(f'{self.url}?search=salary')
        self.assertEqual(len(response.data['data']), 1)
    
    def test_get_single_record(self):
        """Test getting a single record by ID."""
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(f'{self.url}{self.record1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['id'], self.record1.id)
    
    def test_get_nonexistent_record(self):
        """Test getting a record that doesn't exist."""
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(f'{self.url}9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # --- UPDATE tests ---
    
    def test_admin_can_update_record(self):
        """Test that admin can update records."""
        self.client.force_authenticate(user=self.admin)
        data = {'amount': '6000.00'}
        response = self.client.patch(
            f'{self.url}{self.record1.id}/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.record1.refresh_from_db()
        self.assertEqual(self.record1.amount, Decimal('6000.00'))
    
    def test_viewer_cannot_update_record(self):
        """Test that viewers cannot update records."""
        self.client.force_authenticate(user=self.viewer)
        data = {'amount': '9999.00'}
        response = self.client.patch(
            f'{self.url}{self.record1.id}/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    # --- DELETE tests ---
    
    def test_admin_can_soft_delete_record(self):
        """Test that admin can soft-delete records."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'{self.url}{self.record1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Record should still exist in DB but be marked as deleted
        self.record1.refresh_from_db()
        self.assertTrue(self.record1.is_deleted)
        
        # Should not appear in listings
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], 1)
    
    def test_viewer_cannot_delete_record(self):
        """Test that viewers cannot delete records."""
        self.client.force_authenticate(user=self.viewer)
        response = self.client.delete(f'{self.url}{self.record1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    # --- UNAUTHENTICATED tests ---
    
    def test_unauthenticated_cannot_access(self):
        """Test that unauthenticated users cannot access records."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
