"""
Version validation API for Claude MCP Init

Ensures version consistency across all project components using Git tags
as the single source of truth.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional


class VersionValidator:
    """
    Git tag-based version consistency validation system
    
    Validates that version numbers are consistent across:
    - Git tags (primary source of truth)
    - Python package (build-time injected)
    - Homebrew Formula (release artifacts)
    - Legacy VERSION file (if present)
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize version validator
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or self._find_project_root()
        # Extended pattern to support alpha/beta/rc versions
        self.version_pattern = re.compile(r'^\d+\.\d+\.\d+([ab]|rc\d*)?(-.*)?$')
    
    def _find_project_root(self) -> Path:
        """Find project root directory by looking for git repo or VERSION file"""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists() or (current / "VERSION").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def get_version_from_file(self) -> Optional[str]:
        """
        Get version from legacy VERSION file (deprecated)
        
        Returns:
            Version string or None if not found
        """
        version_file = self.project_root / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        return None
    
    def get_git_version(self) -> Optional[str]:
        """
        Get version from git tags (primary source of truth)
        
        Returns:
            Version string from git tags or None
        """
        try:
            # Try exact tag first (for releases)
            result = subprocess.run(
                ["git", "describe", "--tags", "--exact-match", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                check=False
            )
            
            if result.returncode == 0:
                tag = result.stdout.strip()
                if tag.startswith('v'):
                    return tag[1:]
                return tag
            
            # Get latest tag for development versions
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                check=False
            )
            
            if result.returncode == 0:
                tag = result.stdout.strip()
                if tag.startswith('v'):
                    return tag[1:]
                return tag
                
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return None
    
    def get_build_version(self) -> Optional[str]:
        """
        Get version from build-time injection system
        
        Returns:
            Version from _version.py build injection
        """
        try:
            # Import the version module directly
            import sys
            sys.path.insert(0, str(self.project_root / "lib"))
            from claude_mcp_init._version import get_version_info
            
            version_info = get_version_info()
            return version_info.get('build_version')
            
        except ImportError:
            return None
        finally:
            # Clean up sys.path
            if str(self.project_root / "lib") in sys.path:
                sys.path.remove(str(self.project_root / "lib"))
    
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
        Check version consistency across all sources using Git tags as primary
        
        Returns:
            Dictionary with version information and consistency status
        """
        versions = {
            "git_tag": self.get_git_version(),
            "python_package": self.get_python_version(),
            "build_version": self.get_build_version(),
            "formula": self.get_formula_version(),
            "version_file": self.get_version_from_file()  # Legacy
        }
        
        # Primary version is from git tags
        primary_version = versions.get("git_tag")
        
        # Determine current effective version
        # Priority: git_tag > build_version > version_file
        current_version = (
            primary_version or 
            versions.get("build_version") or 
            versions.get("version_file")
        )
        
        # Check consistency using git tag as reference
        discrepancies = self._find_discrepancies_git_based(versions, primary_version)
        
        # Determine consistency status
        # In git-based system, development versions may intentionally differ
        consistent = len(discrepancies) == 0
        
        return {
            "versions": versions,
            "consistent": consistent,
            "current_version": current_version,
            "primary_source": "git_tag" if primary_version else "build_version",
            "discrepancies": discrepancies,
            "git_based": True
        }
    
    def _find_discrepancies_git_based(self, versions: Dict[str, Optional[str]], primary_version: Optional[str]) -> List[str]:
        """
        Find version discrepancies using git tag as primary source
        
        Args:
            versions: Dictionary of version sources and values
            primary_version: Primary version from git tags
            
        Returns:
            List of discrepancy descriptions
        """
        discrepancies = []
        
        # If no primary version, check if we have a build version
        if not primary_version:
            if not versions.get("build_version"):
                discrepancies.append("No git tag or build version found - version source unavailable")
            return discrepancies
        
        # Check formula version for releases (should match git tag for tagged releases)
        formula_version = versions.get("formula")
        if formula_version and not self._versions_compatible(primary_version, formula_version):
            discrepancies.append(
                f"formula version mismatch: git tag {primary_version}, formula {formula_version}"
            )
        
        # Check build version compatibility
        build_version = versions.get("build_version")
        if build_version and not self._versions_compatible(primary_version, build_version):
            # This is often expected in development - not necessarily an error
            if not primary_version.endswith("-dev") and not "dev" in primary_version:
                discrepancies.append(
                    f"build version mismatch: git tag {primary_version}, build {build_version}"
                )
        
        return discrepancies
    
    def _versions_compatible(self, version1: str, version2: str) -> bool:
        """
        Check if two versions are compatible (accounting for dev versions)
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            True if versions are compatible
        """
        if version1 == version2:
            return True
        
        # Extract base version numbers (without dev suffixes)
        base1 = self._extract_base_version(version1)
        base2 = self._extract_base_version(version2)
        
        # For development versions, base versions should match
        if "dev" in version1 or "dev" in version2:
            return base1 == base2
        
        return False
    
    def _extract_base_version(self, version: str) -> str:
        """
        Extract base version from version string
        
        Args:
            version: Version string (e.g., "1.2.3-dev+123")
            
        Returns:
            Base version (e.g., "1.2.3")
        """
        import re
        # Extract base semantic version
        match = re.match(r'^(\d+\.\d+\.\d+)', version)
        return match.group(1) if match else version
    
    def _find_discrepancies(self, versions: Dict[str, Optional[str]]) -> List[str]:
        """
        Legacy version discrepancy finder (deprecated)
        
        Args:
            versions: Dictionary of version sources and values
            
        Returns:
            List of discrepancy descriptions
        """
        # Legacy implementation for backward compatibility
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