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

# Kill FastAPI if requested
if [ "$KILL_FASTAPI" = true ]; then
    # Try both patterns for FastAPI
    kill_process "fastapi run main.py" "FastAPI"
fi

# Kill React if requested
if [ "$KILL_REACT" = true ]; then
    kill_process "vite" "React"
fi
