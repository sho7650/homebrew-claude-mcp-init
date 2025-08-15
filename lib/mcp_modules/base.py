"""
Base plugin interface for MCP modules
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import click


class MCPModule(ABC):
    """Abstract base class for all MCP module plugins"""
    
    @property
    @abstractmethod
    def metadata(self) -> Dict[str, str]:
        """
        Return plugin metadata
        
        Returns:
            Dict containing:
            - name: Plugin name
            - version: Plugin version
            - description: Plugin description
            - author: Plugin author
        """
        pass
    
    @abstractmethod
    def get_cli_options(self) -> List[click.Option]:
        """
        Return list of Click options for this plugin
        
        Returns:
            List of click.Option objects that will be added to the CLI
        """
        pass
    
    @abstractmethod
    def validate_requirements(self) -> Tuple[bool, Optional[str]]:
        """
        Validate that all requirements for this plugin are met
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        pass
    
    @abstractmethod
    def generate_config_files(self, project_path: Path, config: Dict[str, Any]) -> None:
        """
        Generate plugin-specific configuration files
        
        Args:
            project_path: Path to the project directory
            config: Configuration dictionary with all CLI options
        """
        pass
    
    @abstractmethod
    def get_mcp_json_section(self, project_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return the section to be added to .mcp.json for this plugin
        
        Args:
            project_path: Path to the project directory
            config: Configuration dictionary with all CLI options
            
        Returns:
            Dictionary representing this plugin's MCP server configuration
        """
        pass
    
    @abstractmethod
    def get_env_variables(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Return environment variables required by this plugin
        
        Args:
            config: Configuration dictionary with all CLI options
            
        Returns:
            Dictionary of environment variable names and values
        """
        pass
    
    @abstractmethod
    def get_setup_instructions(self) -> List[str]:
        """
        Return post-installation setup instructions
        
        Returns:
            List of instruction strings
        """
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """
        Return default configuration for this plugin
        
        Returns:
            Dictionary of default configuration values
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate plugin configuration
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Tuple of (valid: bool, error_message: Optional[str])
        """
        # Default implementation - can be overridden
        return True, None
    
    def pre_install_hook(self, project_path: Path, config: Dict[str, Any]) -> None:
        """
        Hook called before installation begins
        
        Args:
            project_path: Path to the project directory
            config: Configuration dictionary
        """
        # Optional hook - can be overridden
        pass
    
    def post_install_hook(self, project_path: Path, config: Dict[str, Any]) -> None:
        """
        Hook called after installation completes
        
        Args:
            project_path: Path to the project directory
            config: Configuration dictionary
        """
        # Optional hook - can be overridden
        pass