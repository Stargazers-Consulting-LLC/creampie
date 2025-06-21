#!/usr/bin/env python3
"""
Dynamic Integration Script for AI Documentation

This script automatically extracts patterns from source guides and integrates them
into core principles without requiring manual string updates. It maintains
consistency across the documentation system.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any


class DynamicIntegration:
    def __init__(self, verbose=False):
        self.script_dir = os.path.dirname(__file__)
        self.project_root = os.path.dirname(self.script_dir)
        self.ai_folder = os.path.join(self.project_root, "ai")

        self.changes_made = []
        self.conflicts_resolved = []
        self.errors = []
        self.verbose = verbose

        # Load integration configuration
        self.integration_rules = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load the AI configuration file."""
        config_path = os.path.join(self.ai_folder, "ai_config.json")
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def run_integration(self, trigger: str = "manual_request") -> bool:
        """Run the complete dynamic integration process."""
        if self.verbose:
            print(f"🔄 Running Dynamic Integration (trigger: {trigger})...")
            print()

        if not self.integration_rules.get("enabled", False):
            if self.verbose:
                print("❌ Dynamic integration is disabled in config")
            return False

        try:
            # Extract patterns from source guides
            extracted_patterns = self._extract_patterns_from_guides()

            # Validate extracted patterns
            validated_patterns = self._validate_patterns(extracted_patterns)

            # Resolve conflicts
            resolved_patterns = self._resolve_conflicts(validated_patterns)

            # Update core principles
            success = self._update_core_principles(resolved_patterns)

            # Generate integration report
            self._generate_integration_report(trigger)

            return success

        except Exception as e:
            self.errors.append(f"Integration failed: {e}")
            print(f"❌ Integration failed: {e}")
            return False

    def _extract_patterns_from_guides(self) -> dict[str, Any]:
        """Extract patterns from source guides based on integration rules."""
        if self.verbose:
            print("📖 Extracting patterns from source guides...")

        extracted_patterns = {}
        extraction_rules = self.integration_rules.get("pattern_extraction", {}).get("extraction_rules", {})

        for guide_name, rules in extraction_rules.items():
            guide_path = self._get_guide_path(guide_name)
            if not guide_path or not os.path.exists(guide_path):
                if self.verbose:
                    print(f"⚠️  Guide not found: {guide_name}")
                continue

            try:
                guide_data = self._load_guide(guide_path)
                patterns = self._extract_patterns_from_guide(guide_data, rules)
                extracted_patterns[guide_name] = patterns
                if self.verbose:
                    print(f"✅ Extracted patterns from: {guide_name}")

            except Exception as e:
                self.errors.append(f"Error extracting from {guide_name}: {e}")
                if self.verbose:
                    print(f"❌ Error extracting from {guide_name}: {e}")

        return extracted_patterns

    def _get_guide_path(self, guide_name: str) -> str | None:
        """Get the file path for a guide based on its name."""
        guide_mapping = {
            "python_style_guide": "guide_docs/language_specific/python_style_guide.json",
            "fastapi_development_guide": "guide_docs/language_specific/fastapi_development_guide.json",
            "database_management_guide": "guide_docs/domain_specific/database_management_guide.json",
            "shell_style_guide": "guide_docs/domain_specific/shell_style_guide.json"
        }

        relative_path = guide_mapping.get(guide_name)
        if relative_path:
            return os.path.join(self.ai_folder, relative_path)
        return None

    def _load_guide(self, guide_path: str) -> dict[str, Any]:
        """Load a guide file and return its content."""
        with open(guide_path, encoding="utf-8") as f:
            return json.load(f)

    def _extract_patterns_from_guide(self, guide_data: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
        """Extract specific patterns from a guide based on extraction rules."""
        patterns = {}
        critical_patterns = rules.get("critical_patterns", [])
        sections = guide_data.get("sections", {})

        for pattern_name in critical_patterns:
            # Look for pattern in sections
            pattern_content = self._find_pattern_in_sections(sections, pattern_name)
            if pattern_content:
                patterns[pattern_name] = pattern_content

        return patterns

    def _find_pattern_in_sections(self, sections: dict[str, Any], pattern_name: str) -> dict[str, Any] | None:
        """Find a specific pattern within guide sections."""
        # Direct section match
        if pattern_name in sections:
            return sections[pattern_name]

        # Search within section content
        for section_name, section_data in sections.items():
            if isinstance(section_data, dict):
                # Check if this section contains the pattern
                if pattern_name in section_data.get("content", "").lower():
                    return {
                        "section": section_name,
                        "content": section_data.get("content", ""),
                        "description": section_data.get("description", "")
                    }

        return None

    def _validate_patterns(self, extracted_patterns: dict[str, Any]) -> dict[str, Any]:
        """Validate extracted patterns for consistency and completeness."""
        if self.verbose:
            print("🔍 Validating extracted patterns...")

        validated_patterns = {}

        for guide_name, patterns in extracted_patterns.items():
            validated_patterns[guide_name] = {}

            for pattern_name, pattern_data in patterns.items():
                if self._validate_single_pattern(pattern_name, pattern_data):
                    validated_patterns[guide_name][pattern_name] = pattern_data
                    if self.verbose:
                        print(f"✅ Validated: {guide_name}.{pattern_name}")
                else:
                    if self.verbose:
                        print(f"⚠️  Invalid pattern: {guide_name}.{pattern_name}")

        return validated_patterns

    def _validate_single_pattern(self, pattern_name: str, pattern_data: Any) -> bool:
        """Validate a single pattern."""
        if not pattern_data:
            return False

        # Basic validation - pattern should have content
        if isinstance(pattern_data, dict):
            return bool(pattern_data.get("content") or pattern_data.get("description"))
        elif isinstance(pattern_data, str):
            return bool(pattern_data.strip())

        return False

    def _resolve_conflicts(self, validated_patterns: dict[str, Any]) -> dict[str, Any]:
        """Resolve conflicts between patterns from different guides."""
        if self.verbose:
            print("⚖️  Resolving pattern conflicts...")

        resolved_patterns = {}
        conflicts = []

        # Group patterns by category
        pattern_categories = {}
        for guide_name, patterns in validated_patterns.items():
            for pattern_name, pattern_data in patterns.items():
                category = self._categorize_pattern(pattern_name)
                if category not in pattern_categories:
                    pattern_categories[category] = []
                pattern_categories[category].append({
                    "guide": guide_name,
                    "name": pattern_name,
                    "data": pattern_data
                })

        # Resolve conflicts within each category
        for category, patterns in pattern_categories.items():
            if len(patterns) > 1:
                # Multiple patterns in same category - resolve conflict
                resolved = self._resolve_category_conflict(category, patterns)
                if resolved:
                    resolved_patterns[category] = resolved
                    conflicts.append(f"Resolved conflict in {category}")
            else:
                # Single pattern - no conflict
                resolved_patterns[category] = patterns[0]["data"]

        self.conflicts_resolved.extend(conflicts)
        return resolved_patterns

    def _categorize_pattern(self, pattern_name: str) -> str:
        """Categorize a pattern based on its name."""
        category_mapping = {
            "module_documentation": "documentation_patterns",
            "import_organization": "code_organization",
            "type_hints": "code_quality",
            "error_handling": "error_handling",
            "file_operations": "file_operations",
            "logging_setup": "logging_patterns",
            "database_patterns": "database_patterns",
            "fastapi_patterns": "api_patterns",
            "testing_patterns": "testing_patterns",
            "security_patterns": "security_patterns"
        }

        return category_mapping.get(pattern_name, "general_patterns")

    def _resolve_category_conflict(self, category: str, patterns: list[dict[str, Any]]) -> dict[str, Any] | None:
        """Resolve conflicts within a pattern category."""
        # Priority-based resolution
        priority_order = ["python_style_guide", "fastapi_development_guide", "database_management_guide"]

        for priority_guide in priority_order:
            for pattern in patterns:
                if pattern["guide"] == priority_guide:
                    return pattern["data"]

        # If no priority match, use the first one
        return patterns[0]["data"] if patterns else None

    def _update_core_principles(self, resolved_patterns: dict[str, Any]) -> bool:
        """Update core principles with resolved patterns."""
        if self.verbose:
            print("📝 Updating core principles...")

        core_principles_path = os.path.join(self.ai_folder, "guide_docs", "core_principles.json")

        try:
            # Load current core principles
            with open(core_principles_path, encoding="utf-8") as f:
                core_data = json.load(f)

            # Update sections with new patterns
            sections = core_data.get("sections", {})
            updated = False

            for category, pattern_data in resolved_patterns.items():
                section_name = self._get_core_section_name(category)
                if section_name and section_name not in sections:
                    sections[section_name] = {
                        "title": self._format_section_title(category),
                        "description": f"Dynamically integrated patterns for {category}",
                        "content": self._format_pattern_content(pattern_data),
                        "source": "dynamic_integration",
                        "last_updated": datetime.now().isoformat()
                    }
                    updated = True
                    self.changes_made.append(f"Added section: {section_name}")
                    if self.verbose:
                        print(f"✅ Added section: {section_name}")

            # Update metadata
            if updated:
                core_data["metadata"]["last_updated"] = datetime.now().isoformat()
                core_data["metadata"]["version"] = self._increment_version(core_data["metadata"].get("version", "1.0"))

                # Save updated core principles
                with open(core_principles_path, "w", encoding="utf-8") as f:
                    json.dump(core_data, f, indent=2, ensure_ascii=False)

                if self.verbose:
                    print("✅ Core principles updated successfully")
                return True
            else:
                if self.verbose:
                    print("ℹ️  No updates needed")
                return True

        except Exception as e:
            self.errors.append(f"Error updating core principles: {e}")
            if self.verbose:
                print(f"❌ Error updating core principles: {e}")
            return False

    def _get_core_section_name(self, category: str) -> str | None:
        """Get the appropriate section name in core principles for a category."""
        section_mapping = {
            "documentation_patterns": "documentation_patterns",
            "code_organization": "code_organization_patterns",
            "code_quality": "code_quality_patterns",
            "error_handling": "error_handling_patterns",
            "file_operations": "file_operations_patterns",
            "logging_patterns": "logging_patterns",
            "database_patterns": "database_patterns",
            "api_patterns": "api_patterns",
            "testing_patterns": "testing_patterns",
            "security_patterns": "security_patterns"
        }

        return section_mapping.get(category)

    def _format_section_title(self, category: str) -> str:
        """Format a category name into a proper section title."""
        return category.replace("_", " ").title()

    def _format_pattern_content(self, pattern_data: Any) -> str:
        """Format pattern data into readable content."""
        if isinstance(pattern_data, dict):
            content = pattern_data.get("content", "")
            description = pattern_data.get("description", "")
            if description:
                return f"{description}\n\n{content}"
            return content
        elif isinstance(pattern_data, str):
            return pattern_data
        else:
            return str(pattern_data)

    def _increment_version(self, version: str) -> str:
        """Increment version number."""
        MIN_VERSION_PARTS = 2
        try:
            parts = version.split(".")
            if len(parts) >= MIN_VERSION_PARTS:
                major, minor = parts[0], parts[1]
                new_minor = str(int(minor) + 1)
                return f"{major}.{new_minor}"
        except (ValueError, IndexError):
            pass
        return "1.1"

    def _generate_integration_report(self, trigger: str):
        """Generate a comprehensive integration report."""
        if self.verbose:
            print("📊 Generating integration report...")

        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "trigger": trigger,
                "status": "completed" if not self.errors else "failed"
            },
            "summary": {
                "changes_made": len(self.changes_made),
                "conflicts_resolved": len(self.conflicts_resolved),
                "errors": len(self.errors)
            },
            "details": {
                "changes": self.changes_made,
                "conflicts": self.conflicts_resolved,
                "errors": self.errors
            }
        }

        # Save report
        output_dir = os.path.join(self.ai_folder, "outputs", "dynamic_integration")
        os.makedirs(output_dir, exist_ok=True)

        report_path = os.path.join(output_dir, "integration-report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        if self.verbose:
            print(f"📄 Integration report saved to: {report_path}")

        # Print summary
        if self.verbose:
            print("\n📊 Integration Summary:")
            print(f"   Changes made: {len(self.changes_made)}")
            print(f"   Conflicts resolved: {len(self.conflicts_resolved)}")
            print(f"   Errors: {len(self.errors)}")


def main():
    """Main entry point for the dynamic integration script."""
    trigger = sys.argv[1] if len(sys.argv) > 1 else "manual_request"
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    integrator = DynamicIntegration(verbose=verbose)
    success = integrator.run_integration(trigger)

    # Only show success/failure messages if verbose or if there are changes/errors
    has_changes = len(integrator.changes_made) > 0 or len(integrator.errors) > 0

    if verbose or has_changes:
        if success:
            print("\n✅ Dynamic integration completed successfully")
        else:
            print("\n❌ Dynamic integration failed")

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
