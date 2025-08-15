"""
System health check API for Claude MCP Init

Provides comprehensive system health monitoring and diagnostic capabilities.
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..plugin_manager import PluginManager
from ..utils import check_command


class HealthChecker:
    """
    System health monitoring and diagnostics

    Performs comprehensive health checks on:
    - System dependencies
    - Plugin availability
    - Configuration validity
    - File permissions
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize health checker

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or self._find_project_root()
        self.plugin_manager = PluginManager()
        self.required_commands = {
            "git": "Version control system",
            "python3": "Python interpreter (3.11+)",
            "node": "Node.js runtime (for Serena)",
            "npm": "Node package manager (for Serena)",
        }
        self.optional_commands = {
            "uv": "Fast Python package manager (for Cipher)",
            "uvx": "UV tool runner (for Serena)",
            "brew": "Homebrew package manager",
            "jq": "JSON processor (for config merging)",
        }

    def _find_project_root(self) -> Path:
        """Find project root directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / "VERSION").exists():
                return current
            current = current.parent
        return Path.cwd()

    def check_system_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive system health check

        Returns:
            Dictionary with health status and detailed checks
        """
        checks = {
            "dependencies": self.check_dependencies(),
            "plugins": self.check_plugins(),
            "configuration": self.check_configuration(),
            "permissions": self.check_permissions(),
            "disk_space": self.check_disk_space(),
        }

        # Determine overall status
        all_passed = all(check.get("status") == "healthy" for check in checks.values())

        return {
            "status": "healthy" if all_passed else "unhealthy",
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
            "summary": self._generate_summary(checks),
        }

    def check_dependencies(self) -> Dict[str, Any]:
        """
        Check system dependencies

        Returns:
            Dependency check results
        """
        results = {"required": {}, "optional": {}, "status": "healthy"}

        # Check required commands
        for cmd, description in self.required_commands.items():
            available = check_command(cmd)
            version = self._get_command_version(cmd) if available else None
            results["required"][cmd] = {
                "available": available,
                "description": description,
                "version": version,
            }
            if not available:
                results["status"] = "unhealthy"

        # Check optional commands
        for cmd, description in self.optional_commands.items():
            available = check_command(cmd)
            version = self._get_command_version(cmd) if available else None
            results["optional"][cmd] = {
                "available": available,
                "description": description,
                "version": version,
            }

        # Special Python version check
        python_version = self._check_python_version()
        if python_version:
            major, minor = python_version
            if major < 3 or (major == 3 and minor < 11):
                results["status"] = "unhealthy"
                results["required"]["python3"][
                    "note"
                ] = f"Python 3.11+ required, found {major}.{minor}"

        return results

    def _get_command_version(self, command: str) -> Optional[str]:
        """Get version string for a command"""
        try:
            if command == "python3":
                result = subprocess.run(
                    [command, "--version"], capture_output=True, text=True, check=False
                )
            elif command in ["node", "npm", "git", "brew"]:
                result = subprocess.run(
                    [command, "--version"], capture_output=True, text=True, check=False
                )
            else:
                return None

            if result.returncode == 0:
                return result.stdout.strip().split("\n")[0]
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return None

    def _check_python_version(self) -> Optional[Tuple[int, int]]:
        """Check Python version"""
        try:
            import sys

            return sys.version_info.major, sys.version_info.minor
        except Exception:
            return None

    def check_plugins(self) -> Dict[str, Any]:
        """
        Check plugin availability and status

        Returns:
            Plugin check results
        """
        results = {"available_plugins": {}, "status": "healthy", "errors": []}

        try:
            # Use existing plugin discovery mechanism
            plugin_list = self.plugin_manager.list_plugins()

            for plugin_info in plugin_list:
                plugin_name = plugin_info["name"]
                try:
                    plugin = self.plugin_manager.get_plugin(plugin_name)
                    if plugin:
                        valid, error = plugin.validate_requirements()

                        results["available_plugins"][plugin_name] = {
                            "loaded": True,
                            "valid": valid,
                            "metadata": plugin.metadata,
                            "error": error,
                        }

                        if not valid:
                            results["status"] = "degraded"
                    else:
                        results["available_plugins"][plugin_name] = {
                            "loaded": False,
                            "error": "Plugin instance not found",
                        }
                        results["status"] = "degraded"

                except Exception as e:
                    results["available_plugins"][plugin_name] = {
                        "loaded": False,
                        "error": str(e),
                    }
                    results["status"] = "degraded"
                    results["errors"].append(f"{plugin_name}: {e}")

        except Exception as e:
            results["status"] = "unhealthy"
            results["errors"].append(f"Plugin discovery failed: {e}")

        return results

    def check_configuration(self) -> Dict[str, Any]:
        """
        Check configuration files

        Returns:
            Configuration check results
        """
        results = {"files": {}, "status": "healthy"}

        config_files = [
            ("VERSION", True),
            ("Makefile", True),
            ("Formula/claude-mcp-init.rb", True),
            ("lib/claude_mcp_init/__init__.py", True),
            ("requirements.txt", False),
            ("pytest.ini", False),
        ]

        for file_path, required in config_files:
            full_path = self.project_root / file_path
            exists = full_path.exists()

            results["files"][file_path] = {
                "exists": exists,
                "required": required,
                "readable": (
                    full_path.is_file() and os.access(full_path, os.R_OK)
                    if exists
                    else False
                ),
            }

            if required and not exists:
                results["status"] = "unhealthy"

        return results

    def check_permissions(self) -> Dict[str, Any]:
        """
        Check file and directory permissions

        Returns:
            Permission check results
        """
        results = {
            "directories": {},
            "executables": {},
            "status": "healthy",
            "issues": [],
        }

        # Check directory permissions
        important_dirs = ["lib", "test", "Formula", "bin"]
        for dir_name in important_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                readable = os.access(dir_path, os.R_OK)
                writable = os.access(dir_path, os.W_OK)
                executable = os.access(dir_path, os.X_OK)

                results["directories"][dir_name] = {
                    "readable": readable,
                    "writable": writable,
                    "executable": executable,
                }

                if not (readable and executable):
                    results["status"] = "unhealthy"
                    results["issues"].append(f"{dir_name}: insufficient permissions")

        # Check executable permissions
        executables = ["bin/claude-mcp-init", "bin/claude-mcp-init-python"]
        for exe_path in executables:
            full_path = self.project_root / exe_path
            if full_path.exists():
                executable = os.access(full_path, os.X_OK)
                results["executables"][exe_path] = executable

                if not executable:
                    results["status"] = "degraded"
                    results["issues"].append(f"{exe_path}: not executable")

        return results

    def check_disk_space(self) -> Dict[str, Any]:
        """
        Check available disk space

        Returns:
            Disk space information
        """
        try:
            stat = shutil.disk_usage(self.project_root)
            free_gb = stat.free / (1024**3)
            total_gb = stat.total / (1024**3)
            used_percent = (stat.used / stat.total) * 100

            status = "healthy"
            if free_gb < 0.1:  # Less than 100MB
                status = "critical"
            elif free_gb < 1:  # Less than 1GB
                status = "warning"

            return {
                "status": status,
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_percent": round(used_percent, 1),
            }
        except Exception as e:
            return {"status": "unknown", "error": str(e)}

    def diagnose_issues(self) -> List[Dict[str, Any]]:
        """
        Diagnose system issues and suggest fixes

        Returns:
            List of issues with suggested solutions
        """
        issues = []
        health = self.check_system_health()

        # Check dependencies
        deps = health["checks"]["dependencies"]
        for cmd, info in deps["required"].items():
            if not info["available"]:
                issues.append(
                    {
                        "issue": f"Missing required dependency: {cmd}",
                        "severity": "critical",
                        "description": info["description"],
                        "solution": self._get_install_command(cmd),
                    }
                )

        for cmd, info in deps["optional"].items():
            if not info["available"]:
                issues.append(
                    {
                        "issue": f"Missing optional dependency: {cmd}",
                        "severity": "warning",
                        "description": info["description"],
                        "solution": self._get_install_command(cmd),
                    }
                )

        # Check plugins
        plugins = health["checks"]["plugins"]
        for plugin_name, plugin_info in plugins.get("available_plugins", {}).items():
            if not plugin_info.get("valid", False):
                issues.append(
                    {
                        "issue": f"Plugin {plugin_name} validation failed",
                        "severity": "warning",
                        "description": plugin_info.get("error", "Unknown error"),
                        "solution": f"Check plugin requirements for {plugin_name}",
                    }
                )

        # Check disk space
        disk = health["checks"]["disk_space"]
        if disk["status"] == "critical":
            issues.append(
                {
                    "issue": "Critical: Very low disk space",
                    "severity": "critical",
                    "description": f"Only {disk['free_gb']}GB free",
                    "solution": "Free up disk space immediately",
                }
            )
        elif disk["status"] == "warning":
            issues.append(
                {
                    "issue": "Warning: Low disk space",
                    "severity": "warning",
                    "description": f"Only {disk['free_gb']}GB free",
                    "solution": "Consider freeing up disk space",
                }
            )

        return issues

    def _get_install_command(self, command: str) -> str:
        """Get installation command for missing dependency"""
        install_commands = {
            "git": "brew install git (macOS) or apt-get install git (Linux)",
            "python3": "brew install python@3.11 (macOS) or apt-get install python3.11 (Linux)",
            "node": "brew install node (macOS) or use nvm",
            "npm": "Installed with Node.js",
            "uv": "curl -LsSf https://astral.sh/uv/install.sh | sh",
            "uvx": "Installed with uv",
            "brew": "Visit https://brew.sh for installation",
            "jq": "brew install jq (macOS) or apt-get install jq (Linux)",
        }
        return install_commands.get(command, f"Install {command} for your system")

    def _generate_summary(self, checks: Dict[str, Any]) -> str:
        """Generate health check summary"""
        unhealthy = []
        warnings = []

        for check_name, check_result in checks.items():
            status = check_result.get("status", "unknown")
            if status == "unhealthy" or status == "critical":
                unhealthy.append(check_name)
            elif status == "degraded" or status == "warning":
                warnings.append(check_name)

        if unhealthy:
            return f"Critical issues in: {', '.join(unhealthy)}"
        elif warnings:
            return f"Warnings in: {', '.join(warnings)}"
        else:
            return "All systems operational"

    def generate_report(self) -> str:
        """
        Generate detailed health report in Markdown format

        Returns:
            Markdown-formatted health report
        """
        health = self.check_system_health()
        issues = self.diagnose_issues()

        report = []
        report.append("# Claude MCP Init - System Health Report")
        report.append(f"\n**Generated**: {health['timestamp']}")
        report.append(f"**Status**: {health['status'].upper()}")
        report.append(f"**Summary**: {health['summary']}\n")

        # Dependencies section
        report.append("## Dependencies")
        deps = health["checks"]["dependencies"]

        report.append("\n### Required")
        for cmd, info in deps["required"].items():
            status = "✅" if info["available"] else "❌"
            version = f" ({info['version']})" if info.get("version") else ""
            report.append(f"- {status} **{cmd}**: {info['description']}{version}")

        report.append("\n### Optional")
        for cmd, info in deps["optional"].items():
            status = "✅" if info["available"] else "⚠️"
            version = f" ({info['version']})" if info.get("version") else ""
            report.append(f"- {status} **{cmd}**: {info['description']}{version}")

        # Issues section
        if issues:
            report.append("\n## Issues and Recommendations")
            for issue in issues:
                severity_icon = "🔴" if issue["severity"] == "critical" else "🟡"
                report.append(f"\n### {severity_icon} {issue['issue']}")
                report.append(f"**Description**: {issue['description']}")
                report.append(f"**Solution**: {issue['solution']}")

        # Disk space
        disk = health["checks"]["disk_space"]
        report.append("\n## System Resources")
        report.append(
            f"- **Disk Space**: {disk['free_gb']}GB free of {disk['total_gb']}GB "
            f"({disk['used_percent']}% used)"
        )

        return "\n".join(report)


__all__ = ["HealthChecker"]
