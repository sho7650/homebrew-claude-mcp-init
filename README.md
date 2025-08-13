# Claude MCP Init

Zsh-optimized command-line tool for configuring Serena and Cipher MCP (Model Context Protocol) servers for use with Claude Code.

## Overview

Claude MCP Init is a streamlined, Zsh-optimized tool that automatically:
- Creates project directory structures with support for in-place initialization
- Configures Serena MCP server (semantic code retrieval and editing toolkit)
- Configures Cipher MCP server (persistent memory layer for context)
- Generates Claude Code integration configuration
- Creates comprehensive setup instructions for deployment

**Key Features:**
- **Universal MCP Configuration**: Generates `.mcp.json` compatible with Claude Code, Cursor, and other MCP clients
- **Advanced API Key Management**: Command-line options for OpenAI, Anthropic, and vector store API keys
- **Official Serena Schema**: Full compatibility with Serena MCP server (v0.9.2+)
- **Dynamic Provider Configuration**: Intelligent provider selection based on available API keys
- **Zsh-Optimized**: Built specifically for Zsh with enhanced performance and features
- **In-Place Mode**: Initialize MCP configuration in existing projects with `-n` flag
- **Smart Gitignore Integration**: Uses project's `.gitignore` instead of hardcoded patterns
- **Language Support**: 9 officially supported languages + legacy fallback
- **Homebrew Ready**: Easy installation and distribution via Homebrew

## Prerequisites

Before using Claude MCP Init, ensure you have the following installed:

