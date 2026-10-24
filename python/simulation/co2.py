def update_co2(room):
    """Simulate CO2 concentration in ppm."""

    outdoor_co2 = 420.0

    # Simplified CO2 production by occupants
    co2_production = room.people_count * 2.5

    # Natural ventilation removes accumulated CO2
    ventilation_rate = 0.04

    new_co2 = (
        room.co2
        + co2_production
        - (room.co2 - outdoor_co2) * ventilation_rate
    )

    new_co2 = max(outdoor_co2, min(5000.0, new_co2))
    new_co2 = round(new_co2, 2)

    if new_co2 != room.co2:
        room.co2 = new_co2
        room.update_timestamp()
    