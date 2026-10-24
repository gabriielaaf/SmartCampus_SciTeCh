def update_temperature(room):
    """Simulate room temperature based on AC mode and occupancy."""

    ambient_temperature = 23.0

    # Occupants contribute to room heating
    people_heat = room.people_count * 0.04

    current = room.temperature
    target = room.target_temperature

    if room.ac_mode == "ac_cool":
        # Cooling can only decrease temperature
        if current > target:
            new_temperature = current + (target - current) * 0.15
        else:
            new_temperature = current

    elif room.ac_mode == "ac_heat":
        # Heating can only increase temperature
        if current < target:
            new_temperature = current + (target - current) * 0.15
        else:
            new_temperature = current

    else:
        # AC OFF: temperature approaches ambient + occupant heat
        natural_target = ambient_temperature + people_heat

        new_temperature = current + (
            natural_target - current
        ) * 0.05

    new_temperature = round(new_temperature, 2)

    if new_temperature != room.temperature:
        room.temperature = new_temperature
        room.update_timestamp()