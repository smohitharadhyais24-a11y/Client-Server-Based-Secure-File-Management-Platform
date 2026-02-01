#!/bin/bash

# OS File Server - Full Stack Startup Script
# Starts C server, Python API, and opens web dashboard

echo "=================================================="
echo "   OS FILE SERVER - FULL STACK STARTUP"
echo "=================================================="
echo ""

# Check if server is built
if [ ! -f "build/file_server" ]; then
    echo "[ERROR] Server not built. Run 'make' first."
    exit 1
fi

# Check if Python dependencies are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "[ERROR] Flask not installed. Run:"
    echo "  cd api_layer && pip install -r requirements.txt"
    exit 1
fi

# Start C server in background
echo "[1/3] Starting C OS Core Server (port 8888)..."
./build/file_server &
SERVER_PID=$!
sleep 2

# Start Python API in background
echo "[2/3] Starting Python API Layer (port 5000)..."
cd api_layer
python3 app.py &
API_PID=$!
cd ..
sleep 2

# Open web dashboard
echo "[3/3] Opening Web Dashboard..."
if command -v xdg-open &> /dev/null; then
    xdg-open web_dashboard/index.html
elif command -v open &> /dev/null; then
    open web_dashboard/index.html
elif command -v start &> /dev/null; then
    start web_dashboard/index.html
else
    echo "[INFO] Please manually open: web_dashboard/index.html"
fi

echo ""
echo "=================================================="
echo "   SYSTEM RUNNING"
echo "=================================================="
echo "C Server PID: $SERVER_PID"
echo "API Layer PID: $API_PID"
echo ""
echo "Web Dashboard: file://$(pwd)/web_dashboard/index.html"
echo "API Endpoint: http://localhost:5000"
echo "C Server: TCP port 8888"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=================================================="

# Wait for user interrupt
trap "echo ''; echo 'Stopping services...'; kill $SERVER_PID $API_PID 2>/dev/null; echo 'Done.'; exit 0" INT
wait
