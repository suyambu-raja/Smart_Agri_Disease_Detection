"""
Users – URL Routing
====================
"""

from django.urls import path
from .views import UserProfileView, UserHealthView

app_name = 'users'

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('health/', UserHealthView.as_view(), name='user-health'),
]
