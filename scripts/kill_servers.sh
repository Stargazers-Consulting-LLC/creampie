#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Get project root directory
PROJECT_ROOT="$(get_project_root)"
AI_OUTPUT_DIR="$PROJECT_ROOT/ai/outputs/server_operations"

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

# Initialize status variables
KILL_STATUS="success"
FASTAPI_KILL_STATUS="not_attempted"
REACT_KILL_STATUS="not_attempted"

# Kill FastAPI if requested
if [ "$KILL_FASTAPI" = true ]; then
    # Try both patterns for FastAPI
    if kill_process "fastapi run main.py" "FastAPI"; then
        FASTAPI_KILL_STATUS="success"
    else
        FASTAPI_KILL_STATUS="failed"
        KILL_STATUS="failed"
    fi
fi

# Kill React if requested
if [ "$KILL_REACT" = true ]; then
    if kill_process "vite" "React"; then
        REACT_KILL_STATUS="success"
    else
        REACT_KILL_STATUS="failed"
        KILL_STATUS="failed"
    fi
fi

# Generate AI report
ADDITIONAL_CONTENT="  \"server_kill_details\": {\n    \"kill_status\": \"$KILL_STATUS\",\n    \"fastapi_kill_status\": \"$FASTAPI_KILL_STATUS\",\n    \"react_kill_status\": \"$REACT_KILL_STATUS\",\n    \"fastapi_requested\": \"$KILL_FASTAPI\",\n    \"react_requested\": \"$KILL_REACT\"\n  },"

generate_ai_report "server_kill" "$KILL_STATUS" "0" "$AI_OUTPUT_DIR" "$ADDITIONAL_CONTENT"

if [ "$KILL_STATUS" = "success" ]; then
    print_success "✅ Server kill operations completed successfully!"
    exit 0
else
    print_error "❌ Some server kill operations failed!"
    exit 1
fi
