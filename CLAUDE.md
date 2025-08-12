# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-shell MCP (Model Context Protocol) server configuration tool that automates the setup of two MCP servers: Serena (semantic code toolkit) and Cipher (persistent memory layer). The project provides both a unified command for Homebrew distribution and individual shell scripts for different environments.

## Key Files

- `bin/mcp-starter` - Unified executable with shell auto-detection
- `lib/` - Core libraries for the unified command:
  - `core.sh` - Main functionality and configuration generation
  - `shell-detect.sh` - Shell environment detection
- `scripts/` - Individual shell script implementations:
  - `mcp-starter.sh` (Bash)
  - `mcp-starter.zsh` (Zsh) 
  - `mcp-starter.fish` (Fish)
  - `mcp-starter.ps1` (PowerShell)
  - `mcp-starter.nu` (Nushell)
- `Formula/mcp-starter.rb` - Homebrew Formula for distribution
- `docs/` - Documentation files
- `test/` - Test suite for integration and Formula validation

## Development Commands

### Build the unified command:
```bash
make build
```

### Test the project:
```bash
make test
```

### Install locally for development:
```bash
make dev-install
```

### Create distribution package:
```bash
make dist
```

### Test individual scripts:
```bash
# Test bash script
./scripts/mcp-starter.sh test-project typescript

# Test with different language
./scripts/mcp-starter.sh my-python-project python
```

### Test unified command:
```bash
# After building
./build/bin/mcp-starter test-project typescript

# After dev-install
~/bin/mcp-starter test-project typescript
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

## Script Functionality

All scripts implement the same core features:
1. Parse command-line arguments (project name and optional language)
2. Create project directory structure
3. Generate Serena configuration (`.serena/project.yml`)
4. Generate Cipher configuration (`memAgent/cipher.yml`)
5. Create environment file with OpenAI API key prompt
6. Generate Claude Code MCP configuration
7. Provide setup instructions

## Supported Languages

When creating Serena configurations, these languages are supported:
- typescript (default)
- javascript, python, java, go, rust, php, elixir, clojure, c, cpp

## Prerequisites Check

Scripts verify these dependencies:
- Node.js and npm/npx
- Python with uv package manager
- OpenAI API key (prompted during setup)
- Claude Code installation