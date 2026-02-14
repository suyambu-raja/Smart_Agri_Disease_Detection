from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['uid', 'email', 'display_name', 'phone_number', 'location', 'language', 'created_at', 'updated_at']
        read_only_fields = ['uid', 'created_at', 'updated_at']

class UserRegistrationSerializer(serializers.Serializer):
    """Validate registration payload."""
    email = serializers.EmailField(required=True)
    display_name = serializers.CharField(max_length=150, required=True)
    phone_number = serializers.CharField(max_length=20, required=False, default='')
    location = serializers.CharField(max_length=255, required=False, default='')
