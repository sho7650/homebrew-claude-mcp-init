#!/usr/bin/env python3
"""
Claude MCP Init - Main CLI entry point
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

import click

from .plugin_manager import PluginManager
from .utils import (
    validate_project_name,
    ensure_directory,
    format_error,
    format_success,
    format_info,
    format_warning
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Version
VERSION = "0.11.2"


class MCPInitContext:
    """Context object for CLI commands"""
    
    def __init__(self):
        self.plugin_manager = PluginManager()
        self.config = {}
        self.project_path = None
        self.in_place = False


def create_cli():
    """Create CLI with dynamic plugin options"""
    # Discover plugins and add their options
    plugin_manager = PluginManager()
    
    # Create base CLI
    @click.command()
    @click.option('--version', is_flag=True, help='Show version and exit')
    @click.option('--help-modules', is_flag=True, help='Show available MCP modules')
    @click.option('-n', '--in-place', is_flag=True, help='Create configuration in current directory')
    @click.option('--mcp', help='Comma-separated list of MCP modules to enable (serena,cipher)')
    @click.argument('project_name', required=False)
    @click.argument('language', required=False)
    @click.pass_context
    def cli(ctx, version, help_modules, in_place, mcp, project_name, language, **kwargs):
        """
        Claude MCP Init - Modular MCP server configuration tool
        
        Creates configuration for MCP (Model Context Protocol) servers with support
        for Serena (semantic code toolkit) and Cipher (persistent memory).
        
        Examples:
            claude-mcp-init my-project typescript
            claude-mcp-init --mcp serena my-project python
            claude-mcp-init --mcp cipher --cipher-openai-key sk-xxx my-project
            claude-mcp-init -n --mcp serena,cipher my-project
        """
        if version:
            click.echo(f"claude-mcp-init version {VERSION}")
            sys.exit(0)
        
        # Initialize context with plugin manager
        context = MCPInitContext()
        context.plugin_manager = plugin_manager
        ctx.obj = context
        
        if help_modules:
            _show_available_modules(context.plugin_manager)
            sys.exit(0)
        
        # If no project name provided, show help
        if not project_name:
            click.echo(ctx.get_help())
            sys.exit(0)
        
        # Validate project name
        if not validate_project_name(project_name):
            click.echo(format_error("Invalid project name. Must start with alphanumeric character and contain only letters, numbers, dots, hyphens, and underscores (max 100 chars)."))
            sys.exit(1)
        
        # Set up configuration with plugin options
        context.config = {
            'project_name': project_name,
            'language': language or 'typescript',
            'in_place': in_place
        }
        
        # Add plugin-specific options to config
        context.config.update(kwargs)
        
        # Determine project path
        if in_place:
            context.project_path = Path.cwd()
            # Safety check for in-place mode
            if _check_in_place_safety(context.project_path):
                click.echo(format_error("Cannot use in-place mode: directory appears to contain important files"))
                sys.exit(1)
        else:
            context.project_path = Path.cwd() / project_name
        
        # Parse MCP modules
        if mcp:
            modules = [m.strip() for m in mcp.split(',') if m.strip()]
        else:
            modules = ['serena', 'cipher']  # Default modules
        
        # Validate plugin requirements
        _validate_plugin_requirements(context, modules)
        
        # Generate configuration
        _generate_configuration(context, modules)
    
    # Add plugin options dynamically
    for plugin_name, plugin in plugin_manager.plugins.items():
        for option in plugin.get_cli_options():
            cli = option(cli)
    
    return cli


def _show_available_modules(plugin_manager: PluginManager):
    """Show available MCP modules"""
    click.echo(format_info("Available MCP modules:"))
    click.echo()
    
    for plugin_name, plugin in plugin_manager.plugins.items():
        metadata = plugin.metadata
        click.echo(f"  {plugin_name:12} - {metadata.get('description', 'No description')}")
    
    click.echo()
    click.echo("Usage: claude-mcp-init --mcp MODULE1,MODULE2 project-name [language]")


def _check_in_place_safety(project_path: Path) -> bool:
    """Check if in-place mode is safe to use"""
    # Check for important files that suggest this isn't a project directory
    dangerous_files = [
        'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod',
        'pom.xml', 'build.gradle', 'composer.json', '.git'
    ]
    
    for file_name in dangerous_files:
        if (project_path / file_name).exists():
            return True
    
    return False


def _validate_plugin_requirements(context: MCPInitContext, modules: List[str]):
    """Validate plugin requirements"""
    for module_name in modules:
        if module_name not in context.plugin_manager.plugins:
            click.echo(format_error(f"Unknown module: {module_name}"))
            sys.exit(1)
        
        plugin = context.plugin_manager.plugins[module_name]
        
        # Validate plugin requirements
        valid, error = plugin.validate_requirements()
        if not valid:
            click.echo(format_error(f"Module {module_name} requirements not met: {error}"))
            sys.exit(1)


def _generate_configuration(context: MCPInitContext, modules: List[str]):
    """Generate configuration files for all modules"""
    project_path = context.project_path
    config = context.config
    
    click.echo(format_info(f"Setting up MCP configuration for '{config['project_name']}'..."))
    
    # Ensure project directory exists
    if not config['in_place']:
        ensure_directory(project_path)
    
    # Load plugins
    active_plugins = {}
    
    for module_name in modules:
        if module_name in context.plugin_manager.plugins:
            plugin = context.plugin_manager.plugins[module_name]
            active_plugins[module_name] = plugin
            
            # Run pre-install hook
            plugin.pre_install_hook(project_path, config)
    
    # Generate configuration files for each plugin
    for module_name, plugin in active_plugins.items():
        try:
            plugin.generate_config_files(project_path, config)
        except Exception as e:
            click.echo(format_error(f"Failed to generate config for {module_name}: {e}"))
            sys.exit(1)
    
    # Generate .mcp.json
    _generate_mcp_json(project_path, config, active_plugins)
    
    # Generate .env file
    _generate_env_file(project_path, config, active_plugins)
    
    # Generate setup instructions
    _generate_setup_instructions(project_path, active_plugins)
    
    # Run post-install hooks
    for module_name, plugin in active_plugins.items():
        plugin.post_install_hook(project_path, config)
    
    click.echo(format_success(f"✅ MCP configuration complete! Project ready at {project_path}"))


def _generate_mcp_json(project_path: Path, config: Dict[str, Any], plugins: Dict[str, Any]):
    """Generate .mcp.json configuration file"""
    mcp_file = project_path / '.mcp.json'
    
    # Check if file exists before we modify it
    file_existed = mcp_file.exists()
    
    # Load existing configuration if it exists
    if file_existed:
        try:
            with mcp_file.open('r') as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is corrupted or unreadable, start fresh
            existing_config = {}
    else:
        existing_config = {}
    
    # Ensure mcpServers section exists
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    # Add/update server configurations for current plugins
    for module_name, plugin in plugins.items():
        server_config = plugin.get_mcp_json_section(project_path, config)
        existing_config["mcpServers"][module_name] = server_config
    
    # Write back the merged configuration
    with mcp_file.open('w') as f:
        json.dump(existing_config, f, indent=2)
    
    action = "Updated" if file_existed else "Created"
    click.echo(format_success(f"{action} MCP configuration: {mcp_file}"))


def _generate_env_file(project_path: Path, config: Dict[str, Any], plugins: Dict[str, Any]):
    """Generate .env file with API keys"""
    env_vars = {}
    
    for module_name, plugin in plugins.items():
        plugin_env_vars = plugin.get_env_variables(config)
        env_vars.update(plugin_env_vars)
    
    if env_vars:
        env_file = project_path / '.env'
        with env_file.open('w') as f:
            f.write("# Environment variables for MCP servers\n")
            f.write(f"# Generated by claude-mcp-init v{VERSION}\n\n")
            
            for key, value in env_vars.items():
                if value:  # Only write non-empty values
                    f.write(f"{key}={value}\n")
        
        click.echo(format_success(f"Created environment file: {env_file}"))
        click.echo(format_warning("⚠️  Keep .env file secure and don't commit it to version control"))


def _generate_setup_instructions(project_path: Path, plugins: Dict[str, Any]):
    """Generate setup instructions markdown file"""
    instructions_file = project_path / 'MCP_SETUP_INSTRUCTIONS.md'
    
    with instructions_file.open('w') as f:
        f.write("# MCP Setup Instructions\n\n")
        f.write(f"Generated by claude-mcp-init v{VERSION}\n\n")
        f.write("## Overview\n\n")
        f.write("This project has been configured with the following MCP servers:\n\n")
        
        for module_name, plugin in plugins.items():
            metadata = plugin.metadata
            f.write(f"- **{module_name}**: {metadata.get('description', 'No description')}\n")
        
        f.write("\n## Configuration Files\n\n")
        f.write("- `.mcp.json` - MCP server configuration\n")
        f.write("- `.env` - Environment variables (keep secure)\n")
        
        # Add plugin-specific directories
        for module_name, plugin in plugins.items():
            if module_name == 'serena':
                f.write("- `.serena/project.yml` - Serena configuration\n")
            elif module_name == 'cipher':
                f.write("- `memAgent/cipher.yml` - Cipher configuration\n")
        
        f.write("\n## Setup Instructions\n\n")
        
        for module_name, plugin in plugins.items():
            instructions = plugin.get_setup_instructions()
            if instructions:
                f.write(f"### {module_name.title()}\n\n")
                for instruction in instructions:
                    f.write(f"{instruction}\n")
                f.write("\n")
        
        f.write("## Next Steps\n\n")
        f.write("1. Review and customize configuration files as needed\n")
        f.write("2. Set up your IDE to use the MCP configuration\n")
        f.write("3. Verify that all required dependencies are installed\n")
        f.write("4. Test the MCP servers to ensure they're working correctly\n")
    
    click.echo(format_success(f"Created setup instructions: {instructions_file}"))


def main():
    """Main entry point"""
    cli = create_cli()
    cli()

if __name__ == '__main__':
    main()