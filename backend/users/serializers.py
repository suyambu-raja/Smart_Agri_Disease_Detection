"""
Users – Serializers
====================
Serializers for user profile data stored in Firestore.
"""

from rest_framework import serializers


class UserProfileSerializer(serializers.Serializer):
    """Serialize user profile data from Firestore."""
    uid = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    display_name = serializers.CharField(max_length=150, required=False, default='')
    phone_number = serializers.CharField(max_length=20, required=False, default='')
    location = serializers.CharField(max_length=255, required=False, default='')
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class UserRegistrationSerializer(serializers.Serializer):
    """Validate registration payload."""
    email = serializers.EmailField(required=True)
    display_name = serializers.CharField(max_length=150, required=True)
    phone_number = serializers.CharField(max_length=20, required=False, default='')
    location = serializers.CharField(max_length=255, required=False, default='')
