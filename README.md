# 🏠 IoT Smart Home Lock & Surveillance System

A production-ready Computer Vision & IoT edge surveillance solution built according to the **SmartHome Lock-CCN REPORT** specifications. Features real-time face detection, LBPH recognition, and multi-channel intruder alerts (MQTT notifications + local TTS voice audio).

---

## 📁 Project Directory Layout

```text
.
├── config/
│   ├── schema.py            # Pydantic configuration schema & settings validation
│   └── settings.py          # Environment configuration loader with graceful error handling
├── modules/
│   ├── camera_stream.py     # USB camera, webcam, Raspberry Pi & CCTV RTSP stream manager
│   ├── storage.py           # Intruder JPEG snapshot capture & CSV audit logger (with retention policy)
│   ├── face_engine.py       # Modular face detection & recognition orchestrator
│   ├── alert_system.py      # Multi-channel alert dispatcher
│   ├── detectors/           # Swappable face detection plugins (BaseDetector ABC)
│   │   ├── base.py
│   │   └── haar_detector.py
│   ├── recognizers/         # Swappable face recognition plugins (BaseRecognizer ABC)
│   │   ├── base.py
│   │   └── lbph_recognizer.py
│   └── alerts/              # Swappable alert notification plugins (BaseAlertChannel ABC)
│       ├── base.py
│       ├── mqtt_alert.py
│       └── tts_alert.py
├── dataset/                 # Authorized resident photos (e.g. dataset/Alice/*.jpg)
│   └── README.md
├── models/                  # ML models & classifier cascades
│   └── README.md
├── intruders/               # Captured intruder snapshots & audit log (intruder_log.csv)
│   └── .gitkeep
├── .env.example             # Configuration template
├── requirements.txt         # Project dependencies
├── LICENSE                  # MIT License
├── SECURITY.md              # Security policy, TLS setup & data privacy guidelines
├── CHANGELOG.md             # Release history & technical roadmap
├── train_model.py           # Standalone dataset trainer script
├── facerecog.py             # Main surveillance entry point
└── mqtt_subscriber.py       # Remote terminal MQTT alert subscriber
```

---

## 🚀 Quick Start Guide

### 1. Installation & Environment Setup

Clone the repository and install dependencies inside a virtual environment:

```bash
# Clone the repository
git clone https://github.com/your-username/intruder-detection-opencv.git
cd intruder-detection-opencv

# Create and activate virtual environment
python -m venv env

# Windows
env\Scripts\activate
# Linux/macOS
source env/bin/activate

# Install required dependencies
pip install -r requirements.txt

# Create runtime configuration from template
cp .env.example .env
```

### 2. Download Pre-Trained Model Assets (Optional)

The system automatically falls back to OpenCV's built-in Haar Cascade classifier. However, to save a local copy into `models/`:

- **Haar Cascade XML:** [haarcascade_frontalface_default.xml](https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml)  
  *Save to: `models/haarcascade_frontalface_default.xml`*

### 3. Add Authorized Residents & Train Model

1. Create a folder for each authorized person under `dataset/<PersonName>/`:
   ```text
   dataset/
   ├── Alice/
   │   ├── photo1.jpg
   │   └── photo2.jpg
   └── Bob/
       ├── photo1.jpg
       └── photo2.jpg
   ```
2. Run the dataset trainer:
   ```bash
   python train_model.py
   ```
   *This compiles `models/trained_lbph.yml` and `models/labels.json`.*

### 4. Run Surveillance System

Launch the live surveillance feed:

```bash
python facerecog.py
```

---

## 🎮 Live Keyboard Controls

| Key | Action |
|:---:|:---|
| **`q`** | Quit application cleanly and release camera resources. |
| **`r`** | Hot-reload and retrain face model from dataset without restarting. |
| **`s`** | Save manual frame snapshot to `intruders/`. |

---

## 🧩 Extensibility Design

This project is engineered to be modular and extensible by design. You can swap in custom face detectors, recognizers, or alert notification channels by inheriting from the abstract base classes in `modules/*/base.py`:

- **Detectors (`modules/detectors/base.py`):** Inherit from `BaseDetector` to add new face detection backends (e.g. OpenCV DNN, YuNet, MediaPipe, MTCNN).
- **Recognizers (`modules/recognizers/base.py`):** Inherit from `BaseRecognizer` to add deep learning recognizers (e.g. FaceNet, ArcFace, Dlib).
- **Alert Channels (`modules/alerts/base.py`):** Inherit from `BaseAlertChannel` to add notification channels (e.g. Telegram Bot, Email, Webhook, Discord).

### Example Extension
```python
from modules.alerts.base import BaseAlertChannel

class CustomWebhookAlertChannel(BaseAlertChannel):
    def send_alert(self, image_path=None, camera_name="Front Door Camera") -> bool:
        # Custom webhook alert logic
        return True

    def close(self):
        pass
```

---

## 🛡️ Security & Privacy Architecture

> ⚠️ **Important Security Note:** Out-of-the-box configuration defaults to an unencrypted public MQTT test broker (`test.mosquitto.org:1883`) to allow instant evaluation without setup overhead. **TLS encryption and MQTT authentication are opt-in configuration features.**

For production and private deployments:

- **Opt-In TLS/SSL Encryption:** Set `MQTT_USE_TLS=True` and `MQTT_PORT=8883` in `.env` to enforce encrypted transport layer protection.
- **Opt-In Broker Authentication:** Set `MQTT_USERNAME` and `MQTT_PASSWORD` in `.env` for authenticated private brokers.
- **Privacy Retention Policy:** `StorageManager` automatically purges local intruder snapshots older than `MAX_SNAPSHOT_RETENTION_DAYS` (default: 30 days).
- **100% Edge Processing:** Biometric face detection and recognition run strictly locally on the host device.

See [SECURITY.md](SECURITY.md) for full threat modeling and security hardening guidelines.

---

## 🗺️ Roadmap & Release Evolution

| Version | Status | Key Features |
|:---:|:---:|:---|
| **v1.0.0** | Released | Core OpenCV Haar + LBPH engine, basic MQTT broadcast, TTS voice alerts, CSV audit logging. |
| **v2.0.0** | Released | Plugin ABC architecture, Pydantic schema validation, `.env` hardening, TLS/Auth support, snapshot retention policy. |
| **v2.1.0** | Planned | Deep learning face recognition (`YuNetRecognizer`, `FaceNetRecognizer`). |
| **v2.2.0** | Planned | Direct Telegram Bot photo alert channel (`TelegramAlertChannel`). |
| **v3.0.0** | Planned | Multi-camera DeepSORT tracking + Web Dashboard UI. |

See [CHANGELOG.md](CHANGELOG.md) for complete version history and details.

---

## 📄 License & Academic Reference

Built according to the **SmartHome Lock-CCN REPORT** specifications for Computer Communication and Network (BCS401G).  
Licensed under the [MIT License](LICENSE).
