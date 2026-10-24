import math


VALID_AC_MODES = {"ac_cool", "ac_heat", "ac_off"}


def execute_command(campus, message):
    """
    Validate and execute a command received from Coreflux.

    Expected JSON format:

    {
        "command": "SET_AC",
        "room_id": "B101",
        "params": {
            "mode": "ac_cool",
            "temperature": 19
        }
    }

    Returns:
        True  -> Command executed successfully
        False -> Command rejected
    """

    try:
        # ----------------------------------
        # VALIDATE MESSAGE STRUCTURE
        # ----------------------------------

        if not isinstance(message, dict):
            raise ValueError("Command must be a JSON object")

        if set(message) - {"command", "room_id", "params", "command_id"}:
            raise ValueError("Unexpected command fields")

        command = message.get("command")
        room_id = message.get("room_id")
        params = message.get("params")

        if not isinstance(command, str):
            raise ValueError("Missing or invalid command")

        if not isinstance(room_id, str):
            raise ValueError("Missing or invalid room_id")

        if not isinstance(params, dict):
            raise ValueError("params must be a JSON object")

        if "command_id" in message and not isinstance(message["command_id"], str):
            raise ValueError("command_id must be a string")

        # ----------------------------------
        # FIND CLASSROOM
        # ----------------------------------

        room = campus.get_room(room_id)

        if room is None:
            raise ValueError(f"Unknown classroom: {room_id}")

        # ----------------------------------
        # SET_AC
        # ----------------------------------

        if command == "SET_AC":

            if set(params) - {"mode", "temperature"}:
                raise ValueError("Unexpected SET_AC parameters")

            mode = params.get("mode")

            if not isinstance(mode, str) or mode not in VALID_AC_MODES:
                raise ValueError(
                    "AC mode must be ac_cool, ac_heat or ac_off"
                )

            # Validate temperature before changing anything
            if "temperature" in params:
                temperature = params["temperature"]

                if (
                    type(temperature) not in (int, float)
                    or not math.isfinite(temperature)
                    or not 16 <= temperature <= 30
                ):
                    raise ValueError(
                        "Target temperature must be between 16 and 30°C"
                    )

            # Apply changes only after validation
            if "temperature" in params:
                room.set_target_temperature(params["temperature"])

            room.set_ac(mode)

        # ----------------------------------
        # SET_LIGHTS
        # ----------------------------------

        elif command == "SET_LIGHTS":

            if set(params) != {"enabled"}:
                raise ValueError("SET_LIGHTS requires only 'enabled'")

            enabled = params["enabled"]

            if type(enabled) is not bool:
                raise ValueError("enabled must be a boolean")

            room.set_lights(enabled)

        # ----------------------------------
        # SET_DOOR
        # ----------------------------------

        elif command == "SET_DOOR":

            if set(params) != {"locked"}:
                raise ValueError("SET_DOOR requires only 'locked'")

            locked = params["locked"]

            if type(locked) is not bool:
                raise ValueError("locked must be a boolean")

            room.set_door_lock(locked)

        # ----------------------------------
        # SET_ALARM
        # ----------------------------------

        elif command == "SET_ALARM":

            if set(params) - {"enabled", "reason"}:
                raise ValueError("Unexpected SET_ALARM parameters")

            enabled = params.get("enabled")
            reason = params.get("reason")

            if type(enabled) is not bool:
                raise ValueError("enabled must be a boolean")

            if reason is not None and not isinstance(reason, str):
                raise ValueError("reason must be a string")

            room.set_alarm(enabled, reason)

        # ----------------------------------
        # SET_OCCUPANCY
        # ----------------------------------

        elif command == "SET_OCCUPANCY":

            if set(params) != {"count"}:
                raise ValueError("SET_OCCUPANCY requires only 'count'")

            count = params["count"]

            if type(count) is not int:
                raise ValueError("count must be an integer")

            if not 0 <= count <= room.capacity:
                raise ValueError(
                    f"Occupancy must be between 0 and {room.capacity}"
                )

            room.set_people(count)

        # ----------------------------------
        # SET_ROOM_VALUES
        # ----------------------------------

        elif command == "SET_ROOM_VALUES":

            required = {
                "count",
                "temperature",
                "humidity",
                "co2",
            }

            if set(params) != required:
                raise ValueError("Invalid room values parameters")

            count = params["count"]
            temperature = params["temperature"]
            humidity = params["humidity"]
            co2 = params["co2"]

            if type(count) is not int or not 0 <= count <= room.capacity:
                raise ValueError("Invalid occupancy")

            for value in (temperature, humidity, co2):
                if type(value) not in (int, float) or not math.isfinite(value):
                    raise ValueError("Sensor values must be finite numbers")

            if not -10 <= temperature <= 50:
                raise ValueError("Temperature must be between -10 and 50°C")

            if not 0 <= humidity <= 100:
                raise ValueError("Humidity must be between 0 and 100%")

            if not 0 <= co2 <= 10000:
                raise ValueError("CO2 must be between 0 and 10000 ppm")

            room.set_people(count)
            room.set_temperature(temperature)
            room.set_humidity(humidity)
            room.set_co2(co2)

            room.manual_mode = True
            room.update_timestamp()

        # ----------------------------------
        # RETURN TO AUTOMATIC SIMULATION
        # ----------------------------------

        elif command == "SET_ROOM_AUTO":

            if params:
                raise ValueError("SET_ROOM_AUTO requires empty params")

            room.manual_mode = False
            room.update_timestamp()

        # ----------------------------------
        # UNKNOWN COMMAND
        # ----------------------------------

        else:
            raise ValueError(f"Unknown command: {command}")

        print(
            f"✅ Command executed: {command} "
            f"| Room: {room_id} "
            f"| Params: {params}",
            flush=True
        )

        return True

    except (ValueError, TypeError) as error:

        print(f"❌ Command rejected: {error}", flush=True)

        return False