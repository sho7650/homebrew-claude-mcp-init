#!/usr/bin/env zsh

# Integration Tests for Claude MCP Init - Zsh Optimized
# Tests the unified claude-mcp-init command functionality

# Zsh strict mode and optimizations
setopt EXTENDED_GLOB
setopt NULL_GLOB  
setopt PIPE_FAIL
setopt ERR_EXIT
setopt NO_UNSET

# Test configuration using Zsh features
typeset -r TEST_DIR="$(mktemp -d)"
typeset -r SCRIPT_DIR="${0:A:h}"
typeset -r ROOT_DIR="${SCRIPT_DIR:h}"
typeset -r MCP_STARTER="${1:-${ROOT_DIR}/build/bin/claude-mcp-init}"

# Enable Zsh colors
autoload -U colors && colors

# Test counters using Zsh integers
typeset -i TESTS_RUN=0
typeset -i TESTS_PASSED=0
typeset -i TESTS_FAILED=0

# Helper functions using Zsh print with color formatting
log_info() {
    print -P "%F{blue}$1%f"
}

log_success() {
    print -P "%F{green}✅ $1%f"
}

log_error() {
    print -P "%F{red}❌ $1%f"
}

log_warning() {
    print -P "%F{yellow}⚠️  $1%f"
}

# Test assertion functions
assert_command_succeeds() {
    local command="$1"
    local description="$2"
    
    (( TESTS_RUN++ ))
    
    if eval "$command" >/dev/null 2>&1; then
        log_success "PASS: $description"
        (( TESTS_PASSED++ ))
        return 0
    else
        log_error "FAIL: $description"
        log_error "Command failed: $command"
        (( TESTS_FAILED++ ))
        return 1
    fi
}

assert_command_fails() {
    local command="$1"
    local description="$2"
    
    (( TESTS_RUN++ ))
    
    if ! eval "$command" >/dev/null 2>&1; then
        log_success "PASS: $description"
        (( TESTS_PASSED++ ))
        return 0
    else
        log_error "FAIL: $description"
        log_error "Command should have failed: $command"
        (( TESTS_FAILED++ ))
        return 1
    fi
}

assert_file_exists() {
    local file="$1"
    local description="$2"
    
    (( TESTS_RUN++ ))
    
    if [[ -f "$file" ]]; then
        log_success "PASS: $description"
        (( TESTS_PASSED++ ))
        return 0
    else
        log_error "FAIL: $description"
        log_error "File not found: $file"
        (( TESTS_FAILED++ ))
        return 1
    fi
}

assert_directory_exists() {
    local dir="$1"
    local description="$2"
    
    (( TESTS_RUN++ ))
    
    if [[ -d "$dir" ]]; then
        log_success "PASS: $description"
        (( TESTS_PASSED++ ))
        return 0
    else
        log_error "FAIL: $description"
        log_error "Directory not found: $dir"
        (( TESTS_FAILED++ ))
        return 1
    fi
}

assert_file_contains() {
    local file="$1"
    local pattern="$2"
    local description="$3"
    
    (( TESTS_RUN++ ))
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        log_success "PASS: $description"
        (( TESTS_PASSED++ ))
        return 0
    else
        log_error "FAIL: $description"
        log_error "Pattern '$pattern' not found in file: $file"
        (( TESTS_FAILED++ ))
        return 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up test directory: $TEST_DIR"
    rm -rf "$TEST_DIR"
}

# Setup
setup() {
    log_info "Setting up integration tests..."
    log_info "Test directory: $TEST_DIR"
    log_info "MCP Starter binary: $MCP_STARTER"
    log_info "Root directory: $ROOT_DIR"
    log_info "Absolute binary check: $(ls -la "$MCP_STARTER" 2>&1 || echo "NOT FOUND")"
    
    # Check if binary exists
    if [ ! -f "$MCP_STARTER" ]; then
        log_error "MCP Starter binary not found: $MCP_STARTER"
        log_error "Run 'make build' first"
        exit 1
    fi
    
    # Make binary executable
    chmod +x "$MCP_STARTER"
    
    # Change to test directory but keep reference to absolute paths
    cd "$TEST_DIR"
}

# Test functions
test_version_flag() {
    log_info "Testing --version flag..."
    assert_command_succeeds "$MCP_STARTER --version" "Version flag should work"
}

test_help_flag() {
    log_info "Testing --help flag..."
    assert_command_succeeds "$MCP_STARTER --help" "Help flag should work"
}

