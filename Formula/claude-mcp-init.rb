class ClaudeMcpInit < Formula
  desc "Claude MCP Init v0.11.2 features a **modular plugin architecture** with dual Zsh/Python backends that allows you to selectively configure MCP servers based on your specific needs. The tool automatically creates project structures, generates configurations, and sets up environment variables for seamless integration with Claude Code, Cursor, and other MCP clients."
  homepage "https://github.com/sho7650/homebrew-claude-mcp-init"
  url "https://github.com/sho7650/homebrew-claude-mcp-init/archive/refs/tags/v0.11.2.tar.gz"
  sha256 "__PLACEHOLDER_SHA256__"
  license "MIT"
  version "0.11.2"

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
    # Create a Python virtual environment for the Python backend
    venv = virtualenv_create(libexec, "python3.11")
    venv.pip_install resources
    
    # Process version substitution in both executables
    inreplace "bin/claude-mcp-init", "__VERSION__", version.to_s
    inreplace "bin/claude-mcp-init-python", "__VERSION__", version.to_s
    
    # Install both Zsh and Python wrapper executables
    bin.install "bin/claude-mcp-init"
    bin.install "bin/claude-mcp-init-python"
    
    # Install library files to lib directory (Homebrew standard for runtime libraries)
    lib.install Dir["lib/*"]
    
    # Install Python modules to the virtual environment site-packages
    venv.pip_install_and_link buildpath
    
    # Create symlink for Python backend access
    (bin/"claude-mcp-init-python").write_env_script(
      libexec/"bin/claude-mcp-init-python",
      {
        "PYTHONPATH" => "#{lib}:#{libexec}/lib/python#{Language::Python.major_minor_version("python3.11")}/site-packages"
      }
    )
    
    # Install documentation
    doc.install "README.md" if File.exist?("README.md")
    doc.install "MCP_SETUP_INSTRUCTIONS.md" if File.exist?("MCP_SETUP_INSTRUCTIONS.md")
    
    # Create man page if it exists
    if File.exist?("man/claude-mcp-init.1")
      man1.install "man/claude-mcp-init.1"
    end
  end

  def caveats
    <<~EOS
      Claude MCP Init v0.11.2 has been installed!
      
      🔧 Dual Backend Support:
      This version includes both Zsh and Python backends for enhanced functionality:
        • claude-mcp-init        (Zsh backend - default, stable)
        • claude-mcp-init-python (Python backend - advanced features)
      
      Both backends provide the same MCP server configuration functionality.
      The Python backend offers enhanced plugin architecture and validation.
      
      ⚠️  IMPORTANT: API Keys Required
      To use MCP servers, you must provide API keys for AI providers:
        • OpenAI API key (for most features): --openai-key sk-xxx
        • Anthropic API key (for Claude models): --anthropic-key claude-xxx
        • Additional embedding providers: --cipher-embedding <provider> --cipher-embedding-key <key>
      
      Basic Usage:
        claude-mcp-init <project_name> [language]
      
      Modular Configuration:
        claude-mcp-init --mcp serena my-code-project typescript
        claude-mcp-init --mcp cipher --openai-key sk-xxx my-memory-project python
        claude-mcp-init --mcp serena,cipher my-full-project javascript
      
      API Key Configuration:
        claude-mcp-init --openai-key sk-xxx --cipher-embedding voyage --cipher-embedding-key vo-xxx my-project
      
      Supported Languages:
        typescript, javascript, python, java, go, rust, cpp, ruby, csharp
        Legacy fallback: php, elixir, clojure, c
      
      Embedding Providers:
        openai, azure-openai, gemini, voyage, qwen, aws-bedrock, lmstudio, ollama, disabled
      
      After creating a project:
        1. Update API keys in the .env file (REQUIRED):
           - OPENAI_API_KEY=your-openai-key
           - ANTHROPIC_API_KEY=your-anthropic-key
        2. Follow setup instructions in MCP_SETUP_INSTRUCTIONS.md
        3. Configure your MCP client with the generated .mcp.json
      
      Dependencies installed via Homebrew:
        ✅ Node.js and npm (for Serena MCP server)
        ✅ Python 3.11+ (for Cipher MCP server and Python backend)
        ✅ uv package manager (Python packages)
        ✅ Python virtual environment with Click and PyYAML (for Python backend)
      
      For help: claude-mcp-init --help
    EOS
  end

  test do
    # Test Zsh backend functionality
    system bin/"claude-mcp-init", "--version"
    system bin/"claude-mcp-init", "--help"
    
    # Test Python backend functionality  
    system bin/"claude-mcp-init-python", "--version"
    system bin/"claude-mcp-init-python", "--help"
    
    # Test dependency detection
    assert_match "node", shell_output("which node")
    assert_match "python3", shell_output("which python3")
    assert_match "uv", shell_output("which uv")
    
    # Test Zsh backend project creation
    mkdir "test-zsh-brew" do
      system bin/"claude-mcp-init", "test-zsh-project", "typescript"
      assert_predicate Pathname.pwd/"test-zsh-project", :directory?
      assert_predicate Pathname.pwd/"test-zsh-project/.serena/project.yml", :file?
      assert_predicate Pathname.pwd/"test-zsh-project/memAgent/cipher.yml", :file?
      assert_predicate Pathname.pwd/"test-zsh-project/.env", :file?
      assert_predicate Pathname.pwd/"test-zsh-project/.mcp.json", :file?
      assert_predicate Pathname.pwd/"test-zsh-project/MCP_SETUP_INSTRUCTIONS.md", :file?
    end
    
    # Test Python backend project creation
    mkdir "test-python-brew" do
      system bin/"claude-mcp-init-python", "test-python-project", "python"
      assert_predicate Pathname.pwd/"test-python-project", :directory?
      assert_predicate Pathname.pwd/"test-python-project/.serena/project.yml", :file?
      assert_predicate Pathname.pwd/"test-python-project/memAgent/cipher.yml", :file?
      assert_predicate Pathname.pwd/"test-python-project/.env", :file?
      assert_predicate Pathname.pwd/"test-python-project/.mcp.json", :file?
      assert_predicate Pathname.pwd/"test-python-project/MCP_SETUP_INSTRUCTIONS.md", :file?
    end
  end
end
