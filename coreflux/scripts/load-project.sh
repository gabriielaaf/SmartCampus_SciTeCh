set -u

HOST="${MQTT_HOST:-broker}"
PORT="${MQTT_PORT:-1883}"
USER="${MQTT_USER:-root}"
PASS="${MQTT_PASSWORD:-coreflux}"
PROJECT_PATH="${PROJECT_PATH:-/opt/smartuni}"
PROJECT_NAME="${PROJECT_NAME:-smartuni}"

reply() {
  payload=$1
  id=$2
  attempt=0
  while [ "$attempt" -lt 30 ]; do
    out="/tmp/cf-${id}.log"
    : >"$out"

    mosquitto_sub -h "$HOST" -p "$PORT" -u "$USER" -P "$PASS" \
      -i "load-project-sub" \
      -t '$SYS/Coreflux/Command/Output' -W 25 >"$out" 2>/dev/null &
    sub=$!
    sleep 2
    if mosquitto_pub -h "$HOST" -p "$PORT" -u "$USER" -P "$PASS" \
        -i "load-project-pub" \
        -t '$SYS/Coreflux/Command' -m "$payload" >/dev/null 2>&1; then
      n=0
      while [ "$n" -lt 20 ]; do
        if grep -q "$id" "$out" 2>/dev/null; then
          kill "$sub" 2>/dev/null || true
          wait "$sub" 2>/dev/null || true
          grep "$id" "$out" | tail -n 1
          return 0
        fi
        n=$((n + 1))
        sleep 1
      done
    fi
    kill "$sub" 2>/dev/null || true
    wait "$sub" 2>/dev/null || true
    attempt=$((attempt + 1))
    sleep 2
  done
  echo "No reply for: $payload" >&2
  return 1
}

ok() {
  printf '%s' "$1" | grep -Eq '"success"[[:space:]]*:[[:space:]]*true'
}

echo "Waiting for the broker at ${HOST}:${PORT}..."

add=$(reply "-addProject ${PROJECT_PATH} -requestId hackathon-add" hackathon-add) || exit 1
echo "$add"
if ok "$add"; then
  echo "Added project '${PROJECT_NAME}'."
elif printf '%s' "$add" | grep -q 'already exists'; then
  echo "Project '${PROJECT_NAME}' is already on the broker."
else
  echo "Could not add project '${PROJECT_NAME}'." >&2
  exit 1
fi

echo "Project '${PROJECT_NAME}' is ready in the LoT Editor."
