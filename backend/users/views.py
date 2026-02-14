from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import UserProfile
from .serializers import UserProfileSerializer, UserRegistrationSerializer
import logging

logger = logging.getLogger(__name__)

class UserProfileView(APIView):
    """
    GET  /api/users/profile/   → Retrieve current user's profile from SQL DB
    POST /api/users/profile/   → Create / update current user's profile
    PATCH /api/users/profile/  → Partially update
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, uid):
        # Helper to get or create
        obj, created = UserProfile.objects.get_or_create(uid=uid)
        return obj

    def get(self, request):
        try:
            profile = self.get_object(request.user.uid)
            serializer = UserProfileSerializer(profile)
            return Response({
                'success': True,
                'data': serializer.data,
            })
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            return Response({'success': False, 'error': str(e)}, status=500)

    def post(self, request):
        # Create/Update logic via POST
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=400)
            
        try:
            profile = self.get_object(request.user.uid)
            
            # Update fields from validated data
            data = serializer.validated_data
            for key, val in data.items():
                if hasattr(profile, key):
                   setattr(profile, key, val)
            profile.save()
            
            return Response({
                'success': True,
                'message': 'Profile saved.',
                'data': UserProfileSerializer(profile).data
            })
        except Exception as e:
             logger.error(f"Error saving profile: {e}")
             return Response({'success': False, 'error': str(e)}, status=500)

    def patch(self, request):
        try:
            profile = self.get_object(request.user.uid)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True, 
                    'message': 'Profile updated.',
                    'data': serializer.data
                })
            return Response({'success': False, 'errors': serializer.errors}, status=400)
        except Exception as e:
            logger.error(f"Error patching profile: {e}")
            return Response({'success': False, 'error': str(e)}, status=500)


class UserHealthView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({'status': 'Users service is running.'})
