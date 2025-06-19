#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Function to print colored status messages
print_status() {
    echo -e "\033[1;37m$1\033[0m"
}

print_success() {
    echo -e "\033[1;32m$1\033[0m"
}

print_error() {
    echo -e "\033[1;31m$1\033[0m"
}

# Function to run a command and handle errors
run_command() {
    if ! eval "$1"; then
        print_error "Failed: $1"
        exit 1
    fi
}

# Function to generate AI-consumable lint report
generate_ai_lint_report() {
    local python_status=$1
    local js_status=$2
    local timestamp=$(date -Iseconds)

    # Ensure AI output directory exists
    mkdir -p "$AI_OUTPUT_DIR"

    # Generate report filename
    local report_file="$AI_OUTPUT_DIR/lint-report-$(date +%Y%m%d_%H%M%S).json"

    # Create JSON report
    cat > "$report_file" << EOF
{
  "ai_metadata": {
    "purpose": "Linting results for AI consumption",
    "template_version": "1.0",
    "ai_processing_level": "Medium",
    "required_context": "Code quality standards, linting configuration",
    "validation_required": "No",
    "code_generation": "Not Supported",
    "cross_references": []
  },
  "file_info": {
    "file_path": "outputs/lint_results/$(basename "$report_file")",
    "original_format": "json",
    "generated_at": "$timestamp",
    "file_size": 0,
    "line_count": 0
  },
  "content": {
    "sections": [
      {
        "level": 1,
        "title": "Linting Report",
        "content": "Comprehensive code quality and linting results for AI consumption.",
        "subsections": []
      },
      {
        "level": 2,
        "title": "Execution Summary",
        "content": "**Timestamp**: $timestamp\n**Python Checks**: $python_status\n**JavaScript/TypeScript Checks**: $js_status\n**Overall Status**: $([ "$python_status" = "success" ] && [ "$js_status" = "success" ] && echo "success" || echo "failed")",
        "subsections": []
      },
      {
        "level": 2,
        "title": "Python Linting",
        "content": "**Status**: $python_status\n**Tools Used**:\n- autoflake (unused imports/variables)\n- ruff (linting and formatting)\n- mypy (type checking)\n\n**Target Directory**: cream_api/",
        "subsections": []
      },
      {
        "level": 2,
        "title": "JavaScript/TypeScript Linting",
        "content": "**Status**: $js_status\n**Tools Used**:\n- eslint (linting and fixing)\n- tsc (TypeScript compilation check)\n- prettier (code formatting)\n\n**Target Directory**: cream_ui/",
        "subsections": []
      }
    ],
    "code_blocks": [],
    "links": [],
    "raw_content": "Linting completed. Python: $python_status, JavaScript/TypeScript: $js_status. Overall status: $([ "$python_status" = "success" ] && [ "$js_status" = "success" ] && echo "success" || echo "failed")."
  },
  "cross_references": [
    {
      "title": "Python Configuration",
      "path": "pyproject.toml",
      "type": "config",
      "relevance": "high"
    },
    {
      "title": "ESLint Configuration",
      "path": "cream_ui/eslint.config.js",
      "type": "config",
      "relevance": "high"
    },
    {
      "title": "TypeScript Configuration",
      "path": "cream_ui/tsconfig.json",
      "type": "config",
      "relevance": "medium"
    }
  ],
  "code_generation_hints": [],
  "validation_rules": [],
  "optimization": {
    "version": "1.0",
    "generated_at": "$timestamp",
    "improvements": []
  }
}
EOF

    # Update file size and line count
    local file_size=$(wc -c < "$report_file")
    local line_count=$(wc -l < "$report_file")

    # Update the JSON with actual values
    sed -i "s/\"file_size\": 0/\"file_size\": $file_size/" "$report_file"
    sed -i "s/\"line_count\": 0/\"line_count\": $line_count/" "$report_file"

    print_status "Generated AI lint report: $report_file"
}

# Parse command line arguments
RUN_PYTHON=true
RUN_JS=true
AI_OUTPUT_DIR="ai/outputs/lint_results"

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
    pushd cream_api > /dev/null

    if run_command "poetry run autoflake -i -r --remove-all-unused-imports --recursive --remove-unused-variables --in-place --quiet --exclude=__init__.py ." && \
       run_command "poetry run ruff check --fix ." && \
       run_command "poetry run ruff format ." && \
       run_command "poetry run mypy --config-file=../pyproject.toml ."; then
        print_success "✅ Python checks completed!"
    else
        PYTHON_STATUS="failed"
        print_error "❌ Python checks failed!"
    fi

    popd > /dev/null
fi

if [ "$RUN_JS" = true ]; then
    print_status "📦 Running JavaScript/TypeScript checks..."
    pushd cream_ui > /dev/null

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

# Generate AI report
generate_ai_lint_report "$PYTHON_STATUS" "$JS_STATUS"

# Determine overall success
if [ "$PYTHON_STATUS" = "success" ] && [ "$JS_STATUS" = "success" ]; then
    print_success "🎉 All selected linting checks completed successfully!"
    exit 0
else
    print_error "❌ Some linting checks failed!"
    exit 1
fi
