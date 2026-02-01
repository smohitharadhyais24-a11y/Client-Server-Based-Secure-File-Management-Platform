#!/bin/bash

echo "=== CONCURRENT UPLOAD TEST WITH 100MB FILE ==="
echo ""
echo "Starting Server..."
killall -9 file_server 2>/dev/null
sleep 1
rm -f storage/* metadata/* logs/* 2>/dev/null
./build/file_server &
SERVER_PID=$!
sleep 2

echo "Client 1: Starting 100MB upload with --slow 10 (will take ~4+ minutes)..."
echo "Time: $(date)"
python3 client/client.py UPLOAD test_files/test_100mb.bin --slow 10 > /tmp/c1.log 2>&1 &
CLIENT1_PID=$!
echo "Client 1 PID: $CLIENT1_PID"

sleep 3

echo ""
echo "Client 2: Attempting concurrent upload (should get LOCKED error)..."
echo "Time: $(date)"
python3 client/client.py UPLOAD test_files/test_100mb.bin > /tmp/c2.log 2>&1
echo "Client 2 Response:"
cat /tmp/c2.log | tail -5

echo ""
echo "Waiting for Client 1 to finish..."
wait $CLIENT1_PID
echo "Client 1 finished at $(date)"
echo "Client 1 final output:"
cat /tmp/c1.log | tail -5

echo ""
echo "=== TEST RESULTS ==="
if grep -q "ERROR.*locked" /tmp/c2.log; then
    echo "✅ SUCCESS: Client 2 got LOCKED error (deadlock avoidance works!)"
elif grep -q "SUCCESS" /tmp/c2.log && grep -q "SUCCESS" /tmp/c1.log; then
    echo "⚠️  Both uploads succeeded (sequential, not concurrent collision)"
else
    echo "❌ Unexpected result"
fi

echo ""
echo "Cleaning up..."
kill $SERVER_PID 2>/dev/null

echo "Test complete!"
