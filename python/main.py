import time
import paho.mqtt.client as mqtt

from queue import Queue, Empty

from config import BROKER, PORT, USERNAME, PASSWORD
from populate import create_campus
from generator import Generator
from publisher import MQTTPublisher
from subscriber import MQTTSubscriber
from commands import execute_command


def main():

    # ---------------------------------
    # CAMPUS
    # ---------------------------------

    # Create the campus and its six classrooms
    campus = create_campus()

    # Generator updates the existing classroom objects
    generator = Generator(campus)

    # Incoming MQTT commands are stored here
    command_queue = Queue()

    # ---------------------------------
    # MQTT
    # ---------------------------------

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )

    client.username_pw_set(USERNAME, PASSWORD)

    # Publisher and subscriber use the same MQTT client
    publisher = MQTTPublisher(client, campus)
    subscriber = MQTTSubscriber(client, command_queue)

    # ---------------------------------
    # MQTT CALLBACKS
    # ---------------------------------

    def on_connect(client, userdata, flags, reason_code, properties):

        if reason_code.is_failure:
            print(
                "❌ Connection to Coreflux failed:",
                reason_code
            )
            return

        print("✅ Connected to Coreflux!")

        # Subscribe to commands on every connection
        subscriber.subscribe()

        # Force all classrooms to publish their current state
        publisher.reset()

    def on_disconnect(client, userdata, flags, reason_code, properties):
        print("⚠️ Disconnected from Coreflux")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # ---------------------------------
    # START CONNECTION
    # ---------------------------------

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        print("🚀 Smart Campus started!")

        # ---------------------------------
        # MAIN LOOP
        # ---------------------------------

        while True:

            # 1. Process incoming Coreflux commands
            while True:
                try:
                    command = command_queue.get_nowait()

                except Empty:
                    break

                # Validate command and update Classroom
                execute_command(campus, command)

            # 2. Update simulated sensor values
            generator.update()

            # 3. Publish classrooms whose state changed
            publisher.publish_changed_rooms()

            # 4. Wait before next simulation cycle
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n🛑 Stopping Smart Campus...")

    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()