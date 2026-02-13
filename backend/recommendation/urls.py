"""
Recommendation – URL Routing
==============================
"""

from django.urls import path
from .views import RecommendationView, AvailableDiseasesView

app_name = 'recommendation'

urlpatterns = [
    path('', RecommendationView.as_view(), name='recommendation'),
    path('diseases/', AvailableDiseasesView.as_view(), name='available-diseases'),
]
