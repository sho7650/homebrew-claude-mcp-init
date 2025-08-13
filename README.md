# Claude MCP Init

Modular command-line tool for configuring MCP (Model Context Protocol) servers with support for Serena (semantic code toolkit) and Cipher (persistent memory layer).

## Overview

Claude MCP Init v0.10.0 features a **modular plugin architecture** that allows you to selectively configure MCP servers based on your specific needs. The tool automatically creates project structures, generates configurations, and sets up environment variables for seamless integration with Claude Code, Cursor, and other MCP clients.

**🆕 Version 0.10.0 - Modular Architecture**
- **Plugin-based modules**: Load only the MCP servers you need
- **Selective configuration**: Use `--mcp` to choose specific modules  
- **Enhanced embedding support**: 9 embedding providers including local options
- **Environment variable management**: Secure API key handling via `.env` files
- **Partial file updates**: Smart merging instead of overwrites
- **Improved extensibility**: Easy to add new MCP modules

## Key Features

- **🔧 Modular Architecture**: Plugin-based system for MCP modules (serena, cipher, and future modules)
- **🎯 Selective Loading**: Choose specific modules with `--mcp serena`, `--mcp cipher`, or both
- **🔐 Secure API Management**: Environment variable-based API key handling
- **🌐 Universal Compatibility**: Generates `.mcp.json` compatible with Claude Code, Cursor, and other MCP clients
- **🚀 Enhanced Embedding Support**: OpenAI, Gemini, Voyage, Qwen, AWS Bedrock, Azure, LM Studio, Ollama
- **📁 Smart File Operations**: Intelligent merging of configuration files
- **⚡ Zsh Optimized**: Built specifically for Zsh with performance enhancements
- **🏠 In-Place Mode**: Initialize MCP configuration in existing projects
- **📝 Official Schema Support**: Full compatibility with Serena and Cipher specifications

## Prerequisites

