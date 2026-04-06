"""
URL routing for Authentication endpoints.

Maps URL patterns to view functions. When Django receives a request,
it checks these patterns to find the matching view to handle it.
"""

from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
]
