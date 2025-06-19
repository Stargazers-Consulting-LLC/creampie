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

# Function to generate AI-consumable reports
# Usage: generate_ai_report "report_type" "status" "duration" "ai_output_dir" "additional_content"
generate_ai_report() {
    local report_type="$1"
    local status="$2"
    local duration="$3"
    local ai_output_dir="$4"
    local additional_content="$5"
    local timestamp=$(date -Iseconds)

    # Ensure AI output directory exists
    mkdir -p "$ai_output_dir"

    # Generate report filename
    local report_file="$ai_output_dir/${report_type}-report-$(date +%Y%m%d_%H%M%S).json"

    # Create JSON report
    cat > "$report_file" << EOF
{
  "ai_metadata": {
    "purpose": "${report_type} results for AI consumption",
    "template_version": "1.0",
    "ai_processing_level": "Medium",
    "required_context": "Script execution environment and configuration",
    "validation_required": "No",
    "code_generation": "Not Supported",
    "cross_references": []
  },
  "file_info": {
    "file_path": "outputs/$(basename "$(dirname "$ai_output_dir")")/$(basename "$report_file")",
    "original_format": "json",
    "generated_at": "$timestamp",
    "file_size": 0,
    "line_count": 0
  },
  "content": {
    "sections": [
      {
        "level": 1,
        "title": "${report_type^} Report",
        "content": "Comprehensive ${report_type} execution results and analysis for AI consumption.",
        "subsections": []
      },
      {
        "level": 2,
        "title": "Execution Summary",
        "content": "**Status**: $status\n**Duration**: ${duration}s\n**Timestamp**: $timestamp\n**Report Type**: $report_type",
        "subsections": []
      }
    ],
    "code_blocks": [],
    "links": [],
    "raw_content": "${report_type^} execution completed with status: $status. Duration: ${duration}s."
  },
  "cross_references": [],
  "code_generation_hints": [],
  "validation_rules": [],
  "optimization": {
    "version": "1.0",
    "generated_at": "$timestamp",
    "improvements": []
  }
}
EOF

    # Add additional content if provided
    if [[ -n "$additional_content" ]]; then
        # Insert additional content before the closing brace
        sed -i "s/  \"cross_references\": \[\],/  \"cross_references\": \[\],\n$additional_content/" "$report_file"
    fi

    # Update file size and line count
    local file_size=$(wc -c < "$report_file")
    local line_count=$(wc -l < "$report_file")

    # Update the JSON with actual values
    sed -i "s/\"file_size\": 0/\"file_size\": $file_size/" "$report_file"
    sed -i "s/\"line_count\": 0/\"line_count\": $line_count/" "$report_file"

    print_status "Generated AI ${report_type} report: $report_file"
}

# Function to kill a process by its command pattern
# Usage: kill_process "pattern" "process_name"
kill_process() {
    local pattern="$1"
    local process_name="$2"

    print_status "🔍 Searching for $process_name process..."

    # Find the process ID
    local PID=$(ps aux | grep "$pattern" | grep -v grep | awk '{print $2}')

    if [ -z "$PID" ]; then
        print_status "No $process_name process found running"
        return 0
    fi

    print_status "Found $process_name process with PID: $PID"
    print_status "🔄 Killing process..."

    # Kill the process
    if ! kill "$PID" 2>/dev/null; then
        print_error "Failed to kill $process_name process with PID: $PID"
        return 1
    fi

    # Check if process was killed
    if ps -p "$PID" > /dev/null 2>&1; then
        print_status "Process still running, forcing kill..."
        if ! kill -9 "$PID" 2>/dev/null; then
            print_error "Failed to force kill $process_name process with PID: $PID"
            return 1
        fi
    fi

    print_success "✅ $process_name process killed successfully"
    return 0
}

# Function to check if running as root
# Usage: check_root_privileges
check_root_privileges() {
    if [[ $EUID -ne 0 ]]; then
        print_error "❌ This script must be run as root (use sudo)."
        exit 1
    fi
}

# Function to roll back database migration
# Usage: rollback_migration [force_flag]
rollback_migration() {
    local force_flag="$1"

    print_status "🔄 Rolling back previous migration..."

    # Change to cream_api directory where alembic.ini is located
    pushd "$(get_project_root)/cream_api" > /dev/null || handle_error "Failed to change to cream_api directory"

    # Run alembic downgrade command
    if poetry run alembic downgrade -1; then
        print_success "✅ Successfully rolled back the previous migration"
    else
        print_error "❌ Failed to roll back migration"
        exit 1
    fi

    popd > /dev/null
}

# Function to show usage information with consistent formatting
# Usage: show_usage "script_name" "description" "usage_text"
show_usage() {
    local script_name="$1"
    local description="$2"
    local usage_text="$3"

    cat << EOF
$script_name

$description

Usage: $usage_text
EOF
}
