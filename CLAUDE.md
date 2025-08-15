# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modular MCP (Model Context Protocol) server configuration tool that automates the setup of multiple MCP servers. The tool features a **Python-only architecture** with a plugin-based system allowing easy addition of new MCP modules, with built-in support for Serena (semantic code toolkit) and Cipher (persistent memory layer).

**Version:** 1.0.0 (Python-Only Architecture + Enhanced Security + Streamlined Codebase)

## Key Files

- `bin/claude-mcp-init` - Pure Python executable (main entry point)
- `lib/` - Core Python libraries:
  - `claude_mcp_init/` - Main Python package:
    - `main.py` - CLI entry point and argument parsing
    - `plugin_manager.py` - Plugin system and module management
    - `_version.py` - Git tag-based version management
    - `api/` - API commands for advanced functionality
  - `mcp_modules/` - Python plugin modules:
    - `base.py` - Base module interface
    - `serena/` - Serena MCP module (Python implementation)
    - `cipher/` - Cipher MCP module (Python implementation)
- `Formula/claude-mcp-init.rb` - Homebrew Formula for Python-only distribution
- `docs/` - Documentation files
- `test/` - Python-focused test suite:
  - `python/unit/` - Unit tests using pytest
  - `python/integration/` - Integration tests
  - `formula_test.rb` - Homebrew Formula validation tests

## Development Commands

### Build the Python-only executable:
```bash
make build
```

### Test the project:
```bash
make test  # Runs Python unit/integration tests + Formula tests
```

### Install locally for development:
```bash
make dev-install  # Installs to ~/bin without sudo
```

### Create distribution package:
```bash
make dist
```

### Test the Python executable:
```bash
# After building
./build/bin/claude-mcp-init test-project typescript

# Test in-place mode
./build/bin/claude-mcp-init -n my-project python

# Test with modular configuration (v1.0.0+)
./build/bin/claude-mcp-init --mcp serena my-project
./build/bin/claude-mcp-init --mcp cipher --cipher-openai-key sk-xxx my-project
./build/bin/claude-mcp-init --mcp serena,cipher my-project

# After dev-install
~/bin/claude-mcp-init test-project typescript

# Version and help
./build/bin/claude-mcp-init --version
./build/bin/claude-mcp-init --help

# API commands
./build/bin/claude-mcp-init api --help
./build/bin/claude-mcp-init api health-check
```

## Architecture

The Python tool creates this structure when executed:
```
<project_name>/
├── .serena/
│   └── project.yml         # Serena configuration (official schema)
├── memAgent/
│   └── cipher.yml          # Cipher configuration (dynamic provider)
├── .env                    # Environment variables (API keys)
├── .mcp.json              # Universal MCP server configuration
└── MCP_SETUP_INSTRUCTIONS.md # Setup guide
```

## Python-Only Architecture Features

The Python-only implementation provides these core features:
1. **Modular Architecture**: Plugin-based system for MCP modules
2. **Selective Module Loading**: Load only required MCP modules on demand
3. **Intelligent File Operations**: Smart merging of `.mcp.json` and `.gitignore` files
4. **Secure API Management**: Environment variable-based API key handling
5. **Dynamic Module Discovery**: Automatic detection of available Python MCP modules
6. **Module-specific CLI Options**: Each module defines its own Click command options
7. **Git Tag-based Versioning**: Secure version management without editable files
8. **Enhanced Security**: Single-language environment reduces attack surface
9. **Modern Python Tooling**: Integration with pytest, flake8, black, mypy

### v1.0.0 Python-Only Improvements
- **Single Language**: Pure Python implementation for consistency and security
- **Reduced Complexity**: 40-50% code reduction from hybrid architecture elimination
- **Enhanced Testing**: Comprehensive pytest-based test suite with 36+ unit tests
- **Improved Performance**: Eliminated shell subprocess overhead
- **Better Maintainability**: Simplified codebase with modern Python practices

