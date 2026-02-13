"""
Yield Prediction – Views
=========================
POST /api/yield/predict/  →  Submit parameters, get yield prediction.
GET  /api/yield/history/  →  Retrieve past predictions from Django DB.
"""

import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import YieldInputSerializer
from .ml_model import predict_yield
from .models import YieldPrediction

logger = logging.getLogger(__name__)


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


class YieldPredictView(APIView):
    """
    POST /api/yield/predict/
    Accept: application/json
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = YieldInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data

        try:
            result = predict_yield(
                district=data['district'],
                soil_type=data['soil_type'],
                crop=data['crop'],
                rainfall=data['rainfall'],
                temperature=data['temperature'],
            )

            # Save to Django database if user is authenticated
            user_uid = _get_uid_from_token(request)
            if user_uid:
                YieldPrediction.objects.create(
                    user_uid=user_uid,
                    district=data['district'],
                    soil_type=data['soil_type'],
                    crop=data['crop'],
                    rainfall=data['rainfall'],
                    temperature=data['temperature'],
                    predicted_yield=result['predicted_yield'],
                    unit=result['unit'],
                    risk_level=result['risk_level'],
                )
                logger.info(f"Saved yield prediction to DB for user {user_uid[:8]}...")

            logger.info(
                f"Yield prediction: {data['crop']} in {data['district']} → "
                f"{result['predicted_yield']} {result['unit']} (Risk: {result['risk_level']})"
            )

            return Response({
                'success': True,
                'predicted_yield': result['predicted_yield'],
                'unit': result['unit'],
                'risk_level': result['risk_level'],
            })

        except Exception as e:
            logger.error(f"Yield prediction error: {e}", exc_info=True)
            return Response(
                {'success': False, 'error': f'Prediction failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class YieldHistoryView(APIView):
    """
    GET /api/yield/history/
    Return the authenticated user's past yield predictions from Django DB.
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

        predictions = YieldPrediction.objects.filter(user_uid=user_uid)[:50]

        data = [
            {
                'id': str(p.id),
                'district': p.district,
                'soil_type': p.soil_type,
                'crop': p.crop,
                'rainfall': p.rainfall,
                'temperature': p.temperature,
                'predicted_yield': p.predicted_yield,
                'unit': p.unit,
                'risk_level': p.risk_level,
                'created_at': p.created_at.isoformat(),
            }
            for p in predictions
        ]

        return Response({'success': True, 'data': data})
