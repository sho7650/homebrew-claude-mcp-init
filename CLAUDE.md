# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modular MCP (Model Context Protocol) server configuration tool that automates the setup of multiple MCP servers. The tool features a plugin-based architecture allowing easy addition of new MCP modules, with built-in support for Serena (semantic code toolkit) and Cipher (persistent memory layer).

**Version:** 0.10.0 (Modular Architecture + Partial File Updates + Enhanced API Management)

## Key Files

- `bin/claude-mcp-init` - Modular MCP configuration executable
- `lib/` - Core libraries:
  - `core.zsh` - Project structure and orchestration
  - `utils.zsh` - Common utility functions
  - `file-manager.zsh` - File operations and partial updates
  - `mcp-modules/` - MCP module plugins:
    - `base.zsh` - Base module interface
    - `serena.zsh` - Serena MCP module
    - `cipher.zsh` - Cipher MCP module
- `Formula/claude-mcp-init.rb` - Homebrew Formula for distribution
- `docs/` - Documentation files with version management
- `test/` - Zsh-specific test suite for integration and Formula validation
  - `integration_test.sh` - Zsh-optimized integration tests
  - `formula_test.rb` - Homebrew Formula validation tests

## Development Commands

### Build the Zsh-optimized command:
```zsh
make build
```

### Test the project:
```zsh
make test  # Runs 96 tests (67 integration + 29 Formula tests)
```

### Install locally for development:
```zsh
make dev-install  # Installs to ~/bin without sudo
```

### Create distribution package:
```zsh
make dist
```

### Test the unified command:
```zsh
# After building
./build/bin/claude-mcp-init test-project typescript

# Test in-place mode
./build/bin/claude-mcp-init -n my-project python

# Test with modular configuration (v0.10.0+)
./build/bin/claude-mcp-init --mcp serena my-project
./build/bin/claude-mcp-init --mcp cipher --cipher-openai-key sk-xxx my-project
./build/bin/claude-mcp-init --mcp serena,cipher my-project

# After dev-install
~/bin/claude-mcp-init test-project typescript

# Version and help
./build/bin/claude-mcp-init --version
./build/bin/claude-mcp-init --help
./build/bin/claude-mcp-init --shell
```

## Architecture

The scripts create this structure when executed:
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

## Zsh Command Functionality

The modular command implements these core features:
1. **Modular Architecture**: Plugin-based system for MCP modules
2. **Selective Module Loading**: Load only required MCP modules on demand
3. **Partial File Updates**: Smart merging of `.mcp.json` and `.gitignore` files
4. **Environment Variable Management**: Cipher API keys managed via `.env`
5. **Dynamic Module Discovery**: Automatic detection of available MCP modules
6. **Module-specific Options**: Each module can define its own CLI options
7. **Backwards Compatibility**: Supports legacy command-line options
8. **Optimized Code Structure**: Reduced to ~600 lines with better organization
9. **JSON Operations**: Uses jq for intelligent JSON merging when available

### v0.10.0 Architecture Improvements
- **Modular Design**: Each MCP in separate module file (~100 lines each)
- **Lazy Loading**: Modules loaded only when needed
- **File Management**: Intelligent partial updates instead of overwrites
- **API Key Handling**: Environment-based configuration for Cipher

### Zsh-Specific Optimizations
- **Enhanced Color Output**: Rich terminal formatting using Zsh's built-in color features
- **Associative Arrays**: Efficient configuration management
- **Extended Globbing**: Advanced file pattern matching
- **Robust Error Handling**: Comprehensive error trapping and validation

### Mode Options
- **Normal Mode**: Creates `./PROJECT_NAME/` directory with all configuration files inside
- **In-Place Mode** (`-n`/`--in-place`): Creates `.serena/` and `memAgent/` directories in current working directory with safety checks

## Supported Languages

When creating Serena configurations, these languages are supported:
- **Official Serena Schema** (v0.9.2+): `csharp`, `python`, `rust`, `java`, `typescript`, `javascript`, `go`, `cpp`, `ruby`
- **typescript** (default) - Full TypeScript support with advanced tooling
- **Legacy fallback**: `php`, `elixir`, `clojure`, `c` automatically fallback to typescript

## Prerequisites Check

The Zsh command verifies these dependencies:
- **Zsh shell** (required)
- **Node.js and npm/npx** (for Serena MCP server)
- **Python 3.11+ with uv** package manager (for Cipher MCP server)
- **OpenAI API key** (prompted during setup)