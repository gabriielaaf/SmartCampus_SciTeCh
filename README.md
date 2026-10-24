# SmartCampus — ScyTech Hackathon

A Python smart-campus digital twin with **six simulated classrooms (B101–B106)**. The backend simulates occupancy, temperature, humidity and CO₂, publishes classroom state over MQTT, and accepts commands for classroom devices. A **Streamlit** interface displays live classroom state and sends commands back to the backend.

## How it works

```text
Streamlit interface ── MQTT commands ──► MQTT broker (Coreflux)
        ▲                                     │
        │                                     ▼
        └──── MQTT room states ──────── Python backend
                                         ├─ Classroom models
                                         ├─ Sensor simulation
                                         └─ Command execution
```

The interface and backend run as **two separate processes**. They must connect to the **same MQTT broker**.

## 1. Prerequisites (Ubuntu / Linux)

- Git
- Python 3 with `venv` and `pip`
- **Coreflux installed and running, with the required Coreflux deployments started**
- An accessible **MQTT broker** (for example, the local Coreflux MQTT broker)
- Optional: Mosquitto command-line clients to test MQTT

Install the required system packages:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip mosquitto-clients
```

> **Important:** Start the necessary **deployments in Coreflux** before running the SmartCampus Python applications. Installing `mosquitto-clients` provides testing commands only; it does **not** start Coreflux or an MQTT broker.

## 2. Clone the repository

```bash
git clone https://github.com/paipaga/ScyTech-Hackaton.git
cd ScyTech-Hackaton/python
```

All following commands assume you are in the `python/` directory.

## 3. Create the Python environment

The backend's `start.sh` expects the virtual environment at **`python/.venv/`**.

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install "paho-mqtt>=2,<3" streamlit
```

If the repository later includes a `requirements.txt`, prefer installing its pinned dependencies:

```bash
# Only if requirements.txt exists:
./.venv/bin/python -m pip install -r requirements.txt
```

The backend uses `paho-mqtt` callback API version 2. Streamlit powers the interface.

## 4. Configure MQTT

Edit `python/config.py`:

```python
# MQTT broker reachable from the machine running Python
BROKER = "localhost"
PORT = 1883

# Replace with the credentials configured on your broker
USERNAME = "<mqtt-username>"
PASSWORD = "<mqtt-password>"

SENSOR_TOPIC = "campus/rooms"
COMMAND_TOPIC = "campus/rooms/+/commands"
```

- Use `localhost` **only** if the MQTT broker is reachable on the same machine.
- The backend and interface both read this config and must connect to the same broker as Coreflux.
- The `+` wildcard means “commands for any classroom.”
- Do not commit real broker passwords or access tokens to Git.

Check that the broker is available and your credentials work:

```bash
mosquitto_sub -h localhost -p 1883 -u '<mqtt-username>' -P '<mqtt-password>' \
  -t 'campus/rooms/+/state' -v
```

Leave this subscription open while starting the backend in another terminal. If your broker is remote, change `-h` and `-p` accordingly.

## 5. Fix the interface launcher for the shared environment

**Important:** At the time this guide was written, the repository's `python/interface.sh` tries to use `./interface/.venv/bin/python`, whereas `start.sh` uses `./.venv/bin/python`. If you created only the shared `.venv` in Step 3, edit `python/interface.sh` to use the same interpreter:

```bash
#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "🖥️ Starting SmartCampus Interface..."
./.venv/bin/python -m streamlit run interface/app.py
```

You can overwrite the file with:

```bash
cat > interface.sh <<'SH'
#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "🖥️ Starting SmartCampus Interface..."
./.venv/bin/python -m streamlit run interface/app.py
SH
chmod +x interface.sh start.sh
```

No separate `interface/.venv` is needed.

## 6. Start Coreflux deployments and run the application

### First — Start the Coreflux deployments (required)

1. Open **Coreflux** and connect to your SmartCampus project/environment.
2. Locate the project's **Deployments** section.
3. **Run/start the required deployments** for your SmartCampus project, and confirm they are active. These deployments must be running for the Coreflux-side automation/integration to work.
4. Make sure the MQTT broker used by Coreflux is available and matches the host, port, and credentials in `python/config.py`.

> **Do not skip this step.** The Python scripts do **not** automatically run Coreflux deployments. The exact deployment names depend on your Coreflux project.

### Next — Start the Python applications

After the Coreflux deployments and broker are running, use **two terminals** from the `python/` folder:

### Terminal 1 — Backend / simulation

```bash
./start.sh
```

Expected connection messages:

```text
🚀 Smart Campus started!
✅ Connected to Coreflux!
📡 Listening to: campus/rooms/+/commands
```

