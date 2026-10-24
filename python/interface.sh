#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "🖥️ Starting SmartCampus Interface..."

./interface/.venv/bin/python -m streamlit run interface/app.py