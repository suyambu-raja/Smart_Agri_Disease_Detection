"""
Recommendation – Serializers
==============================
"""

from rest_framework import serializers


class RecommendationRequestSerializer(serializers.Serializer):
    """Validate recommendation query parameters."""
    disease_name = serializers.CharField(
        max_length=200,
        required=True,
        help_text='The disease name (e.g., "Tomato Early Blight").',
    )
    lang = serializers.CharField(
        required=False,
        default='en',
        help_text='Language code (en/ta). Default: en',
    )


class RecommendationResponseSerializer(serializers.Serializer):
    """Serialize recommendation output."""
    disease_name = serializers.CharField()
    fertilizers = serializers.ListField(child=serializers.CharField())
    pesticides = serializers.ListField(child=serializers.CharField())
    organic_treatments = serializers.ListField(child=serializers.CharField())
    preventive_measures = serializers.ListField(child=serializers.CharField())
