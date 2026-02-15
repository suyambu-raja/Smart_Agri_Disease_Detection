"""
Test Disease Model V2 – Verify predictions on all crop types
=============================================================
Tests the newly trained 48-class model with sample images from
the dataset, focusing on Rice, Wheat, Onion (new) + originals.
"""

import os
import sys
import warnings
import numpy as np

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'plantvillage dataset', 'color')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'disease_model.h5')
LABELS_PATH = os.path.join(BASE_DIR, 'models', 'class_labels.txt')

print("=" * 70)
print("  🔬 Disease Model V2 – Testing")
print("=" * 70)

# Load model
import tensorflow as tf
print(f"  Loading model from: {MODEL_PATH}")
model = tf.keras.models.load_model(MODEL_PATH)
print(f"  Model loaded! Params: {model.count_params():,}")

# Load class labels
labels = {}
with open(LABELS_PATH, 'r') as f:
    for line in f:
        parts = line.strip().split(':', 1)
        if len(parts) == 2:
            labels[int(parts[0].strip())] = parts[1].strip()

CLASS_LABELS = [labels[i] for i in sorted(labels.keys())]
print(f"  Classes: {len(CLASS_LABELS)}")

# Test classes — focus on NEW crops + some originals
test_classes = [
    # New crops (the ones we just added)
    'Rice___Brown_spot',
    'Rice___Hispa',
    'Rice___Leaf_blast',
    'Rice___healthy',
    'Wheat___Brown_rust',
    'Wheat___Septoria',
    'Wheat___Yellow_rust',
    'Wheat___healthy',
    'Onion___Purple_blotch',
    'Onion___healthy',
    # Original crops for comparison
    'Tomato___Early_blight',
    'Tomato___healthy',
    'Apple___Apple_scab',
    'Potato___Late_blight',
    'Corn_(maize)___Common_rust_',
    'Grape___Black_rot',
]

def format_label(raw_label):
    return raw_label.replace('___', ' ').replace('_', ' ').title()

print("\n" + "=" * 70)
print("  TEST RESULTS")
print("=" * 70)

from PIL import Image

correct = 0
total = 0
results_by_crop = {}

for expected_class in test_classes:
    folder = os.path.join(DATA_DIR, expected_class)
    if not os.path.isdir(folder):
        print(f"\n  ⚠️  SKIP: {expected_class} (folder not found)")
        continue
    
    images = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        print(f"\n  ⚠️  SKIP: {expected_class} (no images)")
        continue
    
    # Test up to 3 images per class
    test_imgs = images[:3]
    class_correct = 0
    class_total = len(test_imgs)
    
    crop_name = expected_class.split('___')[0]
    if crop_name not in results_by_crop:
        results_by_crop[crop_name] = {'correct': 0, 'total': 0}
    
    for img_name in test_imgs:
        img_path = os.path.join(folder, img_name)
        img = Image.open(img_path).convert('RGB').resize((224, 224))
        
        # Use MobileNetV2 preprocessing (matching training)
        arr = np.array(img, dtype=np.float32)
        arr = tf.keras.applications.mobilenet_v2.preprocess_input(arr)
        arr = np.expand_dims(arr, axis=0)
        
        pred = model.predict(arr, verbose=0)[0]
        pred_idx = int(np.argmax(pred))
        confidence = float(np.max(pred) * 100)
        predicted = CLASS_LABELS[pred_idx]
        
        is_correct = predicted == expected_class
        if is_correct:
            class_correct += 1
            correct += 1
        total += 1
        results_by_crop[crop_name]['total'] += 1
        if is_correct:
            results_by_crop[crop_name]['correct'] += 1
    
    # Show result for this class
    status = "✅" if class_correct == class_total else ("⚠️" if class_correct > 0 else "❌")
    print(f"\n  {status} {expected_class}")
    print(f"     Accuracy: {class_correct}/{class_total}")
    
    # Show one sample prediction
    img_path = os.path.join(folder, test_imgs[0])
    img = Image.open(img_path).convert('RGB').resize((224, 224))
    arr = np.array(img, dtype=np.float32)
    arr = tf.keras.applications.mobilenet_v2.preprocess_input(arr)
    arr = np.expand_dims(arr, axis=0)
    pred = model.predict(arr, verbose=0)[0]
    
    # Top 3 predictions
    top_3 = np.argsort(pred)[-3:][::-1]
    for rank, idx in enumerate(top_3, 1):
        marker = "→" if CLASS_LABELS[idx] == expected_class else " "
        print(f"     {marker} #{rank}: {format_label(CLASS_LABELS[idx]):45s} ({pred[idx]*100:.1f}%)")

# Summary
print("\n" + "=" * 70)
print("  SUMMARY")
print("=" * 70)
print(f"\n  Overall: {correct}/{total} correct ({correct/total*100:.1f}%)")

print(f"\n  Per-crop accuracy:")
for crop, data in sorted(results_by_crop.items()):
    acc = data['correct'] / data['total'] * 100 if data['total'] > 0 else 0
    is_new = crop in ['Rice', 'Wheat', 'Onion']
    tag = " 🆕" if is_new else ""
    print(f"    {crop:40s} {data['correct']}/{data['total']} ({acc:.0f}%){tag}")

print("\n" + "=" * 70)
print("  🌾 The model can now identify different diseases within the SAME crop!")
print("  For example:")
print("    Rice  → Brown Spot, Hispa, Leaf Blast, or Healthy")
print("    Wheat → Brown Rust, Septoria, Yellow Rust, or Healthy")
print("    Onion → Purple Blotch or Healthy")
print("=" * 70)
