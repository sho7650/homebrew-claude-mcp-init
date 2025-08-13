#!/usr/bin/env zsh

# Base MCP Module for Claude MCP Init
# Defines the interface for MCP modules

# Load dependencies
source "${0:A:h:h}/utils.zsh"
source "${0:A:h:h}/file-manager.zsh"

# Set module directory for this base class
typeset -r MCP_MODULE_DIR="${0:A:h}"

# Base MCP Module Class
# Each MCP module should implement these functions

# Validate that the module's requirements are met
# Returns 0 if valid, 1 otherwise
mcp_validate_requirements() {
    local module_name="${1:-base}"
    print_error "Error: mcp_validate_requirements not implemented for $module_name"
    return 1
}

# Generate module-specific configuration files
# Args: project_path, config_array
mcp_generate_config() {
    local module_name="${1:-base}"
    print_error "Error: mcp_generate_config not implemented for $module_name"
    return 1
}

# Get the MCP server configuration for .mcp.json
# Returns JSON string
mcp_get_server_config() {
    local module_name="${1:-base}"
    print_error "Error: mcp_get_server_config not implemented for $module_name"
    return 1
}

# Get required environment variables
# Returns associative array of env vars
mcp_get_env_vars() {
    local module_name="${1:-base}"
    # Default: no environment variables required
    echo ""
}

# Get module metadata
mcp_get_metadata() {
    local module_name="${1:-base}"
    cat <<EOF
{
    "name": "$module_name",
    "version": "1.0.0",
    "description": "Base MCP module"
}
EOF
}

# Get CLI options for this module
mcp_get_cli_options() {
    local module_name="${1:-base}"
    # Return empty by default
    echo ""
}

# Process CLI arguments for this module
mcp_process_args() {
    local module_name="${1:-base}"
    # No-op by default
    return 0
}

# Initialize module (called once when loaded)
mcp_init() {
    local module_name="${1:-base}"
    # No-op by default
    return 0
}

# Cleanup module resources
mcp_cleanup() {
    local module_name="${1:-base}"
    # No-op by default
    return 0
}

# Helper function to load a module
load_mcp_module() {
    local module_name="$1"
    local module_file="${MCP_MODULE_DIR}/${module_name}.zsh"
    
    if [[ ! -f "$module_file" ]]; then
        print_error "MCP module not found: $module_name"
        print_error "Searched: $module_file"
        print_error "Module dir: ${MCP_MODULE_DIR}"
        return 1
    fi
    
    # Source the module file
    source "$module_file"
    
    # Initialize the module
    if type "${module_name}_init" &>/dev/null; then
        "${module_name}_init"
    fi
    
    return 0
}

# Check if a module is loaded
is_module_loaded() {
    local module_name="$1"
    type "${module_name}_generate_config" &>/dev/null
}

# Get list of available modules
get_available_modules() {
    local -a modules=()
    
    for module_file in "${MCP_MODULE_DIR}"/*.zsh(N); do
        local module_name="${module_file:t:r}"
        [[ "$module_name" != "base" ]] && modules+=("$module_name")
    done
    
    echo "${modules[@]}"
}

# Mark as loaded
typeset -r MCP_BASE_LOADED=1

# Export base functions (quietly)
typeset -fx mcp_validate_requirements mcp_generate_config mcp_get_server_config >/dev/null 2>&1
typeset -fx mcp_get_env_vars mcp_get_metadata mcp_get_cli_options >/dev/null 2>&1
typeset -fx mcp_process_args mcp_init mcp_cleanup >/dev/null 2>&1
typeset -fx load_mcp_module is_module_loaded get_available_modules >/dev/null 2>&1