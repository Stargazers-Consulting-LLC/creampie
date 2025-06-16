# Dependency Management Enhancement

## Overview

Improve the dependency management system to ensure better version control, security, and maintainability of the Cream API.

## Current State Analysis

### Current Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.12"
cryptograpy = "^0.0.0"
llama-cpp-python = "^0.3.9"
numpy = "^2.3.0"
pandas = "^2.3.0"
requests = "^2.32.4"
scipy = "^1.15.3"
seleniumbase = "^4.39.4"
whenever = "^0.8.5"
stargazer-utils = "^1.0.0"
fastapi = {extras = ["standard"], version = "^0.115.12"}
sqlalchemy = "^2.0.41"
pydantic-settings = "^2.9.1"
psycopg = "^3.2.9"
alembic = "^1.13.1"
aiohttp = "^3.12.13"
beautifulsoup4 = "^4.13.4"
```

## Issues Identified

1. Some dependencies have loose version constraints
2. Missing version constraints for some packages
3. Potential security vulnerabilities in outdated packages
4. Inconsistent versioning patterns
5. Missing dependency groups for different environments

## Requirements

### 1. Version Constraints

#### Strict Version Pinning

```toml
[tool.poetry.dependencies]
python = "3.12.0"
fastapi = {extras = ["standard"], version = "0.115.12"}
sqlalchemy = "2.0.41"
pydantic-settings = "2.9.1"
```

#### Version Ranges

```toml
[tool.poetry.dependencies]
requests = ">=2.32.4,<3.0.0"
aiohttp = ">=3.12.13,<4.0.0"
```

### 2. Dependency Groups

#### Development Dependencies

```toml
[tool.poetry.group.dev.dependencies]
pytest = "8.4.0"
pytest-asyncio = "1.0.0"
pytest-cov = "4.1.0"
mypy = "1.16.0"
ruff = "0.11.13"
```

#### Testing Dependencies

```toml
[tool.poetry.group.test.dependencies]
pytest = "8.4.0"
pytest-asyncio = "1.0.0"
pytest-cov = "4.1.0"
hypothesis = "6.135.9"
```

#### Documentation Dependencies

```toml
[tool.poetry.group.docs.dependencies]
mkdocs = "1.5.3"
mkdocs-material = "9.5.3"
```

### 3. Security Scanning

#### Dependencies

```toml
[tool.poetry.group.security.dependencies]
safety = "2.3.5"
bandit = "1.7.7"
```

#### Configuration

```ini
# .safety.ini
[safety]
ignore = ["51457", "51458"]  # Known false positives
```

### 4. Dependency Update Workflow

#### Update Script

```python
# scripts/update_dependencies.py
import subprocess
from typing import List

def update_dependencies() -> None:
    """Update dependencies to their latest compatible versions."""
    subprocess.run(["poetry", "update", "--no-interaction"])

def check_security() -> None:
    """Check dependencies for security vulnerabilities."""
    subprocess.run(["safety", "check"])

def run_tests() -> None:
    """Run test suite after dependency updates."""
    subprocess.run(["poetry", "run", "pytest"])
```

## Implementation Steps

1. **Audit Current Dependencies**

   - Review all current dependencies
   - Identify outdated packages
   - Check for security vulnerabilities
   - Document dependency purposes

2. **Update Version Constraints**

   - Pin critical dependencies
   - Set appropriate version ranges
   - Remove unused dependencies
   - Add missing dependencies

3. **Implement Dependency Groups**

   - Create development group
   - Create testing group
   - Create documentation group
   - Create security group

4. **Add Security Scanning**

   - Install security tools
   - Configure security checks
   - Set up CI integration
   - Create security update workflow

5. **Create Update Workflow**
   - Implement update script
   - Add security checks
   - Add test automation
   - Document update process

## Success Criteria

- All dependencies have appropriate version constraints
- Security vulnerabilities are identified and addressed
- Dependency groups are properly organized
- Update process is automated and reliable
- Documentation is complete and up-to-date

## Dependencies

- poetry
- safety
- bandit
- pytest
- mypy
- ruff

## Timeline

- Audit: 1 day
- Updates: 1-2 days
- Security: 1 day
- Documentation: 1 day
- Total: 4-5 days

## Maintenance Plan

### Regular Updates

- Weekly dependency updates
- Monthly security scans
- Quarterly major version reviews

### Update Process

1. Run dependency update script
2. Check for security vulnerabilities
3. Run test suite
4. Review changes
5. Update documentation

### Emergency Updates

- Immediate security patches
- Critical bug fixes
- Breaking changes

## Documentation

### Dependency Documentation

```markdown
# Dependencies

## Core Dependencies

- fastapi: Web framework
- sqlalchemy: Database ORM
- pydantic: Data validation

## Development Dependencies

- pytest: Testing framework
- mypy: Type checking
- ruff: Linting

## Security Dependencies

- safety: Security scanning
- bandit: Security linting
```

### Update Documentation

```markdown
# Dependency Updates

## Regular Updates

1. Run `poetry update`
2. Check security with `safety check`
3. Run tests with `pytest`
4. Review changes
5. Update documentation

## Emergency Updates

1. Identify affected packages
2. Update specific packages
3. Run security checks
4. Deploy fixes
```
