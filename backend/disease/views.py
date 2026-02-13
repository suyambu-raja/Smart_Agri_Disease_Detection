"""
Disease Detection – Views
==========================
POST /api/disease/predict/  →  Upload image, get disease prediction.
GET  /api/disease/history/  →  Retrieve past predictions from Django DB.
"""

import logging
import numpy as np
from io import BytesIO

from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from .serializers import DiseaseImageSerializer, DiseasePredictionResponseSerializer
from .ml_model import predict_disease
from .models import DiseasePrediction

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────
# Constants
# ──────────────────────────────────────────

IMAGE_SIZE = (224, 224)
MAX_FILE_SIZE_MB = 10
ALLOWED_CONTENT_TYPES = [
    'image/jpeg', 'image/png', 'image/jpg', 'image/webp',
]


def _get_uid_from_token(request):
    """Try to extract Firebase UID from Authorization header."""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split('Bearer ')[1]
    try:
        from smart_agriculture.firebase_init import get_firebase_app
        get_firebase_app()
        from firebase_admin import auth as firebase_auth
        decoded = firebase_auth.verify_id_token(token)
        return decoded.get('uid')
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None


class DiseasePredictView(APIView):
    """
    POST /api/disease/predict/
    Accept: multipart/form-data with field 'image'
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        request={'multipart/form-data': DiseaseImageSerializer},
        responses={200: DiseasePredictionResponseSerializer},
        description='Upload a crop leaf image to detect disease using AI.',
    )
    def post(self, request):
        serializer = DiseaseImageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_file = serializer.validated_data['image']

        if image_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return Response(
                {'success': False, 'error': f'Image exceeds {MAX_FILE_SIZE_MB} MB limit.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if image_file.content_type not in ALLOWED_CONTENT_TYPES:
            return Response(
                {
                    'success': False,
                    'error': f'Unsupported image type: {image_file.content_type}. '
                             f'Allowed: {", ".join(ALLOWED_CONTENT_TYPES)}',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            img = Image.open(BytesIO(image_file.read())).convert('RGB')
            img = img.resize(IMAGE_SIZE)

            img_array = np.array(img, dtype=np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Get crop filter if provided
            crop_filter = request.data.get('crop', None)

            result = predict_disease(img_array, crop_filter=crop_filter)

            # Save to Django database if user is authenticated
            user_uid = _get_uid_from_token(request)
            if user_uid:
                # Reset file pointer to beginning so Django can save it
                image_file.seek(0)
                
                DiseasePrediction.objects.create(
                    user_uid=user_uid,
                    disease_name=result['disease_name'],
                    confidence=result['confidence'],
                    is_healthy=result['is_healthy'],
                    raw_label=result.get('raw_label', ''),
                    filename=image_file.name or '',
                    image=image_file  # Save the actual image file
                )
                logger.info(f"Saved disease prediction to DB for user {user_uid[:8]}...")
            else:
                logger.info("Unauthenticated prediction — not saved to DB.")

            return Response({
                'success': True,
                'disease_name': result['disease_name'],
                'confidence': result['confidence'],
                'is_healthy': result['is_healthy'],
            })

        except Exception as e:
            logger.error(f"Disease prediction error: {e}", exc_info=True)
            return Response(
                {'success': False, 'error': f'Prediction failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DiseaseHistoryView(APIView):
    """
    GET /api/disease/history/
    Return the authenticated user's past disease predictions from Django DB.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        user_uid = _get_uid_from_token(request)
        if not user_uid:
            return Response(
                {'success': False, 'error': 'Authentication required. Please log in.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        predictions = DiseasePrediction.objects.filter(user_uid=user_uid)[:50]

        data = []
        for p in predictions:
            image_url = ''
            if p.image:
                image_url = request.build_absolute_uri(p.image.url)
            
            data.append({
                'id': str(p.id),
                'disease_name': p.disease_name,
                'confidence': p.confidence,
                'is_healthy': p.is_healthy,
                'raw_label': p.raw_label,
                'filename': p.filename,
                'image_url': image_url,  # New field
                'created_at': p.created_at.isoformat(),
            })

        return Response({'success': True, 'data': data})
