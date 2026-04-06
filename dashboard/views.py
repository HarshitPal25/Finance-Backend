"""
Dashboard Analytics Views.

These endpoints provide aggregated/summary data for a finance dashboard.
Instead of returning raw records, they return calculated statistics
like totals, averages, breakdowns, and trends.

This is what makes a backend useful for a dashboard UI - the frontend
shouldn't have to calculate these things itself.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncMonth, TruncWeek
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from records.models import FinancialRecord
from users.permissions import IsActiveUser, IsAnalystOrAdmin


@api_view(['GET'])
@permission_classes([IsActiveUser, IsAnalystOrAdmin])
def dashboard_summary(request):
    """
    Get overall financial summary.
    
    GET /api/dashboard/summary/
    Access: Analyst, Admin
    
    Returns:
    - Total income
    - Total expenses
    - Net balance (income - expenses)
    - Total number of records
    - Average transaction amount
    """
    records = FinancialRecord.objects.filter(is_deleted=False)
    
    # Calculate totals using Django's aggregation
    # Q objects allow us to add conditions to aggregations
    totals = records.aggregate(
        total_income=Sum('amount', filter=Q(transaction_type='income')) or Decimal('0'),
        total_expenses=Sum('amount', filter=Q(transaction_type='expense')) or Decimal('0'),
        total_records=Count('id'),
    )
    
    total_income = Decimal(totals['total_income'] or 0)
    total_expenses = Decimal(totals['total_expenses'] or 0)
    net_balance = total_income - total_expenses
    
    return Response({
        'success': True,
        'data': {
            'total_income': f'{total_income:.2f}',
            'total_expenses': f'{total_expenses:.2f}',
            'net_balance': f'{net_balance:.2f}',
            'total_records': totals['total_records'],
            'profit_status': 'profit' if net_balance > 0 else ('loss' if net_balance < 0 else 'break-even'),
        }
    })


@api_view(['GET'])
@permission_classes([IsActiveUser, IsAnalystOrAdmin])
def category_breakdown(request):
    """
    Get spending/income breakdown by category.
    
    GET /api/dashboard/category-breakdown/
    Access: Analyst, Admin
    
    Query params:
    - type: 'income' or 'expense' (optional, defaults to both)
    
    Returns: List of categories with their totals and percentages.
    """
    records = FinancialRecord.objects.filter(is_deleted=False)
    
    # Optional filter by transaction type
    tx_type = request.query_params.get('type', '')
    if tx_type in ('income', 'expense'):
        records = records.filter(transaction_type=tx_type)
    
    # Group by category and sum amounts
    breakdown = (
        records
        .values('category')
        .annotate(
            total=Sum('amount'),
            count=Count('id'),
        )
        .order_by('-total')
    )
    
    # Calculate grand total for percentage calculation
    grand_total = sum(item['total'] for item in breakdown) if breakdown else Decimal('0')
    
    # Format response with percentages
    result = []
    for item in breakdown:
        percentage = (item['total'] / grand_total * 100) if grand_total > 0 else 0
        result.append({
            'category': item['category'],
            'category_display': dict(FinancialRecord.Category.choices).get(item['category'], item['category']),
            'total': str(item['total']),
            'count': item['count'],
            'percentage': round(float(percentage), 2),
        })
    
    return Response({
        'success': True,
        'data': {
            'grand_total': str(grand_total),
            'breakdown': result,
        }
    })


@api_view(['GET'])
@permission_classes([IsActiveUser, IsAnalystOrAdmin])
def monthly_trends(request):
    """
    Get monthly income/expense trends.
    
    GET /api/dashboard/trends/
    Access: Analyst, Admin
    
    Query params:
    - months: number of months to look back (default: 6)
    
    Returns: Monthly totals for income and expenses.
    """
    months_back = int(request.query_params.get('months', 6))
    months_back = min(months_back, 24)  # Cap at 24 months
    
    start_date = date.today() - timedelta(days=months_back * 30)
    
    records = FinancialRecord.objects.filter(
        is_deleted=False,
        date__gte=start_date,
    )
    
    # Group by month using TruncMonth
    # TruncMonth converts a date to the first day of its month
    monthly_data = (
        records
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(
            income=Sum('amount', filter=Q(transaction_type='income')),
            expenses=Sum('amount', filter=Q(transaction_type='expense')),
            count=Count('id'),
        )
        .order_by('month')
    )
    
    trends = []
    for item in monthly_data:
        income = item['income'] or Decimal('0')
        expenses = item['expenses'] or Decimal('0')
        trends.append({
            'month': item['month'].strftime('%Y-%m'),
            'income': str(income),
            'expenses': str(expenses),
            'net': str(income - expenses),
            'transaction_count': item['count'],
        })
    
    return Response({
        'success': True,
        'data': {
            'period': f'Last {months_back} months',
            'trends': trends,
        }
    })


@api_view(['GET'])
@permission_classes([IsActiveUser])  # All authenticated users can see recent activity
def recent_activity(request):
    """
    Get recent financial activity.
    
    GET /api/dashboard/recent-activity/
    Access: All authenticated users (including viewers)
    
    Query params:
    - limit: number of records (default: 10, max: 50)
    
    Returns: Most recent financial records.
    """
    limit = int(request.query_params.get('limit', 10))
    limit = min(limit, 50)  # Cap at 50
    
    records = (
        FinancialRecord.objects
        .filter(is_deleted=False)
        .select_related('created_by')
        .order_by('-date', '-created_at')[:limit]
    )
    
    activity = []
    for record in records:
        activity.append({
            'id': record.id,
            'amount': str(record.amount),
            'transaction_type': record.transaction_type,
            'category': record.category,
            'category_display': record.get_category_display(),
            'date': record.date.isoformat(),
            'description': record.description,
            'created_by': record.created_by.username,
            'created_at': record.created_at.isoformat(),
        })
    
    return Response({
        'success': True,
        'count': len(activity),
        'data': activity,
    })
