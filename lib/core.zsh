#!/usr/bin/env zsh

# Core Library for Claude MCP Init - Simplified for v0.10.0
# Handles project structure and orchestration

# Load dependencies (avoiding double-loading)
if [[ -z "${UTILS_LOADED:-}" ]]; then
    source "${0:A:h}/utils.zsh"
fi
if [[ -z "${FILE_MANAGER_LOADED:-}" ]]; then
    source "${0:A:h}/file-manager.zsh"
fi
source "${0:A:h}/mcp-modules/base.zsh"

# Global configuration
typeset -r MCP_STARTER_VERSION="__VERSION__"  # Will be replaced during build

# Mark utils as loaded
typeset -r UTILS_LOADED=1

# Project structure creation with enhanced Zsh features
create_project_structure() {
    local project_name="$1"
    local in_place_mode="${2:-false}"
    local project_path
    
    if [[ "$in_place_mode" == "true" ]]; then
        # In-place mode: use current directory
        project_path="${PWD:A}"  # Zsh absolute path
        
        # Safety checks for in-place mode
        local existing_dirs=()
        [[ -d "${project_path}/.serena" ]] && existing_dirs+=(".serena/")
        [[ -d "${project_path}/memAgent" ]] && existing_dirs+=("memAgent/")
        
        if (( ${#existing_dirs} > 0 )); then
            print_warning "Warning: MCP configuration directories already exist in current directory" >&2
            for dir in $existing_dirs; do
                print_warning "  - $dir directory found" >&2
            done
            
            # Enhanced user input - check if we're in a non-interactive environment
            if [[ -t 0 && -t 1 ]]; then
                local reply
                print -n "Do you want to continue and potentially overwrite existing configuration? (y/n): " >&2
                read -q reply
                print >&2
                [[ "$reply" != "y" ]] && { print_error "Aborted." >&2; return 1 }
            else
                # Non-interactive mode: proceed automatically for in-place mode
                print_info "Non-interactive mode: proceeding with existing directories" >&2
            fi
        fi
        
        # Check if we're in a git repository
        [[ -d "${project_path}/.git" ]] && {
            print_info "Note: You're initializing MCP configuration in a git repository" >&2
            print_info "The configuration files will be created in the repository root" >&2
        }
        
    else
        # Normal mode: create new project directory
        project_path="${PWD}/${project_name}"
        
        if [[ -d "$project_path" ]]; then
            print_warning "Warning: Project directory already exists: $project_path" >&2
            if [[ -t 0 && -t 1 ]]; then
                local reply
                print -n "Do you want to continue? (y/n): " >&2
                read -q reply
                print >&2
                [[ "$reply" != "y" ]] && { print_error "Aborted." >&2; return 1 }
            else
                # Non-interactive mode: proceed automatically
                print_info "Non-interactive mode: proceeding with existing directory" >&2
            fi
        fi
        
        # Create project directory
        ensure_directory "$project_path"
    fi
    
    print "$project_path"
    return 0
}

# Configure MCP servers
# Security-first API key handling patterns
redact_api_key() {
    local api_key="$1"
    
    if [[ -z "$api_key" ]]; then
        echo "[EMPTY]"
        return
    fi
    
    # Show only first 6 and last 4 characters for debugging
    local key_length=${#api_key}
    if (( key_length <= 10 )); then
        echo "[REDACTED]"
    else
        local prefix="${api_key:0:6}"
        local suffix="${api_key: -4}"
        echo "${prefix}...${suffix}"
    fi
}

secure_log_api_key() {
    local provider="$1"
    local api_key="$2"
    local redacted_key=$(redact_api_key "$api_key")
    
    print_info "✓ $provider API key configured: $redacted_key"
}

# Secure environment variable handling for API keys  
create_secure_env_entry() {
    local env_name="$1"
    local api_key="$2"
    
    # Never log the actual key value
    if [[ -n "$api_key" ]]; then
        echo "${env_name}=${api_key}"
    fi
}

# Validate that sensitive data doesn't leak into logs
check_for_key_leaks() {
    local text="$1"
    
    # Check for common API key patterns in log output
    if [[ "$text" == *"sk-"* ]] || [[ "$text" == *"claude-"* ]] || [[ "$text" == *"vo-"* ]]; then
        print_error "SECURITY WARNING: Potential API key detected in output!"
        return 1
    fi
    
    return 0
}

# Input validation functions for security and reliability
validate_project_name() {
    local project_name="$1"
    
    # Check if empty
    if [[ -z "$project_name" ]]; then
        return 1
    fi
    
    # Check format: alphanumeric start, alphanumeric/dots/hyphens/underscores allowed
    if [[ ! "$project_name" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]*$ ]]; then
        return 1
    fi
    
    # Check length (reasonable limits)
    if (( ${#project_name} > 100 )); then
        return 1
    fi
    
    return 0
}

validate_api_key() {
    local api_key="$1"
    local provider="$2"
    
    # Check if empty
    if [[ -z "$api_key" ]]; then
        return 1
    fi
    
    # Provider-specific validation
    case "$provider" in
        openai)
            # OpenAI keys start with sk- and have specific length
            if [[ ! "$api_key" =~ ^sk-[a-zA-Z0-9]{20,}$ ]]; then
                return 1
            fi
            ;;
        anthropic)
            # Anthropic keys typically start with claude- or sk-ant-
            if [[ ! "$api_key" =~ ^(claude-|sk-ant-)[a-zA-Z0-9_-]{10,}$ ]]; then
                return 1
            fi
            ;;
        voyage)
            # Voyage keys typically start with vo-
            if [[ ! "$api_key" =~ ^vo-[a-zA-Z0-9]{10,}$ ]]; then
                return 1
            fi
            ;;
        gemini)
            # Gemini keys are alphanumeric
            if [[ ! "$api_key" =~ ^[a-zA-Z0-9_-]{20,}$ ]]; then
                return 1
            fi
            ;;
        *)
            # Generic validation for unknown providers
            if [[ ! "$api_key" =~ ^[a-zA-Z0-9_-]{8,}$ ]]; then
                return 1
            fi
            ;;
    esac
    
    return 0
}

validate_language() {
    local language="$1"
    local -a supported_languages=(csharp python rust java typescript javascript go cpp ruby)
    
    # Check if empty
    if [[ -z "$language" ]]; then
        return 1
    fi
    
    # Check if language is in supported list
    if [[ "${supported_languages[(i)$language]}" -gt "${#supported_languages}" ]]; then
        return 1
    fi
    
    return 0
}

validate_module_name() {
    local module_name="$1"
    local -a known_modules=(serena cipher)
    
    # Check if empty
    if [[ -z "$module_name" ]]; then
        return 1
    fi
    
    # Check format: alphanumeric and underscores only
    if [[ ! "$module_name" =~ ^[a-zA-Z0-9_]+$ ]]; then
        return 1
    fi
    
    # Check if module is known (optional warning, not blocking)
    if [[ "${known_modules[(i)$module_name]}" -gt "${#known_modules}" ]]; then
        print_warning "Unknown module: $module_name"
    fi
    
    return 0
}

validate_file_path() {
    local file_path="$1"
    
    # Check if empty
    if [[ -z "$file_path" ]]; then
        return 1
    fi
    
    # Check for dangerous characters
    if [[ "$file_path" == *";"* ]] || [[ "$file_path" == *"|"* ]] || [[ "$file_path" == *"&"* ]] || [[ "$file_path" == *"\$"* ]] || [[ "$file_path" == *"\`"* ]]; then
        return 1
    fi
    
    # Check for path traversal attempts
    if [[ "$file_path" == *"../"* ]] || [[ "$file_path" == *"..\\"* ]]; then
        return 1
    fi
    
    return 0
}

# Module loading cache and registry for performance optimization
typeset -gA MODULE_CACHE=()
typeset -gA MODULE_LOADING_TIMES=()

# Centralized module loader with caching
load_mcp_module() {
    local module_name="$1"
    local module_file="${LIB_DIR}/mcp-modules/${module_name}.zsh"
    
    # Check if module is already loaded (cache hit)
    if [[ -n "${MODULE_CACHE[$module_name]:-}" ]]; then
        return 0
    fi
    
    # Check if module file exists
    if [[ ! -f "$module_file" ]]; then
        print_error "MCP module not found: $module_name"
        print_error "Searched: $module_file"
        return 1
    fi
    
    # Record loading start time for performance monitoring
    local start_time=$(date +%s%N)
    
    # Source the module file with error handling
    if ! source "$module_file" 2>&1; then
        print_error "Failed to source module: $module_name"
        print_error "Error details for $module_file"
        return 1
    fi
    
    # Record successful loading in cache
    MODULE_CACHE[$module_name]="loaded"
    
    # Calculate and store loading time
    local end_time=$(date +%s%N)
    local load_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    MODULE_LOADING_TIMES[$module_name]=$load_time
    
    return 0
}

# Get module loading statistics
get_module_stats() {
    local total_modules=${#MODULE_CACHE[@]}
    local total_time=0
    
    for module in ${(k)MODULE_LOADING_TIMES}; do
        local time=${MODULE_LOADING_TIMES[$module]}
        total_time=$(( total_time + time ))
    done
    
    print_info "Module Loading Statistics:"
    print_info "  Total modules loaded: $total_modules"
    print_info "  Total loading time: ${total_time}ms"
    
    for module in ${(k)MODULE_LOADING_TIMES}; do
        local time=${MODULE_LOADING_TIMES[$module]}
        print_info "  $module: ${time}ms"
    done
}

configure_mcp_servers() {
    local project_path="$1"
    local -a mcp_modules=("${(@s:,:)2}")  # Split comma-separated modules
    shift 2
    local -A config=("$@")
    
    local mcp_file="${project_path}/.mcp.json"
    local env_file="${project_path}/.env"
    local -A all_env_vars=()
    
    # Initialize .mcp.json structure only if file doesn't exist
    if [[ ! -f "$mcp_file" ]]; then
        echo '{"mcpServers": {}}' > "$mcp_file"
    fi
    
    # Process each MCP module using cached loading
    for module_name in $mcp_modules; do
        print_info "Configuring $module_name..."
        
        # Load module using centralized cache system
        if ! load_mcp_module "$module_name"; then
            print_error "Failed to load module: $module_name"
            continue
        fi
        
        # Call module-specific functions directly to avoid override issues
        # Validate requirements
        if ! ${module_name}_validate_requirements; then
            print_error "Requirements not met for $module_name"
            continue
        fi
        
        # Generate module configuration (pass key-value pairs)
        ${module_name}_generate_config "$project_path" ${(kv)config}
        
        # Get server configuration and add to .mcp.json
        local server_config=$(${module_name}_get_server_config "$project_path" ${(kv)config})
        update_mcp_json "$mcp_file" "$module_name" "$server_config"
        
        # Collect environment variables with secure handling
        local env_vars=$(${module_name}_get_env_vars)
        if [[ -n "$env_vars" ]]; then
            while IFS='=' read -r key value; do
                all_env_vars[$key]="$value"
                # Secure logging for API keys
                if [[ "$key" =~ .*API_KEY$ ]]; then
                    local provider="${key%_API_KEY}"
                    secure_log_api_key "$provider" "$value"
                fi
            done <<< "$env_vars"
        fi
    done
    
    # Create .env file with basic placeholders
    if [[ ! -f "$env_file" ]]; then
        cat > "$env_file" <<EOF
# Environment Variables for MCP Servers
# Generated by claude-mcp-init v${MCP_STARTER_VERSION:-0.10.0}

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
EOF
    fi
    
    # Update with any collected environment variables
    for key in ${(k)all_env_vars}; do
        local value="${all_env_vars[$key]}"
        update_env_file "$env_file" "$key" "$value"
    done
    
    print_success "✓ MCP servers configured successfully"
    
    # Display module loading statistics if debug mode is enabled
    if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
        echo
        get_module_stats
    fi
}

# Create setup instructions
create_setup_instructions() {
    local project_path="$1"
    local -a mcp_modules=("${(@s:,:)2}")
    local instructions_file="${project_path}/MCP_SETUP_INSTRUCTIONS.md"
    
    cat > "$instructions_file" <<EOF
# MCP Server Setup Instructions

Generated by claude-mcp-init v${MCP_STARTER_VERSION}
Configured modules: ${(j:, :)mcp_modules}

## Prerequisites Checklist

1. **Environment Variables**
   - [ ] Review and update API keys in \`.env\` file
   - [ ] Verify all required API keys are set

2. **Install Dependencies**
EOF
    
    # Add module-specific instructions
    for module_name in $mcp_modules; do
        case "$module_name" in
            cipher)
                cat >> "$instructions_file" <<EOF
   
   **Cipher requirements:**
   - [ ] UV package manager: \`curl -LsSf https://astral.sh/uv/install.sh | sh\`
   - [ ] Cipher MCP server: \`uv add cipher-mcp\`
EOF
                ;;
            serena)
                cat >> "$instructions_file" <<EOF
   
   **Serena requirements:**
   - [ ] Node.js and npm (for Serena)
   - [ ] Serena will auto-install via uvx on first use
EOF
                ;;
        esac
    done
    
    cat >> "$instructions_file" <<EOF

## Quick Start

### 1. Set up Environment
\`\`\`zsh
# Source environment variables
source .env

# Verify API keys are set
env | grep -E 'API_KEY|KEY='
\`\`\`

### 2. Configure Your MCP Client
Use the generated \`.mcp.json\` file with your MCP client:

**For Claude Code:**
- Copy or merge \`.mcp.json\` settings into your Claude Code MCP configuration

**For Cursor:**
- Copy \`.mcp.json\` to \`.cursor/mcp.json\` (global) or project root (project-specific)

**For other MCP clients:**
- Use the server configurations from \`.mcp.json\`

## Configuration Files

- **\`.mcp.json\`** - Universal MCP server configuration
- **\`.env\`** - Environment variables (API keys)
EOF
    
    # Add module-specific config files
    for module_name in $mcp_modules; do
        case "$module_name" in
            serena)
                echo "- **\`.serena/project.yml\`** - Serena configuration" >> "$instructions_file"
                ;;
            cipher)
                echo "- **\`memAgent/cipher.yml\`** - Cipher configuration" >> "$instructions_file"
                ;;
        esac
    done
    
    cat >> "$instructions_file" <<EOF

## Troubleshooting

### API Keys
- Ensure all required API keys are set in \`.env\`
- Verify keys have sufficient credits and permissions

### Dependencies
- Check that all required tools are installed (uv, npm, etc.)
- Run the prerequisite installation commands if needed

## Additional Resources

- [Claude MCP Init Documentation](https://github.com/sho7650/claude-mcp-init)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)
EOF
    
    print_success "Created setup instructions: $instructions_file"
}

# Enhanced help with modular options
show_help() {
    cat <<EOF
$(print -P "%F{blue}%Bclaude-mcp-init%b - Modular MCP server configuration tool v${MCP_STARTER_VERSION}%f")

$(print -P "%F{blue}%BUSAGE:%b%f")
    claude-mcp-init [OPTIONS] <PROJECT_NAME>

$(print -P "%F{blue}%BARGUMENTS:%b%f")
    <PROJECT_NAME>    Name of the project (used in configuration files)

$(print -P "%F{blue}%BCORE OPTIONS:%b%f")
    --mcp MODULES         Comma-separated list of MCP modules to configure (default: serena,cipher)
    -n, --in-place        Initialize in current directory instead of creating new project folder
    -h, --help            Show this help message
    -v, --version         Show version information
    --shell               Show detected shell information

$(print -P "%F{blue}%BMODULE OPTIONS:%b%f")
EOF
    
    # Show options for available modules
    local module_dir="${LIB_DIR}/mcp-modules"
    if [[ -d "$module_dir" ]]; then
        for module_file in "$module_dir"/*.zsh(N); do
            local module_name="${module_file:t:r}"
            if [[ "$module_name" != "base" ]]; then
                # Try to load module and get options
                if source "$module_file" 2>/dev/null && type "${module_name}_get_cli_options" &>/dev/null; then
                    local options=$(${module_name}_get_cli_options)
                    if [[ -n "$options" ]]; then
                        echo "$options"
                    fi
                fi
            fi
        done
    fi
    
    cat <<EOF

$(print -P "%F{blue}%BEXAMPLES:%b%f")
    # Configure both Serena and Cipher (default)
    claude-mcp-init my-project
    
    # Configure only Serena
    claude-mcp-init --mcp serena my-project
    
    # Configure with API keys
    claude-mcp-init --mcp cipher --cipher-openai-key sk-xxx my-project
    
    # Initialize in current directory
    claude-mcp-init -n --mcp serena,cipher my-project

$(print -P "%F{blue}%BAVAILABLE MODULES:%b%f")
EOF
    
    # List available modules
    local module_dir="${LIB_DIR}/mcp-modules"
    if [[ -d "$module_dir" ]]; then
        for module_file in "$module_dir"/*.zsh(N); do
            local module_name="${module_file:t:r}"
            if [[ "$module_name" != "base" ]]; then
                echo "    - $module_name"
            fi
        done
    else
        echo "    - serena"
        echo "    - cipher"
    fi
    
    cat <<EOF

For more information, visit: https://github.com/sho7650/claude-mcp-init
EOF
}

# Export core functions (quietly)
typeset -fx create_project_structure configure_mcp_servers create_setup_instructions show_help \
    validate_project_name validate_api_key validate_language validate_module_name validate_file_path \
    redact_api_key secure_log_api_key check_for_key_leaks load_mcp_module get_module_stats >/dev/null 2>&1