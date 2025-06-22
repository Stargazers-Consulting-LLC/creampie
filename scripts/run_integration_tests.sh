#!/bin/bash

# Integration Test Runner Script
# Simple wrapper to run both backend (pytest) and frontend (React) tests
#
# SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
# SPDX-License-Identifier: MIT

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Function to show usage information
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run both backend (pytest) and frontend (React) tests.

OPTIONS:
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output for both test suites

EXAMPLES:
    $0                    # Run all integration tests
    $0 -v                 # Run all tests with verbose output

EOF
}

# Parse command line arguments
VERBOSE=false
SHOW_HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            SHOW_HELP=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Show help if requested
if [ "$SHOW_HELP" = true ]; then
    show_usage
    exit 0
fi

# Main execution
print_status "🚀 Running Integration Tests"
print_status "============================"

# Build arguments for both scripts
BACKEND_ARGS=()
FRONTEND_ARGS=()

if [ "$VERBOSE" = true ]; then
    BACKEND_ARGS+=("-v")
    FRONTEND_ARGS+=("-v")
fi

# Run backend tests
print_status "🔧 Running Backend Tests (pytest)..."
if "$SCRIPT_DIR/run_pytest.sh" "${BACKEND_ARGS[@]}"; then
    print_success "✅ Backend tests ran successfully"
else
    print_error "❌ Backend tests failed to execute"
    exit 1
fi

echo

# Run frontend tests
print_status "⚛️  Running Frontend Tests (React)..."
if "$SCRIPT_DIR/run_react_tests.sh" "${FRONTEND_ARGS[@]}"; then
    print_success "✅ Frontend tests ran successfully"
else
    print_error "❌ Frontend tests failed to execute"
    exit 1
fi

echo
print_success "🎉 All integration tests ran!"
