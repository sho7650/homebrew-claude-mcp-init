# Makefile for Claude MCP Init - Python-only Architecture
# Simplified build system for v1.0.0

SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

# Configuration
# Git tag-based version management
GIT_VERSION := $(shell git describe --tags --exact-match HEAD 2>/dev/null | sed 's/^v//' || git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || echo "")
DEFAULT_VERSION := 0.11.6
VERSION := $(if $(GIT_VERSION),$(GIT_VERSION),$(DEFAULT_VERSION))

BINARY_NAME := claude-mcp-init
BUILD_DIR := build
DIST_DIR := dist
INSTALL_PREFIX := /usr/local
TARBALL := $(DIST_DIR)/$(BINARY_NAME)-$(VERSION).tar.gz

# Files and directories
SRC_BINARY := bin/$(BINARY_NAME)
BUILD_BINARY := $(BUILD_DIR)/bin/$(BINARY_NAME)
PYTHON_LIB := lib/claude_mcp_init
PYTHON_MODULES := lib/mcp_modules
VERSION_SCRIPT := scripts/inject_version.py
FORMULA_FILE := Formula/$(BINARY_NAME).rb
DOC_FILES := $(wildcard docs/*.md)

# Build flags
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

.PHONY: help build clean test install uninstall dist release check-tools inject-version

## Display this help message
help:
	@echo "Claude MCP Init Build System (Python-only)"
	@echo "=========================================="
	@echo ""
	@echo "Available targets:"
	@awk '/^##/ { \
		line = $$0; \
		sub(/^## /, "", line); \
		getline target; \
		gsub(/:.*$$/, "", target); \
		printf "  %-20s %s\n", target, line \
	}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Current version: $(VERSION)"
	@echo "Git version: $(GIT_VERSION)"
	@echo "Build directory: $(BUILD_DIR)"
	@echo "Distribution directory: $(DIST_DIR)"

## Inject version into Python backend
inject-version:
	@echo "Injecting version $(VERSION) into Python backend..."
	@if [ -f "$(VERSION_SCRIPT)" ]; then \
		python3 "$(VERSION_SCRIPT)" "$(VERSION)" --version-file "$(PYTHON_LIB)/_version.py"; \
	else \
		echo "⚠️  Version injection script not found: $(VERSION_SCRIPT)"; \
		echo "Skipping version injection"; \
	fi

## Build documentation with version substitution
docs-build: $(DOC_FILES)
	@echo "Building documentation with version $(VERSION)..."
	@mkdir -p $(BUILD_DIR)/docs
	@for doc in $(DOC_FILES); do \
		echo "  Processing $$doc..."; \
		sed 's/__VERSION__/$(VERSION)/g; s/v__VERSION__/v$(VERSION)/g; s/VERSION="__VERSION__"/VERSION="$(VERSION)"/g' "$$doc" > "$(BUILD_DIR)/$${doc}"; \
	done
	@echo "✅ Documentation build completed"

## Build the Python-only claude-mcp-init executable
build: inject-version docs-build $(BUILD_BINARY)

$(BUILD_BINARY): $(SRC_BINARY) $(PYTHON_LIB) $(PYTHON_MODULES)
	@echo "Building $(BINARY_NAME) v$(VERSION) (Python-only)..."
	@mkdir -p $(BUILD_DIR)/bin $(BUILD_DIR)/lib $(BUILD_DIR)/share/doc $(BUILD_DIR)/Formula
	
	# Copy Python libraries
	@echo "Copying Python libraries..."
	@cp -r "$(PYTHON_LIB)" $(BUILD_DIR)/lib/
	@cp -r "$(PYTHON_MODULES)" $(BUILD_DIR)/lib/
	
	# Copy Formula and documentation
	@cp -r Formula/ $(BUILD_DIR)/Formula/
	@cp README.md $(BUILD_DIR)/share/doc/ 2>/dev/null || true
	@cp MCP_SETUP_INSTRUCTIONS.md $(BUILD_DIR)/share/doc/ 2>/dev/null || true
	
	# Process main binary with version substitution
	@cp $(SRC_BINARY) $(BUILD_BINARY)
	@sed -i.bak \
		-e 's/__VERSION__/$(VERSION)/g' \
		-e 's/__BUILD_DATE__/$(BUILD_DATE)/g' \
		-e 's/__GIT_COMMIT__/$(GIT_COMMIT)/g' \
		$(BUILD_BINARY)
	@rm $(BUILD_BINARY).bak
	
	@chmod +x $(BUILD_BINARY)
	@echo "✅ Build completed: $(BUILD_BINARY)"

## Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(DIST_DIR)
	@echo "✅ Clean completed"

## Run Python tests
test: build check-python
	@echo "Running Python tests..."
	@if [ -d test/python ]; then \
		echo "Running pytest..."; \
		cd test/python && python3 -m pytest -v; \
	fi
	@if [ -f test/formula_test.rb ]; then \
		echo "Running Formula tests..."; \
		ruby test/formula_test.rb "$(BUILD_DIR)/Formula/claude-mcp-init.rb"; \
	fi
	@echo "✅ Tests completed"

## Test the built binary with a sample project
test-binary: build
	@echo "Testing binary functionality..."
	@cd /tmp && $(realpath $(BUILD_BINARY)) test-mcp-project typescript
	@if [ -d /tmp/test-mcp-project ]; then \
		echo "✅ Test project created successfully"; \
		rm -rf /tmp/test-mcp-project; \
	else \
		echo "❌ Test project creation failed"; \
		exit 1; \
	fi

## Install to local system
install: build
	@echo "Installing $(BINARY_NAME) to $(INSTALL_PREFIX)..."
	@sudo mkdir -p $(INSTALL_PREFIX)/bin $(INSTALL_PREFIX)/lib
	@sudo cp $(BUILD_BINARY) $(INSTALL_PREFIX)/bin/
	@sudo cp -r $(BUILD_DIR)/lib/claude_mcp_init $(INSTALL_PREFIX)/lib/
	@sudo cp -r $(BUILD_DIR)/lib/mcp_modules $(INSTALL_PREFIX)/lib/
	@sudo chmod +x $(INSTALL_PREFIX)/bin/$(BINARY_NAME)
	@echo "✅ Installation completed"
	@echo "Run: $(BINARY_NAME) --version"

## Uninstall from local system
uninstall:
	@echo "Uninstalling $(BINARY_NAME)..."
	@sudo rm -f $(INSTALL_PREFIX)/bin/$(BINARY_NAME)
	@sudo rm -rf $(INSTALL_PREFIX)/lib/claude_mcp_init
	@sudo rm -rf $(INSTALL_PREFIX)/lib/mcp_modules
	@echo "✅ Uninstall completed"

## Create distribution tarball
dist: build
	@echo "Creating distribution tarball..."
	@mkdir -p $(DIST_DIR)
	@tar -czf $(TARBALL) \
		-C $(BUILD_DIR) \
		bin/$(BINARY_NAME) \
		lib \
		share \
		Formula \
		|| (echo "Failed to create tarball"; exit 1)
	@echo "✅ Distribution created: $(TARBALL)"
	@ls -lh $(TARBALL)

## Update Formula SHA256 for the tarball
update-formula: dist
	@echo "Updating Formula SHA256..."
	@if command -v shasum >/dev/null 2>&1; then \
		SHA256=$$(shasum -a 256 $(TARBALL) | cut -d' ' -f1); \
	elif command -v sha256sum >/dev/null 2>&1; then \
		SHA256=$$(sha256sum $(TARBALL) | cut -d' ' -f1); \
	else \
		echo "Error: No SHA256 utility found"; exit 1; \
	fi; \
	sed -i.bak "s/sha256 \".*\"/sha256 \"$$SHA256\"/" $(FORMULA_FILE); \
	rm $(FORMULA_FILE).bak; \
	echo "✅ Formula updated with SHA256: $$SHA256"

## Create a new release (requires git and gh CLI)
release: check-git check-gh
	@echo "Creating release v$(VERSION)..."
	@$(MAKE) dist
	@git add $(FORMULA_FILE) || true
	@git commit -m "Release v$(VERSION)" || true
	@git tag -a "v$(VERSION)" -m "Release version $(VERSION)"
	@git push origin main
	@git push origin "v$(VERSION)"
	@gh release create "v$(VERSION)" "$(TARBALL)" \
		--title "Release v$(VERSION)" \
		--notes "Claude MCP Init v$(VERSION) - Python-only architecture" \
		--latest
	@echo "✅ Release v$(VERSION) created successfully"

## Check required tools
check-tools:
	@echo "Checking required tools..."
	@command -v python3 >/dev/null || (echo "❌ python3 not found"; exit 1)
	@command -v make >/dev/null || (echo "❌ make not found"; exit 1)
	@command -v tar >/dev/null || (echo "❌ tar not found"; exit 1)
	@command -v sed >/dev/null || (echo "❌ sed not found"; exit 1)
	@echo "✅ All required tools available"

## Check git is available and working
check-git:
	@command -v git >/dev/null || (echo "❌ git not found"; exit 1)
	@git rev-parse --git-dir >/dev/null 2>&1 || (echo "❌ Not in a git repository"; exit 1)

## Check GitHub CLI is available
check-gh:
	@command -v gh >/dev/null || (echo "❌ GitHub CLI (gh) not found. Install with: brew install gh"; exit 1)

## Check Python is available and working
check-python:
	@command -v python3 >/dev/null || (echo "❌ python3 not found. Install Python 3.8+"; exit 1)
	@python3 -c "import sys; assert sys.version_info >= (3, 8)" || (echo "❌ Python 3.8+ required"; exit 1)

## Show current configuration
info:
	@echo "Claude MCP Init Build Configuration (Python-only)"
	@echo "=============================================="
	@echo "Version:        $(VERSION)"
	@echo "Binary name:    $(BINARY_NAME)"
	@echo "Build dir:      $(BUILD_DIR)"
	@echo "Dist dir:       $(DIST_DIR)"
	@echo "Install prefix: $(INSTALL_PREFIX)"
	@echo "Tarball:        $(TARBALL)"
	@echo "Build date:     $(BUILD_DATE)"
	@echo "Git commit:     $(GIT_COMMIT)"
	@echo ""
	@echo "Source files:"
	@echo "  Binary:       $(SRC_BINARY)"
	@echo "  Python lib:   $(PYTHON_LIB)"
	@echo "  Python mods:  $(PYTHON_MODULES)"
	@echo "  Formula:      $(FORMULA_FILE)"

# Development helpers
.PHONY: dev-install dev-test dev-clean

## Install for development (no sudo required)
dev-install: build
	@mkdir -p ~/dev/bin ~/dev/lib
	@cp $(BUILD_BINARY) ~/dev/bin/
	@cp -r $(BUILD_DIR)/lib/claude_mcp_init ~/dev/lib/
	@cp -r $(BUILD_DIR)/lib/mcp_modules ~/dev/lib/
	@chmod +x ~/dev/bin/$(BINARY_NAME)
	@echo "✅ Development installation completed in ~/dev/bin/"
	@echo "Add ~/dev/bin to your PATH if not already present"

## Quick development test
dev-test: dev-install
	@echo "Running quick development test..."
	@~/dev/bin/$(BINARY_NAME) --version
	@~/dev/bin/$(BINARY_NAME) --help | head -5
	@echo "✅ Development test completed"

## Clean development installation
dev-clean:
	@rm -f ~/dev/bin/$(BINARY_NAME)
	@rm -rf ~/dev/lib/claude_mcp_init
	@rm -rf ~/dev/lib/mcp_modules
	@echo "✅ Development installation cleaned"