- **Zsh** - Required shell (macOS default, available on all platforms)
- **Node.js** and **npm** - Required for Serena MCP server
- **Python 3.11+** - Required for Cipher MCP server  
- **uv** - Python package manager ([installation guide](https://github.com/astral-sh/uv))

## Installation

### Homebrew (Recommended)

```zsh
# Add the tap
brew tap yourusername/claude-mcp-init

# Install Claude MCP Init
brew install claude-mcp-init

# Use it immediately
claude-mcp-init my-project typescript
```

### Manual Installation

1. Clone this repository:
```zsh
git clone https://github.com/yourusername/claude-mcp-init.git
cd claude-mcp-init
```

2. Build the command:
```zsh
make build
```

3. Test the built command:
```zsh
./build/bin/claude-mcp-init --version
./build/bin/claude-mcp-init --help
```

4. Install locally (optional):
```zsh
# System-wide installation (requires sudo)
make install

# Or development installation (no sudo required)
make dev-install
```

## Usage

### Command Syntax

```zsh
claude-mcp-init [OPTIONS] <project_name> [language]
```

### Modular Configuration Options

- `--mcp <modules>`: Select specific MCP modules (default: `serena,cipher`)
  - `--mcp serena` - Only Serena semantic code toolkit
  - `--mcp cipher` - Only Cipher persistent memory
  - `--mcp serena,cipher` - Both modules (default)

### API Key Options

- `--openai-key KEY`: OpenAI API key for Cipher LLM and embeddings
- `--anthropic-key KEY`: Anthropic API key for Cipher LLM
- `--cipher-embedding PROVIDER`: Embedding provider (see supported providers below)
- `--cipher-embedding-key KEY`: API key for embedding provider

### General Options

- `-n, --in-place`: Initialize in current directory instead of creating new project folder
- `-h, --help`: Show help information
- `-v, --version`: Show version information
- `--shell`: Show shell information

## Supported Embedding Providers

| Provider | Command | Environment Variables |
|----------|---------|----------------------|
| **OpenAI** | `--cipher-embedding openai` | `OPENAI_API_KEY` |
| **Azure OpenAI** | `--cipher-embedding azure-openai` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |
| **Gemini** | `--cipher-embedding gemini` | `GEMINI_API_KEY` |
| **Voyage** | `--cipher-embedding voyage` | `VOYAGE_API_KEY` |
| **Qwen** | `--cipher-embedding qwen` | `QWEN_API_KEY` |
| **AWS Bedrock** | `--cipher-embedding aws-bedrock` | `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |
| **LM Studio** | `--cipher-embedding lmstudio` | (local, no API key required) |
| **Ollama** | `--cipher-embedding ollama` | (local, no API key required) |
| **Disabled** | `--cipher-embedding disabled` | (embeddings disabled) |

## Examples

### Basic Usage

```zsh
# Create new project with both Serena and Cipher
claude-mcp-init my-project typescript

# Initialize in current directory
claude-mcp-init -n my-project python

# Use only Serena module
claude-mcp-init --mcp serena my-code-project rust

# Use only Cipher module
claude-mcp-init --mcp cipher my-memory-project javascript
```

### With API Keys

```zsh
# OpenAI for LLM and embeddings
claude-mcp-init --openai-key sk-xxx my-project python

# Anthropic for LLM, separate embedding provider
claude-mcp-init --anthropic-key claude-xxx --cipher-embedding voyage --cipher-embedding-key vo-xxx my-project typescript

# Multiple embedding options
claude-mcp-init --openai-key sk-xxx --cipher-embedding gemini --cipher-embedding-key gem-xxx my-project go
```

### Local Embedding Providers

```zsh
# Using LM Studio (local)
claude-mcp-init --anthropic-key claude-xxx --cipher-embedding lmstudio my-project python

# Using Ollama (local)  
claude-mcp-init --openai-key sk-xxx --cipher-embedding ollama my-project rust

# Disable embeddings entirely
claude-mcp-init --openai-key sk-xxx --cipher-embedding disabled my-project javascript
```

### Supported Languages

- **Official Serena Support**: `csharp`, `python`, `rust`, `java`, `typescript`, `javascript`, `go`, `cpp`, `ruby`
- **Legacy languages** (fallback to typescript): `php`, `elixir`, `clojure`, `c`

## Project Structure

Claude MCP Init creates the following directory structure:

```
<project_name>/
├── .serena/
│   └── project.yml         # Serena configuration (if --mcp includes serena)
├── memAgent/
│   └── cipher.yml          # Cipher configuration (if --mcp includes cipher)
├── .env                    # Environment variables (API keys)
├── .mcp.json              # Universal MCP server configuration  
└── MCP_SETUP_INSTRUCTIONS.md # Setup guide
```

## Configuration Examples

### cipher.yml (Environment Variable References)

```yaml
# LLM Configuration
llm:
  provider: openai
  model: gpt-4-turbo
  apiKey: $OPENAI_API_KEY

# Embedding Configuration
embedding:
  type: voyage
  model: voyage-3-large
  apiKey: $VOYAGE_API_KEY
  # Note: Voyage models use fixed 1024 dimensions
```

### .env (API Keys)

```bash
# Environment Variables for MCP Servers
OPENAI_API_KEY=sk-your-actual-openai-key
VOYAGE_API_KEY=vo-your-actual-voyage-key
ANTHROPIC_API_KEY=claude-your-actual-anthropic-key
```

### .mcp.json (Universal MCP Configuration)

```json
{
  "mcpServers": {
    "serena": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant",
        "--project",
        "/absolute/path/to/your/project"
      ],
      "env": {}
    },
    "cipher": {
      "type": "stdio",
      "command": "cipher",
      "args": ["--mode", "mcp"],
      "env": {}
    }
  }
}
```

## Post-Installation Setup

1. **Configure API keys** in `.env` file:
   ```zsh
   # Edit the generated .env file
   nano .env
   # Add your actual API keys
   ```

2. **Install MCP dependencies**:
   ```zsh
   # Install UV package manager (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install Cipher MCP server  
   uv add cipher-mcp
   
   # Note: Serena installs automatically via uvx on first use
   ```

3. **Configure your MCP client**:
   - **Claude Code**: Use the generated `.mcp.json` configuration
   - **Cursor**: Copy `.mcp.json` to `.cursor/mcp.json`
   - **Other MCP clients**: Use server configurations from `.mcp.json`

4. **Test the setup**:
   ```zsh
   # Source environment variables
   source .env
   
   # Test Cipher
   cipher --mode mcp --help
   
   # Verify environment variables
   echo "OpenAI Key set: ${OPENAI_API_KEY:+YES}"
   ```

## Advanced Configuration

### AWS Bedrock Setup

```zsh
claude-mcp-init --openai-key sk-xxx --cipher-embedding aws-bedrock my-project python

