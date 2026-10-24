import json
import time
import paho.mqtt.client as mqtt

from config import BROKER, PORT, USERNAME, PASSWORD, SENSOR_TOPIC
from generator import Generator
from populate import create_campus


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print("❌ Publisher connection failed:", reason_code)
    else:
        print("✅ Publisher connected to Coreflux!")


# Create the campus with its 6 classrooms
campus = create_campus()

# Create the generator using the same campus
generator = Generator(campus)

# MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect

try:
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    # Wait until MQTT connection is established
    while not client.is_connected():
        time.sleep(0.1)

    # Publish initial state of all 6 classrooms
    for room in campus.get_all_rooms():
        topic = f"{SENSOR_TOPIC}/{room.room_id}/state"
        message = json.dumps(room.get_state())

        result = client.publish(topic, message, qos=1)
        result.wait_for_publish()

        print(f"📤 Initial state {room.room_id}: {message}")

    while True:
        # Update the simulation
        changed_rooms = generator.update()

        # Publish only rooms that changed
        for room in changed_rooms:
            topic = f"{SENSOR_TOPIC}/{room.room_id}/state"
            message = json.dumps(room.get_state())

            result = client.publish(topic, message, qos=1)
            result.wait_for_publish()

            print(f"📤 Updated {room.room_id}: {message}", flush=True)

        time.sleep(2)

except KeyboardInterrupt:
    print("\nPublisher stopped.")

finally:
    client.disconnect()
    client.loop_stop()