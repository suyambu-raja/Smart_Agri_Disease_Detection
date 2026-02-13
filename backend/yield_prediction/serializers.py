"""
Yield Prediction – Serializers
================================
"""

from rest_framework import serializers


class YieldInputSerializer(serializers.Serializer):
    """Validate yield prediction input."""
    district = serializers.CharField(max_length=100, required=True)
    soil_type = serializers.CharField(max_length=100, required=True)
    crop = serializers.CharField(max_length=100, required=True)
    rainfall = serializers.FloatField(required=True, min_value=0, max_value=5000)
    temperature = serializers.FloatField(required=True, min_value=-10, max_value=60)


class YieldOutputSerializer(serializers.Serializer):
    """Serialize yield prediction result."""
    predicted_yield = serializers.IntegerField()
    unit = serializers.CharField()
    risk_level = serializers.CharField()
