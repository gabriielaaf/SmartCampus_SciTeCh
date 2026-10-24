import json

from config import COMMAND_TOPIC


class MQTTSubscriber:

    def __init__(self, client, command_queue):
        self.client = client
        self.command_queue = command_queue

        self.client.on_message = self.on_message

    def subscribe(self):
        """
        Subscribe to commands for all classrooms.
        """
        result, message_id = self.client.subscribe(
            COMMAND_TOPIC,
            qos=1
        )

        if result == 0:
            print(f"📡 Listening to: {COMMAND_TOPIC}")
        else:
            print(f"❌ Failed to subscribe: {COMMAND_TOPIC}")

    def on_message(self, client, userdata, msg):
        """
        Receive a Coreflux command, validate its basic
        structure, and add it to the command queue.
        """

        try:
            # ----------------------------------
            # VALIDATE MQTT TOPIC
            # ----------------------------------

            # Expected: campus/rooms/B101/commands
            parts = msg.topic.split("/")

            if (
                len(parts) != 4
                or parts[0] != "campus"
                or parts[1] != "rooms"
                or not parts[2]
                or parts[3] != "commands"
            ):
                print(f"❌ Invalid MQTT topic: {msg.topic}")
                return

            topic_room_id = parts[2]

            # ----------------------------------
            # DECODE JSON
            # ----------------------------------

            command = json.loads(msg.payload.decode("utf-8"))

            if not isinstance(command, dict):
                print("❌ Command must be a JSON object")
                return

            # ----------------------------------
            # VALIDATE ROOM ID
            # ----------------------------------

            json_room_id = command.get("room_id")

            if not isinstance(json_room_id, str):
                print("❌ Missing or invalid room_id")
                return

            if json_room_id != topic_room_id:
                print(
                    f"❌ Room ID mismatch: "
                    f"topic={topic_room_id}, "
                    f"json={json_room_id}"
                )
                return

            # ----------------------------------
            # BASIC COMMAND VALIDATION
            # ----------------------------------

            if not isinstance(command.get("command"), str):
                print("❌ Missing or invalid command type")
                return

            if not isinstance(command.get("params"), dict):
                print("❌ Missing or invalid params")
                return

            # ----------------------------------
            # ADD COMMAND TO QUEUE
            # ----------------------------------

            self.command_queue.put(command)

            print(
                f"📩 Received command: {command}",
                flush=True
            )

        except (ValueError, UnicodeDecodeError) as error:
            print(
                f"❌ Invalid MQTT message: {error}",
                flush=True
            )
