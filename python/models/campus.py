from models.classroom import Classroom


class Campus:
    def __init__(self):
        self.rooms: dict[str, Classroom] = {}

    # ------------------------
    # ROOM MANAGEMENT
    # ------------------------

    def add_room(self, room: Classroom):
        if room.room_id in self.rooms:
            raise ValueError(
                f"Room {room.room_id} already exists"
            )

        self.rooms[room.room_id] = room

    def get_room(self, room_id: str) -> Classroom | None:
        return self.rooms.get(room_id)

    def remove_room(self, room_id: str):
        if room_id not in self.rooms:
            raise ValueError(
                f"Room {room_id} does not exist"
            )

        del self.rooms[room_id]

    def get_all_rooms(self) -> list[Classroom]:
        return list(self.rooms.values())

    # ------------------------
    # SERIALIZATION
    # ------------------------

    def get_state(self) -> dict:
        return {
            room_id: room.get_state()
            for room_id, room in self.rooms.items()
        }

    # ------------------------
    # STATISTICS
    # ------------------------

    def total_people(self) -> int:
        return sum(
            room.people_count
            for room in self.rooms.values()
        )

    def total_capacity(self) -> int:
        return sum(
            room.capacity
            for room in self.rooms.values()
        )
