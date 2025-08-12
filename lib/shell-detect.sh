#!/usr/bin/env bash

# Shell Detection Library for MCP Starter
# Detects the current shell environment for optimal script execution

# Function to detect the current shell
detect_current_shell() {
    local shell_name=""
    
    # Method 1: Check $SHELL environment variable
    if [ -n "$SHELL" ]; then
        shell_name=$(basename "$SHELL")
        case "$shell_name" in
            "bash"|"zsh"|"fish"|"nu")
                echo "$shell_name"
                return 0
                ;;
        esac
    fi
    
    # Method 2: Check parent process name
    local parent_pid=$PPID
    if [ -n "$parent_pid" ]; then
        # Try different methods to get process name
        if command -v ps >/dev/null 2>&1; then
            shell_name=$(ps -p "$parent_pid" -o comm= 2>/dev/null | sed 's/^-//')
        elif [ -r "/proc/$parent_pid/comm" ]; then
            shell_name=$(cat "/proc/$parent_pid/comm" 2>/dev/null)
        fi
        
        case "$shell_name" in
            "bash"|"zsh"|"fish"|"nu"|"nushell")
                [ "$shell_name" = "nushell" ] && shell_name="nu"
                echo "$shell_name"
                return 0
                ;;
            "powershell"|"pwsh")
                echo "powershell"
                return 0
                ;;
        esac
    fi
    
    # Method 3: Check for shell-specific features
    # Test for Fish shell
    if [ -n "$FISH_VERSION" ]; then
        echo "fish"
        return 0
    fi
    
    # Test for Zsh
    if [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
        return 0
    fi
    
    # Test for Bash
    if [ -n "$BASH_VERSION" ]; then
        echo "bash"
        return 0
    fi
    
    # Method 4: PowerShell detection
    if [ -n "$PSVersionTable" ] || [ -n "$PSHOME" ]; then
        echo "powershell"
        return 0
    fi
    
    # Default fallback to bash
    echo "bash"
    return 0
}

# Function to check if shell is supported
is_shell_supported() {
    local shell_type="$1"
    case "$shell_type" in
        "bash"|"zsh"|"fish"|"powershell"|"nu")
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to get shell-specific configuration advice
get_shell_advice() {
    local shell_type="$1"
    
    case "$shell_type" in
        "bash")
            echo "Add 'alias mcp-starter=/usr/local/bin/mcp-starter' to ~/.bashrc"
            ;;
        "zsh")
            echo "Add 'alias mcp-starter=/usr/local/bin/mcp-starter' to ~/.zshrc"
            ;;
        "fish")
            echo "Add 'abbr --add mcp-starter /usr/local/bin/mcp-starter' to ~/.config/fish/config.fish"
            ;;
        "powershell")
            echo "Add 'Set-Alias mcp-starter /usr/local/bin/mcp-starter' to your PowerShell profile"
            ;;
        "nu")
            echo "Add 'alias mcp-starter = /usr/local/bin/mcp-starter' to ~/.config/nushell/config.nu"
            ;;
        *)
            echo "Shell configuration not available for: $shell_type"
            ;;
    esac
}