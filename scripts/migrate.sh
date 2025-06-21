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
VALIDATION_STATUS="success"

# Validate migration state before proceeding
print_status "🔍 Validating migration state..."
if ! poetry run alembic current > /dev/null 2>&1; then
    print_error "❌ Migration state validation failed"
    print_status "💡 This might indicate:"
    print_status "   - Missing migration files"
    print_status "   - Database/alembic_version table mismatch"
    print_status "   - Connection issues"
    print_status ""
    print_status "🔧 Try these solutions:"
    print_status "   - Check database connection: poetry run alembic current"
    print_status "   - Reset migration state: truncate alembic_version table"
    print_status "   - Or drop all tables and start fresh"
    VALIDATION_STATUS="failed"
    MIGRATION_STATUS="failed"
    handle_error "Migration state validation failed. Please check the database connection and alembic_version table."
fi
print_success "✅ Migration state validation passed"

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
    print_error "❌ Failed to apply migrations"
    print_status "💡 Common solutions:"
    print_status "   - Check for data type conflicts (e.g., Integer to UUID)"
    print_status "   - Verify table permissions: sudo ./scripts/grant_table_permissions.sh"
    print_status "   - Review migration file for syntax errors"
    handle_error "Failed to apply migrations"
fi

# Generate AI report using common function
ADDITIONAL_CONTENT="  \"migration_details\": {\n    \"validation_status\": \"$VALIDATION_STATUS\",\n    \"migration_created\": \"$MIGRATION_CREATED\",\n    \"migration_status\": \"$MIGRATION_STATUS\",\n    \"target_directory\": \"cream_api/\",\n    \"configuration\": \"alembic.ini\"\n  },"

generate_ai_report "migration" "$MIGRATION_STATUS" "0" "$AI_OUTPUT_DIR" "$ADDITIONAL_CONTENT"