The backend updates simulated values approximately every **2 seconds** and publishes updated room states.

### Terminal 2 — Streamlit interface

```bash
./interface.sh
```

Open the local URL shown by Streamlit (typically **http://localhost:8501**).

Keep both terminals running. Press **Ctrl+C** in each to stop them.

## 7. Test a real MQTT command

With the backend running, send the following in a third terminal. Substitute your actual broker credentials and host:

```bash
mosquitto_pub \
  -h localhost -p 1883 \
  -u '<mqtt-username>' -P '<mqtt-password>' \
  -t 'campus/rooms/B102/commands' \
  -m '{"command":"SET_AC","room_id":"B102","params":{"mode":"ac_heat","temperature":28}}'
```

In the backend terminal, look for:

```text
📩 Received command: ...
✅ Command executed: SET_AC | Room: B102 | ...
📤 Published B102: ...
```

The published B102 state should have `"ac_mode": "ac_heat"` and `"target_temperature": 28`. When its current temperature is below 28°C, the temperature simulation should gradually increase it.

Watch the state messages directly:

```bash
mosquitto_sub -h localhost -p 1883 \
  -u '<mqtt-username>' -P '<mqtt-password>' \
  -t 'campus/rooms/B102/state' -v
```

You can also turn the lights off:

```bash
mosquitto_pub -h localhost -p 1883 \
  -u '<mqtt-username>' -P '<mqtt-password>' \
  -t 'campus/rooms/B102/commands' \
  -m '{"command":"SET_LIGHTS","room_id":"B102","params":{"enabled":false}}'
```

### MQTT topics and payloads

| Purpose | Topic | Notes |
| --- | --- | --- |
| Backend publishes a classroom state | `campus/rooms/B102/state` | JSON state; retained by publisher |
| Backend receives classroom commands | `campus/rooms/B102/commands` | JSON command; do not retain |
| Backend listens to all commands | `campus/rooms/+/commands` | MQTT wildcard subscription |
| Interface listens to all states | `campus/rooms/+/state` | MQTT wildcard subscription |

Supported commands in `commands.py`:

| Command | Example `params` |
| --- | --- |
| `SET_AC` | `{"mode":"ac_cool","temperature":19}` (`temperature` optional) |
| `SET_LIGHTS` | `{"enabled":true}` |
| `SET_DOOR` | `{"locked":true}` |
| `SET_ALARM` | `{"enabled":true,"reason":"CO2 high"}` |
| `SET_OCCUPANCY` | `{"count":20}` |

The JSON `room_id` must match the classroom ID in the MQTT topic.

## 8. Troubleshooting

**`./start.sh: ./.venv/bin/python: No such file or directory`**

You are missing `python/.venv`. Run Step 3 from the `python/` directory.

**`./interface.sh: ./interface/.venv/bin/python: No such file or directory`**

Your launcher still references the old interface-specific environment. Apply Step 5.

**`ModuleNotFoundError: No module named 'paho'` or `'streamlit'`**

Install the packages into the *same* `.venv` you use to start the application (Step 3).

**`Connection refused` or no “Connected to Coreflux!” message**

Verify Coreflux is running, start the required Coreflux deployments, and check `config.py`, broker status, and network access. Note that an MQTT connection alone does not prove the Coreflux deployments are active.

**The interface changes visually, but the backend doesn't receive a command**

Ensure both processes are running and connected to the same broker. Check that messages are published on `campus/rooms/<ROOM_ID>/commands`. Compare the terminal's `📩 Received command` and `✅ Command executed` logs. A visual interface change alone does not prove that the backend updated its model.

**Backend state changes, but the interface remains stale**

Confirm that the interface logs `✅ Interface listening to campus/rooms/+/state` and that `mosquitto_sub` receives new state publications.

**AC heat/cool doesn't change the measured temperature**

The current temperature must be below the heating target for heating, or above the cooling target for cooling. Setting only `"mode"` preserves the current target; include `"temperature"` to change it.

## Project components

- `python/main.py` — application loop, MQTT connection and command queue
- `python/commands.py` — validates commands and updates classrooms
- `python/subscriber.py` — receives MQTT commands
- `python/publisher.py` — publishes room states
- `python/generator.py` and `python/simulation/` — simulated sensor behavior
- `python/models/` and `python/populate.py` — classroom models and initial six-room campus
- `python/interface/app.py` — Streamlit app
- `python/interface/mqtt_sync.py` — interface MQTT state sync and command sending
- `python/config.py` — broker settings and MQTT topic constants

> Coreflux installation and the names of the required deployments are environment-specific. **Start the project deployments in Coreflux before running `./start.sh` and `./interface.sh`.** The Python scripts assume the MQTT broker is accessible and do not manage Coreflux deployments.