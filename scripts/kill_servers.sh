#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Parse command line arguments
KILL_FASTAPI=false
KILL_REACT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --fastapi)
            KILL_FASTAPI=true
            shift
            ;;
        --react)
            KILL_REACT=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Usage: $0 [--fastapi|--react]"
            echo "You must specify at least one process to kill"
            exit 1
            ;;
    esac
done

# Check if at least one process was specified
if [ "$KILL_FASTAPI" = false ] && [ "$KILL_REACT" = false ]; then
    print_error "No process specified to kill"
    echo "Usage: $0 [--fastapi|--react]"
    echo "You must specify at least one process to kill"
    exit 1
fi

# Function to kill a process by its command pattern
kill_process() {
    local pattern="$1"
    local process_name="$2"

    print_status "🔍 Searching for $process_name process..."

    # Find the process ID
    local PID=$(ps aux | grep "$pattern" | grep -v grep | awk '{print $2}')

    if [ -z "$PID" ]; then
        print_status "No $process_name process found running"
        return 0
    fi

    print_status "Found $process_name process with PID: $PID"
    print_status "🔄 Killing process..."

    # Kill the process
    if ! kill "$PID" 2>/dev/null; then
        print_error "Failed to kill $process_name process with PID: $PID"
        return 1
    fi

    # Check if process was killed
    if ps -p "$PID" > /dev/null 2>&1; then
        print_status "Process still running, forcing kill..."
        if ! kill -9 "$PID" 2>/dev/null; then
            print_error "Failed to force kill $process_name process with PID: $PID"
            return 1
        fi
    fi

    print_success "✅ $process_name process killed successfully"
    return 0
}

# Kill FastAPI if requested
if [ "$KILL_FASTAPI" = true ]; then
    # Try both patterns for FastAPI
    kill_process "fastapi run main.py" "FastAPI"
fi

# Kill React if requested
if [ "$KILL_REACT" = true ]; then
    kill_process "vite" "React"
fi
