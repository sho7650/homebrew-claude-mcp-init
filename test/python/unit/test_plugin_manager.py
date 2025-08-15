"""
Unit tests for PluginManager class
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from claude_mcp_init.plugin_manager import PluginManager
from mcp_modules.base import MCPModule


class TestPluginManager:
    """Test cases for PluginManager"""
    
    def test_plugin_manager_initialization(self, plugin_manager: PluginManager):
        """Test plugin manager initializes correctly"""
        assert isinstance(plugin_manager, PluginManager)
        assert hasattr(plugin_manager, 'plugins')
        assert isinstance(plugin_manager.plugins, dict)
    
    def test_plugin_discovery(self, plugin_manager: PluginManager):
        """Test that plugins are discovered and loaded"""
        # Should find at least serena and cipher plugins
        assert len(plugin_manager.plugins) >= 2
        assert 'serena' in plugin_manager.plugins
        assert 'cipher' in plugin_manager.plugins
    
    def test_get_plugin(self, plugin_manager: PluginManager):
        """Test getting a specific plugin"""
        serena_plugin = plugin_manager.get_plugin('serena')
        assert serena_plugin is not None
        assert isinstance(serena_plugin, MCPModule)
        
        # Test non-existent plugin
        missing_plugin = plugin_manager.get_plugin('nonexistent')
        assert missing_plugin is None
    
    def test_get_enabled_plugins(self, plugin_manager: PluginManager):
        """Test getting enabled plugins"""
        enabled = plugin_manager.get_enabled_plugins(['serena', 'cipher'])
        assert len(enabled) == 2
        assert 'serena' in enabled
        assert 'cipher' in enabled
        
        # Test with invalid plugin
        enabled_with_invalid = plugin_manager.get_enabled_plugins(['serena', 'invalid'])
        assert len(enabled_with_invalid) == 1
        assert 'serena' in enabled_with_invalid
        assert 'invalid' not in enabled_with_invalid
    
    def test_list_plugins(self, plugin_manager: PluginManager):
        """Test listing all plugins"""
        plugin_list = plugin_manager.list_plugins()
        assert isinstance(plugin_list, list)
        assert len(plugin_list) >= 2
        
        # Check plugin metadata structure
        for plugin_meta in plugin_list:
            assert isinstance(plugin_meta, dict)
            assert 'name' in plugin_meta
            assert 'version' in plugin_meta
            assert 'description' in plugin_meta
    
    def test_validate_all_requirements(self, plugin_manager: PluginManager, mock_subprocess):
        """Test validating plugin requirements"""
        all_valid, errors = plugin_manager.validate_all_requirements(['serena', 'cipher'])
        
        # Should return boolean and list
        assert isinstance(all_valid, bool)
        assert isinstance(errors, list)
        
        # Test with invalid plugin
        all_valid_invalid, errors_invalid = plugin_manager.validate_all_requirements(['invalid'])
        assert not all_valid_invalid
        assert len(errors_invalid) > 0
        assert any('not found' in error for error in errors_invalid)
    
    def test_get_all_cli_options(self, plugin_manager: PluginManager):
        """Test getting CLI options from plugins"""
        options = plugin_manager.get_all_cli_options(['serena', 'cipher'])
        assert isinstance(options, list)
        assert len(options) > 0
        
        # Check that each option is a Click option decorator (callable)
        for option in options:
            assert callable(option)  # Should be click.option decorator functions
    
    def test_plugin_metadata(self, plugin_manager: PluginManager):
        """Test plugin metadata is correct"""
        serena = plugin_manager.get_plugin('serena')
        assert serena is not None
        
        metadata = serena.metadata
        assert metadata['name'] == 'serena'
        assert 'version' in metadata
        assert 'description' in metadata
        
        cipher = plugin_manager.get_plugin('cipher')
        assert cipher is not None
        
        metadata = cipher.metadata
        assert metadata['name'] == 'cipher'
        assert 'version' in metadata
        assert 'description' in metadata