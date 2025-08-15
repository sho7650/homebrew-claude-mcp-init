"""
Unit tests for SerenaPlugin
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any

from mcp_modules.serena.plugin import SerenaPlugin


class TestSerenaPlugin:
    """Test cases for SerenaPlugin"""
    
    @pytest.fixture
    def serena_plugin(self) -> SerenaPlugin:
        """Create SerenaPlugin instance for testing"""
        return SerenaPlugin()
    
    @pytest.fixture
    def basic_config(self) -> Dict[str, Any]:
        """Basic configuration for testing"""
        return {
            'project_name': 'test-serena-project',
            'language': 'typescript',
            'serena_language': 'python',
            'serena_read_only': False,
            'serena_excluded_tools': 'tool1,tool2',
            'serena_initial_prompt': 'Test prompt'
        }
    
    def test_metadata(self, serena_plugin: SerenaPlugin):
        """Test plugin metadata"""
        metadata = serena_plugin.metadata
        assert metadata['name'] == 'serena'
        assert metadata['version'] == '1.0.0'
        assert 'description' in metadata
        assert 'author' in metadata
    
    def test_get_cli_options(self, serena_plugin: SerenaPlugin):
        """Test CLI options"""
        options = serena_plugin.get_cli_options()
        assert isinstance(options, list)
        assert len(options) >= 4
        
        # Check that all options are callable (click decorators)
        for option in options:
            assert callable(option)
    
    def test_validate_requirements(self, serena_plugin: SerenaPlugin, mock_subprocess):
        """Test requirements validation"""
        valid, error = serena_plugin.validate_requirements()
        # With mocked subprocess, should return True
        assert isinstance(valid, bool)
        assert error is None or isinstance(error, str)
    
    def test_generate_config_files(self, serena_plugin: SerenaPlugin, basic_config: Dict[str, Any]):
        """Test configuration file generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Generate config files
            serena_plugin.generate_config_files(project_path, basic_config)
            
            # Check .serena directory was created
            serena_dir = project_path / '.serena'
            assert serena_dir.exists()
            assert serena_dir.is_dir()
            
            # Check project.yml was created
            config_file = serena_dir / 'project.yml'
            assert config_file.exists()
            
            # Parse and validate YAML content
            with config_file.open() as f:
                content = f.read()
                assert 'test-serena-project' in content
                assert 'python' in content  # serena_language should override language
                
                # Parse YAML to ensure it's valid
                f.seek(0)
                yaml_content = yaml.safe_load(f)
                assert yaml_content['project_name'] == 'test-serena-project'
                assert yaml_content['language'] == 'python'
                assert yaml_content['read_only'] is False
                assert yaml_content['excluded_tools'] == ['tool1', 'tool2']
                assert yaml_content['initial_prompt'] == 'Test prompt'
    
    def test_generate_config_files_with_none_values(self, serena_plugin: SerenaPlugin):
        """Test config generation with None values"""
        config_with_nones = {
            'project_name': 'test-project',
            'language': 'typescript',
            'serena_excluded_tools': None,
            'serena_initial_prompt': None
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Should not raise exception
            serena_plugin.generate_config_files(project_path, config_with_nones)
            
            config_file = project_path / '.serena' / 'project.yml'
            assert config_file.exists()
            
            with config_file.open() as f:
                yaml_content = yaml.safe_load(f)
                assert yaml_content['excluded_tools'] == []
                assert yaml_content['initial_prompt'] == ''
    
    def test_get_mcp_json_section(self, serena_plugin: SerenaPlugin, basic_config: Dict[str, Any]):
        """Test MCP JSON section generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            mcp_section = serena_plugin.get_mcp_json_section(project_path, basic_config)
            
            assert isinstance(mcp_section, dict)
            assert mcp_section['type'] == 'stdio'
            assert mcp_section['command'] == 'uvx'
            assert '--from' in mcp_section['args']
            assert 'git+https://github.com/oraios/serena' in mcp_section['args']
            assert str(project_path.absolute()) in mcp_section['args']
            assert 'env' in mcp_section
    
    def test_get_env_variables(self, serena_plugin: SerenaPlugin, basic_config: Dict[str, Any]):
        """Test environment variables (should be empty for Serena)"""
        env_vars = serena_plugin.get_env_variables(basic_config)
        assert isinstance(env_vars, dict)
        assert len(env_vars) == 0  # Serena doesn't require env vars
    
    def test_get_setup_instructions(self, serena_plugin: SerenaPlugin):
        """Test setup instructions"""
        instructions = serena_plugin.get_setup_instructions()
        assert isinstance(instructions, list)
        assert len(instructions) > 0
        assert any('Serena' in instruction for instruction in instructions)
    
    def test_get_default_config(self, serena_plugin: SerenaPlugin):
        """Test default configuration"""
        default_config = serena_plugin.get_default_config()
        assert isinstance(default_config, dict)
        assert 'language' in default_config
        assert 'read_only' in default_config
        assert default_config['language'] == 'typescript'
        assert default_config['read_only'] is False
    
    def test_validate_config(self, serena_plugin: SerenaPlugin):
        """Test configuration validation"""
        valid_config = {
            'project_name': 'valid-project',
            'serena_language': 'python'
        }
        
        valid, error = serena_plugin.validate_config(valid_config)
        assert valid is True
        assert error is None
        
        # Test invalid project name
        invalid_config = {
            'project_name': 'invalid project name!',
            'serena_language': 'python'
        }
        
        valid, error = serena_plugin.validate_config(invalid_config)
        assert valid is False
        assert error is not None
        assert 'Invalid project name' in error
    
    def test_language_fallback(self, serena_plugin: SerenaPlugin):
        """Test language fallback to typescript for unsupported languages"""
        config_with_unsupported_lang = {
            'project_name': 'test-project',
            'serena_language': 'unsupported-language'
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            serena_plugin.generate_config_files(project_path, config_with_unsupported_lang)
            
            config_file = project_path / '.serena' / 'project.yml'
            with config_file.open() as f:
                yaml_content = yaml.safe_load(f)
                assert yaml_content['language'] == 'typescript'  # Should fallback
    
    def test_csharp_project_warning(self, serena_plugin: SerenaPlugin, caplog):
        """Test C# project validation warning"""
        csharp_config = {
            'project_name': 'test-csharp',
            'serena_language': 'csharp'
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            serena_plugin.generate_config_files(project_path, csharp_config)
            
            # Should log warning about missing .sln file
            assert any('C# projects' in record.message for record in caplog.records)