import paho.mqtt.client as mqtt
import time
import json

# COREFLUX CONNECTION
BROKER = "localhost"
PORT = 1883

USERNAME = "root"
PASSWORD = "coreflux"

TOPIC = "hackathon/test"

# Called when connected
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print("Connection failed:", reason_code)
        return

    print("✅ Connected to Coreflux!")
    client.subscribe(TOPIC)

# Called when a message arrives
def on_message(client, userdata, msg):
    print("📩 Received:", msg.payload.decode())

# Create MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.username_pw_set(USERNAME, PASSWORD)

client.on_connect = on_connect
client.on_message = on_message

# Connect to Coreflux
client.connect(BROKER, PORT, 60)

client.loop_start()

# Give the client time to establish the subscription
time.sleep(2)

# Send test data
data = {
    "temperature": 25.5,
    "humidity": 60
}

client.publish(TOPIC, json.dumps(data), qos=1)

print("📤 Published:", data)

time.sleep(3)

client.disconnect()
client.loop_stop()