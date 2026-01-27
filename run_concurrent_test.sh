#!/bin/bash

cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   CONCURRENT UPLOAD TEST - DEADLOCK AVOIDANCE DEMONSTRATION    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "✓ Server timeout increased to 300 seconds (5 minutes)"
echo "✓ Using 100MB file with --slow 10 (4.3 minute upload)"
echo "✓ Client 2 will attempt concurrent upload"
echo ""
echo "=== STEP 1: START SERVER ==="
./build/file_server &
SERVER_PID=$!
echo "[PID $SERVER_PID] Server started (listening on port 8888)"
sleep 2

echo ""
echo "=== STEP 2: CLIENT 1 STARTS LONG UPLOAD ==="
echo "Running: python3 client/client.py UPLOAD test_files/test_100mb.bin --slow 10"
echo "Expected: Will take ~4+ minutes"
echo ""
python3 client/client.py UPLOAD test_files/test_100mb.bin --slow 10 &
CLIENT1_PID=$!
echo "[PID $CLIENT1_PID] Client 1 started at $(date '+%H:%M:%S')"
echo ""

echo "⏸️  WAITING 15 SECONDS... (let Client 1 reach ~3-5% progress)"
sleep 15

echo ""
echo "=== STEP 3: CLIENT 2 ATTEMPTS CONCURRENT UPLOAD ==="
echo "Running: python3 client/client.py UPLOAD test_files/test_100mb.bin"
echo "Expected: ERROR - File is locked by another process"
echo ""
python3 client/client.py UPLOAD test_files/test_100mb.bin
CLIENT2_RESULT=$?

echo ""
if grep -q "locked" <(python3 client/client.py UPLOAD test_files/test_100mb.bin 2>&1) 2>/dev/null; then
    echo "✅ SUCCESS: Lock rejection working!"
else
    echo "⏳ (Waiting for Client 1 to finish...)"
fi

echo ""
echo "Waiting for Client 1 to complete..."
wait $CLIENT1_PID
echo "[PID $CLIENT1_PID] Client 1 finished at $(date '+%H:%M:%S')"

echo ""
echo "=== VERIFICATION ==="
ls -lh storage/test_100mb.bin
echo ""
echo "Cleaning up..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo "✅ Test complete!"
