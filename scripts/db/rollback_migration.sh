#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$PROJECT_ROOT/scripts/common.sh"

# Get project root directory
AI_OUTPUT_DIR="$PROJECT_ROOT/ai/outputs/migration_results"

# Parse command line arguments
FORCE=false
ROLLBACK_TO_BASE=false

while getopts "fb" opt; do
    case $opt in
        f)
            FORCE=true
            ;;
        b)
            ROLLBACK_TO_BASE=true
            ;;
        \?)
            print_error "❌ Invalid option: -$OPTARG"
            echo "Usage: $0 [-f] [-b]"
            echo "  -f: Force mode (skip confirmation)"
            echo "  -b: Rollback to base (all migrations)"
            echo "  (default: rollback 1 migration)"
            exit 1
            ;;
    esac
done

# Initialize status variables
ROLLBACK_STATUS="success"
ROLLBACK_TARGET=""

# Main script execution
if [ "$ROLLBACK_TO_BASE" = true ]; then
    ROLLBACK_TARGET="base"
    CONFIRM_MESSAGE="This will roll back ALL database migrations to base (empty database)."
else
    ROLLBACK_TARGET="1 migration"
    CONFIRM_MESSAGE="This will roll back the previous database migration."
fi

if confirm_action "$CONFIRM_MESSAGE" $([ "$FORCE" = true ] && echo "-f"); then
    print_status "🔄 Rolling back migrations..."

    # Change to cream_api directory where alembic.ini is located
    pushd "$PROJECT_ROOT/cream_api" > /dev/null || handle_error "Failed to change to cream_api directory"

    # Run alembic downgrade command
    if [ "$ROLLBACK_TO_BASE" = true ]; then
        print_status "Rolling back to base..."
        if poetry run alembic downgrade base; then
            print_success "✅ Successfully rolled back to base"
        else
            print_error "❌ Failed to roll back to base"
            ROLLBACK_STATUS="failed"
        fi
    else
        print_status "Rolling back 1 migration..."
        if poetry run alembic downgrade -1; then
            print_success "✅ Successfully rolled back the previous migration"
        else
            print_error "❌ Failed to roll back migration"
            ROLLBACK_STATUS="failed"
        fi
    fi

    popd > /dev/null

    # Generate AI report
    ADDITIONAL_CONTENT="  \"migration_rollback_details\": {\n    \"rollback_status\": \"$ROLLBACK_STATUS\",\n    \"force_flag\": \"$FORCE\",\n    \"rollback_target\": \"$ROLLBACK_TARGET\",\n    \"target_directory\": \"cream_api/\",\n    \"configuration\": \"alembic.ini\"\n  },"

    generate_ai_report "migration_rollback" "$ROLLBACK_STATUS" "0" "$AI_OUTPUT_DIR" "$ADDITIONAL_CONTENT"

    if [ "$ROLLBACK_STATUS" = "success" ]; then
        exit 0
    else
        exit 1
    fi
fi
