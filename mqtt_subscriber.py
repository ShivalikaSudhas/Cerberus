import json
import time
import logging
import paho.mqtt.client as mqtt
from config.settings import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [MQTT-SUBSCRIBER] %(message)s')
logger = logging.getLogger("MQTTSubscriber")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info(f"Successfully connected to MQTT Broker '{MQTT_BROKER}:{MQTT_PORT}'")
        logger.info(f"Subscribing to alert topic: '{MQTT_TOPIC}'...")
        client.subscribe(MQTT_TOPIC)
        logger.info("Listening for real-time intruder alert notifications...")
    else:
        logger.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        logger.info("=" * 60)
        logger.info("🚨 REAL-TIME INTRUDER ALERT RECEIVED ON MOBILE CLIENT 🚨")
        logger.info(f"Event      : {payload.get('event')}")
        logger.info(f"Timestamp  : {payload.get('timestamp')}")
        logger.info(f"Camera     : {payload.get('camera')}")
        logger.info(f"Image Path : {payload.get('image_saved')}")
        logger.info(f"Message    : {payload.get('message')}")
        logger.info("=" * 60)
    except Exception as e:
        logger.warning(f"Raw MQTT Message received: {msg.payload.decode('utf-8')} (Parsing note: {e})")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="SmartHome_MobileApp_Subscriber")
    client.on_connect = on_connect
    client.on_message = on_message

    logger.info(f"Connecting subscriber client to {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Stopping MQTT subscriber client...")
        client.disconnect()

if __name__ == "__main__":
    main()
