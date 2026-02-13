"""
Firebase Authentication for Django REST Framework
===================================================
Custom DRF authentication class that verifies Firebase ID tokens.
Extracts the token from the Authorization header (Bearer <token>).
"""

import logging
from rest_framework import authentication, exceptions
from firebase_admin import auth

from smart_agriculture.firebase_init import get_firebase_app

logger = logging.getLogger(__name__)


class FirebaseUser:
    """
    Lightweight user object that wraps a decoded Firebase token.
    This replaces Django's User model for Firebase-authenticated requests.
    """

    def __init__(self, decoded_token: dict):
        self.uid = decoded_token.get('uid', '')
        self.email = decoded_token.get('email', '')
        self.name = decoded_token.get('name', '')
        self.email_verified = decoded_token.get('email_verified', False)
        self.decoded_token = decoded_token
        # DRF expects these attributes
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def __str__(self):
        return self.email or self.uid

    @property
    def pk(self):
        return self.uid


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    DRF Authentication backend that validates Firebase ID tokens.

    Usage:
      Client sends:  Authorization: Bearer <firebase_id_token>
      This class verifies the token with Firebase Admin SDK.
    """

    keyword = 'Bearer'

    def authenticate(self, request):
        """
        Returns (FirebaseUser, decoded_token) on success, or None to skip.
        Raises AuthenticationFailed on invalid tokens.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            return None  # No credentials provided → let permission classes decide

        parts = auth_header.split()

        if len(parts) != 2 or parts[0] != self.keyword:
            return None  # Not a Bearer token

        id_token = parts[1]

        try:
            # Ensure Firebase is initialised
            get_firebase_app()

            # Verify the token (checks signature, expiry, audience, issuer)
            decoded_token = auth.verify_id_token(id_token)
            logger.info(f"Authenticated Firebase user: {decoded_token.get('uid')}")

            user = FirebaseUser(decoded_token)
            return (user, decoded_token)

        except auth.ExpiredIdTokenError:
            logger.warning("Expired Firebase ID token.")
            raise exceptions.AuthenticationFailed('Firebase token has expired.')

        except auth.RevokedIdTokenError:
            logger.warning("Revoked Firebase ID token.")
            raise exceptions.AuthenticationFailed('Firebase token has been revoked.')

        except auth.InvalidIdTokenError as e:
            logger.warning(f"Invalid Firebase ID token: {e}")
            raise exceptions.AuthenticationFailed('Invalid Firebase token.')

        except Exception as e:
            logger.error(f"Firebase authentication error: {e}")
            raise exceptions.AuthenticationFailed(f'Authentication error: {str(e)}')

    def authenticate_header(self, request):
        """
        Return the WWW-Authenticate header value for 401 responses.
        """
        return self.keyword
