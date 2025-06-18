# Shell Style Guide

> **For AI Assistants**: This guide outlines best practices for shell scripting, including bash patterns, error handling, and automation. All patterns include validation rules and implementation guidance for robust shell scripts.

## AI Metadata

**Template Version:** 2.0
**AI Processing Level:** High
**Required Context:** Bash, shell scripting, Linux/Unix systems, automation
**Validation Required:** Yes
**Code Generation:** Supported

**Dependencies:**
- `../Core%20Principles.md` - Decision-making frameworks
- `../Language-Specific/Python%20Testing%20Guide.md` - Testing patterns
- `../../project_context/Architecture%20Overview.md` - System architecture
- `../../project_context/Common%20Patterns.md` - Project-specific patterns

**Validation Rules:**
- All scripts must include proper error handling and exit codes
- Scripts must use strict mode and fail-fast behavior
- All variables must be properly quoted and validated
- Scripts must include comprehensive logging and debugging
- All commands must be idempotent and safe to re-run

## Overview

**Document Purpose:** Shell scripting standards and best practices for the CreamPie project
**Scope:** Bash scripting, automation, deployment, and system administration
**Target Users:** AI assistants and developers writing shell scripts
**Last Updated:** Current

**AI Context:** This guide provides the foundational shell scripting patterns that must be followed for all automation and deployment tasks in the project. It ensures robust, maintainable, and secure shell scripts.

## 1. Script Structure

### Header and Metadata
```bash
#!/usr/bin/env bash
#
# Script Name: deploy_application.sh
# Description: Deploy the CreamPie application to production
# Author: AI Assistant
# Version: 1.0.0
# Created: 2024-01-01
# Last Modified: 2024-01-01
#
# Usage: ./deploy_application.sh [environment] [version]
# Example: ./deploy_application.sh production v1.2.3
#
# Dependencies:
#   - docker
#   - docker-compose
#   - git
#   - jq
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Invalid arguments
#   3 - Dependency missing
#   4 - Configuration error
#   5 - Deployment failed
#
# Environment Variables:
#   DEPLOY_ENV - Target environment (default: production)
#   APP_VERSION - Application version to deploy
#   LOG_LEVEL - Logging level (default: INFO)
#

set -euo pipefail  # Strict mode: exit on error, undefined vars, pipe failures
IFS=$'\n\t'        # Internal field separator for safer word splitting
```

**Code Generation Hint**: This header pattern will inform all shell script structure and metadata.

**Validation**: All scripts must include proper header documentation and strict mode settings.

### Script Organization
```bash
# =============================================================================
# CONFIGURATION
# =============================================================================

# Default values
readonly DEFAULT_ENV="production"
readonly DEFAULT_LOG_LEVEL="INFO"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration variables
DEPLOY_ENV="${DEPLOY_ENV:-$DEFAULT_ENV}"
LOG_LEVEL="${LOG_LEVEL:-$DEFAULT_LOG_LEVEL}"
APP_VERSION=""

# =============================================================================
# FUNCTIONS
# =============================================================================

# Logging functions
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_warn() {
    echo "[WARN] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

log_debug() {
    if [[ "$LOG_LEVEL" == "DEBUG" ]]; then
        echo "[DEBUG] $(date '+%Y-%m-%d %H:%M:%S') - $*"
    fi
}

# Error handling
error_exit() {
    local exit_code="${1:-1}"
    local error_message="${2:-Unknown error occurred}"
    log_error "$error_message"
    exit "$exit_code"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    # Add cleanup logic here
    log_info "Cleanup completed"
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

validate_dependencies() {
    local missing_deps=()

    for dep in docker docker-compose git jq; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            missing_deps+=("$dep")
        fi
    done

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error_exit 3 "Missing dependencies: ${missing_deps[*]}"
    fi

    log_info "All dependencies are available"
}

validate_environment() {
    local valid_envs=("development" "staging" "production")
    local env_valid=false

    for env in "${valid_envs[@]}"; do
        if [[ "$DEPLOY_ENV" == "$env" ]]; then
            env_valid=true
            break
        fi
    done

    if [[ "$env_valid" == false ]]; then
        error_exit 2 "Invalid environment: $DEPLOY_ENV. Valid options: ${valid_envs[*]}"
    fi

    log_info "Environment validation passed: $DEPLOY_ENV"
}

validate_version() {
    if [[ -z "$APP_VERSION" ]]; then
        error_exit 2 "Application version is required"
    fi

    # Validate version format (semantic versioning)
    if [[ ! "$APP_VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        error_exit 2 "Invalid version format: $APP_VERSION. Expected format: vX.Y.Z"
    fi

    log_info "Version validation passed: $APP_VERSION"
}

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

deploy_application() {
    log_info "Starting deployment to $DEPLOY_ENV environment"
    log_info "Deploying version: $APP_VERSION"

    # Add deployment logic here
    log_info "Deployment completed successfully"
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
            -e|--environment)
                DEPLOY_ENV="$2"
                shift 2
                ;;
            -v|--version)
                APP_VERSION="$2"
                shift 2
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  -e, --environment ENV  Target environment (default: production)"
                echo "  -v, --version VERSION  Application version to deploy"
                echo "  -h, --help            Show this help message"
                exit 0
                ;;
            *)
                error_exit 2 "Unknown option: $1"
                ;;
        esac
    done

    # Validate inputs
    validate_dependencies
    validate_environment
    validate_version

    # Execute main logic
    deploy_application

    log_info "Script completed successfully"
    exit 0
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

**Code Generation Hint**: This script structure pattern will inform all shell script organization and implementation.

**Validation**: All scripts must follow this structure with proper sections and error handling.

## 2. Error Handling Patterns

### Strict Mode and Safety
```bash
#!/usr/bin/env bash

