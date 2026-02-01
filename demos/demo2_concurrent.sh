#!/bin/bash

# DEMO SCRIPT 2: Concurrent Access
# Demonstrates: File locking when multiple clients access same file

echo "=========================================="
echo " DEMO 2: Concurrent Access & Locking"
echo "=========================================="
echo ""

echo "This demo requires 3 terminals:"
echo ""
echo "Terminal 1: Run server"
echo "  make run"
echo ""
echo "Terminal 2: Start long upload (run this first)"
echo "  python3 client/client.py UPLOAD test_files/test3.txt"
echo ""
echo "Terminal 3: Try to upload same file immediately (while Terminal 2 is running)"
echo "  python3 client/client.py UPLOAD test_files/test3.txt"
echo ""
echo "Expected Result:"
echo "  Terminal 3 will receive: ERROR - File is locked by another process"
echo ""
echo "This demonstrates:"
echo "  - File locking with fcntl"
echo "  - Deadlock avoidance (non-blocking locks)"
echo "  - Multiple clients cannot write to same file simultaneously"
echo ""
echo "=========================================="
