import json

import paho.mqtt.client as mqtt

from config import BROKER, PORT, USERNAME, PASSWORD, SENSOR_TOPIC


class CampusMQTTSync:

    def __init__(self, campus):

        self.campus = campus
        self.connected = False

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2
        )

        self.client.username_pw_set(
            USERNAME,
            PASSWORD
        )

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.client.connect_async(
            BROKER,
            PORT,
            60
        )

        self.client.loop_start()

    def on_connect(
        self, client, userdata, flags, reason_code, properties
    ):

        if reason_code.is_failure:
            print("❌ MQTT connection failed:", reason_code)
            return

        self.connected = True

        topic = f"{SENSOR_TOPIC}/+/state"

        client.subscribe(topic, qos=1)

        print(f"✅ Interface listening to {topic}")

    def on_disconnect(
        self, client, userdata, flags, reason_code, properties
    ):

        self.connected = False
        print("⚠️ Interface disconnected from MQTT")

    def on_message(self, client, userdata, msg):

        try:
            parts = msg.topic.split("/")

            if (
                len(parts) != 4
                or parts[0] != "campus"
                or parts[1] != "rooms"
                or parts[3] != "state"
            ):
                return

            room_id = parts[2]

            state = json.loads(
                msg.payload.decode("utf-8")
            )

            if not isinstance(state, dict):
                return

            if state.get("room_id", room_id) != room_id:
                return

            room = self.campus.get_room(room_id)

            if room is None:
                return

            # Sensores ambientais
            for field in (
                "temperature",
                "humidity",
                "co2",
                "target_temperature",
            ):

                value = state.get(field)

                if (
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                ):
                    setattr(room, field, float(value))

            # Ocupação
            people = state.get("people_count")

            if (
                type(people) is int
                and 0 <= people <= room.capacity
            ):
                room.people_count = people

            # Ar condicionado
            mode = state.get("ac_mode")

            if mode in ("ac_off", "ac_cool", "ac_heat"):
                room.ac_mode = mode
                room.ac_on = mode != "ac_off"

            # Luzes
            lights = state.get("lights_on")

            if type(lights) is bool:
                room.lights_on = lights

            # Porta
            locked = state.get("door_locked")

            if type(locked) is bool:
                room.door_locked = locked
                room.door_closed = locked

            # Alarmes
            alarm = state.get("alarm_on")

            if type(alarm) is bool:
                room.alarm_on = alarm
                room.alarm_reason = state.get("alarm_reason")

            room.update_timestamp()

            print(
                f"📥 {room_id}: "
                f"{room.temperature:.1f} °C"
            )

        except (ValueError, TypeError, UnicodeDecodeError) as error:

            print("❌ Invalid room state:", error)

    def send_command(self, room_id, command, params):

        if not self.connected:
            print("❌ Cannot send command: MQTT disconnected")
            return False

        topic = f"campus/rooms/{room_id}/commands"

        payload = {
            "room_id": room_id,
            "command": command,
            "params": params,
        }

        result = self.client.publish(
            topic,
            json.dumps(payload),
            qos=1,
            retain=False
        )

        return result.rc == mqtt.MQTT_ERR_SUCCESS