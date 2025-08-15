"""
Claude MCP Init - Modular MCP server configuration tool

This package provides a Python-based plugin architecture for configuring
MCP (Model Context Protocol) servers with support for multiple modules.
"""

# Import secure version management
from ._version import __version__, get_version_info
__author__ = "Claude MCP Init Team"
__description__ = "Modular MCP server configuration tool"

# Only import PluginManager - avoid importing main to prevent RunPy warnings
from .plugin_manager import PluginManager

__all__ = ["PluginManager"]