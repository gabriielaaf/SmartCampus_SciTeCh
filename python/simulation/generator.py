from simulation.occupancy import update_occupancy
from simulation.temperature import update_temperature
from simulation.humidity import update_humidity
from simulation.co2 import update_co2


class Generator:

    def __init__(self, campus):
        self.campus = campus

    def update(self):
        """
        Update every classroom.

        Returns a list of classrooms whose sensor state changed.
        """

        changed_rooms = []

        for room in self.campus.get_all_rooms():

            # Save sensor values before simulation
            old_state = (
                room.people_count,
                room.temperature,
                room.humidity,
                room.co2,
            )

            # Run simulation modules
            update_occupancy(room)
            update_temperature(room)
            update_humidity(room)
            update_co2(room)

            # Compare sensor values after simulation
            new_state = (
                room.people_count,
                room.temperature,
                room.humidity,
                room.co2,
            )

            if new_state != old_state:
                changed_rooms.append(room)

        return changed_rooms
