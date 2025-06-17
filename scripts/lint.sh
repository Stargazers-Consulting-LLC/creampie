#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Function to print colored status messages
print_status() {
    echo -e "\033[1;37m$1\033[0m"
}

print_success() {
    echo -e "\033[1;32m$1\033[0m"
}

print_error() {
    echo -e "\033[1;31m$1\033[0m"
}

# Function to run a command and handle errors
run_command() {
    if ! eval "$1"; then
        print_error "Failed: $1"
        exit 1
    fi
}

# Parse command line arguments
RUN_PYTHON=true
RUN_JS=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --python-only)
            RUN_JS=false
            shift
            ;;
        --js-only)
            RUN_PYTHON=false
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Usage: $0 [--python-only|--js-only]"
            exit 1
            ;;
    esac
done

print_status "🔍 Starting linting checks..."

if [ "$RUN_PYTHON" = true ]; then
    print_status "📝 Running Python checks..."
    pushd cream_api > /dev/null

    run_command "poetry run autoflake -i -r --remove-all-unused-imports --recursive --remove-unused-variables --in-place --quiet --exclude=__init__.py ."
    run_command "poetry run ruff check --fix ."
    run_command "poetry run ruff format ."
    run_command "poetry run mypy --config-file=../pyproject.toml ."

    popd > /dev/null
    print_success "✅ Python checks completed!"
fi

if [ "$RUN_JS" = true ]; then
    print_status "📦 Running JavaScript/TypeScript checks..."
    pushd cream_ui > /dev/null

    run_command "yarn eslint --fix ."
    run_command "yarn tsc --noEmit"
    run_command "yarn prettier --write . --log-level=warn"

    popd > /dev/null
    print_success "✅ JavaScript/TypeScript checks completed!"
fi

print_success "🎉 All selected linting checks completed successfully!"
