import os
import cv2
import json
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [TRAINER] %(message)s')
logger = logging.getLogger("TrainModel")

def train_standalone():
    base_dir = Path(__file__).resolve().parent
    dataset_dir = base_dir / "dataset"
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Haar Cascade Classifier
    cascade_path = models_dir / "haarcascade_frontalface_default.xml"
    if not cascade_path.exists():
        cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"

    face_cascade = cv2.CascadeClassifier(str(cascade_path))
    if face_cascade.empty():
        logger.error(f"Failed to load Haar Cascade XML from: {cascade_path}")
        return False

    # 2. Scan dataset directory
    logger.info(f"Scanning dataset directory: {dataset_dir}")
    person_dirs = [d for d in dataset_dir.iterdir() if d.is_dir()]

    if not person_dirs:
        logger.warning("No person directories found under dataset/. Please add dataset/<PersonName>/*.jpg")
        return False

    faces = []
    labels = []
    label_map = {}
    label_id = 0

    for person_dir in person_dirs:
        person_name = person_dir.name
        image_paths = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.png")) + list(person_dir.glob("*.jpeg"))

        if not image_paths:
            logger.warning(f"No images found for '{person_name}'. Skipping...")
            continue

        label_map[str(label_id)] = person_name
        logger.info(f"Processing '{person_name}' ({len(image_paths)} image sample(s))...")

        for img_path in image_paths:
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue

            # Detect face regions
            detected = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)
            for (x, y, w, h) in detected:
                face_roi = img[y:y+h, x:x+w]
                faces.append(face_roi)
                labels.append(label_id)

        label_id += 1

    if not faces or not labels:
        logger.error("No valid face samples detected in dataset. Aborting training.")
        return False

    # 3. Train LBPH Recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    logger.info(f"Training LBPH Model on {len(faces)} face region(s)...")
    recognizer.train(faces, np.array(labels))

    # 4. Save trained model YML and labels JSON
    model_yml_path = models_dir / "trained_lbph.yml"
    labels_json_path = models_dir / "labels.json"

    # Save YML model file
    try:
        recognizer.save(str(model_yml_path))
    except AttributeError:
        recognizer.write(str(model_yml_path))

    # Save labels JSON file
    with open(labels_json_path, 'w', encoding='utf-8') as f:
        json.dump(label_map, f, indent=2)

    logger.info("=" * 60)
    logger.info("✅ LBPH TRAINING COMPLETED SUCCESSFULLY!")
    logger.info(f"Trained Model Saved : {model_yml_path}")
    logger.info(f"Labels Saved        : {labels_json_path}")
    logger.info(f"Total Users Trained : {len(label_map)} ({list(label_map.values())})")
    logger.info("=" * 60)
    return True

if __name__ == "__main__":
    train_standalone()
