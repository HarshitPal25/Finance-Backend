"""URL routing for Dashboard endpoints."""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('summary/', views.dashboard_summary, name='summary'),
    path('category-breakdown/', views.category_breakdown, name='category-breakdown'),
    path('trends/', views.monthly_trends, name='trends'),
    path('recent-activity/', views.recent_activity, name='recent-activity'),
]
