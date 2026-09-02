# IoT Smart Home Lock & Surveillance System — Full Specification Sheet

**Academic Reference:** Computer Communication and Network (BCS401G)
**Version:** 2.0 (Updated: September 2026)
**Architecture:** Modular Edge-AI + MQTT IoT Distributed System

---

## 1. General System Overview

| Parameter | Details |
|:---|:---|
| **Project Name** | IoT Smart Home Lock & Surveillance System |
| **Course** | Computer Communication and Network (BCS401G) |
| **Domain** | Computer Vision · IoT · Network Communication · Edge AI |
| **Architecture** | Modular Client-Broker Distributed Architecture |
| **Main Entry Point** | `facerecog.py` |
| **Remote Client** | `mqtt_subscriber.py` / MyMQTT Mobile App |
| **MQTT Broker** | `test.mosquitto.org` (Port 1883) |
| **MQTT Topic** | `smarthome/lock/alerts` |
| **Alert Format** | Plain-text human-readable (Emoji + Timestamp + Image Name) |

---

## 2. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  LAPTOP / EDGE DEVICE                   │
│                                                         │
│  Webcam ──► CameraStream ──► FaceEngine                 │
│                                    │                    │
│                           Unknown? │                    │
│                                    ▼                    │
│                         StorageManager ──► intruders/   │
│                                    │                    │
│                                    ▼                    │
│                           AlertSystem                   │
│                          ┌────────────┐                 │
│                          │ MQTT Pub   │──► test.mosquitto.org
│                          │ TTS Voice  │──► Laptop Speaker
│                          └────────────┘                 │
└─────────────────────────────────────────────────────────┘
                                │ MQTT Broker (Internet)
                                ▼
┌─────────────────────────────────────────────────────────┐
│                    MOBILE PHONE                         │
│         MyMQTT App ──► smarthome/lock/alerts            │
│         Receives: 🚨 INTRUDER ALERT! + Timestamp + Image│
└─────────────────────────────────────────────────────────┘
```

---

## 3. Hardware Specifications & Device Compatibility

| Component | Specification |
|:---|:---|
| **Primary Host** | x86_64 Dual-Core 2.0+ GHz Laptop or ARM64 Raspberry Pi 4/5 |
| **RAM** | Minimum 2 GB (4 GB recommended) |
| **Storage** | 500 MB free disk space |
| **Webcam (Default)** | Integrated Laptop Webcam — Source Index `0` |
| **External USB Camera** | USB Video Class (UVC) — Source Index `1`, `2` |
| **Raspberry Pi Camera** | CSI Camera via `libcamera` / `rpicam-vid` RTSP |
| **CCTV / IP Camera** | RTSP/HTTP H.264 Stream (`rtsp://<ip>:<port>/stream`) |
| **Mobile Phone** | Android/iOS with MyMQTT app (any network — WiFi or 4G/LTE) |
| **Internet** | Required for MQTT broker connection on both devices |

---

## 4. Software Stack & Dependencies

| Library | Version | Role |
|:---|:---|:---|
| **Python** | 3.10+ | Runtime (inside `env/` virtual environment) |
| **opencv-contrib-python** | ≥ 5.0.0.93 | Frame capture, Haar Cascade detection, LBPH recognition |
| **paho-mqtt** | ≥ 2.1.0 | MQTT publish/subscribe client (MQTT v3 API v2) |
| **pyttsx3** | ≥ 2.99 | Offline TTS voice alert engine |
| **pywin32** | ≥ 312 | Windows COM interface required by pyttsx3 |
| **numpy** | ≥ 2.2.6 | Image matrix math and array processing |
| **python-dotenv** | ≥ 1.0.0 | `.env` file loader for environment configuration |

---

## 5. Project Directory Structure

