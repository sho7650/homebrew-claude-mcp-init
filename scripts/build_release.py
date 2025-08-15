#!/usr/bin/env python3
"""
Release build script for Claude MCP Init

This script creates a minimal, secure release package while maintaining
modular development structure. It handles:
- Version injection and consistency
- Resource embedding and bundling
- Security hardening
- Single-file distribution preparation
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional


class ReleaseBuildError(Exception):
    """Custom exception for release build errors"""
    pass


class ReleaseBuilder:
    """
    Handles building optimized release packages from modular development structure
    """
    
    def __init__(self, project_root: Path, build_dir: Path, target_version: Optional[str] = None):
        """
        Initialize release builder
        
        Args:
            project_root: Root directory of the project
            build_dir: Directory for build artifacts
            target_version: Target version (if None, uses git tags)
        """
        self.project_root = project_root
        self.build_dir = build_dir
        self.target_version = target_version
        self.temp_dir = None
        
    def get_target_version(self) -> str:
        """
        Get target version for release
        
        Returns:
            Version string
        """
        if self.target_version:
            return self.target_version
        
        # Try to get from git tags
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
                if tag.startswith('v'):
                    return tag[1:]
                return tag
        except subprocess.SubprocessError:
            pass
        
        # No fallback - git tags are required for release builds
        raise ReleaseBuildError("Cannot determine target version - git tags required for releases")
    
    def validate_development_structure(self) -> bool:
        """
        Validate that development structure is complete
        
        Returns:
            True if structure is valid
        """
        required_files = [
            "bin/claude-mcp-init-unified",
            "lib/claude_mcp_init/__init__.py",
            "lib/claude_mcp_init/_version.py",
            "scripts/inject_version.py",
            "scripts/embed_zsh.py",
            "Formula/claude-mcp-init.rb"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
        
        print("✅ Development structure validation passed")
        return True
    
    def inject_versions(self, version: str) -> bool:
        """
        Inject version into all relevant files
        
        Args:
            version: Version to inject
            
        Returns:
            True if successful
        """
        print(f"🔧 Injecting version {version}...")
        
        try:
            # Inject into Python backend
            version_script = self.project_root / "scripts/inject_version.py"
            version_file = self.project_root / "lib/claude_mcp_init/_version.py"
            
            result = subprocess.run([
                "python3", str(version_script), version,
                "--version-file", str(version_file)
            ], check=False)
            
            if result.returncode != 0:
                print("❌ Failed to inject version into Python backend")
                return False
            
            print("✅ Version injection completed")
            return True
            
        except Exception as e:
            print(f"❌ Version injection failed: {e}")
            return False
    
    def create_unified_executable(self, version: str) -> Path:
        """
        Create unified executable with embedded resources
        
        Args:
            version: Target version
            
        Returns:
            Path to created executable
        """
        print("🚀 Creating unified executable...")
        
        # Create temporary working directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="claude-mcp-init-build-"))
        
        try:
            # Copy unified executable template
            source_executable = self.project_root / "bin/claude-mcp-init-unified"
            target_executable = self.temp_dir / "claude-mcp-init"
            
            shutil.copy2(source_executable, target_executable)
            
            # Inject version into executable
            self._replace_in_file(target_executable, "__VERSION__", version)
            
            # Embed Zsh script
            zsh_script = self.project_root / "bin/claude-mcp-init"
            if zsh_script.exists():
                embed_script = self.project_root / "scripts/embed_zsh.py"
                result = subprocess.run([
                    "python3", str(embed_script),
                    str(zsh_script), str(target_executable),
                    "--verify"
                ], check=False)
                
                if result.returncode == 0:
                    print("✅ Zsh script embedded successfully")
                else:
                    print("⚠️  Zsh script embedding failed, continuing without Zsh backend")
            
            # Make executable
            target_executable.chmod(0o755)
            
            print(f"✅ Unified executable created: {target_executable}")
            return target_executable
            
        except Exception as e:
            print(f"❌ Failed to create unified executable: {e}")
            raise ReleaseBuildError(f"Unified executable creation failed: {e}")
    
    def _replace_in_file(self, file_path: Path, old_text: str, new_text: str):
        """Replace text in file"""
        content = file_path.read_text()
        updated_content = content.replace(old_text, new_text)
        file_path.write_text(updated_content)
    
    def create_python_package(self, version: str) -> Path:
        """
        Create optimized Python package for embedded use
        
        Args:
            version: Target version
            
        Returns:
            Path to package directory
        """
        print("📦 Creating optimized Python package...")
        
        source_lib = self.project_root / "lib/claude_mcp_init"
        target_lib = self.temp_dir / "lib/claude_mcp_init"
        
        # Copy Python package
        shutil.copytree(source_lib, target_lib)
        
        # Optimize: Remove unnecessary files
        unnecessary_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/test_*",
            "**/*_test.py"
        ]
        
        for pattern in unnecessary_patterns:
            for file_path in target_lib.glob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
        
        print("✅ Python package optimized")
        return target_lib
    
    def create_minimal_distribution(self, version: str) -> Path:
        """
        Create minimal distribution package
        
        Args:
            version: Target version
            
        Returns:
            Path to distribution directory
        """
        print("📋 Creating minimal distribution...")
        
        # Create distribution structure
        dist_dir = self.build_dir / f"claude-mcp-init-{version}"
        dist_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy unified executable
        unified_executable = self.create_unified_executable(version)
        target_executable = dist_dir / "claude-mcp-init"
        shutil.copy2(unified_executable, target_executable)
        
        # Copy optimized Python package for runtime
        python_package = self.create_python_package(version)
        target_python = dist_dir / "lib"
        target_python.mkdir(exist_ok=True)
        shutil.copytree(python_package, target_python / "claude_mcp_init")
        
        # Copy essential documentation
        docs_to_copy = ["README.md", "docs/API_USAGE.md"]
        docs_dir = dist_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        for doc_file in docs_to_copy:
            source_doc = self.project_root / doc_file
            if source_doc.exists():
                if doc_file == "README.md":
                    shutil.copy2(source_doc, dist_dir / "README.md")
                else:
                    target_doc = docs_dir / source_doc.name
                    shutil.copy2(source_doc, target_doc)
        
        # Create release manifest
        self._create_release_manifest(dist_dir, version)
        
        print(f"✅ Minimal distribution created: {dist_dir}")
        return dist_dir
    
    def _create_release_manifest(self, dist_dir: Path, version: str):
        """Create release manifest with build information"""
        manifest = {
            "version": version,
            "build_type": "release",
            "build_timestamp": subprocess.run(
                ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                capture_output=True, text=True
            ).stdout.strip(),
            "git_commit": subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, cwd=self.project_root
            ).stdout.strip()[:8],
            "contents": {
                "executable": "claude-mcp-init",
                "python_backend": "lib/claude_mcp_init/",
                "documentation": ["README.md", "docs/"]
            },
            "security": {
                "embedded_resources": True,
                "version_hardcoded": True,
                "no_external_dependencies": True
            }
        }
        
        manifest_file = dist_dir / "MANIFEST.json"
        with manifest_file.open('w') as f:
            json.dump(manifest, f, indent=2)
    
    def create_homebrew_package(self, dist_dir: Path, version: str) -> Path:
        """
        Create Homebrew-ready package
        
        Args:
            dist_dir: Distribution directory
            version: Target version
            
        Returns:
            Path to tarball
        """
        print("🍺 Creating Homebrew package...")
        
        tarball_name = f"claude-mcp-init-{version}.tar.gz"
        tarball_path = self.build_dir / tarball_name
        
        # Create tarball
        result = subprocess.run([
            "tar", "-czf", str(tarball_path),
            "-C", str(dist_dir.parent),
            dist_dir.name
        ], check=False)
        
        if result.returncode != 0:
            raise ReleaseBuildError("Failed to create tarball")
        
        # Calculate SHA256
        sha256_result = subprocess.run([
            "shasum", "-a", "256", str(tarball_path)
        ], capture_output=True, text=True, check=False)
        
        if sha256_result.returncode == 0:
            sha256 = sha256_result.stdout.split()[0]
            print(f"✅ Homebrew package created: {tarball_path}")
            print(f"📋 SHA256: {sha256}")
            
            # Save SHA256 for Formula update
            sha256_file = self.build_dir / f"{tarball_name}.sha256"
            sha256_file.write_text(sha256)
        
        return tarball_path
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def build_release(self) -> Dict[str, Any]:
        """
        Build complete release package
        
        Returns:
            Build result information
        """
        try:
            print("🏗️  Starting release build...")
            
            # Validate development structure
            if not self.validate_development_structure():
                raise ReleaseBuildError("Development structure validation failed")
            
            # Get target version
            version = self.get_target_version()
            print(f"🎯 Target version: {version}")
            
            # Inject versions
            if not self.inject_versions(version):
                raise ReleaseBuildError("Version injection failed")
            
            # Create minimal distribution
            dist_dir = self.create_minimal_distribution(version)
            
            # Create Homebrew package
            tarball_path = self.create_homebrew_package(dist_dir, version)
            
            print("🎉 Release build completed successfully!")
            
            return {
                "success": True,
                "version": version,
                "distribution_dir": str(dist_dir),
                "tarball": str(tarball_path),
                "size_mb": round(tarball_path.stat().st_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            print(f"❌ Release build failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Build release package for Claude MCP Init")
    parser.add_argument("--version", help="Target version (if not specified, uses git tags)")
    parser.add_argument("--build-dir", type=Path, default=Path("build"), help="Build directory")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--clean", action="store_true", help="Clean build directory before building")
    
    args = parser.parse_args()
    
    if args.clean and args.build_dir.exists():
        print(f"🧹 Cleaning build directory: {args.build_dir}")
        shutil.rmtree(args.build_dir)
    
    # Create build directory
    args.build_dir.mkdir(parents=True, exist_ok=True)
    
    # Create builder and run
    builder = ReleaseBuilder(args.project_root, args.build_dir, args.version)
    result = builder.build_release()
    
    if result["success"]:
        print(f"\n✅ Release build successful!")
        print(f"📦 Version: {result['version']}")
        print(f"📁 Distribution: {result['distribution_dir']}")
        print(f"📋 Tarball: {result['tarball']}")
        print(f"💾 Size: {result['size_mb']} MB")
        sys.exit(0)
    else:
        print(f"\n❌ Release build failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()