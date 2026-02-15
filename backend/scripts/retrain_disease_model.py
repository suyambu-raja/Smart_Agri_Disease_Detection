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

# Show detected labels (dynamic – no hardcoded list!)
actual_labels = sorted(train_gen.class_indices.keys())
print(f"\nDetected {len(actual_labels)} label(s) from dataset:")
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
