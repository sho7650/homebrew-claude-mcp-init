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

from . import __version__
from .plugin_manager import PluginManager
from .utils import (
    validate_project_name,
    ensure_directory,
    format_error,
    format_success,
    format_info,
    format_warning
)
from .api import MCPInitAPI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Version - imported from __init__.py for centralized management
VERSION = __version__


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


@click.group()
@click.version_option(version=VERSION, prog_name='claude-mcp-init')
def api():
    """API management commands for Claude MCP Init"""
    pass


@api.command()
@click.option('--format', type=click.Choice(['json', 'pretty']), default='pretty', 
              help='Output format')
def status(format):
    """Show comprehensive system status"""
    api_client = MCPInitAPI()
    status_info = api_client.get_status()
    
    if format == 'json':
        click.echo(json.dumps(status_info, indent=2))
    else:
        # Pretty format
        status_color = {
            'healthy': 'green',
            'warning': 'yellow',
            'unhealthy': 'red'
        }.get(status_info['status'], 'white')
        
        click.echo(f"\n📊 {click.style('Claude MCP Init Status', bold=True)}")
        click.echo(f"Overall Status: {click.style(status_info['status'].upper(), fg=status_color, bold=True)}")
        click.echo(f"API Version: {status_info['api_version']}")
        click.echo(f"Current Version: {status_info['components']['version_validator']['current_version']}")
        click.echo(f"Timestamp: {status_info['timestamp']}")
        
        click.echo(f"\n🔧 {click.style('Components:', bold=True)}")
        for name, info in status_info['components'].items():
            status_icon = {'healthy': '✅', 'warning': '⚠️', 'unhealthy': '❌'}.get(info['status'], '❓')
            click.echo(f"  {status_icon} {name}: {info['status']}")


@api.command()
@click.option('--format', type=click.Choice(['json', 'pretty']), default='pretty',
              help='Output format')
def validate(format):
    """Validate system configuration and readiness"""
    api_client = MCPInitAPI()
    validation = api_client.validate_system()
    
    if format == 'json':
        click.echo(json.dumps(validation, indent=2))
    else:
        # Pretty format
        status_icon = '✅' if validation['valid'] else '❌'
        status_color = 'green' if validation['valid'] else 'red'
        
        click.echo(f"\n🔍 {click.style('System Validation', bold=True)}")
        click.echo(f"Result: {status_icon} {click.style('VALID' if validation['valid'] else 'INVALID', fg=status_color, bold=True)}")
        click.echo(f"Checks Performed: {', '.join(validation['checks_performed'])}")
        
        if validation['issues']:
            click.echo(f"\n❌ {click.style('Issues Found:', fg='red', bold=True)}")
            for issue in validation['issues']:
                click.echo(f"  • {issue}")


@api.command()
@click.option('--format', type=click.Choice(['json', 'markdown']), default='markdown',
              help='Report format')
def health(format):
    """Generate detailed health report"""
    api_client = MCPInitAPI()
    
    if format == 'json':
        report = api_client.get_health_report('dict')
        click.echo(json.dumps(report, indent=2))
    else:
        report = api_client.get_health_report('markdown')
        click.echo(report)


@api.command()
@click.option('--format', type=click.Choice(['json', 'pretty']), default='pretty',
              help='Output format')
