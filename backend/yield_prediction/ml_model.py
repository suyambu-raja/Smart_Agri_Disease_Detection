"""
Yield Prediction – ML Model Loader (Singleton)
================================================
Loads the pre-trained RandomForest model trained on real
Indian crop production and climate data.

Input features: [district, soil_type, crop, rainfall, temperature]
Output: predicted_yield (kg/acre)
"""

import logging
import os
import joblib
import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)

_model = None
_model_loaded = False
_using_mock = False

# ──────────────────────────────────────────
# Encoding maps — must match training pipeline
# Sourced from real Tamil Nadu agricultural data
# ──────────────────────────────────────────

DISTRICT_ENCODING = {
    'Coimbatore': 0, 'Chennai': 1, 'Madurai': 2,
    'Tiruchirappalli': 3, 'Salem': 4, 'Tirunelveli': 5,
    'Erode': 6, 'Thanjavur': 7, 'Vellore': 8,
    'Kancheepuram': 9, 'Cuddalore': 10, 'Dindigul': 11,
    'Krishnagiri': 12, 'Nagapattinam': 13, 'Ramanathapuram': 14,
    'Sivaganga': 15, 'Theni': 16, 'Virudhunagar': 17,
}

SOIL_TYPE_ENCODING = {
    'Black Soil': 0, 'Red Soil': 1, 'Alluvial Soil': 2,
    'Laterite Soil': 3, 'Clay Soil': 4, 'Sandy Soil': 5,
    'Loamy Soil': 6,
}

CROP_ENCODING = {
    'Rice': 0, 'Wheat': 1, 'Maize': 2,
    'Sugarcane': 3, 'Cotton': 4, 'Groundnut': 5,
    'Millets': 6, 'Pulses': 7, 'Banana': 8,
    'Coconut': 9, 'Turmeric': 10, 'Tea': 11,
}

# Real average yields per acre (kg) from Indian agriculture stats
CROP_BASELINES = {
    'Rice': 1700, 'Wheat': 600, 'Maize': 1900,
    'Sugarcane': 35000, 'Cotton': 500, 'Groundnut': 700,
    'Millets': 500, 'Pulses': 300, 'Banana': 17000,
    'Coconut': 4000, 'Turmeric': 2200, 'Tea': 650,
}


def get_yield_model():
    """
    Return the cached scikit-learn yield model (singleton).
    Falls back to mock if file is missing.
    """
    global _model, _model_loaded, _using_mock

    if _model_loaded:
        return _model, _using_mock

    if os.getenv('SKIP_YIELD_MODEL', 'False').lower() in ('true', '1', 'yes'):
        logger.info("Yield model skipped via SKIP_YIELD_MODEL env var.")
        _model = None
        _model_loaded = True
        _using_mock = True
        return _model, _using_mock

    model_path = settings.YIELD_MODEL_PATH
    compressed_path = model_path + '.gz'

    # 1. Decompress if needed (to enable mmap)
    if not os.path.exists(model_path) and os.path.exists(compressed_path):
        try:
            logger.info(f"Decompressing {compressed_path} to disk for mmap...")
            import gzip
            import shutil
            with gzip.open(compressed_path, 'rb') as f_in:
                with open(model_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            logger.warning(f"Could not decompress model to disk (RAM usage might be high): {e}")

    # 2. Try loading uncompressed with mmap (Low RAM)
    if os.path.exists(model_path):
        try:
            _model = joblib.load(model_path, mmap_mode='r')
            _model_loaded = True
            _using_mock = False
            logger.info(f"Yield model loaded from {model_path} (mmap_mode='r')")
            return _model, _using_mock
        except Exception as e:
            logger.error(f"Error loading yield model (mmap): {e}")

    # 3. Fallback: Load directly from compressed file (High RAM)
    if os.path.exists(compressed_path):
        try:
            _model = joblib.load(compressed_path)
            _model_loaded = True
            _using_mock = False
            logger.info(f"Yield model loaded from {compressed_path} (High RAM mode)")
            return _model, _using_mock
        except Exception as e:
            logger.error(f"Error loading compressed yield model: {e}")

    # 4. Fallback: Rule-based Mock
    logger.warning(f"Yield model not found. Using rule-based estimator.")
    _model = None
    _model_loaded = True
    _using_mock = True
    return _model, _using_mock


def _classify_risk(predicted_yield: float, crop: str) -> str:
    """
    Classify risk level based on predicted yield vs real crop baselines.
    Low = yield is ≥85% of baseline (good harvest)
    Medium = yield is 55–85% of baseline (moderate)
    High = yield is <55% of baseline (poor harvest, risk of loss)
    """
    baseline = CROP_BASELINES.get(crop, 1000)

    ratio = predicted_yield / baseline if baseline else 0.5
    if ratio >= 0.85:
        return 'Low'
    elif ratio >= 0.55:
        return 'Medium'
    else:
        return 'High'


def predict_yield(district: str, soil_type: str, crop: str,
                  rainfall: float, temperature: float) -> dict:
    """
    Predict crop yield given the input features.

    Args:
        district: Tamil Nadu district name
        soil_type: Type of soil
        crop: Crop name
        rainfall: Monthly rainfall in mm
        temperature: Average temperature in °C

    Returns:
        {
          "predicted_yield": 1450,
          "unit": "kg/acre",
          "risk_level": "Low"
        }
    """
    model, using_mock = get_yield_model()

    if using_mock:
        # Rule-based mock prediction
        base = CROP_BASELINES.get(crop, 1000)
        rainfall_factor = min(rainfall / 70.0, 1.5)
        temp_factor = 1.0 - abs(temperature - 28) * 0.02
        predicted = round(base * rainfall_factor * temp_factor)
        predicted = max(predicted, 50)

        return {
            'predicted_yield': predicted,
            'unit': 'kg/acre',
            'risk_level': _classify_risk(predicted, crop),
        }

    # Real model prediction
    district_enc = DISTRICT_ENCODING.get(district, 0)
    soil_enc = SOIL_TYPE_ENCODING.get(soil_type, 0)
    crop_enc = CROP_ENCODING.get(crop, 0)

    features = np.array([[district_enc, soil_enc, crop_enc, rainfall, temperature]])
    predicted = float(model.predict(features)[0])
    predicted = round(max(predicted, 0))

    return {
        'predicted_yield': predicted,
        'unit': 'kg/acre',
        'risk_level': _classify_risk(predicted, crop),
    }
