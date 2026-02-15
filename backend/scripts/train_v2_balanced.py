"""
Train Disease Detection Model V2 – 48-Class Balanced Training
================================================================
Handles extreme class imbalance between original PlantVillage classes
(275-5507 images) and new Rice/Wheat/Onion classes (10-23 images).

Strategy:
  1. Offline augmentation to bring small classes up to ~200 images
  2. Class-weighted loss so model doesn't ignore rare classes
  3. Two-phase transfer learning (MobileNetV2)
  4. Uses proper MobileNetV2 preprocessing ([-1, 1] range)
  5. Caps large classes at 500 images to reduce imbalance ratio
  6. Saves model + class_labels.txt for inference

Usage:
    cd backend
    python scripts/train_v2_balanced.py
"""

import os
import sys
import shutil
import random
import warnings
import json
from collections import Counter
from datetime import datetime

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np

# ──────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'plantvillage dataset', 'color')
BALANCED_DIR = os.path.join(BASE_DIR, 'data', 'plantvillage dataset', '_balanced_training')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'disease_model.h5')
LABELS_PATH = os.path.join(BASE_DIR, 'models', 'class_labels.txt')
TRAINING_LOG_PATH = os.path.join(BASE_DIR, 'models', 'training_log.json')

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

# Balance config
MIN_IMAGES_PER_CLASS = 150     # Augment small classes up to this
MAX_IMAGES_PER_CLASS = 500     # Cap large classes to reduce imbalance
MIN_REQUIRED_IMAGES = 5        # Skip classes with fewer than this

# Training config
EPOCHS_PHASE1 = 8   # Head only (base frozen)
EPOCHS_PHASE2 = 12  # Fine-tune top layers
FINE_TUNE_LAYERS = 40
LEARNING_RATE_PHASE1 = 0.001
LEARNING_RATE_PHASE2 = 0.00005


