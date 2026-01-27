#!/bin/bash

# SETUP VERIFICATION SCRIPT
# Checks if all prerequisites are met

echo "=========================================="
echo " SETUP VERIFICATION SCRIPT"
echo "=========================================="
echo ""

ERRORS=0

# Check GCC
echo -n "Checking GCC... "
if command -v gcc &> /dev/null; then
    GCC_VERSION=$(gcc --version | head -n1)
    echo "✓ Found: $GCC_VERSION"
else
    echo "✗ NOT FOUND"
    echo "   Install: sudo apt-get install gcc"
    ERRORS=$((ERRORS+1))
fi

# Check Python
echo -n "Checking Python3... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found: $PYTHON_VERSION"
else
    echo "✗ NOT FOUND"
    echo "   Install: sudo apt-get install python3"
    ERRORS=$((ERRORS+1))
fi

# Check pthread support
echo -n "Checking pthread... "
TEST_FILE=$(mktemp).c
echo "int main() { return 0; }" > $TEST_FILE
if gcc -pthread -xc $TEST_FILE -o /dev/null 2>&1; then
    echo "✓ pthread support available"
else
    echo "✗ pthread NOT available"
    ERRORS=$((ERRORS+1))
fi
rm -f $TEST_FILE

# Check make
echo -n "Checking make... "
if command -v make &> /dev/null; then
    MAKE_VERSION=$(make --version | head -n1)
    echo "✓ Found: $MAKE_VERSION"
else
    echo "⚠ NOT FOUND (optional)"
    echo "   Install: sudo apt-get install make"
fi

echo ""
echo "=========================================="
echo " Directory Structure"
echo "=========================================="

# Check directories
REQUIRED_DIRS=("server" "client" "storage" "metadata" "logs" "test_files")
for dir in "${REQUIRED_DIRS[@]}"; do
    echo -n "Checking $dir/... "
    if [ -d "$dir" ]; then
        echo "✓ Exists"
    else
        echo "✗ Missing"
        ERRORS=$((ERRORS+1))
    fi
done

echo ""
echo "=========================================="
echo " Required Files"
echo "=========================================="

# Check required files
echo -n "Checking server/file_server.c... "
if [ -f "server/file_server.c" ]; then
    LINES=$(wc -l < server/file_server.c)
    echo "✓ Found ($LINES lines)"
else
    echo "✗ Missing"
    ERRORS=$((ERRORS+1))
fi

echo -n "Checking client/client.py... "
if [ -f "client/client.py" ]; then
    LINES=$(wc -l < client/client.py)
    echo "✓ Found ($LINES lines)"
else
    echo "✗ Missing"
    ERRORS=$((ERRORS+1))
fi

echo -n "Checking Makefile... "
if [ -f "Makefile" ]; then
    echo "✓ Found"
else
    echo "⚠ Missing (can compile manually)"
fi

echo ""
echo "=========================================="
echo " Test Files"
echo "=========================================="

TEST_FILES=("test1.txt" "test2.txt" "test3.txt")
for file in "${TEST_FILES[@]}"; do
    echo -n "Checking test_files/$file... "
    if [ -f "test_files/$file" ]; then
        SIZE=$(stat -f%z "test_files/$file" 2>/dev/null || stat -c%s "test_files/$file" 2>/dev/null)
        echo "✓ Found ($SIZE bytes)"
    else
        echo "⚠ Missing (can create with 'make test')"
    fi
done

echo ""
echo "=========================================="
echo " Network Check"
echo "=========================================="

# Check if port 8888 is available
echo -n "Checking port 8888... "
if command -v lsof &> /dev/null; then
    if lsof -i:8888 &> /dev/null; then
        echo "⚠ Port in use (server might be running)"
    else
        echo "✓ Port available"
    fi
elif command -v netstat &> /dev/null; then
    if netstat -tuln | grep :8888 &> /dev/null; then
        echo "⚠ Port in use (server might be running)"
    else
        echo "✓ Port available"
    fi
else
    echo "? Cannot check (lsof/netstat not found)"
fi

echo ""
echo "=========================================="
echo " RESULT"
echo "=========================================="

if [ $ERRORS -eq 0 ]; then
    echo "✓ All checks passed!"
    echo ""
    echo "Next steps:"
    echo "  1. Compile server:  make build"
    echo "  2. Start server:    make run"
    echo "  3. Run client:      python3 client/client.py"
    echo ""
    echo "Or run full demo:  bash demo_full.sh"
else
    echo "✗ Found $ERRORS error(s)"
    echo ""
    echo "Please fix the errors above before proceeding."
fi

echo ""
