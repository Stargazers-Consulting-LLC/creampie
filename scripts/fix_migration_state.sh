#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Get project root directory
PROJECT_ROOT="$(get_project_root)"
AI_OUTPUT_DIR="$PROJECT_ROOT/ai/outputs/migration_results"

# Parse command line arguments
FORCE=false
while getopts "f" opt; do
    case $opt in
        f)
            FORCE=true
            ;;
        \?)
            print_error "❌ Invalid option: -$OPTARG"
            echo "Usage: $0 [-f]"
            echo "  -f: Force mode (skip confirmation)"
            exit 1
            ;;
    esac
done

# Initialize status variables
FIX_STATUS="success"

# Main script execution
if confirm_action "This will drop the alembic_version table and reset migration state to start fresh." $([ "$FORCE" = true ] && echo "-f"); then
    print_status "🔧 Dropping alembic_version table..."

    # Change to cream_api directory where alembic.ini is located
    pushd "$PROJECT_ROOT/cream_api" > /dev/null || handle_error "Failed to change to cream_api directory"

    # Drop the alembic_version table
    print_status "Dropping alembic_version table..."
    if poetry run python -c "
import asyncio
from sqlalchemy import text
from cream_api.db import async_engine

async def drop_alembic_version():
    async with async_engine.begin() as conn:
        await conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
        print('Dropped alembic_version table')

asyncio.run(drop_alembic_version())
"; then
        print_success "✅ Dropped alembic_version table"
    else
        print_error "❌ Failed to drop alembic_version table"
        FIX_STATUS="failed"
    fi

    popd > /dev/null

    # Generate AI report
    ADDITIONAL_CONTENT="  \"migration_fix_details\": {\n    \"fix_status\": \"$FIX_STATUS\",\n    \"force_flag\": \"$FORCE\",\n    \"action\": \"dropped_alembic_version_table\",\n    \"target_directory\": \"cream_api/\",\n    \"configuration\": \"alembic.ini\"\n  },"

    generate_ai_report "migration_fix" "$FIX_STATUS" "0" "$AI_OUTPUT_DIR" "$ADDITIONAL_CONTENT"

    if [ "$FIX_STATUS" = "success" ]; then
        print_success "🎉 Migration state reset successfully!"
        print_status "You can now run: ./scripts/migrate.sh"
        exit 0
    else
        print_error "❌ Failed to reset migration state"
        exit 1
    fi
fi
