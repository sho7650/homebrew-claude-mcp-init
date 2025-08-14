# lib Directory

This directory contains the core libraries and modular components for the claude-mcp-init tool.

## Core Libraries

### `core.zsh`
**Project structure and orchestration library** - The main coordination layer for the MCP starter tool.

**Features:**
- **Version Management**: Handles `MCP_STARTER_VERSION` constant
- **Project Structure Creation**: `create_project_structure()` function with in-place mode support
- **Dependency Loading**: Auto-loads required utilities and modules
- **Modular Architecture**: Simplified design for v0.10.0+

**Dependencies:**
- `utils.zsh` - Common utilities
- `file-manager.zsh` - File operations
- `mcp-modules/base.zsh` - Module interface

### `utils.zsh`
**Common utility functions library** - Zsh-optimized helper functions for the MCP tool.

**Features:**
- **Enhanced Color Output**: `print_header()`, `print_info()` functions using Zsh built-in colors
- **Zsh Optimizations**: 
  - `EXTENDED_GLOB` - Advanced pattern matching
  - `NULL_GLOB` - Empty pattern handling
  - `PIPE_FAIL` - Pipeline error propagation
- **Auto-loading**: Colors and completion features

### `file-manager.zsh`
**File operations and partial updates library** - Handles intelligent file management and JSON operations.

**Features:**
- **JSON Operations**: `merge_json()` function with jq integration
- **Dependency Detection**: `has_jq()` for checking jq availability
- **Partial Updates**: Smart merging instead of file overwrites
- **Utility Integration**: Loads `utils.zsh` if needed

## MCP Modules Directory

### `mcp-modules/`
**Plugin-based MCP module system** - Contains modular MCP server implementations.

#### `base.zsh`
**Base module interface** - Defines the standard interface all MCP modules must implement.

**Features:**
- **Module Interface**: Base class for all MCP modules
- **Validation System**: `mcp_validate_requirements()` function template
- **Module Discovery**: `MCP_MODULE_DIR` constant for module location
- **Dependency Loading**: Auto-loads `utils.zsh` and `file-manager.zsh`

#### `serena.zsh`
**Serena MCP module** - Implements the Serena semantic code toolkit integration.

**Features:**
- Follows base module interface
- Serena-specific configuration and validation
- Official Serena schema support

#### `cipher.zsh`
**Cipher MCP module** - Implements the Cipher persistent memory layer integration.

**Features:**
- Follows base module interface
- Cipher-specific configuration and API key management
- Environment variable integration

## Architecture Overview

The library follows a modular, plugin-based architecture:

1. **Core Layer**: `core.zsh` orchestrates the entire system
2. **Utility Layer**: `utils.zsh` and `file-manager.zsh` provide common functionality
3. **Module Layer**: `mcp-modules/` contains pluggable MCP implementations
4. **Interface Layer**: `base.zsh` defines the contract for all modules

**Benefits:**
- **Lazy Loading**: Modules loaded only when needed
- **Extensibility**: Easy to add new MCP modules
- **Maintainability**: Clear separation of concerns
- **Efficiency**: Optimized for Zsh shell features