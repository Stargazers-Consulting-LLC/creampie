# Shell Style Guide

> This guide provides comprehensive patterns and best practices for shell scripting and command-line operations. Use these patterns to create reliable, maintainable shell scripts.

## Table of Contents

1. [Script Structure](#script-structure)
2. [Error Handling](#error-handling)
3. [Logging and Output](#logging-and-output)
4. [File and Directory Operations](#file-and-directory-operations)
5. [Process Management](#process-management)
6. [Configuration Management](#configuration-management)
7. [Command Line Arguments](#command-line-arguments)
8. [Security Best Practices](#security-best-practices)
9. [Testing and Validation](#testing-and-validation)
10. [Documentation Standards](#documentation-standards)

## Script Structure

### Header and Metadata

Every script should begin with a comprehensive header that includes:

```bash
#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Header: Script Name and Purpose
# This script [brief description of what the script does]
# Usage: [usage pattern]
# Example: [example command]
```

### Script Organization

Organize your script into clear sections:

```bash
# =============================================================================
# CONFIGURATION
# =============================================================================

# Default values and constants
readonly DEFAULT_VALUE="default"
readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration variables
CONFIG_VALUE="${CONFIG_VALUE:-$DEFAULT_VALUE}"

# =============================================================================
# FUNCTIONS
# =============================================================================

# Function definitions go here

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

# Input validation functions

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

# Core business logic functions

# =============================================================================
# MAIN SCRIPT
# =============================================================================

# Main execution logic
```

## Error Handling

### Strict Mode Settings

Always use strict mode for robust error handling:

```bash
#!/bin/bash

# Strict mode settings
set -euo pipefail  # Exit on error, undefined vars, pipe failures
set -o errtrace    # ERR trap is inherited by shell functions
set -o functrace   # DEBUG and RETURN traps are inherited by shell functions

# Error handling
trap 'error_exit $? "Error on line $LINENO"' ERR
```

### Error Handling Functions

Implement comprehensive error handling:

```bash
# Function to handle errors
error_exit() {
    local exit_code="${1:-1}"
    local error_message="${2:-Unknown error occurred}"

    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $error_message" >&2
    echo "[ERROR] Exit code: $exit_code" >&2

    # Log error details
    if [[ -n "${BASH_VERSION:-}" ]]; then
        echo "[ERROR] Bash version: $BASH_VERSION" >&2
        echo "[ERROR] Script: ${BASH_SOURCE[0]}" >&2
        echo "[ERROR] Line: $LINENO" >&2
    fi

    exit "$exit_code"
}

# Cleanup function
cleanup() {
    local exit_code=$?

    echo "[INFO] Cleaning up..."

    # Add cleanup logic here
    # - Remove temporary files
    # - Stop background processes
    # - Close file descriptors

    if [[ $exit_code -ne 0 ]]; then
        echo "[WARN] Script exited with code: $exit_code"
    fi

    echo "[INFO] Cleanup completed"
}

# Set up traps
trap cleanup EXIT
trap 'error_exit 1 "Script interrupted"' INT TERM
```

### Input Validation

Always validate inputs before processing:

```bash
# Validate required arguments
validate_required_args() {
    local required_args=("$@")
    local missing_args=()

    for arg in "${required_args[@]}"; do
        if [[ -z "${!arg:-}" ]]; then
            missing_args+=("$arg")
        fi
    done

    if [[ ${#missing_args[@]} -gt 0 ]]; then
        error_exit 2 "Missing required arguments: ${missing_args[*]}"
    fi
}

# Validate file existence
validate_file_exists() {
    local file_path="$1"
    local description="${2:-File}"

    if [[ ! -f "$file_path" ]]; then
        error_exit 4 "$description does not exist: $file_path"
    fi

    if [[ ! -r "$file_path" ]]; then
        error_exit 4 "$description is not readable: $file_path"
    fi
}

# Validate directory existence
validate_directory_exists() {
    local dir_path="$1"
    local description="${2:-Directory}"

    if [[ ! -d "$dir_path" ]]; then
        error_exit 4 "$description does not exist: $dir_path"
    fi

    if [[ ! -r "$dir_path" ]]; then
        error_exit 4 "$description is not readable: $dir_path"
    fi
}

# Validate command availability
validate_command() {
    local command_name="$1"

    if ! command -v "$command_name" >/dev/null 2>&1; then
        error_exit 3 "Required command not found: $command_name"
    fi
}
```

## Logging and Output

### Color-Coded Output

Use consistent color coding for different message types:

```bash
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
```

### Logging Functions

Implement configurable logging levels:

```bash
# Logging configuration
readonly LOG_LEVELS=("DEBUG" "INFO" "WARN" "ERROR")
readonly DEFAULT_LOG_LEVEL="INFO"
LOG_LEVEL="${LOG_LEVEL:-$DEFAULT_LOG_LEVEL}"

# Validate log level
validate_log_level() {
    local valid_level=false
    for level in "${LOG_LEVELS[@]}"; do
        if [[ "$LOG_LEVEL" == "$level" ]]; then
            valid_level=true
            break
        fi
    done

    if [[ "$valid_level" == false ]]; then
        error_exit 2 "Invalid log level: $LOG_LEVEL. Valid levels: ${LOG_LEVELS[*]}"
    fi
}

# Logging functions
log_debug() {
    if [[ "$LOG_LEVEL" == "DEBUG" ]]; then
        echo "[DEBUG] $(date '+%Y-%m-%d %H:%M:%S') - $*"
    fi
}

log_info() {
    if [[ "$LOG_LEVEL" == "DEBUG" || "$LOG_LEVEL" == "INFO" ]]; then
        echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $*"
    fi
}

log_warn() {
    if [[ "$LOG_LEVEL" == "DEBUG" || "$LOG_LEVEL" == "INFO" || "$LOG_LEVEL" == "WARN" ]]; then
        echo "[WARN] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
    fi
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}
```

## File and Directory Operations

### Safe File Operations

Always use safe file operations with proper validation:

```bash
# Create directory safely
create_directory() {
    local dir_path="$1"
    local description="${2:-Directory}"

    if [[ ! -d "$dir_path" ]]; then
        log_info "Creating $description: $dir_path"
        if ! mkdir -p "$dir_path"; then
            error_exit 4 "Failed to create $description: $dir_path"
        fi
    else
        log_debug "$description already exists: $dir_path"
    fi
}

# Copy file safely
copy_file() {
    local source="$1"
    local destination="$2"
    local description="${3:-File}"

    validate_file_exists "$source" "Source $description"

    log_info "Copying $description: $source -> $destination"
    if ! cp "$source" "$destination"; then
        error_exit 4 "Failed to copy $description: $source -> $destination"
    fi
}

# Move file safely
move_file() {
    local source="$1"
    local destination="$2"
    local description="${3:-File}"

    validate_file_exists "$source" "Source $description"

    log_info "Moving $description: $source -> $destination"
    if ! mv "$source" "$destination"; then
        error_exit 4 "Failed to move $description: $source -> $destination"
    fi
}

# Remove file safely
remove_file() {
    local file_path="$1"
    local description="${2:-File}"

    if [[ -f "$file_path" ]]; then
        log_info "Removing $description: $file_path"
        if ! rm "$file_path"; then
            error_exit 4 "Failed to remove $description: $file_path"
        fi
    else
        log_debug "$description does not exist: $file_path"
    fi
}

# Create backup
create_backup() {
    local file_path="$1"
    local backup_suffix="${2:-.backup.$(date +%Y%m%d_%H%M%S)}"

    if [[ -f "$file_path" ]]; then
        local backup_path="$file_path$backup_suffix"
        log_info "Creating backup: $file_path -> $backup_path"
        copy_file "$file_path" "$backup_path" "backup"
    fi
}
```

## Process Management

### Command Execution

Implement safe command execution with error handling:

```bash
# Execute command with error handling
execute_command() {
    local command="$1"
    local description="${2:-Command}"
    local exit_on_error="${3:-true}"

    log_debug "Executing $description: $command"

    if eval "$command"; then
        log_debug "$description completed successfully"
        return 0
    else
        local exit_code=$?
        log_error "$description failed with exit code: $exit_code"

        if [[ "$exit_on_error" == "true" ]]; then
            error_exit "$exit_code" "$description failed"
        fi

        return "$exit_code"
    fi
}

# Execute command and capture output
execute_command_output() {
    local command="$1"
    local description="${2:-Command}"
    local capture_stderr="${3:-false}"

    log_debug "Executing $description: $command"

    local output
    local exit_code

    if [[ "$capture_stderr" == "true" ]]; then
        output=$(eval "$command" 2>&1)
        exit_code=$?
    else
        output=$(eval "$command")
        exit_code=$?
    fi

    if [[ $exit_code -eq 0 ]]; then
        log_debug "$description completed successfully"
        echo "$output"
        return 0
    else
        log_error "$description failed with exit code: $exit_code"
        if [[ "$capture_stderr" == "true" ]]; then
            echo "$output" >&2
        fi
        return "$exit_code"
    fi
}
```

### Process Control

Manage background processes safely:

```bash
# Run command in background
run_background() {
    local command="$1"
    local description="${2:-Background process}"
    local log_file="${3:-/dev/null}"

    log_info "Starting $description in background"

    if nohup eval "$command" > "$log_file" 2>&1 &; then
        local pid=$!
        log_info "$description started with PID: $pid"
        echo "$pid"
    else
        error_exit 1 "Failed to start $description"
    fi
}

# Wait for process
wait_for_process() {
    local pid="$1"
    local timeout="${2:-30}"
    local description="${3:-Process}"

    log_info "Waiting for $description (PID: $pid, timeout: ${timeout}s)"

    local elapsed=0
    while kill -0 "$pid" 2>/dev/null && [[ $elapsed -lt $timeout ]]; do
        sleep 1
        ((elapsed++))
    done

    if kill -0 "$pid" 2>/dev/null; then
        log_warn "$description (PID: $pid) did not complete within timeout"
        return 1
    else
        log_info "$description (PID: $pid) completed"
        return 0
    fi
}

# Kill process safely
kill_process() {
    local pid="$1"
    local description="${2:-Process}"
    local timeout="${3:-10}"

    if ! kill -0 "$pid" 2>/dev/null; then
        log_debug "$description (PID: $pid) is not running"
        return 0
    fi

    log_info "Stopping $description (PID: $pid)"

    # Try graceful shutdown first
    kill "$pid"

    # Wait for graceful shutdown
    local elapsed=0
    while kill -0 "$pid" 2>/dev/null && [[ $elapsed -lt $timeout ]]; do
        sleep 1
        ((elapsed++))
    done

    # Force kill if still running
    if kill -0 "$pid" 2>/dev/null; then
        log_warn "Force killing $description (PID: $pid)"
        kill -9 "$pid"
        sleep 1

        if kill -0 "$pid" 2>/dev/null; then
            error_exit 1 "Failed to kill $description (PID: $pid)"
        fi
    fi

    log_info "$description (PID: $pid) stopped"
}
```

## Configuration Management

### Configuration Loading

Load and validate configuration safely:

```bash
# Load configuration from file
load_config() {
    local config_file="$1"
    local description="${2:-Configuration}"

    validate_file_exists "$config_file" "$description file"

    log_info "Loading $description from: $config_file"

    # Source the configuration file
    if ! source "$config_file"; then
        error_exit 4 "Failed to load $description from: $config_file"
    fi

    log_debug "$description loaded successfully"
}

# Load environment variables from file
load_env_file() {
    local env_file="$1"

    if [[ -f "$env_file" ]]; then
        log_info "Loading environment variables from: $env_file"

        # Read and export environment variables
        while IFS= read -r line; do
            # Skip comments and empty lines
            if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]]; then
                continue
            fi

            # Export variable if it's a valid assignment
            if [[ "$line" =~ ^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*= ]]; then
                export "$line"
                log_debug "Exported: $line"
            fi
        done < "$env_file"
    else
        log_warn "Environment file not found: $env_file"
    fi
}

# Validate configuration
validate_config() {
    local required_vars=("$@")
    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        error_exit 4 "Missing required configuration variables: ${missing_vars[*]}"
    fi

    log_info "Configuration validation passed"
}

# Set default values
set_defaults() {
    local defaults=("$@")

    for default in "${defaults[@]}"; do
        IFS='=' read -r var_name default_value <<< "$default"
        if [[ -z "${!var_name:-}" ]]; then
            export "$var_name"="$default_value"
            log_debug "Set default for $var_name: $default_value"
        fi
    done
}
```

## Command Line Arguments

### Argument Parsing

Implement robust command line argument parsing:

```bash
# Function to show usage information
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

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            SHOW_HELP=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -*)
            # Unknown option
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            # Positional argument
            if [[ -z "$POSITIONAL_ARG" ]]; then
                POSITIONAL_ARG="$1"
            else
                print_error "Too many arguments provided"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Show help if requested
if [ "$SHOW_HELP" = true ]; then
    show_usage
    exit 0
fi
```

### Confirmation Prompts

Implement safe confirmation prompts:

```bash
# Function to confirm an action
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
```

## Security Best Practices

### Input Validation

Always validate and sanitize inputs:

```bash
# Validate numeric input
validate_numeric() {
    local value="$1"
    local description="${2:-Value}"

    if [[ ! "$value" =~ ^[0-9]+$ ]]; then
        error_exit 2 "$description must be a positive integer: $value"
    fi
}

# Validate boolean input
validate_boolean() {
    local value="$1"
    local description="${2:-Value}"

    case "$value" in
        true|false|0|1|yes|no)
            return 0
            ;;
        *)
            error_exit 2 "$description must be a boolean value: $value"
            ;;
    esac
}

# Validate file path (prevent directory traversal)
validate_safe_path() {
    local path="$1"
    local description="${2:-Path}"

    # Check for directory traversal attempts
    if [[ "$path" =~ \.\. ]]; then
        error_exit 2 "$description contains directory traversal: $path"
    fi

    # Check for absolute paths if not allowed
    if [[ "$path" =~ ^/ ]]; then
        error_exit 2 "$description must be a relative path: $path"
    fi
}
```

### Privilege Checking

Check for required privileges:

```bash
# Function to check if running as root
check_root_privileges() {
    if [[ $EUID -ne 0 ]]; then
        print_error "❌ This script must be run as root (use sudo)."
        exit 1
    fi
}

# Function to check if running as specific user
check_user_privileges() {
    local required_user="$1"

    if [[ "$(whoami)" != "$required_user" ]]; then
        print_error "❌ This script must be run as user: $required_user"
        exit 1
    fi
}
```

## Testing and Validation

### Dependency Checking

Always check for required dependencies:

```bash
# Validate dependencies
validate_dependencies() {
    local missing_deps=()

    for dep in "$@"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            missing_deps+=("$dep")
        fi
    done

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error_exit 3 "Missing dependencies: ${missing_deps[*]}"
    fi

    log_info "All dependencies are available"
}
```

### Environment Validation

Validate the execution environment:

```bash
# Validate environment
validate_environment() {
    local valid_envs=("$@")
    local current_env="${ENVIRONMENT:-unknown}"
    local env_valid=false

    for env in "${valid_envs[@]}"; do
        if [[ "$current_env" == "$env" ]]; then
            env_valid=true
            break
        fi
    done

    if [[ "$env_valid" == false ]]; then
        error_exit 2 "Invalid environment: $current_env. Valid options: ${valid_envs[*]}"
    fi

    log_info "Environment validation passed: $current_env"
}
```

## Documentation Standards

### Script Documentation

Every script should include comprehensive documentation:

```bash
#!/bin/bash
#
# Script Name: script_name.sh
# Description: Brief description of what the script does
# Author: [Author Name]
# Version: 1.0.0
# Created: YYYY-MM-DD
# Last Modified: YYYY-MM-DD
#
# Usage: ./script_name.sh [OPTIONS] [ARGUMENTS]
# Example: ./script_name.sh --verbose input_file
#
# Dependencies:
#   - command1
#   - command2
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Invalid arguments
#   3 - Dependency missing
#   4 - Configuration error
#
# Environment Variables:
#   VAR_NAME - Description of the variable
#
```

### Function Documentation

Document all functions with clear descriptions:

```bash
# Function to do something
# Usage: function_name "arg1" "arg2"
# Arguments:
#   arg1 - Description of first argument
#   arg2 - Description of second argument
# Returns: 0 on success, non-zero on failure
# Example: function_name "value1" "value2"
function_name() {
    local arg1="$1"
    local arg2="$2"

    # Function implementation
}
```

## File Naming Conventions

### Script Files
- Use lowercase with underscores for all shell scripts
- Example: `deploy_application.sh`, `health_check.sh`, `update_documentation.sh`
- No spaces, hyphens, or special characters in script filenames
- This ensures cross-platform compatibility and consistent execution

### Output Files
- Generated files should use descriptive names with timestamps when appropriate
- Example: `healthcheck-result.json`, `deployment-log-20250618.txt`
- Use hyphens for readability in output filenames

### Configuration Files
- Use lowercase with underscores or hyphens for config files
- Example: `app_config.json`, `deployment-config.sh`
- Be consistent within each project

### Log Files
- Use descriptive names with timestamps
- Example: `deployment-20250618-143022.log`
- Include date and time for easy identification

## Implementation Guidelines

### For Developers
1. **Follow these patterns** for all shell script implementation
2. **Use strict mode** with proper error handling
3. **Include comprehensive logging** with configurable levels
4. **Validate all inputs** and dependencies
5. **Implement proper cleanup** and signal handling
6. **Use safe file operations** with validation
7. **Include proper documentation** and usage examples
8. **Follow security best practices** for all operations

### Quality Checklist
Before implementing shell scripts, ensure:
- [ ] Strict mode is enabled with proper error handling
- [ ] Comprehensive logging is implemented with configurable levels
- [ ] All inputs and dependencies are validated
- [ ] Proper cleanup and signal handling is implemented
- [ ] File operations are safe with proper validation
- [ ] Documentation includes usage examples and exit codes
- [ ] Security best practices are followed
- [ ] Scripts are idempotent and safe to re-run

## Examples

### Complete Script Example

```bash
#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Header: Example Script
# This script demonstrates proper shell script structure and patterns
# Usage: ./example_script.sh [OPTIONS] [INPUT_FILE]
# Example: ./example_script.sh --verbose data.txt

# =============================================================================
# CONFIGURATION
# =============================================================================

# Default values
readonly DEFAULT_INPUT_FILE="default.txt"
readonly DEFAULT_LOG_LEVEL="INFO"

# Configuration variables
INPUT_FILE="${INPUT_FILE:-$DEFAULT_INPUT_FILE}"
LOG_LEVEL="${LOG_LEVEL:-$DEFAULT_LOG_LEVEL}"

# =============================================================================
# FUNCTIONS
# =============================================================================

# Process the input file
process_file() {
    local file_path="$1"

    log_info "Processing file: $file_path"

    if [[ ! -f "$file_path" ]]; then
        error_exit 4 "Input file not found: $file_path"
    fi

    # Process the file
    while IFS= read -r line; do
        log_debug "Processing line: $line"
        # Add processing logic here
    done < "$file_path"

    log_success "File processing completed"
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

validate_inputs() {
    validate_file_exists "$INPUT_FILE" "Input file"
    validate_log_level
}

# =============================================================================
# MAIN SCRIPT
# =============================================================================

main() {
    # Set up signal handlers
    trap cleanup EXIT
    trap 'error_exit 1 "Script interrupted"' INT TERM

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--file)
                INPUT_FILE="$2"
                shift 2
                ;;
            -v|--verbose)
                LOG_LEVEL="DEBUG"
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Validate inputs
    validate_inputs

    # Process the file
    process_file "$INPUT_FILE"

    log_success "Script completed successfully"
    exit 0
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

This style guide provides a comprehensive foundation for writing reliable, maintainable shell scripts. Follow these patterns consistently to ensure your scripts are robust, secure, and easy to maintain.
