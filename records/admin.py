"""Register FinancialRecord model with Django admin."""

from django.contrib import admin
from .models import FinancialRecord


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    """Admin configuration for financial records."""
    list_display = ['id', 'amount', 'transaction_type', 'category', 'date', 'created_by', 'is_deleted']
    list_filter = ['transaction_type', 'category', 'is_deleted', 'date']
    search_fields = ['description', 'created_by__username']
    date_hierarchy = 'date'
