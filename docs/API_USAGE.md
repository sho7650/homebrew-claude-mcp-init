# Claude MCP Init API Documentation

## Overview

The Claude MCP Init API provides programmatic access to MCP (Model Context Protocol) configuration management, system health monitoring, and release automation.

## API Components

### 1. VersionValidator
Ensures version consistency across all project components.

```python
from claude_mcp_init.api import VersionValidator

validator = VersionValidator()

# Check version consistency
status = validator.check_version_consistency()
print(f"Consistent: {status['consistent']}")
print(f"Current version: {status['current_version']}")

# Validate release readiness
ready, issues = validator.validate_release_readiness()
if not ready:
    for issue in issues:
        print(f"Issue: {issue}")

# Suggest next version
next_version = validator.suggest_next_version("minor")  # major, minor, patch
print(f"Suggested version: {next_version}")
```

### 2. HealthChecker
Comprehensive system health monitoring.

```python
from claude_mcp_init.api import HealthChecker

checker = HealthChecker()

# Comprehensive health check
health = checker.check_system_health()
print(f"Status: {health['status']}")

# Diagnose issues
issues = checker.diagnose_issues()
for issue in issues:
    print(f"{issue['severity']}: {issue['issue']}")
    print(f"Solution: {issue['solution']}")

# Generate report
report = checker.generate_report()  # Markdown format
print(report)
```

### 3. FormulaUpdater
Homebrew Formula management and automation.

```python
from claude_mcp_init.api import FormulaUpdater

updater = FormulaUpdater()

# Update Formula version
success = updater.update_formula_version("0.12.0", "sha256_checksum")

# Validate Formula
valid, issues = updater.validate_formula()
if not valid:
    for issue in issues:
        print(f"Formula issue: {issue}")

# Complete release update
result = updater.update_formula_for_release("0.12.0")
print(f"Release ready: {result['validation_passed']}")
```

### 4. Unified API Gateway
Single entry point for all API functionality.

```python
from claude_mcp_init.api import MCPInitAPI

api = MCPInitAPI()

# Get comprehensive status
status = api.get_status()
print(f"Overall status: {status['status']}")

# Validate entire system
validation = api.validate_system()
if validation['valid']:
    print("System is ready!")
else:
    print("Issues found:")
    for issue in validation['issues']:
        print(f"  - {issue}")

# Prepare for release
result = api.prepare_release("0.12.0")
if result['ready']:
    print("Release preparation complete!")
    print(result['release_notes'])
```

## Convenience Functions

For quick access without creating API instances:

```python
from claude_mcp_init.api import get_system_status, validate_system, get_version_info

# Quick status check
status = get_system_status()
print(f"Status: {status['status']}")

# Quick validation
validation = validate_system()
print(f"Valid: {validation['valid']}")

# Quick version info
version_info = get_version_info()
print(f"Consistent: {version_info['consistent']}")
```

## CLI Integration

All API functionality is available via command line:

### System Status
```bash
claude-mcp-init api status                    # Pretty format
claude-mcp-init api status --format json      # JSON format
```

### System Validation
```bash
claude-mcp-init api validate                  # Pretty format
claude-mcp-init api validate --format json    # JSON format
```

### Health Report
```bash
claude-mcp-init api health                    # Markdown report
claude-mcp-init api health --format json      # JSON format
```

### Diagnostic Analysis
```bash
claude-mcp-init api diagnose                  # Pretty format with solutions
claude-mcp-init api diagnose --format json    # JSON format
```

### Version Information
```bash
claude-mcp-init api version-info              # Detailed version status
```

### Release Preparation
```bash
claude-mcp-init api prepare-release 0.12.0    # Prepare for release
claude-mcp-init api prepare-release 0.12.0 --dry-run  # Dry run
```

## API Response Formats

### Status Response
```json
{
  "api_version": "0.2.0",
  "status": "healthy|warning|unhealthy",
  "timestamp": "2025-08-15T17:53:22.687422",
  "components": {
    "version_validator": {
      "status": "healthy|warning|unhealthy",
      "current_version": "0.11.5",
      "consistent": true
    },
    "health_check": {
      "status": "healthy|warning|unhealthy",
      "summary": "All systems operational"
    },
    "formula_updater": {
      "status": "healthy|warning|unhealthy",
      "formula_version": "0.11.5",
      "valid": true
    }
  }
}
```

