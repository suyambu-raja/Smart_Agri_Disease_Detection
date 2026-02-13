"""
Recommendation – Views
=======================
GET /api/recommendation/?disease_name=Tomato+Early+Blight
Returns fertilizer and pesticide suggestions for the given disease.
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .knowledge_base import get_recommendation, RECOMMENDATIONS
from .serializers import RecommendationRequestSerializer

logger = logging.getLogger(__name__)


class RecommendationView(APIView):
    """
    GET /api/recommendation/?disease_name=<disease>

    Query params:
        disease_name (str): The disease name to look up.

    Returns recommendations for treatment: fertilizers,
    pesticides, organic treatments, and preventive measures.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        serializer = RecommendationRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        disease_name = serializer.validated_data['disease_name']
        recommendation = get_recommendation(disease_name)

        if recommendation is None:
            logger.warning(f"No recommendation found for: {disease_name}")
            return Response(
                {
                    'success': False,
                    'error': f'No recommendations found for "{disease_name}".',
                    'available_diseases': sorted(RECOMMENDATIONS.keys()),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        logger.info(f"Recommendation served for: {disease_name}")
        return Response({
            'success': True,
            'disease_name': disease_name,
            **recommendation,
        })


class AvailableDiseasesView(APIView):
    """
    GET /api/recommendation/diseases/
    Returns a list of all diseases the system can provide recommendations for.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({
            'success': True,
            'diseases': sorted(RECOMMENDATIONS.keys()),
            'count': len(RECOMMENDATIONS),
        })
