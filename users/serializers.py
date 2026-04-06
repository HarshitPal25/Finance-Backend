"""
Serializers for the Users app.

Serializers convert complex data (like Django model instances) to/from
JSON format that can be sent over HTTP. Think of them as translators
between Python objects and JSON.

They also handle validation - checking that incoming data is correct
before saving it to the database.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Handles user registration.
    
    - Takes username, email, password, and optional role
    - Validates the data
    - Creates the user with a hashed password (never stores plain text!)
    """
    password = serializers.CharField(
        write_only=True,  # Password is never included in responses
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    role = serializers.ChoiceField(
        choices=User.Role.choices,
        default=User.Role.VIEWER,
        required=False,
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_email(self, value):
        """Ensure email is unique (case-insensitive)."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def create(self, validated_data):
        """
        Create user with hashed password.
        
        We use create_user() instead of create() because create_user()
        automatically hashes the password. Storing plain text passwords
        is a critical security vulnerability.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', User.Role.VIEWER),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Handles user login validation.
    
    Takes username and password, validates credentials,
    and returns the authenticated user object.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """
        Validate login credentials.
        
        Django's authenticate() function checks the username/password
        combination and returns the user if valid, or None if invalid.
        """
        user = authenticate(
            username=data['username'],
            password=data['password'],
        )
        
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        
        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")
        
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    General user serializer for reading/updating user data.
    
    Note: password is excluded from this serializer.
    Admin users use this to view and manage other users.
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserRoleUpdateSerializer(serializers.Serializer):
    """Serializer specifically for updating a user's role."""
    role = serializers.ChoiceField(choices=User.Role.choices)


class UserStatusUpdateSerializer(serializers.Serializer):
    """Serializer specifically for activating/deactivating a user."""
    is_active = serializers.BooleanField()
