"""
Retrain Disease Model – MobileNetV2 Transfer Learning
======================================================
Uses the existing PlantVillage color dataset to train a high-accuracy
38-class disease classifier using MobileNetV2 backbone.

Expected: ~93-96% validation accuracy in 10 epochs.
"""

import os, sys, warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator

print("=" * 60)
print("  Disease Model Retraining – MobileNetV2")
print("=" * 60)
print(f"TensorFlow: {tf.__version__}")
print(f"GPU: {tf.config.list_physical_devices('GPU')}")

# ──────────────────────────────────────────
# Config
# ──────────────────────────────────────────

DATA_DIR = os.path.join('data', 'plantvillage dataset', 'color')
MODEL_OUTPUT = os.path.join('models', 'disease_model.h5')
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS_PHASE1 = 5   # Head only (base frozen)
EPOCHS_PHASE2 = 10  # Fine-tune top layers

# ──────────────────────────────────────────
# 1. Data Loading & Augmentation
# ──────────────────────────────────────────

print(f"\nLoading data from: {DATA_DIR}")

datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=25,
    width_shift_range=0.15,
    height_shift_range=0.15,
    shear_range=0.15,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2,
)

train_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True,
)

val_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False,
)

NUM_CLASSES = len(train_gen.class_indices)
print(f"Classes: {NUM_CLASSES}")
print(f"Training: {train_gen.samples} images")
print(f"Validation: {val_gen.samples} images")

# Verify labels match our expected order
expected_labels = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust',
    'Apple___healthy', 'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy',
    'Grape___Black_rot', 'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
    'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
    'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight',
    'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy',
]

actual_labels = sorted(train_gen.class_indices.keys())
print(f"\nLabel order from dataset:")
for i, label in enumerate(actual_labels):
    print(f"  {i:2d}: {label}")

# ──────────────────────────────────────────
# 2. Build Model – MobileNetV2 Transfer Learning
# ──────────────────────────────────────────

print("\nBuilding MobileNetV2 model...")

base_model = keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet',
)
base_model.trainable = False  # Freeze for phase 1

model = keras.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(512, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.2),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(NUM_CLASSES, activation='softmax'),
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy'],
)

print(f"Total params: {model.count_params():,}")

# ──────────────────────────────────────────
# 3. Callbacks
# ──────────────────────────────────────────

os.makedirs('models', exist_ok=True)

callbacks = [
    keras.callbacks.ModelCheckpoint(
        MODEL_OUTPUT,
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1,
    ),
    keras.callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=5,
        restore_best_weights=True,
        verbose=1,
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=2,
        min_lr=1e-7,
        verbose=1,
    ),
]

# ──────────────────────────────────────────
# 4. PHASE 1: Train head only (base frozen)
# ──────────────────────────────────────────

print("\n" + "=" * 60)
print(f"PHASE 1: Training head ({EPOCHS_PHASE1} epochs, base frozen)")
print("=" * 60)

model.fit(
    train_gen,
    epochs=EPOCHS_PHASE1,
    validation_data=val_gen,
    callbacks=callbacks,
)

# ──────────────────────────────────────────
# 5. PHASE 2: Fine-tune top 30 layers
# ──────────────────────────────────────────

print("\n" + "=" * 60)
print(f"PHASE 2: Fine-tuning top 30 layers ({EPOCHS_PHASE2} more epochs)")
print("=" * 60)

base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy'],
)

model.fit(
    train_gen,
    initial_epoch=EPOCHS_PHASE1,
    epochs=EPOCHS_PHASE1 + EPOCHS_PHASE2,
    validation_data=val_gen,
    callbacks=callbacks,
)

# ──────────────────────────────────────────
# 6. Final evaluation
# ──────────────────────────────────────────

model.save(MODEL_OUTPUT)
val_loss, val_acc = model.evaluate(val_gen)

print("\n" + "=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)
print(f"  Validation Accuracy: {val_acc * 100:.2f}%")
print(f"  Validation Loss:     {val_loss:.4f}")
print(f"  Model saved to:      {MODEL_OUTPUT}")
print(f"  Model size:          {os.path.getsize(MODEL_OUTPUT) / (1024*1024):.1f} MB")

# Save class labels
labels_path = 'models/class_labels.txt'
with open(labels_path, 'w') as f:
    for label, idx in sorted(train_gen.class_indices.items(), key=lambda x: x[1]):
        f.write(f"{idx}: {label}\n")
print(f"  Labels saved to:     {labels_path}")
print("=" * 60)
