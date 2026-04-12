#!/bin/bash
# Simple script to run the timekpr-app server

# Change to the project directory
cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH=src

# Run the server
python -c "from timekpr_app.api.main import cli; cli()"