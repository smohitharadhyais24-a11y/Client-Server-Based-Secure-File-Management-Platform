#!/bin/bash

# Quick test to verify lock rejection works

cd '/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS'

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        VERIFYING LOCK REJECTION FIX - QUICK TEST               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Using test3_large.bin (5MB, ~13 sec with --slow 10)"
echo "Using test_100mb.bin (100MB, ~4+ min with --slow 10)"
echo ""
echo "Clean start..."
killall -9 file_server 2>/dev/null
rm -f storage/* metadata/* logs/* 2>/dev/null
sleep 1

echo ""
echo "=== STARTING SERVER ==="
./build/file_server > /tmp/server_test.log 2>&1 &
SERVER_PID=$!
sleep 2
echo "✓ Server started (PID: $SERVER_PID)"

echo ""
echo "=== TEST 1: 5MB file (quick test) ==="
echo "Client 1: Upload with --slow 10"
python3 client/client.py UPLOAD test_files/test3_large.bin --slow 10 > /tmp/c1_quick.log 2>&1 &
C1_PID=$!
sleep 2

echo "Client 2: Attempt concurrent upload (should be REJECTED)"
python3 client/client.py UPLOAD test_files/test3_large.bin > /tmp/c2_quick.log 2>&1

echo ""
echo "Results:"
if grep -q "ERROR" /tmp/c2_quick.log && grep -q "locked" /tmp/c2_quick.log; then
    echo "✅ SUCCESS! Client 2 got lock rejection error"
    echo "   $(grep ERROR /tmp/c2_quick.log)"
else
    echo "❌ FAILED! Client 2 should have been rejected"
    echo "   Got: $(grep -E 'SUCCESS|ERROR' /tmp/c2_quick.log | head -1)"
fi

wait $C1_PID 2>/dev/null
echo ""
echo "Waiting for cleanup..."
sleep 2

echo ""
echo "=== STOPPING SERVER ==="
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
echo "✓ Server stopped"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
if grep -q "ERROR" /tmp/c2_quick.log && grep -q "locked" /tmp/c2_quick.log; then
    echo "║  ✅ LOCK REJECTION WORKING - DEMO READY!                       ║"
else
    echo "║  ❌ LOCK REJECTION NOT WORKING - CHECK SERVER CODE              ║"
fi
echo "╚════════════════════════════════════════════════════════════════╝"
