"""
Disease Detection – ML Model Loader (Singleton)
=================================================
Loads the pre-trained CNN model exactly once into memory.
Subsequent calls return the cached model.

NOTE: TensorFlow is imported lazily. If TF is unavailable
      (e.g., Python 3.13+), a mock predictor is returned
      so the server can still start for development.
"""

import logging
import os
import numpy as np
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

_model = None
_model_loaded = False
_using_mock = False

# Gatekeeper (ImageNet)
_gatekeeper_model = None

# ──────────────────────────────────────────
# Class labels — index matches model output
# Update this list to match your training labels
# ──────────────────────────────────────────

# Default fallback labels (if file missing)
# 48 classes: original PlantVillage (38) + Rice (4) + Wheat (4) + Onion (2)
DEFAULT_CLASS_LABELS = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Onion___Purple_blotch',
    'Onion___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Rice___Brown_spot',
    'Rice___Hispa',
    'Rice___Leaf_blast',
    'Rice___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy',
    'Wheat___Brown_rust',
    'Wheat___Septoria',
    'Wheat___Yellow_rust',
    'Wheat___healthy',
]

def get_class_labels():
    """Load class labels from file or return default."""
    labels_path = os.path.join(settings.BASE_DIR, 'models', 'class_labels.txt')
    if os.path.exists(labels_path):
        try:
            labels = {}
            with open(labels_path, 'r') as f:
                for line in f:
                    parts = line.strip().split(':', 1)
                    if len(parts) == 2:
                        idx = int(parts[0].strip())
                        label = parts[1].strip()
                        labels[idx] = label
            return [labels[i] for i in sorted(labels.keys())]
        except Exception as e:
            logger.error(f"Error reading class_labels.txt: {e}")
    
    return DEFAULT_CLASS_LABELS

CLASS_LABELS = get_class_labels()


def _format_label(raw_label: str) -> str:
    """Convert 'Tomato___Early_blight' → 'Tomato Early Blight'."""
    return raw_label.replace('___', ' ').replace('_', ' ').title()


# ----------------------------------------------------------------------
# models
# ----------------------------------------------------------------------

def get_disease_model():
    """
    Return the cached TensorFlow/Keras model (singleton).
    Falls back to a mock if TF is not available.
    """
    global _model, _model_loaded, _using_mock

    if _model_loaded:
        return _model, _using_mock

    model_path = settings.DISEASE_MODEL_PATH

    # Attempt to load real TF model
    if os.path.exists(model_path):
        try:
            import tensorflow as tf
            _model = tf.keras.models.load_model(model_path)
            _model_loaded = True
            _using_mock = False
            logger.info(f"Disease model loaded from {model_path}")
            return _model, _using_mock
        except ImportError:
            logger.warning("TensorFlow is not installed. Using mock predictor.")
        except Exception as e:
            logger.error(f"Error loading disease model: {e}")
    else:
        logger.warning(f"Disease model file not found at {model_path}")

    # Fallback: mock model
    _model = None
    _model_loaded = True
    _using_mock = True
    logger.info("Disease model: using MOCK predictor (dev mode).")
    return _model, _using_mock


def get_gatekeeper_model():
    """Lazy-load the standard MobileNetV2 (ImageNet) for content verification."""
    global _gatekeeper_model

    # SMART DEFAULT MEMORY MANAGEMENT:
    # 1. RENDER (Free Tier 512MB RAM): DISABLE to prevent crashes.
    # 2. LOCALHOST / HUGGING FACE / CLOUD RUN (2GB+ RAM): ENABLE for better security.
    
    is_render = os.getenv('RENDER', 'False').lower() in ('true', '1', 'yes')
    
    # Default: Enable everywhere EXCEPT Render
    default_state = 'False' if is_render else 'True'
    
    # Allow explicit override via ENABLE_GATEKEEPER env var
    should_enable = os.getenv('ENABLE_GATEKEEPER', default_state).lower() in ('true', '1', 'yes')

    if not should_enable:
        # logger.info("Gatekeeper (MobileNetV2) disabled to save memory.")
        return None

    if _gatekeeper_model is None:
        try:
            logger.info("Loading Gatekeeper (MobileNetV2/ImageNet)...")
            from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2
            _gatekeeper_model = MobileNetV2(weights='imagenet', include_top=True)
        except Exception as e:
            logger.error(f"Failed to load Gatekeeper: {e}")
            return None
    return _gatekeeper_model


