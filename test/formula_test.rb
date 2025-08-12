#!/usr/bin/env ruby

# Formula Tests for MCP Starter Homebrew Formula
# Tests that the Homebrew Formula is correctly structured

require 'yaml'
require 'json'

class FormulaTest
  RED = "\033[0;31m"
  GREEN = "\033[0;32m"
  YELLOW = "\033[1;33m"
  BLUE = "\033[0;34m"
  NC = "\033[0m"

  def initialize(formula_path = nil, version_path = nil)
    @tests_run = 0
    @tests_passed = 0
    @tests_failed = 0
    @formula_path = formula_path || File.join(File.dirname(__FILE__), '..', 'Formula', 'claude-mcp-init.rb')
    @version_path = version_path || File.join(File.dirname(__FILE__), '..', 'VERSION')
  end

  def log_info(message)
    puts "#{BLUE}#{message}#{NC}"
  end

  def log_success(message)
    puts "#{GREEN}✅ #{message}#{NC}"
  end

  def log_error(message)
    puts "#{RED}❌ #{message}#{NC}"
  end

  def log_warning(message)
    puts "#{YELLOW}⚠️  #{message}#{NC}"
  end

  def assert(condition, description)
    @tests_run += 1
    
    if condition
      log_success("PASS: #{description}")
      @tests_passed += 1
      true
    else
      log_error("FAIL: #{description}")
      @tests_failed += 1
      false
    end
  end

  def test_formula_file_exists
    log_info("Testing Formula file existence...")
    assert(File.exist?(@formula_path), "Formula file should exist at #{@formula_path}")
  end

  def test_version_file_exists
    log_info("Testing VERSION file existence...")
    assert(File.exist?(@version_path), "VERSION file should exist at #{@version_path}")
  end

  def test_formula_syntax
    log_info("Testing Formula syntax...")
    
    begin
      # Try to load the Ruby file
      formula_content = File.read(@formula_path)
      
      # Basic syntax check
      assert(formula_content.include?('class ClaudeMcpInit < Formula'), "Formula should define ClaudeMcpInit class")
      assert(formula_content.include?('desc'), "Formula should have description")
      assert(formula_content.include?('homepage'), "Formula should have homepage")
      assert(formula_content.include?('url'), "Formula should have source URL")
      assert(formula_content.include?('sha256'), "Formula should have SHA256")
      assert(formula_content.include?('license'), "Formula should have license")
      assert(formula_content.include?('def install'), "Formula should have install method")
      assert(formula_content.match(/\s*test\s+do/), "Formula should have test method")
    rescue => e
      assert(false, "Formula should be valid Ruby: #{e.message}")
    end
  end

  def test_dependencies
    log_info("Testing Formula dependencies...")
    
    formula_content = File.read(@formula_path)
    
    # Check required dependencies
    assert(formula_content.include?('depends_on "node"'), "Formula should depend on node")
    assert(formula_content.include?('depends_on "python@3.11"'), "Formula should depend on python@3.11")  
    assert(formula_content.include?('depends_on "uv"'), "Formula should depend on uv")
  end

  def test_install_method
    log_info("Testing Formula install method...")
    
    formula_content = File.read(@formula_path)
    
    # Check install operations
    assert(formula_content.include?('bin.install'), "Formula should install binary")
    assert(formula_content.include?('lib.install'), "Formula should install libraries")
    assert(formula_content.include?('doc.install'), "Formula should install documentation")
  end

  def test_test_method
    log_info("Testing Formula test method...")
    
    formula_content = File.read(@formula_path)
    
    # Check test operations
    assert(formula_content.include?('system bin/"claude-mcp-init", "--version"'), "Formula should test version")
    assert(formula_content.include?('system bin/"claude-mcp-init", "--help"'), "Formula should test help")
    assert(formula_content.include?('assert_predicate'), "Formula should have file existence tests")
  end

  def test_version_consistency
    log_info("Testing version consistency...")
    
    if File.exist?(@version_path)
      version = File.read(@version_path).strip
      formula_content = File.read(@formula_path)
      
      assert(formula_content.include?("version \"#{version}\""), "Formula version should match VERSION file")
      assert(formula_content.include?("v#{version}.tar.gz"), "Formula URL should include correct version")
    else
      log_warning("VERSION file not found, skipping version consistency test")
    end
  end

  def test_required_files_referenced
    log_info("Testing required files are referenced...")
    
    formula_content = File.read(@formula_path)
    
    # Check that Formula references the correct files for installation
    assert(formula_content.include?('bin/claude-mcp-init'), "Formula should reference main binary")
    assert(formula_content.include?('lib'), "Formula should reference library directory")
    assert(formula_content.include?('README.md'), "Formula should reference README")
  end

  def test_caveats_section
    log_info("Testing caveats section...")
    
    formula_content = File.read(@formula_path)
    
    if formula_content.include?('def caveats')
      assert(formula_content.include?('Usage:'), "Caveats should include usage information")
      assert(formula_content.include?('OPENAI_API_KEY'), "Caveats should mention API key requirement")
    else
      log_warning("No caveats section found - consider adding user guidance")
    end
  end

  def test_license_specified
    log_info("Testing license specification...")
    
    formula_content = File.read(@formula_path)
    
    # Check that a license is specified
    assert(formula_content.match(/license\s+"[^"]+"/), "Formula should specify a license")
  end

  def test_homepage_url_format
    log_info("Testing homepage URL format...")
    
    formula_content = File.read(@formula_path)
    
    # Extract homepage URL
    if match = formula_content.match(/homepage\s+"([^"]+)"/)
      homepage = match[1]
      assert(homepage.start_with?('http'), "Homepage should be a valid HTTP(S) URL")
      assert(homepage.include?('github.com'), "Homepage should point to GitHub repository")
    else
      assert(false, "Homepage URL should be specified")
    end
  end

  def run_all_tests
    log_info("Starting MCP Starter Formula Tests")
    log_info("==================================")
    
    test_formula_file_exists
    test_version_file_exists
    
    if File.exist?(@formula_path)
      test_formula_syntax
      test_dependencies
      test_install_method
      test_test_method
      test_version_consistency
      test_required_files_referenced
      test_caveats_section
      test_license_specified
      test_homepage_url_format
    end
    
    # Summary
    puts
    log_info("Test Summary")
    log_info("============")
    log_info("Tests run: #{@tests_run}")
    log_success("Passed: #{@tests_passed}")
    
    if @tests_failed > 0
      log_error("Failed: #{@tests_failed}")
      log_error("Formula tests FAILED")
      false
    else
      log_success("All tests PASSED!")
      true
    end
  end
end

# Run tests if executed directly
if __FILE__ == $0
  # Accept command line arguments for custom paths
  formula_path = ARGV[0]
  version_path = ARGV[1]
  
  test = FormulaTest.new(formula_path, version_path)
  success = test.run_all_tests
  exit(success ? 0 : 1)
end