# CCTV Streams & Raspberry Pi Integration Directory

This folder is reserved for configuring multiple IP cameras, CCTV RTSP video streams, and Raspberry Pi camera network streams.

### Raspberry Pi RTSP Stream Setup:
To stream video from a Raspberry Pi (with Pi Camera or USB webcam) to this Smart Home Lock system over your local Wi-Fi:

1. **On the Raspberry Pi**, install `libcamera` / `rtsp-simple-server` or `mjpg-streamer`:
   ```bash
   rpicam-vid -t 0 --inline --listen -o tcp://0.0.0.0:8554
   ```
2. **In this application**, set the `CAMERA_SOURCE` environment variable or edit `.env`:
   ```env
   CAMERA_SOURCE=rtsp://<RASPBERRY_PI_IP>:8554/stream
   ```

### External USB Camera Setup:
If using a second USB camera plugged into your PC/Laptop:
```env
CAMERA_SOURCE=1
```
(where `0` is internal webcam and `1` is external USB camera).