```
d:\intruder detection opencv\
│
├── facerecog.py              ← Main surveillance entry point
├── train_model.py            ← Standalone LBPH dataset trainer
├── mqtt_subscriber.py        ← PC/terminal MQTT alert subscriber client
│
├── config\
│   └── settings.py           ← Centralised .env loader & path constants
│
├── modules\
│   ├── __init__.py
│   ├── camera_stream.py      ← Multi-source camera manager + auto-reconnect
│   ├── face_engine.py        ← Haar Cascade + LBPH face recognition engine
│   ├── alert_system.py       ← MQTT publisher + TTS voice alert system
│   └── storage.py            ← Intruder JPEG snapshot + CSV audit logger
│
├── models\
│   ├── haarcascade_frontalface_default.xml   ← OpenCV face detector
│   ├── trained_lbph.yml                      ← Trained LBPH weights
│   └── labels.json                           ← Person name ↔ label ID map
│
├── dataset\
│   └── <PersonName>\         ← Authorized user face image folders
│       └── *.jpg / *.png
│
├── intruders\
│   ├── intruder_YYYYMMDD_HHMMSS.jpg  ← Captured intruder snapshots
│   └── intruder_log.csv              ← Audit log of all intruder events
│
├── .env                      ← Runtime configuration (active)
├── .env.example              ← Configuration template
├── requirements.txt          ← pip dependencies list
└── spec_sheet.md             ← This document
```

---

## 6. Configuration Reference (`.env`)

```ini
# Camera Stream Configuration
CAMERA_SOURCE=0           # 0=laptop webcam, 1=USB cam, or RTSP URL string
FRAME_WIDTH=640
FRAME_HEIGHT=480
FPS=30

# Face Recognition Settings
CONFIDENCE_THRESHOLD=70.0
LBPH_CONFIDENCE_THRESHOLD=70.0   # LBPH distance <= 70.0 = authorized match

# MQTT Alert Settings
MQTT_BROKER=test.mosquitto.org
MQTT_PORT=1883
MQTT_TOPIC=smarthome/lock/alerts

# Alert Cooldown (seconds between repeated alerts)
UNKNOWN_COOLDOWN_SECONDS=5.0

# Voice Notification
ENABLE_VOICE_ALERT=True
```

---

## 7. Module-by-Module Implementation Details

---

### 7.1 `facerecog.py` — Main Surveillance Entry Point

**Purpose:** Orchestrates all modules together in a single real-time loop.

**Execution Flow:**
1. Initializes `CameraStream` (reads source from `.env`)
2. Loads `FaceEngine` with pre-trained LBPH model (< 0.8s cold start)
3. Initializes `StorageManager` pointing to `intruders/`
4. Initializes `AlertSystem` with MQTT broker + TTS
5. Enters main `while True` loop:
   - Reads frame from camera
   - Runs `detect_and_recognize(frame)`
   - Draws colored bounding boxes (🟢 Green = authorized, 🔴 Red = unknown)
   - If unknown face detected → saves snapshot → triggers MQTT + voice alert
   - Renders HUD overlay with keyboard controls

**Key Design Decision:** `has_unknown` flag is set per-frame; alert is triggered once per cooldown window (5 seconds default) to prevent spam.

**Keyboard Controls:**

| Key | Action |
|:---:|:---|
| `q` | Graceful shutdown — releases camera and disconnects MQTT |
| `r` | Hot-retrain face model from dataset without restarting |
| `s` | Manual snapshot saved to `intruders/snapshot_<timestamp>.jpg` |

---

### 7.2 `modules/camera_stream.py` — Camera Stream Manager

**Purpose:** Abstraction layer for all camera source types with resilience.

**Supported Sources:**
- `int` (0, 1, 2…) → USB/Webcam via `cv2.VideoCapture(index, cv2.CAP_DSHOW)` on Windows
- `str` RTSP URL → IP cameras and Raspberry Pi CSI (`rpicam-vid` RTSP stub)
- HTTP stream URL → network video feeds

**Key Features:**
- **Exponential Backoff Reconnect:** On stream drop, waits `min(2^attempt, 10)` seconds before retrying
- **DirectShow Backend (Windows):** Uses `cv2.CAP_DSHOW` automatically on Windows for lower latency
- **Configurable Resolution:** Width × Height × FPS set via OpenCV `CAP_PROP_*` at init

**Auto-Reconnect Logic:**
```
Attempt 1 → wait 2s → reconnect
Attempt 2 → wait 4s → reconnect
Attempt 3 → wait 8s → reconnect
Attempt 4+ → wait 10s (capped) → reconnect
```

---

### 7.3 `modules/face_engine.py` — Face Detection & Recognition Engine

**Purpose:** Two-stage face pipeline: detection → recognition.

**Stage 1 — Detection (Haar Cascade):**
- Classifier: `haarcascade_frontalface_default.xml`
- Parameters: `scaleFactor=1.2`, `minNeighbors=5`, `minSize=(50,50)`
- Input: BGR frame → converted to grayscale for processing

