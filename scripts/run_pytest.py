#!/usr/bin/env python3
"""
Enhanced Pytest Runner

A Python equivalent of run_pytest.sh with enhanced flexibility and AI reporting.
Provides watch mode, test listing, marker filtering, and comprehensive reporting.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime

import click


class PytestRunner:
    """Enhanced pytest runner with AI reporting capabilities."""

    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.script_dir)
        self.ai_output_dir = os.path.join(self.project_root, "ai", "outputs", "test_results")
        self.cream_api_dir = os.path.join(self.project_root, "cream_api")

        # Ensure AI output directory exists
        os.makedirs(self.ai_output_dir, exist_ok=True)

    def list_test_files(self) -> None:
        """List available pytest test files."""
        click.echo("Available pytest test files:")
        click.echo()

        # Find all test files recursively
        test_files = []
        for root, _, files in os.walk(self.cream_api_dir):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.cream_api_dir)
                    test_files.append(rel_path)

        for test_file in sorted(test_files):
            click.echo(f"  {test_file}")
        click.echo()

    def list_test_functions(self, file_path: str) -> None:
        """List test functions in a specific file."""
        full_path = os.path.join(self.cream_api_dir, file_path)

        if not os.path.exists(full_path):
            click.echo(f"❌ File not found: {file_path}", err=True)
            sys.exit(1)

        click.echo(f"Pytest test functions in {file_path}:")
        click.echo()

        try:
            with open(full_path, encoding="utf-8") as file:
                for line in file:
                    if line.strip().startswith("def test_"):
                        # Extract function name
                        func_name = line.strip().split("def ")[1].split("(")[0]
                        click.echo(f"  {func_name}")
        except Exception as e:
            click.echo(f"❌ Error reading file: {e}", err=True)
            sys.exit(1)
        click.echo()

    def list_markers(self) -> None:
        """List available pytest markers."""
        click.echo("Available pytest markers:")
        click.echo()

        try:
            result = subprocess.run(
                ["poetry", "run", "pytest", "--markers"],
                cwd=self.cream_api_dir,
                capture_output=True,
                text=True,
                check=True,
            )

            for line in result.stdout.split("\n"):
                if line.strip().startswith("@pytest.mark."):
                    click.echo(f"  {line.strip()}")
        except subprocess.CalledProcessError as e:
            click.echo(f"❌ Error listing markers: {e}", err=True)
            sys.exit(1)
        click.echo()

    def validate_test_path(self, test_path: str | None) -> bool:
        """Validate the test path."""
        if not test_path:
            return True  # Empty path is valid (runs all tests)

        full_path = os.path.join(self.cream_api_dir, test_path)

        # Check if it's a file
        if os.path.isfile(full_path):
            if os.path.basename(full_path).startswith("test_") and full_path.endswith(".py"):
                return True
            else:
                click.echo(f"❌ File {test_path} is not a pytest test file (should start with 'test_')", err=True)
                return False

        # Check if it's a directory
        if os.path.isdir(full_path):
            # Check if directory contains test files
            has_test_files = False
            for _root, _, files in os.walk(full_path):
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        has_test_files = True
                        break
                if has_test_files:
                    break

            if has_test_files:
                return True
            else:
                click.echo(f"❌ Directory {test_path} contains no pytest test files", err=True)
                return False

        click.echo(f"❌ Path {test_path} does not exist", err=True)
        return False

    def run_tests_once(
        self, test_path: str | None, test_function: str | None, marker: str | None, verbose: bool
    ) -> tuple[bool, dict, str]:
        """Run tests once and return success status, test counts, and output."""
        start_time = time.time()

        # Build pytest arguments
        pytest_args = ["poetry", "run", "pytest"]

        if verbose:
            pytest_args.append("-v")

        if marker:
            pytest_args.extend(["-m", marker])

        if test_path:
            if test_function:
                pytest_args.append(f"{test_path}::{test_function}")
            else:
                pytest_args.append(test_path)

        # Run pytest and capture output
        try:
            result = subprocess.run(
                pytest_args,
                cwd=self.cream_api_dir,
                capture_output=True,
                text=True,
                check=True,
            )

            duration = time.time() - start_time
            click.echo(f"✅ Pytest completed successfully in {duration:.1f}s")

            # Parse test counts from output
            test_counts = self.parse_test_counts(result.stdout)
            return True, test_counts, result.stdout

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            click.echo(f"❌ Pytest failed after {duration:.1f}s")

            # Parse test counts even from failed runs
            test_counts = self.parse_test_counts(e.stdout or "")
            # Combine stdout and stderr for complete error information
            full_output = (e.stdout or "") + "\n" + (e.stderr or "")
            return False, test_counts, full_output

    def parse_test_counts(self, output: str) -> dict:
        """Parse test counts from pytest output."""
        counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total": 0}

        # Look for the summary line (e.g., "9 passed in 18.84s" or "1 failed, 8 passed in 18.84s")
        lines = output.split("\n")
        for output_line in lines:
            stripped_line = output_line.strip()
            if "passed" in stripped_line and ("s ==" in stripped_line or "s ==" in stripped_line):
                # Parse the summary line
                parts = stripped_line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        if i + 1 < len(parts):
                            next_part = parts[i + 1]
                            if "passed" in next_part:
                                counts["passed"] = int(part)
                            elif "failed" in next_part:
                                counts["failed"] = int(part)
                            elif "error" in next_part:
                                counts["errors"] = int(part)
                            elif "skipped" in next_part:
                                counts["skipped"] = int(part)

                # Calculate total
                counts["total"] = counts["passed"] + counts["failed"] + counts["errors"] + counts["skipped"]
                break

        return counts

    def generate_ai_report(  # noqa: PLR0913
        self,
        test_path: str | None,
        test_function: str | None,
        marker: str | None,
        verbose: bool,
        success: bool,
        duration: float,
        test_counts: dict,
        output: str,
    ) -> None:
        """Generate AI report for test results."""
        timestamp = datetime.now().isoformat()

        report = {
            "metadata": {
                "title": "Pytest Test Results",
                "description": "Results from pytest test execution",
                "version": "1.0.0",
                "last_updated": timestamp,
                "source": "scripts/run_pytest.py",
                "cross_references": ["cream_api/tests/", "pytest.ini", "pyproject.toml"],
            },
            "test_execution": {
                "success": success,
                "duration_seconds": round(duration, 2),
                "timestamp": timestamp,
                "test_path": test_path or "All tests",
                "test_function": test_function or "All functions",
                "marker": marker or "None",
                "verbose": verbose,
                "test_counts": test_counts,
            },
            "environment": {
                "python_version": sys.version,
                "working_directory": self.cream_api_dir,
                "project_root": self.project_root,
            },
            "output": output,
        }

        # Save report
        safe_timestamp = timestamp.replace(":", "-")
        report_file = os.path.join(self.ai_output_dir, f"pytest-results-{safe_timestamp}.json")
        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=2, ensure_ascii=False)

        click.echo(f"📄 AI report saved to: {report_file}")

        # Display test summary
        if test_counts["total"] > 0:
            passed = test_counts["passed"]
            failed = test_counts["failed"]
            errors = test_counts["errors"]
            skipped = test_counts["skipped"]
            click.echo(f"📊 Test Summary: {passed} passed, {failed} failed, {errors} errors, {skipped} skipped")


@click.command()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option("-m", "--marker", help="Run tests with specific marker (e.g., slow, integration)")
@click.option("--list", "list_files", is_flag=True, help="List available test files")
@click.option("--list-functions", help="List test functions in a specific file")
@click.option("--list-markers", is_flag=True, help="List available pytest markers")
@click.argument("test_path", required=False)
@click.argument("test_function", required=False)
def main(  # noqa: PLR0913
    verbose: bool,
    marker: str | None,
    list_files: bool,
    list_functions: str | None,
    list_markers: bool,
    test_path: str | None,
    test_function: str | None,
) -> None:
    """Enhanced pytest runner with AI reporting."""
    runner = PytestRunner()

    # Handle list operations
    if list_files:
        runner.list_test_files()
        return

    if list_functions:
        runner.list_test_functions(list_functions)
        return

    if list_markers:
        runner.list_markers()
        return

    # Parse test path and function
    # Handle test_path::test_function format
    if test_path and "::" in test_path:
        parts = test_path.split("::")
        test_path = parts[0]
        test_function = parts[1]

    # Validate test path
    if not runner.validate_test_path(test_path):
        sys.exit(1)

    # Show what we're running
    click.echo("🚀 Starting pytest execution")

    if test_path:
        if test_function:
            click.echo(f"🎯 Target: {test_path}::{test_function}")
        else:
            click.echo(f"🎯 Target: {test_path}")
    else:
        click.echo("🎯 Target: All pytest tests")

    if marker:
        click.echo(f"🏷️ Marker: {marker}")

    click.echo()

    # Run tests once
    start_time = time.time()
    success, test_counts, output = runner.run_tests_once(test_path, test_function, marker, verbose)
    duration = time.time() - start_time

    # Generate AI report
    runner.generate_ai_report(test_path, test_function, marker, verbose, success, duration, test_counts, output)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
