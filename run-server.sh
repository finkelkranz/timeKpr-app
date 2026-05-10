#!/bin/bash
# Script to run the timekpr-app server with process management

cd "$(dirname "$0")"

PID=$(pgrep -f "timekpr_app.api.main" | head -n 1)

if [ ! -z "$PID" ]; then
  echo "Server is already running (PID: $PID)"
  read -p "Stop and restart? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    kill $PID
    sleep 1
  else
    exit 0
  fi
fi

SCRIPT_DIR=$(pwd)
export PYTHONPATH="$SCRIPT_DIR/src"

echo "Starting timeKpr server on http://localhost:8000..."
.venv/bin/python -m timekpr_app.api.main