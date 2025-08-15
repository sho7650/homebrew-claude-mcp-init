#!/usr/bin/env python3
"""
Build-time version injection script for Claude MCP Init

This script updates the __build_version__ in _version.py with the actual
version from git tags or command line arguments.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_git_version() -> Optional[str]:
    """
    Get version from git tags
    
    Returns:
        Version string from git tag or None if not available
    """
    try:
        # Try to get exact tag first (for releases)
        result = subprocess.run(
            ["git", "describe", "--tags", "--exact-match", "HEAD"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip().startswith("v"):
            return result.stdout.strip()[1:]  # Remove 'v' prefix
        
        # Try to get latest tag for development builds
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip().startswith("v"):
            return result.stdout.strip()[1:]  # Remove 'v' prefix
            
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return None


def validate_version_format(version: str) -> bool:
    """
    Validate version format (semantic versioning with common extensions)
    
    Args:
        version: Version string to validate
        
    Returns:
        True if version format is valid
    """
    # Standard semantic versioning pattern
    semver_pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    
    # Common extensions: a (alpha), b (beta), rc (release candidate)
    extended_pattern = r'^(\d+)\.(\d+)\.(\d+)([ab]|rc\d*)?(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    
    return bool(re.match(semver_pattern, version)) or bool(re.match(extended_pattern, version))


def inject_version(version_file: Path, new_version: str) -> bool:
    """
    Inject version into _version.py file
    
    Args:
        version_file: Path to _version.py file
        new_version: Version to inject
        
    Returns:
        True if injection was successful
    """
    if not version_file.exists():
        print(f"Error: Version file not found: {version_file}")
        return False
    
    if not validate_version_format(new_version):
        print(f"Error: Invalid version format: {new_version}")
        return False
    
    try:
        # Read current content
        content = version_file.read_text()
        
        # Replace __build_version__ line with more robust pattern
        import re
        pattern = r'^(\s*)__build_version__\s*=\s*["\'][^"\']*["\']'
        replacement = r'\1__build_version__ = "' + new_version + '"'
        
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        if new_content == content:
            # Try alternative approach: line-by-line replacement
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '__build_version__' in line and '=' in line and line.strip().startswith('__build_version__'):
                    indent = len(line) - len(line.lstrip())
                    lines[i] = ' ' * indent + f'__build_version__ = "{new_version}"'
                    new_content = '\n'.join(lines)
                    break
            else:
                print(f"Warning: No __build_version__ line found to replace")
                return False
        
        # Write back updated content
        version_file.write_text(new_content)
        
        print(f"Successfully injected version {new_version} into {version_file}")
        return True
        
    except Exception as e:
        print(f"Error injecting version: {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Inject version into Claude MCP Init build"
    )
    parser.add_argument(
        "version",
        nargs="?",
        help="Version to inject (if not provided, uses git tag)"
    )
    parser.add_argument(
        "--version-file",
        type=Path,
        default=Path(__file__).parent.parent / "lib" / "claude_mcp_init" / "_version.py",
        help="Path to _version.py file"
    )
    parser.add_argument(
        "--git-version",
        action="store_true",
        help="Use git tag as version source"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify current version in file"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        # Verify current version
        if args.version_file.exists():
            content = args.version_file.read_text()
            match = re.search(r'__build_version__ = ["\']([^"\']*)["\']', content)
            if match:
                current_version = match.group(1)
                print(f"Current build version: {current_version}")
                
                # Validate format
                if validate_version_format(current_version):
                    print("✅ Version format is valid")
                else:
                    print("❌ Version format is invalid")
                    sys.exit(1)
            else:
                print("❌ No __build_version__ found in file")
                sys.exit(1)
        else:
            print(f"❌ Version file not found: {args.version_file}")
            sys.exit(1)
        return
    
    # Determine version to inject
    version_to_inject = args.version
    
    if not version_to_inject or args.git_version:
        git_version = get_git_version()
        if git_version:
            version_to_inject = git_version
            print(f"Using git version: {git_version}")
        elif not version_to_inject:
            print("Error: No version provided and could not get version from git")
            sys.exit(1)
    
    if not version_to_inject:
        print("Error: No version to inject")
        sys.exit(1)
    
    print(f"Injecting version: {version_to_inject}")
    print(f"Target file: {args.version_file}")
    
    if args.dry_run:
        print("DRY RUN: Would inject version but not making changes")
        if validate_version_format(version_to_inject):
            print("✅ Version format is valid")
        else:
            print("❌ Version format is invalid")
            sys.exit(1)
        return
    
    # Perform injection
    success = inject_version(args.version_file, version_to_inject)
    
    if success:
        print("✅ Version injection completed successfully")
    else:
        print("❌ Version injection failed")
        sys.exit(1)


if __name__ == "__main__":
    main()