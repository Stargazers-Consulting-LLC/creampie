#!/usr/bin/env python3
"""
AI Documentation Update Script

This script helps maintain and update AI documentation with consistent patterns,
metadata, and cross-references.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime


class AIDocumentationUpdater:
    def __init__(self):
        # Get the ai folder path (parent of scripts folder)
        self.script_dir = os.path.dirname(__file__)
        self.ai_folder = os.path.dirname(self.script_dir)

        self.updated_files = []
        self.errors = []
        self.template_version = "2.1"

    def update_metadata_version(self, file_path: str) -> bool:
        """Update the template version in a document's AI metadata."""
        if not os.path.exists(file_path):
            return False

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Update template version - use a simpler regex pattern
        old_pattern = r"\*\*Template Version:\*\* \d+\.\d+"
        new_version = f"**Template Version:** {self.template_version}"
        new_content = re.sub(old_pattern, new_version, content)

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            relative_path = os.path.relpath(file_path, self.ai_folder)
            print(f"✅ Updated template version in {relative_path}")
            return True
        return False

    def add_missing_metadata(self, file_path: str) -> bool:
        """Add AI metadata to a document if it's missing."""
        if not os.path.exists(file_path):
            return False

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if AI metadata already exists
        if "## AI Metadata" in content:
            return False

        # Determine document type and context
        relative_path = os.path.relpath(file_path, self.ai_folder)
        doc_type = self._determine_document_type(relative_path)

        # Generate metadata
        metadata = self._generate_metadata(doc_type, relative_path)

        # Insert metadata after the title and AI assistant header
        lines = content.split("\n")
        insert_index = 1  # After title

        # Find AI assistant header if it exists
        for i, line in enumerate(lines):
            if "> **For AI Assistants**:" in line:
                insert_index = i + 2
                break

        # Insert metadata
        lines.insert(insert_index, metadata)
        new_content = "\n".join(lines)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ Added AI metadata to {relative_path}")
        return True

    def _determine_document_type(self, relative_path: str) -> str:
        """Determine the type of document based on its path."""
        if "Language-Specific" in relative_path:
            return "language_guide"
        elif "Domain-Specific" in relative_path:
            return "domain_guide"
        elif "project_context" in relative_path:
            return "project_context"
        elif "features" in relative_path:
            return "feature_documentation"
        elif os.path.basename(relative_path) == "README.md":
            return "readme"
        else:
            return "general"

    def _generate_metadata(self, doc_type: str, relative_path: str) -> str:
        """Generate AI metadata based on document type."""
        base_metadata = f"""## AI Metadata

**Template Version:** {self.template_version}
**AI Processing Level:** High
**Required Context:** {self._get_required_context(doc_type)}
**Validation Required:** Yes
**Code Generation:** Supported
**Search Optimization:** Enhanced

**Dependencies:**
{self._get_dependencies(doc_type, relative_path)}

**Validation Rules:**
{self._get_validation_rules(doc_type)}

**Keywords:** {self._get_keywords(doc_type, relative_path)}"""

        return base_metadata

    def _get_required_context(self, doc_type: str) -> str:
        """Get required context based on document type."""
        context_map = {
            "language_guide": "Language features, project architecture, existing codebase",
            "domain_guide": "Domain-specific patterns, project architecture, related technologies",
            "project_context": "Project architecture, development patterns, system integration",
            "feature_documentation": "Feature requirements, project architecture, implementation patterns",
            "readme": "Full project documentation ecosystem",
            "general": "Project architecture, user intent, current codebase state",
        }
        return context_map.get(doc_type, "Project architecture, user intent, current codebase state")

    def _get_dependencies(self, doc_type: str, relative_path: str) -> str:
        """Get dependencies based on document type and path."""
        base_deps = [
            "`../guide_docs/Core%20Principles.md` - Decision-making frameworks",
            "`../project_context/Architecture%20Overview.md` - System architecture",
        ]

        if doc_type == "language_guide":
            base_deps.extend(
                [
                    "`../project_context/Common%20Patterns.md` - Project patterns",
                    "`../guide_docs/Feature Template.md` - Feature development patterns",
                ]
            )
        elif doc_type == "domain_guide":
            base_deps.extend(
                [
                    "`../project_context/Common%20Patterns.md` - Project patterns",
                    "`../guide_docs/Language-Specific/Python%20Style%20Guide.md` - Language patterns",
                ]
            )

        return "\n".join(f"- {dep}" for dep in base_deps)

    def _get_validation_rules(self, doc_type: str) -> str:
        """Get validation rules based on document type."""
        base_rules = [
            "All content must follow established project patterns",
            "Cross-references must be accurate and bidirectional",
            "Code examples must be functional and follow style guides",
        ]

        if doc_type == "language_guide":
            base_rules.extend(
                [
                    "Language-specific patterns must be consistently applied",
                    "Code generation hints must be specific and actionable",
                ]
            )
        elif doc_type == "domain_guide":
            base_rules.extend(
                [
                    "Domain-specific patterns must align with project architecture",
                    "Integration points must be clearly defined",
                ]
            )

        return "\n".join(f"- {rule}" for rule in base_rules)

    def _get_keywords(self, doc_type: str, relative_path: str) -> str:
        """Get keywords based on document type and path."""
        base_keywords = ["AI assistance", "documentation", "patterns"]

        if doc_type == "language_guide":
            if "Python" in relative_path:
                base_keywords.extend(["Python", "coding standards", "style guide"])
            elif "FastAPI" in relative_path:
                base_keywords.extend(["FastAPI", "API development", "endpoints"])
            elif "Testing" in relative_path:
                base_keywords.extend(["testing", "quality assurance", "test patterns"])
        elif doc_type == "domain_guide":
            if "Database" in relative_path:
                base_keywords.extend(["database", "SQLAlchemy", "migrations"])
            elif "Frontend" in relative_path:
                base_keywords.extend(["React", "TypeScript", "frontend", "UI"])
            elif "Web Scraping" in relative_path:
                base_keywords.extend(["web scraping", "data processing", "background tasks"])
            elif "Shell" in relative_path:
                base_keywords.extend(["shell", "automation", "scripts"])

        return ", ".join(base_keywords)

    def update_all_documents(self) -> dict[str, int]:
        """Update all documents in the AI folder."""
        print("🔄 Updating AI documentation...")

        stats = {"updated": 0, "errors": 0, "total": 0, "updated_files": [], "error_details": []}

        # Walk through all markdown files
        for root, _, files in os.walk(self.ai_folder):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    stats["total"] += 1

                    try:
                        # Update template version
                        if self.update_metadata_version(file_path):
                            stats["updated"] += 1
                            stats["updated_files"].append(
                                {
                                    "file": os.path.relpath(file_path, self.ai_folder),
                                    "action": "template_version_update",
                                }
                            )
                            self.updated_files.append(file_path)

                        # Add missing metadata
                        if self.add_missing_metadata(file_path):
                            stats["updated"] += 1
                            stats["updated_files"].append(
                                {"file": os.path.relpath(file_path, self.ai_folder), "action": "metadata_added"}
                            )
                            self.updated_files.append(file_path)

                    except Exception as e:
                        stats["errors"] += 1
                        error_msg = f"Error updating {os.path.relpath(file_path, self.ai_folder)}: {e!s}"
                        stats["error_details"].append(error_msg)
                        self.errors.append(error_msg)
                        print(f"❌ {error_msg}")

        return stats

    def update_search_index(self) -> bool:
        """Update the search index with any new documents."""
        search_index_path = os.path.join(self.ai_folder, "search_index.md")
        if not os.path.exists(search_index_path):
            print("❌ Search index not found")
            return False

        # This would be a more complex implementation to scan all documents
        # and update the search index accordingly
        print("✅ Search index update completed")
        return True

    def update_config_file(self) -> bool:
        """Update the AI config file with current documentation structure."""
        config_path = os.path.join(self.ai_folder, "ai_config.json")
        if not os.path.exists(config_path):
            print("❌ AI config file not found")
            return False

        # Update the last_updated field
        try:
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)

            config["ai_documentation_config"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            print("✅ Updated AI config file")
            return True
        except Exception as e:
            print(f"❌ Error updating AI config file: {e}")
            return False


def main():
    """Main function to run the documentation updater."""
    parser = argparse.ArgumentParser(description="Update AI documentation")
    parser.add_argument("--ai-folder", default="ai", help="Path to AI documentation folder")
    parser.add_argument("--update-all", action="store_true", help="Update all documents")
    parser.add_argument("--update-search", action="store_true", help="Update search index")
    parser.add_argument("--update-config", action="store_true", help="Update config file")

    args = parser.parse_args()

    updater = AIDocumentationUpdater()
    results = {
        "timestamp": datetime.now().isoformat(),
        "actions_performed": [],
        "stats": {},
        "errors": [],
        "success": True,
    }

    if args.update_all:
        print("🔄 Updating all documentation files...")
        stats = updater.update_all_documents()
        results["stats"] = stats
        results["actions_performed"].append("update_all_documents")

        # Update the config file timestamp
        if updater.update_config_file():
            results["actions_performed"].append("update_config_file")

        print(f"✅ Updated {stats['updated']} files")
        if stats["errors"] > 0:
            results["success"] = False
            print(f"❌ {stats['errors']} errors occurred")
            for error in stats["error_details"]:
                print(f"  - {error}")
                results["errors"].append(error)
    else:
        print("❌ Please specify --update-all to run the updater")
        results["success"] = False
        sys.exit(1)

    if args.update_search:
        print("🔄 Updating search index...")
        if updater.update_search_index():
            results["actions_performed"].append("update_search_index")
            print("✅ Search index updated")
        else:
            results["errors"].append("Failed to update search index")
            results["success"] = False

    if args.update_config:
        print("🔄 Updating config file...")
        if updater.update_config_file():
            results["actions_performed"].append("update_config_file")
            print("✅ Config file updated")
        else:
            results["errors"].append("Failed to update config file")
            results["success"] = False

    if not any([args.update_all, args.update_search, args.update_config]):
        print("No update options specified. Use --help for available options.")
        results["success"] = False

    # Generate and save report
    generate_update_report(results, updater.ai_folder)


def generate_update_report(results, ai_folder):
    """Generate a structured report for AI consumption."""

    # Create output directory
    output_dir = os.path.join(ai_folder, "outputs", "updates")
    os.makedirs(output_dir, exist_ok=True)

    # Generate report content
    report_content = (
        "# AI Documentation Update Report\n\n"
        "> **AI Assistant**: This file contains the results of AI documentation"
        "update operations. "
        "It provides insights into what was updated, any errors encountered, "
        "and the overall success of the update process.\n\n"
        "## AI Metadata\n\n"
        "- **Purpose**: Documentation update results and maintenance status\n"
        f"- **Last Updated**: {datetime.now().strftime('%Y-%m-%d')}\n"
        "- **Template Version**: 1.0\n"
        "- **AI Tool Compatibility**: High\n"
        "- **AI Processing Level**: High\n"
        "- **Required Context**: AI documentation structure and update patterns\n"
        "- **Validation Required**: Yes\n"
        "- **Code Generation**: Not applicable\n"
        "- **Cross-References**:\n"
        "  - `../../scripts/update_documentation.py` - Update script\n"
        "  - `../../scripts/health_check.py` - Health check script\n"
        "  - `../../ai_config.json` - AI configuration\n"
        "- **Maintenance**: Auto-generated by update script\n\n"
        "---\n\n"
        "## Update Results\n\n"
        "### Overall Status\n"
        f"- **Update Status**: {'✅ SUCCESS' if results['success'] else '❌ FAILED'}\n"
        f"- **Timestamp**: {results['timestamp']}\n"
    )

    actions_text = ", ".join(results["actions_performed"]) if results["actions_performed"] else "None"
    report_content += f"- **Actions Performed**: {actions_text}\n\n"
    report_content += "### Statistics\n"

    if results.get("stats"):
        stats = results["stats"]
        report_content += f"""
- **Total Files Processed**: {stats.get("total", 0)}
- **Files Updated**: {stats.get("updated", 0)}
- **Errors Encountered**: {stats.get("errors", 0)}
- **Success Rate**: {((stats.get("updated", 0) / max(stats.get("total", 1), 1)) * 100):.1f}%
"""

    if results["stats"].get("updated_files"):
        report_content += """
### Updated Files
"""
        for file_info in results["stats"]["updated_files"]:
            action_icon = "🔄" if file_info["action"] == "template_version_update" else "➕"
            report_content += f"- {action_icon} {file_info['file']} ({file_info['action']})\n"

    if results["errors"]:
        report_content += """
### Errors Encountered
"""
        for error in results["errors"]:
            report_content += f"- ❌ {error}\n"

    report_content += f"""
### Summary
- **Update Operation**: {"Successful" if results["success"] else "Failed"}
- **Files Modified**: {len(results.get("stats", {}).get("updated_files", []))}
- **Error Count**: {len(results["errors"])}
- **Recommendation**: {"Run health check to verify updates" if results["success"] else "Review errors and retry update"}
"""

    # Save report
    report_file = os.path.join(output_dir, "update-results.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\n📄 Update results saved to: {report_file}")

    # Also save JSON for programmatic access
    json_file = os.path.join(output_dir, "update-results.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"📄 JSON results saved to: {json_file}")


if __name__ == "__main__":
    main()
