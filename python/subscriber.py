import ssl
import paho.mqtt.client as mqtt

from config import BROKER, PORT, USERNAME, PASSWORD, COMMAND_TOPIC


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print("❌ Subscriber connection failed:", reason_code)
        return

    print("✅ Subscriber connected to Coreflux!")

    client.subscribe(COMMAND_TOPIC, qos=1)

    print(f"📡 Listening to: {COMMAND_TOPIC}")


def on_message(client, userdata, msg):
    command = msg.payload.decode()

    print(f"📩 Coreflux command: {command}", flush=True)

    if command == "AC_ON":
        print("❄️ Air conditioning ON")

    elif command == "AC_OFF":
        print("🌡️ Air conditioning OFF")

    elif command == "LIGHTS_ON":
        print("💡 Lights ON")

    elif command == "LIGHTS_OFF":
        print("💡 Lights OFF")

    elif command == "DOOR_LOCK":
        print("🔒 Door locked")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

except KeyboardInterrupt:
    print("\nSubscriber stopped.")

finally:
    client.disconnect()
    