# Coreflux Local Connection
BROKER = "localhost"
PORT = 1883

USERNAME = "root"
PASSWORD = "coreflux"

# MQTT Topics

# Base topic for publishing classroom states
SENSOR_TOPIC = "campus/rooms"

# Subscribe to commands for ALL classrooms
COMMAND_TOPIC = "campus/rooms/+/commands"