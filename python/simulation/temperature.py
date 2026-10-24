def update_temperature(room):
    """
    Simulate classroom temperature.

    Rules:
    - Occupants contribute to room heating.
    - AC OFF: temperature approaches ambient conditions.
    - AC COOL: temperature decreases toward the selected target.
    - AC HEAT: temperature increases toward the selected target.
    - Natural environmental effects continue while AC is operating.
    """

    # ----------------------------------
    # CONFIGURATION
    # ----------------------------------

    AMBIENT_TEMPERATURE = 23.0

    # Accelerated rates for the hackathon simulation
    NATURAL_RATE = 0.08
    AC_RATE = 0.30

    # ----------------------------------
    # CALCULATE NATURAL TEMPERATURE
    # ----------------------------------

    people_heat = room.people_count * 0.04

    natural_target = AMBIENT_TEMPERATURE + people_heat

    current = room.temperature
    target = room.target_temperature

    natural_change = (
        natural_target - current
    ) * NATURAL_RATE

    # ----------------------------------
    # AC OFF
    # ----------------------------------

    if room.ac_mode == "ac_off":

        new_temperature = current + natural_change

    # ----------------------------------
    # AC COOLING
    # ----------------------------------

    elif room.ac_mode == "ac_cool":

        if current > target:
            ac_change = (target - current) * AC_RATE

            # Cooling counteracts natural environmental heating
            new_temperature = current + min(
                0,
                natural_change + ac_change
            )

            # Do not cool below the target
            new_temperature = max(target, new_temperature)

        else:
            # Cooling cannot actively heat
            new_temperature = current + max(0, natural_change)
            new_temperature = min(target, new_temperature)

    # ----------------------------------
    # AC HEATING
    # ----------------------------------

    elif room.ac_mode == "ac_heat":

        if current < target:
            ac_change = (target - current) * AC_RATE

            # Heating counteracts natural environmental cooling
            new_temperature = current + max(
                0,
                natural_change + ac_change
            )

            # Do not heat above the target
            new_temperature = min(target, new_temperature)

        else:
            # Heating cannot actively cool
            new_temperature = current + min(0, natural_change)
            new_temperature = max(target, new_temperature)

    else:
        raise ValueError(f"Unknown AC mode: {room.ac_mode}")

    # ----------------------------------
    # UPDATE CLASSROOM
    # ----------------------------------

    new_temperature = round(new_temperature, 2)

    if new_temperature != room.temperature:
        room.temperature = new_temperature
        room.update_timestamp()