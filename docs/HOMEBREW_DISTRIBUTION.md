# Homebrew Distribution Guide

Complete guide for distributing MCP Starter through Homebrew.

## Overview

This document outlines the complete process for:
- Setting up Homebrew distribution
- Creating and maintaining a Homebrew tap
- Releasing new versions
- Managing the Formula

## Prerequisites

1. **GitHub Repository** - Public repository with the MCP Starter code
2. **GitHub CLI** - `brew install gh` and authenticate with `gh auth login`
3. **Homebrew** - Installed and working on your system
4. **OpenAI API Key** - For testing Cipher functionality

## Initial Setup

### 1. Create the Homebrew Tap Repository

```bash
# Create a new repository for your tap
gh repo create homebrew-mcp-starter --public --description "Homebrew tap for MCP Starter"

# Clone the tap repository
git clone https://github.com/yourusername/homebrew-mcp-starter.git
cd homebrew-mcp-starter

# Create the Formula directory
mkdir Formula
```

### 2. Prepare the Main Repository

```bash
# In your mcp-starter repository
git add .
git commit -m "Add Homebrew distribution support"
git push origin main

# Create initial release
git tag v__VERSION__
git push origin v__VERSION__
```

### 3. Build and Test the Package

```bash
# Build the distribution
make build
make test
make dist

# Test the unified binary
./build/bin/mcp-starter --version
./build/bin/mcp-starter test-project typescript
```

## Creating the Formula

### 1. Copy the Formula to Your Tap

```bash
# Copy the Formula file to your tap repository
cp Formula/mcp-starter.rb ../homebrew-mcp-starter/Formula/

cd ../homebrew-mcp-starter
```

### 2. Update Formula URLs

Edit `Formula/mcp-starter.rb` and update:
- Replace `yourusername` with your actual GitHub username
- Update the repository URL
- Ensure the version matches your release

```ruby
class McpStarter < Formula
  desc "Multi-shell MCP server configuration tool for Claude Code"
  homepage "https://github.com/YOURUSERNAME/mcp-starter"
  url "https://github.com/YOURUSERNAME/mcp-starter/archive/v__VERSION__.tar.gz"
  # ... rest of the formula
end
```

### 3. Calculate SHA256

```bash
# Download your release tarball and calculate SHA256
curl -LO https://github.com/YOURUSERNAME/mcp-starter/archive/v__VERSION__.tar.gz
sha256sum v__VERSION__.tar.gz  # On Linux
# or
shasum -a 256 v__VERSION__.tar.gz  # On macOS

# Update the SHA256 in the Formula
sed -i 's/sha256 ".*"/sha256 "YOUR_CALCULATED_SHA256"/' Formula/mcp-starter.rb
```

### 4. Commit and Push the Formula

```bash
git add Formula/mcp-starter.rb
git commit -m "Add mcp-starter formula v__VERSION__"
git push origin main
```

## Testing the Homebrew Installation

### 1. Install from Your Tap

```bash
# Add your tap
brew tap yourusername/mcp-starter

# Install the formula
brew install mcp-starter

# Test the installation
mcp-starter --version
mcp-starter --help
```

### 2. Test Full Functionality

```bash
# Create a test project
cd /tmp
mcp-starter test-homebrew-project typescript

# Verify project structure
ls -la test-homebrew-project/
cat test-homebrew-project/.serena/project.yml
cat test-homebrew-project/memAgent/cipher.yml

# Cleanup
rm -rf test-homebrew-project
```

### 3. Test Uninstallation

```bash
# Uninstall the package
brew uninstall mcp-starter

# Remove the tap
brew untap yourusername/mcp-starter
```

## Release Process

### 1. Automated Release (Recommended)

Using the provided GitHub Actions workflow:

```bash
# Update version
make bump-version NEW_VERSION=1.1.0

# Commit and push
git add VERSION Formula/mcp-starter.rb
git commit -m "Bump version to 1.1.0"
git push origin main

# Create release (triggers GitHub Action)
git tag v1.1.0
git push origin v1.1.0
```

