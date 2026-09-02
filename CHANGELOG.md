# Changelog

All notable changes to the **IoT Smart Home Lock & Surveillance System** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-09-02

### Added
- **Plugin Architecture**: Abstract Base Classes (`BaseDetector`, `BaseRecognizer`, `BaseAlertChannel`) under `modules/detectors/`, `modules/recognizers/`, and `modules/alerts/`.
- **Pydantic Configuration Schema**: `config/schema.py` documenting and validating every setting.
- **Graceful `.env` Error Handling**: `config/settings.py` displays clear setup guidance if `.env` is missing instead of crashing silently.
- **Unique MQTT Client IDs**: Automatically appends UUID to publisher client IDs to prevent session conflicts on reconnect.
- **Human-Readable Alert Formatting**: MQTT alert messages formatted as clean plain text with emoji indicators for phone subscribers.
- **Comprehensive `.gitignore`**: Excludes private datasets, trained weights, log files, virtual environments, and `.env` secrets.

### Changed
- Refactored `FaceEngine` to orchestrate pluggable detector and recognizer plugins while preserving exact API contract.
- Refactored `AlertSystem` to dispatch alerts across a list of pluggable alert channel plugins.
- Switched default public MQTT broker to `test.mosquitto.org` for zero-configuration testing.
- Removed all hardcoded absolute Windows file paths across codebase and documentation.

### Fixed
- Fixed bug where MQTT client loop dropped alerts on rapid system restarts due to duplicate client ID session revocation.
- Fixed unhandled exception when `.env` configuration file was missing on fresh installs.

---

## [1.0.0] - 2026-09-01

### Added
- Initial baseline release of IoT Smart Home Lock & Surveillance System.
- OpenCV Haar Cascade frontal face detection.
- Local Binary Patterns Histograms (LBPH) face recognition engine.
- Instant model loading from `models/trained_lbph.yml` and `models/labels.json`.
- Offline Text-To-Speech (TTS) audio alert synthesizer using `pyttsx3`.
- Basic MQTT publisher broadcasting JSON alerts to `smarthome/lock/alerts`.
- Local intruder snapshot JPEG capture and CSV event logging (`intruders/intruder_log.csv`).
- Standalone dataset model trainer (`train_model.py`).
- Standalone terminal MQTT alert subscriber (`mqtt_subscriber.py`).

---

## 🗺️ Roadmap & Future Enhancements

- [ ] **Deep Learning Face Recognition**: Implement `YuNetRecognizer` and `FaceNetRecognizer` plugins under `modules/recognizers/` for higher accuracy under varying lighting conditions.
- [ ] **Person & Object Detection**: Add YOLOv8 / MobileNet SSD detector plugins under `modules/detectors/` to reduce false positives (e.g. distinguishing pets from human intruders).
- [ ] **Multi-Camera Object Tracking**: Implement DeepSORT / ByteTrack tracking across multiple CCTV RTSP streams.
- [ ] **Telegram & Email Alert Plugins**: Add `TelegramAlertChannel` and `EmailAlertChannel` under `modules/alerts/` for direct mobile photo alerts via Telegram Bot API.
- [ ] **Explainable AI (XAI) & Heatmaps**: Generate Grad-CAM feature heatmaps overlaid on saved intruder snapshot images.
- [ ] **Edge Hardware Acceleration**: Port models to TensorRT (NVIDIA Jetson) and OpenVINO (Intel NUC / Raspberry Pi AI Hat).
- [ ] **Web Dashboard UI**: Add a real-time FastAPI / React web dashboard for viewing live CCTV streams and managing authorized user datasets.
