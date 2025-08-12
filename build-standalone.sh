#!/usr/bin/env bash

# Build a standalone self-contained binary for mcp-starter
# This script inlines all library code into a single executable

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(cat "$SCRIPT_DIR/VERSION")"
BUILD_DIR="$SCRIPT_DIR/build"
OUTPUT_FILE="$BUILD_DIR/bin/mcp-starter"

echo "Building self-contained mcp-starter binary..."

# Create build directory
mkdir -p "$BUILD_DIR/bin"

# Start with the shebang and header
cat > "$OUTPUT_FILE" << 'EOF'
#!/usr/bin/env bash

# MCP Starter - Multi-shell MCP server configuration tool
# Self-contained executable for distribution
# 
# This script detects the current shell environment and executes
# the appropriate implementation for configuring Serena and Cipher
# MCP servers for use with Claude Code.

set -euo pipefail

# Script metadata
EOF

# Add version and variables
cat >> "$OUTPUT_FILE" << EOF
readonly SCRIPT_VERSION="$VERSION"
readonly SCRIPT_NAME="mcp-starter"

EOF

echo "# === INLINED LIBRARY CODE ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Inline the core library functions
echo "# Core Library Functions" >> "$OUTPUT_FILE"
# Remove the shebang line and add the core library, substitute version
tail -n +2 "$SCRIPT_DIR/lib/core.sh" | sed "s/__VERSION__/$VERSION/g" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Inline the shell detection library
echo "# Shell Detection Library Functions" >> "$OUTPUT_FILE"  
# Remove the shebang line and add the shell detection library
tail -n +2 "$SCRIPT_DIR/lib/shell-detect.sh" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "# === MAIN PROGRAM CODE ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Add the main program logic (skip the library loading section)
cat >> "$OUTPUT_FILE" << 'EOF'
# Main implementation function
run_mcp_starter() {
    local project_name="$1"
    local language="${2:-typescript}"
    local shell_type
    
    # Get current shell
    shell_type=$(detect_current_shell)
    
    print_color "$SCRIPT_NAME - Version $SCRIPT_VERSION" "$BLUE"
    print_color "====================================" "$BLUE"
    print_color "Detected shell: $shell_type" "$BLUE"
    echo
    
    # Validate language
    if ! validate_language "$language"; then
        print_color "Warning: Unsupported language '$language'. Using 'typescript' instead." "$YELLOW"
        language="typescript"
    fi
    
    print_color "Project: $project_name" "$GREEN"
    print_color "Language: $language" "$GREEN"
    echo
    
    # Check prerequisites
    print_color "Checking prerequisites..." "$BLUE"
    if ! check_prerequisites; then
        return 1
    fi
    
    # Create project structure
    print_color "Creating project structure..." "$BLUE"
    local project_path
    if ! project_path=$(create_project_structure "$project_name"); then
        return 1
    fi
    
    # Create configuration files
    print_color "Creating configuration files..." "$BLUE"
    create_serena_config "$project_path" "$language"
    create_cipher_config "$project_path"
    create_env_file "$project_path"
    generate_claude_config "$project_path" "$language"
    create_setup_instructions "$project_path" "$shell_type"
    
    echo
    print_color "✅ MCP server configuration completed successfully!" "$GREEN"
    echo
    print_color "Next steps:" "$BLUE"
    print_color "1. Navigate to project: cd $project_name" "$YELLOW"
    print_color "2. Update OPENAI_API_KEY in .env file" "$YELLOW"
    print_color "3. Follow instructions in MCP_SETUP_INSTRUCTIONS.md" "$YELLOW"
    echo
    print_color "Happy coding with Claude Code + Serena + Cipher! 🚀" "$BLUE"
    
    # Show shell-specific advice if not using a POSIX shell
    if [ "$shell_type" != "bash" ] && [ "$shell_type" != "zsh" ]; then
        echo
        print_color "Shell-specific note:" "$YELLOW"
        get_shell_advice "$shell_type"
    fi
}

# Main entry point
main() {
    # Handle options
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            show_version
            exit 0
            ;;
        --shell)
            show_shell_info
            exit 0
            ;;
        -*)
            echo "Error: Unknown option '$1'" >&2
            echo "Use '$SCRIPT_NAME --help' for usage information." >&2
            exit 1
            ;;
    esac
    
    # Validate arguments
    if [ $# -lt 1 ]; then
        print_color "Error: Missing project name" "$RED"
        echo
        echo "Usage: $SCRIPT_NAME <project_name> [language]"
        echo "Example: $SCRIPT_NAME my-project typescript"
        echo
        echo "Use '$SCRIPT_NAME --help' for more information."
        exit 1
    fi
    
    # Extract arguments
    local project_name="$1"
    local language="${2:-typescript}"
    
    # Validate project name
    if [[ ! "$project_name" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]*$ ]]; then
        print_color "Error: Invalid project name '$project_name'" "$RED"
        print_color "Project names must start with alphanumeric character and contain only letters, numbers, dots, hyphens, and underscores." "$YELLOW"
        exit 1
    fi
    
    # Run the main functionality
    run_mcp_starter "$project_name" "$language"
}

# Error handling
trap 'echo "Error: An unexpected error occurred on line $LINENO" >&2; exit 1' ERR

# Execute main function with all arguments
main "$@"
EOF

# Make the output file executable
chmod +x "$OUTPUT_FILE"

echo "✅ Self-contained binary built: $OUTPUT_FILE"
echo "File size: $(ls -lh "$OUTPUT_FILE" | awk '{print $5}')"
echo "Testing binary..."

# Quick test
if "$OUTPUT_FILE" --version; then
    echo "✅ Binary test passed"
else
    echo "❌ Binary test failed"
    exit 1
fi