- **Zsh** - Required shell (macOS default, available on all platforms)
- **Node.js** and **npm** - Required for Serena MCP server
- **Python 3.11+** - Required for Cipher MCP server  
- **uv** - Python package manager ([installation guide](https://github.com/astral-sh/uv))
- **OpenAI API Key** - Required for Cipher's LLM and embedding features

## Installation

### Homebrew (Recommended)

The easiest way to install Claude MCP Init:

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

2. Build the Zsh-optimized command:
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

For development work, use the dev-install target which installs to `~/bin`:

```zsh
make dev-install

# Add ~/bin to your PATH if not already present
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Now you can run from anywhere:
claude-mcp-init my-project typescript
```

## Usage

### Command Syntax

```zsh
claude-mcp-init [OPTIONS] <project_name> [language]
```

### Parameters

- `<project_name>` (required): Name of the project (used in configuration files)
- `[language]` (optional): Programming language for Serena configuration
  - Default: `typescript`
  - **Official Serena Support**: `csharp`, `python`, `rust`, `java`, `typescript`, `javascript`, `go`, `cpp`, `ruby`
  - **Legacy languages** (fallback to typescript): `php`, `elixir`, `clojure`, `c`

### Options

- `-n, --in-place`: Initialize in current directory instead of creating new project folder
- `--openai-key KEY`: Set OpenAI API key for Cipher MCP server
- `--anthropic-key KEY`: Set Anthropic API key for Cipher MCP server  
- `--vector-store-key KEY`: Set vector store API key (optional)
- `--interactive-keys`: Interactive API key setup mode
- `--generate-mcp-only`: Generate only .mcp.json in existing project

### Examples

**Create a new project directory (default behavior):**
```zsh
claude-mcp-init my-app typescript
# Creates ./my-app/ directory with MCP configuration
```

**Initialize in current directory (in-place mode):**
```zsh
cd existing-project
claude-mcp-init -n my-app typescript
# Creates .serena/ and memAgent/ in current directory
```

**Different programming languages:**
```zsh
# Python project
claude-mcp-init my-python-app python

# Rust project
claude-mcp-init my-rust-app rust

# JavaScript project  
claude-mcp-init my-js-app javascript
```

**With API key configuration:**
```zsh
# With OpenAI API key
claude-mcp-init --openai-key sk-your-key-here my-project typescript

# With both OpenAI and Anthropic keys
claude-mcp-init --openai-key sk-xxx --anthropic-key claude-xxx my-project python

# With Anthropic key only (auto-configures Cipher for Anthropic)
claude-mcp-init --anthropic-key claude-xxx my-project rust

# Interactive key setup
claude-mcp-init --interactive-keys my-project typescript
```

**Advanced usage:**
```zsh
# Generate only .mcp.json in existing project
cd existing-project
claude-mcp-init --generate-mcp-only --openai-key sk-xxx existing-project

# All options combined
claude-mcp-init -n --openai-key sk-xxx --anthropic-key claude-xxx my-project go
```

**Help and version information:**
```zsh
# Get help
claude-mcp-init --help

# Check version
claude-mcp-init --version

# Show shell information
claude-mcp-init --shell
```

## Project Structure

Claude MCP Init creates the following directory structure:

```
<project_name>/
├── .serena/
│   └── project.yml         # Serena configuration (official schema)
├── memAgent/
│   └── cipher.yml          # Cipher configuration  
├── .env                    # Environment variables (API keys)
├── .mcp.json              # Universal MCP configuration
└── MCP_SETUP_INSTRUCTIONS.md # Setup guide
```

## Post-Installation Setup

After running Claude MCP Init:

1. **Navigate to your project** (if not using in-place mode):
   ```zsh
   cd <project_name>
   ```

2. **Configure API keys** (if not provided during setup):
   Edit `.env` file and add your actual API keys:
   ```zsh
   # Required for Cipher MCP server
   OPENAI_API_KEY=sk-your-actual-openai-key
   
   # Optional: For additional LLM support
   ANTHROPIC_API_KEY=claude-your-actual-anthropic-key
   ```

3. **Install MCP dependencies:**
   ```zsh
   # Install UV package manager (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install Cipher MCP server
   uv add cipher-mcp
   
   # Note: Serena installs automatically via uvx on first use
   ```

4. **Configure your MCP client:**
   - **Claude Code**: Use the generated `.mcp.json` configuration
   - **Cursor**: Copy `.mcp.json` to `.cursor/mcp.json` 
   - **Other MCP clients**: Use server configurations from `.mcp.json`

5. **Test the setup:**
   ```zsh
   # Test Serena (auto-installs on first use)
   uvx --from git+https://github.com/oraios/serena serena start-mcp-server --help
   
   # Test Cipher
   cipher --mode mcp --help
   
   # Verify environment variables
   echo "OpenAI Key set: ${OPENAI_API_KEY:+YES}"
   echo "Anthropic Key set: ${ANTHROPIC_API_KEY:+YES}"
   ```

6. **Start your MCP client:**
   Launch Claude Code, Cursor, or your preferred MCP client and start using your enhanced MCP servers!

## Configuration Files

### Universal MCP Configuration (`.mcp.json`)

Universal MCP server configuration compatible with all MCP clients:
- Serena server configuration with project context
- Cipher server configuration with API key management
- Standard stdio transport protocol
- Environment variable integration

### Serena Configuration (`.serena/project.yml`)

Configures the Serena semantic code toolkit with official schema:
- Language-specific settings (9 officially supported languages)
- Project-specific configurations
- Gitignore integration
- Read-only and tool exclusion settings

### Cipher Configuration (`memAgent/cipher.yml`)

Configures the Cipher memory layer with dynamic provider support:
- LLM provider settings (OpenAI/Anthropic auto-selection)
- Embedding configuration
- Memory persistence settings
- Vector store configuration

### Environment Variables (`.env`)

Contains API keys and server configuration:
- `OPENAI_API_KEY` - For OpenAI services (LLM and embeddings)
- `ANTHROPIC_API_KEY` - For Anthropic Claude services
- `VECTOR_STORE_API_KEY` - Optional vector store integration
- `MCP_SERVER_MODE` - Server operation mode

## Troubleshooting

### Common Issues

**Missing dependencies error:**
- Ensure Node.js, npm, Python 3, and uv are installed
- Check that commands are available in your PATH

**Serena not responding:**
- Verify language servers are installed for your chosen language
- Check Claude Code logs for errors

**Cipher memory errors:**
- Verify OPENAI_API_KEY is correctly set in `.env`
- Ensure you have sufficient OpenAI API credits

**Connection issues:**
- Restart Claude Code
- Check that both MCP servers are running (look for hammer icon)
- Review logs in Claude Code

### Verification Steps

1. **Check MCP servers are running:**
   - Look for the hammer icon in Claude Code
   - Available tools should include both Serena and Cipher tools

2. **Test Serena:**
   Ask in Claude Code: "Show me the project structure"

3. **Test Cipher:**
   Ask in Claude Code: "Remember that this project uses [your framework/language]"

## Platform Support

### macOS ✅
- Native Zsh support (default shell since macOS Catalina)
- Homebrew installation available
- All features fully supported

### Linux ✅  
- Zsh available on all major distributions
- Full compatibility with package managers
- All features fully supported

### Windows ⚠️
- Requires WSL (Windows Subsystem for Linux) or Git Bash with Zsh
- Zsh installation: `choco install zsh` or via WSL
- Ensure line endings are LF, not CRLF

## Zsh Optimization Features

Claude MCP Init leverages Zsh-specific features for enhanced performance:

- **Extended Globbing**: Advanced pattern matching for file operations
- **Associative Arrays**: Efficient configuration management  
- **Enhanced Color Support**: Rich terminal output formatting
- **Built-in Options Parsing**: Native zparseopts for argument handling
- **Advanced Parameter Expansion**: Robust path and string manipulation

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug fixes and performance improvements
- Additional programming language support
- Enhanced Zsh optimizations
- Documentation improvements
- Test coverage enhancements

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resources

- [Serena Documentation](https://github.com/oraios/serena)
- [Cipher Documentation](https://github.com/campfirein/cipher)
- [Claude Code MCP Documentation](https://docs.anthropic.com/claude-code/mcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the generated `MCP_SETUP_INSTRUCTIONS.md` in your project
3. Open an issue in this repository
4. Consult the official documentation for Serena, Cipher, or Claude Code