def update_temperature(room):
    """
    Simulate classroom temperature.

    Rules:
    - AC OFF: temperature approaches ambient + occupant heat.
    - AC COOL: temperature decreases toward the target.
    - AC HEAT: temperature increases toward the target.
    - AC never moves temperature in the wrong direction.
    """

    # ----------------------------------
    # CONFIGURATION
    # ----------------------------------

    AMBIENT_TEMPERATURE = 23.0

    # Accelerated rates for the simulation
    NATURAL_RATE = 0.08
    AC_RATE = 0.30

    # ----------------------------------
    # TEMPERATURE VALUES
    # ----------------------------------

    current = room.temperature
    target = room.target_temperature

    people_heat = room.people_count * 0.04
    natural_target = AMBIENT_TEMPERATURE + people_heat

    # ----------------------------------
    # AC OFF
    # ----------------------------------

    if room.ac_mode == "ac_off":
        new_temperature = current + (
            natural_target - current
        ) * NATURAL_RATE

    # ----------------------------------
    # AC COOL
    # ----------------------------------

    elif room.ac_mode == "ac_cool":
        if current > target:
            new_temperature = current + (
                target - current
            ) * AC_RATE
        else:
            new_temperature = current

    # ----------------------------------
    # AC HEAT
    # ----------------------------------

    elif room.ac_mode == "ac_heat":
        if current < target:
            new_temperature = current + (
                target - current
            ) * AC_RATE
        else:
            new_temperature = current

    else:
        raise ValueError(f"Unknown AC mode: {room.ac_mode}")

    # ----------------------------------
    # UPDATE CLASSROOM
    # ----------------------------------

    new_temperature = round(new_temperature, 2)

    if new_temperature != room.temperature:
        room.temperature = new_temperature
        room.update_timestamp()