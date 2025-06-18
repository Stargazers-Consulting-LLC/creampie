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
SHOW_HELP=false
VERBOSE=false
NO_LOG=false
TEST_PATH=""
TEST_FUNCTION=""
MARKER=""
WATCH_MODE=false

# Function to show usage information
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] [TEST_PATH] [TEST_FUNCTION]

Run tests with enhanced logging and flexibility.

OPTIONS:
    -h, --help              Show this help message
    -t, --with-timestamp    Use timestamped log files
    -v, --verbose           Enable verbose output
    -n, --no-log            Don't create log files (useful for quick runs)
    -m, --marker MARKER     Run tests with specific marker (e.g., slow, integration)
    -w, --watch             Watch mode: auto-rerun tests when files change
    --list                  List available test files
    --list-functions FILE   List test functions in a specific file
    --list-markers          List available pytest markers

TEST_PATH:
    Path to test file or directory (e.g., tests/stock_data/test_api.py)
    If not specified, runs all tests

TEST_FUNCTION:
    Specific test function to run (e.g., test_get_stock_data)
    Must be used with a TEST_PATH

EXAMPLES:
    $0                                    # Run all tests
    $0 tests/stock_data/test_api.py      # Run specific test file
    $0 tests/stock_data/                 # Run all tests in directory
    $0 tests/stock_data/test_api.py::test_get_stock_data  # Run specific test
    $0 -v tests/stock_data/test_api.py   # Run with verbose output
    $0 -t                                 # Run with timestamped logs
    $0 -m slow                            # Run only slow tests
    $0 -w                                 # Watch mode
    $0 --list                             # List available test files
    $0 --list-functions tests/stock_data/test_api.py
    $0 --list-markers                     # List available markers

EOF
}

# Function to list available test files
list_test_files() {
    print_status "Available test files:"
    echo

    # Find all test files recursively
    find cream_api/tests -name "test_*.py" -type f | while read -r file; do
        # Get relative path from project root
        rel_path="${file#cream_api/}"
        echo "  $rel_path"
    done
    echo
}

# Function to list test functions in a file
list_test_functions() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        print_error "File not found: $file"
        exit 1
    fi

    print_status "Test functions in $file:"
    echo

    # Extract test function names using grep
    grep -E "^def test_" "$file" | sed 's/def //' | sed 's/(.*$//' | while read -r func; do
        echo "  $func"
    done
    echo
}

# Function to list available pytest markers
list_markers() {
    print_status "Available pytest markers:"
    echo

    # Run pytest --markers to get available markers
    poetry run pytest --markers 2>/dev/null | grep -E "^@pytest\.mark\." | while read -r marker; do
        echo "  $marker"
    done
    echo
}

# Function to validate test path
validate_test_path() {
    local path="$1"

    if [[ -z "$path" ]]; then
        return 0  # Empty path is valid (runs all tests)
    fi

    # Check if it's a file
    if [[ -f "$path" ]]; then
        if [[ "$path" == *test_*.py ]]; then
            return 0
        else
            print_error "File $path is not a test file (should start with 'test_')"
            return 1
        fi
    fi

    # Check if it's a directory
    if [[ -d "$path" ]]; then
        # Check if directory contains test files
        if find "$path" -name "test_*.py" -type f | grep -q .; then
            return 0
        else
            print_error "Directory $path contains no test files"
            return 1
        fi
    fi

    print_error "Path $path does not exist"
    return 1
}

# Function to run tests in watch mode
run_watch_mode() {
    print_status "Starting watch mode - tests will re-run when files change"
    print_status "Press Ctrl+C to stop"

    # Check if fswatch is available
    if command -v fswatch &> /dev/null; then
        WATCH_CMD="fswatch -o cream_api/tests"
    elif command -v inotifywait &> /dev/null; then
        WATCH_CMD="inotifywait -r -e modify,create,delete cream_api/tests"
    else
        print_error "No file watcher found. Install fswatch or inotify-tools for watch mode."
        exit 1
    fi

    # Run initial test
    run_tests_once

    # Watch for changes
    while true; do
        if eval "$WATCH_CMD" > /dev/null 2>&1; then
            echo
            print_status "Files changed, re-running tests..."
            run_tests_once
        fi
    done
}

