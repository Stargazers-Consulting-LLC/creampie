#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Header: Grant table permissions script
# This script grants SELECT, INSERT, UPDATE, and DELETE permissions on a given table to a specified PostgreSQL user.
# Usage: sudo ./grant_table_permissions.sh <table>
# Example: sudo ./grant_table_permissions.sh public.tracked_stock

# Database and user constants
DB_NAME="cream"
APP_USER="creamapp"

# Check if run as root
if [[ $EUID -ne 0 ]]; then
    print_error "❌ This script must be run as root (use sudo)."
    exit 1
fi

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 <table>

Grants SELECT, INSERT, UPDATE, and DELETE permissions on the specified table to the default PostgreSQL user.

Defaults:
  Database: $DB_NAME
  User:     $APP_USER

Arguments:
  <table>      The table name (optionally schema-qualified, e.g., public.tracked_stock)

Example:
  sudo $0 public.tracked_stock
EOF
}

# Validate arguments
if [ $# -ne 1 ]; then
    print_error "❌ Invalid number of arguments."
    show_usage
    exit 1
fi

TABLE_NAME="$1"

print_status "🔄 Granting permissions on table '$TABLE_NAME' in database '$DB_NAME' to user '$APP_USER'..."

# Grant permissions using psql as the postgres user
run_command "sudo -u postgres psql -d \"$DB_NAME\" -c \"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE $TABLE_NAME TO $APP_USER;\""

print_success "✅ Permissions granted to user '$APP_USER' on table '$TABLE_NAME' in database '$DB_NAME'."
