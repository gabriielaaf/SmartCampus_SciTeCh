#!/bin/bash

set -e

cd "$(dirname "$0")"

PYTHON="$(pwd)/.venv/bin/python"

echo "🚀 Starting Coreflux Smart Building..."

# Start subscriber
"$PYTHON" -u subscriber.py &
SUBSCRIBER_PID=$!

cleanup() {
    echo ""
    echo "🛑 Stopping Coreflux processes..."

    kill "$SUBSCRIBER_PID" 2>/dev/null || true
    wait "$SUBSCRIBER_PID" 2>/dev/null || true
}

trap cleanup EXIT

# Start publisher
"$PYTHON" -u publisher.py
