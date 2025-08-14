# Makefile for Claude MCP Init Homebrew Distribution
# Handles building, testing, and releasing the Zsh-optimized claude-mcp-init command

SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

# Configuration
VERSION := $(shell cat VERSION 2>/dev/null || echo "1.0.0")
BINARY_NAME := claude-mcp-init
BUILD_DIR := build
DIST_DIR := dist
INSTALL_PREFIX := /usr/local
TARBALL := $(DIST_DIR)/$(BINARY_NAME)-$(VERSION).tar.gz

# Files and directories
SRC_BINARY := bin/$(BINARY_NAME)
BUILD_BINARY := $(BUILD_DIR)/bin/$(BINARY_NAME)
LIB_FILES := $(wildcard lib/*.zsh)
FORMULA_FILE := Formula/$(BINARY_NAME).rb
TEST_FILES := $(wildcard test/*.sh)
DOC_FILES := $(wildcard docs/*.md)

# Build flags
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

.PHONY: help build docs-build clean test install uninstall dist release check-tools format lint

## Display this help message
help:
	@echo "Claude MCP Init Build System"
	@echo "========================"
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
	@echo "Build directory: $(BUILD_DIR)"
	@echo "Distribution directory: $(DIST_DIR)"

## Build documentation with version substitution
docs-build: $(DOC_FILES)
	@echo "Building documentation with version $(VERSION)..."
	@mkdir -p $(BUILD_DIR)/docs
	@for doc in $(DOC_FILES); do \
		echo "  Processing $$doc..."; \
		sed 's/__VERSION__/$(VERSION)/g; s/v__VERSION__/v$(VERSION)/g; s/VERSION="__VERSION__"/VERSION="$(VERSION)"/g' "$$doc" > "$(BUILD_DIR)/$${doc}"; \
	done
	@echo "✅ Documentation build completed"

## Build the unified claude-mcp-init executable
build: docs-build $(BUILD_BINARY)

$(BUILD_BINARY): $(SRC_BINARY) $(LIB_FILES) VERSION
	@echo "Building $(BINARY_NAME) v$(VERSION)..."
	@mkdir -p $(BUILD_DIR)/bin $(BUILD_DIR)/lib $(BUILD_DIR)/share/doc $(BUILD_DIR)/Formula
	
	# Copy and process library files to lib directory
	@echo "Copying library files to lib..."
	@cp -r lib/*.zsh $(BUILD_DIR)/lib/
	@if [ -d "lib/mcp-modules" ]; then \
		mkdir -p $(BUILD_DIR)/lib/mcp-modules; \
		cp -r lib/mcp-modules/* $(BUILD_DIR)/lib/mcp-modules/; \
	fi
	
	# Copy Formula and documentation
	@cp -r Formula/ $(BUILD_DIR)/Formula/
	@cp README.md $(BUILD_DIR)/share/doc/ 2>/dev/null || true
	@cp MCP_SETUP_INSTRUCTIONS.md $(BUILD_DIR)/share/doc/ 2>/dev/null || true
	
	# Process main binary with version substitution (keep lib path for Homebrew compatibility)
	@cp $(SRC_BINARY) $(BUILD_BINARY)
	@sed -i.bak \
		-e 's/__VERSION__/$(VERSION)/g' \
		-e 's/__BUILD_DATE__/$(BUILD_DATE)/g' \
		-e 's/__GIT_COMMIT__/$(GIT_COMMIT)/g' \
		$(BUILD_BINARY)
	@rm $(BUILD_BINARY).bak
	
	# Process remaining files for version substitution (excluding docs handled separately)
	@echo "Applying version $(VERSION) to remaining files..."
	@find $(BUILD_DIR) -name "*.sh" -o -name "claude-mcp-init" -o -name "*.zsh" -o -name "*.rb" | \
		xargs sed -i.bak -e 's/__VERSION__/$(VERSION)/g' -e 's/$${MCP_STARTER_VERSION:-[^}]*}/$(VERSION)/g' 2>/dev/null || true
	@find $(BUILD_DIR) -name "*.bak" -delete
	
	@chmod +x $(BUILD_BINARY)
	@if [ -d "$(BUILD_DIR)/scripts" ] && [ -n "$$(ls -A $(BUILD_DIR)/scripts 2>/dev/null)" ]; then chmod +x $(BUILD_DIR)/scripts/*; fi
	@echo "✅ Build completed: $(BUILD_BINARY)"
	@echo "✅ All files processed with version $(VERSION)"

## Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(DIST_DIR)
	@echo "✅ Clean completed"

## Run tests
test: build check-zsh
	@echo "Running tests..."
	@if [ -f test/integration_test.sh ]; then \
		echo "Running integration tests with Zsh..."; \
		zsh test/integration_test.sh "$(realpath $(BUILD_BINARY))"; \
	fi
	@if [ -f test/formula_test.rb ]; then \
		echo "Running Formula tests..."; \
		ruby test/formula_test.rb "$(BUILD_DIR)/Formula/claude-mcp-init.rb" "$(realpath $(PWD)/VERSION)"; \
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
	@sudo cp -r $(BUILD_DIR)/lib $(INSTALL_PREFIX)/lib/$(BINARY_NAME)
	@sudo chmod +x $(INSTALL_PREFIX)/bin/$(BINARY_NAME)
	@echo "✅ Installation completed"
	@echo "Run: $(BINARY_NAME) --version"

## Uninstall from local system
uninstall:
	@echo "Uninstalling $(BINARY_NAME)..."
	@sudo rm -f $(INSTALL_PREFIX)/bin/$(BINARY_NAME)
	@sudo rm -rf $(INSTALL_PREFIX)/lib/$(BINARY_NAME)
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
release: check-git check-gh dist update-formula
	@echo "Creating release v$(VERSION)..."
	@git add $(FORMULA_FILE) VERSION
	@git commit -m "Release v$(VERSION)" || true
	@git tag -a "v$(VERSION)" -m "Release version $(VERSION)"
	@git push origin main
	@git push origin "v$(VERSION)"
	@gh release create "v$(VERSION)" $(TARBALL) \
		--title "Release v$(VERSION)" \
		--notes "Automated release of claude-mcp-init v$(VERSION)" \
		--latest
	@echo "✅ Release v$(VERSION) created successfully"

## Check required tools
check-tools:
	@echo "Checking required tools..."
	@command -v bash >/dev/null || (echo "❌ bash not found"; exit 1)
	@command -v zsh >/dev/null || (echo "❌ zsh not found"; exit 1)
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

## Check Zsh is available and working
check-zsh:
	@command -v zsh >/dev/null || (echo "❌ zsh not found. Install with: brew install zsh or sudo apt-get install zsh"; exit 1)
	@zsh --version >/dev/null || (echo "❌ zsh is not working properly"; exit 1)

## Format shell scripts using shfmt (if available)
format:
	@if command -v shfmt >/dev/null 2>&1; then \
		echo "Formatting shell scripts..."; \
		find bin lib -name "*.sh" -exec shfmt -w -i 4 -ci {} \; ; \
		echo "✅ Formatting completed"; \
	else \
		echo "⚠️  shfmt not found. Install with: brew install shfmt"; \
	fi

## Lint shell scripts using shellcheck (if available)
lint:
	@if command -v shellcheck >/dev/null 2>&1; then \
		echo "Linting shell scripts..."; \
		find bin lib -name "*.sh" -exec shellcheck {} \; ; \
		echo "✅ Linting completed"; \
	else \
		echo "⚠️  shellcheck not found. Install with: brew install shellcheck"; \
	fi

## Update all source files with version placeholders
update-version-placeholders:
	@echo "Updating version placeholders in source files..."
	@# Update Formula file
	@cp $(FORMULA_FILE) $(FORMULA_FILE).bak
	@sed 's/version "[^"]*"/version "__VERSION__"/g; s|archive/v[0-9]\+\.[0-9]\+\.[0-9]\+\.tar\.gz|archive/v__VERSION__.tar.gz|g' $(FORMULA_FILE).bak > $(FORMULA_FILE)
	@rm $(FORMULA_FILE).bak
	@# Update script files
	@find scripts lib -name "*.sh" -o -name "*.fish" -o -name "*.nu" -o -name "*.ps1" -o -name "*.zsh" | \
		xargs sed -i.bak 's/version: [0-9]\+\.[0-9]\+\.[0-9]\+/version: __VERSION__/g'
	@find scripts lib -name "*.bak" -delete
	@# Update documentation files
	@find docs -name "*.md" | xargs sed -i.bak 's/v[0-9]\+\.[0-9]\+\.[0-9]\+/v__VERSION__/g; s/VERSION="[^"]*"/VERSION="__VERSION__"/g'
	@find docs -name "*.bak" -delete
	@echo "✅ Version placeholders updated"

## Bump version (usage: make bump-version NEW_VERSION=1.1.0)
bump-version:
	@if [ -z "$(NEW_VERSION)" ]; then \
		echo "❌ Usage: make bump-version NEW_VERSION=1.1.0"; \
		exit 1; \
	fi
	@echo "$(NEW_VERSION)" > VERSION
	@echo "✅ Version bumped to $(NEW_VERSION)"
	@echo "Run 'make build' to apply version to all files"

## Check version consistency across all files
check-version:
	@echo "Checking version consistency..."
	@echo "Current VERSION file: $(VERSION)"
	@echo ""
	@echo "Checking source files for version consistency:"
	@if find scripts lib Formula docs -name "*.sh" -o -name "claude-mcp-init" -o -name "*.zsh" -o -name "*.md" -o -name "*.rb" 2>/dev/null | \
		xargs grep -l "[0-9]\+\.[0-9]\+\.[0-9]\+" 2>/dev/null | \
		while read file; do \
			echo "  $$file: $$(grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' "$$file" | head -1)"; \
		done | grep -v "__VERSION__" | grep -v "$(VERSION)" >/dev/null; then \
		echo "⚠️  Version inconsistencies found. Run 'make update-version-placeholders' to fix."; \
	else \
		echo "✅ All versions are consistent or use placeholders"; \
	fi

## Show current configuration
info:
	@echo "Claude MCP Init Build Configuration"
	@echo "==============================="
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
	@echo "  Libraries:    $(LIB_FILES)"
	@echo "  Formula:      $(FORMULA_FILE)"
	@echo "  Tests:        $(TEST_FILES)"

# Development helpers
.PHONY: dev-install dev-test dev-clean

## Install for development (no sudo required)
dev-install: build
	@mkdir -p ~/dev/bin ~/dev/lib
	@cp $(BUILD_BINARY) ~/dev/bin/
	@cp -r $(BUILD_DIR)/lib ~/dev/
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
	@rm -rf ~/dev/lib/
	@echo "✅ Development installation cleaned"