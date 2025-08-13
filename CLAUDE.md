# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Zsh-optimized MCP (Model Context Protocol) server configuration tool that automates the setup of two MCP servers: Serena (semantic code toolkit) and Cipher (persistent memory layer). The project provides a unified Zsh command optimized for performance and features.

**Version:** 0.9.2 (Official Serena Schema + Zsh-optimized)

## Key Files

- `bin/claude-mcp-init` - Zsh-optimized unified executable
- `lib/` - Core Zsh libraries:
  - `core.zsh` - Main functionality and configuration generation (Zsh-optimized)
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
│   └── project.yml         # Serena configuration
├── memAgent/
│   └── cipher.yml          # Cipher configuration
└── .env                    # Environment variables
```

## Zsh Command Functionality

The unified Zsh command implements these core features:
1. **Official Serena Schema Compliance**: Generates `.serena/project.yml` using official Serena MCP server schema
2. **Smart Gitignore Integration**: Uses `ignore_all_files_in_gitignore: true` instead of hardcoded patterns
3. **Zsh-Optimized Argument Parsing**: Enhanced option parsing with native zparseopts and error handling
4. **Project Structure Creation**: Normal mode creates `./PROJECT_NAME/` directory or in-place mode initializes current directory
5. **Cipher Configuration**: Creates comprehensive `memAgent/cipher.yml` for persistent memory
6. **Environment Setup**: Creates `.env` file with OpenAI API key prompts
7. **Claude Code Integration**: Generates ready-to-use `claude-mcp-config.json`
8. **Setup Instructions**: Creates detailed `MCP_SETUP_INSTRUCTIONS.md`

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