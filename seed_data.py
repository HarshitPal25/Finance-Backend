#!/usr/bin/env python3
"""
Seed Data Script - Populates the database with sample data for testing.

Usage:
    python3 manage.py shell < seed_data.py

Or run directly:
    python3 seed_data.py
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from users.models import User
from records.models import FinancialRecord


def create_users():
    """Create sample users with different roles."""
    print("Creating users...")
    
    users = {}
    
    # Admin user
    if not User.objects.filter(username='admin').exists():
        users['admin'] = User.objects.create_user(
            username='admin',
            email='admin@financedash.com',
            password='admin123456',
            role='admin',
        )
        print(f"  ✓ Created admin user (username: admin, password: admin123456)")
    else:
        users['admin'] = User.objects.get(username='admin')
        print(f"  - Admin user already exists")
    
    # Analyst user
    if not User.objects.filter(username='analyst').exists():
        users['analyst'] = User.objects.create_user(
            username='analyst',
            email='analyst@financedash.com',
            password='analyst123456',
            role='analyst',
        )
        print(f"  ✓ Created analyst user (username: analyst, password: analyst123456)")
    else:
        users['analyst'] = User.objects.get(username='analyst')
        print(f"  - Analyst user already exists")
    
    # Viewer user
    if not User.objects.filter(username='viewer').exists():
        users['viewer'] = User.objects.create_user(
            username='viewer',
            email='viewer@financedash.com',
            password='viewer123456',
            role='viewer',
        )
        print(f"  ✓ Created viewer user (username: viewer, password: viewer123456)")
    else:
        users['viewer'] = User.objects.get(username='viewer')
        print(f"  - Viewer user already exists")
    
    return users


def create_financial_records(admin_user):
    """Create sample financial records spanning several months."""
    print("\nCreating financial records...")
    
    if FinancialRecord.objects.count() > 0:
        print("  - Records already exist. Skipping.")
        return
    
    today = date.today()
    records = []
    
    # Generate 6 months of data
    for month_offset in range(6):
        month_start = today.replace(day=1) - timedelta(days=30 * month_offset)
        
        # Monthly salary (income)
        records.append(FinancialRecord(
            amount=Decimal('50000.00'),
            transaction_type='income',
            category='salary',
            date=month_start.replace(day=1),
            description=f'Monthly salary - {month_start.strftime("%B %Y")}',
            created_by=admin_user,
        ))
        
        # Freelance income (occasional)
        if month_offset % 2 == 0:
            records.append(FinancialRecord(
                amount=Decimal(str(random.randint(5000, 20000))),
                transaction_type='income',
                category='freelance',
                date=month_start.replace(day=15),
                description=f'Freelance project payment',
                created_by=admin_user,
            ))
        
        # Monthly rent (expense)
        records.append(FinancialRecord(
            amount=Decimal('15000.00'),
            transaction_type='expense',
            category='rent',
            date=month_start.replace(day=5),
            description=f'Monthly rent - {month_start.strftime("%B %Y")}',
            created_by=admin_user,
        ))
        
        # Weekly groceries
        for week in range(4):
            day = min(month_start.replace(day=7 + week * 7).day, 28)
            records.append(FinancialRecord(
                amount=Decimal(str(random.randint(1500, 4000))),
                transaction_type='expense',
                category='food',
                date=month_start.replace(day=day),
                description=f'Weekly groceries',
                created_by=admin_user,
            ))
        
        # Utilities
        records.append(FinancialRecord(
            amount=Decimal(str(random.randint(2000, 5000))),
            transaction_type='expense',
            category='utilities',
            date=month_start.replace(day=10),
            description='Electricity and water bill',
            created_by=admin_user,
        ))
        
        # Transportation
        records.append(FinancialRecord(
            amount=Decimal(str(random.randint(2000, 6000))),
            transaction_type='expense',
            category='transport',
            date=month_start.replace(day=20),
            description='Fuel and commute expenses',
            created_by=admin_user,
        ))
        
        # Entertainment (occasional)
        if month_offset % 3 != 2:
            records.append(FinancialRecord(
                amount=Decimal(str(random.randint(500, 3000))),
                transaction_type='expense',
                category='entertainment',
                date=month_start.replace(day=25),
                description='Movies and dining out',
                created_by=admin_user,
            ))
        
        # Healthcare (occasional)
        if month_offset % 3 == 0:
            records.append(FinancialRecord(
                amount=Decimal(str(random.randint(1000, 5000))),
                transaction_type='expense',
                category='healthcare',
                date=month_start.replace(day=12),
                description='Medical checkup and medicines',
                created_by=admin_user,
            ))
        
        # Investment income (occasional)
        if month_offset % 2 == 1:
            records.append(FinancialRecord(
                amount=Decimal(str(random.randint(2000, 8000))),
                transaction_type='income',
                category='investment',
                date=month_start.replace(day=18),
                description='Mutual fund returns',
                created_by=admin_user,
            ))
    
    FinancialRecord.objects.bulk_create(records)
    print(f"  ✓ Created {len(records)} financial records")


def main():
    print("=" * 50)
    print("  Finance Dashboard - Seed Data")
    print("=" * 50)
    print()
    
    users = create_users()
    create_financial_records(users['admin'])
    
    print()
    print("=" * 50)
    print("  Seed data created successfully!")
    print("=" * 50)
    print()
    print("  Login credentials:")
    print("  ─────────────────────────────────────")
    print("  Admin:   admin / admin123456")
    print("  Analyst: analyst / analyst123456")
    print("  Viewer:  viewer / viewer123456")
    print("  ─────────────────────────────────────")
    print()


if __name__ == '__main__':
    main()
