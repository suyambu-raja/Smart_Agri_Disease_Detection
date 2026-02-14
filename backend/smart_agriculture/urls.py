"""
Smart Agriculture – Root URL Configuration
============================================
Routes each app to its own namespace under /api/.
Includes Swagger UI and ReDoc for interactive API documentation.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def health_check(request):
    """Simple health-check endpoint for load balancers / uptime monitors."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'Smart Agriculture API',
        'version': '1.0.0',
    })


urlpatterns = [
    # Health check (no auth required)
    path('', health_check, name='health-check'),
    path('health/', health_check, name='health-check-alt'),

    # ── Swagger / OpenAPI Docs ──
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Django admin (optional, can be removed in production)
    path('admin/', admin.site.urls),

    # API routes
    path('api/users/', include('users.urls')),
    path('api/disease/', include('disease.urls')),
    path('api/yield/', include('yield_prediction.urls')),
    path('api/recommendation/', include('recommendation.urls')),
    path('api/tts/', include('tts.urls')),
    path('api/weather/', include('weather.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
