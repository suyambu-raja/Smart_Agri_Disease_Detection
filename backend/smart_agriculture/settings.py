"""
Smart Agriculture – Django Settings
====================================
Production-ready configuration with:
  • Firebase Firestore as the database
  • Firebase Authentication middleware
  • CORS support
  • Environment variable driven config (.env)
  • WhiteNoise for static files
  • Logging
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ──────────────────────────────────────────
# 1. BASE DIRECTORY & ENV
# ──────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / '.env')

# ──────────────────────────────────────────
# 2. SECURITY
# ──────────────────────────────────────────

SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-fallback-key-DO-NOT-USE-IN-PRODUCTION'
)

DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
]

# ──────────────────────────────────────────
# 3. INSTALLED APPS
# ──────────────────────────────────────────

INSTALLED_APPS = [
    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',

    # Project apps
    'users',
    'disease',
    'yield_prediction',
    'recommendation',
    'tts',
    'weather',
]

# ... existing code ...

FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'firebase-adminsdk.json')

# AI Services
# AI Services
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
DISEASE_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'disease_model.h5')
# ... existing code ...

# ──────────────────────────────────────────
# 4. MIDDLEWARE
# ──────────────────────────────────────────

MIDDLEWARE = [
    # CORS must be as high as possible
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise for serving static files in production
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ──────────────────────────────────────────
# 5. URL & WSGI / ASGI
# ──────────────────────────────────────────

ROOT_URLCONF = 'smart_agriculture.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smart_agriculture.wsgi.application'

# ──────────────────────────────────────────
# 6. DATABASE  (SQLite for all application data;
#    Firebase is used only for authentication)
# ──────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ──────────────────────────────────────────
# 7. PASSWORD VALIDATORS
# ──────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ──────────────────────────────────────────
# 8. INTERNATIONALIZATION
# ──────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────
# 9. STATIC FILES
# ──────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ──────────────────────────────────────────
# 10. DEFAULT AUTO FIELD
# ──────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ──────────────────────────────────────────
# 11. CORS CONFIGURATION
# ──────────────────────────────────────────

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:3000,http://localhost:5173'
    ).split(',')
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ──────────────────────────────────────────
# 12. DJANGO REST FRAMEWORK
# ──────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'smart_agriculture.firebase_auth.FirebaseAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'smart_agriculture.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
}

# ──────────────────────────────────────────
# 12b. SWAGGER / OPENAPI (drf-spectacular)
# ──────────────────────────────────────────

SPECTACULAR_SETTINGS = {
    'TITLE': 'Smart Agriculture API',
    'DESCRIPTION': 'Crop Disease Detection, Yield Prediction & Treatment Recommendations',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}

# ──────────────────────────────────────────
# 13. FIREBASE CONFIGURATION
# ──────────────────────────────────────────

FIREBASE_CREDENTIALS_PATH = os.getenv(
    'FIREBASE_CREDENTIALS_PATH',
    str(BASE_DIR / 'firebase_credentials.json')
)

# ──────────────────────────────────────────
# 14. ML MODEL PATHS
# ──────────────────────────────────────────

DISEASE_MODEL_PATH = os.getenv(
    'DISEASE_MODEL_PATH',
    str(BASE_DIR / 'models' / 'disease_model.h5')
)

YIELD_MODEL_PATH = os.getenv(
    'YIELD_MODEL_PATH',
    str(BASE_DIR / 'models' / 'yield_model.pkl')
)

# ──────────────────────────────────────────
# 15. LOGGING
# ──────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'smart_agriculture.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'disease': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'yield_prediction': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
