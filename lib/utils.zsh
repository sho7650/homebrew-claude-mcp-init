#!/usr/bin/env zsh

# Utils Library for Claude MCP Init - Zsh Optimized
# Contains common utility functions

# Zsh optimizations
setopt EXTENDED_GLOB
setopt NULL_GLOB
setopt PIPE_FAIL

# Enable Zsh colors
autoload -U colors && colors

# Enhanced color printing using Zsh features
print_header() {
    print -P "%F{blue}%B$1%b%f"
    print -P "%F{blue}$(printf '=%.0s' {1..${#1}})%f"
}

print_info() {
    print -P "%F{blue}$1%f"
}

print_success() {
    print -P "%F{green}$1%f"
}

print_warning() {
    print -P "%F{yellow}$1%f"
}

print_error() {
    print -P "%F{red}$1%f"
}

# Optimized prerequisite checking using Zsh features
check_prerequisites() {
    local -a missing_deps=()
    local -a required_commands=(node npm python3 uv)
    
    # Check for required commands using Zsh array operations
    for cmd in $required_commands; do
        command -v $cmd &>/dev/null || missing_deps+=($cmd)
    done
    
    if (( ${#missing_deps} > 0 )); then
        print_error "Error: Missing required dependencies: ${(j: :)missing_deps}"
        print_warning "Please install with: brew install ${(j: :)missing_deps}"
        print_warning "Or follow the installation guide in README.md"
        return 1
    fi
    
    return 0
}

# Enhanced language validation using Zsh features
validate_language() {
    local language="$1"
    local -ra valid_languages=(csharp python rust java typescript javascript go cpp ruby)
    
    # Use Zsh array membership test
    [[ ${valid_languages[(ie)$language]} -le ${#valid_languages} ]]
}

# Version display with Zsh formatting
show_version() {
    local version="${1:-__VERSION__}"
    print -P "%F{blue}%Bclaude-mcp-init%b version %F{green}${version}%f"
    print -P "%F{blue}Zsh-optimized MCP server configuration tool%f"
}

# Shell information display
show_shell_info() {
    print -P "%F{blue}%BShell Information:%b%f"
    print -P "%F{green}Detected shell: zsh (optimized)%f"
    print -P "%F{blue}Version: ${ZSH_VERSION}%f"
    print -P "%F{blue}Features: Extended globbing, associative arrays, enhanced completion%f"
}

# Check if a file exists and is readable
file_exists() {
    [[ -f "$1" && -r "$1" ]]
}

# Check if a directory exists and is accessible
dir_exists() {
    [[ -d "$1" && -x "$1" ]]
}

# Get absolute path using Zsh modifier
get_absolute_path() {
    print "${1:A}"
}

# Get directory name using Zsh modifier
get_dirname() {
    print "${1:h}"
}

# Get basename using Zsh modifier
get_basename() {
    print "${1:t}"
}

# Mark as loaded (avoid read-only conflicts)
[[ -z "${UTILS_LOADED:-}" ]] && typeset UTILS_LOADED=1

# Export functions for use in other scripts (quietly)
typeset -fx print_header print_info print_success print_warning print_error >/dev/null 2>&1
typeset -fx check_prerequisites validate_language show_version show_shell_info >/dev/null 2>&1
typeset -fx file_exists dir_exists get_absolute_path get_dirname get_basename >/dev/null 2>&1