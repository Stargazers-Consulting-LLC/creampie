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

PYTHON_STATUS="success"
JS_STATUS="success"

if [ "$RUN_PYTHON" = true ]; then
    print_status "📝 Running Python checks..."

    # Run autoflake on cream_api
    pushd "$PROJECT_ROOT/cream_api" > /dev/null
    if run_command "poetry run autoflake -i -r --remove-all-unused-imports --recursive --remove-unused-variables --in-place --quiet --exclude=__init__.py ."; then
        print_success "✅ Autoflake completed!"
    else
        PYTHON_STATUS="failed"
        print_error "❌ Autoflake failed!"
    fi
    popd > /dev/null

    # Run ruff on entire project (including scripts) to match pre-commit
    pushd "$PROJECT_ROOT" > /dev/null
    if run_command "poetry run ruff check --fix ." && \
       run_command "poetry run ruff format ."; then
        print_success "✅ Ruff checks completed!"
    else
        PYTHON_STATUS="failed"
        print_error "❌ Ruff checks failed!"
    fi
    popd > /dev/null

    # Run mypy on cream_api
    pushd "$PROJECT_ROOT" > /dev/null
    if run_command "poetry run mypy --config-file=pyproject.toml cream_api"; then
        print_success "✅ MyPy checks completed!"
    else
        PYTHON_STATUS="failed"
        print_error "❌ MyPy checks failed!"
    fi
    popd > /dev/null
fi

if [ "$RUN_JS" = true ]; then
    print_status "📦 Running JavaScript/TypeScript checks..."
    pushd "$PROJECT_ROOT/cream_ui" > /dev/null

    if run_command "yarn eslint --fix ." && \
       run_command "yarn tsc --noEmit" && \
       run_command "yarn prettier --write . --log-level=warn"; then
        print_success "✅ JavaScript/TypeScript checks completed!"
    else
        JS_STATUS="failed"
        print_error "❌ JavaScript/TypeScript checks failed!"
    fi

    popd > /dev/null
fi

# Generate AI report using common function
OVERALL_STATUS=$([ "$PYTHON_STATUS" = "success" ] && [ "$JS_STATUS" = "success" ] && echo "success" || echo "failed")
ADDITIONAL_CONTENT="  \"lint_details\": {\n    \"python_status\": \"$PYTHON_STATUS\",\n    \"js_status\": \"$JS_STATUS\",\n    \"python_tools\": [\"autoflake\", \"ruff\", \"mypy\"],\n    \"js_tools\": [\"eslint\", \"tsc\", \"prettier\"]\n  },"

generate_ai_report "lint" "$OVERALL_STATUS" "0" "$AI_OUTPUT_DIR" "$ADDITIONAL_CONTENT"

# Determine overall success
if [ "$PYTHON_STATUS" = "success" ] && [ "$JS_STATUS" = "success" ]; then
    print_success "🎉 All selected linting checks completed successfully!"
    exit 0
else
    print_error "❌ Some linting checks failed!"
    exit 1
fi
