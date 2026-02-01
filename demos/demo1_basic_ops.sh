#!/bin/bash

# DEMO SCRIPT 1: Basic Operations
# Demonstrates: Upload, List, Download, Delete

echo "=========================================="
echo " DEMO 1: Basic File Operations"
echo "=========================================="
echo ""

echo "Step 1: Upload test file"
python3 client/client.py UPLOAD test_files/test1.txt
sleep 1

echo ""
echo "Step 2: List files on server"
python3 client/client.py LIST
sleep 1

echo ""
echo "Step 3: Download file"
python3 client/client.py DOWNLOAD test1.txt downloaded_test1.txt
sleep 1

echo ""
echo "Step 4: Delete file"
python3 client/client.py DELETE test1.txt
sleep 1

echo ""
echo "Step 5: List files again (should be empty)"
python3 client/client.py LIST

echo ""
echo "=========================================="
echo " DEMO 1 COMPLETE"
echo "=========================================="
