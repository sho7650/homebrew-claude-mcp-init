"""
Claude MCP Init API - Programmatic interface for MCP management

This module provides a comprehensive API for managing MCP configurations,
validating system state, and automating maintenance tasks.
"""

from datetime import datetime
from typing import Any, Dict

from .formula_updater import FormulaUpdater
from .health_check import HealthChecker

# Import implemented API modules
from .version_validator import VersionValidator


class MCPInitAPI:
    """
    Unified API gateway for Claude MCP Init

    Provides programmatic access to all MCP management functionality
    through a single, consistent interface.
    """

    def __init__(self):
        """Initialize API components"""
        self.version = VersionValidator()
        self.health = HealthChecker()
        self.formula = FormulaUpdater()
        self.api_version = "0.2.0"

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status

        Returns:
            Dictionary containing system status information
        """
        # Get status from each component
        version_status = self.version.check_version_consistency()
        health_status = self.health.check_system_health()
        formula_info = self.formula.get_formula_info()

        # Determine overall status
        overall_status = "healthy"
        if not version_status.get("consistent", True):
            overall_status = "warning"
        if health_status.get("status") == "unhealthy":
            overall_status = "unhealthy"

        return {
            "api_version": self.api_version,
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "version_validator": {
                    "status": (
                        "healthy" if version_status.get("consistent") else "warning"
                    ),
                    "current_version": version_status.get("current_version"),
                    "consistent": version_status.get("consistent"),
                },
                "health_check": {
                    "status": health_status.get("status"),
                    "summary": health_status.get("summary"),
                },
                "formula_updater": {
                    "status": "healthy" if formula_info.get("valid") else "warning",
                    "formula_version": formula_info.get("version"),
                    "valid": formula_info.get("valid"),
                },
            },
            "version": version_status,
            "health": health_status,
        }

    def validate_system(self) -> Dict[str, Any]:
        """
        Perform full system validation

        Returns:
            Validation results with any issues found
        """
        results: Dict[str, Any] = {
            "valid": True,
            "timestamp": datetime.now().isoformat(),
            "checks_performed": [],
            "issues": [],
        }

        # Version validation
        version_check = self.version.check_version_consistency()
        results["checks_performed"].append("version_consistency")
        if not version_check.get("consistent"):
            results["valid"] = False
            results["issues"].extend(version_check.get("discrepancies", []))

        # Release readiness check
        release_ready, release_issues = self.version.validate_release_readiness()
        results["checks_performed"].append("release_readiness")
        if not release_ready:
            results["valid"] = False
            results["issues"].extend(release_issues)

        # Health check
        health = self.health.check_system_health()
        results["checks_performed"].append("system_health")
        if health.get("status") == "unhealthy":
            results["valid"] = False
            issues = self.health.diagnose_issues()
            for issue in issues:
                if issue.get("severity") == "critical":
                    results["issues"].append(issue["issue"])

        # Formula validation
        formula_valid, formula_issues = self.formula.validate_formula()
        results["checks_performed"].append("formula_validation")
        if not formula_valid:
            results["valid"] = False
            results["issues"].extend(formula_issues)

        return results

    def prepare_release(self, version: str) -> Dict[str, Any]:
        """
        Prepare system for a new release

        Args:
            version: Version to prepare for release

        Returns:
            Release preparation results
        """
        results: Dict[str, Any] = {
            "version": version,
            "ready": False,
            "steps_completed": [],
            "issues": [],
        }

        try:
            # Validate version format
            valid_format, format_error = self.version.validate_version_format(version)
            if not valid_format:
                results["issues"].append(f"Invalid version format: {format_error}")
                return results

            # Check if system is ready for release
            validation = self.validate_system()
            results["steps_completed"].append("system_validation")

            if not validation["valid"]:
                results["issues"].extend(validation["issues"])
                return results

            # Update Formula for release
            formula_result = self.formula.update_formula_for_release(version)
            results["steps_completed"].append("formula_update")
            results["formula_update"] = formula_result

            if not formula_result.get("validation_passed"):
                results["issues"].extend(formula_result.get("issues", []))
                return results

            # Generate release notes
            release_notes = self.formula.create_release_notes(version)
            results["steps_completed"].append("release_notes_generation")
            results["release_notes"] = release_notes

            results["ready"] = True

        except Exception as e:
            results["issues"].append(f"Release preparation failed: {e}")

        return results

    def get_health_report(self, format: str = "dict") -> Any:
        """
        Get detailed health report

        Args:
            format: Output format ('dict' or 'markdown')

        Returns:
            Health report in requested format
        """
        if format == "markdown":
            return self.health.generate_report()
        else:
            health = self.health.check_system_health()
            issues = self.health.diagnose_issues()
            return {
                "health": health,
                "issues": issues,
                "timestamp": datetime.now().isoformat(),
            }

    def diagnose_and_fix(self) -> Dict[str, Any]:
        """
        Diagnose issues and suggest fixes

        Returns:
            Diagnostic results with solutions
        """
        issues = self.health.diagnose_issues()
        version_issues = []

        # Check version consistency
        version_check = self.version.check_version_consistency()
        if not version_check.get("consistent"):
            for discrepancy in version_check.get("discrepancies", []):
                version_issues.append(
                    {
                        "issue": f"Version inconsistency: {discrepancy}",
                        "severity": "warning",
                        "solution": "Run 'make update-version-python' to synchronize versions",
                    }
                )

        return {
            "system_issues": issues,
            "version_issues": version_issues,
            "total_issues": len(issues) + len(version_issues),
            "critical_count": sum(1 for i in issues if i.get("severity") == "critical"),
            "warning_count": sum(1 for i in issues if i.get("severity") == "warning")
            + len(version_issues),
        }


# Convenience functions for direct API access
def get_system_status() -> Dict[str, Any]:
    """Get system status directly"""
    api = MCPInitAPI()
    return api.get_status()


def validate_system() -> Dict[str, Any]:
    """Validate system directly"""
    api = MCPInitAPI()
    return api.validate_system()


def get_version_info() -> Dict[str, Any]:
    """Get version information directly"""
    api = MCPInitAPI()
    return api.version.check_version_consistency()


# Export main API class and convenience functions
__all__ = [
    "MCPInitAPI",
    "VersionValidator",
    "HealthChecker",
    "FormulaUpdater",
    "get_system_status",
    "validate_system",
    "get_version_info",
]
