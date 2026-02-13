"""
Yield Prediction – URL Routing
================================
"""

from django.urls import path
from .views import YieldPredictView, YieldHistoryView

app_name = 'yield_prediction'

urlpatterns = [
    path('predict/', YieldPredictView.as_view(), name='yield-predict'),
    path('history/', YieldHistoryView.as_view(), name='yield-history'),
]
