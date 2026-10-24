from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Classroom:
    room_id: str
    capacity: int

    # Sensores ambientais
    temperature: float = 22.0
    humidity: float = 50.0
    co2: float = 400.0

    # Ocupação
    people_count: int = 0

    # Atuadores existentes
    ac_on: bool = False
    lights_on: bool = False
    door_locked: bool = False

    # Configuração
    target_temperature: float = 22.0

    # Novos atributos
    ac_mode: str = "off"     # off, cool, heat
    door_closed: bool = False

    last_updated: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def __post_init__(self):

        if self.capacity < 0:
            raise ValueError("Capacity cannot be negative")

        if not 0 <= self.people_count <= self.capacity:
            raise ValueError("Occupancy exceeds room capacity")

        if self.ac_mode not in ("off", "cool", "heat"):
            raise ValueError(
                "AC mode must be off, cool or heat"
            )

        # Compatibilidade com objetos antigos
        if self.ac_on and self.ac_mode == "off":
            self.ac_mode = "cool"

        if self.ac_mode != "off":
            self.ac_on = True

        # Uma porta trancada tem de estar fechada
        self.door_closed = self.door_locked

    def update_timestamp(self):
        self.last_updated = datetime.now(
            timezone.utc
        ).isoformat()

    # ========================================================
    # OCCUPANCY
    # ========================================================

    def set_people(self, count: int):

        if not 0 <= count <= self.capacity:
            raise ValueError(
                f"Occupancy must be between 0 and {self.capacity}"
            )

        self.people_count = count
        self.update_timestamp()

    # ========================================================
    # SENSORS
    # ========================================================

    def set_temperature(self, temperature: float):
        self.temperature = float(temperature)
        self.update_timestamp()

    def set_humidity(self, humidity: float):

        if not 0 <= humidity <= 100:
            raise ValueError(
                "Humidity must be between 0 and 100%"
            )

        self.humidity = float(humidity)
        self.update_timestamp()

    def set_co2(self, co2: float):

        if co2 < 0:
            raise ValueError("CO2 cannot be negative")

        self.co2 = float(co2)
        self.update_timestamp()

    # ========================================================
    # AIR CONDITIONING
    # ========================================================

    def set_ac(self, enabled: bool):
        """
        Método antigo, mantido para compatibilidade.
        """

        self.set_ac_mode(
            "cool" if enabled and self.ac_mode == "off"
            else self.ac_mode if enabled
            else "off"
        )

    def set_ac_mode(self, mode: str):
        """
        Define o modo de funcionamento:
        - off: desligado
        - cool: frio
        - heat: quente
        """

        if mode not in ("off", "cool", "heat"):
            raise ValueError(
                "AC mode must be off, cool or heat"
            )

        self.ac_mode = mode
        self.ac_on = mode != "off"

        self.update_timestamp()

    # ========================================================
    # LIGHTS
    # ========================================================

    def set_lights(self, enabled: bool):

        self.lights_on = bool(enabled)
        self.update_timestamp()

    # ========================================================
    # DOOR
    # ========================================================

    def set_door_closed(self, closed: bool):
        self.set_door_lock(closed)

    def set_door_lock(self, enabled: bool):
        self.door_locked = bool(enabled)
        self.door_closed = self.door_locked
        self.update_timestamp()
       
    # ========================================================
    # CONFIGURATION
    # ========================================================

    def set_target_temperature(self, temperature: float):

        if not 16 <= temperature <= 30:
            raise ValueError(
                "Target temperature must be between 16 and 30°C"
            )

        self.target_temperature = temperature
        self.update_timestamp()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def get_state(self) -> dict:

        return {
            "room_id": self.room_id,
            "capacity": self.capacity,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "co2": self.co2,
            "people_count": self.people_count,

            "ac_on": self.ac_on,
            "ac_mode": (
                self.ac_mode if self.ac_on else "off"
            ),

            "lights_on": self.lights_on,

            "door_locked": self.door_locked,
            "door_closed": self.door_closed,

            "target_temperature": self.target_temperature,
            "last_updated": self.last_updated,
        }