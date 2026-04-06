"""
Django Filter configuration for Financial Records.

Filters allow API consumers to query records by specific criteria
using URL query parameters. For example:
  GET /api/records/?category=food&transaction_type=expense&date_from=2024-01-01
"""

import django_filters
from .models import FinancialRecord


class FinancialRecordFilter(django_filters.FilterSet):
    """
    FilterSet for financial records.
    
    Supports filtering by:
    - transaction_type: exact match (income/expense)
    - category: exact match
    - date_from / date_to: date range filtering
    - amount_min / amount_max: amount range filtering
    - search: search in description text
    """
    
    date_from = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',  # gte = greater than or equal
        help_text="Filter records from this date (YYYY-MM-DD)"
    )
    date_to = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',  # lte = less than or equal
        help_text="Filter records up to this date (YYYY-MM-DD)"
    )
    amount_min = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte',
        help_text="Minimum amount"
    )
    amount_max = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte',
        help_text="Maximum amount"
    )
    
    class Meta:
        model = FinancialRecord
        fields = ['transaction_type', 'category', 'date_from', 'date_to',
                  'amount_min', 'amount_max']
