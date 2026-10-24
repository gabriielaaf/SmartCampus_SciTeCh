import random


def update_occupancy(room):
    """Simulate people entering or leaving a classroom."""

    # 20% chance of a change each simulation cycle
    if random.random() > 0.20:
        return

    change = random.randint(-3, 3)

    new_count = room.people_count + change
    new_count = max(0, min(room.capacity, new_count))

    if new_count != room.people_count:
        room.set_people(new_count)
