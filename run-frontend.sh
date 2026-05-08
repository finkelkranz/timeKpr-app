#!/bin/bash
# Script to run the timekpr-app frontend with process management

cd "$(dirname "$0")"

FRONTEND_DIR="frontend"
PID_FILE=".frontend.pid"

# Check if npm run dev is already running (works on any port)
PID=$(pgrep -f "npm run dev" | head -n 1)

if [ ! -z "$PID" ]; then
  echo "⚠️  Frontend is already running (PID: $PID)"
  read -p "Do you want to stop and restart it? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping existing frontend..."
    kill $PID
    sleep 1
  else
    echo "Exiting without starting new frontend."
    exit 0
  fi
fi

echo "Starting timeKpr frontend in background..."
# Run the development server in background with nohup
cd "$FRONTEND_DIR"
nohup npm run dev > "../../${PID_FILE}.log" 2>&1 &
NEW_PID=$!
echo $NEW_PID > "../${PID_FILE}"

echo "Frontend started with PID: $NEW_PID"
echo "To stop frontend (without closing browser), run: kill $NEW_PID"
echo "Frontend is running on http://localhost:5173"