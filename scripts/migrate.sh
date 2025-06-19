#!/bin/bash

# Exit on error
set -e

# Source common functions
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/common.sh"

# Get the project root and API directory
PROJECT_ROOT="$(get_project_root)"
API_DIR="$PROJECT_ROOT/cream_api"
AI_OUTPUT_DIR="ai/outputs/migration_results"

# Check if we're in the right directory
if [ ! -f "$API_DIR/alembic.ini" ]; then
    handle_error "alembic.ini not found in $API_DIR"
fi

# Change to the API directory
cd "$API_DIR" || handle_error "Failed to change to $API_DIR"

# Initialize status variables
MIGRATION_CREATED="no"
MIGRATION_STATUS="success"

# Create new migration if there are changes
print_status "Checking for model changes..."
if poetry run alembic revision --autogenerate -m "auto migration" > /dev/null 2>&1; then
    print_success "Created new migration"
    MIGRATION_CREATED="yes"
else
    print_success "No new migrations needed"
fi

# Apply all pending migrations
print_status "Applying pending migrations..."
if poetry run alembic upgrade head; then
    print_success "All migrations applied successfully"
else
    MIGRATION_STATUS="failed"
    handle_error "Failed to apply migrations"
fi

# Function to generate AI-consumable migration report
generate_ai_migration_report() {
    local migration_created=$1
    local migration_status=$2
    local timestamp=$(date -Iseconds)

    # Ensure AI output directory exists
    mkdir -p "$AI_OUTPUT_DIR"

    # Generate report filename
    local report_file="$AI_OUTPUT_DIR/migration-report-$(date +%Y%m%d_%H%M%S).json"

    # Create JSON report
    cat > "$report_file" << EOF
{
  "ai_metadata": {
    "purpose": "Database migration results for AI consumption",
    "template_version": "1.0",
    "ai_processing_level": "Medium",
    "required_context": "Database schema, Alembic configuration",
    "validation_required": "No",
    "code_generation": "Not Supported",
    "cross_references": []
  },
  "file_info": {
    "file_path": "outputs/migration_results/$(basename "$report_file")",
    "original_format": "json",
    "generated_at": "$timestamp",
    "file_size": 0,
    "line_count": 0
  },
  "content": {
    "sections": [
      {
        "level": 1,
        "title": "Migration Report",
        "content": "Database migration execution results and status for AI consumption.",
        "subsections": []
      },
      {
        "level": 2,
        "title": "Execution Summary",
        "content": "**Timestamp**: $timestamp\n**Migration Created**: $migration_created\n**Migration Applied**: $migration_status\n**Overall Status**: $([ "$migration_status" = "success" ] && echo "success" || echo "failed")",
        "subsections": []
      },
      {
        "level": 2,
        "title": "Migration Process",
        "content": "**Step 1 - Model Changes**: $migration_created\n**Step 2 - Apply Migrations**: $migration_status\n\n**Target Directory**: cream_api/\n**Configuration**: alembic.ini",
        "subsections": []
      },
      {
        "level": 2,
        "title": "Database Status",
        "content": "**Current State**: $([ "$migration_status" = "success" ] && echo "Up to date" || echo "Migration failed")\n**Migration Files**: cream_api/migrations/versions/\n**Database**: PostgreSQL/SQLite (development)",
        "subsections": []
      }
    ],
    "code_blocks": [],
    "links": [],
    "raw_content": "Migration completed. Created: $migration_created, Applied: $migration_status. Overall status: $([ "$migration_status" = "success" ] && echo "success" || echo "failed")."
  },
  "cross_references": [
    {
      "title": "Alembic Configuration",
      "path": "cream_api/alembic.ini",
      "type": "config",
      "relevance": "high"
    },
    {
      "title": "Migration Environment",
      "path": "cream_api/migrations/env.py",
      "type": "config",
      "relevance": "high"
    },
    {
      "title": "Database Models",
      "path": "cream_api/stock_data/models.py",
      "type": "code",
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

    print_status "Generated AI migration report: $report_file"
}

# Generate AI report
generate_ai_migration_report "$MIGRATION_CREATED" "$MIGRATION_STATUS"