**Stage 2 — Recognition (LBPH):**
- Algorithm: Local Binary Patterns Histograms (`cv2.face.LBPHFaceRecognizer`)
- Match rule: `distance ≤ 70.0` → **Authorized** (returns person name)
- Match rule: `distance > 70.0` → **Unknown** (triggers intruder alert)
- Model files: `models/trained_lbph.yml` + `models/labels.json`

**Instant Load Design:** Model is pre-trained and saved. On startup, FaceEngine reads the YML file directly — no dataset scan needed. Cold-start time < 0.8 seconds.

**Auto-Train Fallback:** If `trained_lbph.yml` is missing on startup, automatically calls `train_standalone()` from `train_model.py`.

**Live Retrain (key `r`):** Calls `train_standalone()` then `load_model()` — model is hot-swapped without restarting the surveillance loop.

---

### 7.4 `modules/alert_system.py` — MQTT Publisher + TTS Voice System

**Purpose:** Sends real-time alerts to mobile phone via MQTT and laptop speaker via TTS.

**MQTT Implementation:**
- Library: `paho-mqtt` v2 (`CallbackAPIVersion.VERSION2`)
- Client ID: Random unique per run — `SmartHome_Sender_<8-char UUID hex>`
  - *(Prevents broker session conflicts on restart — fixes "works once" bug)*
- Connection: `connect_async()` + `loop_start()` — non-blocking background thread
- `on_connect` callback: sets `is_connected = True` only after broker confirms connection
- Pre-publish wait: waits up to 3 seconds for `is_connected` before each publish
- QoS Level: 1 (at-least-once delivery guarantee)

**Alert Message Format (sent to phone):**
```
🚨 INTRUDER ALERT!
📷 Camera  : Front Door Camera
🕐 Time    : 2026-09-02 15:10:02
🖼 Image   : intruder_20260902_151002.jpg
⚠ Warning  : Unknown person detected!
```

**TTS Voice Alert:**
- Engine: `pyttsx3` (offline, no internet required)
- Speech rate: 160 words/minute
- Volume: 1.0 (maximum)
- Threading: Runs in daemon thread — does not block main video loop

**Cooldown:** 5.0 seconds between consecutive alerts (configurable via `UNKNOWN_COOLDOWN_SECONDS`)

---

### 7.5 `modules/storage.py` — Intruder Snapshot & Audit Logger

**Purpose:** Persists intruder evidence to disk.

**Snapshot:**
- File: `intruders/intruder_YYYYMMDD_HHMMSS.jpg`
- Format: High-quality JPEG via `cv2.imwrite()`

**Audit Log:**
- File: `intruders/intruder_log.csv`
- Columns: `Timestamp`, `Image_Path`, `Status`, `Camera_Source`
- Appended on every detection event

---

### 7.6 `train_model.py` — Standalone LBPH Trainer

**Purpose:** Trains the face recognition model from labeled image folders.

**Execution Steps:**
1. Loads Haar Cascade for face detection within training images
2. Scans `dataset/<PersonName>/` folders — each folder = one authorized person
3. For each image: reads grayscale → detects face ROI → appends to training list
4. Trains `LBPHFaceRecognizer` on collected face ROIs
5. Saves `models/trained_lbph.yml` (model weights) + `models/labels.json` (ID → name map)

**Supported Image Formats:** `.jpg`, `.jpeg`, `.png`

**Run Command:**
```powershell
& "d:\intruder detection opencv\env\Scripts\python.exe" train_model.py
```

---

### 7.7 `mqtt_subscriber.py` — PC Terminal Alert Subscriber

**Purpose:** Simulates a remote terminal receiver for MQTT alerts (alternative to mobile app).

**Usage:** Run on any PC connected to the internet to receive live alert logs:
```powershell
& "d:\intruder detection opencv\env\Scripts\python.exe" mqtt_subscriber.py
```

**Output Example:**
```
============================================================
🚨 REAL-TIME INTRUDER ALERT RECEIVED ON MOBILE CLIENT 🚨
Event      : INTRUDER_DETECTED
Timestamp  : 2026-09-02 15:10:02
Camera     : Front Door Camera
Image Path : D:\intruder detection opencv\intruders\intruder_20260902_151002.jpg
Message    : Warning! Unknown person detected at smart home lock.
============================================================
```