def check_is_plant(image_array: np.ndarray) -> tuple:
    """
    Verifies if the image contains plant/agricultural content.
    Returns (is_valid, description).
    """
    gk = get_gatekeeper_model()
    if not gk:
        return True, "Check Skipped"

    try:
        from tensorflow.keras.applications.mobilenet_v2 import decode_predictions
        preds = gk.predict(image_array, verbose=0)
        decoded = decode_predictions(preds, top=3)[0] # List of (id, label, prob)
        
        # Valid keywords
        VALID = {
            'plant', 'leaf', 'flower', 'fruit', 'vegetable', 'tree', 'grass', 
            'agriculture', 'garden', 'crop', 'corn', 'wheat', 'rice', 'onion', 
            'potato', 'tomato', 'pepper', 'apple', 'grape', 'orange', 
            'strawberry', 'peach', 'cherry', 'blueberry', 'raspberry', 
            'soybean', 'squash', 'lettuce', 'cabbage', 'broccoli', 
            'produce', 'food', 'pot', 'farm', 'greenhouse', 'mushroom',
            'pod', 'seed', 'grain', 'root', 'tuber'
        }
        
        matches = []
        for _, label, prob in decoded:
            label_lower = label.lower()
            if any(k in label_lower for k in VALID):
                matches.append(label)
        
        if matches:
            return True, matches[0]
            
        # If no match, return top prediction
        top_label = decoded[0][1]
        return False, top_label

    except Exception as e:
        logger.error(f"Gatekeeper check error: {e}")
        return True, "Error"


def predict_disease(image_array: np.ndarray, crop_filter: str = None) -> dict:
    """
    Run inference on a preprocessed image array (1, 224, 224, 3).
    Includes Gatekeeper & Confidence checks.
    """
    model, using_mock = get_disease_model()

    if using_mock:
        # Mock logic (same as before)
        found = False
        mock_idx = 29
        if crop_filter:
            for i, label in enumerate(CLASS_LABELS):
                if crop_filter.lower() in label.lower():
                    mock_idx = i
                    found = True
                    break
        raw_label = CLASS_LABELS[mock_idx]
        return {
            'success': True,
            'disease_name': _format_label(raw_label),
            'confidence': 85.50,
            'is_healthy': 'healthy' in raw_label.lower(),
            'raw_label': raw_label,
        }

    # Real Inference
    # Ensure input is [-1, 1] for MobileNetV2
    if np.max(image_array) <= 1.0:
        image_array = image_array * 255.0 # Scale to [0, 255] first
    
    import tensorflow as tf
    # This scales [0, 255] -> [-1, 1]
    image_array = tf.keras.applications.mobilenet_v2.preprocess_input(image_array)

    # 1. Gatekeeper Check
    is_plant, content_desc = check_is_plant(image_array)
    if not is_plant:
        return {
            'success': False,
            'disease_name': "Invalid data",
            'confidence': 0.0,
            'is_healthy': False,
            'error': f"Image appears to be '{content_desc.replace('_', ' ')}', not a crop leaf.",
            'raw_label': 'invalid_content'
        }

    # 2. Disease Prediction
    try:
        predictions = model.predict(image_array, verbose=0)[0]
        
        # Apply crop filter logic (simplified)
        if crop_filter:
            valid_indices = [
                i for i, label in enumerate(CLASS_LABELS) 
                if label.lower().startswith(crop_filter.lower()) or 
                   (crop_filter.lower() == 'corn' and 'corn' in label.lower()) or
                   (crop_filter.lower() == 'cherry' and 'cherry' in label.lower())
            ]
            if valid_indices:
                mask = np.zeros_like(predictions)
                mask[valid_indices] = 1.0
                predictions = predictions * mask
        
        pred_idx = int(np.argmax(predictions))
        confidence = float(np.max(predictions) * 100)
        raw_label = CLASS_LABELS[pred_idx]

        # 3. Confidence Threshold (Unsupported Crop Check)
        if confidence < 45.0:
            return {
                'success': False,
                'disease_name': "Crop Not Trained",
                'confidence': round(confidence, 2),
                'is_healthy': False,
                'error': f"Low confidence ({round(confidence, 1)}%). This crop looks unsupported.",
                'raw_label': raw_label
            }

        return {
            'success': True, 
            'disease_name': _format_label(raw_label),
            'confidence': round(confidence, 2),
            'is_healthy': 'healthy' in raw_label.lower(),
            'raw_label': raw_label,
        }

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {
            'success': False,
            'disease_name': "Error",
            'confidence': 0.0,
            'is_healthy': False,
            'error': str(e)
        }
