#!/bin/bash

# React Test Runner Script
# Runs frontend tests and generates reports for AI analysis
#
# SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>
# SPDX-License-Identifier: MIT

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Variable declarations
PROJECT_ROOT="$(get_project_root)"
FRONTEND_DIR="$PROJECT_ROOT/cream_ui"
AI_OUTPUT_DIR="$PROJECT_ROOT/ai/outputs/test_results"
SHOW_HELP=false
VERBOSE=false
WATCH_MODE=false
TEST_PATH=""

# Function to show usage information
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] [TEST_PATH]

Run React tests with enhanced flexibility and AI-friendly reporting.

OPTIONS:
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output
    -w, --watch         Run tests in watch mode
    -p, --path PATH     Run tests for specific path or pattern
    --coverage          Generate coverage report (default)
    --no-coverage       Skip coverage report

EXAMPLES:
    $0                    # Run all tests with coverage
    $0 -p "StockRequest"  # Run tests matching pattern
    $0 -p "src/components/stock-tracking"  # Run specific directory
    $0 -w                 # Run tests in watch mode
    $0 -v                 # Run with verbose output

EOF
}

# Function to validate React test environment
validate_react_environment() {
    print_status "Validating React test environment..."

    # Check if frontend directory exists
    if [[ ! -d "$FRONTEND_DIR" ]]; then
        handle_error "Frontend directory not found: $FRONTEND_DIR"
    fi

    # Check if package.json exists
    if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
        handle_error "package.json not found in frontend directory"
    fi

    # Check if node_modules exists
    if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
        handle_error "node_modules not found. Run 'yarn install' in $FRONTEND_DIR"
    fi

    # Check if vitest is available
    if [[ ! -f "$FRONTEND_DIR/node_modules/.bin/vitest" ]]; then
        handle_error "Vitest not found. Install with 'yarn add -D vitest'"
    fi

    print_success "Environment validation passed"
}

# Function to run React tests
run_react_tests() {
    local test_args=()
    local start_time=$(date +%s)

    # Build test arguments
    if [[ "$WATCH_MODE" == true ]]; then
        test_args+=("--watch")
    else
        test_args+=("--run")
    fi

    if [[ "$VERBOSE" == true ]]; then
        test_args+=("--reporter=verbose")
    else
        test_args+=("--coverage")
        test_args+=("--reporter=json")
        test_args+=("--outputFile=$AI_OUTPUT_DIR/react-test-results.json")
    fi

    # Add specific test path if provided
    if [[ -n "$TEST_PATH" ]]; then
        test_args+=("$TEST_PATH")
    fi

    print_status "Running React tests with args: ${test_args[*]}"

    # Change to frontend directory and run tests
    cd "$FRONTEND_DIR"

    # Run the test command
    local test_exit_code=0
    if yarn test "${test_args[@]}"; then
        print_success "React tests passed"
        test_exit_code=0
    else
        print_error "React tests failed"
        test_exit_code=1
    fi

    # Store duration for summary
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo "$duration" > "$AI_OUTPUT_DIR/react-test-duration.txt"

    return $test_exit_code
}

# Function to parse test results and display human summary
display_test_summary() {
    local test_results_file="$AI_OUTPUT_DIR/react-test-results.json"
    local duration_file="$AI_OUTPUT_DIR/react-test-duration.txt"

    if [[ ! -f "$test_results_file" ]]; then
        print_error "Test results file not found: $test_results_file"
        return 1
    fi

    # Parse test results using jq if available, otherwise use basic parsing
    if command -v jq >/dev/null 2>&1; then
        local total_tests=$(jq -r '.numTotalTests' "$test_results_file" 2>/dev/null || echo "0")
        local passed_tests=$(jq -r '.numPassedTests' "$test_results_file" 2>/dev/null || echo "0")
        local failed_tests=$(jq -r '.numFailedTests' "$test_results_file" 2>/dev/null || echo "0")
        local total_suites=$(jq -r '.numTotalTestSuites' "$test_results_file" 2>/dev/null || echo "0")
        local passed_suites=$(jq -r '.numPassedTestSuites' "$test_results_file" 2>/dev/null || echo "0")
        local failed_suites=$(jq -r '.numFailedTestSuites' "$test_results_file" 2>/dev/null || echo "0")
        local success=$(jq -r '.success' "$test_results_file" 2>/dev/null || echo "false")
    else
        # Basic parsing without jq
        local total_tests=$(grep -o '"numTotalTests":[0-9]*' "$test_results_file" | cut -d: -f2 || echo "0")
        local passed_tests=$(grep -o '"numPassedTests":[0-9]*' "$test_results_file" | cut -d: -f2 || echo "0")
        local failed_tests=$(grep -o '"numFailedTests":[0-9]*' "$test_results_file" | cut -d: -f2 || echo "0")
        local total_suites=$(grep -o '"numTotalTestSuites":[0-9]*' "$test_results_file" | cut -d: -f2 || echo "0")
        local passed_suites=$(grep -o '"numPassedTestSuites":[0-9]*' "$test_results_file" | cut -d: -f2 || echo "0")
        local failed_suites=$(grep -o '"numFailedTestSuites":[0-9]*' "$test_results_file" | cut -d: -f2 || echo "0")
        local success=$(grep -o '"success":true' "$test_results_file" >/dev/null && echo "true" || echo "false")
    fi

    # Get duration from our tracked file
    local duration=""
    if [[ -f "$duration_file" ]]; then
        local duration_sec=$(cat "$duration_file" 2>/dev/null || echo "0")
        if [[ "$duration_sec" =~ ^[0-9]+$ && "$duration_sec" -gt 0 ]]; then
            duration=" (${duration_sec}s)"
        fi
    fi

    # Display human-friendly summary
    echo
    echo "🧪 React Test Results Summary"
    echo "============================="

    if [[ "$success" == "true" ]]; then
        print_success "✅ All tests passed!"
    else
        print_error "❌ Some tests failed"
    fi

    echo
    echo "📊 Test Statistics:"
    echo "   • Test Suites: $passed_suites/$total_suites passed"
    echo "   • Tests:        $passed_tests/$total_tests passed"

    if [[ "$failed_tests" -gt 0 ]]; then
        echo "   • Failed:       $failed_tests tests"
    fi

    if [[ -n "$duration" ]]; then
        echo "   • Duration:     $duration"
    fi

    echo
    echo "📁 Test Path: ${TEST_PATH:-All tests}"
    echo "📄 Detailed results: $test_results_file"

    # Show failed test details if any
    if [[ "$failed_tests" -gt 0 && "$VERBOSE" == true ]]; then
        echo
        echo "❌ Failed Tests:"
        if command -v jq >/dev/null 2>&1; then
            jq -r '.testResults[] | select(.status == "failed") | .assertionResults[] | select(.status == "failed") | "   • " + .fullName + ": " + .failureMessages[0]' "$test_results_file" 2>/dev/null | head -10
        fi
    fi

    echo
}

