#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Get project root directory (parent of scripts directory)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Parse command line arguments
RUN_PYTHON=true
RUN_JS=true
AI_OUTPUT_DIR="$PROJECT_ROOT/ai/outputs/lint_results"

while [[ $# -gt 0 ]]; do
    case $1 in
        --python-only)
            RUN_JS=false
            shift
            ;;
        --js-only)
            RUN_PYTHON=false
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Usage: $0 [--python-only|--js-only]"
            exit 1
            ;;
    esac
done

print_status "🔍 Starting linting checks..."

# Ensure output directory exists
mkdir -p "$AI_OUTPUT_DIR"

PYTHON_STATUS="success"
JS_STATUS="success"
PYTHON_REPORTS=()
JS_REPORTS=()

# Function to generate individual linter report
generate_linter_report() {
    local tool_name="$1"
    local status="$2"
    local output="$3"
    local report_file="$AI_OUTPUT_DIR/${tool_name}_report.json"

    cat > "$report_file" << EOF
{
  "tool": "$tool_name",
  "status": "$status",
  "timestamp": "$(date -Iseconds)",
  "output": $(echo "$output" | jq -R .),
  "summary": {
    "errors": $(echo "$output" | grep -c "error\|Error\|ERROR" || echo "0"),
    "warnings": $(echo "$output" | grep -c "warning\|Warning\|WARNING" || echo "0"),
    "lines_processed": $(echo "$output" | wc -l)
  }
}
EOF

    print_status "📄 Generated $tool_name report: $report_file"
}

if [ "$RUN_PYTHON" = true ]; then
    print_status "📝 Running Python checks..."

    # Run autoflake on cream_api
    pushd "$PROJECT_ROOT/cream_api" > /dev/null
    print_status "Running autoflake..."
    AUTOFLUKE_OUTPUT=$(poetry run autoflake -i -r --remove-all-unused-imports --recursive --remove-unused-variables --in-place --quiet --exclude=__init__.py . 2>&1 || true)
    if [ $? -eq 0 ]; then
        print_success "✅ Autoflake completed!"
        generate_linter_report "autoflake" "success" "$AUTOFLUKE_OUTPUT"
    else
        PYTHON_STATUS="failed"
        print_error "❌ Autoflake failed!"
        generate_linter_report "autoflake" "failed" "$AUTOFLUKE_OUTPUT"
    fi
    popd > /dev/null

    # Run ruff check on entire project
    pushd "$PROJECT_ROOT" > /dev/null
    print_status "Running ruff check..."
    RUFF_CHECK_OUTPUT=$(poetry run ruff check --fix . 2>&1 || true)
    if [ $? -eq 0 ]; then
        print_success "✅ Ruff check completed!"
        generate_linter_report "ruff_check" "success" "$RUFF_CHECK_OUTPUT"
    else
        PYTHON_STATUS="failed"
        print_error "❌ Ruff check failed!"
        generate_linter_report "ruff_check" "failed" "$RUFF_CHECK_OUTPUT"
    fi

    # Run ruff format on entire project
    print_status "Running ruff format..."
    RUFF_FORMAT_OUTPUT=$(poetry run ruff format . 2>&1 || true)
    if [ $? -eq 0 ]; then
        print_success "✅ Ruff format completed!"
        generate_linter_report "ruff_format" "success" "$RUFF_FORMAT_OUTPUT"
    else
        PYTHON_STATUS="failed"
        print_error "❌ Ruff format failed!"
        generate_linter_report "ruff_format" "failed" "$RUFF_FORMAT_OUTPUT"
    fi
    popd > /dev/null

    # Run mypy on cream_api
    pushd "$PROJECT_ROOT" > /dev/null
    print_status "Running mypy..."
    MYPY_OUTPUT=$(poetry run mypy --config-file=pyproject.toml cream_api 2>&1 || true)
    if [ $? -eq 0 ]; then
        print_success "✅ MyPy checks completed!"
        generate_linter_report "mypy" "success" "$MYPY_OUTPUT"
    else
        PYTHON_STATUS="failed"
        print_error "❌ MyPy checks failed!"
        generate_linter_report "mypy" "failed" "$MYPY_OUTPUT"
    fi
    popd > /dev/null
fi

if [ "$RUN_JS" = true ]; then
    print_status "📦 Running JavaScript/TypeScript checks..."
    pushd "$PROJECT_ROOT/cream_ui" > /dev/null

    # Run eslint
    print_status "Running eslint..."
    ESLINT_OUTPUT=$(yarn eslint --fix . 2>&1 || true)
    if [ $? -eq 0 ]; then
        print_success "✅ ESLint completed!"
        generate_linter_report "eslint" "success" "$ESLINT_OUTPUT"
    else
        JS_STATUS="failed"
        print_error "❌ ESLint failed!"
        generate_linter_report "eslint" "failed" "$ESLINT_OUTPUT"
    fi

    # Run TypeScript compiler
    print_status "Running TypeScript compiler..."
    TSC_OUTPUT=$(yarn tsc --noEmit 2>&1 || true)
    if [ $? -eq 0 ]; then
        print_success "✅ TypeScript compiler completed!"
        generate_linter_report "tsc" "success" "$TSC_OUTPUT"
    else
        JS_STATUS="failed"
        print_error "❌ TypeScript compiler failed!"
        generate_linter_report "tsc" "failed" "$TSC_OUTPUT"
    fi

    # Run prettier
    print_status "Running prettier..."
    PRETTIER_OUTPUT=$(yarn prettier --write . --log-level=warn 2>&1 || true)
    if [ $? -eq 0 ]; then
        print_success "✅ Prettier completed!"
        generate_linter_report "prettier" "success" "$PRETTIER_OUTPUT"
    else
        JS_STATUS="failed"
        print_error "❌ Prettier failed!"
        generate_linter_report "prettier" "failed" "$PRETTIER_OUTPUT"
    fi

    popd > /dev/null
fi

# Generate comprehensive AI report
OVERALL_STATUS=$([ "$PYTHON_STATUS" = "success" ] && [ "$JS_STATUS" = "success" ] && echo "success" || echo "failed")

# Count reports generated
PYTHON_REPORT_COUNT=$(ls "$AI_OUTPUT_DIR"/*_report.json 2>/dev/null | wc -l || echo "0")

ADDITIONAL_CONTENT="  \"lint_details\": {\n    \"python_status\": \"$PYTHON_STATUS\",\n    \"js_status\": \"$JS_STATUS\",\n    \"python_tools\": [\"autoflake\", \"ruff_check\", \"ruff_format\", \"mypy\"],\n    \"js_tools\": [\"eslint\", \"tsc\", \"prettier\"],\n    \"reports_generated\": $PYTHON_REPORT_COUNT,\n    \"report_directory\": \"$AI_OUTPUT_DIR\"\n  },"

generate_ai_report "lint" "$OVERALL_STATUS" "0" "$AI_OUTPUT_DIR" "$ADDITIONAL_CONTENT"

# Print summary of generated reports
print_status "📊 Linting Summary:"
print_status "  Python Status: $PYTHON_STATUS"
print_status "  JavaScript Status: $JS_STATUS"
print_status "  Reports generated: $PYTHON_REPORT_COUNT"
print_status "  Report directory: $AI_OUTPUT_DIR"

# Determine overall success
if [ "$PYTHON_STATUS" = "success" ] && [ "$JS_STATUS" = "success" ]; then
    print_success "🎉 All selected linting checks completed successfully!"
    exit 0
else
    print_error "❌ Some linting checks failed!"
    print_status "📄 Check individual reports in $AI_OUTPUT_DIR for details"
    exit 1
fi
