[![Continuous Integration](https://github.com/sho7650/homebrew-claude-mcp-init/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/sho7650/homebrew-claude-mcp-init/actions/workflows/ci.yml)

# Claude MCP Init

**Python-based MCP server configuration tool with streamlined architecture for Claude Code.**

Modular command-line tool for configuring MCP (Model Context Protocol) servers with support for Serena (semantic code toolkit) and Cipher (persistent memory layer).

## Overview

Claude MCP Init features a **Python-only architecture** that provides enhanced security, maintainability, and performance. The tool automatically creates project structures, generates configurations, and sets up environment variables for seamless integration with Claude Code, Cursor, and other MCP clients.

**🎉 Version 1.0.0-ready - Python-Only Architecture**

- **🐍 Python-only implementation**: Simplified, secure, and maintainable codebase
- **🔒 Git tag-based versioning**: Secure version management system
- **⚡ Enhanced performance**: Eliminated shell subprocess overhead
- **🛡️ Improved security**: Single-language environment reduces attack surface
- **📦 Single executable distribution**: Pure Python executable with embedded resources
- **🧪 Comprehensive testing**: Python-focused test suite with 36+ unit tests
- **🔧 Modern tooling**: Integration with flake8, black, mypy, pytest

## Key Features

- **🔧 Modular Architecture**: Plugin-based system for MCP modules (serena, cipher, and future modules)
- **🎯 Selective Loading**: Choose specific modules with `--mcp serena`, `--mcp cipher`, or both
- **🔐 Secure API Management**: Environment variable-based API key handling
- **🌐 Universal Compatibility**: Generates `.mcp.json` compatible with Claude Code, Cursor, and other MCP clients
- **🚀 Enhanced Embedding Support**: OpenAI, Gemini, Voyage, Qwen, AWS Bedrock, Azure, LM Studio, Ollama
- **📁 Smart File Operations**: Intelligent merging of configuration files
- **🐍 Python Optimized**: Built with modern Python practices and tooling
- **🏠 In-Place Mode**: Initialize MCP configuration in existing projects
- **📝 Official Schema Support**: Full compatibility with Serena and Cipher specifications
- **🔧 API Commands**: Built-in health checks, version validation, and Formula management

## Prerequisites

- **Python 3.11+** - Primary runtime requirement
- **Node.js** and **npm** - Required for Serena MCP server
- **uv** - Python package manager ([installation guide](https://github.com/astral-sh/uv))

## Installation

### Homebrew (Recommended)

```bash
# Add the tap
brew tap sho7650/homebrew-claude-mcp-init

# Install Claude MCP Init
brew install claude-mcp-init

# Use it immediately
claude-mcp-init my-project typescript
```

### Manual Installation

1. Clone this repository:

```bash
git clone https://github.com/sho7650/homebrew-claude-mcp-init.git
cd homebrew-claude-mcp-init
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Build the command:

```bash
make build
```

4. Test the built command:

```bash
./build/bin/claude-mcp-init --version
./build/bin/claude-mcp-init --help
```

5. Install locally (optional):

```bash
# System-wide installation (requires sudo)
make install

# Or development installation (no sudo required)
make dev-install
```

## Usage

### Command Syntax

```bash
claude-mcp-init [OPTIONS] <project_name> [language]
```

### Modular Configuration Options

- `--mcp <modules>`: Select specific MCP modules (default: `serena,cipher`)
  - `--mcp serena` - Only Serena semantic code toolkit
  - `--mcp cipher` - Only Cipher persistent memory
  - `--mcp serena,cipher` - Both modules (default)

### API Key Configuration

- `--cipher-openai-key <key>`: OpenAI API key for Cipher
- `--cipher-anthropic-key <key>`: Anthropic API key for Cipher
- `--cipher-embedding <provider>`: Embedding provider selection

### Basic Examples

```bash
# Create TypeScript project with both modules
claude-mcp-init my-project typescript

# Python project with Serena only
claude-mcp-init --mcp serena python-project python

# Cipher-only setup with API key
claude-mcp-init --mcp cipher --cipher-openai-key sk-xxx memory-project

# In-place configuration
claude-mcp-init -n --mcp serena,cipher existing-project
```

### Advanced Examples

```bash
# Project with specific embedding provider
claude-mcp-init --cipher-embedding voyage --cipher-openai-key sk-xxx advanced-project

# Java project with comprehensive setup
claude-mcp-init --mcp serena,cipher --cipher-anthropic-key claude-xxx java-project java

# API commands for health monitoring
claude-mcp-init api health-check
claude-mcp-init api version-check
```

## Supported Languages

**Primary Support** (Official Serena Schema):
- `typescript` (default), `javascript`, `python`, `java`, `go`, `rust`, `cpp`, `ruby`, `csharp`

**Legacy Support** (auto-fallback to TypeScript):
- `php`, `elixir`, `clojure`, `c`

## Embedding Providers

Cipher supports multiple embedding providers:
- `openai` (default), `azure-openai`, `gemini`, `voyage`, `qwen`, `aws-bedrock`, `lmstudio`, `ollama`, `disabled`

## API Commands

Claude MCP Init includes built-in API commands for advanced management:

```bash
# Health monitoring
claude-mcp-init api health-check

# Version validation
claude-mcp-init api version-check

# Homebrew Formula management  
claude-mcp-init api update-formula

# Plugin diagnostics
claude-mcp-init api diagnose
```

## Project Structure

After running the tool, your project will have this structure:

```
<project_name>/
├── .serena/
│   └── project.yml         # Serena configuration (official schema)
├── memAgent/
│   └── cipher.yml          # Cipher configuration (dynamic provider)
├── .env                    # Environment variables (API keys)
├── .mcp.json               # Universal MCP server configuration
└── MCP_SETUP_INSTRUCTIONS.md # Setup guide
```

## Architecture

The Python-only architecture provides:

- **Single Language**: Pure Python implementation for consistency
- **Modular Plugins**: Independent modules for Serena and Cipher
- **Secure Versioning**: Git tag-based version management
- **Modern Tooling**: Integration with Python best practices
- **Enhanced Testing**: Comprehensive test suite with pytest
- **Clean Distribution**: Single executable with embedded resources

### Development Structure

```
claude-mcp-init/
├── bin/
│   └── claude-mcp-init     # Pure Python executable
├── lib/
│   ├── claude_mcp_init/    # Core Python package
│   │   ├── main.py         # CLI entry point
│   │   ├── plugin_manager.py # Plugin system
│   │   ├── api/            # API commands
│   │   └── _version.py     # Secure version management
│   └── mcp_modules/        # Plugin modules
│       ├── serena/         # Serena plugin
│       └── cipher/         # Cipher plugin
├── test/
│   ├── python/             # Python test suite
│   └── formula_test.rb     # Homebrew Formula tests
└── scripts/
    ├── inject_version.py   # Build-time version injection
    └── build_release.py    # Release packaging
```

## Configuration Details

### Serena (Semantic Code Toolkit)

Serena provides semantic analysis and code understanding capabilities:

- **Language Support**: TypeScript, Python, Java, Go, Rust, C++, Ruby, C#
- **Features**: Code analysis, semantic search, project understanding
- **Configuration**: `.serena/project.yml` with official schema
- **Integration**: Works with any MCP-compatible client

### Cipher (Persistent Memory Layer)

Cipher provides AI memory and embedding capabilities:

- **Memory Types**: Conversation history, code context, project knowledge
- **Embedding Providers**: OpenAI, Gemini, Voyage, AWS Bedrock, and more
- **Configuration**: `memAgent/cipher.yml` with dynamic provider support
- **API Integration**: OpenAI and Anthropic API support

## Requirements After Installation

1. **Update API keys** in the generated `.env` file:
   ```bash
   OPENAI_API_KEY=your-openai-key-here
   ANTHROPIC_API_KEY=your-anthropic-key-here
   ```

2. **Follow setup instructions** in `MCP_SETUP_INSTRUCTIONS.md`

3. **Configure your MCP client** with the generated `.mcp.json`

## Development

### Prerequisites for Development

```bash
# Install Python dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black isort mypy

# Install system dependencies
brew install node uv  # macOS
# or
sudo apt-get install nodejs npm  # Ubuntu
curl -LsSf https://astral.sh/uv/install.sh | sh  # uv
```

### Running Tests

```bash
# Run Python unit tests
PYTHONPATH=lib python -m pytest test/python/unit/ -v

# Run integration tests
PYTHONPATH=lib python -m pytest test/python/integration/ -v

# Run with coverage
PYTHONPATH=lib python -m pytest test/python/ --cov=claude_mcp_init --cov=mcp_modules

# Run Formula tests
ruby test/formula_test.rb
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

### Building

```bash
# Build for development
make build

# Build for release
make dist

# Test binary functionality
make test-binary
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with proper tests
4. Run the test suite: `PYTHONPATH=lib python -m pytest`
5. Run code quality checks: `flake8 lib/ && black lib/ && mypy lib/`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/sho7650/homebrew-claude-mcp-init/issues)
- **Documentation**: [API Usage Guide](docs/API_USAGE.md)
- **Examples**: See the examples directory for common use cases

## Related Projects

- **Serena**: [Semantic Code Toolkit](https://github.com/serena-rpc/serena)
- **Cipher**: [Persistent Memory Layer](https://github.com/cipher-rpc/cipher)
- **MCP**: [Model Context Protocol](https://github.com/anthropics/mcp)

---

**Made with ❤️ for the Claude Code community**