#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$(dirname "$SCRIPT_DIR")/common.sh"
PROJECT_ROOT="$(get_project_root)"

# Get the project root and API directory
API_DIR="$PROJECT_ROOT/cream_api"
AI_OUTPUT_DIR="ai/outputs/migration_results"

# Parse command line arguments
DRY_RUN=false
FORCE=false
SHOW_HELP=false

while getopts "dfh" opt; do
    case $opt in
        d)
            DRY_RUN=true
            ;;
        f)
            FORCE=true
            ;;
        h)
            SHOW_HELP=true
            ;;
        \?)
            print_error "❌ Invalid option: -$OPTARG"
            echo "Usage: $0 [-d] [-f] [-h]"
            echo "  -d: Dry run (show what would be done without applying)"
            echo "  -f: Force mode (skip confirmations)"
            echo "  -h: Show this help message"
            exit 1
            ;;
    esac
done

# Show help if requested
if [ "$SHOW_HELP" = true ]; then
    show_usage "$(basename "$0")" \
        "Database migration script for CreamPie application" \
        "$0 [-d] [-f] [-h]"
    exit 0
fi

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
START_TIME=$(date +%s)

# Show current migration status
print_status "📊 Current migration status:"
if poetry run alembic current > /dev/null 2>&1; then
    CURRENT_REV=$(poetry run alembic current | awk '{print $1}')
    print_status "   Current revision: $CURRENT_REV"
else
    print_status "   No migrations applied yet"
fi

# Show pending migrations
print_status "📋 Pending migrations:"
PENDING_COUNT=$(poetry run alembic heads | wc -l)
if [ "$PENDING_COUNT" -gt 0 ]; then
    poetry run alembic heads | while read -r line; do
        print_status "   $line"
    done
else
    print_status "   No pending migrations"
fi

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
    print_status "   - Reset migration state: ./scripts/db/fix_migration_state.sh"
    print_status "   - Or drop all tables and start fresh"
    VALIDATION_STATUS="failed"
    MIGRATION_STATUS="failed"
    handle_error "Migration state validation failed. Please check the database connection and alembic_version table."
fi
print_success "✅ Migration state validation passed"

# Create new migration if there are changes
print_status "Checking for model changes..."
# Use alembic check to see if there are any changes that need migration
if poetry run alembic check > /dev/null 2>&1; then
    print_status "No model changes detected"
    MIGRATION_CREATED="no"
else
    # Show what changes would be made
    print_status "Model changes detected:"
    poetry run alembic check 2>&1 | grep -E "(add|remove|change)" | while read -r line; do
        print_status "   $line"
    done

    if [ "$DRY_RUN" = true ]; then
        print_status "🔍 Dry run mode - no migration will be created"
        MIGRATION_CREATED="no"
    else
        # There are changes, create migration
        if poetry run alembic revision --autogenerate -m "auto migration" > /dev/null 2>&1; then
            print_success "Created new migration with changes"
            MIGRATION_CREATED="yes"

            # Show the generated migration file
            LATEST_MIGRATION=$(poetry run alembic history --verbose | head -1 | awk '{print $1}')
            MIGRATION_FILE="$API_DIR/migrations/versions/${LATEST_MIGRATION}.py"
            print_status "📄 Generated migration: $MIGRATION_FILE"
        else
            print_error "Failed to create migration"
            MIGRATION_STATUS="failed"
            handle_error "Failed to create migration"
        fi
    fi
fi

# Apply all pending migrations
if [ "$DRY_RUN" = false ]; then
    print_status "Applying pending migrations..."
    if poetry run alembic upgrade head; then
        print_success "All migrations applied successfully"
    else
        MIGRATION_STATUS="failed"
        print_error "❌ Failed to apply migrations"
        print_status "💡 Common solutions:"
        print_status "   - Check for data type conflicts (e.g., Integer to UUID)"
        print_status "   - Verify table permissions: sudo ./scripts/db/grant_table_permissions.sh"
        print_status "   - Review migration file for syntax errors"
        print_status "   - Check database logs for specific error details"
        handle_error "Failed to apply migrations"
    fi
else
    print_status "🔍 Dry run mode - no migrations will be applied"
fi

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Generate AI report using common function
ADDITIONAL_CONTENT="  \"migration_details\": {\n    \"validation_status\": \"$VALIDATION_STATUS\",\n    \"migration_created\": \"$MIGRATION_CREATED\",\n    \"migration_status\": \"$MIGRATION_STATUS\",\n    \"dry_run\": \"$DRY_RUN\",\n    \"force_mode\": \"$FORCE\",\n    \"duration_seconds\": \"$DURATION\",\n    \"target_directory\": \"cream_api/\",\n    \"configuration\": \"alembic.ini\"\n  },"

generate_ai_report "migration" "$MIGRATION_STATUS" "$DURATION" "$AI_OUTPUT_DIR" "$ADDITIONAL_CONTENT"

# Final status
if [ "$MIGRATION_STATUS" = "success" ]; then
    if [ "$DRY_RUN" = true ]; then
        print_success "🎉 Migration check completed successfully in ${DURATION}s"
        print_status "Run without -d flag to apply migrations"
    else
        print_success "🎉 Migration completed successfully in ${DURATION}s"
    fi
else
    print_error "❌ Migration failed after ${DURATION}s"
    exit 1
fi
