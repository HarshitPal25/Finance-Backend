"""
Financial Record Model.

Represents a financial transaction/entry in the system.
Each record is linked to the user who created it.
Supports soft delete (records are hidden but not permanently removed).
"""

from django.db import models
from django.conf import settings


class FinancialRecord(models.Model):
    """
    A single financial transaction entry.
    
    Soft Delete: Instead of permanently deleting records, we set
    is_deleted=True. This preserves data integrity and allows
    recovery of accidentally deleted records.
    """
    
    class TransactionType(models.TextChoices):
        INCOME = 'income', 'Income'
        EXPENSE = 'expense', 'Expense'
    
    class Category(models.TextChoices):
        """Pre-defined categories for financial records."""
        SALARY = 'salary', 'Salary'
        FREELANCE = 'freelance', 'Freelance'
        INVESTMENT = 'investment', 'Investment'
        FOOD = 'food', 'Food & Dining'
        TRANSPORT = 'transport', 'Transportation'
        UTILITIES = 'utilities', 'Utilities'
        ENTERTAINMENT = 'entertainment', 'Entertainment'
        HEALTHCARE = 'healthcare', 'Healthcare'
        EDUCATION = 'education', 'Education'
        SHOPPING = 'shopping', 'Shopping'
        RENT = 'rent', 'Rent'
        OTHER = 'other', 'Other'
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Transaction amount (positive number)"
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
        help_text="Type of transaction: income or expense"
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        help_text="Category of the transaction"
    )
    date = models.DateField(
        help_text="Date of the transaction"
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="Optional notes about this transaction"
    )
    
    # Who created this record
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='financial_records',
        help_text="The user who created this record"
    )
    
    # Soft delete flag
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft-deleted records are hidden but not removed from database"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['category']),
            models.Index(fields=['date']),
            models.Index(fields=['is_deleted']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()}: ₹{self.amount} ({self.get_category_display()}) on {self.date}"
    
    def soft_delete(self):
        """Mark this record as deleted without removing it from the database."""
        self.is_deleted = True
        self.save()
    
    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.save()
