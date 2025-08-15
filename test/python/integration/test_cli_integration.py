"""
Integration tests for CLI functionality
"""

import json
import tempfile
from pathlib import Path
from click.testing import CliRunner

import pytest

from claude_mcp_init.main import create_cli


class TestCLIIntegration:
    """Integration tests for CLI commands"""
    
    @pytest.fixture
    def cli_runner(self):
        """Create CLI runner for testing"""
        return CliRunner()
    
    @pytest.fixture 
    def test_cli(self):
        """Create CLI instance for testing"""
        return create_cli()
    
    def test_version_flag(self, cli_runner, test_cli):
        """Test --version flag"""
        result = cli_runner.invoke(test_cli, ['--version'])
        assert result.exit_code == 0
        assert '0.11.6' in result.output
    
    def test_help_modules_flag(self, cli_runner, test_cli):
        """Test --help-modules flag"""
        result = cli_runner.invoke(test_cli, ['--help-modules'])
        assert result.exit_code == 0
        assert 'serena' in result.output
        assert 'cipher' in result.output
    
    def test_help_flag(self, cli_runner, test_cli):
        """Test --help flag"""
        result = cli_runner.invoke(test_cli, ['--help'])
        assert result.exit_code == 0
        assert 'Claude MCP Init' in result.output
        assert 'PROJECT_NAME' in result.output
    
    def test_no_arguments_shows_help(self, cli_runner, test_cli):
        """Test that no arguments shows help"""
        result = cli_runner.invoke(test_cli, [])
        assert result.exit_code == 0
        assert 'Claude MCP Init' in result.output
    
    def test_invalid_project_name(self, cli_runner, test_cli):
        """Test invalid project name validation"""
        result = cli_runner.invoke(test_cli, ['invalid project name!'])
        assert result.exit_code == 1
        assert 'Invalid project name' in result.output
    
    def test_serena_only_project_creation(self, cli_runner, test_cli):
        """Test creating project with Serena only"""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(test_cli, [
                '--mcp', 'serena',
                'test-serena-project',
                'python'
            ])
            
            assert result.exit_code == 0
            assert 'MCP configuration complete' in result.output
            
            # Check files were created
            project_dir = Path('test-serena-project')
            assert project_dir.exists()
            assert (project_dir / '.serena' / 'project.yml').exists()
            assert (project_dir / '.mcp.json').exists()
            assert (project_dir / 'MCP_SETUP_INSTRUCTIONS.md').exists()
            
            # Check .mcp.json content
            with (project_dir / '.mcp.json').open() as f:
                mcp_config = json.load(f)
                assert 'mcpServers' in mcp_config
                assert 'serena' in mcp_config['mcpServers']
                assert 'cipher' not in mcp_config['mcpServers']
    
    def test_cipher_only_project_creation(self, cli_runner, test_cli):
        """Test creating project with Cipher only"""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(test_cli, [
                '--mcp', 'cipher',
                '--cipher-openai-key', 'sk-fake-test-key',
                'test-cipher-project'
            ])
            
            assert result.exit_code == 0
            assert 'MCP configuration complete' in result.output
            
            # Check files were created
            project_dir = Path('test-cipher-project')
            assert project_dir.exists()
            assert (project_dir / 'memAgent' / 'cipher.yml').exists()
            assert (project_dir / '.mcp.json').exists()
            assert (project_dir / '.env').exists()
            
            # Check .env file
            with (project_dir / '.env').open() as f:
                env_content = f.read()
                assert 'OPENAI_API_KEY=sk-fake-test-key' in env_content
    
    def test_both_plugins_project_creation(self, cli_runner, test_cli):
        """Test creating project with both Serena and Cipher"""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(test_cli, [
                '--mcp', 'serena,cipher',
                '--serena-language', 'rust',
                '--cipher-anthropic-key', 'claude-fake-key',
                '--cipher-embedding', 'gemini',
                'test-both-project'
            ])
            
            assert result.exit_code == 0
            assert 'MCP configuration complete' in result.output
            
            # Check files were created
            project_dir = Path('test-both-project')
            assert project_dir.exists()
            assert (project_dir / '.serena' / 'project.yml').exists()
            assert (project_dir / 'memAgent' / 'cipher.yml').exists()
            assert (project_dir / '.mcp.json').exists()
            assert (project_dir / '.env').exists()
            
            # Check .mcp.json contains both plugins
            with (project_dir / '.mcp.json').open() as f:
                mcp_config = json.load(f)
                assert 'serena' in mcp_config['mcpServers']
                assert 'cipher' in mcp_config['mcpServers']
    
    def test_in_place_mode(self, cli_runner, test_cli):
        """Test in-place mode creation"""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(test_cli, [
                '--in-place',
                '--mcp', 'serena',
                'test-in-place-project'
            ])
            
            assert result.exit_code == 0
            
            # Check files were created in current directory
            current_dir = Path('.')
            assert (current_dir / '.serena' / 'project.yml').exists()
            assert (current_dir / '.mcp.json').exists()
    
    def test_plugin_specific_options(self, cli_runner, test_cli):
        """Test plugin-specific options are processed correctly"""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(test_cli, [
                '--mcp', 'serena',
                '--serena-language', 'go',
                '--serena-read-only',
                '--serena-excluded-tools', 'tool1,tool2,tool3',
                '--serena-initial-prompt', 'Custom initial prompt',
                'test-options-project'
            ])
            
            assert result.exit_code == 0
            
            # Check serena config contains the options
            project_dir = Path('test-options-project')
            with (project_dir / '.serena' / 'project.yml').open() as f:
                import yaml
                serena_config = yaml.safe_load(f)
                assert serena_config['language'] == 'go'
                assert serena_config['read_only'] is True
                assert serena_config['excluded_tools'] == ['tool1', 'tool2', 'tool3']
                assert serena_config['initial_prompt'] == 'Custom initial prompt'
    
    def test_unknown_module_error(self, cli_runner, test_cli):
        """Test error handling for unknown module"""
        result = cli_runner.invoke(test_cli, [
            '--mcp', 'unknown-module',
            'test-project'
        ])
        
        assert result.exit_code == 1
        assert 'Unknown module: unknown-module' in result.output
    
    def test_default_modules_when_no_mcp_specified(self, cli_runner, test_cli):
        """Test that default modules (serena,cipher) are used when no --mcp specified"""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(test_cli, [
                '--cipher-openai-key', 'sk-fake-key',
                'test-default-modules'
            ])
            
            assert result.exit_code == 0
            
            # Check both plugins were used
            project_dir = Path('test-default-modules')
            assert (project_dir / '.serena' / 'project.yml').exists()
            assert (project_dir / 'memAgent' / 'cipher.yml').exists()
    
    def test_language_argument(self, cli_runner, test_cli):
        """Test language argument is processed correctly"""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(test_cli, [
                '--mcp', 'serena',
                'test-language-project',
                'java'
            ])
            
            assert result.exit_code == 0
            
            # Check language was set
            project_dir = Path('test-language-project')
            with (project_dir / '.serena' / 'project.yml').open() as f:
                import yaml
                serena_config = yaml.safe_load(f)
                assert serena_config['language'] == 'java'