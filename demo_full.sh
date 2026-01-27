#!/bin/bash

# COMPREHENSIVE DEMO SCRIPT
# Runs all demo operations in sequence

echo "=========================================="
echo " COMPREHENSIVE FILE SERVER DEMO"
echo " Operating System Concepts Implementation"
echo "=========================================="
echo ""
echo "Make sure server is running in another terminal!"
echo "Start with: make run"
echo ""
read -p "Press Enter when server is ready..."

echo ""
echo "=========================================="
echo " PART 1: Basic Upload/Download"
echo "=========================================="
sleep 1

echo ""
echo "[UPLOAD] Uploading test1.txt..."
python3 client/client.py UPLOAD test_files/test1.txt
sleep 1

echo ""
echo "[LIST] Listing files..."
python3 client/client.py LIST
sleep 1

echo ""
echo "[DOWNLOAD] Downloading test1.txt..."
python3 client/client.py DOWNLOAD test1.txt downloaded_test1.txt
sleep 1

echo ""
echo "=========================================="
echo " PART 2: Multiple Files"
echo "=========================================="
sleep 1

echo ""
echo "[UPLOAD] Uploading test2.txt..."
python3 client/client.py UPLOAD test_files/test2.txt
sleep 1

echo ""
echo "[UPLOAD] Uploading test3.txt..."
python3 client/client.py UPLOAD test_files/test3.txt
sleep 1

echo ""
echo "[LIST] Listing all files..."
python3 client/client.py LIST
sleep 1

echo ""
echo "=========================================="
echo " PART 3: Logs and Locks"
echo "=========================================="
sleep 1

echo ""
echo "[LOGS] Viewing audit logs..."
python3 client/client.py LOGS
sleep 1

echo ""
echo "[LOCKS] Viewing current locks..."
python3 client/client.py LOCKS
sleep 1

echo ""
echo "=========================================="
echo " PART 4: File Deletion"
echo "=========================================="
sleep 1

echo ""
echo "[DELETE] Deleting test1.txt..."
python3 client/client.py DELETE test1.txt
sleep 1

echo ""
echo "[LIST] Final file list..."
python3 client/client.py LIST
sleep 1

echo ""
echo "=========================================="
echo " DEMO COMPLETE!"
echo "=========================================="
echo ""
echo "Key OS Concepts Demonstrated:"
echo "  ✓ UNIX File I/O (open, read, write)"
echo "  ✓ TCP Socket IPC"
echo "  ✓ File Locking (fcntl)"
echo "  ✓ Deadlock Prevention (bounded transfers)"
echo "  ✓ Thread Management (pthread)"
echo "  ✓ Audit Logging"
echo ""
echo "Check downloaded_test1.txt to verify download success!"
