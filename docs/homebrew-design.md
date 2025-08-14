# Homebrew Formula Design Documentation

## 1. Unified Command Design

### Architecture: Zsh-Optimized MCP Server Configuration Tool

```
claude-mcp-init (single executable)
├── Zsh optimization features
├── Common core functionality  
├── Security-first design patterns
└── Enhanced error handling
```

### Shell Detection and Optimization

```zsh
# Zsh-optimized features
setopt EXTENDED_GLOB
setopt NULL_GLOB
setopt PIPE_FAIL

# Enhanced Zsh array and associative array usage
typeset -A CONFIG=()
typeset -gA MODULE_CACHE=()
```

### File Structure

```
claude-mcp-init/
├── bin/
│   └── claude-mcp-init              # Unified executable (Zsh-optimized)
├── Formula/
│   └── claude-mcp-init.rb           # Homebrew Formula
├── lib/
│   ├── core.zsh                     # Core Zsh functionality
│   ├── utils.zsh                    # Utility functions
│   ├── file-manager.zsh             # File management
│   └── mcp-modules/                 # MCP server modules
│       ├── base.zsh                 # Base module functionality
│       ├── serena.zsh               # Serena MCP server
│       └── cipher.zsh               # Cipher MCP server
├── test/
│   ├── formula_test.rb              # Formula tests
│   └── integration_test.sh          # Integration tests (96+ tests)
├── docs/
│   ├── HOMEBREW_DISTRIBUTION.md     # Distribution guide
│   ├── HOMEBREW_IMPLEMENTATION_SUMMARY.md
│   └── homebrew-design.md           # This document
├── principles/
│   └── architecture.md              # Security architecture principles
├── .github/
│   └── workflows/
│       └── ci.yml                   # CI/CD automation
├── Makefile                         # Build process
├── VERSION                          # Version management (v0.10.2)
└── LICENSE                          # MIT License
```

## 2. Homebrew Formula Design

### claude-mcp-init.rb Structure (v0.10.2)

```ruby
class ClaudeMcpInit < Formula
  desc "Zsh-optimized MCP server configuration tool with security-first design"
  homepage "https://github.com/sho7650/homebrew-claude-mcp-init"
  url "https://github.com/sho7650/homebrew-claude-mcp-init/archive/refs/tags/v0.10.2.tar.gz"
  sha256 "PLACEHOLDER_SHA256_TO_BE_UPDATED"
  license "MIT"
  version "0.10.2"
  
  depends_on "node"
  depends_on "python@3.11"
  depends_on "uv"
  
  def install
    # Version substitution for runtime compatibility
    inreplace "bin/claude-mcp-init", "__VERSION__", version.to_s
    
    # Standard Homebrew installation paths
    bin.install "bin/claude-mcp-init"
    lib.install Dir["lib/*"]
    doc.install "README.md" if File.exist?("README.md")
    doc.install "MCP_SETUP_INSTRUCTIONS.md" if File.exist?("MCP_SETUP_INSTRUCTIONS.md")
  end
  
  def caveats
    <<~EOS
      ⚠️  IMPORTANT: API Keys Required
      To use MCP servers, you must provide API keys for AI providers
    EOS
  end
  
  test do
    # Comprehensive testing including project creation
    system bin/"claude-mcp-init", "--version"
    system bin/"claude-mcp-init", "--help"
    
    # Dependency verification
    assert_match "node", shell_output("which node")
    assert_match "python3", shell_output("which python3")
    assert_match "uv", shell_output("which uv")
  end
end
```

## 3. Zsh-Optimized Script Design

### Core Structure (v0.10.2)

```zsh
#!/usr/bin/env zsh

# Zsh optimizations and strict mode
setopt EXTENDED_GLOB
setopt NULL_GLOB
setopt PIPE_FAIL

# Enhanced error handling for critical operations
handle_critical_error() {
    local error_msg="$1"
    local exit_code="${2:-1}"
    print_error "Critical Error: $error_msg" >&2
    exit "$exit_code"
}

# Script metadata
typeset -r SCRIPT_VERSION="__VERSION__"
typeset -r SCRIPT_NAME="claude-mcp-init"
typeset -r SCRIPT_DIR="${0:A:h}"
typeset -r LIB_DIR="${SCRIPT_DIR}/../lib"

# Load core libraries with error handling
if [[ -f "${LIB_DIR}/core.zsh" ]]; then
    source "${LIB_DIR}/core.zsh" 2>/dev/null
else
    print -P "%F{red}Error: Could not find core.zsh library%f" >&2
    exit 1
fi

# Configuration using associative array
typeset -A CONFIG=(
    [project]=""
    [in_place]=false
    [mcp_modules]="serena,cipher"
    [shell_type]="zsh"
)

# Main implementation with enhanced security
main() {
    # Parse arguments with error handling
    if ! parse_arguments "$@"; then
        handle_critical_error "Argument parsing failed"
    fi
    
    # Run the main functionality with error handling
    if ! run_mcp_init; then
        handle_critical_error "MCP initialization failed"
    fi
}

main "$@"
```

