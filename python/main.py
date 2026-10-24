import time
import paho.mqtt.client as mqtt

from queue import Queue, Empty

from config import BROKER, PORT, USERNAME, PASSWORD
from populate import create_campus
from generator import Generator
from publisher import MQTTPublisher
from subscriber import MQTTSubscriber


def apply_command(campus, command):
    """
    Apply an MQTT command to the correct classroom.
    """

    room_id = command["room_id"]
    device = command["device"]
    value = command["value"]

    room = campus.get_room(room_id)

    if room is None:
        print(f"❌ Unknown classroom: {room_id}")
        return

    try:
        # AC MODES
        if device == "ac" and value in ("ac_cool", "ac_heat", "ac_off"):
            room.set_ac(value)

        elif device == "lights" and type(value) is bool:
            room.set_lights(value)

        elif device == "door_lock" and type(value) is bool:
            room.set_door_lock(value)

        elif device == "alarm" and type(value) is bool:
            reason = command.get("reason")

            if reason is not None and not isinstance(reason, str):
                print("❌ Invalid alarm reason")
                return

            room.set_alarm(value, reason)

        elif device == "target_temperature" and type(value) in (int, float):
            room.set_target_temperature(value)

        elif device == "people_count" and type(value) is int:
            room.set_people(value)

        else:
            print(f"❌ Invalid command: {command}")
            return

        print(f"✅ {room_id}: {device} = {value}")

    except ValueError as error:
        print(f"❌ Invalid value: {error}")


def main():

    # ---------------------------------
    # CAMPUS
    # ---------------------------------

    campus = create_campus()

    generator = Generator(campus)

    command_queue = Queue()

    # ---------------------------------
    # MQTT
    # ---------------------------------

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )

    client.username_pw_set(USERNAME, PASSWORD)

    publisher = MQTTPublisher(client, campus)
    subscriber = MQTTSubscriber(client, command_queue)

    def on_connect(client, userdata, flags, reason_code, properties):

        if reason_code.is_failure:
            print("❌ Connection to Coreflux failed:", reason_code)
            return

        print("✅ Connected to Coreflux!")

        # Subscribe to classroom commands
        subscriber.subscribe()

        # Publish all rooms after connecting or reconnecting
        publisher.reset()

    def on_disconnect(client, userdata, flags, reason_code, properties):
        print("⚠️ Disconnected from Coreflux")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # ---------------------------------
    # START CONNECTION
    # ---------------------------------

    client.connect(BROKER, PORT, 60)
    client.loop_start()

    print("🚀 Smart Campus started!")

    # ---------------------------------
    # MAIN LOOP
    # ---------------------------------

    try:
        while True:

            # 1. Process commands received from Coreflux
            while True:
                try:
                    command = command_queue.get_nowait()
                except Empty:
                    break

                apply_command(campus, command)

            # 2. Update simulated classroom sensors
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