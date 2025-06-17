# Shell Style Guide

This style guide should be used as a reference for maintaining consistency across shell scripts in the project.

## General Guidelines

1. Use `#!/bin/bash` as the shebang line
2. Enable error handling with `set -e` at the start of scripts
3. Use meaningful variable and function names
4. Keep functions small and focused
5. Use comments to explain complex logic
6. Follow the principle of least surprise
7. Keep the code DRY (Don't Repeat Yourself)

## Script Organization

1. Scripts should be organized in the following order:
   ```bash
   #!/bin/bash

   # Exit on error
   set -e

   # Source common functions
   SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
   source "$SCRIPT_DIR/common.sh"

   # Variable declarations

   # Function definitions

   # Main script logic
   ```

2. Use absolute paths with `SCRIPT_DIR` and `PROJECT_ROOT` for reliable path resolution
3. Source common functions from `common.sh` for shared functionality
4. Group related functionality into functions

## Error Handling

1. Use the `run_command` function for command execution and error handling:
   ```bash
   run_command "command with args"
   ```

2. Use `handle_error` for fatal errors:
   ```bash
   handle_error "Descriptive error message"
   ```

3. Use proper exit codes:
   - 0 for success
   - Non-zero for errors

## Output Formatting

1. Use the common print functions for consistent output:
   - `print_status` for informational messages
   - `print_success` for success messages
   - `print_error` for error messages

2. Use emojis for visual feedback:
   - 🔄 for processes
   - 📦 for package operations
   - 🔍 for checks/verification
   - ✅ for success
   - ❌ for errors

3. Keep messages clear and concise

## Command Execution

1. Use `poetry run` for Python commands:
   ```bash
   poetry run command
   ```

2. Use `pushd`/`popd` for directory changes:
   ```bash
   pushd directory > /dev/null
   # commands
   popd > /dev/null
   ```

3. Redirect unnecessary output to `/dev/null`

## Common Functions

1. Use the following functions from `common.sh`:
   - `print_message`, `print_status`, `print_success`, `print_error` for output
   - `handle_error` for error handling
   - `run_command` for command execution
   - `get_script_dir` and `get_project_root` for path resolution

## Best Practices

1. Always check for required files/directories before proceeding
2. Use descriptive variable names
3. Comment complex logic
4. Use proper indentation (4 spaces)
5. Keep line length reasonable
6. Use quotes around variables
7. Use `[[` instead of `[` for tests
8. Use `$()` instead of backticks for command substitution

## Security

1. Never hardcode sensitive information
2. Use environment variables for secrets
3. Validate input data
4. Use proper file permissions
5. Avoid using `eval` unless necessary

## Testing

1. Test scripts with different scenarios
2. Include both positive and negative test cases
3. Test error handling
4. Test with different environments

## Documentation

1. Include a header comment explaining the script's purpose
2. Document function parameters and return values
3. Use comments to explain complex logic
4. Keep README.md updated with script usage
