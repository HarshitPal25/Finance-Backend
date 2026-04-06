"""
Views for User Management (Admin only).

These endpoints allow administrators to view, update, and manage
all users in the system.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import User
from .serializers import (
    UserSerializer,
    UserRoleUpdateSerializer,
    UserStatusUpdateSerializer,
)
from .permissions import IsAdmin, IsActiveUser


@api_view(['GET'])
@permission_classes([IsActiveUser, IsAdmin])
def list_users(request):
    """
    List all users in the system.
    
    GET /api/users/
    Access: Admin only
    
    Supports pagination (configured globally in settings.py).
    """
    users = User.objects.all()
    
    # Apply search filter if provided
    search = request.query_params.get('search', '')
    if search:
        users = users.filter(username__icontains=search)
    
    # Apply role filter if provided
    role = request.query_params.get('role', '')
    if role:
        users = users.filter(role=role)
    
    # Apply active status filter
    is_active = request.query_params.get('is_active', '')
    if is_active.lower() in ('true', 'false'):
        users = users.filter(is_active=is_active.lower() == 'true')
    
    serializer = UserSerializer(users, many=True)
    return Response({
        'success': True,
        'count': users.count(),
        'data': serializer.data,
    })


@api_view(['GET'])
@permission_classes([IsActiveUser, IsAdmin])
def get_user(request, user_id):
    """
    Get details of a specific user.
    
    GET /api/users/<user_id>/
    Access: Admin only
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 404,
                'message': f'User with ID {user_id} not found.',
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializer(user)
    return Response({
        'success': True,
        'data': serializer.data,
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([IsActiveUser, IsAdmin])
def update_user(request, user_id):
    """
    Update a user's information.
    
    PUT/PATCH /api/users/<user_id>/
    Access: Admin only
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 404,
                'message': f'User with ID {user_id} not found.',
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'User updated successfully.',
            'data': serializer.data,
        })
    
    return Response({
        'success': False,
        'error': {
            'code': 400,
            'message': 'Update failed. Please check your input.',
            'details': serializer.errors,
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsActiveUser, IsAdmin])
def update_user_role(request, user_id):
    """
    Change a user's role.
    
    PUT /api/users/<user_id>/role/
    Access: Admin only
    
    Request body:
    { "role": "analyst" }
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 404,
                'message': f'User with ID {user_id} not found.',
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Prevent admin from changing their own role (safety check)
    if user.id == request.user.id:
        return Response({
            'success': False,
            'error': {
                'code': 400,
                'message': 'You cannot change your own role.',
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserRoleUpdateSerializer(data=request.data)
    if serializer.is_valid():
        user.role = serializer.validated_data['role']
        user.save()
        return Response({
            'success': True,
            'message': f"User '{user.username}' role updated to '{user.role}'.",
            'data': UserSerializer(user).data,
        })
    
    return Response({
        'success': False,
        'error': {
            'code': 400,
            'message': 'Invalid role.',
            'details': serializer.errors,
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsActiveUser, IsAdmin])
def update_user_status(request, user_id):
    """
    Activate or deactivate a user.
    
    PUT /api/users/<user_id>/status/
    Access: Admin only
    
    Request body:
    { "is_active": false }
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 404,
                'message': f'User with ID {user_id} not found.',
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Prevent admin from deactivating themselves
    if user.id == request.user.id:
        return Response({
            'success': False,
            'error': {
                'code': 400,
                'message': 'You cannot change your own status.',
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserStatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        user.is_active = serializer.validated_data['is_active']
        user.save()
        status_text = "activated" if user.is_active else "deactivated"
        return Response({
            'success': True,
            'message': f"User '{user.username}' has been {status_text}.",
            'data': UserSerializer(user).data,
        })
    
    return Response({
        'success': False,
        'error': {
            'code': 400,
            'message': 'Invalid status value.',
            'details': serializer.errors,
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsActiveUser, IsAdmin])
def delete_user(request, user_id):
    """
    Delete a user from the system.
    
    DELETE /api/users/<user_id>/
    Access: Admin only
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 404,
                'message': f'User with ID {user_id} not found.',
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Prevent admin from deleting themselves
    if user.id == request.user.id:
        return Response({
            'success': False,
            'error': {
                'code': 400,
                'message': 'You cannot delete your own account.',
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    username = user.username
    user.delete()
    
    return Response({
        'success': True,
        'message': f"User '{username}' has been deleted.",
    }, status=status.HTTP_200_OK)
