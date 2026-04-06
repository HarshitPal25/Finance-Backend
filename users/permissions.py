"""
Custom Permission Classes for Role-Based Access Control.

These permissions are used as decorators/classes on views to enforce
which roles can access which endpoints.

How Django REST Framework permissions work:
1. Every view can specify `permission_classes = [SomePermission]`
2. Before the view runs, DRF calls `has_permission()` on each permission class
3. If any permission returns False, DRF returns a 403 Forbidden response
4. The view code only runs if ALL permissions pass
"""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Only allows access to users with the 'admin' role.
    Used for: user management, creating/updating/deleting records.
    """
    message = "Only administrators can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsAnalystOrAdmin(BasePermission):
    """
    Allows access to users with 'analyst' or 'admin' roles.
    Used for: dashboard analytics, summary endpoints.
    """
    message = "Only analysts and administrators can access this resource."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('analyst', 'admin')
        )


class IsActiveUser(BasePermission):
    """
    Ensures the user's account is active.
    Inactive users are blocked from all actions.
    """
    message = "Your account has been deactivated. Contact an administrator."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active
        )


class ReadOnlyForViewers(BasePermission):
    """
    Viewers can only use safe (read-only) HTTP methods: GET, HEAD, OPTIONS.
    Analysts and Admins can use all methods.
    
    This is used on the records endpoints where viewers can read
    but cannot create, update, or delete.
    """
    message = "Viewers have read-only access. You cannot modify records."
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Safe methods (GET, HEAD, OPTIONS) are allowed for everyone
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        
        # Write methods require admin role
        return request.user.role == 'admin'
