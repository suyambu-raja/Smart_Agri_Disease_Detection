"""
Disease Detection – Serializers
================================
"""

from rest_framework import serializers


class DiseaseImageSerializer(serializers.Serializer):
    """Validate the uploaded image file."""
    image = serializers.ImageField(
        required=True,
        help_text='Upload a crop leaf image (JPEG/PNG).',
    )


class DiseasePredictionResponseSerializer(serializers.Serializer):
    """Serialize the prediction result."""
    disease_name = serializers.CharField()
    confidence = serializers.FloatField()
    is_healthy = serializers.BooleanField()