# Function to generate AI-friendly test report
generate_test_report() {
    local test_results_file="$AI_OUTPUT_DIR/react-test-results.json"
    local report_file="$AI_OUTPUT_DIR/react-test-summary.json"

    if [[ ! -f "$test_results_file" ]]; then
        print_error "Test results file not found: $test_results_file"
        return 1
    fi

    print_status "Generating React test report: $report_file"

    # Create a comprehensive AI-friendly report
    cat > "$report_file" << EOF
{
  "ai_metadata": {
    "purpose": "React test results for AI consumption",
    "template_version": "1.0",
    "ai_processing_level": "Medium",
    "required_context": "React test execution environment and configuration",
    "validation_required": "No",
    "code_generation": "Not Supported",
    "cross_references": []
  },
  "file_info": {
    "file_path": "outputs/test_results/react-test-summary.json",
    "original_format": "json",
    "generated_at": "$(date -Iseconds)",
    "file_size": $(stat -c%s "$test_results_file" 2>/dev/null || echo 0),
    "line_count": $(wc -l < "$test_results_file" 2>/dev/null || echo 0)
  },
  "content": {
    "sections": [
      {
        "level": 1,
        "title": "React Test Report",
        "content": "Comprehensive React test execution results and analysis for AI consumption.",
        "subsections": []
      },
      {
        "level": 2,
        "title": "Execution Summary",
        "content": "**Status**: $(if [[ -f "$test_results_file" ]]; then echo "completed"; else echo "failed"; fi)\n**Duration**: $(if [[ -f "$test_results_file" ]]; then echo "completed"; else echo "failed"; fi)\n**Timestamp**: $(date -Iseconds)\n**Test Framework**: vitest\n**Frontend Directory**: $FRONTEND_DIR",
        "subsections": []
      },
      {
        "level": 2,
        "title": "Test Configuration",
        "content": "**Test Path**: '${TEST_PATH:-All tests}'\n**Verbose Mode**: $VERBOSE\n**Watch Mode**: $WATCH_MODE\n**Coverage**: $(if [[ "$VERBOSE" == true ]]; then echo "Disabled"; else echo "Enabled"; fi)\n**Reporter**: $(if [[ "$VERBOSE" == true ]]; then echo "verbose"; else echo "json"; fi)",
        "subsections": []
      }
    ],
    "code_blocks": [],
    "links": [],
    "raw_content": "React test execution completed with status: $(if [[ -f "$test_results_file" ]]; then echo "completed"; else echo "failed"; fi). Duration: completed. Test path: '${TEST_PATH:-All tests}'."
  },
  "cross_references": [],
  "code_generation_hints": [],
  "validation_rules": [],
  "optimization": {
    "version": "1.0",
    "generated_at": "$(date -Iseconds)",
    "improvements": []
  }
}
EOF

    print_success "Generated React test report: $report_file"
}

# Function to cleanup test environment
cleanup_test_environment() {
    print_status "Cleaning up React test environment"
    # Add any cleanup tasks here if needed
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -w|--watch)
            WATCH_MODE=true
            shift
            ;;
        -p|--path)
            TEST_PATH="$2"
            shift 2
            ;;
        --coverage)
            # Coverage is enabled by default, so just continue
            shift
            ;;
        --no-coverage)
            VERBOSE=true  # This will disable coverage
            shift
            ;;
        *)
            # Treat as test path if not already set
            if [[ -z "$TEST_PATH" ]]; then
                TEST_PATH="$1"
            else
                print_error "Unknown option: $1"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Main execution
main() {
    print_status "🧪 React Test Runner"
    print_status "===================="

    # Validate environment
    validate_react_environment

    # Create output directory
    mkdir -p "$AI_OUTPUT_DIR"

    # Run tests
    if run_react_tests; then
        print_success "✅ React tests passed"
    else
        print_error "❌ React tests failed"
    fi

    # Display human-friendly summary
    display_test_summary

    # Generate report
    generate_test_report

    # Cleanup
    cleanup_test_environment

    # Return appropriate exit code
    if [[ -f "$AI_OUTPUT_DIR/react-test-results.json" ]]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"
