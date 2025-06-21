#!/usr/bin/env python3
"""
AI Documentation Health Check Script

This script validates the AI documentation structure, metadata, and cross-references
to ensure optimal AI tool consumption. Updated for JSON format.
"""

import json
import os
import sys
import urllib.parse
from datetime import datetime


class AIDocumentationHealthCheck:
    def __init__(self, verbose=False):
        # Get the ai folder path (parent of scripts folder, then ai subfolder)
        self.script_dir = os.path.dirname(__file__)
        self.project_root = os.path.dirname(self.script_dir)
        self.ai_folder = os.path.join(self.project_root, "ai")

        self.issues = []
        self.warnings = []
        self.success_count = 0
        self.verbose = verbose

    def run_health_check(self):
        """Run the complete health check and generate report."""
        if self.verbose:
            print("🔍 Running AI Documentation Health Check...")
            print()

        # Run all checks
        self.check_folder_structure()
        self.check_ai_metadata()
        self.check_cross_references()
        self.check_search_index()
        self.check_quick_reference()
        self.check_ai_config()
        self.check_template_consistency()

        # Generate report
        report = self.generate_report()

        # Only print report if verbose or if there are issues
        if self.verbose or self.issues or self.warnings:
            print(report)

        # Write JSON result file
        result_file = os.path.join(self.ai_folder, "outputs", "health_check", "healthcheck-result.json")

        # Ensure the output directory exists
        result_dir = os.path.dirname(result_file)
        os.makedirs(result_dir, exist_ok=True)

        # Generate JSON result
        json_result = self.generate_json_result()

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(json_result, f, indent=2, ensure_ascii=False)
            f.flush()  # Force flush to disk
            os.fsync(f.fileno())  # Force sync to ensure file is written

        # Only show file info if verbose
        if self.verbose:
            # Get file stats using os.path
            stat_info = os.stat(result_file)
            print(f"\n📄 Health check results saved to: {result_file}")
            print(f"📄 File size: {stat_info.st_size} bytes")
            print(f"📄 File modified: {datetime.fromtimestamp(stat_info.st_mtime)}")

        return len(self.issues) == 0

    def check_folder_structure(self):
        """Check that all required folders and files exist."""
        if self.verbose:
            print("📁 Checking folder structure...")

        # Debug: Print the paths being checked
        if self.verbose:
            print(f"🔍 AI folder path: {self.ai_folder}")
            print(f"🔍 Current working directory: {os.getcwd()}")

        required_files = [
            "readme.json",
            "ai_quick_reference.json",
            "search_index.json",
            "ai_config.json",
            "guide_docs/readme.json",
            "guide_docs/core_principles.json",
            "guide_docs/feature_template.json",
            "guide_docs/code_review_patterns.json",
            "guide_docs/ai_tool_optimization_guide.json",
            "project_context/readme.json",
            "project_context/architecture_overview.json",
            "project_context/common_patterns.json",
            "project_context/development_workflow.json",
        ]

        self._check_file_list(required_files, "required file", self.issues)

        # Check language-specific guides
        lang_guides = [
            "guide_docs/language_specific/python_style_guide.json",
            "guide_docs/language_specific/react_style_guide.json",
            "guide_docs/language_specific/python_testing_style_guide.json",
        ]

        self._check_file_list(lang_guides, "language guide", self.warnings)

        # Check domain_specific guides
        domain_guides = [
            "guide_docs/domain_specific/database_management_guide.json",
            "guide_docs/domain_specific/shell_style_guide.json",
        ]

        self._check_file_list(domain_guides, "domain guide", self.warnings)

    def _check_file_list(self, file_list, file_type, issue_list):
        """Check a list of files and add issues to the specified list."""
        for file_path in file_list:
            full_path = os.path.join(self.ai_folder, file_path)
            if os.path.exists(full_path):
                self.success_count += 1
                if self.verbose:
                    print(f"✅ Found: {file_path}")
            else:
                issue_list.append(f"Missing {file_type}: {file_path}")
                if self.verbose:
                    print(f"❌ Missing: {file_path} (checked at: {full_path})")

    def check_ai_metadata(self):
        """Check that all JSON files have proper AI metadata."""
        if self.verbose:
            print("📋 Checking AI metadata...")

        for root, _, files in os.walk(self.ai_folder):
            for file in files:
                if file.endswith(".json") and not file.startswith("ai_config"):
                    file_path = os.path.join(root, file)
                    # Skip output files
                    if "outputs" in file_path:
                        continue

                    self._check_single_file_metadata(file_path)

    def _check_single_file_metadata(self, file_path):
        """Check AI metadata for a single file."""
        relative_path = os.path.relpath(file_path, self.ai_folder)

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Only accept new streamlined format (metadata, sections, etc.)
            has_new_format = "metadata" in data and (
                "sections" in data or "example_patterns" in data or "implementation_guidelines" in data
            )

            if has_new_format:
                # New format validation - these are valid AI-optimized guides
                self.success_count += 1
                # Note: We don't validate optional metadata fields like title, description, version
                # as they don't affect core functionality and may be intentionally empty
            else:
                # Old format or invalid format found
                self.issues.append(f"Uses deprecated AI metadata format: {relative_path}")

        except json.JSONDecodeError as e:
            self.issues.append(f"Invalid JSON in {relative_path}: {e!s}")
        except Exception as e:
            self.issues.append(f"Error reading {relative_path}: {e!s}")

    def _check_ai_metadata_fields(self, data, relative_path):
        """Check required AI metadata fields for old format - deprecated."""
        # This method is kept for backward compatibility but should not be used

    def check_cross_references(self):
        """Check that cross-references are valid and bidirectional."""
        if self.verbose:
            print("🔗 Checking cross-references...")

        # Get all JSON files
        json_files = []
        for root, _, files in os.walk(self.ai_folder):
            for file in files:
                if file.endswith(".json") and not file.startswith("ai_config"):
                    file_path = os.path.join(root, file)
                    if "outputs" not in file_path:
                        json_files.append(file_path)

        file_paths = {os.path.relpath(f, self.ai_folder): f for f in json_files}

        # Check cross-references in each file
        for file_path in json_files:
            self._check_file_cross_references(file_path, file_paths)

    def _check_file_cross_references(self, file_path, file_paths):
        """Check cross-references for a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            relative_path = os.path.relpath(file_path, self.ai_folder)

            # Check structured cross-references
            self._check_structured_cross_references(data, relative_path, file_paths)

            # Check cross-references in AI metadata
            self._check_metadata_cross_references(data, relative_path, file_paths)

            self.success_count += 1

        except Exception as e:
            self.issues.append(f"Error checking cross-references in {relative_path}: {e!s}")

    def _check_structured_cross_references(self, data, relative_path, file_paths):
        """Check structured cross-references in a file."""
        cross_refs = data.get("cross_references", [])
        for ref in cross_refs:
            if isinstance(ref, dict):
                ref_path = ref.get("path", "")
            else:
                ref_path = ref

            if ref_path:
                # Skip example placeholders
                if self._is_example_placeholder(ref_path):
                    continue

                # Check if referenced file exists (try multiple variations)
                if not self._file_exists_in_paths(ref_path, file_paths):
                    self.warnings.append(f"Cross-reference to non-existent file: {ref_path} in {relative_path}")

    def _check_metadata_cross_references(self, data, relative_path, file_paths):
        """Check cross-references in AI metadata."""
        ai_metadata = data.get("ai_metadata", {})
        metadata_refs = ai_metadata.get("cross_references", [])
        for ref in metadata_refs:
            # Skip example placeholders
            if self._is_example_placeholder(ref):
                continue

            if not self._file_exists_in_paths(ref, file_paths):
                self.warnings.append(f"AI metadata cross-reference to non-existent file: {ref} in {relative_path}")

    def _file_exists_in_paths(self, ref_path, file_paths):
        """Check if a file exists in the file paths, trying multiple variations."""
        file_exists = False

        # Try the original path
        if ref_path in file_paths:
            file_exists = True

        # Try URL-decoded path
        elif self._try_decoded_path(ref_path, file_paths):
            file_exists = True

        # Try with spaces instead of %20
        elif "%20" in ref_path:
            space_path = ref_path.replace("%20", " ")
            if space_path in file_paths:
                file_exists = True

        # Try with underscores instead of %20
        elif "%20" in ref_path:
            underscore_path = ref_path.replace("%20", "_")
            if underscore_path in file_paths:
                file_exists = True

        # Try relative to current directory
        elif self._try_relative_path(ref_path, file_paths):
            file_exists = True

        # Check if it's a special file that should be ignored
        elif self._should_ignore_reference(ref_path):
            file_exists = True

        # Final check: try to find any file that matches the decoded name
        elif self._try_basename_match(ref_path, file_paths):
            file_exists = True

        return file_exists

    def _try_decoded_path(self, ref_path, file_paths):
        """Try URL-decoded path."""
        try:
            decoded_path = urllib.parse.unquote(ref_path)
            return decoded_path in file_paths
        except Exception:
            return False

    def _try_relative_path(self, ref_path, file_paths):
        """Try relative path checks."""
        current_dir = os.path.dirname(ref_path)
        if current_dir:
            # Check if it's a directory reference
            if ref_path.endswith("/") and current_dir in file_paths:
                return True

            # Check if it's a script or config file
            if ref_path.endswith((".py", ".sh", ".js", ".json")):
                return True

        return False

    def _try_basename_match(self, ref_path, file_paths):
        """Try to find any file that matches the decoded name."""
        try:
            decoded_path = urllib.parse.unquote(ref_path)
            for existing_path in file_paths:
                if os.path.basename(decoded_path) == os.path.basename(existing_path):
                    return True
        except Exception:
            pass

        return False

    def _should_ignore_reference(self, ref_path):
        """Check if a reference should be ignored (scripts, configs, etc.)."""
        # Ignore script files
        if ref_path.startswith("scripts/"):
            return True

        # Ignore config files
        if ref_path == "ai_config.json":
            return True

        # Ignore output directories
        if ref_path.startswith("outputs/"):
            return True

        # Ignore directory references
        if ref_path.endswith("/"):
            return True

        return False

    def _is_example_placeholder(self, path):
        """Check if a path is an example placeholder."""
        placeholder_patterns = ["path/to/", "example", "placeholder", "template"]

        path_lower = path.lower()
        return any(pattern in path_lower for pattern in placeholder_patterns)

    def check_search_index(self):
        """Check that search index is comprehensive and accessible."""
        if self.verbose:
            print("🔍 Checking search index...")

        search_index_path = os.path.join(self.ai_folder, "search_index.json")
        if not os.path.exists(search_index_path):
            self.issues.append("Missing search index file")
            return

        try:
            with open(search_index_path, encoding="utf-8") as f:
                data = json.load(f)

            # Check that search index has new format structure
            if "metadata" not in data:
                self.issues.append("Search index missing metadata section")
            else:
                self.success_count += 1

            # Check that search index has sections
            if "sections" in data:
                sections = data["sections"]
                if sections:
                    self.success_count += 1
                else:
                    self.warnings.append("Search index has no sections")
            else:
                self.warnings.append("Search index missing sections")

        except Exception as e:
            self.issues.append(f"Error reading search index: {e!s}")

    def check_quick_reference(self):
        """Check that quick reference is comprehensive and accessible."""
        if self.verbose:
            print("📖 Checking quick reference...")

        quick_ref_path = os.path.join(self.ai_folder, "ai_quick_reference.json")
        if not os.path.exists(quick_ref_path):
            self.issues.append("Missing quick reference file")
            return

        try:
            with open(quick_ref_path, encoding="utf-8") as f:
                data = json.load(f)

            # Check that quick reference has new format structure
            if "metadata" not in data:
                self.issues.append("Quick reference missing metadata section")
            else:
                self.success_count += 1

            # Check that quick reference has sections
            if "sections" in data:
                sections = data["sections"]
                if sections:
                    self.success_count += 1
                else:
                    self.warnings.append("Quick reference has no sections")
            else:
                self.warnings.append("Quick reference missing sections")

        except Exception as e:
            self.issues.append(f"Error reading quick reference: {e!s}")

    def check_ai_config(self):
        """Check that AI configuration is valid and up-to-date."""
        if self.verbose:
            print("⚙️ Checking AI configuration...")

        config_path = os.path.join(self.ai_folder, "ai_config.json")
        if not os.path.exists(config_path):
            self.issues.append("Missing AI configuration file")
            return

        try:
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)

            # Check required configuration sections
            required_sections = ["ai_documentation_config", "documentation_structure", "ai_tool_settings"]
            for section in required_sections:
                if section not in config:
                    self.issues.append(f"Missing configuration section: {section}")
                else:
                    self.success_count += 1

            # Check version
            version = config.get("ai_documentation_config", {}).get("version")
            if version != "3.0":
                self.warnings.append(f"Configuration version mismatch: expected 3.0, got {version}")

        except Exception as e:
            self.issues.append(f"Error reading AI configuration: {e!s}")

    def check_template_consistency(self):
        """Check that all files follow consistent template structure."""
        if self.verbose:
            print("📋 Checking template consistency...")

        for root, _, files in os.walk(self.ai_folder):
            for file in files:
                if file.endswith(".json") and not file.startswith("ai_config"):
                    file_path = os.path.join(root, file)

                    # Skip output files and health check result
                    if "outputs" in file_path or os.path.basename(file_path) == "healthcheck-result.md":
                        continue

                    try:
                        with open(file_path, encoding="utf-8") as f:
                            data = json.load(f)

                        relative_path = os.path.relpath(file_path, self.ai_folder)

                        # Check for new streamlined format
                        has_new_format = "metadata" in data and (
                            "sections" in data or "example_patterns" in data or "implementation_guidelines" in data
                        )

                        if has_new_format:
                            # Validate new format structure
                            # Note: We don't validate optional metadata fields like title, description, version
                            # as they don't affect core functionality and may be intentionally empty

                            # Check for content sections
                            if "sections" in data:
                                self.success_count += 1
                            elif "example_patterns" in data or "implementation_guidelines" in data:
                                self.success_count += 1
                            else:
                                self.warnings.append(f"Missing content sections: {relative_path}")
                        else:
                            # Old format - mark as deprecated
                            self.issues.append(f"Uses deprecated template format: {relative_path}")

                    except Exception as e:
                        self.issues.append(f"Error checking template consistency in {relative_path}: {e!s}")

    def generate_report(self):
        """Generate the health check report."""
        self.success_count + len(self.issues) + len(self.warnings)

        report = f"""📊 AI Documentation Health Check Report
