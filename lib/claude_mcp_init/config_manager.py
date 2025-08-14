"""
Configuration Manager - Manages project configuration and file generation
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration files and environment variables"""
    
    def __init__(self, project_path: Path):
        """
        Initialize configuration manager
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        self.env_vars: Dict[str, str] = {}
        self.mcp_config: Dict[str, Any] = {"mcpServers": {}}
    
    def create_project_structure(self, in_place: bool = False) -> Path:
        """
        Create the project directory structure
        
        Args:
            in_place: If True, use current directory; otherwise create new directory
            
        Returns:
            Path to the project directory
        """
        if in_place:
            project_dir = Path.cwd()
            logger.info(f"Using current directory: {project_dir}")
        else:
            project_dir = self.project_path
            if project_dir.exists():
                logger.warning(f"Project directory already exists: {project_dir}")
            else:
                project_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created project directory: {project_dir}")
        
        return project_dir
    
    def add_env_variable(self, name: str, value: str) -> None:
        """
        Add an environment variable
        
        Args:
            name: Variable name
            value: Variable value
        """
        self.env_vars[name] = value
    
    def add_env_variables(self, variables: Dict[str, str]) -> None:
        """
        Add multiple environment variables
        
        Args:
            variables: Dictionary of variable names and values
        """
        self.env_vars.update(variables)
    
    def add_mcp_server(self, name: str, config: Dict[str, Any]) -> None:
        """
        Add an MCP server configuration
        
        Args:
            name: Server name
            config: Server configuration dictionary
        """
        self.mcp_config["mcpServers"][name] = config
    
    def write_env_file(self) -> None:
        """Write the .env file"""
        env_file = self.project_path / ".env"
        
        content = ["# Environment Variables for MCP Servers", ""]
        
        for name, value in self.env_vars.items():
            # If value starts with $, it's a reference to another env var
            if value.startswith("$"):
                content.append(f"{name}={value}")
            else:
                content.append(f"{name}={value}")
        
        env_file.write_text("\n".join(content) + "\n")
        logger.info(f"Created .env file: {env_file}")
    
    def write_mcp_json(self) -> None:
        """Write the .mcp.json file"""
        mcp_file = self.project_path / ".mcp.json"
        
        # Ensure project path is absolute in MCP config
        for server_config in self.mcp_config["mcpServers"].values():
            if "args" in server_config:
                # Replace project path placeholders
                args = []
                for arg in server_config["args"]:
                    if "{project_path}" in arg:
                        arg = arg.replace("{project_path}", str(self.project_path.absolute()))
                    args.append(arg)
                server_config["args"] = args
        
        with mcp_file.open("w") as f:
            json.dump(self.mcp_config, f, indent=2)
        
        logger.info(f"Created .mcp.json file: {mcp_file}")
    
    def write_setup_instructions(self, plugins: Dict[str, Any]) -> None:
        """
        Write the setup instructions file
        
        Args:
            plugins: Dictionary of enabled plugins
        """
        instructions_file = self.project_path / "MCP_SETUP_INSTRUCTIONS.md"
        
        content = [
            "# MCP Setup Instructions",
            "",
            "This project has been configured with MCP (Model Context Protocol) servers.",
            "",
            "## Configured Modules",
            ""
        ]
        
        for name, plugin in plugins.items():
            meta = plugin.metadata
            content.append(f"### {meta['name']}")
            content.append(f"- Version: {meta['version']}")
            content.append(f"- Description: {meta['description']}")
            content.append("")
        
        content.extend([
            "## Setup Steps",
            "",
            "1. **Install Dependencies**",
            ""
        ])
        
        # Add plugin-specific instructions
        for plugin in plugins.values():
            instructions = plugin.get_setup_instructions()
            if instructions:
                content.extend(instructions)
                content.append("")
        
        content.extend([
            "2. **Configure API Keys**",
            "",
            "Edit the `.env` file and add your actual API keys:",
            "",
            "```bash",
            "nano .env",
            "```",
            "",
            "3. **Configure Your MCP Client**",
            "",
            "- **Claude Code**: The `.mcp.json` file is already configured",
            "- **Cursor**: Copy `.mcp.json` to `.cursor/mcp.json`",
            "- **Other clients**: Use the server configurations from `.mcp.json`",
            "",
            "## Testing",
            "",
            "To verify your setup:",
            "",
            "1. Source the environment variables: `source .env`",
            "2. Check that your MCP client shows the configured tools",
            "3. Test each module's functionality",
            "",
            "## Troubleshooting",
            "",
            "- Ensure all dependencies are installed",
            "- Verify API keys are correctly set",
            "- Check that file paths in `.mcp.json` are absolute",
            "- Review module-specific logs for errors",
            ""
        ])
        
        instructions_file.write_text("\n".join(content))
        logger.info(f"Created setup instructions: {instructions_file}")
    
    def merge_json_file(self, file_path: Path, new_data: Dict[str, Any]) -> None:
        """
        Merge new data into an existing JSON file
        
        Args:
            file_path: Path to the JSON file
            new_data: Data to merge
        """
        if file_path.exists():
            with file_path.open() as f:
                existing = json.load(f)
            
            # Deep merge
            merged = self._deep_merge(existing, new_data)
            
            with file_path.open("w") as f:
                json.dump(merged, f, indent=2)
        else:
            with file_path.open("w") as f:
                json.dump(new_data, f, indent=2)
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        Deep merge two dictionaries
        
        Args:
            base: Base dictionary
            update: Dictionary to merge in
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def update_gitignore(self, patterns: List[str]) -> None:
        """
        Update .gitignore with new patterns
        
        Args:
            patterns: List of patterns to add
        """
        gitignore_file = self.project_path / ".gitignore"
        
        if gitignore_file.exists():
            existing = set(gitignore_file.read_text().strip().split("\n"))
        else:
            existing = set()
        
        # Add new patterns
        for pattern in patterns:
            existing.add(pattern)
        
        # Write back
        gitignore_file.write_text("\n".join(sorted(existing)) + "\n")
        logger.info(f"Updated .gitignore: {gitignore_file}")