def diagnose(format):
    """Diagnose issues and suggest solutions"""
    api_client = MCPInitAPI()
    diagnosis = api_client.diagnose_and_fix()
    
    if format == 'json':
        click.echo(json.dumps(diagnosis, indent=2))
    else:
        # Pretty format
        total = diagnosis['total_issues']
        critical = diagnosis['critical_count']
        warnings = diagnosis['warning_count']
        
        if total == 0:
            click.echo(f"✅ {click.style('No issues found!', fg='green', bold=True)}")
            return
        
        click.echo(f"\n🔍 {click.style('Diagnostic Results', bold=True)}")
        click.echo(f"Total Issues: {total}")
        if critical > 0:
            click.echo(f"Critical: {click.style(str(critical), fg='red', bold=True)}")
        if warnings > 0:
            click.echo(f"Warnings: {click.style(str(warnings), fg='yellow', bold=True)}")
        
        # System issues
        if diagnosis['system_issues']:
            click.echo(f"\n🔧 {click.style('System Issues:', bold=True)}")
            for issue in diagnosis['system_issues']:
                severity_color = 'red' if issue['severity'] == 'critical' else 'yellow'
                severity_icon = '🔴' if issue['severity'] == 'critical' else '🟡'
                click.echo(f"  {severity_icon} {click.style(issue['issue'], fg=severity_color)}")
                click.echo(f"    Solution: {issue['solution']}")
        
        # Version issues
        if diagnosis['version_issues']:
            click.echo(f"\n📋 {click.style('Version Issues:', bold=True)}")
            for issue in diagnosis['version_issues']:
                click.echo(f"  🟡 {click.style(issue['issue'], fg='yellow')}")
                click.echo(f"    Solution: {issue['solution']}")


@api.command()
@click.argument('version')
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes')
def prepare_release(version, dry_run):
    """Prepare system for a new release"""
    api_client = MCPInitAPI()
    
    if dry_run:
        click.echo(f"🔍 {click.style('DRY RUN: Preparing release for version', bold=True)} {version}")
        # Validation only
        validation = api_client.validate_system()
        if validation['valid']:
            click.echo("✅ System validation passed - ready for release preparation")
        else:
            click.echo("❌ System validation failed:")
            for issue in validation['issues']:
                click.echo(f"  • {issue}")
        return
    
    click.echo(f"🚀 {click.style('Preparing release for version', bold=True)} {version}")
    
    result = api_client.prepare_release(version)
    
    if result['ready']:
        click.echo(f"✅ {click.style('Release preparation complete!', fg='green', bold=True)}")
        click.echo(f"Steps completed: {', '.join(result['steps_completed'])}")
        if 'release_notes' in result:
            click.echo(f"\n📝 Release notes generated:")
            click.echo(result['release_notes'])
    else:
        click.echo(f"❌ {click.style('Release preparation failed:', fg='red', bold=True)}")
        for issue in result['issues']:
            click.echo(f"  • {issue}")


@api.command()
def version_info():
    """Show detailed version information"""
    api_client = MCPInitAPI()
    version_info = api_client.version.check_version_consistency()
    
    click.echo(f"\n📋 {click.style('Version Information', bold=True)}")
    
    for source, version in version_info['versions'].items():
        if version:
            status_icon = '✅'
            display_version = version
        else:
            status_icon = '❌'
            display_version = 'Not found'
        
        click.echo(f"  {status_icon} {source.replace('_', ' ').title()}: {display_version}")
    
    if version_info['consistent']:
        click.echo(f"\n✅ {click.style('All versions are consistent', fg='green', bold=True)}")
    else:
        click.echo(f"\n⚠️ {click.style('Version inconsistencies detected:', fg='yellow', bold=True)}")
        for discrepancy in version_info['discrepancies']:
            click.echo(f"  • {discrepancy}")


@click.group()
@click.version_option(version=VERSION, prog_name='claude-mcp-init')
def main_cli():
    """Claude MCP Init - Modular MCP server configuration tool"""
    pass


def main():
    """Main entry point"""
    # Add both the original CLI command and API subcommand to main group
    main_cli.add_command(create_cli(), name='init')
    main_cli.add_command(api)
    
    # If no subcommand provided, default to init behavior
    ctx = click.get_current_context(silent=True)
    if ctx is None or len(sys.argv) == 1:
        # Direct execution without subcommand - use original behavior
        cli = create_cli()
        cli()
    else:
        main_cli()

if __name__ == '__main__':
    main()