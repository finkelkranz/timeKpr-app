#!/bin/bash
# Script to run the timekpr-app frontend with process management

cd "$(dirname "$0")"

FRONTEND_DIR="frontend"
PID_FILE=".frontend.pid"

PID=$(pgrep -f "vite" | head -n 1)

if [ ! -z "$PID" ]; then
  echo "Frontend is already running (PID: $PID)"
  read -p "Stop and restart? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    kill $PID
    sleep 1
  else
    exit 0
  fi
fi

cd "$FRONTEND_DIR"
echo "Starting timeKpr frontend on http://localhost:5173..."
npm run dev