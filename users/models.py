"""
User Model - Custom user model with role-based access control.

Roles:
- VIEWER: Can only view dashboard data and recent activity
- ANALYST: Can view records and access analytics/insights
- ADMIN: Full access - can create, update, delete records and manage users
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's built-in AbstractUser.
    
    We extend AbstractUser instead of AbstractBaseUser because it gives us
    all of Django's auth features (login, password hashing, etc.) for free,
    while letting us add custom fields like 'role'.
    """
    
    class Role(models.TextChoices):
        """
        Enum-like class for user roles.
        TextChoices provides human-readable labels and validation automatically.
        """
        VIEWER = 'viewer', 'Viewer'
        ANALYST = 'analyst', 'Analyst'
        ADMIN = 'admin', 'Admin'
    
    email = models.EmailField(unique=True, help_text="User's email address (must be unique)")
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text="User's role determines what actions they can perform"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive users cannot log in or perform any actions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_analyst(self):
        return self.role == self.Role.ANALYST
    
    @property
    def is_viewer(self):
        return self.role == self.Role.VIEWER
