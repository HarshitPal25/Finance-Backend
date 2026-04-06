"""
Serializers for Financial Records.

Handles validation of financial data and conversion between
JSON and Django model instances.
"""

from rest_framework import serializers
from .models import FinancialRecord
from decimal import Decimal


class FinancialRecordSerializer(serializers.ModelSerializer):
    """
    Main serializer for financial records.
    
    Handles:
    - Creating new records (with validation)
    - Updating existing records
    - Reading record data (including the creator's username)
    """
    
    # Show the username of who created the record (read-only)
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
    )
    
    # Show human-readable labels for type and category
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True,
    )
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True,
    )
    
    class Meta:
        model = FinancialRecord
        fields = [
            'id', 'amount', 'transaction_type', 'transaction_type_display',
            'category', 'category_display', 'date', 'description',
            'created_by', 'created_by_username',
            'is_deleted', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'is_deleted', 'created_at', 'updated_at']
    
    def validate_amount(self, value):
        """Ensure amount is a positive number."""
        if value <= Decimal('0'):
            raise serializers.ValidationError("Amount must be a positive number.")
        if value > Decimal('999999999999.99'):
            raise serializers.ValidationError("Amount is too large.")
        return value
    
    def validate_date(self, value):
        """Ensure date is not in the far future."""
        from datetime import date, timedelta
        if value > date.today() + timedelta(days=365):
            raise serializers.ValidationError("Date cannot be more than 1 year in the future.")
        return value
    
    def create(self, validated_data):
        """
        Set the created_by field to the currently logged-in user.
        This is automatically passed from the view via serializer context.
        """
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class FinancialRecordListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing records.
    Returns fewer fields for better performance when listing many records.
    """
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
    )
    
    class Meta:
        model = FinancialRecord
        fields = [
            'id', 'amount', 'transaction_type', 'category',
            'date', 'description', 'created_by_username', 'created_at',
        ]
