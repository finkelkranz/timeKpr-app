#!/bin/bash
# Script to run the timekpr-app server with process management

# Change to the project directory
cd "$(dirname "$0")"

# Check if server is already running
PID=$(pgrep -f "python.*timekpr_app.api.main" | head -n 1)

if [ ! -z "$PID" ]; then
  echo "⚠️  Server is already running (PID: $PID)"
  read -p "Do you want to stop and restart it? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping existing server..."
    kill $PID
    sleep 1
  else
    echo "Exiting without starting new server."
    exit 0
  fi
fi

# Activate virtual environment
source .venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH=src

echo "Starting timeKpr server..."
# Run the server
python -c "from timekpr_app.api.main import cli; cli()"