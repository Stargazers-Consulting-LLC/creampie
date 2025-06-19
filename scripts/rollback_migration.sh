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

# Main script execution
if confirm_action "This will roll back the previous database migration." $([ "$FORCE" = true ] && echo "-f"); then
    rollback_migration
fi
