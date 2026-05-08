#!/bin/bash
# Script to stop the frontend server without closing the browser

PID_FILE=".frontend.pid"

if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "Stopping frontend (PID: $PID)..."
    kill "$PID"
    rm "$PID_FILE"
    echo "Frontend stopped."
  else
    echo "Frontend is not running (stale PID file)."
    rm "$PID_FILE"
  fi
else
  echo "No frontend PID file found. Searching for npm run dev..."
  PID=$(pgrep -f "npm run dev" | head -n 1)
  if [ ! -z "$PID" ]; then
    echo "Found frontend (PID: $PID). Stopping..."
    kill "$PID"
    echo "Frontend stopped."
  else
    echo "No frontend process found."
  fi
fi
