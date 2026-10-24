from simulation.occupancy import update_occupancy
from simulation.temperature import update_temperature
from simulation.humidity import update_humidity
from simulation.co2 import update_co2


class Generator:
    def __init__(self, campus):
        self.campus = campus

    def update(self):
        changed_rooms = []

        for room in self.campus.get_all_rooms():

            # Não alterar salas em modo manual
            if room.manual_mode:
                # Em modo manual, só o AC pode alterar a temperatura
                if room.ac_mode != "ac_off":
                    update_temperature(room)

                continue

            old_state = (
                room.people_count,
                room.temperature,
                room.humidity,
                room.co2,
            )

            update_occupancy(room)
            update_temperature(room)
            update_humidity(room)
            update_co2(room)

            new_state = (
                room.people_count,
                room.temperature,
                room.humidity,
                room.co2,
            )

            if old_state != new_state:
                changed_rooms.append(room)

        return changed_rooms