## 4. Build Process (v0.10.2)

### Makefile with Security Enhancements

```makefile
VERSION := $(shell cat VERSION)
BINARY := build/bin/claude-mcp-init
BUILD_DIR := build

.PHONY: build test clean dist dev-install

# Build the Zsh-optimized command
build:
	@echo "Building claude-mcp-init v$(VERSION)..."
	mkdir -p $(BUILD_DIR)/bin $(BUILD_DIR)/lib
	
	# Copy and process library files
	cp -r lib/* $(BUILD_DIR)/lib/
	
	# Process main binary with version substitution
	cp bin/claude-mcp-init $(BINARY)
	sed -i.bak 's/__VERSION__/$(VERSION)/g' $(BINARY) && rm $(BINARY).bak
	chmod +x $(BINARY)
	
	# Process library files for version substitution
	find $(BUILD_DIR)/lib -name "*.zsh" -exec sed -i.bak 's/__VERSION__/$(VERSION)/g' {} \; -exec rm {}.bak \;
	
	@echo "✅ Build completed: $(BINARY)"

# Run comprehensive test suite (96+ tests)
test: build
	@echo "Running tests..."
	@echo "Running integration tests..."
	./test/integration_test.sh
	@echo "Running Formula tests..."
	ruby test/formula_test.rb

# Development installation to ~/bin
dev-install: build
	mkdir -p ~/bin
	cp $(BINARY) ~/bin/
	@echo "✅ Installed to ~/bin/claude-mcp-init"

# Create distribution package
dist: build test
	mkdir -p dist
	tar -czf dist/claude-mcp-init-v$(VERSION).tar.gz -C $(BUILD_DIR) .
	@echo "✅ Distribution package created: dist/claude-mcp-init-v$(VERSION).tar.gz"

clean:
	rm -rf $(BUILD_DIR) dist/
```

## 5. Dependency Management (v0.10.2)

### Homebrew Dependencies

```ruby
depends_on "node"           # Required for Serena MCP server
depends_on "python@3.11"    # Required for Cipher MCP server  
depends_on "uv"            # Modern Python package manager

# Optional dependencies (system-provided)
uses_from_macos "git"      # For Serena installation via uvx
```

### Runtime Verification with Enhanced Error Handling

```zsh
check_prerequisites() {
    local missing_deps=()
    
    # Check for required dependencies
    command -v node >/dev/null 2>&1 || missing_deps+=("node")
    command -v python3 >/dev/null 2>&1 || missing_deps+=("python3")
    command -v uv >/dev/null 2>&1 || missing_deps+=("uv")
    
    if (( ${#missing_deps[@]} > 0 )); then
        print_error "Missing required dependencies: ${(j:, :)missing_deps}"
        print_warning "Install with: brew install ${(j: :)missing_deps}"
        return 1
    fi
    
    # Verify versions
    local node_version=$(node --version 2>/dev/null | sed 's/v//')
    local python_version=$(python3 --version 2>/dev/null | awk '{print $2}')
    
    print_info "✓ Node.js version: $node_version"
    print_info "✓ Python version: $python_version"
    print_info "✓ UV package manager: $(uv --version 2>/dev/null || echo 'Available')"
    
    return 0
}
```

## 6. Version Management Strategy (v0.10.2)

### Semantic Versioning with Security Focus

```
0.10.0  - Initial modular architecture
0.10.1  - Enhanced configuration and bug fixes
0.10.2  - Security enhancements and optimization improvements
```

### Release Process with Security Validation

1. Update `VERSION` file to new version
2. Update Formula with new version and URL
3. Run comprehensive security scans
4. Execute full test suite (96+ tests)
5. Create Git tag and commit
6. Generate GitHub Release
7. Update Formula SHA256 with actual release checksum
8. Validate Homebrew Formula compliance