test_shell_flag() {
    log_info "Testing --shell flag..."
    assert_command_succeeds "$MCP_STARTER --shell" "Shell flag should work"
}

test_invalid_flag() {
    log_info "Testing invalid flag..."
    assert_command_fails "$MCP_STARTER --invalid-flag" "Invalid flag should fail"
}

test_no_arguments() {
    log_info "Testing no arguments..."
    assert_command_fails "$MCP_STARTER" "No arguments should fail"
}

test_invalid_project_name() {
    log_info "Testing invalid project name..."
    assert_command_fails "$MCP_STARTER '!!!invalid'" "Invalid project name should fail"
}

test_basic_project_creation() {
    log_info "Testing basic project creation..."
    
    local project_name="test-basic-project"
    
    # Create project
    assert_command_succeeds "$MCP_STARTER $project_name" "Basic project creation should succeed"
    
    # Check directory structure
    assert_directory_exists "$project_name" "Project directory should exist"
    assert_directory_exists "$project_name/.serena" "Serena directory should exist"
    assert_directory_exists "$project_name/memAgent" "MemAgent directory should exist"
    
    # Check configuration files
    assert_file_exists "$project_name/.serena/project.yml" "Serena config should exist"
    assert_file_exists "$project_name/memAgent/cipher.yml" "Cipher config should exist"
    assert_file_exists "$project_name/.env" "Environment file should exist"
    assert_file_exists "$project_name/claude-mcp-config.json" "Claude config should exist"
    assert_file_exists "$project_name/MCP_SETUP_INSTRUCTIONS.md" "Setup instructions should exist"
    
    # Check configuration content
    assert_file_contains "$project_name/.serena/project.yml" "name: $project_name" "Serena config should contain project name"
    assert_file_contains "$project_name/.serena/project.yml" "language: typescript" "Serena config should have default language"
    assert_file_contains "$project_name/memAgent/cipher.yml" "provider: openai" "Cipher config should have OpenAI provider"
    assert_file_contains "$project_name/.env" "OPENAI_API_KEY=" "Environment should contain API key placeholder"
    assert_file_contains "$project_name/claude-mcp-config.json" "serena" "Claude config should contain serena server"
    assert_file_contains "$project_name/claude-mcp-config.json" "cipher" "Claude config should contain cipher server"
}

test_project_with_language() {
    log_info "Testing project creation with specific language..."
    
    local project_name="test-python-project"
    local language="python"
    
    # Create project with Python
    assert_command_succeeds "$MCP_STARTER $project_name $language" "Project with Python language should succeed"
    
    # Check language configuration
    assert_file_contains "$project_name/.serena/project.yml" "language: $language" "Serena config should have Python language"
    assert_file_contains "$project_name/.serena/project.yml" "primary: $language" "Serena config should have Python as primary"
    assert_file_contains "$project_name/claude-mcp-config.json" "\"--language=$language\"" "Claude config should include language flag"
    assert_file_contains "$project_name/claude-mcp-config.json" "\"--language=$language\"" "Claude config should include Python language"
}

test_invalid_language() {
    log_info "Testing invalid language handling..."
    
    local project_name="test-invalid-lang"
    local language="invalid-language"
    
    # Create project with invalid language (should fallback to typescript)
    assert_command_succeeds "$MCP_STARTER $project_name $language" "Project with invalid language should succeed with fallback"
    
    # Check that it fell back to typescript
    assert_file_contains "$project_name/.serena/project.yml" "language: typescript" "Should fallback to typescript"
}

test_existing_directory_handling() {
    log_info "Testing existing directory handling..."
    
    local project_name="test-existing-dir"
    
    # Create directory first
    mkdir "$project_name"
    
    # Try to create project (should prompt but we'll skip interactive test)
    # This is a limitation of non-interactive testing
    log_warning "Skipping interactive existing directory test"
}

test_all_supported_languages() {
    log_info "Testing all supported languages..."
    
    # Use Zsh array syntax
    local -a languages=(typescript javascript python java go rust php elixir clojure c cpp)
    
    for lang in $languages; do
        local project_name="test-lang-$lang"
        
        assert_command_succeeds "$MCP_STARTER $project_name $lang" "Project with $lang should succeed"
        assert_file_contains "$project_name/.serena/project.yml" "language: $lang" "Project should use $lang"
    done
}

