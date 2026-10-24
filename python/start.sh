#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "🚀 Starting Coreflux Smart Campus..."

./.venv/bin/python -u main.py