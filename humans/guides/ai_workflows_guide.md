# AI Workflows Guide for Human Operators

**SPDX-License-Identifier: MIT**
**SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>**

```
{
    Hi everyone, Robert here.

    I had cursor write the documentation below and then I put in some notes.

    Editorial notes will be between curly braces, like how this one is.

    Probably something like 5 hours of the total work time was trying to get Cursor to behave in the way I wanted to for the workflow I wanted to do:

    - COMPUTER, write a feature proposal for THING.
    - COMPUTER, write the steps out to implement THING as specced for a Junior Engineer. Write them as JIRA tickets.
    - - That last part is almost assuredly why the .md files are named things like STOCK-003
    - COMPUTER, implement STOCK-001.
    - COMPUTER, fix the failing tests.
    - COMPUTER, fix the linter errors.

    Something about specifying what the failing tests were and linter errors remained bugged me. Why would it not just... know? To that end, most of the scripts covered in this document output a json, which is the format Cursor told me it wanted.

    Hopefully that's technical debt just paid off and I can work faster the rest of the project, but who knows.

    That said, some of this document is just... weird. There's no other word for it. It will repeatedly tell you to check the output of files intended solely for Cursor's consumption. It will make up the functionality of some of the scripts. *You cannot trust these tools at face value.*
}
```

## Table of Contents

