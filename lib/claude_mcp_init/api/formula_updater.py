"""
Homebrew Formula management API for Claude MCP Init

Automates Formula updates, version synchronization, and release management.
"""

import hashlib
import re
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class FormulaUpdater:
    """
    Homebrew Formula update and management system

    Handles:
    - Formula version updates
    - SHA256 checksum calculation
    - Tarball validation
    - Release automation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize Formula updater

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or self._find_project_root()
        self.formula_path = self.project_root / "Formula" / "claude-mcp-init.rb"
        self.formula_name = "claude-mcp-init"
        self.github_repo = "sho7650/mcp-starter"  # Default repo, can be overridden

    def _find_project_root(self) -> Path:
        """Find project root directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / "VERSION").exists():
                return current
            current = current.parent
        return Path.cwd()

    def update_formula_version(
        self, version: str, sha256: Optional[str] = None
    ) -> bool:
        """
        Update Formula file with new version and SHA256

        Args:
            version: New version string (without 'v' prefix)
            sha256: SHA256 checksum of the tarball (will calculate if not provided)

        Returns:
            True if update successful
        """
        if not self.formula_path.exists():
            raise FileNotFoundError(f"Formula not found: {self.formula_path}")

        # Read current Formula content
        content = self.formula_path.read_text()

        # Update version
        content = re.sub(r'version\s+"[^"]+"', f'version "{version}"', content)

        # Update URL with new version
        content = re.sub(
            r'(url\s+"[^"]+/archive/)v[\d.]+\.tar\.gz"',
            f'\\1v{version}.tar.gz"',
            content,
        )

        # Update SHA256 if provided
        if sha256:
            content = re.sub(r'sha256\s+"[^"]+"', f'sha256 "{sha256}"', content)

        # Write updated content
        self.formula_path.write_text(content)
        return True

    def calculate_tarball_sha256(self, tarball_path: Path) -> str:
        """
        Calculate SHA256 checksum of a tarball

        Args:
            tarball_path: Path to the tarball file

        Returns:
            SHA256 checksum as hex string
        """
        if not tarball_path.exists():
            raise FileNotFoundError(f"Tarball not found: {tarball_path}")

        sha256 = hashlib.sha256()
        with tarball_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    def download_release_tarball(
        self, version: str, output_path: Optional[Path] = None
    ) -> Path:
        """
        Download release tarball from GitHub

        Args:
            version: Version to download (without 'v' prefix)
            output_path: Where to save the tarball

        Returns:
            Path to downloaded tarball
        """
        url = f"https://github.com/{self.github_repo}/archive/v{version}.tar.gz"

        if output_path is None:
            output_path = (
                Path(tempfile.gettempdir()) / f"{self.formula_name}-{version}.tar.gz"
            )

        # Validate URL scheme for security  # nosec B310
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.scheme not in ("https", "http"):
            raise ValueError(
                f"URL scheme '{parsed.scheme}' not allowed. Only https/http permitted."
            )
        try:
            urllib.request.urlretrieve(url, output_path)  # nosec B310
            return output_path
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to download tarball: {e}")

    def validate_formula(self) -> Tuple[bool, List[str]]:
        """
        Validate Formula syntax and content

        Returns:
            Tuple of (valid, list of issues)
        """
        if not self.formula_path.exists():
            return False, ["Formula file not found"]

        issues = []
        content = self.formula_path.read_text()

        # Check required fields
        required_patterns = [
            (r"class\s+\w+\s+<\s+Formula", "Class definition"),
            (r'desc\s+"[^"]+"', "Description"),
            (r'homepage\s+"[^"]+"', "Homepage URL"),
            (r'url\s+"[^"]+"', "Download URL"),
            (r'sha256\s+"[^"]+"', "SHA256 checksum"),
            (r'version\s+"[^"]+"', "Version declaration"),
        ]

        for pattern, field_name in required_patterns:
            if not re.search(pattern, content):
                issues.append(f"Missing required field: {field_name}")

        # Validate with brew if available
        if self._check_brew_available():
            try:
                result = subprocess.run(
                    ["brew", "audit", "--formula", str(self.formula_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0 and result.stderr:
                    issues.append(f"Brew audit issues: {result.stderr}")
            except subprocess.SubprocessError as e:
                issues.append(f"Brew audit failed: {e}")

        return len(issues) == 0, issues

    def _check_brew_available(self) -> bool:
        """Check if Homebrew is available"""
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=False)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def generate_formula_from_template(
        self, version: str, description: Optional[str] = None
    ) -> str:
        """
        Generate Formula content from template

        Args:
            version: Version string
            description: Package description

        Returns:
            Formula content as string
        """
        description = description or "Modular MCP server configuration tool"

        template = f"""class ClaudeMcpInit < Formula
  desc "{description}"
  homepage "https://github.com/{self.github_repo}"
  url "https://github.com/{self.github_repo}/archive/v{version}.tar.gz"
  sha256 "__SHA256__"
  version "{version}"

  depends_on "python@3.11"
  depends_on "node"

  def install
    # Install library files
    lib.install Dir["lib/*"]

    # Install bin files
    bin.install "bin/claude-mcp-init"
    bin.install "bin/claude-mcp-init-python"

    # Make scripts executable
    bin.children.each {{ |f| f.chmod 0755 }}
  end

  test do
    system "#{{{bin}}}/claude-mcp-init", "--version"
  end
end"""

        return template

    def publish_to_tap(self, tap_repo: str, branch: str = "main") -> bool:
        """
        Publish Formula to a Homebrew Tap repository

        Args:
            tap_repo: Repository path (e.g., "user/homebrew-tap")
            branch: Branch to publish to

        Returns:
            True if successful
        """
        # This would typically involve:
        # 1. Cloning the tap repository
        # 2. Copying the Formula file
        # 3. Creating a commit
        # 4. Pushing to the repository
        # 5. Optionally creating a pull request

        # For now, return a placeholder
        # Full implementation would require git operations
        return False

    def create_release_notes(
        self, version: str, previous_version: Optional[str] = None
    ) -> str:
        """
        Generate release notes for Formula update

        Args:
            version: New version
            previous_version: Previous version for comparison

        Returns:
            Release notes in Markdown format
        """
        notes = []
        notes.append(f"# Claude MCP Init v{version}")
        notes.append("")

        if previous_version:
            notes.append(f"## Changes from v{previous_version}")

            # Get git log between versions
            try:
                result = subprocess.run(
                    ["git", "log", f"v{previous_version}..v{version}", "--oneline"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    check=False,
                )
                if result.returncode == 0 and result.stdout:
                    notes.append("")
                    notes.append("### Commits")
                    for line in result.stdout.strip().split("\n"):
                        notes.append(f"- {line}")
            except subprocess.SubprocessError:
                pass

        notes.append("")
        notes.append("## Installation")
        notes.append("```bash")
        notes.append(
            "brew tap {}/{}".format(
                self.github_repo.split("/")[0], "homebrew-" + self.formula_name
            )
        )
        notes.append(f"brew install {self.formula_name}")
        notes.append("```")

        notes.append("")
        notes.append("## Updating")
        notes.append("```bash")
        notes.append("brew update")
        notes.append(f"brew upgrade {self.formula_name}")
        notes.append("```")

        return "\n".join(notes)

    def update_formula_for_release(self, version: str) -> Dict[str, Any]:
        """
        Complete Formula update process for a new release

        Args:
            version: Version to release

        Returns:
            Dictionary with update results
        """
        results: Dict[str, Any] = {
            "version": version,
            "formula_updated": False,
            "sha256": None,
            "validation_passed": False,
            "issues": [],
        }

        try:
            # Build distribution tarball
            subprocess.run(["make", "dist"], cwd=self.project_root, check=True)

            # Find the tarball
            dist_dir = self.project_root / "dist"
            tarball_path = dist_dir / f"{self.formula_name}-{version}.tar.gz"

            if tarball_path.exists():
                # Calculate SHA256
                sha256 = self.calculate_tarball_sha256(tarball_path)
                results["sha256"] = sha256

                # Update Formula
                self.update_formula_version(version, sha256)
                results["formula_updated"] = True

                # Validate
                valid, issues = self.validate_formula()
                results["validation_passed"] = valid
                results["issues"] = issues
            else:
                results["issues"].append(f"Tarball not found: {tarball_path}")

        except subprocess.CalledProcessError as e:
            results["issues"].append(f"Build failed: {e}")
        except Exception as e:
            results["issues"].append(f"Update failed: {e}")

        return results

    def get_formula_info(self) -> Dict[str, Any]:
        """
        Get current Formula information

        Returns:
            Dictionary with Formula details
        """
        if not self.formula_path.exists():
            return {"error": "Formula not found"}

        content = self.formula_path.read_text()
        info = {"path": str(self.formula_path), "exists": True}

        # Extract version
        version_match = re.search(r'version\s+"([^"]+)"', content)
        if version_match:
            info["version"] = version_match.group(1)

        # Extract SHA256
        sha_match = re.search(r'sha256\s+"([^"]+)"', content)
        if sha_match:
            info["sha256"] = sha_match.group(1)

        # Extract URL
        url_match = re.search(r'url\s+"([^"]+)"', content)
        if url_match:
            info["url"] = url_match.group(1)

        # Validate
        valid, issues = self.validate_formula()
        info["valid"] = valid
        if issues:
            info["issues"] = issues

        return info


__all__ = ["FormulaUpdater"]
