#!/usr/bin/env python3
"""
Pre-commit Hook for Dynamic Integration and Health Check

This script runs as a Git pre-commit hook to automatically trigger:
1. AI documentation health check
2. Dynamic integration when AI documentation guides are modified

It ensures that core principles stay synchronized with source guides and
maintains documentation quality.
"""

import os
import subprocess
import sys


class PreCommitHook:
    def __init__(self):
        self.script_dir = os.path.dirname(__file__)
        self.project_root = os.path.dirname(self.script_dir)
        self.ai_folder = os.path.join(self.project_root, "ai")

        # AI documentation files that should trigger integration
        self.ai_doc_patterns = [
            "ai/guide_docs/language_specific/",
            "ai/guide_docs/domain_specific/",
            "ai/guide_docs/core_principles.json",
            "ai/ai_config.json",
        ]

        # Files that should NOT trigger integration (to avoid loops)
        self.exclude_patterns = ["ai/outputs/", "ai/features/", "*.pyc", "__pycache__"]

    def run(self) -> bool:
        """Run the pre-commit hook."""
        print("🔍 Pre-commit hook: Checking AI documentation...")

        try:
            # Always run health check first
            print("📋 Running AI documentation health check...")
            health_check_success = self._run_health_check()

            if not health_check_success:
                print("❌ Health check failed - commit blocked")
                return False

            # Get staged files
            staged_files = self._get_staged_files()

            # Check if any AI documentation files are modified
            ai_files_modified = self._check_ai_files_modified(staged_files)

            if ai_files_modified:
                print("📝 AI documentation files modified - triggering dynamic integration...")

                # Run dynamic integration
                integration_success = self._run_dynamic_integration()

                if integration_success:
                    print("✅ Dynamic integration completed successfully")
                    return True
                else:
                    print("❌ Dynamic integration failed - commit blocked")
                    return False
            else:
                print("ℹ️  No AI documentation changes detected")
                return True

        except Exception as e:
            print(f"❌ Pre-commit hook error: {e}")
            return False

    def _run_health_check(self) -> bool:
        """Run the AI documentation health check."""
        health_check_script = os.path.join(self.script_dir, "ai_health_check.py")

        if not os.path.exists(health_check_script):
            print(f"❌ Health check script not found: {health_check_script}")
            return False

        try:
            # Run the health check script
            result = subprocess.run(
                [sys.executable, health_check_script],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                check=False,
            )

            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"Health check stderr: {result.stderr}")

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error running health check: {e}")
            return False

    def _get_staged_files(self) -> list[str]:
        """Get list of staged files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                check=False,
            )

            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                return [f for f in files if f.strip()]
            else:
                print(f"Warning: Could not get staged files: {result.stderr}")
                return []

        except Exception as e:
            print(f"Warning: Error getting staged files: {e}")
            return []

    def _check_ai_files_modified(self, staged_files: list[str]) -> bool:
        """Check if any AI documentation files are in the staged files."""
        if not staged_files:
            return False

        for file_path in staged_files:
            # Check if file matches AI documentation patterns
            if self._is_ai_doc_file(file_path):
                print(f"📄 AI documentation file modified: {file_path}")
                return True

        return False

    def _is_ai_doc_file(self, file_path: str) -> bool:
        """Check if a file is an AI documentation file that should trigger integration."""
        # Check exclusion patterns first
        for exclude_pattern in self.exclude_patterns:
            if exclude_pattern in file_path:
                return False

        # Check inclusion patterns
        for include_pattern in self.ai_doc_patterns:
            if include_pattern in file_path:
                return True

        return False

    def _run_dynamic_integration(self) -> bool:
        """Run the dynamic integration script."""
        integration_script = os.path.join(self.script_dir, "dynamic_integration.py")

        if not os.path.exists(integration_script):
            print(f"❌ Dynamic integration script not found: {integration_script}")
            return False

        try:
            # Run the integration script
            result = subprocess.run(
                [sys.executable, integration_script, "pre_commit_trigger"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                check=False,
            )

            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"Integration stderr: {result.stderr}")

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error running dynamic integration: {e}")
            return False


def main():
    """Main entry point for the pre-commit hook."""
    hook = PreCommitHook()
    success = hook.run()

    if not success:
        print("\n❌ Pre-commit hook failed - commit blocked")
        print("💡 To bypass this hook, use: git commit --no-verify")
        print("💡 Issues may be:")
        print("   - AI documentation health check failed")
        print("   - Dynamic integration failed")
        print("   - Documentation quality issues detected")
        sys.exit(1)
    else:
        print("✅ Pre-commit hook passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
