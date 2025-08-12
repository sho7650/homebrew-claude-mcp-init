# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a shell script specification project for MCP (Model Context Protocol) server configuration. The main file `specifications.md` contains complete technical specifications and embedded implementations for multi-shell scripts that automate the setup of two MCP servers: Serena (semantic code toolkit) and Cipher (persistent memory layer).

## Key Files

- `specifications.md` - Comprehensive technical specification (1,518 lines) containing:
  - Complete shell script implementations for bash, zsh, fish, PowerShell, and Nushell
  - Configuration templates for Serena and Cipher
  - Testing strategies and documentation

## Script Development Commands

Since this is a specification project, the primary task is extracting and creating the actual executable scripts:

### To extract and create shell scripts from specifications:
```bash
# Extract bash script (lines 80-484)
sed -n '80,484p' specifications.md > mcp-starter.sh
chmod +x mcp-starter.sh

# Extract zsh script (lines 486-878)
sed -n '486,878p' specifications.md > mcp-starter.zsh
chmod +x mcp-starter.zsh

# Extract fish script (lines 880-1246)
sed -n '880,1246p' specifications.md > mcp-starter.fish
chmod +x mcp-starter.fish

# Extract PowerShell script (lines 1250-1305)
sed -n '1250,1305p' specifications.md > mcp-starter.ps1

# Extract Nushell script (lines 1307-1346)
sed -n '1307,1346p' specifications.md > mcp-starter.nu
```

### To test the extracted scripts:
```bash
# Test bash script
./mcp-starter.sh test-project typescript

# Test with different language
./mcp-starter.sh my-python-project python
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