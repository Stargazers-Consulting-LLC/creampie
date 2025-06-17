#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Get project root directory
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Parse command line arguments
FORCE=false
while getopts "f" opt; do
    case $opt in
        f)
            FORCE=true
            ;;
        \?)
            print_error "❌ Invalid option: -$OPTARG"
            exit 1
            ;;
    esac
done

# Function to roll back migration
rollback_migration() {
    print_status "🔄 Rolling back previous migration..."

    # Change to cream_api directory where alembic.ini is located
    pushd "$PROJECT_ROOT/cream_api" > /dev/null || handle_error "Failed to change to cream_api directory"

    # Run alembic downgrade command
    if poetry run alembic downgrade -1; then
        print_success "✅ Successfully rolled back the previous migration"
    else
        print_error "❌ Failed to roll back migration"
        exit 1
    fi

    popd > /dev/null
}

# Main script execution
if confirm_action "This will roll back the previous database migration." $([ "$FORCE" = true ] && echo "-f"); then
    rollback_migration
fi