# Function to run tests once
run_tests_once() {
    local start_time=$(date +%s)

    # Build pytest arguments
    local pytest_args=()

    # Add verbose flag if requested
    if [ "$VERBOSE" = true ]; then
        pytest_args+=("-v")
    fi

    # Add marker if specified
    if [[ -n "$MARKER" ]]; then
        pytest_args+=("-m" "$MARKER")
    fi

    # Add test path and function if specified
    if [[ -n "$TEST_PATH" ]]; then
        if [[ -n "$TEST_FUNCTION" ]]; then
            pytest_args+=("$TEST_PATH::$TEST_FUNCTION")
        else
            pytest_args+=("$TEST_PATH")
        fi
    fi

    # Run pytest
    if poetry run pytest "${pytest_args[@]}"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_success "Tests completed successfully in ${duration}s"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_error "Tests failed after ${duration}s"
        return 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            SHOW_HELP=true
            shift
            ;;
        -t|--with-timestamp)
            WITH_TIMESTAMP=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -n|--no-log)
            NO_LOG=true
            shift
            ;;
        -m|--marker)
            if [[ -z "$2" ]]; then
                print_error "Error: -m/--marker requires a marker name"
                exit 1
            fi
            MARKER="$2"
            shift 2
            ;;
        -w|--watch)
            WATCH_MODE=true
            shift
            ;;
        --list)
            list_test_files
            exit 0
            ;;
        --list-functions)
            if [[ -z "$2" ]]; then
                print_error "Error: --list-functions requires a file path"
                exit 1
            fi
            list_test_functions "$2"
            exit 0
            ;;
        --list-markers)
            list_markers
            exit 0
            ;;
        -*)
            # Unknown option
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            # Check if this looks like a test function (contains ::)
            if [[ "$1" == *"::"* ]]; then
                # Split on :: to get path and function
                IFS='::' read -r TEST_PATH TEST_FUNCTION <<< "$1"
            else
                # This is either a test path or the first positional argument
                if [[ -z "$TEST_PATH" ]]; then
                    TEST_PATH="$1"
                elif [[ -z "$TEST_FUNCTION" ]]; then
                    TEST_FUNCTION="$1"
                else
                    print_error "Too many arguments provided"
                    show_usage
                    exit 1
                fi
            fi
            shift
            ;;
    esac
done

# Show help if requested
if [ "$SHOW_HELP" = true ]; then
    show_usage
    exit 0
fi

# Validate test path
if ! validate_test_path "$TEST_PATH"; then
    exit 1
fi

# Main script logic
print_status "Starting test suite execution"

# Show what we're running
if [[ -n "$TEST_PATH" ]]; then
    if [[ -n "$TEST_FUNCTION" ]]; then
        print_status "Target: $TEST_PATH::$TEST_FUNCTION"
    else
        print_status "Target: $TEST_PATH"
    fi
else
    print_status "Target: All tests"
fi

# Show additional options
if [[ -n "$MARKER" ]]; then
    print_status "Marker: $MARKER"
fi

if [ "$WATCH_MODE" = true ]; then
    print_status "Watch mode: Enabled"
fi

# Handle watch mode
if [ "$WATCH_MODE" = true ]; then
    run_watch_mode
    exit 0
fi

# Handle regular test execution
if [ "$NO_LOG" = true ]; then
    # Run tests without logging
    if run_tests_once; then
        exit 0
    else
        exit 1
    fi
fi

# Ensure log directory exists
if [ ! -d "$TEST_LOG_DIR" ]; then
    mkdir -p "$TEST_LOG_DIR"
    print_status "Created test log directory: $TEST_LOG_DIR"
fi

# Get log file name
if [ "$WITH_TIMESTAMP" = true ]; then
    CURRENT_LOG_FILE="$TEST_LOG_DIR/pytest_$(date +%Y%m%d_%H%M%S).log"
else
    CURRENT_LOG_FILE="$TEST_LOG_FILE"
fi

# Run pytest with logging
print_status "Running pytest and logging output to $CURRENT_LOG_FILE"
[ -t 1 ] && export FORCE_COLOR=1

# Build pytest arguments for logging run
PYTEST_ARGS=()

# Add verbose flag if requested
if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS+=("-v")
fi

# Add marker if specified
if [[ -n "$MARKER" ]]; then
    PYTEST_ARGS+=("-m" "$MARKER")
fi

# Add test path and function if specified
if [[ -n "$TEST_PATH" ]]; then
    if [[ -n "$TEST_FUNCTION" ]]; then
        PYTEST_ARGS+=("$TEST_PATH::$TEST_FUNCTION")
    else
        PYTEST_ARGS+=("$TEST_PATH")
    fi
fi

# Run pytest with both display and logging
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