---

### 7.8 `config/settings.py` — Centralised Configuration Loader

**Purpose:** Single source of truth for all path constants and environment variable parsing.

**Key Constants Exported:**
| Constant | Value / Source |
|:---|:---|
| `BASE_DIR` | Project root (`Path(__file__).parent.parent`) |
| `DATASET_DIR` | `BASE_DIR / "dataset"` |
| `INTRUDERS_DIR` | `BASE_DIR / "intruders"` |
| `MODELS_DIR` | `BASE_DIR / "models"` |
| `MQTT_BROKER` | `os.getenv("MQTT_BROKER", "test.mosquitto.org")` |
| `MQTT_PORT` | `int(os.getenv("MQTT_PORT", 1883))` |
| `MQTT_TOPIC` | `os.getenv("MQTT_TOPIC", "smarthome/lock/alerts")` |
| `UNKNOWN_COOLDOWN_SECONDS` | `float(os.getenv("UNKNOWN_COOLDOWN_SECONDS", 5.0))` |
| `LBPH_CONFIDENCE_THRESHOLD` | `float(os.getenv("LBPH_CONFIDENCE_THRESHOLD", 70.0))` |
| `ENABLE_VOICE_ALERT` | `bool(os.getenv("ENABLE_VOICE_ALERT", "True"))` |

---

## 8. MQTT Network Communication Details

| Parameter | Value |
|:---|:---|
| **Broker** | `test.mosquitto.org` (Eclipse Mosquitto public test broker) |
| **Port** | `1883` (unencrypted TCP) |
| **Protocol** | MQTT v3.1.1 |
| **Topic** | `smarthome/lock/alerts` |
| **Publisher Client ID** | `SmartHome_Sender_<random 8-char hex>` (unique per run) |
| **Subscriber (Phone)** | MyMQTT app — any auto-generated client ID |
| **QoS** | Level 1 (at-least-once) |
| **Keepalive** | 60 seconds |
| **Payload Format** | Plain UTF-8 text (human-readable with emoji) |
| **Alert Cooldown** | 5.0 seconds |

**Phone Setup (MyMQTT app):**
1. Host: `test.mosquitto.org` | Port: `1883` | MQTT V3 | No login required
2. Subscribe to topic: `smarthome/lock/alerts`
3. Alerts appear in the **Subscribe** tab automatically

---

## 9. Performance Benchmarks

| Metric | Value |
|:---|:---|
| **Cold Start Time** | < 0.8 seconds (model pre-loaded from YML) |
| **Detection FPS** | 15–30 FPS on standard Dual-Core CPU |
| **MQTT Alert Latency** | < 200 ms broker-to-subscriber |
| **Voice Alert Delay** | < 50 ms (non-blocking daemon thread) |
| **RAM Footprint** | ~120 MB baseline |
| **Alert Cooldown** | 5.0 seconds (configurable) |

---

## 10. Execution Commands

```powershell
# Step 1 — Install dependencies
& "d:\intruder detection opencv\env\Scripts\pip.exe" install -r requirements.txt

# Step 2 — Add authorized face images to dataset
# Place images in: dataset\<PersonName>\*.jpg

# Step 3 — Train the face recognition model
& "d:\intruder detection opencv\env\Scripts\python.exe" train_model.py

# Step 4 — Run the surveillance system
& "d:\intruder detection opencv\env\Scripts\python.exe" facerecog.py

# Optional — Run PC terminal subscriber (separate window)
& "d:\intruder detection opencv\env\Scripts\python.exe" mqtt_subscriber.py
```

---

## 11. Known Issues & Fixes Applied

| Issue | Root Cause | Fix Applied |
|:---|:---|:---|
| MQTT alerts not sent on 2nd run | Hardcoded duplicate Client ID caused broker to kick stale session | UUID-based unique Client ID per run |
| Publish before connection ready | `is_connected` set before broker confirms | `on_connect` callback sets flag only on broker ACK |
| Phone showed raw JSON | Alert payload was a JSON dict | Changed to human-readable plain text with emoji |
| HiveMQ refused phone connection | HiveMQ public broker now requires authentication | Switched to `test.mosquitto.org` (fully open) |
| Phone subscribed to wrong topic | Subscribed to `smarthome/lock/alert` (missing `s`) | Corrected to `smarthome/lock/alerts` |
