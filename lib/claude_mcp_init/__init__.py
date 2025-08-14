"""
Claude MCP Init - Modular MCP server configuration tool

This package provides a Python-based plugin architecture for configuring
MCP (Model Context Protocol) servers with support for multiple modules.
"""

__version__ = "0.11.1"
__author__ = "Claude MCP Init Team"
__description__ = "Modular MCP server configuration tool"

from .main import cli
from .plugin_manager import PluginManager

__all__ = ["cli", "PluginManager"]