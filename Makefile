# Makefile for Secure File Management Server
# Operating System Concepts Implementation

CC = gcc
CFLAGS = -Wall -Wextra -pthread -O2
LIBS = -lcrypto
TARGET = file_server
SRC_DIR = server
BUILD_DIR = build
SOURCE = $(SRC_DIR)/file_server.c

# Directories
STORAGE_DIR = storage
METADATA_DIR = metadata
LOG_DIR = logs
TEST_DIR = test_files

.PHONY: all build clean run setup help test

all: setup build

# Build the server
build:
	@echo "=== Building File Server ==="
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(SOURCE) -o $(BUILD_DIR)/$(TARGET) $(LIBS)
	@echo "✓ Server built successfully: $(BUILD_DIR)/$(TARGET)"

# Setup directories
setup:
	@echo "=== Setting up project directories ==="
	@mkdir -p $(STORAGE_DIR)
	@mkdir -p $(METADATA_DIR)
	@mkdir -p $(LOG_DIR)
	@mkdir -p $(TEST_DIR)
	@echo "✓ Directories created"

# Run the server
run: build
	@echo "=== Starting File Server ==="
	@echo "Press Ctrl+C to stop the server"
	@echo ""
	@cd $(BUILD_DIR) && ./$(TARGET)

# Clean build artifacts
clean:
	@echo "=== Cleaning build artifacts ==="
	@rm -rf $(BUILD_DIR)
	@echo "✓ Build directory cleaned"

# Clean all (including storage, logs, metadata)
clean-all: clean
	@echo "=== Cleaning all data ==="
	@rm -rf $(STORAGE_DIR)/*
	@rm -rf $(METADATA_DIR)/*
	@rm -rf $(LOG_DIR)/*
	@echo "✓ All data cleaned"

# Run tests
test: build
	@echo "=== Running Tests ==="
	@echo "Creating test files..."
	@echo "Test file content" > $(TEST_DIR)/test1.txt
	@echo "Another test file" > $(TEST_DIR)/test2.txt
	@echo "Large test file with more content to test transfer" > $(TEST_DIR)/test3.txt
	@echo "✓ Test files created in $(TEST_DIR)/"

# Show help
help:
	@echo "Secure File Management Server - Makefile Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Setup directories and build server (default)"
	@echo "  build      - Compile the C server"
	@echo "  setup      - Create required directories"
	@echo "  run        - Build and start the server"
	@echo "  clean      - Remove build artifacts"
	@echo "  clean-all  - Remove build artifacts and all data"
	@echo "  test       - Create test files for demonstration"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Example workflow:"
	@echo "  make          # Setup and build"
	@echo "  make test     # Create test files"
	@echo "  make run      # Start server (in one terminal)"
	@echo "  # Then run client in another terminal"
