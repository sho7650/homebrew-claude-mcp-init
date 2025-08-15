"""
Plugin Manager - Handles plugin discovery and lifecycle
"""

import importlib
import inspect
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from mcp_modules.base import MCPModule

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages plugin discovery, loading, and lifecycle"""

    def __init__(self, plugins_path: Optional[Path] = None):
        """
        Initialize the plugin manager

        Args:
            plugins_path: Path to the plugins directory (defaults to mcp_modules)
        """
        self.plugins: Dict[str, MCPModule] = {}
        self.plugins_path = plugins_path or self._get_default_plugins_path()
        self._discover_and_load_plugins()

    def _get_default_plugins_path(self) -> Path:
        """Get the default path to the plugins directory"""
        return Path(__file__).parent.parent / "mcp_modules"

    def _discover_and_load_plugins(self) -> None:
        """Discover and load all available plugins"""
        logger.info(f"Discovering plugins in {self.plugins_path}")

        # Add plugins path to sys.path if not already there
        plugins_str = str(self.plugins_path.parent)
        if plugins_str not in sys.path:
            sys.path.insert(0, plugins_str)

        # Iterate through plugin directories
        for plugin_dir in self.plugins_path.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith("__"):
                self._load_plugin(plugin_dir.name)

    def _load_plugin(self, plugin_name: str) -> None:
        """
        Load a single plugin by name

        Args:
            plugin_name: Name of the plugin directory
        """
        try:
            # Try to import the plugin module
            module_name = f"mcp_modules.{plugin_name}.plugin"
            logger.debug(f"Attempting to load plugin: {module_name}")

            plugin_module = importlib.import_module(module_name)

            # Find the plugin class (subclass of MCPModule)
            for name, obj in inspect.getmembers(plugin_module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, MCPModule)
                    and obj != MCPModule
                ):

                    # Instantiate the plugin
                    plugin_instance = obj()
                    plugin_meta = plugin_instance.metadata

                    # Register the plugin
                    self.plugins[plugin_meta["name"]] = plugin_instance
                    logger.info(
                        f"Loaded plugin: {plugin_meta['name']} v{plugin_meta['version']}"
                    )
                    break
            else:
                logger.warning(f"No valid plugin class found in {module_name}")

        except ImportError as e:
            logger.debug(f"Could not load plugin {plugin_name}: {e}")
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {e}")

    def get_plugin(self, name: str) -> Optional[MCPModule]:
        """
        Get a plugin by name

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(name)

    def get_enabled_plugins(self, module_names: List[str]) -> Dict[str, MCPModule]:
        """
        Get enabled plugins based on module names

        Args:
            module_names: List of module names to enable

        Returns:
            Dictionary of enabled plugins
        """
        enabled = {}
        for name in module_names:
            plugin = self.get_plugin(name)
            if plugin:
                enabled[name] = plugin
            else:
                logger.warning(f"Plugin {name} not found")
        return enabled

    def list_plugins(self) -> List[Dict[str, str]]:
        """
        List all available plugins

        Returns:
            List of plugin metadata dictionaries
        """
        return [plugin.metadata for plugin in self.plugins.values()]

    def validate_all_requirements(
        self, module_names: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate requirements for specified modules

        Args:
            module_names: List of module names to validate

        Returns:
            Tuple of (all_valid: bool, error_messages: List[str])
        """
        errors = []
        for name in module_names:
            plugin = self.get_plugin(name)
            if plugin:
                valid, error = plugin.validate_requirements()
                if not valid:
                    errors.append(f"{name}: {error}")
            else:
                errors.append(f"Plugin {name} not found")

        return len(errors) == 0, errors

    def get_all_cli_options(self, module_names: List[str]) -> List:
        """
        Get CLI options from enabled plugins

        Args:
            module_names: List of module names

        Returns:
            List of Click options
        """
        options = []
        for name in module_names:
            plugin = self.get_plugin(name)
            if plugin:
                options.extend(plugin.get_cli_options())
        return options

    def reload_plugin(self, name: str) -> bool:
        """
        Reload a plugin (useful for development)

        Args:
            name: Plugin name to reload

        Returns:
            True if successfully reloaded
        """
        if name in self.plugins:
            del self.plugins[name]
            self._load_plugin(name)
            return name in self.plugins
        return False
