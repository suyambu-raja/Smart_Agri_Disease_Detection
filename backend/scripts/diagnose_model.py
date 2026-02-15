"""Quick diagnostic: Test current model with multiple disease images."""
import os, sys, warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'smart_agriculture.settings'

import django
django.setup()

import numpy as np
import tensorflow as tf
from PIL import Image
from django.conf import settings

# Write results to file
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'diagnose_results.txt')
f = open(OUTPUT_FILE, 'w', encoding='utf-8')

model = tf.keras.models.load_model(settings.DISEASE_MODEL_PATH)

f.write("=" * 60 + "\n")
f.write("MODEL DIAGNOSTICS\n")
f.write("=" * 60 + "\n")
num_output_classes = model.output_shape[-1]
f.write(f"Model output shape: {model.output_shape}\n")
f.write(f"Number of output neurons: {num_output_classes}\n")

from disease.ml_model import CLASS_LABELS
f.write(f"Number of CLASS_LABELS in backend: {len(CLASS_LABELS)}\n")
f.write(f"MATCH: {num_output_classes == len(CLASS_LABELS)}\n")

DATA_DIR = os.path.join(settings.BASE_DIR, 'data', 'plantvillage dataset', 'color')

test_classes = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___healthy',
    'Potato___Early_blight',
    'Potato___healthy',
    'Grape___Black_rot',
    'Corn_(maize)___Common_rust_',
]

f.write("\n" + "=" * 60 + "\n")
f.write("TESTING PREDICTIONS\n")
f.write("=" * 60 + "\n")

for expected_class in test_classes:
    folder = os.path.join(DATA_DIR, expected_class)
    if not os.path.isdir(folder):
        f.write(f"\nSKIP: {expected_class} - folder not found\n")
        continue

    images = [x for x in os.listdir(folder) if x.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        f.write(f"\nSKIP: {expected_class} - no images\n")
        continue

    # Test FIRST image
    img_path = os.path.join(folder, images[0])
    img = Image.open(img_path).convert('RGB').resize((224, 224))

    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)

    raw_preds = model.predict(arr, verbose=0)[0]

    pred_idx = int(np.argmax(raw_preds))
    pred_conf = float(np.max(raw_preds) * 100)
    top3 = np.argsort(raw_preds)[-3:][::-1]

    correct = "CORRECT" if CLASS_LABELS[pred_idx] == expected_class else "WRONG"

    f.write(f"\n--- Expected: {expected_class} ---\n")
    f.write(f"  Predicted idx: {pred_idx} -> {CLASS_LABELS[pred_idx]} ({pred_conf:.1f}%) [{correct}]\n")
    f.write(f"  Raw output: sum={np.sum(raw_preds):.4f}, min={np.min(raw_preds):.6f}, max={np.max(raw_preds):.6f}, std={np.std(raw_preds):.6f}\n")
    f.write(f"  Top 3:\n")
    for rank, idx in enumerate(top3):
        label = CLASS_LABELS[idx] if idx < len(CLASS_LABELS) else f"INDEX_{idx}"
        f.write(f"    #{rank+1}: idx={idx} -> {label} ({raw_preds[idx]*100:.2f}%)\n")

    # Also test with SECOND image if available
    if len(images) > 5:
        img_path2 = os.path.join(folder, images[5])
        img2 = Image.open(img_path2).convert('RGB').resize((224, 224))
        arr2 = np.array(img2, dtype=np.float32) / 255.0
        arr2 = np.expand_dims(arr2, axis=0)
        raw_preds2 = model.predict(arr2, verbose=0)[0]
        pred_idx2 = int(np.argmax(raw_preds2))
        pred_conf2 = float(np.max(raw_preds2) * 100)
        correct2 = "CORRECT" if CLASS_LABELS[pred_idx2] == expected_class else "WRONG"
        f.write(f"  2nd image: idx={pred_idx2} -> {CLASS_LABELS[pred_idx2]} ({pred_conf2:.1f}%) [{correct2}]\n")

f.write("\n" + "=" * 60 + "\n")
f.write("DONE\n")
f.close()
print(f"Results written to {OUTPUT_FILE}")
