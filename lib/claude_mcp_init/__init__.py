"""
Claude MCP Init - Modular MCP server configuration tool

This package provides a Python-based plugin architecture for configuring
MCP (Model Context Protocol) servers with support for multiple modules.
"""

import os
from pathlib import Path

def _get_version() -> str:
    """
    Get version from VERSION file with fallback.
    
    Returns:
        Version string from VERSION file or fallback version
    """
    try:
        # Look for VERSION file in package root directory
        package_root = Path(__file__).parent.parent.parent
        version_file = package_root / "VERSION"
        
        if version_file.exists():
            return version_file.read_text().strip()
        else:
            # Fallback version if VERSION file not found
            return "0.11.2"
    except Exception:
        # Security-first: return fallback version on any error
        return "0.11.2"

__version__ = _get_version()
__author__ = "Claude MCP Init Team"
__description__ = "Modular MCP server configuration tool"

# Only import PluginManager - avoid importing main to prevent RunPy warnings
from .plugin_manager import PluginManager

__all__ = ["PluginManager"]