### Python Architecture Benefits
- **Type Safety**: Full mypy type checking support
- **Code Quality**: Integration with flake8, black, isort for consistent formatting
- **Security Scanning**: Built-in bandit and safety security analysis
- **Modern Packaging**: Standard Python packaging and distribution model
- **Cross-platform**: Consistent behavior across different operating systems

### Mode Options
- **Normal Mode**: Creates `./PROJECT_NAME/` directory with all configuration files inside
- **In-Place Mode** (`-n`/`--in-place`): Creates `.serena/` and `memAgent/` directories in current working directory with safety checks

## Supported Languages

When creating Serena configurations, these languages are supported:
- **Official Serena Schema** (v0.9.2+): `csharp`, `python`, `rust`, `java`, `typescript`, `javascript`, `go`, `cpp`, `ruby`
- **typescript** (default) - Full TypeScript support with advanced tooling
- **Legacy fallback**: `php`, `elixir`, `clojure`, `c` automatically fallback to typescript

## Prerequisites

The Python tool requires these dependencies:
- **Python 3.11+** (primary runtime requirement)
- **Node.js and npm** (for Serena MCP server)
- **uv package manager** (for Cipher MCP server installation)
- **OpenAI or Anthropic API key** (for AI functionality)

## Development Prerequisites

For development work on the codebase:
```bash
# Install Python dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black isort mypy bandit safety

# Install system dependencies
brew install node uv  # macOS
# or
sudo apt-get install nodejs npm  # Ubuntu
curl -LsSf https://astral.sh/uv/install.sh | sh  # uv package manager
```

## Testing

### Python Unit Tests
```bash
# Run unit tests
PYTHONPATH=lib python -m pytest test/python/unit/ -v

# Run with coverage
PYTHONPATH=lib python -m pytest test/python/unit/ --cov=claude_mcp_init --cov=mcp_modules
```

### Integration Tests
```bash
# Run integration tests
PYTHONPATH=lib python -m pytest test/python/integration/ -v
```

### Code Quality
```bash
# Linting
flake8 lib/claude_mcp_init/ lib/mcp_modules/

# Formatting
black lib/claude_mcp_init/ lib/mcp_modules/
isort lib/claude_mcp_init/ lib/mcp_modules/

# Type checking
mypy lib/claude_mcp_init/ --ignore-missing-imports

# Security scanning
bandit -r lib/claude_mcp_init/ lib/mcp_modules/
```

### Formula Testing
```bash
# Test Homebrew Formula
ruby test/formula_test.rb
```

## Key Architectural Changes (v1.0.0)

### What's New
- **Pure Python Implementation**: Eliminated all Zsh/Shell legacy code
- **Git Tag-based Versioning**: Secure version management system without editable version files
- **Enhanced Security**: Single-language environment with comprehensive security scanning
- **Simplified Build Process**: Python-only build pipeline with reduced complexity
- **Modern Testing**: Comprehensive pytest-based test suite with coverage reporting
- **API Commands**: Built-in health checks, version validation, and Formula management

### What's Removed
- All Zsh shell scripts (`core.zsh`, `utils.zsh`, `file-manager.zsh`)
- Shell-based MCP modules (`base.zsh`, `serena.zsh`, `cipher.zsh`)
- Shell integration tests (`integration_test.sh`)
- Unified binary approach and Zsh embedding
- Legacy shell dependency requirements

### What's Maintained
- All core functionality (project creation, MCP configuration, API key management)
- Modular plugin architecture (now in Python)
- Support for all languages (TypeScript, Python, Java, Go, Rust, etc.)
- Homebrew Formula distribution model
- In-place and normal mode operations
- Universal MCP client compatibility

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and return values
- Format code with `black` and sort imports with `isort`
- Ensure all code passes `flake8` linting
- Add docstrings for all public functions and classes

### Testing Requirements
- Write unit tests for all new functionality
- Maintain 80%+ test coverage
- Add integration tests for CLI functionality
- Validate Formula changes with Ruby tests

### Security Requirements
- Never commit API keys or secrets to the repository
- Run `bandit` security scanning on all Python code
- Use `safety` to check for vulnerable dependencies
- Follow secure coding practices for file operations