#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Get the project root and API directory
PROJECT_ROOT="$(get_project_root)"
API_DIR="$PROJECT_ROOT/cream_api"

# Check if we're in the right directory
if [ ! -f "$API_DIR/alembic.ini" ]; then
    handle_error "alembic.ini not found in $API_DIR"
fi

# Change to the API directory
cd "$API_DIR" || handle_error "Failed to change to $API_DIR"

# Create new migration if there are changes
print_status "Checking for model changes..."
if poetry run alembic revision --autogenerate -m "auto migration" > /dev/null 2>&1; then
    print_success "Created new migration"
else
    print_success "No new migrations needed"
fi

# Apply all pending migrations
print_status "Applying pending migrations..."
if poetry run alembic upgrade head; then
    print_success "All migrations applied successfully"
else
    handle_error "Failed to apply migrations"
fi
