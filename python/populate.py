from models.campus import Campus
from models.classroom import Classroom


def create_campus() -> Campus:
    campus = Campus()

    rooms = [
        Classroom(
            room_id="B101",
            capacity=30,
            people_count=22,
            temperature=23.5,
            humidity=48.0,
            co2=780,
            ac_on=True,
            lights_on=True,
            door_locked=False
        ),

        Classroom(
            room_id="B102",
            capacity=25,
            people_count=18,
            temperature=26.0,
            humidity=53.0,
            co2=1050,
            ac_on=False,
            lights_on=True,
            door_locked=False
        ),

        Classroom(
            room_id="B103",
            capacity=40,
            people_count=0,
            temperature=21.0,
            humidity=45.0,
            co2=420,
            ac_on=False,
            lights_on=False,
            door_locked=True
        ),

        Classroom(
            room_id="B104",
            capacity=20,
            people_count=15,
            temperature=24.5,
            humidity=52.0,
            co2=940,
            ac_on=True,
            lights_on=True,
            door_locked=False
        ),

        Classroom(
            room_id="B105",
            capacity=35,
            people_count=8,
            temperature=22.0,
            humidity=46.0,
            co2=580,
            ac_on=False,
            lights_on=True,
            door_locked=False
        ),

        Classroom(
            room_id="B106",
            capacity=30,
            people_count=0,
            temperature=28.0,
            humidity=59.0,
            co2=410,
            ac_on=False,
            lights_on=False,
            door_locked=True
        )
    ]

    for room in rooms:
        campus.add_room(room)

    return campus


if __name__ == "__main__":
    campus = create_campus()

    print(f"Número de salas: {len(campus.get_all_rooms())}")

    for room in campus.get_all_rooms():
        print(room.get_state())