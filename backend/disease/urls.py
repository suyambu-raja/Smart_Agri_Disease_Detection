"""
Disease Detection – URL Routing
================================
"""

from django.urls import path
from .views import DiseasePredictView, DiseaseHistoryView

app_name = 'disease'

urlpatterns = [
    path('predict/', DiseasePredictView.as_view(), name='disease-predict'),
    path('history/', DiseaseHistoryView.as_view(), name='disease-history'),
]