# Strict mode settings
set -euo pipefail  # Exit on error, undefined vars, pipe failures
set -o errtrace    # ERR trap is inherited by shell functions
set -o functrace   # DEBUG and RETURN traps are inherited by shell functions

# Error handling
trap 'error_exit $? "Error on line $LINENO"' ERR

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

**Code Generation Hint**: This error handling pattern will inform all shell script error handling implementation.

**Validation**: All scripts must include proper error handling with traps and cleanup functions.

### Input Validation
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
```

**Code Generation Hint**: This validation pattern will inform all input validation implementation.

**Validation**: All scripts must include comprehensive input validation for all parameters and files.

## 3. Logging and Debugging

### Logging Functions
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

# Debug functions
debug_variables() {
    if [[ "$LOG_LEVEL" == "DEBUG" ]]; then
        echo "[DEBUG] Environment variables:"
        for var in "$@"; do
            echo "[DEBUG]   $var=${!var:-<unset>}"
        done
    fi
}

debug_command() {
    if [[ "$LOG_LEVEL" == "DEBUG" ]]; then
        echo "[DEBUG] Executing: $*"
    fi
    "$@"
}

# Progress indicator
show_progress() {
    local message="$1"
    local duration="${2:-2}"

    echo -n "$message"
    for i in $(seq 1 "$duration"); do
        echo -n "."
        sleep 0.5
    done
    echo " done"
}
```

**Code Generation Hint**: This logging pattern will inform all shell script logging implementation.

**Validation**: All scripts must include proper logging with configurable levels and debug functions.

## 4. File and Directory Operations

### Safe File Operations
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

# Find files safely
find_files() {
    local search_path="$1"
    local pattern="$2"
    local max_depth="${3:-3}"

    validate_directory_exists "$search_path" "Search directory"

    log_debug "Searching for files matching '$pattern' in $search_path (max depth: $max_depth)"

    local files=()
    while IFS= read -r -d '' file; do
        files+=("$file")
    done < <(find "$search_path" -maxdepth "$max_depth" -name "$pattern" -print0 2>/dev/null)

    echo "${files[@]}"
}
```

**Code Generation Hint**: This file operation pattern will inform all file and directory manipulation implementation.

**Validation**: All file operations must include proper validation and error handling.

## 5. Process and Command Management

### Command Execution
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

**Code Generation Hint**: This process management pattern will inform all command execution and process handling implementation.

**Validation**: All command execution must include proper error handling and process management.

## 6. Configuration Management

### Configuration Loading
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

**Code Generation Hint**: This configuration pattern will inform all configuration management implementation.

**Validation**: All configuration loading must include proper validation and default value handling.

## 7. Network and API Operations

### HTTP Requests
```bash
# Make HTTP GET request
http_get() {
    local url="$1"
    local headers="${2:-}"
    local timeout="${3:-30}"

    log_debug "Making GET request to: $url"

    local curl_opts=(
        "--silent"
        "--show-error"
        "--max-time" "$timeout"
        "--fail"
    )

    if [[ -n "$headers" ]]; then
        while IFS=':' read -r key value; do
            curl_opts+=("--header" "$key: $value")
        done <<< "$headers"
    fi

    if response=$(curl "${curl_opts[@]}" "$url" 2>&1); then
        log_debug "GET request successful"
        echo "$response"
        return 0
    else
        local exit_code=$?
        log_error "GET request failed: $response"
        return "$exit_code"
    fi
}

