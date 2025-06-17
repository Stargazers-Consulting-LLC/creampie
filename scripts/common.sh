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
