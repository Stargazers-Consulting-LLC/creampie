#!/usr/bin/env python3
"""
Install Pre-commit Hook for Dynamic Integration

This script installs the pre-commit hook that automatically triggers dynamic integration
when AI documentation guides are modified.
"""

import shutil
import stat
from pathlib import Path


def install_pre_commit_hook():
    """Install the pre-commit hook."""
    print("🔧 Installing pre-commit hook for dynamic integration...")

    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    git_hooks_dir = project_root / ".git" / "hooks"
    pre_commit_hook = git_hooks_dir / "pre-commit"

    # Check if we're in a git repository
    if not (project_root / ".git").exists():
        print("❌ Not in a git repository. Please run this from the project root.")
        return False

    # Create hooks directory if it doesn't exist
    git_hooks_dir.mkdir(parents=True, exist_ok=True)

    # Copy the pre-commit hook script
    hook_script = script_dir / "pre-commit-hook.py"
    if not hook_script.exists():
        print(f"❌ Pre-commit hook script not found: {hook_script}")
        return False

    try:
        # Copy the script
        shutil.copy2(hook_script, pre_commit_hook)

        # Make it executable
        pre_commit_hook.chmod(pre_commit_hook.stat().st_mode | stat.S_IEXEC)

        print(f"✅ Pre-commit hook installed: {pre_commit_hook}")
        print()
        print("📋 Hook will automatically trigger when you commit changes to:")
        print("   - ai/guide_docs/language_specific/")
        print("   - ai/guide_docs/domain_specific/")
        print("   - ai/guide_docs/core_principles.json")
        print("   - ai/ai_config.json")
        print()
        print("💡 To bypass the hook, use: git commit --no-verify")
        print("💡 To uninstall, delete: .git/hooks/pre-commit")

        return True

    except Exception as e:
        print(f"❌ Error installing pre-commit hook: {e}")
        return False


def uninstall_pre_commit_hook():
    """Uninstall the pre-commit hook."""
    print("🗑️  Uninstalling pre-commit hook...")

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    pre_commit_hook = project_root / ".git" / "hooks" / "pre-commit"

    if pre_commit_hook.exists():
        try:
            pre_commit_hook.unlink()
            print("✅ Pre-commit hook uninstalled")
            return True
        except Exception as e:
            print(f"❌ Error uninstalling pre-commit hook: {e}")
            return False
    else:
        print("ℹ️  Pre-commit hook not found")
        return True


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        success = uninstall_pre_commit_hook()
    else:
        success = install_pre_commit_hook()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
