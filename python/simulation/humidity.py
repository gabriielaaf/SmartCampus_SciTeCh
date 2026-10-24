import random


def update_humidity(room):
    """Simulate classroom humidity based on occupancy and AC mode."""

    baseline_humidity = 45.0

    # More occupants can increase humidity
    people_effect = room.people_count * 0.15

    target = baseline_humidity + people_effect

    # AC influence on humidity
    if room.ac_mode == "ac_cool":
        target -= 5.0

    elif room.ac_mode == "ac_heat":
        target -= 1.0

    # Small random environmental variation
    target += random.uniform(-0.5, 0.5)

    # Gradually approach target humidity
    new_humidity = room.humidity + (
        target - room.humidity
    ) * 0.08

    # Keep humidity within realistic simulation limits
    new_humidity = max(20.0, min(80.0, new_humidity))
    new_humidity = round(new_humidity, 2)

    if new_humidity != room.humidity:
        room.humidity = new_humidity
        room.update_timestamp()