1. [Overview](#overview)
2. [Getting Started with AI Tools](#getting-started-with-ai-tools)
3. [AI Documentation Structure](#ai-documentation-structure)
4. [Core AI Workflows](#core-ai-workflows)
5. [Development Workflows](#development-workflows)
6. [Troubleshooting and Debugging](#troubleshooting-and-debugging)
7. [Best Practices](#best-practices)
8. [Maintenance and Updates](#maintenance-and-updates)

## Overview

This guide explains how the scripts in the `scripts/` folder interact with the `ai/` folder to provide AI-optimized development workflows. The system generates structured outputs that AI tools can consume for debugging, analysis, and decision-making.

## Key Scripts and Their AI Integration

```
{
    It should be noted that all the .json files below are not intended for humans. You still get console output and could tee that off into a separate file if you really wanted to. The test runners actually already do this, because it was the easiest way to get the test results to the LLM.

    I wanted to leave in the `cat` commands it gives as examples of the continous weird nonsense that Cursor in specific and LLMs in general will just make up. There is NO reason for you, a real human person, to ever view those files except to debug Cursor, and that hasn't been a problem in a couple days for me.
}
```

### 1. Health Check System (`scripts/ai_health_check.py`)

```
{
    This script is actually quite flawed and I didn't realize until way too late into the second weekend to get it fixed by my self imposed public deadline. I say "flawed" but should read as "Doesn't effing work".

    I tried to fix it late on Saturday and it turned into a mild nightmare as cursor continued to assign scope creep to itself to fix this problem. "Let's just regenerate the files every time" turned into a feature plan with 8 steps that it assigned itself *hundreds* of Story Points to fix.

    What it's supposed to do is make sure that all the 'ai/' documentation that cursor is meant to ingest automatically is up to date with the human documentation.

    Cursor's agent mode, for whatever reason, puts a LOT of emphasis on this file, and assigns it a lot of meaning. Why is this first when it's run once a commit as a hook? I have no idea.

    You shouldn't ever need to check the output of this file yourself with the `cat` command as listed below. I'd be shocked to learn Cursor ever looked at this file.
}
```

**Purpose**: Validates the AI documentation system and generates structured reports.

**AI Integration**:
- Generates reports in `ai/outputs/health_check/healthcheck-result.json`
- Validates cross-references between AI documentation files
- Checks metadata consistency across the system

**Usage**:
```bash
# Run health check
python scripts/ai_health_check.py

# Check results
cat ai/outputs/health_check/healthcheck-result.json
```

**When to Use**:
- Before making changes to AI documentation
- When debugging AI tool issues
- To validate system integrity

### 2. Testing Scripts with AI Output

#### Backend Testing (`scripts/run_pytest.sh`)

{
    This is probably the script I ran the most because I put way too much emphasis on the backend in the 16 or so hours I've spent actively working on this.

    Without fanfare: What it does is run pytest, show you the results (without color, unfortunately), and log two files for Cursor to view, all in a mildly fancy wrapper.

    "I ran tests for you" would *generally* trigger it to search for the files.

    I got real used to copy and pasting:

    > Generated AI pytest report: /creampie/ai/outputs/test_results/pytest-results.json

    I want to draw special attention to this one, because it was while making and debugging the final batch of tests that Cursor straight up invented a bug. It told me that aiohttp was failing to handle a database request correctly because of the UUID, and that this was a common compatability problem between SQLite3 (the test DB) and PostgreSQL (The "prod" DB.)

    The truth is, of course, that this was completely incorrect. Multiple other tests already had this pattern and it worked fine. What I did was ask it to make a minimal, reproducible test that I could pass to the aiohttp team as a bug.

    The code it gave me was, stripped to the studs:
    > results = [1,2,3,4,5]
    > await results

    ...Which failed. Because obviously it failed. This is just a syntax error that thinks it's better than you.

    When confronted with its own failing test, Cursor conceded that it was wrong, output "I see the issue!" and then fixed the test by applying a pytest async marker. But of course, not until it tried to fix the test.
}

**AI Integration**:
- Generates test results in `ai/outputs/test_results/`
- Creates structured JSON reports for AI consumption
- Captures test output and coverage data

**Usage**:
```bash
# Run all tests
./scripts/run_pytest.sh

# Run specific test with verbose output
./scripts/run_pytest.sh -v tests/stock_data/test_api.py

# Check test results
ls ai/outputs/test_results/
cat ai/outputs/test_results/pytest-results.json
```

#### Frontend Testing (`scripts/run_react_tests.sh`)

```
{
    This is pretty literally a copy and paste of the pytest runner.

    As in, I asked for a react runner and told it to base it off of the pytest runner.

    It's the same idea: Run the tests and output files for Cursor that it can read in planned directories.
}
```

**AI Integration**:
- Generates React test results in `ai/outputs/test_results/`
- Creates AI-friendly JSON reports
- Captures test statistics and coverage

**Usage**:
```bash
# Run React tests
./scripts/run_react_tests.sh

# Run with verbose output
./scripts/run_react_tests.sh -v

# Check results
cat ai/outputs/test_results/react-test-results.json
```

### 3. Linting and Code Quality (`scripts/lint.sh`)

```
{
    This one just runs all the linters and does the .json output for Cursor.

    The only real thing I find notable about this file is that it outputs 7 reports instead of 1 split between a .json and a .txt file.
}
```

**AI Integration**:
- Generates linting reports in `ai/outputs/lint_results/`
- Creates individual reports for each tool (ruff, mypy, eslint, etc.)
- Provides structured data about code quality issues

**Usage**:
```bash
# Run all linting checks
./scripts/lint.sh

# Run Python-only checks
./scripts/lint.sh --python-only

# Check lint results
ls ai/outputs/lint_results/
cat ai/outputs/lint_results/ruff_check_report.json
```

### 4. Database Operations

```
{
    Some of these are mildly interesting.

    `migrate.sh` is meant to:
    - Make migrations via alembic for any models that were missing one.
    - Run all the migration files in the codebase.
    - ... That's it.

    There was a bug with the `migrate.sh` script which probably cost me at least an hour. It was *always* generating a migration, even if they were empty files.
}
```

#### Migration Script (`scripts/db/migrate.sh`)

**AI Integration**:
- Generates migration reports in `ai/outputs/migration_results/`
- Tracks migration status and validation
- Provides structured data about database changes

**Usage**:
```bash
# Run migrations
./scripts/db/migrate.sh

# Dry run to see what would change
./scripts/db/migrate.sh -d

# Check migration results
cat ai/outputs/migration_results/migration-results.json
```

#### Database Setup (`scripts/db/populate_test_data.py`)

```
{
    I figured any respectable codebase needs a way to reset the development database. That's all this is.
}
```

**AI Integration**:
- Generates setup reports for AI analysis
- Tracks database population status
- Provides structured data about test data creation

**Usage**:
```bash
# Populate test data
python scripts/db/populate_test_data.py

# With custom count
python scripts/db/populate_test_data.py --count 20
```

### 5. Server Management (`scripts/kill_servers.sh`)

```
{
    Early on I had an issue with background tasks where FastAPI would just hang indefinitely trying to call `gather` on a group of tasks that ran forever. This script is meant to be a way to kill the server fast.

    At this point, the "Shell Style Guide" was established and it decided it needed to output the results to a .json for itself. I don't think I ever used that functionality though.
}
```

**AI Integration**:
- Generates server operation reports in `ai/outputs/server_operations/`
- Tracks server kill status and processes
- Provides structured data about server management

**Usage**:
```bash
# Kill FastAPI server
./scripts/kill_servers.sh --fastapi

# Kill React server
./scripts/kill_servers.sh --react

# Check server operation results
cat ai/outputs/server_operations/server_kill-results.json
```

### 6. Dependency Management (`scripts/pyupdate.sh`)

```
{
    Honestly, I don't remember why I felt the need to generate this file.

    Like, there clearly isn't one for react. Why did I make Cursor make this. (lol)
}
```

**AI Integration**:
- Generates dependency update reports in `ai/outputs/dependency_updates/`
- Tracks update status for each step
- Provides structured data about dependency changes

**Usage**:
```bash
# Update dependencies
./scripts/pyupdate.sh

# Check update results
cat ai/outputs/dependency_updates/dependency_update-results.json
```

### 7. Stock Data Operations (`scripts/retrieve_stock_data.py`)

```
{
    This script was meant to be a one or two time thing before the UI was ready. It just pings the local FastAPI endpoint to start retrieval for you.
}
```


**AI Integration**:
- Generates stock data operation reports in `ai/outputs/stock_data_operations/`
- Tracks retrieval success/failure
- Provides structured data about stock data operations

**Usage**:
```bash
# Retrieve stock data
python scripts/retrieve_stock_data.py AAPL

# Check operation results
cat ai/outputs/stock_data_operations/stock-data-retrieval-results.json
```

## AI Output Structure

All scripts generate consistent JSON output in the `ai/outputs/` directory:

### Output Categories
- `ai/outputs/health_check/` - System validation reports
- `ai/outputs/test_results/` - Test execution results
- `ai/outputs/lint_results/` - Code quality analysis
- `ai/outputs/migration_results/` - Database migration status
- `ai/outputs/server_operations/` - Server management results
- `ai/outputs/dependency_updates/` - Dependency management
- `ai/outputs/stock_data_operations/` - Stock data operations

### JSON Report Format
All scripts generate reports with this structure:
```json
{
  "ai_metadata": {
    "template_version": "4.0",
    "ai_processing_level": "High",
    "required_context": "Script execution results",
    "validation_required": true,
    "code_generation": "Not applicable",
    "cross_references": ["scripts/script_name"],
    "maintenance": "Auto-generated by script"
  },
  "file_info": {
    "purpose": "Results and status report",
    "last_updated": "2025-06-21",
    "format": "json",
    "optimization_target": "ai_tool_consumption"
  },
  "content": {
    "summary": {
      "success": true,
      "errors_count": 0,
      "warnings_count": 0,
      "timestamp": "2025-06-21T10:30:00"
    },
    "results": {},
    "errors": [],
    "warnings": []
  }
}
```

## Debugging Workflow

```
{
    This is the funniest and saddest part of the whole project, depending on how you look at it.

    Getting Cursor to check these folders in a new context window with a phrase like "Please fix the 4 ruff errors" is shockingly difficult. Like, it would interrupt that as you made up the 4 and ask to personally run ruff again.

    So even though these rules are literally *for Cursor* and I had this written explicitly *for humans*, it's sort of interesting it decided to include them.

    You should never have to check these. Cursor should automatically check them. If it doesn't, then I consider that a bug. It's more insidious than that though, because Cursor will also tell you that there's nothing wrong even when it doesn't do the thing I've explicitly had itself make rules for more times than anything.
}
```

### Before Debugging (CRITICAL)

**Always check existing AI outputs first**:

```bash
# Check for existing reports
ls ai/outputs/test_results/
ls ai/outputs/lint_results/
ls ai/outputs/health_check/

# Read actual error messages
cat ai/outputs/test_results/pytest-results.json
cat ai/outputs/lint_results/ruff_check_report.json
```

### Common Debugging Patterns

```
{
    Again, only Cursor should never check these files. It's extremely bizarre that it's asking you to cat them.

    You, the human, have your own output. Why would you need to cat a mostly unformatted JSON?
}
```

1. **Test Failures**:
   ```bash
   # Check test results
   cat ai/outputs/test_results/pytest-results.json

   # Run tests again if needed
   ./scripts/run_pytest.sh -v
   ```

2. **Linting Issues**:
   ```bash
   # Check lint results
   cat ai/outputs/lint_results/ruff_check_report.json

   # Fix and re-run
   ./scripts/lint.sh --python-only
   ```

3. **Database Issues**:
   ```bash
   # Check migration status
   cat ai/outputs/migration_results/migration-results.json

   # Fix migration state if needed
   ./scripts/db/fix_migration_state.sh
   ```

## Integration Testing

### Full Integration Test (`scripts/run_integration_tests.sh`)

```
{
    This just runs the other two test runners back to back.

    ...That's it. I don't know why it decided to give this a whole section like it's particularly special.
}
```

**AI Integration**:
- Runs both backend and frontend tests
- Generates comprehensive test reports
- Provides unified status for AI analysis

**Usage**:
```bash
# Run all integration tests
./scripts/run_integration_tests.sh

# With verbose output
./scripts/run_integration_tests.sh -v
```

## Helper Scripts

### Common Functions (`scripts/common.sh`)

```
{
    This file arguably does way too much.

    Like, it contains the shell scripting to kill a process, which is only ever used in ./kill_servers.sh
}
```

**AI Integration**:
- Provides `generate_ai_report()` function for consistent reporting
- Standardizes JSON output format across all scripts
- Ensures proper metadata and structure

**Usage by Other Scripts**:
```bash
# Scripts use this function to generate reports
generate_ai_report "operation_type" "status" "duration" "output_dir" "additional_content"
```

### Output Helper (`scripts/output_helper.py`)

**AI Integration**:
- Python helper for generating structured JSON output
- Provides consistent metadata and formatting
- Supports both human-readable and machine-readable output

**Usage**:
```python
from scripts.output_helper import OutputHelper

helper = OutputHelper("my_script", "my_category")
helper.add_result("processed_files", 5)
helper.add_error("Failed to process file.txt")
json_file = helper.save_output("my_results")
```

## Best Practices for Human Operators

### 1. Always Check AI Outputs First
```
{
    lol
}
```

```bash
# Before debugging, check existing reports
ls ai/outputs/
cat ai/outputs/test_results/latest_test_run.json
```

### 2. Use Scripts for All Operations
```
{
    Correct!
}
```
```bash
# Don't run commands directly
# Instead, use the provided scripts
./scripts/run_pytest.sh  # ✅ Good
poetry run pytest        # ❌ Avoid
```

### 3. Check Script Results
```
{
    No.
}
```
```bash
# After running any script, check its output
./scripts/lint.sh
cat ai/outputs/lint_results/lint-results.json
```

### 4. Use Health Check for System Validation
```
{
    ...No.
}
```
```bash
# Validate the AI system before making changes
python scripts/ai_health_check.py
cat ai/outputs/health_check/healthcheck-result.json
```

## Troubleshooting

### Common Issues
```
{
    This section is frankly fascinating.

    Most of it is just wrong. You shouldn't ever have to look at the ai output files yourself. They're for the AI!

    There's also that repeated emphasis on ./ai_health_check.py, which again, is just meant to make sure the .json files the AI is supposed to reference during development are in the most digestible format for it possible.
}
```

1. **Missing AI Outputs**:
   ```bash
   # Check if outputs directory exists
   ls ai/outputs/

   # Run health check to validate system
   python scripts/ai_health_check.py
   ```

2. **Script Failures**:
   ```bash
   # Check script output
   cat ai/outputs/[category]/[script]-results.json

   # Look for error messages in the JSON
   jq '.content.errors' ai/outputs/[category]/[script]-results.json
   ```

3. **Inconsistent Reports**:
   ```bash
   # Validate system integrity
   python scripts/ai_health_check.py

   # Check for cross-reference issues
   cat ai/outputs/health_check/healthcheck-result.json
   ```

## Quick Reference

### Essential Commands
```bash
# Health check
python scripts/ai_health_check.py

# Testing
./scripts/run_pytest.sh
./scripts/run_react_tests.sh

# Linting
./scripts/lint.sh

# Database
./scripts/db/migrate.sh

# Check outputs
ls ai/outputs/
```

### Key Output Files
- `ai/outputs/health_check/healthcheck-result.json` - System validation
- `ai/outputs/test_results/pytest-results.json` - Backend test results
- `ai/outputs/test_results/react-test-results.json` - Frontend test results
- `ai/outputs/lint_results/lint-results.json` - Code quality results
- `ai/outputs/migration_results/migration-results.json` - Database migration status

### Debugging Checklist
- [ ] Check `ai/outputs/` for existing reports
- [ ] Read actual error messages from JSON files
- [ ] Run relevant scripts to generate fresh reports
- [ ] Use health check to validate system integrity
- [ ] Check cross-references in AI documentation

## Conclusion

The scripts in the `scripts/` folder are designed to work seamlessly with the AI documentation system. They generate structured, machine-readable outputs that enable AI tools to understand project status, debug issues, and make informed decisions.

**Key Principles**:
1. **Always use the provided scripts** - they generate AI-friendly output
2. **Check AI outputs before debugging** - avoid duplicate work
3. **Use health check for system validation** - ensure AI system integrity
4. **Follow the structured workflow** - leverage the AI integration for efficiency

This system enables both human operators and AI tools to work more effectively together by providing consistent, structured data about all development operations.

