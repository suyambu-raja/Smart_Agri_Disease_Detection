"""
Custom Exception Handler for DRF
==================================
Provides consistent JSON error responses across all endpoints.
"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Wrap DRF's default exception handler with a consistent envelope:
    {
      "success": false,
      "error": "<error message>",
      "detail": "<optional detail>"
    }
    """
    # Call DRF's default handler first
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            'success': False,
            'error': str(exc),
            'status_code': response.status_code,
        }

        # Preserve original detail if present
        if hasattr(response, 'data'):
            if isinstance(response.data, dict):
                custom_data['detail'] = response.data
            elif isinstance(response.data, list):
                custom_data['detail'] = response.data

        response.data = custom_data
        return response

    # Unhandled exceptions → 500
    logger.exception(f"Unhandled exception in {context.get('view', 'unknown')}: {exc}")
    return Response(
        {
            'success': False,
            'error': 'Internal server error',
            'status_code': 500,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
