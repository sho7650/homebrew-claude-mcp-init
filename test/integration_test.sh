#!/usr/bin/env bash

# Integration Tests for MCP Starter
# Tests the unified mcp-starter command functionality

set -euo pipefail

# Test configuration
readonly TEST_DIR="$(mktemp -d)"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ROOT_DIR="$(dirname "$SCRIPT_DIR")"
readonly MCP_STARTER="${1:-${ROOT_DIR}/build/bin/mcp-starter}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_color() {
    printf "%b%s%b\n" "$2" "$1" "$NC"
}

log_info() {
    print_color "$1" "$BLUE"
}

log_success() {
    print_color "✅ $1" "$GREEN"
}

log_error() {
    print_color "❌ $1" "$RED"
}

log_warning() {
    print_color "⚠️  $1" "$YELLOW"
}

# Test assertion functions
assert_command_succeeds() {
    local command="$1"
    local description="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if eval "$command" >/dev/null 2>&1; then
        log_success "PASS: $description"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "FAIL: $description"
        log_error "Command failed: $command"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_command_fails() {
    local command="$1"
    local description="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if ! eval "$command" >/dev/null 2>&1; then
        log_success "PASS: $description"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "FAIL: $description"
        log_error "Command should have failed: $command"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_file_exists() {
    local file="$1"
    local description="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if [ -f "$file" ]; then
        log_success "PASS: $description"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "FAIL: $description"
        log_error "File not found: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_directory_exists() {
    local dir="$1"
    local description="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if [ -d "$dir" ]; then
        log_success "PASS: $description"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "FAIL: $description"
        log_error "Directory not found: $dir"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_file_contains() {
    local file="$1"
    local pattern="$2"
    local description="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        log_success "PASS: $description"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "FAIL: $description"
        log_error "Pattern '$pattern' not found in file: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
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
    
    # Check if binary exists
    if [ ! -f "$MCP_STARTER" ]; then
        log_error "MCP Starter binary not found: $MCP_STARTER"
        log_error "Run 'make build' first"
        exit 1
    fi
    
    # Make binary executable
    chmod +x "$MCP_STARTER"
    
    # Change to test directory
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
    assert_file_contains "$project_name/.serena/project.yml" "primary_language: $language" "Serena config should have Python as primary"
    assert_file_contains "$project_name/claude-mcp-config.json" "\"--language\"" "Claude config should include language flag"
    assert_file_contains "$project_name/claude-mcp-config.json" "\"$language\"" "Claude config should include Python language"
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
    
    local languages=("typescript" "javascript" "python" "java" "go" "rust" "php" "elixir" "clojure" "c" "cpp")
    
    for lang in "${languages[@]}"; do
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

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi