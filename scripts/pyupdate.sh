#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Get project root directory
PROJECT_ROOT="$(get_project_root)"
AI_OUTPUT_DIR="$PROJECT_ROOT/ai/outputs/dependency_updates"

print_status "🔄 Starting dependency update process..."

# Initialize status variables
UPDATE_STATUS="success"
POETRY_UPDATE_STATUS="success"
POETRY_LOCK_STATUS="success"
POETRY_CHECK_STATUS="success"
POETRY_INSTALL_STATUS="success"

# Update dependencies
print_status "📦 Updating dependencies..."
if run_command "poetry update"; then
    print_success "✅ Dependencies updated successfully"
else
    POETRY_UPDATE_STATUS="failed"
    UPDATE_STATUS="failed"
fi

# Update lock file
print_status "🔒 Updating lock file..."
if run_command "poetry lock"; then
    print_success "✅ Lock file updated successfully"
else
    POETRY_LOCK_STATUS="failed"
    UPDATE_STATUS="failed"
fi

# Check for any issues
print_status "🔍 Checking for issues..."
if run_command "poetry check"; then
    print_success "✅ Poetry check passed"
else
    POETRY_CHECK_STATUS="failed"
    UPDATE_STATUS="failed"
fi

# Install dependencies
print_status "📥 Installing dependencies..."
if run_command "poetry install --sync"; then
    print_success "✅ Dependencies installed successfully"
else
    POETRY_INSTALL_STATUS="failed"
    UPDATE_STATUS="failed"
fi

# Generate AI report
ADDITIONAL_CONTENT="  \"dependency_update_details\": {\n    \"poetry_update_status\": \"$POETRY_UPDATE_STATUS\",\n    \"poetry_lock_status\": \"$POETRY_LOCK_STATUS\",\n    \"poetry_check_status\": \"$POETRY_CHECK_STATUS\",\n    \"poetry_install_status\": \"$POETRY_INSTALL_STATUS\",\n    \"target_directory\": \"project_root/\",\n    \"configuration\": \"pyproject.toml\"\n  },"

generate_ai_report "dependency_update" "$UPDATE_STATUS" "0" "$AI_OUTPUT_DIR" "$ADDITIONAL_CONTENT"

if [ "$UPDATE_STATUS" = "success" ]; then
    print_success "✅ Dependencies updated successfully!"
    exit 0
else
    print_error "❌ Some dependency update steps failed!"
    exit 1
fi
