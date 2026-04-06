"""
Views for Authentication (Register & Login).

Views are the functions/classes that handle incoming HTTP requests.
When a user hits an endpoint like POST /api/auth/register, Django
routes the request to the corresponding view, which processes it
and returns a response.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserRegistrationSerializer, UserLoginSerializer


@api_view(['POST'])
@permission_classes([AllowAny])  # Anyone can register (no auth needed)
def register(request):
    """
    Register a new user.
    
    POST /api/auth/register
    
    Request body:
    {
        "username": "john",
        "email": "john@example.com",
        "password": "securepassword123",
        "role": "viewer"  // optional, defaults to "viewer"
    }
    
    Returns: User data + JWT tokens
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens for the new user so they can
        # start making authenticated requests immediately
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'User registered successfully.',
            'data': {
                'user': UserRegistrationSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'error': {
            'code': 400,
            'message': 'Registration failed. Please check your input.',
            'details': serializer.errors,
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # Anyone can log in
def login(request):
    """
    Log in and receive JWT tokens.
    
    POST /api/auth/login
    
    Request body:
    {
        "username": "john",
        "password": "securepassword123"
    }
    
    Returns: User data + JWT tokens
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful.',
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'error': {
            'code': 401,
            'message': 'Login failed. Invalid credentials.',
            'details': serializer.errors,
        }
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def profile(request):
    """
    Get the currently logged-in user's profile.
    
    GET /api/auth/profile
    Headers: Authorization: Bearer <token>
    
    Returns: Current user's data
    """
    user = request.user
    return Response({
        'success': True,
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
        }
    })
