#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${2}${1}${NC}"
}

print_status() {
    print_message "$1" "$WHITE"
}

print_success() {
    print_message "$1" "$GREEN"
}

print_error() {
    print_message "$1" "$RED"
}

# Function to handle errors
handle_error() {
    print_error "Error: $1"
    exit 1
}

# Function to run a command and handle errors
run_command() {
    if ! eval "$1"; then
        print_error "Failed: $1"
        exit 1
    fi
}

# Get the directory where the script is located
get_script_dir() {
    cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd
}

# Get the project root directory
get_project_root() {
    dirname "$(get_script_dir)"
}

# Function to confirm an action
# Usage: confirm_action "Warning message" [-f]
# Returns 0 if confirmed, 1 if not
confirm_action() {
    local message="$1"
    local force=false

    # Check for force flag
    if [[ "$2" == "-f" ]]; then
        force=true
    fi

    if [ "$force" = true ]; then
        return 0
    fi

    print_status "⚠️  $message"
    read -p "Are you sure you want to continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "❌ Operation cancelled by user"
        return 1
    fi
    return 0
}
