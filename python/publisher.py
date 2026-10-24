import json
import paho.mqtt.client as mqtt

from config import SENSOR_TOPIC


class MQTTPublisher:

    def __init__(self, client, campus):
        self.client = client
        self.campus = campus
        self.last_published = {}

    def reset(self):
        """
        Force all classrooms to be published again.
        Useful after MQTT reconnects.
        """
        self.last_published.clear()

    def publish_changed_rooms(self):
        """
        Publish only classrooms whose state changed.
        """

        if not self.client.is_connected():
            return

        for room in self.campus.get_all_rooms():

            current_state = room.get_state()

            # Ignore timestamp when detecting changes
            comparable_state = {
                key: value
                for key, value in current_state.items()
                if key != "last_updated"
            }

            previous_state = self.last_published.get(room.room_id)

            if comparable_state == previous_state:
                continue

            topic = f"{SENSOR_TOPIC}/{room.room_id}/state"
            message = json.dumps(current_state)

            result = self.client.publish(
                topic,
                message,
                qos=1,
                retain=True
            )

            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"❌ Failed to publish {room.room_id}")
                continue

            try:
                result.wait_for_publish(timeout=5)
            except (RuntimeError, ValueError) as error:
                print(f"❌ Publish error for {room.room_id}: {error}")
                continue

            if not result.is_published():
                print(f"⚠️ Publication not confirmed: {room.room_id}")
                continue

            self.last_published[room.room_id] = comparable_state.copy()

            print(
                f"📤 Published {room.room_id}: {message}",
                flush=True
            )