def create_balanced_dataset():
    """
    Create a balanced training directory by:
    1. Augmenting small classes (< MIN_IMAGES_PER_CLASS) with offline augmentation
    2. Subsampling large classes (> MAX_IMAGES_PER_CLASS)
    """
    print("\n" + "=" * 60)
    print("  STEP 1: Creating Balanced Dataset")
    print("=" * 60)

    import tensorflow as tf
    from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array

    # Clean up any previous balanced dir
    if os.path.exists(BALANCED_DIR):
        shutil.rmtree(BALANCED_DIR)

    classes = sorted([
        d for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d)) and not d.startswith('_')
    ])

    aug_gen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.3,
        height_shift_range=0.3,
        shear_range=0.3,
        zoom_range=0.3,
        horizontal_flip=True,
        vertical_flip=False,
        brightness_range=[0.7, 1.3],
        fill_mode='nearest',
    )

    skipped = []
    class_counts = {}
    total_original = 0
    total_balanced = 0

    for cls in classes:
        src_dir = os.path.join(DATA_DIR, cls)
        dst_dir = os.path.join(BALANCED_DIR, cls)
        os.makedirs(dst_dir, exist_ok=True)

        imgs = [f for f in os.listdir(src_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        original_count = len(imgs)
        total_original += original_count

        if original_count < MIN_REQUIRED_IMAGES:
            print(f"  ⚠️  SKIP {cls}: only {original_count} images (need >= {MIN_REQUIRED_IMAGES})")
            skipped.append(cls)
            shutil.rmtree(dst_dir)
            continue

        # Determine target count
        if original_count < MIN_IMAGES_PER_CLASS:
            target_count = MIN_IMAGES_PER_CLASS
        elif original_count > MAX_IMAGES_PER_CLASS:
            target_count = MAX_IMAGES_PER_CLASS
        else:
            target_count = original_count

        # Step 1: Copy original images (subsample if needed)
        if original_count > target_count:
            selected = random.sample(imgs, target_count)
        else:
            selected = imgs[:]

        for img_name in selected:
            shutil.copy2(os.path.join(src_dir, img_name), os.path.join(dst_dir, img_name))

        copied_count = len(selected)

        # Step 2: Augment if we need more images
        if copied_count < target_count:
            needed = target_count - copied_count
            aug_count = 0

            # Load all source images for augmentation
            source_images = []
            for img_name in imgs:
                try:
                    img = load_img(os.path.join(src_dir, img_name), target_size=IMAGE_SIZE)
                    arr = img_to_array(img)
                    source_images.append(arr)
                except Exception:
                    continue

            if source_images:
                source_array = np.array(source_images)
                
                # Generate augmented images
                aug_iter = aug_gen.flow(
                    source_array,
                    batch_size=1,
                    save_to_dir=dst_dir,
                    save_prefix='aug',
                    save_format='jpeg',
                )

                for _ in range(needed):
                    next(aug_iter)
                    aug_count += 1

            final_count = copied_count + aug_count
        else:
            final_count = copied_count

        class_counts[cls] = final_count
        total_balanced += final_count

        # Status indicator based on category
        if original_count < 50:
            indicator = "🆕"  # New small class
        elif original_count < MIN_IMAGES_PER_CLASS:
            indicator = "📈"  # Augmented
        elif original_count > MAX_IMAGES_PER_CLASS:
            indicator = "📉"  # Subsampled
        else:
            indicator = "✅"  # Used as-is

        print(f"  {indicator} {cls}: {original_count} → {final_count} images")

    print(f"\n  📊 Summary:")
    print(f"     Classes:  {len(class_counts)} (skipped {len(skipped)})")
    print(f"     Original: {total_original} images")
    print(f"     Balanced: {total_balanced} images")
    print(f"     Ratio:    {max(class_counts.values())/max(min(class_counts.values()),1):.1f}x (was {5507/10:.0f}x)")

    if skipped:
        print(f"     Skipped:  {skipped}")

    return class_counts


def compute_class_weights(train_gen):
    """Compute class weights inversely proportional to class frequency."""
    class_counts = Counter()
    for cls_name, cls_idx in train_gen.class_indices.items():
        cls_dir = os.path.join(BALANCED_DIR, cls_name)
        if os.path.isdir(cls_dir):
            count = len([f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
            class_counts[cls_idx] = count

    total = sum(class_counts.values())
    n_classes = len(class_counts)

    # sklearn-style balanced weights: total / (n_classes * count_for_class)
    weights = {}
    for cls_idx, count in class_counts.items():
        weights[cls_idx] = total / (n_classes * count)

    # Normalize so mean weight is 1.0
    mean_w = np.mean(list(weights.values()))
    weights = {k: v / mean_w for k, v in weights.items()}

    # Log extreme weights
    sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    idx_to_name = {v: k for k, v in train_gen.class_indices.items()}
    print("\n  Top 5 highest-weighted classes:")
    for idx, w in sorted_w[:5]:
        print(f"    {idx_to_name.get(idx, '?'):50s} weight={w:.3f}")
    print("  Bottom 5 lowest-weighted classes:")
    for idx, w in sorted_w[-5:]:
        print(f"    {idx_to_name.get(idx, '?'):50s} weight={w:.3f}")

    return weights


def train_model():
    """Main training function."""
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    print("\n" + "=" * 60)
    print("  🌱 Disease Model V2 – Balanced 48-Class Training")
    print("=" * 60)
    print(f"  TensorFlow: {tf.__version__}")
    gpus = tf.config.list_physical_devices('GPU')
    print(f"  GPU available: {len(gpus) > 0}")
    if gpus:
        print(f"  GPU devices: {gpus}")
        # Allow GPU memory growth
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # ── Step 1: Create balanced dataset ──
    class_counts = create_balanced_dataset()

    if len(class_counts) < 10:
        print("❌ Too few classes. Check your dataset directory.")
        sys.exit(1)

    # ── Step 2: Load data with proper MobileNetV2 preprocessing ──
    print("\n" + "=" * 60)
    print("  STEP 2: Loading Data Pipeline")
    print("=" * 60)

    # Using MobileNetV2 preprocessing ([-1, 1] range) consistently
    train_datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input,
        rotation_range=25,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.15,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2,
    )

    val_datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input,
        validation_split=0.2,
    )

    train_gen = train_datagen.flow_from_directory(
        BALANCED_DIR,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True,
    )

    val_gen = val_datagen.flow_from_directory(
        BALANCED_DIR,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False,
    )

    NUM_CLASSES = len(train_gen.class_indices)
    print(f"\n  Classes:    {NUM_CLASSES}")
    print(f"  Training:   {train_gen.samples} images")
    print(f"  Validation: {val_gen.samples} images")

    # Print all class labels
    print(f"\n  Class labels ({NUM_CLASSES} total):")
    for label, idx in sorted(train_gen.class_indices.items(), key=lambda x: x[1]):
        print(f"    {idx:2d}: {label}")

    # ── Step 3: Compute class weights ──
    print("\n" + "=" * 60)
    print("  STEP 3: Computing Class Weights")
    print("=" * 60)

    class_weights = compute_class_weights(train_gen)

    # ── Step 4: Build Model ──
    print("\n" + "=" * 60)
    print("  STEP 4: Building MobileNetV2 Model")
    print("=" * 60)

    base_model = keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet',
    )
    base_model.trainable = False  # Freeze for Phase 1

    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        layers.Dense(512, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)),
        layers.Dropout(0.2),
        layers.Dense(NUM_CLASSES, activation='softmax'),
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE_PHASE1),
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )

    print(f"  Total params:     {model.count_params():,}")
    trainable = sum(np.prod(w.shape) for w in model.trainable_weights)
    print(f"  Trainable params: {trainable:,}")

    # ── Step 5: Callbacks ──
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            MODEL_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True,
            verbose=1,
            min_delta=0.001,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
    ]

    # ── Step 6: Phase 1 – Train head only ──
    print("\n" + "=" * 60)
    print(f"  PHASE 1: Training classification head ({EPOCHS_PHASE1} epochs)")
    print(f"  Learning rate: {LEARNING_RATE_PHASE1}")
    print(f"  Base model: FROZEN")
    print("=" * 60)

    history1 = model.fit(
        train_gen,
        epochs=EPOCHS_PHASE1,
        validation_data=val_gen,
        callbacks=callbacks,
        class_weight=class_weights,
    )

    # ── Step 7: Phase 2 – Fine-tune ──
    print("\n" + "=" * 60)
    print(f"  PHASE 2: Fine-tuning top {FINE_TUNE_LAYERS} layers ({EPOCHS_PHASE2} epochs)")
    print(f"  Learning rate: {LEARNING_RATE_PHASE2}")
    print("=" * 60)

    base_model.trainable = True
    for layer in base_model.layers[:-FINE_TUNE_LAYERS]:
        layer.trainable = False

    trainable_after = sum(np.prod(w.shape) for w in model.trainable_weights)
    print(f"  Trainable params (fine-tune): {trainable_after:,}")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE_PHASE2),
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )

    # Reset early stopping patience for phase 2
    callbacks_phase2 = [
        keras.callbacks.ModelCheckpoint(
            MODEL_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=6,
            restore_best_weights=True,
            verbose=1,
            min_delta=0.0005,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-8,
            verbose=1,
        ),
    ]

    history2 = model.fit(
        train_gen,
        initial_epoch=EPOCHS_PHASE1,
        epochs=EPOCHS_PHASE1 + EPOCHS_PHASE2,
        validation_data=val_gen,
        callbacks=callbacks_phase2,
        class_weight=class_weights,
    )

    # ── Step 8: Evaluate ──
    print("\n" + "=" * 60)
    print("  STEP 8: Final Evaluation")
    print("=" * 60)

    # Load the best saved model
    best_model = keras.models.load_model(MODEL_PATH)
    val_loss, val_acc = best_model.evaluate(val_gen, verbose=1)

    # Per-class accuracy for new crops
    print("\n  Per-class evaluation (new crops):")
    new_crops = ['Rice', 'Wheat', 'Onion']
    idx_to_name = {v: k for k, v in train_gen.class_indices.items()}

    # Get all predictions on validation set
    val_gen.reset()
    steps = len(val_gen)
    all_preds = []
    all_labels = []
    for step in range(steps):
        x_batch, y_batch = next(val_gen)
        preds = best_model.predict(x_batch, verbose=0)
        all_preds.extend(np.argmax(preds, axis=1))
        all_labels.extend(np.argmax(y_batch, axis=1))

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    for crop in new_crops:
        crop_indices = [idx for idx, name in idx_to_name.items() if name.startswith(crop + '___')]
        if not crop_indices:
            continue
        mask = np.isin(all_labels, crop_indices)
        if mask.sum() > 0:
            crop_acc = np.mean(all_preds[mask] == all_labels[mask]) * 100
            print(f"    {crop}: {crop_acc:.1f}% ({mask.sum()} val samples)")
        else:
            print(f"    {crop}: No validation samples")

    # ── Step 9: Save class labels ──
    print("\n  Saving class labels...")
    with open(LABELS_PATH, 'w') as f:
        for label, idx in sorted(train_gen.class_indices.items(), key=lambda x: x[1]):
            f.write(f"{idx}: {label}\n")
    print(f"  ✅ Labels saved: {LABELS_PATH}")

    # ── Step 10: Save training log ──
    training_log = {
        'timestamp': datetime.now().isoformat(),
        'tensorflow_version': tf.__version__,
        'gpu': len(gpus) > 0,
        'num_classes': NUM_CLASSES,
        'train_samples': train_gen.samples,
        'val_samples': val_gen.samples,
        'val_accuracy': float(val_acc),
        'val_loss': float(val_loss),
        'epochs_phase1': EPOCHS_PHASE1,
        'epochs_phase2': EPOCHS_PHASE2,
        'fine_tune_layers': FINE_TUNE_LAYERS,
        'model_path': MODEL_PATH,
        'class_labels': {str(idx): name for name, idx in train_gen.class_indices.items()},
        'class_weights_used': {str(k): float(v) for k, v in class_weights.items()},
    }

    with open(TRAINING_LOG_PATH, 'w') as f:
        json.dump(training_log, f, indent=2)
    print(f"  ✅ Training log: {TRAINING_LOG_PATH}")

    # ── Step 11: Cleanup ──
    print("\n  Cleaning up balanced dataset...")
    shutil.rmtree(BALANCED_DIR, ignore_errors=True)
    print("  ✅ Cleanup complete")

    # ── Final Summary ──
    model_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)

    print("\n" + "=" * 60)
    print("  ✅ TRAINING COMPLETE!")
    print("=" * 60)
    print(f"  Classes:            {NUM_CLASSES}")
    print(f"  Validation Accuracy:{val_acc * 100:.2f}%")
    print(f"  Validation Loss:    {val_loss:.4f}")
    print(f"  Model saved:        {MODEL_PATH}")
    print(f"  Model size:         {model_size:.1f} MB")
    print(f"  Labels saved:       {LABELS_PATH}")
    print("=" * 60)

    # Identify disease categories per crop
    print("\n  🌾 Crops and their diseases in the model:")
    crops = {}
    for label in sorted(train_gen.class_indices.keys()):
        crop = label.split('___')[0]
        disease = label.split('___')[1] if '___' in label else 'Unknown'
        if crop not in crops:
            crops[crop] = []
        crops[crop].append(disease)

    for crop, diseases in sorted(crops.items()):
        print(f"\n    {crop} ({len(diseases)} classes):")
        for d in diseases:
            print(f"      - {d}")

    return val_acc


if __name__ == '__main__':
    print("=" * 60)
    print("  🌱 Smart Agriculture – Disease Model V2 Training")
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    if not os.path.exists(DATA_DIR):
        print(f"❌ Dataset not found at: {DATA_DIR}")
        sys.exit(1)

    acc = train_model()

    if acc and acc < 0.7:
        print("\n⚠️  WARNING: Accuracy is below 70%. Consider:")
        print("   1. Adding more images to small classes")
        print("   2. Increasing epochs")
        print("   3. Adjusting augmentation parameters")

    print(f"\n  Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
