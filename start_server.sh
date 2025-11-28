#!/bin/bash
# Start Server Script for Chess960 Visualization
# This script starts a simple HTTP server on port 8080

PORT=8080

echo "Starting HTTP server on port $PORT..."
echo "Open your browser to: http://localhost:$PORT/chess960_visualization.html"
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m http.server $PORT