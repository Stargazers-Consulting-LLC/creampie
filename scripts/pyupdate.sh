#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

print_status "🔄 Starting dependency update process..."

# Update dependencies
print_status "📦 Updating dependencies..."
run_command "poetry update"

# Update lock file
print_status "🔒 Updating lock file..."
run_command "poetry lock"

# Check for any issues
print_status "🔍 Checking for issues..."
run_command "poetry check"

# Install dependencies
print_status "📥 Installing dependencies..."
run_command "poetry install --sync"

print_success "✅ Dependencies updated successfully!"
