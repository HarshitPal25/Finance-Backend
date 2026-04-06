"""
finance_backend URL Configuration

All API endpoints are prefixed with /api/ for clarity.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/users/', include('users.user_urls')),
    path('api/records/', include('records.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
