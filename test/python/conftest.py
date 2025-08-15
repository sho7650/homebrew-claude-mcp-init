"""
Pytest configuration and fixtures for Claude MCP Init tests
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any

import pytest

# Add lib directory to path for testing
LIB_DIR = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(LIB_DIR))

from claude_mcp_init.plugin_manager import PluginManager
from claude_mcp_init.main import MCPInitContext


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def plugin_manager() -> PluginManager:
    """Create a plugin manager instance for testing"""
    return PluginManager()


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Mock configuration for testing"""
    return {
        'project_name': 'test-project',
        'language': 'typescript',
        'in_place': False,
        'serena_language': 'typescript',
        'serena_read_only': False,
        'serena_excluded_tools': '',
        'serena_initial_prompt': '',
        'cipher_openai_key': 'sk-fake-test-key',
        'cipher_anthropic_key': '',
        'cipher_embedding': 'openai',
        'cipher_embedding_key': '',
        'cipher_system_prompt': 'Test system prompt'
    }


@pytest.fixture
def mcp_context(temp_dir: Path, plugin_manager: PluginManager) -> MCPInitContext:
    """Create MCP context for testing"""
    context = MCPInitContext()
    context.plugin_manager = plugin_manager
    context.project_path = temp_dir / 'test-project'
    context.config = {
        'project_name': 'test-project',
        'language': 'typescript',
        'in_place': False
    }
    return context


@pytest.fixture
def fake_api_keys() -> Dict[str, str]:
    """Fake API keys for testing"""
    return {
        'openai': 'sk-fake-openai-test-key-1234567890',
        'anthropic': 'claude-fake-anthropic-test-key-abcdefghij',
        'voyage': 'vo-fake-voyage-test-key-1234567890',
        'gemini': 'fake-gemini-test-key-1234567890'
    }


@pytest.fixture
def mock_env_vars(fake_api_keys: Dict[str, str], monkeypatch):
    """Mock environment variables for testing"""
    for provider, key in fake_api_keys.items():
        env_var = f"{provider.upper()}_API_KEY"
        monkeypatch.setenv(env_var, key)
    return fake_api_keys


class MockProcess:
    """Mock subprocess process for testing"""
    
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
    
    def communicate(self):
        return self.stdout, self.stderr


@pytest.fixture
def mock_subprocess(monkeypatch):
    """Mock subprocess for testing external commands"""
    def mock_run(*args, **kwargs):
        return MockProcess()
    
    def mock_check_output(*args, **kwargs):
        return "mocked output"
    
    import subprocess
    monkeypatch.setattr(subprocess, "run", mock_run)
    monkeypatch.setattr(subprocess, "check_output", mock_check_output)