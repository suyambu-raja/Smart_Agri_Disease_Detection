"""
Users – Views
==============
API views for user profile management.
All data is stored in Firebase Firestore under the 'users' collection.
"""

import logging
from datetime import datetime, timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from smart_agriculture.firebase_init import get_firestore_client
from .serializers import UserProfileSerializer, UserRegistrationSerializer

logger = logging.getLogger(__name__)


class UserProfileView(APIView):
    """
    GET  /api/users/profile/   → Retrieve current user's profile
    POST /api/users/profile/   → Create / update current user's profile
    """

    def get(self, request):
        """Retrieve the authenticated user's profile from Firestore."""
        try:
            db = get_firestore_client()
            user_ref = db.collection('users').document(request.user.uid)
            user_doc = user_ref.get()

            if not user_doc.exists:
                return Response(
                    {'success': False, 'error': 'User profile not found.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            data = user_doc.to_dict()
            data['uid'] = request.user.uid
            serializer = UserProfileSerializer(data)

            return Response({
                'success': True,
                'data': serializer.data,
            })

        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        """Create or update the authenticated user's profile."""
        serializer = UserRegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            db = get_firestore_client()
            now = datetime.now(timezone.utc)

            profile_data = {
                **serializer.validated_data,
                'uid': request.user.uid,
                'updated_at': now,
            }

            user_ref = db.collection('users').document(request.user.uid)
            user_doc = user_ref.get()

            if not user_doc.exists:
                profile_data['created_at'] = now
                user_ref.set(profile_data)
                logger.info(f"Created profile for user {request.user.uid}")
                msg = 'Profile created successfully.'
                resp_status = status.HTTP_201_CREATED
            else:
                user_ref.update(profile_data)
                logger.info(f"Updated profile for user {request.user.uid}")
                msg = 'Profile updated successfully.'
                resp_status = status.HTTP_200_OK

            return Response(
                {'success': True, 'message': msg, 'data': profile_data},
                status=resp_status,
            )

        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserHealthView(APIView):
    """
    GET /api/users/health/  → Public health check for the users service.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'status': 'Users service is running.'})
