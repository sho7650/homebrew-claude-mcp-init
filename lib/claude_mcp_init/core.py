"""
Core orchestrator for Claude MCP Init
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from .plugin_manager import PluginManager
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


class MCPInitCore:
    """Core orchestrator for MCP initialization"""
    
    def __init__(self, plugin_manager: Optional[PluginManager] = None):
        """
        Initialize the core orchestrator
        
        Args:
            plugin_manager: Plugin manager instance (creates new if not provided)
        """
        self.plugin_manager = plugin_manager or PluginManager()
    
    def initialize_project(self, config: Dict[str, Any]) -> None:
        """
        Initialize a new MCP project
        
        Args:
            config: Configuration dictionary containing:
                - project_name: Name of the project
                - modules: List of module names to enable
                - in_place: Whether to initialize in current directory
                - Other plugin-specific options
        """
        project_name = config['project_name']
        module_names = config.get('modules', ['serena', 'cipher'])
        in_place = config.get('in_place', False)
        
        logger.info(f"Initializing project: {project_name}")
        logger.info(f"Enabled modules: {', '.join(module_names)}")
        
        # Determine project path
        if in_place:
            project_path = Path.cwd()
        else:
            project_path = Path(project_name)
        
        # Create config manager
        config_manager = ConfigManager(project_path)
        
        # Create project structure
        project_dir = config_manager.create_project_structure(in_place)
        
        # Get enabled plugins
        enabled_plugins = self.plugin_manager.get_enabled_plugins(module_names)
        
        if not enabled_plugins:
            raise ValueError(f"No valid plugins found for modules: {module_names}")
        
        # Validate all plugin requirements
        valid, errors = self.plugin_manager.validate_all_requirements(module_names)
        if not valid:
            error_msg = "Plugin requirements not met:\n" + "\n".join(errors)
            raise RuntimeError(error_msg)
        
        # Run pre-install hooks
        for name, plugin in enabled_plugins.items():
            logger.debug(f"Running pre-install hook for {name}")
            plugin.pre_install_hook(project_dir, config)
        
        # Generate configuration files for each plugin
        for name, plugin in enabled_plugins.items():
            logger.info(f"Configuring {name} module")
            
            # Validate plugin config
            valid, error = plugin.validate_config(config)
            if not valid:
                raise ValueError(f"Invalid configuration for {name}: {error}")
            
            # Generate plugin files
            plugin.generate_config_files(project_dir, config)
            
            # Add environment variables
            env_vars = plugin.get_env_variables(config)
            config_manager.add_env_variables(env_vars)
            
            # Add MCP server configuration
            mcp_section = plugin.get_mcp_json_section(project_dir, config)
            if mcp_section:
                config_manager.add_mcp_server(name, mcp_section)
        
        # Write consolidated configuration files
        config_manager.write_env_file()
        config_manager.write_mcp_json()
        config_manager.write_setup_instructions(enabled_plugins)
        
        # Update .gitignore if needed
        gitignore_patterns = [
            ".env",
            "*.pyc",
            "__pycache__/",
            ".DS_Store",
            "node_modules/",
            ".venv/",
            "venv/",
        ]
        config_manager.update_gitignore(gitignore_patterns)
        
        # Run post-install hooks
        for name, plugin in enabled_plugins.items():
            logger.debug(f"Running post-install hook for {name}")
            plugin.post_install_hook(project_dir, config)
        
        # Print success message with next steps
        self._print_success_message(project_name, in_place, enabled_plugins)
    
    def _print_success_message(self, project_name: str, in_place: bool, plugins: Dict[str, Any]) -> None:
        """
        Print success message and next steps
        
        Args:
            project_name: Name of the project
            in_place: Whether project was created in place
            plugins: Dictionary of enabled plugins
        """
        print("\n" + "=" * 60)
        print("✅ MCP server configuration completed successfully!")
        print("=" * 60)
        
        print("\n📦 Configured modules:")
        for name, plugin in plugins.items():
            meta = plugin.metadata
            print(f"  - {meta['name']} v{meta['version']}")
        
        print("\n📋 Next steps:")
        if not in_place:
            print(f"  1. Navigate to project: cd {project_name}")
            step_num = 2
        else:
            step_num = 1
        
        print(f"  {step_num}. Update API keys in .env file")
        print(f"  {step_num + 1}. Follow instructions in MCP_SETUP_INSTRUCTIONS.md")
        
        print("\n🚀 Happy coding with MCP-enabled Claude!")
        print("=" * 60)
    
    def list_available_plugins(self) -> List[Dict[str, str]]:
        """
        List all available plugins
        
        Returns:
            List of plugin metadata dictionaries
        """
        return self.plugin_manager.list_plugins()
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a plugin
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin information dictionary or None
        """
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if plugin:
            return {
                'metadata': plugin.metadata,
                'default_config': plugin.get_default_config(),
                'setup_instructions': plugin.get_setup_instructions(),
            }
        return None