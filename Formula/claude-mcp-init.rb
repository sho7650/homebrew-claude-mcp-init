class ClaudeMcpInit < Formula
  desc "Python-based MCP server configuration tool for Claude Code with modular plugin architecture that automatically creates project structures, generates configurations, and sets up environment variables for seamless integration with Claude Code, Cursor, and other MCP clients."
  homepage "https://github.com/sho7650/homebrew-claude-mcp-init"
  url "https://github.com/sho7650/homebrew-claude-mcp-init/archive/refs/tags/v__VERSION__.tar.gz"
  sha256 "__PLACEHOLDER_SHA256__"
  license "MIT"
  version "__VERSION__"

  head "https://github.com/sho7650/homebrew-claude-mcp-init.git", branch: "main"

  depends_on "node"
  depends_on "python@3.11"
  depends_on "uv"

  # Python dependencies for the Python backend
  resource "click" do
    url "https://files.pythonhosted.org/packages/96/d3/f04c7bfcf5c1862a2a5b845c6b2b360488cf47af55dfa79c98f6a6bf98b5/click-8.1.7.tar.gz"
    sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
  end

  resource "PyYAML" do
    url "https://files.pythonhosted.org/packages/cd/e5/af35f7ea75cf72f2cd079c95ee16797de7cd71f29ea7c68ae5ce7be1eda94/PyYAML-6.0.1.tar.gz"
    sha256 "bfdf460b1736c775f2ba9f6a92bca30bc2095067b8a9d77876d1fad6cc3b4a43"
  end

  def install
    # Create a Python virtual environment
    venv = virtualenv_create(libexec, "python3.11")
    venv.pip_install resources
    
    # Install Python modules to the virtual environment
    venv.pip_install_and_link buildpath/"lib"
    
    # Install Python executable
    bin.install "bin/claude-mcp-init"
    
    # Create wrapper script that sets up Python environment
    (bin/"claude-mcp-init").write_env_script(
      bin/"claude-mcp-init",
      {
        "PYTHONPATH" => "#{libexec}/lib/python#{Language::Python.major_minor_version("python3.11")}/site-packages"
      }
    )
    
    # Install documentation
    doc.install "README.md" if File.exist?("README.md")
    doc.install "docs/API_USAGE.md" if File.exist?("docs/API_USAGE.md")
    doc.install "MCP_SETUP_INSTRUCTIONS.md" if File.exist?("MCP_SETUP_INSTRUCTIONS.md")
  end

  def caveats
    <<~EOS
      Claude MCP Init v#{version} has been installed!
      
      🐍 Python-Only Architecture:
      This version features a streamlined Python-only architecture for improved
      maintainability, security, and performance.
      
      📦 Single Executable:
        • claude-mcp-init (Pure Python executable)
      
      🚀 Key Features:
        • Modular plugin system (Serena + Cipher)
        • Git tag-based secure versioning
        • Enhanced security and code quality
        • Simplified installation and deployment
      
      ⚠️  IMPORTANT: API Keys Required
      To use MCP servers, you must provide API keys for AI providers:
        • OpenAI API key: --cipher-openai-key sk-xxx
        • Anthropic API key: --cipher-anthropic-key claude-xxx
        • Embedding providers: --cipher-embedding <provider>
      
      📖 Basic Usage:
        claude-mcp-init <project_name> [language]
      
      🔧 Modular Configuration:
        claude-mcp-init --mcp serena my-code-project typescript
        claude-mcp-init --mcp cipher --cipher-openai-key sk-xxx my-memory-project python
        claude-mcp-init --mcp serena,cipher my-full-project javascript
      
      🔑 API Key Configuration:
        claude-mcp-init --cipher-openai-key sk-xxx --cipher-embedding voyage my-project
      
      🌍 Supported Languages:
        typescript, javascript, python, java, go, rust, cpp, ruby, csharp
        Legacy fallback: php, elixir, clojure, c (auto-fallback to typescript)
      
      🔌 Embedding Providers:
        openai, azure-openai, gemini, voyage, qwen, aws-bedrock, lmstudio, ollama, disabled
      
      📋 After creating a project:
        1. Update API keys in the .env file (REQUIRED):
           - OPENAI_API_KEY=your-openai-key
           - ANTHROPIC_API_KEY=your-anthropic-key
        2. Follow setup instructions in MCP_SETUP_INSTRUCTIONS.md
        3. Configure your MCP client with the generated .mcp.json
      
      ✅ Dependencies installed via Homebrew:
        • Node.js and npm (for Serena MCP server)
        • Python 3.11+ (primary runtime)
        • uv package manager (Python packages)
        • Python virtual environment with Click and PyYAML
      
      🔧 Advanced Features:
        • API commands: claude-mcp-init api --help
        • Version validation: claude-mcp-init api version-check
        • Health monitoring: claude-mcp-init api health-check
        • Formula management: claude-mcp-init api update-formula
      
      For help: claude-mcp-init --help
    EOS
  end

  test do
    # Test basic functionality
    system bin/"claude-mcp-init", "--version"
    system bin/"claude-mcp-init", "--help"
    
    # Test API functionality (Python-only feature)
    system bin/"claude-mcp-init", "api", "--help"
    
    # Test dependency detection
    assert_match "node", shell_output("which node")
    assert_match "python3", shell_output("which python3")
    assert_match "uv", shell_output("which uv")
    
    # Test Python version requirement
    python_version = shell_output("python3 --version").strip
    assert_match "Python 3.1", python_version
    
    # Test project creation functionality
    mkdir "test-python-brew" do
      system bin/"claude-mcp-init", "test-project", "typescript"
      assert_predicate Pathname.pwd/"test-project", :directory?
      assert_predicate Pathname.pwd/"test-project/.serena/project.yml", :file?
      assert_predicate Pathname.pwd/"test-project/memAgent/cipher.yml", :file?
      assert_predicate Pathname.pwd/"test-project/.env", :file?
      assert_predicate Pathname.pwd/"test-project/.mcp.json", :file?
      assert_predicate Pathname.pwd/"test-project/MCP_SETUP_INSTRUCTIONS.md", :file?
    end
    
    # Test Python-specific functionality
    mkdir "test-python-api-brew" do
      system bin/"claude-mcp-init", "test-python-api", "python"
      assert_predicate Pathname.pwd/"test-python-api", :directory?
      assert_predicate Pathname.pwd/"test-python-api/.serena/project.yml", :file?
      assert_predicate Pathname.pwd/"test-python-api/memAgent/cipher.yml", :file?
    end
    
    # Test in-place mode
    mkdir "test-in-place-brew" do
      system bin/"claude-mcp-init", "-n", "test-in-place", "javascript"
      assert_predicate Pathname.pwd/".serena/project.yml", :file?
      assert_predicate Pathname.pwd/"memAgent/cipher.yml", :file?
      assert_predicate Pathname.pwd/".env", :file?
      assert_predicate Pathname.pwd/".mcp.json", :file?
    end
    
    # Test module selection
    mkdir "test-modules-brew" do
      system bin/"claude-mcp-init", "--mcp", "serena", "test-serena-only", "go"
      assert_predicate Pathname.pwd/"test-serena-only", :directory?
      assert_predicate Pathname.pwd/"test-serena-only/.serena/project.yml", :file?
    end
  end
end