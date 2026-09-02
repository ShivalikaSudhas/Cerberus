# Security & Privacy Policy

The **IoT Smart Home Lock & Surveillance System** prioritizes edge data privacy, secure network communications, and local evidence retention policies.

---

## 🔒 Security Best Practices & Configuration

### 1. Transport Layer Security (MQTT over TLS/SSL)

By default, public unencrypted test brokers (`test.mosquitto.org:1883`) are used for fast local evaluation. For production home security deployment, **always enable TLS encryption and MQTT authentication**:

In your `.env` file:
```ini
# Production Secure Broker Setup
MQTT_BROKER=your-private-broker.com
MQTT_PORT=8883
MQTT_USE_TLS=True
MQTT_USERNAME=your_secure_user
MQTT_PASSWORD=your_secure_password_here
MQTT_TOPIC=smarthome/private_uuid_hash/alerts
```

- Setting `MQTT_USE_TLS=True` or `MQTT_PORT=8883` forces `paho-mqtt` to use TLS 1.2+ transport layer encryption (`ssl.PROTOCOL_TLSv1_2`), encrypting all alert notifications in transit between your laptop and the mobile client.
- Use a unique/secret topic path (e.g. `smarthome/<UUID>/alerts`) to prevent topic sniffing on public brokers.

---

### 2. Local Privacy & Automatic Snapshot Retention

Camera feeds and intruder evidence snapshots contain sensitive biometric data. The system implements an automatic **Privacy Retention Policy**:

- **Local Storage Only:** Face processing and image snapshots remain 100% local on the edge host device (`intruders/`). Images are never uploaded to third-party cloud servers.
- **Automatic Retention Cleanup:** The `StorageManager` automatically purges local intruder JPEG snapshots older than `MAX_SNAPSHOT_RETENTION_DAYS` (default: 30 days) every time the system starts up.

To adjust snapshot retention:
```ini
# Auto-delete intruder snapshots older than 7 days
MAX_SNAPSHOT_RETENTION_DAYS=7
```

---

### 3. Protection of Biometric Datasets & Environment Secrets

- **`.env` Exclusion:** Never commit your runtime `.env` file to version control. The `.gitignore` rule automatically excludes secrets.
- **Dataset Privacy:** Photos in `dataset/<PersonName>/` and trained weights in `models/trained_lbph.yml` are excluded via `.gitignore` to prevent leaking biometric signatures.

---

## 🛡️ Reporting a Vulnerability

If you discover a security vulnerability or security flaw in this project, please report it responsibly by contacting the maintainer or opening a private advisory. Please do not open public GitHub issues for security vulnerabilities.
