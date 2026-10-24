import json
import time
import paho.mqtt.client as mqtt

from config import BROKER, PORT, USERNAME, PASSWORD, SENSOR_TOPIC
from generator import generate_sensor_data


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print("❌ Publisher connection failed:", reason_code)
    else:
        print("✅ Publisher connected to Coreflux!")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.username_pw_set(USERNAME, PASSWORD)

client.on_connect = on_connect

try:
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    while True:
        data = generate_sensor_data()

        message = json.dumps(data)

        result = client.publish(SENSOR_TOPIC, message, qos=1)
        result.wait_for_publish()

        print("📤 Sent:", message, flush=True)

        time.sleep(2)

except KeyboardInterrupt:
    print("\nPublisher stopped.")

finally:
    client.disconnect()
    client.loop_stop()
    