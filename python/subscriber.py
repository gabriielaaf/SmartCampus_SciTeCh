import json

from config import COMMAND_TOPIC


class MQTTSubscriber:

    def __init__(self, client, command_queue):
        self.client = client
        self.command_queue = command_queue

        self.client.on_message = self.on_message

    def subscribe(self):
        self.client.subscribe(COMMAND_TOPIC, qos=1)

        print(f"📡 Listening to: {COMMAND_TOPIC}")

    def on_message(self, client, userdata, msg):
        try:
            # Expected topic: campus/rooms/B101/commands
            parts = msg.topic.split("/")

            if len(parts) != 4 or parts[3] != "commands":
                print(f"❌ Unexpected topic: {msg.topic}")
                return

            room_id = parts[2]

            command = json.loads(msg.payload.decode())

            if not isinstance(command, dict):
                print("❌ Command must be a JSON object")
                return

            self.command_queue.put({
                "room_id": room_id,
                "device": command.get("device"),
                "value": command.get("value"),
                "reason": command.get("reason")
            })

            print(f"📩 Received command for {room_id}: {command}")

        except (ValueError, UnicodeDecodeError) as error:
            print(f"❌ Invalid MQTT message: {error}")
            