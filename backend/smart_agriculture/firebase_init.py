"""
Firebase Initialization – Singleton Pattern
=============================================
Initializes the Firebase Admin SDK exactly once.
Provides access to Firestore client across the application.
"""

import logging
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────
# Singleton: Firebase app is initialized only once
# ──────────────────────────────────────────

_firestore_client = None


def get_firebase_app():
    """
    Return the default Firebase app, initializing it if needed.
    Uses the service-account JSON pointed to by settings.FIREBASE_CREDENTIALS_PATH.
    """
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    return firebase_admin.get_app()


def get_firestore_client():
    """
    Return a cached Firestore client (singleton).
    """
    global _firestore_client
    if _firestore_client is None:
        get_firebase_app()  # ensure initialised
        _firestore_client = firestore.client()
        logger.info("Firestore client created.")
    return _firestore_client
