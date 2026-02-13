"""Quick diagnostic: Test the existing disease model with a sample image."""
import os, sys, warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'smart_agriculture.settings'

import django
django.setup()

import numpy as np
import tensorflow as tf
from django.conf import settings

model = tf.keras.models.load_model(settings.DISEASE_MODEL_PATH)

# Check architecture
print("=== MODEL ARCHITECTURE ===")
print(f"Total layers: {len(model.layers)}")
print(f"Total params: {model.count_params():,}")
for i, layer in enumerate(model.layers):
    trainable = sum(np.prod(w.shape) for w in layer.trainable_weights)
    non_trainable = sum(np.prod(w.shape) for w in layer.non_trainable_weights)
    print(f"  [{i}] {layer.__class__.__name__:30s} trainable={trainable:>10,}  non_trainable={non_trainable:>8,}")

# Check if first layer is MobileNetV2
first_layer = model.layers[0]
print(f"\nFirst layer type: {type(first_layer).__name__}")
print(f"First layer name: {first_layer.name}")
if hasattr(first_layer, 'layers'):
    print(f"First layer sub-layers: {len(first_layer.layers)}")

# Test with a real image from the dataset
print("\n=== TESTING WITH DATASET IMAGES ===")
from PIL import Image
from io import BytesIO

test_cases = [
    ('Tomato___Early_blight', 'data/plantvillage dataset/color/Tomato___Early_blight'),
    ('Tomato___healthy', 'data/plantvillage dataset/color/Tomato___healthy'),
    ('Apple___Apple_scab', 'data/plantvillage dataset/color/Apple___Apple_scab'),
]

from disease.ml_model import CLASS_LABELS, _format_label

for expected, folder in test_cases:
    if not os.path.isdir(folder):
        print(f"  SKIP: {folder} not found")
        continue
    
    # Pick first image from the class
    images = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        continue
    
    img_path = os.path.join(folder, images[0])
    img = Image.open(img_path).convert('RGB').resize((224, 224))
    
    # Method 1: Simple rescale (what our code does)
    arr1 = np.array(img, dtype=np.float32) / 255.0
    arr1 = np.expand_dims(arr1, axis=0)
    
    pred1 = model.predict(arr1, verbose=0)
    idx1 = int(np.argmax(pred1[0]))
    conf1 = float(np.max(pred1[0]) * 100)
    
    # Method 2: MobileNetV2 preprocessing
    arr2 = np.array(img, dtype=np.float32)
    arr2 = tf.keras.applications.mobilenet_v2.preprocess_input(arr2)
    arr2 = np.expand_dims(arr2, axis=0)
    
    pred2 = model.predict(arr2, verbose=0)
    idx2 = int(np.argmax(pred2[0]))
    conf2 = float(np.max(pred2[0]) * 100)
    
    print(f"\n  Expected: {expected}")
    print(f"  File: {images[0]}")
    print(f"  /255 rescale → {CLASS_LABELS[idx1]:45s} ({conf1:.1f}%) {'✓' if CLASS_LABELS[idx1] == expected else '✗'}")
    print(f"  MobileNet PP → {CLASS_LABELS[idx2]:45s} ({conf2:.1f}%) {'✓' if CLASS_LABELS[idx2] == expected else '✗'}")
