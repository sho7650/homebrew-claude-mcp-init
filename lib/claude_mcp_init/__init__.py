"""
Claude MCP Init - Modular MCP server configuration tool
Version 0.11.0 - Python Plugin Architecture
"""

__version__ = "0.11.0"
__author__ = "Claude MCP Init Team"

from .core import MCPInitCore
from .plugin_manager import PluginManager
from .config_manager import ConfigManager

__all__ = [
    "MCPInitCore",
    "PluginManager",
    "ConfigManager",
    "__version__",
]