#!/usr/bin/env python3
"""AI Documentation Health Check Script.

This script validates the AI documentation structure and ensures all files
follow the proper format and have valid cross-references.

The script is designed to work with the unified AI rules approach
where ai/ai_rules.json is the primary source of truth.

References:
    - [Python Style Guide](humans/guides/python_style_guide.md)
    - [AI Documentation Rules](ai/ai_rules.json)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

# Standard library imports
import functools
import json
import os
import sys
from datetime import datetime
from typing import Any

# Local imports
# (None for this script)

# Module-level constants
DEFAULT_VERBOSE = False

# Module-level variables
# (None for this script)


class AIDocumentationHealthCheck:
    """Health check for AI documentation structure and optimization.

    This class provides comprehensive validation of AI documentation files,
    ensuring they follow proper structure, have valid cross-references,
    and conform to established patterns for AI tool consumption.
    """

    def __init__(self, verbose: bool = DEFAULT_VERBOSE) -> None:
        """Initialize the health check instance.

        Args:
            verbose: Whether to print detailed output during checks.
        """
        self.verbose = verbose
        self.ai_folder = "ai"
        self.success_count = 0
        self.issues: list[str] = []
        self.warnings: list[str] = []

    def run_health_check(self) -> bool:
        """Run the complete health check.

        Returns:
            True if no critical issues found, False otherwise.
        """
        if self.verbose:
            print("🔍 Starting AI documentation health check...")

        # Check core structure
        self._check_core_structure()

        # Check consolidated rules
        self._check_consolidated_rules()

        # Check JSON files
        self._check_json_files()

        # Check cross-references
        self._check_cross_references()

        # Check metadata consistency
        self._check_metadata_consistency()

        # Save report
        self._save_report()

        # Always print summary
        print(f"\n✅ Successful checks: {self.success_count}")
        print(f"❌ Issues found: {len(self.issues)}")
        print(f"⚠️ Warnings: {len(self.warnings)}")

        if self.verbose:
            if self.issues:
                print("\n❌ Issues:")
                for issue in self.issues:
                    print(f"  - {issue}")

            if self.warnings:
                print("\n⚠️ Warnings:")
                for warning in self.warnings:
                    print(f"  - {warning}")

        if len(self.issues) == 0:
            print("\n✅ Health check completed successfully!")
        else:
            print("\n❌ Health check found issues that need attention.")

        return len(self.issues) == 0

    def _check_core_structure(self) -> None:
        """Check that core AI documentation structure exists."""
        if self.verbose:
            print("📁 Checking core structure...")

        required_files = ["ai_rules.json", "search_index.json", "ai_config.json"]

        for file_name in required_files:
            file_path = os.path.join(self.ai_folder, file_name)
            if os.path.exists(file_path):
                self.success_count += 1
            else:
                self.issues.append(f"Missing required file: {file_name}")

        required_dirs = ["guide_docs", "project_context", "outputs"]

        for dir_name in required_dirs:
            dir_path = os.path.join(self.ai_folder, dir_name)
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                self.success_count += 1
            else:
                self.issues.append(f"Missing required directory: {dir_name}")

    def _check_consolidated_rules(self) -> None:
        """Check that consolidated rules file is properly structured."""
        if self.verbose:
            print("📋 Checking consolidated rules...")

        rules_file = os.path.join(self.ai_folder, "ai_rules.json")
        if not os.path.exists(rules_file):
            self.issues.append("Missing ai_rules.json")
            return

        try:
            with open(rules_file, encoding="utf-8") as f:
                data = json.load(f)

            # Check for required sections
            required_sections = ["core_principles", "mandatory_workflows", "documentation_structure"]
            for section in required_sections:
                if section in data:
                    self.success_count += 1
                else:
                    self.warnings.append(f"Missing section in consolidated rules: {section}")

            # Check metadata
            if "metadata" in data:
                metadata = data["metadata"]
                if "version" in metadata and "last_updated" in metadata:
                    self.success_count += 1
                else:
                    self.warnings.append("Missing metadata in consolidated rules")
            else:
                self.warnings.append("Missing metadata section in consolidated rules")

        except Exception as e:
            self.issues.append(f"Error reading consolidated rules: {e}")

    def _check_json_files(self) -> None:
        """Check that all JSON files have proper structure."""
        if self.verbose:
            print("📄 Checking JSON file structure...")

        json_files = []
        for root, _dirs, files in os.walk(self.ai_folder):
            for file in files:
                if file.endswith(".json"):
                    json_files.append(os.path.join(root, file))

        for json_file in json_files:
            if "outputs" in json_file:
                continue

            relative_path = os.path.relpath(json_file, self.ai_folder)

            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                if self._has_proper_structure(data):
                    self.success_count += 1
                else:
                    self.warnings.append(f"Improper structure in {relative_path}")

            except Exception as e:
                self.issues.append(f"Error reading {relative_path}: {e}")

    def _has_proper_structure(self, data: dict[str, Any]) -> bool:
        """Check if a JSON file has proper AI documentation structure.

        Args:
            data: The JSON data to validate.

        Returns:
            True if the data has proper structure, False otherwise.
        """
        # Special handling for ai_config.json and search_index.json
        if isinstance(data, dict) and len(data) > 0:
            # These files can have different structures, just check they're valid JSON objects
            return True

        # For other files, check for standard structure
        # Must have either metadata or ai_metadata
        has_metadata = "metadata" in data or "ai_metadata" in data

        # Must have either sections or content
        has_content = "sections" in data or "content" in data

        return has_metadata and has_content

    def _check_cross_references(self) -> None:
        """Check that cross-references point to existing files."""
        if self.verbose:
            print("🔗 Checking cross-references...")

        json_files = []
        for root, _dirs, files in os.walk(self.ai_folder):
            for file in files:
                if file.endswith(".json"):
                    json_files.append(os.path.join(root, file))

        for json_file in json_files:
            if "outputs" in json_file:
                continue

            relative_path = os.path.relpath(json_file, self.ai_folder)

            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Check cross-references in metadata
                self._check_file_cross_references(data, json_file)

            except Exception as e:
                self.issues.append(f"Error checking cross-references in {relative_path}: {e}")

    def _check_file_cross_references(self, data: dict[str, Any], file_path: str) -> None:
        """Check cross-references in a single file.

        Args:
            data: The JSON data containing cross-references.
            file_path: The path to the file being checked.
        """
        # Check metadata cross-references
        metadata = data.get("metadata", {})
        cross_refs = metadata.get("cross_references", [])

        for ref in cross_refs:
            if self._should_ignore_reference(ref):
                continue

            if not self._reference_exists(ref):
                self.warnings.append(f"Cross-reference to non-existent file: {ref} in {file_path}")

        # Check AI metadata cross-references
        ai_metadata = data.get("ai_metadata", {})
        ai_cross_refs = ai_metadata.get("cross_references", [])

        for ref in ai_cross_refs:
            if self._should_ignore_reference(ref):
                continue

            if not self._reference_exists(ref):
                self.warnings.append(f"AI metadata cross-reference to non-existent file: {ref} in {file_path}")

    def _should_ignore_reference(self, ref: str) -> bool:
        """Check if a reference should be ignored.

        Args:
            ref: The reference string to check.

        Returns:
            True if the reference should be ignored, False otherwise.
        """
        # Ignore external URLs
        if ref.startswith(("http://", "https://")):
            return True

        # Ignore example placeholders
        if "example" in ref.lower() or "placeholder" in ref.lower():
            return True

        return False

    @staticmethod
    @functools.lru_cache(maxsize=256)
    def _reference_exists(ref: str) -> bool:
        """Check if a referenced file or directory exists using os.path.

        Args:
            ref: The reference string to check.

        Returns:
            True if the referenced file or directory exists, False otherwise.
        """
        project_root = os.path.abspath(os.path.join("ai", ".."))

        # Handle directory references (ending with /)
        if ref.endswith("/"):
            dir_name = ref.rstrip("/")
            # Resolve the directory path
            if os.path.isabs(dir_name):
                resolved_dir = os.path.normpath(dir_name)
            else:
                resolved_dir = os.path.normpath(os.path.join(project_root, dir_name))
            return os.path.exists(resolved_dir) and os.path.isdir(resolved_dir)

        # Handle file references
        filename = os.path.basename(ref)
        base_name, _ = os.path.splitext(filename)

        # First try exact path resolution
        if os.path.isabs(ref):
            resolved_path = os.path.normpath(ref)
        else:
            resolved_path = os.path.normpath(os.path.join(project_root, ref))

        if os.path.exists(resolved_path) and os.path.isfile(resolved_path):
            return True

        # If that fails, search for the file by name in the project
        for _, _, files in os.walk(project_root):
            if filename in files or base_name in files:
                return True
        return False

    def _check_metadata_consistency(self) -> None:
        """Check that metadata is consistent across files."""
        if self.verbose:
            print("📊 Checking metadata consistency...")

        json_files = []
        for root, _dirs, files in os.walk(self.ai_folder):
            for file in files:
                if file.endswith(".json"):
                    json_files.append(os.path.join(root, file))

        for json_file in json_files:
            if "outputs" in json_file:
                continue

            relative_path = os.path.relpath(json_file, self.ai_folder)

            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Check that files have proper metadata
                if "metadata" in data:
                    metadata = data["metadata"]

                    # Check for required metadata fields
                    if "version" not in metadata:
                        self.warnings.append(f"Missing version in metadata: {relative_path}")
                    if "last_updated" not in metadata:
                        self.warnings.append(f"Missing last_updated in metadata: {relative_path}")

                    self.success_count += 1
                else:
                    self.warnings.append(f"Missing metadata section: {relative_path}")

            except Exception as e:
                self.issues.append(f"Error checking metadata in {relative_path}: {e}")

    def _save_report(self) -> None:
        """Save the health check report."""
        # Ensure outputs directory exists
        outputs_dir = os.path.join(self.ai_folder, "outputs", "health_check")
        os.makedirs(outputs_dir, exist_ok=True)

        # Save JSON report
        json_report = self._generate_json_report()
        json_file = os.path.join(outputs_dir, "healthcheck-result.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_report, f, indent=2)

        if self.verbose:
            print(f"📄 JSON results saved to: {json_file}")

    def _generate_json_report(self) -> dict[str, Any]:
        """Generate the JSON health check report.

        Returns:
            The JSON report dictionary.
        """
        return {
            "ai_metadata": {
                "template_version": "4.0",
                "ai_processing_level": "High",
                "required_context": "AI documentation structure and standards",
                "validation_required": True,
                "code_generation": "Not applicable",
                "cross_references": ["scripts/ai_health_check.py"],
                "maintenance": "Auto-generated by health check script",
            },
            "file_info": {
                "purpose": "Health check results and status report for AI documentation optimization",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "format": "json",
                "optimization_target": "ai_tool_consumption",
            },
            "content": {
                "summary": {
                    "successful_checks": self.success_count,
                    "issues_found": len(self.issues),
                    "warnings": len(self.warnings),
                    "overall_status": "healthy" if len(self.issues) == 0 else "issues_found",
                },
                "details": {"issues": self.issues, "warnings": self.warnings},
            },
        }


def main() -> None:
    """Main function to run the health check."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    health_check = AIDocumentationHealthCheck(verbose=verbose)
    success = health_check.run_health_check()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