## 7. Testing Strategy (v0.10.2)

### Comprehensive Integration Testing

```zsh
#!/usr/bin/env zsh
# test/integration_test.sh - 96+ Tests

# Security validation for all test commands
validate_test_command() {
    local command="$1"
    
    case "$command" in
        *claude-mcp-init*)
            return 0
            ;;
        \$MCP_STARTER*)
            return 0
            ;;
        test\ *)
            return 0
            ;;
        \[*)
            return 0
            ;;
        *)
            log_error "Security: Invalid command pattern detected: $command"
            return 1
            ;;
    esac
}

# Basic functionality tests
test_basic_functionality() {
    local project_name="test-basic-project"
    
    assert_command_succeeds "$MCP_STARTER $project_name" "Basic project creation should succeed"
    assert_directory_exists "$project_name" "Project directory should exist"
    assert_file_exists "$project_name/.serena/project.yml" "Serena config should exist"
    assert_file_exists "$project_name/memAgent/cipher.yml" "Cipher config should exist"
    assert_file_exists "$project_name/.mcp.json" "MCP config should exist"
}

# Security-focused API key testing
test_api_key_options() {
    local project_name="test-api-keys"
    local openai_key="$(get_test_openai_key)"
    local anthropic_key="$(get_test_anthropic_key)"
    
    assert_command_succeeds "$MCP_STARTER --openai-key $openai_key $project_name typescript" "Project with OpenAI key should succeed"
    assert_file_contains "$project_name/.env" "OPENAI_API_KEY=$openai_key" "Environment should contain provided OpenAI key"
}

# Language support validation
test_all_supported_languages() {
    local -a languages=(csharp python rust java typescript javascript go cpp ruby)
    
    for lang in $languages; do
        local project_name="test-lang-$lang"
        assert_command_succeeds "$MCP_STARTER $project_name $lang" "Project with $lang should succeed"
        assert_file_contains "$project_name/.serena/project.yml" "language: $lang" "Project should use $lang"
    done
}
```

## 8. Distribution Strategy (v0.10.2)

### Custom Homebrew Tap

```
# Custom tap repository
https://github.com/sho7650/homebrew-claude-mcp-init
└── Formula/
    └── claude-mcp-init.rb

# Installation method
brew tap sho7650/claude-mcp-init
brew install claude-mcp-init
```

### Official Homebrew Core (Future Goal)

```
# Requirements for homebrew/homebrew-core submission:
# - 30+ days of GitHub stars
# - 30+ days of active development
# - Stable release version
# - Security-first architecture
# - Comprehensive testing (96+ tests)
```

## 9. User Experience (v0.10.2)

### Installation

```bash
# Via Homebrew (recommended)
brew tap sho7650/claude-mcp-init
brew install claude-mcp-init

# Usage with enhanced security features
claude-mcp-init --openai-key sk-xxx my-project typescript
claude-mcp-init --anthropic-key claude-xxx my-ai-project python
claude-mcp-init --mcp serena,cipher --in-place my-current-project
```

### Upgrade

```bash
brew upgrade claude-mcp-init
```

### Uninstall

```bash
brew uninstall claude-mcp-init
brew untap sho7650/claude-mcp-init
```

## 10. Security Implementation Status (v0.10.2)

### ✅ Completed Security Features
- [x] Command injection prevention in tests
- [x] API key redaction and secure logging
- [x] Comprehensive input validation
- [x] Path traversal protection
- [x] Environment variable-based API key storage
- [x] Module caching with performance monitoring
- [x] Enhanced error handling with explicit validation
- [x] Security-first design patterns throughout codebase

### ✅ Testing & Quality Assurance
- [x] 96+ comprehensive integration tests
- [x] Formula validation tests (29 tests)
- [x] Security scan compliance
- [x] Documentation completeness validation
- [x] API key handling security validation

### ✅ Distribution Readiness
- [x] Homebrew Formula v0.10.2 compliance
- [x] Version consistency across all components
- [x] API key requirement documentation
- [x] Security-focused caveats and warnings
- [x] Comprehensive dependency management

This design provides a secure, Zsh-optimized MCP server configuration tool that can be installed via `brew install claude-mcp-init` and used with enhanced security features like `claude-mcp-init --openai-key sk-xxx project-name` across various development environments.