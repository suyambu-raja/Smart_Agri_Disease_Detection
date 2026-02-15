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
    1. Checks for FIREBASE_CREDENTIALS_JSON env var (raw JSON content).
    2. Falls back to file path at settings.FIREBASE_CREDENTIALS_PATH.
    """
    import os
    import json

    if not firebase_admin._apps:
        try:
            # 1. Try loading raw JSON from env var (best for HF Spaces)
            creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
            if creds_json:
                logger.info("Loading Firebase credentials from environment variable...")
                cred_dict = json.loads(creds_json)
                cred = credentials.Certificate(cred_dict)
            else:
                # 2. Fallback to file path
                logger.info(f"Loading Firebase credentials from file: {settings.FIREBASE_CREDENTIALS_PATH}")
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            # Don't raise in dev to avoid crashing if minor config issue
            # raise 
    try:
        return firebase_admin.get_app()
    except ValueError:
        return None


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
