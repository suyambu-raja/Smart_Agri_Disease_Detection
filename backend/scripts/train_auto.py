"""
Train Disease Detection Model on PlantVillage Dataset
======================================================
Uses MobileNetV2 transfer learning on the locally downloaded
PlantVillage color dataset (38 classes, ~54,000 images).

Two-phase training:
  Phase 1: Train classification head only (base frozen)
  Phase 2: Fine-tune top layers of MobileNetV2
"""

import os
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator

print("=" * 60)
print("🌱 Disease Model Training – PlantVillage Dataset")
print("=" * 60)
print(f"TensorFlow: {tf.__version__}")
print(f"GPU available: {len(tf.config.list_physical_devices('GPU')) > 0}")
print()

# ──────────────────────────────────────────
# Config
# ──────────────────────────────────────────
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS_PHASE1 = 3
EPOCHS_PHASE2 = 5
FINE_TUNE_LAYERS = 30

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'plantvillage dataset', 'color')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'disease_model.h5')

if not os.path.exists(DATA_DIR):
    print(f"❌ Dataset not found at: {DATA_DIR}")
    exit(1)

# ──────────────────────────────────────────
# 1. Data Pipeline with Augmentation
# ──────────────────────────────────────────
print("🔄 Loading dataset...")

train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=20,
    width_shift_range=0.15,
    height_shift_range=0.15,
    shear_range=0.15,
    zoom_range=0.15,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2,
)

train_gen = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True,
)

val_gen = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False,
)

NUM_CLASSES = len(train_gen.class_indices)
print(f"   Classes:    {NUM_CLASSES}")
print(f"   Training:   {train_gen.samples} images")
print(f"   Validation: {val_gen.samples} images")

# ──────────────────────────────────────────
# 2. Build Model
# ──────────────────────────────────────────
print("\n🏗️ Building MobileNetV2 model...")

base_model = keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet',
)
base_model.trainable = False

model = keras.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(NUM_CLASSES, activation='softmax'),
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy'],
)

# ──────────────────────────────────────────
# 3. Callbacks
# ──────────────────────────────────────────
callbacks = [
    keras.callbacks.ModelCheckpoint(
        MODEL_PATH, monitor='val_accuracy',
        save_best_only=True, verbose=1,
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.5,
        patience=2, verbose=1,
    ),
]

# ──────────────────────────────────────────
# 4. Phase 1 – Head only
# ──────────────────────────────────────────
print("\n" + "=" * 60)
print(f"PHASE 1: Training head ({EPOCHS_PHASE1} epochs)")
print("=" * 60)

model.fit(
    train_gen,
    epochs=EPOCHS_PHASE1,
    validation_data=val_gen,
    callbacks=callbacks,
)

# ──────────────────────────────────────────
# 5. Phase 2 – Fine-tune
# ──────────────────────────────────────────
print("\n" + "=" * 60)
print(f"PHASE 2: Fine-tuning top {FINE_TUNE_LAYERS} layers ({EPOCHS_PHASE2} epochs)")
print("=" * 60)

base_model.trainable = True
for layer in base_model.layers[:-FINE_TUNE_LAYERS]:
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
# 6. Results
# ──────────────────────────────────────────
val_loss, val_acc = model.evaluate(val_gen, verbose=0)

print("\n" + "=" * 60)
print("✅ TRAINING COMPLETE!")
print("=" * 60)
print(f"   Accuracy:  {val_acc * 100:.2f}%")
print(f"   Loss:      {val_loss:.4f}")
print(f"   Saved to:  {MODEL_PATH}")
print(f"   Size:      {os.path.getsize(MODEL_PATH) / (1024*1024):.1f} MB")

# Save labels
labels_path = os.path.join(os.path.dirname(MODEL_PATH), 'class_labels.txt')
with open(labels_path, 'w') as f:
    for label, idx in sorted(train_gen.class_indices.items(), key=lambda x: x[1]):
        f.write(f"{idx}: {label}\n")
print(f"   Labels:    {labels_path}")
print("=" * 60)