### Validation Response
```json
{
  "valid": true,
  "timestamp": "2025-08-15T17:53:22.687422",
  "checks_performed": ["version_consistency", "release_readiness", "system_health"],
  "issues": []
}
```

### Health Check Response
```json
{
  "status": "healthy|degraded|unhealthy",
  "checks": {
    "dependencies": {"status": "healthy", "required": {...}, "optional": {...}},
    "plugins": {"status": "healthy", "available_plugins": {...}},
    "configuration": {"status": "healthy", "files": {...}},
    "permissions": {"status": "healthy", "directories": {...}},
    "disk_space": {"status": "healthy", "free_gb": 371.61}
  },
  "timestamp": "2025-08-15T17:53:17.298017",
  "summary": "All systems operational"
}
```

### Diagnostic Response
```json
{
  "system_issues": [
    {
      "issue": "Missing required dependency: git",
      "severity": "critical",
      "description": "Version control system",
      "solution": "brew install git (macOS) or apt-get install git (Linux)"
    }
  ],
  "version_issues": [
    {
      "issue": "Version inconsistency: formula version mismatch",
      "severity": "warning",
      "solution": "Run 'make update-version-python' to synchronize versions"
    }
  ],
  "total_issues": 2,
  "critical_count": 1,
  "warning_count": 1
}
```

## Error Handling

The API uses Python exceptions for error handling:

```python
from claude_mcp_init.api import MCPInitAPI

try:
    api = MCPInitAPI()
    status = api.get_status()
except FileNotFoundError as e:
    print(f"Configuration file not found: {e}")
except RuntimeError as e:
    print(f"Runtime error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Check system health regularly**
   ```python
   health = api.health.check_system_health()
   if health['status'] != 'healthy':
       issues = api.diagnose_and_fix()
       # Handle issues
   ```

2. **Validate before release**
   ```python
   validation = api.validate_system()
   if validation['valid']:
       # Proceed with release
       result = api.prepare_release(version)
   ```

3. **Monitor version consistency**
   ```python
   version_check = api.version.check_version_consistency()
   if not version_check['consistent']:
       # Fix version discrepancies
   ```

4. **Use appropriate output formats**
   - Use `pretty` format for human-readable output
   - Use `json` format for programmatic processing
   - Use `markdown` format for documentation

## Integration Examples

### CI/CD Pipeline
```yaml
# .github/workflows/release.yml
- name: Validate system
  run: |
    claude-mcp-init api validate --format json > validation.json
    if [ "$(jq '.valid' validation.json)" = "false" ]; then
      echo "System validation failed"
      exit 1
    fi

- name: Prepare release
  run: |
    claude-mcp-init api prepare-release ${{ github.ref_name }} --format json
```

### Monitoring Script
```python
#!/usr/bin/env python3
import json
from claude_mcp_init.api import get_system_status

status = get_system_status()
if status['status'] != 'healthy':
    # Send alert
    print(f"ALERT: System unhealthy - {status['summary']}")
    exit(1)
```

### Development Workflow
```bash
# Check system before development
claude-mcp-init api diagnose

# Validate before committing
claude-mcp-init api validate

# Check version consistency
claude-mcp-init api version-info

# Prepare for release
claude-mcp-init api prepare-release 0.12.0 --dry-run
```

## API Versioning

The API follows semantic versioning:
- **Major version**: Breaking changes to API interface
- **Minor version**: New features, backward compatible
- **Patch version**: Bug fixes, backward compatible

Current API version: **0.2.0**

## Support

For API support and examples, refer to:
- Main project documentation
- Test files in `test/python/unit/` directory
- Integration examples in `test/python/integration/` directory

## Security Considerations

- API keys are handled securely through the credential manager
- File permissions are validated before operations
- Input validation is performed on all parameters
- No sensitive information is logged or exposed in API responses