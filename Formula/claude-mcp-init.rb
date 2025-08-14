class ClaudeMcpInit < Formula
  desc "Claude MCP Init v0.10.4 features a **modular plugin architecture** that allows you to selectively configure MCP servers based on your specific needs. The tool automatically creates project structures, generates configurations, and sets up environment variables for seamless integration with Claude Code, Cursor, and other MCP clients."
  homepage "https://github.com/sho7650/homebrew-claude-mcp-init"
  url "https://github.com/sho7650/homebrew-claude-mcp-init/archive/refs/tags/v0.10.4.tar.gz"
  sha256 "fa76da81da39b91a2e27de13bbe11dc28b3d0e5de133f972ad38c87fc1902577"
  license "MIT"
  version "0.10.4"

  head "https://github.com/sho7650/homebrew-claude-mcp-init.git", branch: "main"

  depends_on "node"
  depends_on "python@3.11"
  depends_on "uv"

  def install
    # Process version substitution in the main executable
    inreplace "bin/claude-mcp-init", "__VERSION__", version.to_s
    
    # Install the processed executable
    bin.install "bin/claude-mcp-init"
    
    # Install library files to lib directory (Homebrew standard for runtime libraries)  
    lib.install Dir["lib/*"]
    
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
      Claude MCP Init v0.10.4 has been installed!
      
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
        ✅ Python 3.11+ (for Cipher MCP server)  
        ✅ uv package manager (Python packages)
      
      For help: claude-mcp-init --help
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
      assert_predicate Pathname.pwd/"test-brew-project/.mcp.json", :file?
      assert_predicate Pathname.pwd/"test-brew-project/MCP_SETUP_INSTRUCTIONS.md", :file?
    end
  end
end
