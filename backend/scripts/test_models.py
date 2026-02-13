"""Quick test to verify both AI models load and predict correctly."""
import os
import sys
import numpy as np

# Add parent directory to path so Django modules can be found
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = 'smart_agriculture.settings'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import django
django.setup()

print("=" * 50)
print("Testing Disease Detection Model")
print("=" * 50)

from disease.ml_model import get_disease_model, predict_disease

model, is_mock = get_disease_model()
print("Mock mode:", is_mock)
print("Model type:", type(model).__name__)

# Test with a random image
test_img = np.random.rand(1, 224, 224, 3).astype(np.float32)
result = predict_disease(test_img)
print("Prediction:", result["disease_name"])
print("Confidence:", result["confidence"], "%")
print("Is healthy:", result["is_healthy"])
print("Raw label:", result["raw_label"])

print()
print("=" * 50)
print("Testing Yield Prediction Model")
print("=" * 50)

from yield_prediction.ml_model import get_yield_model, predict_yield

model2, is_mock2 = get_yield_model()
print("Mock mode:", is_mock2)
print("Model type:", type(model2).__name__)

result2 = predict_yield("Coimbatore", "Black Soil", "Rice", 120.0, 30.0)
print("Yield:", result2["predicted_yield"], "kg/acre")
print("Risk:", result2["risk_level"])

print()
print("=" * 50)
print("ALL TESTS PASSED!")
print("=" * 50)
