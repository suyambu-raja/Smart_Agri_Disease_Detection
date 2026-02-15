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
            logger.warning(
                "TensorFlow is not installed. Using mock predictor. "
                "Install TF with: pip install tensorflow"
            )
        except Exception as e:
            logger.error(f"Error loading disease model: {e}")
    else:
        logger.warning(f"Disease model file not found at {model_path}")

    # Fallback: mock model for dev/testing
    _model = None
    _model_loaded = True
    _using_mock = True
    logger.info("Disease model: using MOCK predictor (dev mode).")
    return _model, _using_mock


def predict_disease(image_array: np.ndarray, crop_filter: str = None) -> dict:
    """
    Run inference on a preprocessed image array (1, 224, 224, 3).
    If crop_filter is provided (e.g., 'Tomato'), it masks irrelevant classes.
    """
    model, using_mock = get_disease_model()

    if using_mock:
        # Mock logic
        found = False
        if crop_filter:
            for i, label in enumerate(CLASS_LABELS):
                if crop_filter.lower() in label.lower():
                    mock_idx = i
                    found = True
                    break
        if not found:
            mock_idx = 29  # Tomato___Early_blight default

        return {
            'disease_name': _format_label(CLASS_LABELS[mock_idx]),
            'confidence': round(85.50, 2),
            'is_healthy': False,
            'raw_label': CLASS_LABELS[mock_idx],
        }

    # Real model inference
    # Use MobileNetV2 preprocessing: scale [0,255] to [-1, 1]
    # If input is already [0, 1] (from /255.0 in views.py), convert back to [0, 255] first
    if np.max(image_array) <= 1.0:
        image_array = image_array * 255.0
    
    import tensorflow as tf
    image_array = tf.keras.applications.mobilenet_v2.preprocess_input(image_array)

    predictions = model.predict(image_array, verbose=0)[0]  # shape (N,)

    # Log top 3 for debugging
    top_3_indices = np.argsort(predictions)[-3:][::-1]
    logger.info(f"Top 3 predictions:")
    for i in top_3_indices:
        if i < len(CLASS_LABELS):
            logger.info(f"  {CLASS_LABELS[i]}: {predictions[i]*100:.2f}%")

    # Apply crop filter if provided
    if crop_filter:
        crop_filter = crop_filter.lower()
        # Find indices that match the crop
        valid_indices = [
            i for i, label in enumerate(CLASS_LABELS) 
            if label.lower().startswith(crop_filter) or 
               (crop_filter == 'corn' and 'corn_(maize)' in label.lower()) or
               (crop_filter == 'cherry' and 'cherry_(including_sour)' in label.lower()) or
               (crop_filter == 'pepper' and 'pepper,_bell' in label.lower()) or
               (crop_filter == 'rice' and label.lower().startswith('rice')) or
               (crop_filter == 'wheat' and label.lower().startswith('wheat')) or
               (crop_filter == 'onion' and label.lower().startswith('onion'))
        ]

        if valid_indices:
            # Mask out invalid indices (set to 0)
            masked_preds = np.zeros_like(predictions)
            for i in valid_indices:
                masked_preds[i] = predictions[i]
            
            # Re-normalize so they sum to 1
            total = np.sum(masked_preds)
            if total > 0:
                predictions = masked_preds / total
            else:
                # If everything was zeroed (shouldn't happen), fallback to original
                pass

    predicted_idx = int(np.argmax(predictions))
    
    # Final check for index bounds
    if predicted_idx >= len(CLASS_LABELS):
        logger.error(f"Predicted index {predicted_idx} out of bounds (Labels: {len(CLASS_LABELS)})")
        predicted_idx = 0
        
    confidence = float(np.max(predictions) * 100)
    raw_label = CLASS_LABELS[predicted_idx]

    return {
        'disease_name': _format_label(raw_label),
        'confidence': round(confidence, 2),
        'is_healthy': 'healthy' in raw_label.lower(),
        'raw_label': raw_label,
    }