The GitHub Action will:
- Run tests
- Build distribution
- Update Formula SHA256
- Create GitHub release
- Update tap repository

### 2. Manual Release Process

If you prefer manual control:

```bash
# 1. Update version and build
make bump-version NEW_VERSION=1.1.0
make clean build test dist

# 2. Create GitHub release
gh release create v1.1.0 dist/mcp-starter-1.1.0.tar.gz \
  --title "Release v1.1.0" \
  --notes "Release notes here"

# 3. Update Formula in tap repository
cd ../homebrew-mcp-starter
make update-formula  # This updates SHA256
git add Formula/mcp-starter.rb
git commit -m "Update mcp-starter to v1.1.0"
git push origin main
```

## Maintenance Tasks

### 1. Dependency Updates

When updating dependencies in the Formula:

```ruby
# In Formula/mcp-starter.rb
depends_on "node"
depends_on "python@3.12"  # Updated version
depends_on "uv"

# Add new dependencies if needed
depends_on "git"
```

### 2. Testing New Versions

```bash
# Test locally before releasing
brew uninstall mcp-starter
brew install mcp-starter --verbose --debug

# Test with different configurations
mcp-starter test-project python
mcp-starter test-project rust
```

### 3. Handling Issues

Common issues and solutions:

**SHA256 Mismatch:**
```bash
# Recalculate and update
sha256sum dist/mcp-starter-X.X.X.tar.gz
# Update Formula with new hash
```

**Dependency Issues:**
```bash
# Test dependencies locally
brew deps mcp-starter
brew install --only-dependencies mcp-starter
```

**Formula Syntax Errors:**
```bash
# Validate Formula
brew audit mcp-starter
brew style mcp-starter
```

## Monitoring and Analytics

### 1. Usage Statistics

Monitor your package popularity:

```bash
# Check download statistics
brew info mcp-starter
```

### 2. Issue Tracking

Monitor issues in both repositories:
- Main repository: Feature requests, bugs
- Tap repository: Installation issues, Formula problems

### 3. User Feedback

Encourage users to report issues and provide feedback:
- GitHub Issues
- Community discussions
- Version-specific feedback

## Advanced Topics

### 1. Multiple Formula Variants

For different installation options:

```ruby
# Create additional formulas
class McpStarterDev < Formula
  desc "MCP Starter development version"
  # ... development-specific configuration
end
```

### 2. Custom Installation Options

```ruby
# Add options to the Formula
option "with-docs", "Install documentation"
option "without-examples", "Skip example files"

def install
  if build.with? "docs"
    doc.install "docs"
  end
  # ...
end
```

### 3. Post-Install Messages

```ruby
def caveats
  <<~EOS
    MCP Starter requires additional setup:
    
    1. Set your OpenAI API key:
       export OPENAI_API_KEY="your-key-here"
    
    2. Install required MCP servers:
       npm install -g @byterover/cipher
    
    3. Get started:
       mcp-starter my-project typescript
  EOS
end
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check GitHub Actions logs
   - Verify all dependencies are available
   - Test build locally

2. **Installation Issues**
   - Verify Formula syntax with `brew audit`
   - Check dependency availability
   - Test on clean system

3. **Runtime Issues**
   - Verify all required tools are in PATH
   - Check file permissions
   - Test with different shell environments

### Getting Help

- Homebrew Documentation: https://docs.brew.sh/Formula-Cookbook
- GitHub Actions Documentation: https://docs.github.com/en/actions
- Community Support: Homebrew Discourse

## Best Practices

1. **Version Management**
   - Use semantic versioning
   - Tag releases properly
   - Maintain changelog

2. **Testing**
   - Test on multiple platforms
   - Test with different shell environments
   - Automate testing in CI

3. **Documentation**
   - Keep Formula comments up to date
   - Document breaking changes
   - Provide migration guides

4. **Community**
   - Respond to issues promptly
   - Welcome contributions
   - Follow Homebrew guidelines

## Conclusion

Following this guide will ensure your MCP Starter package is properly distributed through Homebrew and maintained according to community standards. Regular updates, thorough testing, and responsive maintenance will help build a strong user base and contribute to the ecosystem.