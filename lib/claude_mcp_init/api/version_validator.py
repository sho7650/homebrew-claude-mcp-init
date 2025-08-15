"""
Version validation API for Claude MCP Init

Ensures version consistency across all project components.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional


class VersionValidator:
    """
    Version consistency validation system
    
    Validates that version numbers are consistent across:
    - VERSION file
    - Python package
    - Homebrew Formula
    - Git tags
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize version validator
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or self._find_project_root()
        self.version_pattern = re.compile(r'^\d+\.\d+\.\d+$')
    
    def _find_project_root(self) -> Path:
        """Find project root directory by looking for VERSION file"""
        current = Path.cwd()
        while current != current.parent:
            if (current / "VERSION").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def get_version_from_file(self) -> Optional[str]:
        """
        Get version from VERSION file
        
        Returns:
            Version string or None if not found
        """
        version_file = self.project_root / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        return None
    
    def get_python_version(self) -> Optional[str]:
        """
        Get version from Python package
        
        Returns:
            Version string from __init__.py or None
        """
        try:
            # Import the package to get version
            import sys
            sys.path.insert(0, str(self.project_root / "lib"))
            from claude_mcp_init import __version__
            return __version__
        except ImportError:
            return None
        finally:
            # Clean up sys.path
            if str(self.project_root / "lib") in sys.path:
                sys.path.remove(str(self.project_root / "lib"))
    
    def get_formula_version(self) -> Optional[str]:
        """
        Get version from Homebrew Formula
        
        Returns:
            Version string from Formula or None
        """
        formula_path = self.project_root / "Formula" / "claude-mcp-init.rb"
        if not formula_path.exists():
            return None
        
        content = formula_path.read_text()
        # Look for version line in Formula
        match = re.search(r'version\s+"([^"]+)"', content)
        if match:
            return match.group(1)
        return None
    
    def get_latest_git_tag(self) -> Optional[str]:
        """
        Get latest git tag
        
        Returns:
            Latest tag version or None
        """
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                check=False
            )
            if result.returncode == 0:
                tag = result.stdout.strip()
                # Remove 'v' prefix if present
                if tag.startswith('v'):
                    tag = tag[1:]
                return tag
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return None
    
    def check_version_consistency(self) -> Dict[str, Any]:
        """
        Check version consistency across all sources
        
        Returns:
            Dictionary with version information and consistency status
        """
        versions = {
            "version_file": self.get_version_from_file(),
            "python_package": self.get_python_version(),
            "formula": self.get_formula_version(),
            "git_tag": self.get_latest_git_tag()
        }
        
        # Filter out None values for comparison
        valid_versions = [v for v in versions.values() if v is not None]
        
        # Check if all versions match
        consistent = len(set(valid_versions)) <= 1 if valid_versions else False
        
        return {
            "versions": versions,
            "consistent": consistent,
            "current_version": versions.get("version_file"),
            "discrepancies": self._find_discrepancies(versions)
        }
    
    def _find_discrepancies(self, versions: Dict[str, Optional[str]]) -> List[str]:
        """
        Find version discrepancies
        
        Args:
            versions: Dictionary of version sources and values
            
        Returns:
            List of discrepancy descriptions
        """
        discrepancies = []
        base_version = versions.get("version_file")
        
        if not base_version:
            discrepancies.append("VERSION file not found")
            return discrepancies
        
        for source, version in versions.items():
            if source == "version_file":
                continue
            if version and version != base_version:
                discrepancies.append(
                    f"{source}: expected {base_version}, found {version}"
                )
            elif version is None and source != "git_tag":
                discrepancies.append(f"{source}: version not found")
        
        return discrepancies
    
    def validate_version_format(self, version: str) -> Tuple[bool, Optional[str]]:
        """
        Validate version format (semantic versioning)
        
        Args:
            version: Version string to validate
            
        Returns:
            Tuple of (valid, error_message)
        """
        if not version:
            return False, "Version string is empty"
        
        if not self.version_pattern.match(version):
            return False, f"Version '{version}' does not match semantic versioning (X.Y.Z)"
        
        parts = version.split('.')
        try:
            major, minor, patch = map(int, parts)
            if major < 0 or minor < 0 or patch < 0:
                return False, "Version numbers must be non-negative"
        except ValueError:
            return False, "Version parts must be integers"
        
        return True, None
    
    def validate_release_readiness(self) -> Tuple[bool, List[str]]:
        """
        Validate that the project is ready for release
        
        Returns:
            Tuple of (ready, list of issues)
        """
        issues = []
        
        # Check version consistency
        consistency = self.check_version_consistency()
        if not consistency["consistent"]:
            issues.extend(consistency["discrepancies"])
        
        # Check version format
        current_version = consistency.get("current_version")
        if current_version:
            valid, error = self.validate_version_format(current_version)
            if not valid:
                issues.append(f"Version format error: {error}")
        else:
            issues.append("No version found")
        
        # Check for uncommitted changes
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                issues.append("Uncommitted changes in repository")
        except (subprocess.SubprocessError, FileNotFoundError):
            issues.append("Unable to check git status")
        
        # Check if tests exist
        test_dir = self.project_root / "test"
        if not test_dir.exists():
            issues.append("Test directory not found")
        
        return len(issues) == 0, issues
    
    def suggest_next_version(self, bump_type: str = "patch") -> str:
        """
        Suggest next version number
        
        Args:
            bump_type: Type of version bump (major, minor, patch)
            
        Returns:
            Suggested next version
        """
        current = self.get_version_from_file()
        if not current:
            return "0.1.0"
        
        try:
            parts = current.split('.')
            major, minor, patch = map(int, parts)
            
            if bump_type == "major":
                return f"{major + 1}.0.0"
            elif bump_type == "minor":
                return f"{major}.{minor + 1}.0"
            else:  # patch
                return f"{major}.{minor}.{patch + 1}"
        except (ValueError, IndexError):
            return "0.1.0"


__all__ = ["VersionValidator"]