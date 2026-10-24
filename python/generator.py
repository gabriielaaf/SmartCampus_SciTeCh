import random


def generate_sensor_data():
    return {
        "temperature": round(random.uniform(18, 35), 2),
        "humidity": round(random.uniform(30, 80), 2),
        "co2": random.randint(400, 1800)
    }

