"""
Tests for Dashboard Analytics endpoints.
"""

from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from records.models import FinancialRecord


class DashboardTests(TestCase):
    """Tests for dashboard analytics endpoints."""
    
    def setUp(self):
        """Set up test data with financial records."""
        self.client = APIClient()
        
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
        
        # Create sample financial records
        FinancialRecord.objects.create(
            amount=Decimal('50000.00'), transaction_type='income',
            category='salary', date=date.today(),
            description='Monthly salary', created_by=self.admin,
        )
        FinancialRecord.objects.create(
            amount=Decimal('10000.00'), transaction_type='income',
            category='freelance', date=date.today(),
            description='Freelance project', created_by=self.admin,
        )
        FinancialRecord.objects.create(
            amount=Decimal('15000.00'), transaction_type='expense',
            category='rent', date=date.today(),
            description='Monthly rent', created_by=self.admin,
        )
        FinancialRecord.objects.create(
            amount=Decimal('3000.00'), transaction_type='expense',
            category='food', date=date.today(),
            description='Groceries', created_by=self.admin,
        )
        FinancialRecord.objects.create(
            amount=Decimal('2000.00'), transaction_type='expense',
            category='transport', date=date.today(),
            description='Fuel', created_by=self.admin,
        )
    
    def test_summary_analyst_access(self):
        """Test that analysts can access the summary endpoint."""
        self.client.force_authenticate(user=self.analyst)
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data['data']
        self.assertEqual(data['total_income'], '60000.00')
        self.assertEqual(data['total_expenses'], '20000.00')
        self.assertEqual(data['net_balance'], '40000.00')
        self.assertEqual(data['profit_status'], 'profit')
    
    def test_summary_admin_access(self):
        """Test that admins can access the summary endpoint."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_summary_viewer_denied(self):
        """Test that viewers cannot access the summary endpoint."""
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_category_breakdown(self):
        """Test category breakdown returns correct data."""
        self.client.force_authenticate(user=self.analyst)
        response = self.client.get('/api/dashboard/category-breakdown/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data['data']
        self.assertIn('breakdown', data)
        self.assertTrue(len(data['breakdown']) > 0)
    
    def test_category_breakdown_filtered(self):
        """Test category breakdown filtered by type."""
        self.client.force_authenticate(user=self.analyst)
        response = self.client.get('/api/dashboard/category-breakdown/?type=expense')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # All categories should be expense categories
        data = response.data['data']
        expense_categories = {'rent', 'food', 'transport'}
        returned_categories = {item['category'] for item in data['breakdown']}
        self.assertTrue(returned_categories.issubset(expense_categories | {'other'}))
    
    def test_monthly_trends(self):
        """Test monthly trends endpoint."""
        self.client.force_authenticate(user=self.analyst)
        response = self.client.get('/api/dashboard/trends/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('trends', response.data['data'])
    
    def test_recent_activity_all_roles(self):
        """Test that all roles can access recent activity."""
        for user in [self.admin, self.analyst, self.viewer]:
            self.client.force_authenticate(user=user)
            response = self.client.get('/api/dashboard/recent-activity/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(len(response.data['data']) > 0)
    
    def test_recent_activity_limit(self):
        """Test that recent activity respects the limit parameter."""
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get('/api/dashboard/recent-activity/?limit=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
    
    def test_unauthenticated_denied(self):
        """Test that unauthenticated users are blocked from all endpoints."""
        endpoints = [
            '/api/dashboard/summary/',
            '/api/dashboard/category-breakdown/',
            '/api/dashboard/trends/',
            '/api/dashboard/recent-activity/',
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
