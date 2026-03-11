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

    # Allow disabling via env var to save memory (e.g. on Render Free Tier)
    if os.getenv('SKIP_GATEKEEPER', 'False').lower() in ('true', '1', 'yes'):
        logger.info("Gatekeeper (MobileNetV2) skipped via SKIP_GATEKEEPER env var.")
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


def _is_valid_leaf_image(image_array: np.ndarray) -> tuple:
    """
    Lightweight pre-check to detect obviously invalid images BEFORE running
    the disease model. Only rejects clearly invalid inputs (blank, solid color).
    """
    img = image_array[0]  # Remove batch dimension: (224, 224, 3)
    
    # 1. Color Variance Check
    channel_stds = [np.std(img[:, :, c]) for c in range(3)]
    avg_std = np.mean(channel_stds)
    
    if avg_std < 0.02:
        return False, "Image appears to be a solid color or blank"
    
    # 2. Edge Density Check
    gray = np.mean(img, axis=2)
    dx = np.abs(np.diff(gray, axis=1))
    dy = np.abs(np.diff(gray, axis=0))
    edge_density = (np.mean(dx) + np.mean(dy)) / 2
    
    if edge_density < 0.003:
        return False, "Image has no visible texture or detail"
    
    if avg_std < 0.05 and edge_density < 0.01:
        return False, "Image does not appear to contain a photograph"
    
    return True, "Image looks valid"


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
        decoded = decode_predictions(preds, top=5)[0]

        VALID = {
            'daisy', 'flower', 'rose', 'plant', 'leaf', 'tree', 'grass',
            'corn', 'ear', 'lemon', 'orange', 'apple', 'fig', 'pineapple',
            'banana', 'jackfruit', 'strawberry', 'peach', 'cherry', 'blueberry', 'raspberry', 
            'soybean', 'squash', 'lettuce', 'cabbage', 'broccoli', 'acorn', 'bell_pepper',
            'produce', 'food', 'pot', 'farm', 'greenhouse', 'mushroom', 'vine', 'stinkhorn',
            'pod', 'seed', 'grain', 'root', 'tuber', 'hay', 'rapeseed', 'cucumber', 'vegetable'
        }

        matches = []
        for _, label, prob in decoded:
            label_lower = label.lower()
            # If the image net label contains an agricultural related word
            if any(k in label_lower for k in VALID):
                matches.append(label)

        if matches:
            return True, matches[0]

        # Not a plant -> Returns the top prediction to tell user what they submitted
        top_label = decoded[0][1]
        logger.info(f"Gatekeeper failed. Image top hit: {top_label}")
        return False, top_label

    except Exception as e:
        logger.error(f"Gatekeeper check error: {e}")
        return True, "Error resolving gatekeeper format"


def _compute_entropy(probabilities: np.ndarray) -> float:
    """
    Compute prediction entropy (uncertainty measure).
    - Low entropy (~0.0): Model is very confident in one class → trustworthy
    - High entropy (>2.0): Probability is spread across many classes → untrustworthy
    For 48 classes, max entropy = ln(48) ≈ 3.87
    """
    probs = np.clip(probabilities, 1e-10, 1.0)
    return float(-np.sum(probs * np.log(probs)))


