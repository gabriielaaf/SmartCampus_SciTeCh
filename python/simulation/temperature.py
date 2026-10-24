def update_temperature(room):
    """Simulate room temperature."""

    ambient_temperature = 23.0

    # Occupants contribute to room heating
    people_heat = room.people_count * 0.04

    if room.ac_on:
        # Move towards the desired AC temperature
        target = room.target_temperature
        rate = 0.15
    else:
        # Move towards ambient temperature + occupant heat
        target = ambient_temperature + people_heat
        rate = 0.05

    new_temperature = room.temperature + (
        target - room.temperature
    ) * rate

    new_temperature = round(new_temperature, 2)

    if new_temperature != room.temperature:
        room.temperature = new_temperature
        room.update_timestamp()