#!/bin/bash

# Script to restart Chrome with remote debugging enabled
# This preserves your session and allows Playwright to connect

echo "Closing Chrome gracefully..."
osascript -e 'quit app "Google Chrome"'

# Wait for Chrome to fully close
sleep 2

# Check if Chrome is still running
if pgrep -x "Google Chrome" > /dev/null; then
    echo "Chrome didn't close gracefully, force closing..."
    pkill -9 "Google Chrome"
    sleep 1
fi

echo "Starting Chrome with remote debugging on port 9222..."
open -a "Google Chrome" --args --remote-debugging-port=9222

echo "Chrome restarted with debugging enabled."
echo "Please navigate to the Routine Report page: https://cam.cammaster.org/v3/analysis/reporting/routine"
echo "Then run the capture script."