# Make HTTP POST request
http_post() {
    local url="$1"
    local data="$2"
    local content_type="${3:-application/json}"
    local headers="${4:-}"
    local timeout="${5:-30}"

    log_debug "Making POST request to: $url"

    local curl_opts=(
        "--silent"
        "--show-error"
        "--max-time" "$timeout"
        "--fail"
        "--header" "Content-Type: $content_type"
        "--data" "$data"
    )

    if [[ -n "$headers" ]]; then
        while IFS=':' read -r key value; do
            curl_opts+=("--header" "$key: $value")
        done <<< "$headers"
    fi

    if response=$(curl "${curl_opts[@]}" "$url" 2>&1); then
        log_debug "POST request successful"
        echo "$response"
        return 0
    else
        local exit_code=$?
        log_error "POST request failed: $response"
        return "$exit_code"
    fi
}

# Check if URL is accessible
check_url() {
    local url="$1"
    local timeout="${2:-10}"

    log_debug "Checking URL accessibility: $url"

    if curl --silent --show-error --max-time "$timeout" --fail --head "$url" >/dev/null 2>&1; then
        log_debug "URL is accessible: $url"
        return 0
    else
        log_debug "URL is not accessible: $url"
        return 1
    fi
}

# Wait for URL to become accessible
wait_for_url() {
    local url="$1"
    local timeout="${2:-60}"
    local interval="${3:-5}"
    local description="${4:-URL}"

    log_info "Waiting for $description to become accessible: $url"

    local elapsed=0
    while [[ $elapsed -lt $timeout ]]; do
        if check_url "$url" "$interval"; then
            log_info "$description is now accessible: $url"
            return 0
        fi

        sleep "$interval"
        ((elapsed += interval))
    done

    error_exit 1 "$description did not become accessible within timeout: $url"
}
```

**Code Generation Hint**: This network pattern will inform all HTTP request and network operation implementation.

**Validation**: All network operations must include proper error handling and timeout management.

## Implementation Guidelines

### For AI Assistants
1. **Follow these patterns** for all shell script implementation
2. **Use strict mode** with proper error handling
3. **Include comprehensive logging** with configurable levels
4. **Validate all inputs** and dependencies
5. **Implement proper cleanup** and signal handling
6. **Use safe file operations** with validation
7. **Include proper documentation** and usage examples
8. **Follow security best practices** for all operations

### For Human Developers
1. **Reference these patterns** when writing shell scripts
2. **Use strict mode** for robust error handling
3. **Include comprehensive logging** for debugging
4. **Validate all inputs** before processing
5. **Implement proper cleanup** for resource management
6. **Test scripts thoroughly** with different scenarios
7. **Follow security guidelines** for production scripts

## Quality Assurance

### Script Standards
- All scripts must use strict mode with proper error handling
- Scripts must include comprehensive logging and debugging
- All inputs must be validated before processing
- Scripts must be idempotent and safe to re-run
- Proper cleanup must be implemented for all resources

### Security Standards
- Scripts must not expose sensitive information in logs
- File permissions must be set appropriately
- Input validation must prevent command injection
- Environment variables must be properly sanitized
- Temporary files must be created securely

### Performance Standards
- Scripts must handle large files efficiently
- Background processes must be properly managed
- Resource cleanup must be timely and complete
- Timeouts must be set for all external operations
- Memory usage must be monitored and controlled

### Testing Standards
- Unit tests must be written for complex functions
- Integration tests must cover script workflows
- Error scenarios must be tested thoroughly
- Performance tests must be implemented
- Security tests must validate input handling

---

**AI Quality Checklist**: Before implementing shell scripts, ensure:
- [x] Strict mode is enabled with proper error handling
- [x] Comprehensive logging is implemented with configurable levels
- [x] All inputs and dependencies are validated
- [x] Proper cleanup and signal handling is implemented
- [x] File operations are safe with proper validation
- [x] Documentation includes usage examples and exit codes
- [x] Security best practices are followed
- [x] Scripts are idempotent and safe to re-run
