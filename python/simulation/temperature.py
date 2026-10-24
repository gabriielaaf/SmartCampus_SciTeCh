def update_temperature(room):
    """
    Simulate classroom temperature.

    - AC OFF: slowly approaches natural room temperature.
    - AC COOL: actively decreases temperature toward target.
    - AC HEAT: actively increases temperature toward target.
    """

    # ----------------------------------
    # CONFIGURATION
    # ----------------------------------

    AMBIENT_TEMPERATURE = 23.0

    AC_SPEED = 0.35
    NATURAL_SPEED = 0.04

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

        difference = natural_target - current

        change = max(
            -NATURAL_SPEED,
            min(NATURAL_SPEED, difference)
        )

        new_temperature = current + change

    # ----------------------------------
    # AC COOL
    # ----------------------------------

    elif room.ac_mode == "ac_cool":

        if current > target:
            new_temperature = max(
                target,
                current - AC_SPEED
            )
        else:
            new_temperature = current

    # ----------------------------------
    # AC HEAT
    # ----------------------------------

    elif room.ac_mode == "ac_heat":

        if current < target:
            new_temperature = min(
                target,
                current + AC_SPEED
            )
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