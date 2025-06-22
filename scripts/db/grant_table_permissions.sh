#!/bin/bash

# =============================================================================
# Script: grant_table_permissions.sh
# Description: Grant necessary database permissions for the CreamPie application
# Usage: sudo ./scripts/db/grant_table_permissions.sh
# Author: CreamPie Development Team
# Version: 2.0
# Dependencies: PostgreSQL, psql, sudo access
# Exit Codes: 0=Success, 1=Error
# Environment Variables: DB_NAME, DB_USER, DB_HOST, DB_PORT
# =============================================================================

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$(dirname "$SCRIPT_DIR")/common.sh"
PROJECT_ROOT="$(get_project_root)"

# Get project root directory
AI_OUTPUT_DIR="$PROJECT_ROOT/ai/outputs/database_operations"

# Strict mode for error handling
set -euo pipefail

# Configuration
DB_NAME=${DB_NAME:-"cream"}
DB_USER=${DB_USER:-"creamapp"}
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}

# Initialize status variables
PERMISSION_STATUS="success"
VALIDATION_STATUS="success"
GRANT_STATUS="success"

# Functions
# =============================================================================

validate_environment() {
    print_status "🔍 Validating environment..."

    # Check if psql is available
    if ! command -v psql &> /dev/null; then
        VALIDATION_STATUS="failed"
        handle_error "psql command not found. Please install PostgreSQL client."
    fi

    # Check if postgres user exists
    if ! id "postgres" &> /dev/null; then
        VALIDATION_STATUS="failed"
        handle_error "postgres user not found. Please ensure PostgreSQL is properly installed."
    fi

    print_success "✅ Environment validation passed"
}

grant_all_permissions() {
    print_status "📋 Granting all permissions in a single database session..."

    if ! sudo -u postgres psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" << 'EOF'
-- Grant USAGE on the public schema (needed to see tables)
GRANT USAGE ON SCHEMA public TO creamapp;

-- Grant permissions on all application tables
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE stock_data TO creamapp;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE tracked_stock TO creamapp;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_users TO creamapp;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE sessions TO creamapp;

-- Grant permissions on all other sequences
DO $$
DECLARE
    seq_record RECORD;
BEGIN
    FOR seq_record IN
        SELECT sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema = 'public'
    LOOP
        EXECUTE 'GRANT USAGE ON SEQUENCE ' || seq_record.sequence_name || ' TO creamapp';
    END LOOP;
END $$;

-- Show granted permissions for verification
\echo 'Permissions granted successfully!'
\echo 'Schema: USAGE on public schema'
\echo 'Tables with full permissions: stock_data, tracked_stock, app_users, sessions'
\echo 'Sequences with USAGE permission: all public sequences'
EOF
    then
        GRANT_STATUS="failed"
        PERMISSION_STATUS="failed"
        handle_error "Failed to grant database permissions"
    fi
}

# Main Script
# =============================================================================

main() {
    print_status "🚀 Starting database permission grant process..."
    print_status "Database: $DB_NAME"
    print_status "User: $DB_USER"
    print_status "Host: $DB_HOST:$DB_PORT"
    echo ""

    # Validate environment
    validate_environment

    # Grant all permissions in a single database session
    grant_all_permissions

    echo ""
    print_success "✅ Permissions granted successfully!"
    print_success "The CreamPie application should now work without permission errors."
    echo ""
    print_status "📊 Granted permissions:"
    print_status "  - SELECT, INSERT, UPDATE, DELETE on all tables"
    print_status "  - USAGE on all sequences"
    print_status "  - Tables: stock_data, tracked_stock, app_users, sessions"

    # Generate AI report
    ADDITIONAL_CONTENT="  \"database_permission_details\": {\n    \"validation_status\": \"$VALIDATION_STATUS\",\n    \"grant_status\": \"$GRANT_STATUS\",\n    \"permission_status\": \"$PERMISSION_STATUS\",\n    \"database_name\": \"$DB_NAME\",\n    \"database_user\": \"$DB_USER\",\n    \"database_host\": \"$DB_HOST\",\n    \"database_port\": \"$DB_PORT\",\n    \"tables_affected\": [\"stock_data\", \"tracked_stock\", \"app_users\", \"sessions\"]\n  },"

    generate_ai_report "database_permissions" "$PERMISSION_STATUS" "0" "$AI_OUTPUT_DIR" "$ADDITIONAL_CONTENT"
}

# Validation
# =============================================================================

# Check if running as root
check_root_privileges

# Run main function
main
