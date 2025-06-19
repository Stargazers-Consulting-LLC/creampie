#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Get the project root and API directory
PROJECT_ROOT="$(get_project_root)"
API_DIR="$PROJECT_ROOT/cream_api"
AI_OUTPUT_DIR="ai/outputs/migration_results"

# Check if we're in the right directory
if [ ! -f "$API_DIR/alembic.ini" ]; then
    handle_error "alembic.ini not found in $API_DIR"
fi

# Change to the API directory
cd "$API_DIR" || handle_error "Failed to change to $API_DIR"

# Initialize status variables
MIGRATION_CREATED="no"
MIGRATION_STATUS="success"

# Create new migration if there are changes
print_status "Checking for model changes..."
if poetry run alembic revision --autogenerate -m "auto migration" > /dev/null 2>&1; then
    print_success "Created new migration"
    MIGRATION_CREATED="yes"
else
    print_success "No new migrations needed"
fi

# Apply all pending migrations
print_status "Applying pending migrations..."
if poetry run alembic upgrade head; then
    print_success "All migrations applied successfully"
else
    MIGRATION_STATUS="failed"
    handle_error "Failed to apply migrations"
fi

# Generate AI report using common function
ADDITIONAL_CONTENT="  \"migration_details\": {\n    \"migration_created\": \"$MIGRATION_CREATED\",\n    \"migration_status\": \"$MIGRATION_STATUS\",\n    \"target_directory\": \"cream_api/\",\n    \"configuration\": \"alembic.ini\"\n  },"

generate_ai_report "migration" "$MIGRATION_STATUS" "0" "$AI_OUTPUT_DIR" "$ADDITIONAL_CONTENT"
