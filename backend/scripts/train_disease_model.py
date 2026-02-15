"""
Train Disease Detection Model – MobileNetV2 Transfer Learning
================================================================
Trains a CNN on the PlantVillage dataset for 38-class crop disease
classification using MobileNetV2 as a feature extractor.

Dataset:
  Download PlantVillage from Kaggle:
  https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset

  Expected structure:
    data/plantvillage/
      ├── Apple___Apple_scab/
      ├── Apple___Black_rot/
      ├── ...
      └── Tomato___healthy/

Requirements:
  - Python 3.10 – 3.12
  - pip install tensorflow numpy matplotlib

Usage:
  python scripts/train_disease_model.py --data_dir data/plantvillage --epochs 15

Output:
  models/disease_model.h5
"""

import os
import argparse
import numpy as np

# ──────────────────────────────────────────
# Parse arguments
# ──────────────────────────────────────────

parser = argparse.ArgumentParser(description='Train crop disease detection model')
parser.add_argument('--data_dir', type=str, required=True,
                    help='Path to PlantVillage dataset directory')
parser.add_argument('--epochs', type=int, default=15,
                    help='Number of training epochs (default: 15)')
parser.add_argument('--batch_size', type=int, default=32,
                    help='Batch size (default: 32)')
parser.add_argument('--learning_rate', type=float, default=0.001,
                    help='Learning rate (default: 0.001)')
parser.add_argument('--fine_tune_layers', type=int, default=30,
                    help='Number of top MobileNetV2 layers to fine-tune (default: 30)')
parser.add_argument('--output', type=str, default=None,
                    help='Output model path (default: models/disease_model.h5)')


def main():
    args = parser.parse_args()

    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    print("=" * 60)
    print("🌱 Smart Agriculture – Disease Model Training")
    print("=" * 60)
    print(f"TensorFlow version: {tf.__version__}")
    print(f"GPU available: {len(tf.config.list_physical_devices('GPU')) > 0}")

    # ──────────────────────────────────────────
    # 1. Data Loading & Augmentation
    # ──────────────────────────────────────────

    IMAGE_SIZE = (224, 224)
    BATCH_SIZE = args.batch_size

    # Training augmentation
    # NOTE: MobileNetV2 expects inputs[-1, 1]. 
    # We use the built-in preprocess_input function instead of rescale=1./255
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

    print(f"\nLoading data from: {args.data_dir}")

    train_generator = train_datagen.flow_from_directory(
        args.data_dir,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True,
    )

    val_generator = train_datagen.flow_from_directory(
        args.data_dir,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False,
    )

    NUM_CLASSES = len(train_generator.class_indices)
    print(f"Number of classes: {NUM_CLASSES}")
    print(f"Training samples: {train_generator.samples}")
    print(f"Validation samples: {val_generator.samples}")
    print(f"Class labels: {list(train_generator.class_indices.keys())}")

    # ──────────────────────────────────────────
    # 2. Build Model (MobileNetV2 + Custom Head)
    # ──────────────────────────────────────────

    print("\nBuilding MobileNetV2 model...")

    base_model = keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet',
    )

    # Freeze all base layers initially
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
        optimizer=keras.optimizers.Adam(learning_rate=args.learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )

    model.summary()

    # ──────────────────────────────────────────
    # 3. Callbacks
    # ──────────────────────────────────────────

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = args.output or os.path.join(BASE_DIR, 'models', 'disease_model.h5')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            output_path,
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
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
    ]

    # ──────────────────────────────────────────
    # 4. Phase 1: Train head only (base frozen)
    # ──────────────────────────────────────────

    print("\n" + "=" * 60)
    print("PHASE 1: Training classification head (base frozen)")
    print("=" * 60)

    initial_epochs = min(args.epochs, 5)

    history1 = model.fit(
        train_generator,
        epochs=initial_epochs,
        validation_data=val_generator,
        callbacks=callbacks,
    )

    # ──────────────────────────────────────────
    # 5. Phase 2: Fine-tune top layers of MobileNetV2
    # ──────────────────────────────────────────

    if args.epochs > 5:
        print("\n" + "=" * 60)
        print(f"PHASE 2: Fine-tuning top {args.fine_tune_layers} layers")
        print("=" * 60)

        base_model.trainable = True

        # Freeze all layers except the top N
        for layer in base_model.layers[:-args.fine_tune_layers]:
            layer.trainable = False

        # Recompile with lower learning rate
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=args.learning_rate / 10),
            loss='categorical_crossentropy',
            metrics=['accuracy'],
        )

        history2 = model.fit(
            train_generator,
            initial_epoch=initial_epochs,
            epochs=args.epochs,
            validation_data=val_generator,
            callbacks=callbacks,
        )

    # ──────────────────────────────────────────
    # 6. Final save & evaluation
    # ──────────────────────────────────────────

    model.save(output_path)

    val_loss, val_acc = model.evaluate(val_generator)

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"  Validation Accuracy: {val_acc * 100:.2f}%")
    print(f"  Validation Loss:     {val_loss:.4f}")
    print(f"  Model saved to:      {output_path}")
    print(f"  Model size:          {os.path.getsize(output_path) / (1024*1024):.1f} MB")
    print("=" * 60)

    # Save class labels for reference
    labels_path = os.path.join(os.path.dirname(output_path), 'class_labels.txt')
    with open(labels_path, 'w') as f:
        for label, idx in sorted(train_generator.class_indices.items(), key=lambda x: x[1]):
            f.write(f"{idx}: {label}\n")
    print(f"  Class labels saved to: {labels_path}")


if __name__ == '__main__':
    main()
