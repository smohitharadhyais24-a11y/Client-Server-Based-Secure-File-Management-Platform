#!/bin/bash

# DEMO SCRIPT 3: View Logs and Locks
# Demonstrates: Audit logging and lock inspection

echo "=========================================="
echo " DEMO 3: Logs and Locks"
echo "=========================================="
echo ""

echo "Step 1: Upload a file"
python3 client/client.py UPLOAD test_files/test2.txt
sleep 1

echo ""
echo "Step 2: View audit logs"
python3 client/client.py LOGS
sleep 1

echo ""
echo "Step 3: View current locks"
python3 client/client.py LOCKS
sleep 1

echo ""
echo "=========================================="
echo " DEMO 3 COMPLETE"
echo "=========================================="