def predict_disease(image_array: np.ndarray, crop_filter: str = None) -> dict:
    """
    Run inference on a preprocessed image array (1, 224, 224, 3) where values are [0, 1].
    Three-stage validation:
    1. Image pre-check: reject obviously invalid inputs (blank/solid)
    2. Gatekeeper Object detection to reject non-plant completely
    3. Disease model prediction + Entropy analysis
    """
    model, using_mock = get_disease_model()

    if using_mock:
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
            'error_type': None,
        }

    # ──────────────────────────────────────────
    # Stage 1: Fast Image Pre-Check (Blank image etc)
    # ──────────────────────────────────────────
    is_valid, reason = _is_valid_leaf_image(image_array)
    if not is_valid:
        logger.info(f"Image pre-check REJECTED: {reason}")
        return {
            'success': False,
            'disease_name': "Invalid Image",
            'confidence': 0.0,
            'is_healthy': False,
            'error_type': 'invalid_image',
            'error': f"This does not appear to be a valid photo. {reason}.",
            'raw_label': 'invalid_content'
        }

    # ──────────────────────────────────────────
    # Stage 2: Gatekeeper Check
    # Ensure it's some sort of plant using ImageNet (to avoid false positives on random objects)
    # ──────────────────────────────────────────
    if np.max(image_array) <= 1.0:
        image_scaled = image_array * 255.0
    else:
        image_scaled = np.copy(image_array)
    
    import tensorflow as tf
    # Gatekeeper + MobileNetV2 expect [-1, 1] inputs
    image_preprocessed = tf.keras.applications.mobilenet_v2.preprocess_input(image_scaled.copy())

    is_plant, content_desc = check_is_plant(image_preprocessed)
    if not is_plant:
        # We explicitly reject the non-plant image
        logger.info(f"Gatekeeper REJECTED: Detected as {content_desc}")
        return {
            'success': False,
            'disease_name': "Invalid data",
            'confidence': 0.0,
            'is_healthy': False,
            'error_type': 'invalid_image',
            'error': f"Image appears to contain '{content_desc.replace('_', ' ')}', not a crop leaf.",
            'raw_label': 'invalid_content'
        }

    # ──────────────────────────────────────────
    # Stage 3: Disease Model Prediction & Validation
    # ──────────────────────────────────────────
    try:
        predictions = model.predict(image_preprocessed, verbose=0)[0]
        entropy = _compute_entropy(predictions)
        
        # Apply crop filter logic
        filtered_predictions = predictions.copy()
        if crop_filter:
            valid_indices = [
                i for i, label in enumerate(CLASS_LABELS) 
                if label.lower().startswith(crop_filter.lower()) or 
                   (crop_filter.lower() == 'corn' and 'corn' in label.lower()) or
                   (crop_filter.lower() == 'cherry' and 'cherry' in label.lower())
            ]
            if valid_indices:
                mask = np.zeros_like(filtered_predictions)
                mask[valid_indices] = 1.0
                filtered_predictions = filtered_predictions * mask
        
        pred_idx = int(np.argmax(filtered_predictions))
        confidence = float(np.max(filtered_predictions) * 100)
        raw_label = CLASS_LABELS[pred_idx]

        # Evaluate Uncertainty (Entropy + Confidence)
        if entropy > 2.5:
            logger.info(f"REJECTED: High entropy ({entropy:.2f})")
            return {
                'success': False,
                'disease_name': "Unrecognized Image",
                'confidence': round(confidence, 2),
                'is_healthy': False,
                'error_type': 'not_trained',
                'error': f"The model is highly uncertain. Please upload a clear photo focusing only on a crop leaf.",
                'raw_label': raw_label
            }
        
        if entropy > 1.5 and confidence < 40.0:
            logger.info(f"REJECTED: Mixed entropy ({entropy:.2f}) + low conf ({confidence:.1f}%)")
            return {
                'success': False,
                'disease_name': "Low Confidence",
                'confidence': round(confidence, 2),
                'is_healthy': False,
                'error_type': 'not_trained',
                'error': f"Prediction too uncertain ({round(confidence, 1)}%). Try a clearer, closer photo.",
                'raw_label': raw_label
            }
            
        if confidence < 25.0:
            logger.info(f"REJECTED: Low confidence ({confidence:.1f}%)")
            return {
                'success': False,
                'disease_name': "Crop Not Trained",
                'confidence': round(confidence, 2),
                'is_healthy': False,
                'error_type': 'not_trained',
                'error': f"This leaf is not recognized in our database with sufficient confidence.",
                'raw_label': raw_label
            }

        # Valid prediction!
        logger.info(f"ACCEPTED: {raw_label} ({confidence:.1f}%) entropy={entropy:.3f}")
        return {
            'success': True, 
            'disease_name': _format_label(raw_label),
            'confidence': round(confidence, 2),
            'is_healthy': 'healthy' in raw_label.lower(),
            'raw_label': raw_label,
            'error_type': None,
        }

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {
            'success': False,
            'disease_name': "Error",
            'confidence': 0.0,
            'is_healthy': False,
            'error_type': 'error',
            'error': str(e)
        }
