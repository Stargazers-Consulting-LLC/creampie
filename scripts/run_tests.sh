#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Variable declarations
TEST_LOG_DIR="test_logs"
TEST_LOG_FILE="$TEST_LOG_DIR/pytest.log"
WITH_TIMESTAMP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--with-timestamp)
            WITH_TIMESTAMP=true
            shift
            ;;
        *)
            # Pass all other arguments to pytest
            PYTEST_ARGS+=("$1")
            shift
            ;;
    esac
done

# Function to ensure log directory exists
ensure_log_directory() {
    if [ ! -d "$TEST_LOG_DIR" ]; then
        mkdir -p "$TEST_LOG_DIR"
        print_status "Created test log directory: $TEST_LOG_DIR"
    fi
}

# Function to get timestamped log file name
get_log_file() {
    if [ "$WITH_TIMESTAMP" = true ]; then
        echo "$TEST_LOG_DIR/pytest_$(date +%Y%m%d_%H%M%S).log"
    else
        echo "$TEST_LOG_FILE"
    fi
}

# Main script logic
print_status "Starting test suite execution"

# Ensure log directory exists
ensure_log_directory

# Get log file name
CURRENT_LOG_FILE=$(get_log_file)

# Run pytest with logging
print_status "Running pytest and logging output to $CURRENT_LOG_FILE"
[ -t 1 ] && export FORCE_COLOR=1

# First run for display
poetry run pytest "${PYTEST_ARGS[@]}" &
DISPLAY_PID=$!

# Second run for logging
poetry run pytest "${PYTEST_ARGS[@]}" > "$CURRENT_LOG_FILE" 2>&1
LOG_STATUS=$?

# Wait for display run to finish
wait $DISPLAY_PID
DISPLAY_STATUS=$?

# Exit with the status from the display run
if [ $DISPLAY_STATUS -eq 0 ]; then
    print_success "Tests completed successfully"
    exit 0
else
    print_error "Tests failed - check $CURRENT_LOG_FILE for details"
    exit 1
fi