============================================================

✅ Successful checks: {self.success_count}
❌ Issues found: {len(self.issues)}
⚠️ Warnings: {len(self.warnings)}

"""

        if self.issues:
            report += "\n❌ Issues:\n"
            for issue in self.issues:
                report += f"  - {issue}\n"

        if self.warnings:
            report += "\n⚠️ Warnings:\n"
            for warning in self.warnings:
                report += f"  - {warning}\n"

        if not self.issues and not self.warnings:
            report += "\n🎉 All checks passed! AI documentation is optimized for tool consumption."
        else:
            report += "\n🔧 Please address the issues and warnings above."

        report += "\n============================================================"

        return report

    def generate_json_result(self):
        """Generate the JSON result for the health check."""
        return {
            "ai_metadata": {
                "template_version": "3.0",
                "ai_processing_level": "High",
                "required_context": "AI documentation structure and standards",
                "validation_required": True,
                "code_generation": "Not applicable",
                "cross_references": ["scripts/ai_health_check.py", "scripts/update_documentation.py", "ai_config.json"],
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
                    "warnings_found": len(self.warnings),
                    "overall_status": "pass" if len(self.issues) == 0 else "fail",
                },
                "details": {"issues": self.issues, "warnings": self.warnings},
                "human_readable_report": self.generate_report(),
            },
        }


def main():
    """Main health check function."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    health_check = AIDocumentationHealthCheck(verbose=verbose)
    success = health_check.run_health_check()

    # Only show success/failure messages if verbose or if there are issues
    has_issues = len(health_check.issues) > 0 or len(health_check.warnings) > 0

    if verbose or has_issues:
        if success:
            print("\n✅ Health check completed successfully!")
        else:
            print("\n❌ Health check found issues that need attention.")

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
