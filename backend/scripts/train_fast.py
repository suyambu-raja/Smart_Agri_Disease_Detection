"""
Fast Disease Model Training – Uses subset of data for quick training.
Creates a temporary directory with N images per class, then trains.
Designed to complete in ~15 minutes on CPU.
"""

import os
import sys
import shutil
import random
import argparse
import numpy as np

# Suppress TF warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def main():
    parser = argparse.ArgumentParser(description='Fast train disease model with subset')
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--images_per_class', type=int, default=200,
                        help='Max images per class (default: 200)')
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--output', type=str, default=None)
    args = parser.parse_args()

    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    print("=" * 60)
    print("FAST Disease Model Training (Subset)")
    print("=" * 60)
    print(f"TensorFlow: {tf.__version__}")
    print(f"GPU: {len(tf.config.list_physical_devices('GPU')) > 0}")

    # ── Step 1: Create subset directory ──
    SUBSET_DIR = os.path.join(os.path.dirname(args.data_dir), '_training_subset')
    if os.path.exists(SUBSET_DIR):
        shutil.rmtree(SUBSET_DIR)

    print(f"\nCreating subset with max {args.images_per_class} images per class...")

    classes = sorted([
        d for d in os.listdir(args.data_dir)
        if os.path.isdir(os.path.join(args.data_dir, d)) and not d.startswith('_')
    ])

    total_images = 0
    skipped_classes = []
    for cls in classes:
        src = os.path.join(args.data_dir, cls)
        dst = os.path.join(SUBSET_DIR, cls)
        os.makedirs(dst, exist_ok=True)

        imgs = [f for f in os.listdir(src) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        if len(imgs) < 5:
            print(f"  WARNING: {cls} has only {len(imgs)} images (need >= 5). Skipping.")
            skipped_classes.append(cls)
            shutil.rmtree(dst)
            continue

        selected = random.sample(imgs, min(len(imgs), args.images_per_class))
        for img_name in selected:
            shutil.copy2(os.path.join(src, img_name), os.path.join(dst, img_name))
        total_images += len(selected)
        print(f"  {cls}: {len(selected)} images")

    if skipped_classes:
        print(f"\nSkipped {len(skipped_classes)} classes with < 5 images: {skipped_classes}")

    print(f"\nTotal subset: {total_images} images across {len(classes) - len(skipped_classes)} classes")

    # ── Step 2: Data loading with MobileNetV2 preprocessing ──
    IMAGE_SIZE = (224, 224)

    train_datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2,
    )

    train_gen = train_datagen.flow_from_directory(
        SUBSET_DIR, target_size=IMAGE_SIZE, batch_size=args.batch_size,
        class_mode='categorical', subset='training', shuffle=True,
    )

    val_gen = train_datagen.flow_from_directory(
        SUBSET_DIR, target_size=IMAGE_SIZE, batch_size=args.batch_size,
        class_mode='categorical', subset='validation', shuffle=False,
    )

    NUM_CLASSES = len(train_gen.class_indices)
    print(f"\nClasses: {NUM_CLASSES}")
    print(f"Training batches: {len(train_gen)}")
    print(f"Validation batches: {len(val_gen)}")

    # ── Step 3: Build model ──
    print("\nBuilding MobileNetV2 model...")

    base_model = keras.applications.MobileNetV2(
        input_shape=(224, 224, 3), include_top=False, weights='imagenet',
    )
    base_model.trainable = False

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

    # ── Step 4: Output path ──
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = args.output or os.path.join(BASE_DIR, 'models', 'disease_model.h5')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            output_path, monitor='val_accuracy', save_best_only=True, verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy', patience=4, restore_best_weights=True, verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=2, min_lr=1e-7, verbose=1,
        ),
    ]

    # ── Step 5: Phase 1 – Train head (base frozen) ──
    print("\n" + "=" * 60)
    print("PHASE 1: Training head (base frozen)")
    print("=" * 60)

    initial_epochs = min(args.epochs, 5)
    model.fit(train_gen, epochs=initial_epochs, validation_data=val_gen, callbacks=callbacks)

    # ── Step 6: Phase 2 – Fine-tune top layers ──
    if args.epochs > 5:
        print("\n" + "=" * 60)
        print("PHASE 2: Fine-tuning top 30 layers")
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
            train_gen, initial_epoch=initial_epochs, epochs=args.epochs,
            validation_data=val_gen, callbacks=callbacks,
        )

    # ── Step 7: Save final model & labels ──
    model.save(output_path)

    val_loss, val_acc = model.evaluate(val_gen)

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"  Validation Accuracy: {val_acc * 100:.2f}%")
    print(f"  Validation Loss:     {val_loss:.4f}")
    print(f"  Model saved to:      {output_path}")
    print(f"  Model size:          {os.path.getsize(output_path) / (1024*1024):.1f} MB")

    # Save class labels
    labels_path = os.path.join(os.path.dirname(output_path), 'class_labels.txt')
    with open(labels_path, 'w') as f:
        for label, idx in sorted(train_gen.class_indices.items(), key=lambda x: x[1]):
            f.write(f"{idx}: {label}\n")
    print(f"  Class labels saved to: {labels_path}")
    print("=" * 60)

    # ── Cleanup subset ──
    shutil.rmtree(SUBSET_DIR, ignore_errors=True)
    print("  Cleaned up temporary subset directory.")


if __name__ == '__main__':
    main()
