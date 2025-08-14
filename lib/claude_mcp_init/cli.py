"""
Dynamic CLI - Automatically builds CLI from plugin options
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

import click

from .plugin_manager import PluginManager
from .config_manager import ConfigManager
from .core import MCPInitCore

logger = logging.getLogger(__name__)


class DynamicCLI:
    """Dynamically builds CLI based on available plugins"""
    
    def __init__(self):
        """Initialize the dynamic CLI builder"""
        self.plugin_manager = PluginManager()
        self.cli_command = None
    
    def build_cli(self) -> click.Command:
        """
        Build the CLI command with all plugin options
        
        Returns:
            Click command object
        """
        # Create base command
        @click.command(context_settings=dict(
            help_option_names=['-h', '--help'],
            max_content_width=120
        ))
        @click.argument('project_name')
        @click.argument('language', required=False, default='typescript')
        @click.option(
            '--mcp',
            default='serena,cipher',
            help='Comma-separated list of MCP modules to enable'
        )
        @click.option(
            '-n', '--in-place',
            is_flag=True,
            help='Initialize in current directory instead of creating new project folder'
        )
        @click.option(
            '-v', '--version',
            is_flag=True,
            help='Show version information'
        )
        @click.option(
            '--debug',
            is_flag=True,
            help='Enable debug logging'
        )
        @click.pass_context
        def cli(ctx, project_name, language, mcp, in_place, version, debug, **kwargs):
            """
            Claude MCP Init - Modular MCP server configuration tool
            
            Create and configure MCP (Model Context Protocol) servers for your project.
            
            Examples:
                claude-mcp-init my-project typescript
                claude-mcp-init --mcp serena my-code-project python
                claude-mcp-init --mcp cipher --openai-key sk-xxx my-memory-project
            """
            # Handle version flag
            if version:
                from . import __version__
                click.echo(f"Claude MCP Init v{__version__}")
                sys.exit(0)
            
            # Setup logging
            if debug:
                logging.basicConfig(level=logging.DEBUG)
            else:
                logging.basicConfig(level=logging.INFO)
            
            # Parse module list
            module_names = [m.strip() for m in mcp.split(',') if m.strip()]
            
            # Initialize core
            core = MCPInitCore(self.plugin_manager)
            
            # Prepare config
            config = {
                'project_name': project_name,
                'language': language,
                'in_place': in_place,
                'modules': module_names,
                **kwargs  # Include all plugin-specific options
            }
            
            # Remove None values from config
            config = {k: v for k, v in config.items() if v is not None}
            
            # Run initialization
            try:
                core.initialize_project(config)
                click.echo(click.style("✅ MCP server configuration completed successfully!", fg='green'))
            except Exception as e:
                click.echo(click.style(f"❌ Error: {e}", fg='red'), err=True)
                if debug:
                    import traceback
                    traceback.print_exc()
                sys.exit(1)
        
        # Get all available plugins
        all_plugins = self.plugin_manager.list_plugins()
        
        # Add options from each plugin
        for plugin_meta in all_plugins:
            plugin_name = plugin_meta['name']
            plugin = self.plugin_manager.get_plugin(plugin_name)
            
            if plugin:
                # Get plugin options
                plugin_options = plugin.get_cli_options()
                
                # Add each option to the CLI
                for option in plugin_options:
                    cli = option(cli)
        
        # Store the command
        self.cli_command = cli
        return cli
    
    def add_plugin_group(self, plugin_name: str) -> None:
        """
        Add a plugin's options as a command group (for future expansion)
        
        Args:
            plugin_name: Name of the plugin
        """
        # This could be used to create subcommands for each plugin
        # For now, we're adding all options to the main command
        pass


def create_cli() -> click.Command:
    """
    Create the CLI command
    
    Returns:
        Click command object
    """
    cli_builder = DynamicCLI()
    return cli_builder.build_cli()


def main():
    """Main entry point for the CLI"""
    cli = create_cli()
    cli()


if __name__ == '__main__':
    main()