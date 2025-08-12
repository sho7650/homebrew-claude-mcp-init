class ClaudeMcpInit < Formula
  desc "Multi-shell MCP server configuration tool for Claude Code"
  homepage "https://github.com/yourusername/claude-mcp-init"
  url "https://github.com/yourusername/claude-mcp-init/archive/v__VERSION__.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000" # Will be updated on release
  license "MIT"
  version "__VERSION__"

  head "https://github.com/yourusername/claude-mcp-init.git", branch: "main"

  depends_on "node"
  depends_on "python@3.11"
  depends_on "uv"

  def install
    # Install the main executable
    bin.install "bin/claude-mcp-init"
    
    # Install library files
    lib.install "lib" => "claude-mcp-init"
    
    # Install documentation
    doc.install "README.md"
    doc.install "CLAUDE.md"
    
    # Create man page if it exists
    if File.exist?("man/claude-mcp-init.1")
      man1.install "man/claude-mcp-init.1"
    end
  end

  def caveats
    <<~EOS
      Claude MCP Init has been installed!
      
      Usage:
        claude-mcp-init <project_name> [language]
      
      Example:
        claude-mcp-init my-project typescript
        claude-mcp-init my-python-app python
      
      Supported languages:
        typescript, javascript, python, java, go, rust, php, elixir, clojure, c, cpp
      
      After creating a project, you'll need to:
        1. Update OPENAI_API_KEY in the .env file
        2. Follow the instructions in MCP_SETUP_INSTRUCTIONS.md
      
      Dependencies:
        - Node.js (installed via Homebrew)
        - Python 3.11 (installed via Homebrew)  
        - uv package manager (installed via Homebrew)
        - OpenAI API key (required for Cipher)
    EOS
  end

  test do
    # Test basic functionality
    system bin/"claude-mcp-init", "--version"
    system bin/"claude-mcp-init", "--help"
    
    # Test dependency detection
    assert_match "node", shell_output("which node")
    assert_match "python3", shell_output("which python3")
    assert_match "uv", shell_output("which uv")
    
    # Test project creation in temp directory
    mkdir "test-project-brew" do
      system bin/"claude-mcp-init", "test-brew-project", "typescript"
      assert_predicate Pathname.pwd/"test-brew-project", :directory?
      assert_predicate Pathname.pwd/"test-brew-project/.serena/project.yml", :file?
      assert_predicate Pathname.pwd/"test-brew-project/memAgent/cipher.yml", :file?
      assert_predicate Pathname.pwd/"test-brew-project/.env", :file?
      assert_predicate Pathname.pwd/"test-brew-project/claude-mcp-config.json", :file?
    end
  end
end