"""URL routing for Financial Records endpoints."""

from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    path('', views.record_list_create, name='list-create'),
    path('<int:record_id>/', views.record_detail, name='detail'),
]
