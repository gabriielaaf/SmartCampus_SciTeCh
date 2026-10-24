from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Classroom:
    # Identification
    room_id: str
    capacity: int

    # Environmental sensors
    temperature: float = 22.0
    humidity: float = 50.0
    co2: float = 400.0

    # Occupancy
    people_count: int = 0

    # Actuators
    ac_on: bool = False
    lights_on: bool = False
    door_locked: bool = False

    # Configuration
    target_temperature: float = 22.0

    # Metadata
    last_updated: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def update_timestamp(self):
        self.last_updated = datetime.now(timezone.utc).isoformat()

    # ------------------------
    # OCCUPANCY
    # ------------------------

    def set_people(self, count: int):
        if not 0 <= count <= self.capacity:
            raise ValueError(
                f"Occupancy must be between 0 and {self.capacity}"
            )

        self.people_count = count
        self.update_timestamp()

    # ------------------------
    # ACTUATORS
    # ------------------------

    def set_ac(self, enabled: bool):
        self.ac_on = enabled
        self.update_timestamp()

    def set_lights(self, enabled: bool):
        self.lights_on = enabled
        self.update_timestamp()

    def set_door_lock(self, enabled: bool):
        self.door_locked = enabled
        self.update_timestamp()

    # ------------------------
    # CONFIGURATION
    # ------------------------

    def set_target_temperature(self, temperature: float):
        if not 16 <= temperature <= 30:
            raise ValueError(
                "Target temperature must be between 16 and 30°C"
            )

        self.target_temperature = temperature
        self.update_timestamp()

    # ------------------------
    # SERIALIZATION
    # ------------------------

    def get_state(self) -> dict:
        return {
            "room_id": self.room_id,
            "capacity": self.capacity,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "co2": self.co2,
            "people_count": self.people_count,
            "ac_on": self.ac_on,
            "lights_on": self.lights_on,
            "door_locked": self.door_locked,
            "target_temperature": self.target_temperature,
            "last_updated": self.last_updated,
        }
