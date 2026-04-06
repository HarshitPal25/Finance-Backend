"""
URL routing for User Management endpoints (Admin only).
"""

from django.urls import path
from . import user_views

app_name = 'users'

urlpatterns = [
    path('', user_views.list_users, name='list'),
    path('<int:user_id>/', user_views.get_user, name='detail'),
    path('<int:user_id>/update/', user_views.update_user, name='update'),
    path('<int:user_id>/role/', user_views.update_user_role, name='update-role'),
    path('<int:user_id>/status/', user_views.update_user_status, name='update-status'),
    path('<int:user_id>/delete/', user_views.delete_user, name='delete'),
]
