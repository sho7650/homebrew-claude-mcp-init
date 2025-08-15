"""
Secure version management for Claude MCP Init

This module provides git tag-based version management with secure fallbacks
and build-time injection support.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple


# Build-time injected version (will be replaced by build process)
__build_version__ = "0.11.5"

# Fallback version for emergency cases
__fallback_version__ = "0.11.5"


def _run_git_command(args: list, cwd: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Safely run git command and return result
    
    Args:
        args: Git command arguments
        cwd: Working directory for git command
        
    Returns:
        Tuple of (success, output)
    """
    try:
        if cwd is None:
            cwd = Path(__file__).parent.parent.parent
        
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,  # 5 second timeout
            check=False
        )
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
            
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return False, "Git command failed"


def _get_version_from_git() -> Optional[str]:
    """
    Get version from git tags
    
    Returns:
        Version string from git tag or None if not available
    """
    # Try to get exact tag first (for releases)
    success, output = _run_git_command(["describe", "--tags", "--exact-match", "HEAD"])
    if success and output.startswith("v"):
        return output[1:]  # Remove 'v' prefix
    
    # Try to get nearest tag with commit info (for development)
    success, output = _run_git_command(["describe", "--tags", "--always", "--dirty"])
    if success:
        if output.startswith("v"):
            # Format: v0.11.5-3-g1234567 or v0.11.5-dirty
            parts = output[1:].split("-")
            if len(parts) >= 2:
                base_version = parts[0]
                if "dirty" in output:
                    return f"{base_version}-dev-dirty"
                else:
                    commits_ahead = parts[1]
                    return f"{base_version}-dev+{commits_ahead}"
            else:
                return parts[0]  # Just the version
        else:
            # No tags found, just commit hash
            return f"{__fallback_version__}-dev+{output[:8]}"
    
    return None


def _get_version_from_environment() -> Optional[str]:
    """
    Get version from environment variable
    
    Returns:
        Version from CLAUDE_MCP_INIT_VERSION env var or None
    """
    return os.environ.get("CLAUDE_MCP_INIT_VERSION")


def get_version() -> str:
    """
    Get version using secure priority system
    
    Priority order:
    1. Environment variable (for testing/override)
    2. Git tag (when available and in git repo)
    3. Build-time injected version
    4. Fallback version
    
    Returns:
        Version string
    """
    # 1. Environment override (for testing)
    env_version = _get_version_from_environment()
    if env_version:
        return env_version
    
    # 2. Git tag (when in git repository)
    git_version = _get_version_from_git()
    if git_version:
        return git_version
    
    # 3. Build-time injected version
    if __build_version__ and not __build_version__.endswith("-dev"):
        return __build_version__
    
    # 4. Fallback version
    return __fallback_version__


def get_version_info() -> dict:
    """
    Get detailed version information
    
    Returns:
        Dictionary with version details
    """
    version = get_version()
    
    # Determine version type
    version_type = "unknown"
    is_development = False
    is_dirty = False
    
    if "dev" in version:
        version_type = "development"
        is_development = True
    elif "dirty" in version:
        version_type = "development"
        is_development = True
        is_dirty = True
    elif version == __build_version__ and not __build_version__.endswith("-dev"):
        version_type = "release"
    elif version == _get_version_from_environment():
        version_type = "environment"
    elif version == __fallback_version__:
        version_type = "fallback"
    else:
        version_type = "git_tag"
    
    # Get git info
    git_available = False
    git_commit = None
    git_branch = None
    
    success, commit = _run_git_command(["rev-parse", "HEAD"])
    if success:
        git_available = True
        git_commit = commit[:8]
        
        success, branch = _run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        if success:
            git_branch = branch
    
    return {
        "version": version,
        "version_type": version_type,
        "is_development": is_development,
        "is_dirty": is_dirty,
        "build_version": __build_version__,
        "fallback_version": __fallback_version__,
        "git_available": git_available,
        "git_commit": git_commit,
        "git_branch": git_branch,
        "sources": {
            "environment": _get_version_from_environment(),
            "git": _get_version_from_git(),
            "build": __build_version__,
            "fallback": __fallback_version__
        }
    }


# Export version for easy import
__version__ = get_version()


# Version validation functions
def is_valid_version_format(version: str) -> bool:
    """
    Check if version follows semantic versioning format with common extensions
    
    Args:
        version: Version string to validate
        
    Returns:
        True if version format is valid
    """
    import re
    
    # Standard semantic versioning pattern with optional pre-release/build metadata
    semver_pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    
    # Common extensions: a (alpha), b (beta), rc (release candidate)
    extended_pattern = r'^(\d+)\.(\d+)\.(\d+)([ab]|rc\d*)?(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    
    return bool(re.match(semver_pattern, version)) or bool(re.match(extended_pattern, version))


def compare_versions(v1: str, v2: str) -> int:
    """
    Compare two version strings
    
    Args:
        v1: First version string
        v2: Second version string
        
    Returns:
        -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2
    """
    try:
        from packaging import version
        return (version.parse(v1) > version.parse(v2)) - (version.parse(v1) < version.parse(v2))
    except ImportError:
        # Fallback to string comparison
        return (v1 > v2) - (v1 < v2)


if __name__ == "__main__":
    # CLI interface for version information
    import json
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        print(json.dumps(get_version_info(), indent=2))
    else:
        print(get_version())