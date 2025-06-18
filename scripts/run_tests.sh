#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Variable declarations
TEST_LOG_DIR="test_logs"
TEST_LOG_FILE="$TEST_LOG_DIR/pytest.log"

# Function to ensure log directory exists
ensure_log_directory() {
    if [ ! -d "$TEST_LOG_DIR" ]; then
        mkdir -p "$TEST_LOG_DIR"
        print_status "Created test log directory: $TEST_LOG_DIR"
    fi
}

# Main script logic
print_status "Starting test suite execution"

# Ensure log directory exists
ensure_log_directory

# Run pytest with output teeing
print_status "Running pytest and logging output to $TEST_LOG_FILE"
if poetry run pytest "$@" 2>&1 | tee "$TEST_LOG_FILE"; then
    print_success "Tests completed successfully"
    exit 0
else
    print_error "Tests failed - check $TEST_LOG_FILE for details"
    exit 1
fi