# Then configure AWS credentials in .env:
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
```

### Azure OpenAI Setup

```zsh
claude-mcp-init --anthropic-key claude-xxx --cipher-embedding azure-openai --cipher-embedding-key azure-key my-project typescript

# Configure Azure endpoint in .env:
# AZURE_OPENAI_API_KEY=your-azure-key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
```

## Troubleshooting

### Common Issues

**Missing dependencies error:**
- Ensure Node.js, npm, Python 3.11+, and uv are installed
- Check that commands are available in your PATH

**Module not found error:**
- Use `--mcp serena,cipher` to specify both modules explicitly
- Check that module files exist in `lib/mcp-modules/`

**API key errors:**
- Verify API keys are correctly set in `.env` file
- Source the environment: `source .env`
- Check API key format and validity

**Embedding provider issues:**
- Ensure correct provider name (use `--help` to see options)
- Verify API keys for external providers
- For local providers (ollama, lmstudio), ensure servers are running

### Verification Steps

1. **Check module loading:**
   ```zsh
   claude-mcp-init --help
   # Should show modular options
   ```

2. **Test MCP servers:**
   - Look for the hammer icon in Claude Code
   - Available tools should include Serena and/or Cipher tools

3. **Test individual modules:**
   ```zsh
   # Test Serena only
   claude-mcp-init --mcp serena test-serena python
   
   # Test Cipher only  
   claude-mcp-init --mcp cipher --openai-key sk-test test-cipher typescript
   ```

## Development

### Building from Source

```zsh
# Clone repository
git clone https://github.com/yourusername/claude-mcp-init.git
cd claude-mcp-init

# Build and test
make build
make test

# Run development version
./build/bin/claude-mcp-init --version
```

### Project Structure

```
claude-mcp-init/
├── bin/claude-mcp-init     # Main executable
├── lib/
│   ├── core.zsh           # Core orchestration
│   ├── utils.zsh          # Common utilities
│   ├── file-manager.zsh   # File operations
│   └── mcp-modules/       # MCP modules
│       ├── base.zsh       # Base module interface
│       ├── serena.zsh     # Serena module
│       └── cipher.zsh     # Cipher module
├── test/                  # Test suite
├── Formula/               # Homebrew formula
└── docs/                  # Documentation
```

## Contributing

Contributions are welcome! Areas for contribution:
- New MCP module implementations
- Additional embedding provider support
- Enhanced error handling and validation
- Documentation improvements
- Test coverage enhancements

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resources

- [Serena MCP Server](https://github.com/oraios/serena)
- [Cipher MCP Server](https://github.com/campfirein/cipher)
- [Claude Code MCP Documentation](https://docs.anthropic.com/claude-code/mcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the generated `MCP_SETUP_INSTRUCTIONS.md` in your project
3. Open an issue in this repository
4. Consult the official MCP documentation