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
    ac_mode: str = "ac_off"
    lights_on: bool = False
    door_locked: bool = False

    # Alarm
    alarm_on: bool = False
    alarm_reason: str | None = None

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

    def set_ac(self, mode: str):
        valid_modes = {"ac_cool", "ac_heat", "ac_off"}

        if mode not in valid_modes:
            raise ValueError(
                f"Invalid AC mode: {mode}. "
                f"Expected one of: {', '.join(sorted(valid_modes))}"
            )

        if self.ac_mode != mode:
            self.ac_mode = mode
            self.update_timestamp()

    def set_lights(self, enabled: bool):
        self.lights_on = enabled
        self.update_timestamp()

    def set_door_lock(self, enabled: bool):
        self.door_locked = enabled
        self.update_timestamp()

    # ------------------------
    # ALARM
    # ------------------------

    def set_alarm(self, enabled: bool, reason: str | None = None):
        self.alarm_on = enabled
        self.alarm_reason = (reason or "Unknown alarm") if enabled else None
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
            "ac_mode": self.ac_mode,
            "lights_on": self.lights_on,
            "door_locked": self.door_locked,
            "alarm_on": self.alarm_on,
            "alarm_reason": self.alarm_reason,
            "target_temperature": self.target_temperature,
            "last_updated": self.last_updated,
        }