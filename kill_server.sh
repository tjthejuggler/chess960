#!/bin/bash

# Kill Server Script for Chess960 Visualization
# This script kills any process using port 8080

PORT=8080

echo "🔍 Searching for processes using port $PORT..."

# Method 1: Try lsof (most reliable)
if command -v lsof &> /dev/null; then
    PIDS=$(lsof -ti :$PORT 2>/dev/null)
    if [ ! -z "$PIDS" ]; then
        echo "🎯 Found process(es) using port $PORT: $PIDS"
        for PID in $PIDS; do
            PROCESS_NAME=$(ps -p $PID -o comm= 2>/dev/null)
            echo "🔪 Killing process $PID ($PROCESS_NAME)..."
            kill -9 $PID 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "✅ Successfully killed process $PID"
            else
                echo "❌ Failed to kill process $PID (may require sudo)"
            fi
        done
        echo "🏁 Done!"
        exit 0
    fi
fi

# Method 2: Try fuser
if command -v fuser &> /dev/null; then
    PIDS=$(fuser $PORT/tcp 2>/dev/null)
    if [ ! -z "$PIDS" ]; then
        echo "🎯 Found process(es) using port $PORT: $PIDS"
        fuser -k $PORT/tcp 2>/dev/null
        echo "✅ Killed processes using port $PORT"
        echo "🏁 Done!"
        exit 0
    fi
fi

# Method 3: Try netstat/ss and manual kill
if command -v netstat &> /dev/null; then
    PID=$(netstat -tulpn 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1)
elif command -v ss &> /dev/null; then
    PID=$(ss -tulpn 2>/dev/null | grep ":$PORT " | awk '{print $7}' | grep -oP '\d+' | head -1)
fi

if [ ! -z "$PID" ]; then
    echo "🎯 Found process using port $PORT: $PID"
    PROCESS_NAME=$(ps -p $PID -o comm= 2>/dev/null)
    echo "🔪 Killing process $PID ($PROCESS_NAME)..."
    kill -9 $PID 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Successfully killed process $PID"
    else
        echo "❌ Failed to kill process $PID (may require sudo)"
    fi
    echo "🏁 Done!"
    exit 0
fi

# No process found
echo "✅ No process found using port $PORT"
echo "💡 The port may be in TIME_WAIT state. Wait a few seconds and try again."
exit 0