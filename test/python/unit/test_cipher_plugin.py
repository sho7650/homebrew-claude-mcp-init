"""
Unit tests for CipherPlugin
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any

from mcp_modules.cipher.plugin import CipherPlugin


class TestCipherPlugin:
    """Test cases for CipherPlugin"""
    
    @pytest.fixture
    def cipher_plugin(self) -> CipherPlugin:
        """Create CipherPlugin instance for testing"""
        return CipherPlugin()
    
    @pytest.fixture
    def cipher_config(self) -> Dict[str, Any]:
        """Configuration with Cipher options"""
        return {
            'project_name': 'test-cipher-project',
            'cipher_openai_key': 'sk-fake-openai-key',
            'cipher_anthropic_key': '',
            'cipher_embedding': 'openai',
            'cipher_embedding_key': '',
            'cipher_system_prompt': 'Test system prompt for Cipher'
        }
    
    def test_metadata(self, cipher_plugin: CipherPlugin):
        """Test plugin metadata"""
        metadata = cipher_plugin.metadata
        assert metadata['name'] == 'cipher'
        assert metadata['version'] == '1.0.0'
        assert 'description' in metadata
        assert 'author' in metadata
    
    def test_get_cli_options(self, cipher_plugin: CipherPlugin):
        """Test CLI options"""
        options = cipher_plugin.get_cli_options()
        assert isinstance(options, list)
        assert len(options) >= 5
        
        # Check that all options are callable (click decorators)
        for option in options:
            assert callable(option)
    
    def test_validate_requirements(self, cipher_plugin: CipherPlugin, mock_subprocess):
        """Test requirements validation"""
        valid, error = cipher_plugin.validate_requirements()
        # With mocked subprocess, should return True
        assert isinstance(valid, bool)
        assert error is None or isinstance(error, str)
    
    def test_generate_config_files_openai(self, cipher_plugin: CipherPlugin, cipher_config: Dict[str, Any]):
        """Test configuration file generation with OpenAI"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Generate config files
            cipher_plugin.generate_config_files(project_path, cipher_config)
            
            # Check memAgent directory was created
            mem_agent_dir = project_path / 'memAgent'
            assert mem_agent_dir.exists()
            assert mem_agent_dir.is_dir()
            
            # Check cipher.yml was created
            config_file = mem_agent_dir / 'cipher.yml'
            assert config_file.exists()
            
            # Parse and validate YAML content
            with config_file.open() as f:
                yaml_content = yaml.safe_load(f)
                assert yaml_content['llm']['provider'] == 'openai'
                assert yaml_content['llm']['model'] == 'gpt-4-turbo'
                assert yaml_content['llm']['apiKey'] == '$OPENAI_API_KEY'
                assert yaml_content['systemPrompt'] == 'Test system prompt for Cipher'
    
    def test_generate_config_files_anthropic(self, cipher_plugin: CipherPlugin):
        """Test configuration file generation with Anthropic"""
        anthropic_config = {
            'project_name': 'test-anthropic',
            'cipher_openai_key': '',
            'cipher_anthropic_key': 'claude-fake-key',
            'cipher_embedding': '',
            'cipher_system_prompt': 'Anthropic test prompt'
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            cipher_plugin.generate_config_files(project_path, anthropic_config)
            
            config_file = project_path / 'memAgent' / 'cipher.yml'
            with config_file.open() as f:
                yaml_content = yaml.safe_load(f)
                assert yaml_content['llm']['provider'] == 'anthropic'
                assert yaml_content['llm']['model'] == 'claude-3-5-sonnet-20241022'
                assert yaml_content['llm']['apiKey'] == '$ANTHROPIC_API_KEY'
    
    def test_generate_config_with_embedding(self, cipher_plugin: CipherPlugin):
        """Test configuration with embedding provider"""
        config_with_embedding = {
            'project_name': 'test-embedding',
            'cipher_openai_key': 'sk-fake-key',
            'cipher_embedding': 'voyage',
            'cipher_embedding_key': 'vo-fake-key',
            'cipher_system_prompt': 'Test prompt'
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            cipher_plugin.generate_config_files(project_path, config_with_embedding)
            
            config_file = project_path / 'memAgent' / 'cipher.yml'
            with config_file.open() as f:
                yaml_content = yaml.safe_load(f)
                assert 'embedding' in yaml_content
                assert yaml_content['embedding']['type'] == 'voyage'
                assert yaml_content['embedding']['model'] == 'voyage-3-large'
                assert yaml_content['embedding']['apiKey'] == '$VOYAGE_API_KEY'
    
    def test_generate_config_disabled_embedding(self, cipher_plugin: CipherPlugin):
        """Test configuration with disabled embedding"""
        config_disabled_embedding = {
            'project_name': 'test-disabled',
            'cipher_openai_key': 'sk-fake-key',
            'cipher_embedding': 'disabled',
            'cipher_system_prompt': 'Test prompt'
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            cipher_plugin.generate_config_files(project_path, config_disabled_embedding)
            
            config_file = project_path / 'memAgent' / 'cipher.yml'
            with config_file.open() as f:
                yaml_content = yaml.safe_load(f)
                assert 'embedding' in yaml_content
                assert yaml_content['embedding']['disabled'] is True
    
    def test_get_mcp_json_section(self, cipher_plugin: CipherPlugin, cipher_config: Dict[str, Any]):
        """Test MCP JSON section generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            mcp_section = cipher_plugin.get_mcp_json_section(project_path, cipher_config)
            
            assert isinstance(mcp_section, dict)
            assert mcp_section['type'] == 'stdio'
            assert mcp_section['command'] == 'cipher'
            assert mcp_section['args'] == ['--mode', 'mcp']
            assert 'env' in mcp_section
            assert mcp_section['env']['OPENAI_API_KEY'] == 'sk-fake-openai-key'
    
    def test_get_env_variables(self, cipher_plugin: CipherPlugin, cipher_config: Dict[str, Any]):
        """Test environment variables generation"""
        env_vars = cipher_plugin.get_env_variables(cipher_config)
        assert isinstance(env_vars, dict)
        assert env_vars['OPENAI_API_KEY'] == 'sk-fake-openai-key'
        assert 'ANTHROPIC_API_KEY' not in env_vars  # Empty in config
    
    def test_get_setup_instructions(self, cipher_plugin: CipherPlugin):
        """Test setup instructions"""
        instructions = cipher_plugin.get_setup_instructions()
        assert isinstance(instructions, list)
        assert len(instructions) > 0
        assert any('Cipher' in instruction for instruction in instructions)
        assert any('Python 3.11+' in instruction for instruction in instructions)
    
    def test_get_default_config(self, cipher_plugin: CipherPlugin):
        """Test default configuration"""
        default_config = cipher_plugin.get_default_config()
        assert isinstance(default_config, dict)
        assert 'provider' in default_config
        assert 'model' in default_config
        assert default_config['provider'] == 'openai'
        assert default_config['model'] == 'gpt-4-turbo'
    
    def test_validate_config_valid(self, cipher_plugin: CipherPlugin):
        """Test configuration validation with valid config"""
        valid_config = {
            'project_name': 'valid-project',
            'cipher_openai_key': 'sk-valid-key-1234567890'
        }
        
        valid, error = cipher_plugin.validate_config(valid_config)
        assert valid is True
        assert error is None
    
    def test_validate_config_no_api_keys(self, cipher_plugin: CipherPlugin):
        """Test configuration validation without API keys"""
        invalid_config = {
            'project_name': 'test-project'
            # No API keys provided
        }
        
        valid, error = cipher_plugin.validate_config(invalid_config)
        assert valid is False
        assert error is not None
        assert 'API key' in error
    
    def test_validate_config_invalid_api_key(self, cipher_plugin: CipherPlugin):
        """Test configuration validation with invalid API key format"""
        invalid_config = {
            'project_name': 'test-project',
            'cipher_openai_key': 'invalid-key-format'
        }
        
        valid, error = cipher_plugin.validate_config(invalid_config)
        assert valid is False
        assert error is not None
        assert 'Invalid OpenAI API key' in error
    
    def test_embedding_config_variations(self, cipher_plugin: CipherPlugin):
        """Test different embedding provider configurations"""
        providers_to_test = ['openai', 'gemini', 'voyage', 'qwen', 'lmstudio', 'ollama']
        
        for provider in providers_to_test:
            embedding_config = cipher_plugin._get_embedding_config(provider)
            assert isinstance(embedding_config, dict)
            assert 'type' in embedding_config
            assert 'model' in embedding_config
            
            if provider in ['lmstudio', 'ollama']:
                assert 'baseUrl' in embedding_config
            elif provider not in ['aws-bedrock']:
                assert 'apiKey' in embedding_config
    
    def test_env_var_name_generation(self, cipher_plugin: CipherPlugin):
        """Test environment variable name generation"""
        assert cipher_plugin._get_env_var_name('openai') == 'OPENAI_API_KEY'
        assert cipher_plugin._get_env_var_name('anthropic') == 'ANTHROPIC_API_KEY'
        assert cipher_plugin._get_env_var_name('custom') == 'CUSTOM_API_KEY'