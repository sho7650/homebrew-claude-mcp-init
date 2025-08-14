bin Directory

This directory contains the main executable for the MCP starter project.

## Files

### `claude-mcp-init`
**Main executable script** - A Zsh-based modular MCP (Model Context Protocol) server configuration tool.

**Key Features:**
- **Version**: 0.10.0 - Modular architecture with unified executable
- **Shell**: Zsh with advanced optimizations enabled
  - `EXTENDED_GLOB` - Enhanced pattern matching
  - `NULL_GLOB` - Handle empty glob patterns gracefully
  - `PIPE_FAIL` - Proper error handling in pipelines
- **Color Support**: Auto-loads Zsh colors and tab completion
- **Modular Design**: Loads core libraries from `../lib/core.zsh`

**Architecture:**
- **Library Path**: `../lib/` (relative to script location)
- **Core Dependencies**: 
  - `core.zsh` - Project structure and orchestration
  - Auto-loads additional utilities and MCP modules
- **Error Handling**: Production-ready configuration with graceful fallbacks

**Usage:**
The script serves as the entry point for creating and configuring MCP server setups with support for multiple modules (Serena, Cipher, etc.) and flexible deployment options.

**Script Metadata:**
- `SCRIPT_VERSION`: Replaced during build process
- `SCRIPT_NAME`: claude-mcp-init
- `SCRIPT_DIR`: Auto-detected script directory
- `LIB_DIR`: Library directory path resolution