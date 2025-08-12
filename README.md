# MCP Starter Scripts

Automated shell scripts for configuring and launching Serena and Cipher MCP (Model Context Protocol) servers for use with Claude Code.

## Overview

This repository provides multi-shell scripts that automatically:
- Create a project directory structure
- Configure Serena MCP server (semantic code retrieval and editing toolkit)
- Configure Cipher MCP server (memory layer for persistent context)
- Generate Claude Code integration configuration
- Create setup instructions for easy deployment

## Prerequisites

Before using the scripts, ensure you have the following installed:

- **Node.js** and **npm** - Required for Cipher installation
- **Python 3** - Required for Serena
- **uv** - Python package manager ([installation guide](https://github.com/astral-sh/uv))
- **OpenAI API Key** - Required for Cipher's LLM and embedding features

## Available Scripts

Choose the script that matches your shell:

| Shell | Script | Platform Support |
|-------|--------|-----------------|
| Bash | `scripts/claude-mcp-init.sh` | macOS, Linux, WSL |
| Zsh | `scripts/claude-mcp-init.zsh` | macOS, Linux |
| Fish | `scripts/claude-mcp-init.fish` | macOS, Linux |
| PowerShell | `scripts/claude-mcp-init.ps1` | Windows, macOS, Linux |
| Nushell | `scripts/claude-mcp-init.nu` | Cross-platform |

## Installation

### Homebrew (Recommended)

The easiest way to install MCP Starter:

```bash
# Add the tap
brew tap yourusername/claude-mcp-init

# Install MCP Starter
brew install claude-mcp-init

# Use it immediately
claude-mcp-init my-project typescript
```

### Manual Installation

#### Quick Start

1. Clone this repository:
```bash
git clone https://github.com/yourusername/claude-mcp-init.git
cd claude-mcp-init
```

2. Build the unified command:
```bash
make build
```

3. Install locally:
```bash
make install
```

#### Individual Shell Scripts

Alternatively, run the individual shell scripts directly:

#### Bash
```bash
./scripts/claude-mcp-init.sh my-project typescript
```

#### Zsh
```zsh
./scripts/claude-mcp-init.zsh my-project python
```

#### Fish
```fish
./scripts/claude-mcp-init.fish my-project javascript
```

#### PowerShell
```powershell
.\scripts\claude-mcp-init.ps1 -ProjectName my-project -Language rust
```

#### Nushell
```nu
./scripts/claude-mcp-init.nu my-project go
```

### Global Installation (Optional)

To make the script available system-wide:

```bash
# For Unix-like systems (Bash/Zsh/Fish)
sudo cp scripts/claude-mcp-init.sh /usr/local/bin/claude-mcp-init
sudo chmod +x /usr/local/bin/claude-mcp-init

# Now you can run from anywhere:
claude-mcp-init my-project typescript
```

## Usage

### Command Syntax

```bash
claude-mcp-init.<shell> <project_name> [language]
```

### Parameters

- `<project_name>` (required): Name of the project directory to create
- `[language]` (optional): Programming language for Serena configuration
  - Default: `typescript`
  - Supported: `typescript`, `javascript`, `python`, `java`, `go`, `rust`, `php`, `elixir`, `clojure`, `c`, `cpp`

### Examples

Create a TypeScript project (default):
```bash
./scripts/claude-mcp-init.sh my-app
```

Create a Python project:
```bash
./scripts/claude-mcp-init.sh my-python-app python
```

Create a Rust project:
```bash
./scripts/claude-mcp-init.zsh my-rust-app rust
```

## Project Structure

The scripts create the following directory structure:

```
<project_name>/
├── .serena/
│   └── project.yml         # Serena configuration
├── memAgent/
│   └── cipher.yml          # Cipher configuration
├── .env                    # Environment variables
├── claude-mcp-config.json  # Claude Code MCP configuration
└── MCP_SETUP_INSTRUCTIONS.md # Setup guide
```

## Post-Installation Setup

After running the script:

1. **Navigate to your project:**
   ```bash
   cd <project_name>
   ```

2. **Update the OpenAI API key:**
   Edit `.env` file and replace `your-openai-api-key-here` with your actual API key:
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key
   ```

3. **Install MCP dependencies:**
   ```bash
   # Install Cipher globally
   npm install -g @byterover/cipher
   
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **Configure Claude Code:**
   ```bash
   # Add Serena MCP server
   claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena-mcp-server --context claude-code --project $(pwd)
   
   # Add Cipher MCP server
   claude mcp add cipher -- cipher --mode mcp --agent $(pwd)/memAgent/cipher.yml
   ```

5. **Start Claude Code:**
   ```bash
   claude
   ```

6. **Initialize Serena** (in Claude Code chat):
   ```
   /mcp__serena__initial_instructions
   ```

## Configuration Files

### Serena Configuration (`.serena/project.yml`)

Configures the Serena semantic code toolkit with:
- Language-specific settings
- Tool configurations
- Memory settings
- Context and mode defaults

### Cipher Configuration (`memAgent/cipher.yml`)

Configures the Cipher memory layer with:
- LLM provider settings (OpenAI GPT-4)
- Embedding configuration
- Memory persistence settings
- Vector store configuration

### Environment Variables (`.env`)

Contains API keys and configuration options:
- `OPENAI_API_KEY` - Required for Cipher
- Optional API keys for other services
- Logging and development settings

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

## Platform-Specific Notes

### macOS
- All scripts work natively
- Zsh is the default shell since macOS Catalina

### Linux
- All Unix shell scripts work natively
- PowerShell Core required for PowerShell script

### Windows
- Use PowerShell script natively
- For Bash/Zsh/Fish scripts, use WSL (Windows Subsystem for Linux) or Git Bash
- Ensure line endings are LF, not CRLF

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug fixes
- Additional shell support
- Language configuration improvements
- Documentation enhancements

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