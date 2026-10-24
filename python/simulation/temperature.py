def update_temperature(room):
    """Simple temperature simulation based on AC mode."""

    current = room.temperature

    if room.ac_mode == "ac_cool":
        # Cooling: decrease temperature
        new_temperature = max(16.0, current - 0.3)

    elif room.ac_mode == "ac_heat":
        # Heating: increase temperature
        new_temperature = min(35.0, current + 0.3)

    else:
        # AC OFF: slowly approach 25°C
        if current < 25.0:
            new_temperature = min(25.0, current + 0.05)

        elif current > 25.0:
            new_temperature = max(25.0, current - 0.05)

        else:
            new_temperature = current

    # Update classroom model
    new_temperature = round(new_temperature, 2)

    if new_temperature != room.temperature:
        room.temperature = new_temperature
        room.update_timestamp()