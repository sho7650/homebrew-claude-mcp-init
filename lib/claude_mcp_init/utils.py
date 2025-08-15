"""
Utility functions for Claude MCP Init
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def validate_project_name(name: str) -> bool:
    """
    Validate project name

    Args:
        name: Project name to validate

    Returns:
        True if valid, False otherwise
    """
    # Must start with alphanumeric
    # Can contain letters, numbers, dots, hyphens, and underscores
    # Max 100 characters
    pattern = r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,99}$"
    return bool(re.match(pattern, name))


def validate_api_key(key: str, provider: str) -> bool:
    """
    Validate API key format

    Args:
        key: API key to validate
        provider: Provider name (openai, anthropic, etc.)

    Returns:
        True if valid format, False otherwise
    """
    if not key:
        return False

    validators = {
        "openai": lambda k: k.startswith("sk-") and len(k) > 20,
        "anthropic": lambda k: k.startswith(("claude-", "sk-ant-")) and len(k) > 10,
        "voyage": lambda k: k.startswith("vo-") and len(k) > 10,
        "gemini": lambda k: len(k) > 10,  # Gemini keys don't have specific prefix
        "azure": lambda k: len(k) > 10,  # Azure keys vary
    }

    validator = validators.get(provider, lambda k: len(k) > 10)
    return validator(key)


def check_command(command: str) -> bool:
    """
    Check if a command is available in the system

    Args:
        command: Command to check

    Returns:
        True if command exists, False otherwise
    """
    try:
        subprocess.run(["which", command], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get_python_version() -> Tuple[int, int]:
    """
    Get the Python version

    Returns:
        Tuple of (major, minor) version numbers
    """
    return sys.version_info.major, sys.version_info.minor


def ensure_directory(path: Path) -> None:
    """
    Ensure a directory exists

    Args:
        path: Path to directory
    """
    path.mkdir(parents=True, exist_ok=True)


def read_yaml_file(path: Path) -> Dict[str, Any]:
    """
    Read a YAML file

    Args:
        path: Path to YAML file

    Returns:
        Dictionary of YAML contents
    """
    import yaml

    with path.open() as f:
        return yaml.safe_load(f) or {}


def write_yaml_file(path: Path, data: Dict[str, Any]) -> None:
    """
    Write a YAML file

    Args:
        path: Path to YAML file
        data: Data to write
    """
    import yaml

    with path.open("w") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def format_error(message: str, details: Optional[str] = None) -> str:
    """
    Format an error message

    Args:
        message: Main error message
        details: Optional detailed information

    Returns:
        Formatted error string
    """
    result = f"❌ Error: {message}"
    if details:
        result += f"\n   Details: {details}"
    return result


def format_warning(message: str) -> str:
    """
    Format a warning message

    Args:
        message: Warning message

    Returns:
        Formatted warning string
    """
    return f"⚠️  Warning: {message}"


def format_success(message: str) -> str:
    """
    Format a success message

    Args:
        message: Success message

    Returns:
        Formatted success string
    """
    return f"✅ {message}"


def format_info(message: str) -> str:
    """
    Format an info message

    Args:
        message: Info message

    Returns:
        Formatted info string
    """
    return f"ℹ️  {message}"


def is_valid_language(language: str) -> bool:
    """
    Check if a language is supported

    Args:
        language: Language name

    Returns:
        True if supported, False otherwise
    """
    supported = {
        "csharp",
        "python",
        "rust",
        "java",
        "typescript",
        "javascript",
        "go",
        "cpp",
        "ruby",
        # Legacy languages (will be mapped to typescript)
        "php",
        "elixir",
        "clojure",
        "c",
    }
    return language.lower() in supported


def normalize_language(language: str) -> str:
    """
    Normalize language name

    Args:
        language: Language name

    Returns:
        Normalized language name
    """
    # Map legacy languages to typescript
    legacy_map = {
        "php": "typescript",
        "elixir": "typescript",
        "clojure": "typescript",
        "c": "typescript",
    }

    language = language.lower()
    return legacy_map.get(language, language)