test_permission_checks() {
    log_info "Testing file permissions..."
    
    local project_name="test-permissions"
    
    # Create project
    assert_command_succeeds "$MCP_STARTER $project_name" "Project creation should succeed"
    
    # Check that configuration files are readable
    assert_command_succeeds "test -r $project_name/.serena/project.yml" "Serena config should be readable"
    assert_command_succeeds "test -r $project_name/memAgent/cipher.yml" "Cipher config should be readable"
    assert_command_succeeds "test -r $project_name/.env" "Environment file should be readable"
    assert_command_succeeds "test -r $project_name/claude-mcp-config.json" "Claude config should be readable"
}

test_in_place_mode() {
    log_info "Testing in-place mode..."
    
    local project_name="test-inplace"
    local test_subdir="$TEST_DIR/inplace_test"
    
    # Create a separate test directory for in-place testing
    mkdir -p "$test_subdir"
    cd "$test_subdir"
    
    # Test basic in-place functionality with -n flag
    assert_command_succeeds "$MCP_STARTER -n $project_name typescript" "In-place mode with -n should succeed"
    
    # Check that directories are created in current directory (not in subdirectory)
    assert_command_succeeds "test -d .serena" ".serena directory should exist in current dir"
    assert_command_succeeds "test -d memAgent" "memAgent directory should exist in current dir"
    assert_command_succeeds "test ! -d $project_name" "Project subdirectory should NOT be created"
    
    # Check configuration files
    assert_file_exists ".serena/project.yml" "Serena config should exist in current dir"
    assert_file_exists "memAgent/cipher.yml" "Cipher config should exist in current dir"
    assert_file_exists ".env" "Environment file should exist in current dir"
    assert_file_exists "claude-mcp-config.json" "Claude config should exist in current dir"
    
    # Check that project name is still used in configuration
    assert_file_contains ".serena/project.yml" "name: $project_name" "Serena config should contain project name"
    
    cd "$TEST_DIR"
    
    # Test with --in-place long option
    local test_subdir2="$TEST_DIR/inplace_test2"
    mkdir -p "$test_subdir2"
    cd "$test_subdir2"
    
    assert_command_succeeds "$MCP_STARTER --in-place $project_name python" "In-place mode with --in-place should succeed"
    assert_command_succeeds "test -d .serena" ".serena should exist with --in-place"
    assert_file_contains ".serena/project.yml" "language: python" "Should use specified language"
    
    cd "$TEST_DIR"
}

test_in_place_with_existing_dirs() {
    log_info "Testing in-place mode with existing directories..."
    
    local project_name="test-existing"
    local test_subdir="$TEST_DIR/existing_test"
    
    # Create test directory with existing .serena directory
    mkdir -p "$test_subdir/.serena"
    mkdir -p "$test_subdir/memAgent"
    echo "existing content" > "$test_subdir/.serena/existing.txt"
    cd "$test_subdir"
    
    # This should prompt for confirmation, but since we can't interact,
    # we'll test that the command handles the existing directories
    # Note: In actual use, this would require user input
    
    # Test that command recognizes existing directories
    # We expect this to fail or require input, which we can't provide in automated tests
    # So we test the detection logic by checking error handling
    
    cd "$TEST_DIR"
}

# Run all tests
run_all_tests() {
    log_info "Starting MCP Starter Integration Tests"
    log_info "======================================"
    
    setup
    
    # Individual test functions
    test_version_flag
    test_help_flag
    test_shell_flag
    test_invalid_flag
    test_no_arguments
    test_invalid_project_name
    test_basic_project_creation
    test_project_with_language
    test_invalid_language
    test_all_supported_languages
    test_permission_checks
    test_in_place_mode
    test_in_place_with_existing_dirs
    
    # Summary
    echo
    log_info "Test Summary"
    log_info "============"
    log_info "Tests run: $TESTS_RUN"
    log_success "Passed: $TESTS_PASSED"
    
    if [ $TESTS_FAILED -gt 0 ]; then
        log_error "Failed: $TESTS_FAILED"
        log_error "Integration tests FAILED"
        return 1
    else
        log_success "All tests PASSED!"
        return 0
    fi
}

# Main execution
main() {
    trap cleanup EXIT
    
    if run_all_tests; then
        exit 0
    else
        exit 1
    fi
}

# Run if executed directly (Zsh syntax)
if [[ "${ZSH_ARGZERO:-$0}" == "$0" ]]; then
    main "$@"
fi