# Development Workflow

> **For AI Assistants**: This guide outlines the development workflow, including Git practices, testing procedures, and deployment processes. All patterns include validation rules and implementation guidance for consistent development practices.

## AI Metadata

**Template Version:** 2.0
**AI Processing Level:** High
**Required Context:** Git, CI/CD, testing, deployment, project management
**Validation Required:** Yes
**Code Generation:** Supported

**Dependencies:**
- `../guide_docs/Core%20Principles.md` - Decision-making frameworks
- `../guide_docs/Language-Specific/Python%20Testing%20Guide.md` - Testing patterns
- `../guide_docs/Domain-Specific/Database%20Management%20Guide.md` - Database patterns
- `Architecture%20Overview.md` - System architecture
- `Common%20Patterns.md` - Project-specific patterns

**Validation Rules:**
- All code changes must follow Git workflow and branching strategy
- All commits must include proper commit messages and validation
- All changes must pass automated testing before deployment
- All deployments must follow proper environment promotion
- All documentation must be updated with code changes

## Overview

**Document Purpose:** Development workflow standards and procedures for the CreamPie project
**Scope:** Git workflow, testing, CI/CD, deployment, and project management
**Target Users:** AI assistants and developers working on the project
**Last Updated:** Current

**AI Context:** This guide provides the foundational development workflow that must be followed for all code changes and deployments in the project. It ensures consistent, reliable, and maintainable development practices.

## 1. Git Workflow

### Branching Strategy
```bash
# Main branches
main                    # Production-ready code
develop                 # Integration branch for features
staging                 # Pre-production testing

# Feature branches
feature/feature-name    # New features
bugfix/bug-description  # Bug fixes
hotfix/critical-fix     # Critical production fixes
release/version-number  # Release preparation
```

**Code Generation Hint**: This branching strategy will inform all Git branch naming and organization.

**Validation**: All branches must follow this naming convention and purpose.

### Commit Message Standards
```bash
# Commit message format
<type>(<scope>): <description>

[optional body]

[optional footer]

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation changes
style:    Code style changes (formatting, etc.)
refactor: Code refactoring
test:     Adding or updating tests
chore:    Maintenance tasks

# Examples
feat(auth): add JWT authentication system
fix(api): resolve rate limiting issue in stock data endpoint
docs(readme): update installation instructions
test(stock-data): add unit tests for data processor
refactor(ui): extract reusable button component
chore(deps): update dependencies to latest versions
```

**Code Generation Hint**: This commit message format will inform all Git commit message creation.

**Validation**: All commits must follow this format with proper type and description.

### Git Workflow Commands
```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/new-feature-name

# Make changes and commit
git add .
git commit -m "feat(scope): descriptive commit message"

# Push feature branch
git push origin feature/new-feature-name

# Create pull request
# - Target: develop
# - Include description of changes
# - Request code review

# After approval, merge to develop
git checkout develop
git pull origin develop
git merge feature/new-feature-name
git push origin develop

# Clean up feature branch
git branch -d feature/new-feature-name
git push origin --delete feature/new-feature-name
```

**Code Generation Hint**: This Git workflow will inform all version control operations.

**Validation**: All Git operations must follow this workflow sequence.

## 2. Code Review Process

### Pull Request Standards
```markdown
# Pull Request Template

## Description
Brief description of changes made

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] No new warnings

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console errors
- [ ] Performance impact considered

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #issue-number
```

**Code Generation Hint**: This PR template will inform all pull request creation and review.

**Validation**: All pull requests must include proper description and checklist completion.

### Code Review Guidelines
```markdown
# Code Review Checklist

## Functionality
- [ ] Code works as intended
- [ ] Edge cases handled
- [ ] Error handling implemented
- [ ] Performance considerations

## Code Quality
- [ ] Follows style guidelines
- [ ] No code duplication
- [ ] Proper naming conventions
- [ ] Comments where needed

## Security
- [ ] No security vulnerabilities
- [ ] Input validation implemented
- [ ] Sensitive data protected
- [ ] Authentication/authorization correct

## Testing
- [ ] Tests cover new functionality
- [ ] Tests pass consistently
- [ ] Test coverage adequate
- [ ] Integration tests updated

## Documentation
- [ ] Code is self-documenting
- [ ] README updated if needed
- [ ] API documentation updated
- [ ] Comments explain complex logic
```

**Code Generation Hint**: This review checklist will inform all code review processes.

**Validation**: All code reviews must follow this checklist for comprehensive evaluation.

## 3. Testing Workflow

### Test Execution
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_specific_module.py

# Run tests with coverage
poetry run pytest --cov=cream_api --cov-report=html

# Run tests in parallel
poetry run pytest -n auto

# Run tests with verbose output
poetry run pytest -v

# Run only unit tests
poetry run pytest tests/unit/

# Run only integration tests
poetry run pytest tests/integration/

# Run tests matching pattern
poetry run pytest -k "test_function_name"
```

**Code Generation Hint**: This test execution pattern will inform all testing procedures.

**Validation**: All code changes must pass all relevant tests before merging.

### Test Coverage Requirements
```yaml
# Coverage thresholds
coverage:
  global:
    statements: 80
    branches: 75
    functions: 80
    lines: 80

  modules:
    cream_api:
      statements: 85
      branches: 80
      functions: 85
      lines: 85

    cream_ui:
      statements: 80
      branches: 75
      functions: 80
      lines: 80
```

**Code Generation Hint**: This coverage configuration will inform all test coverage requirements.

**Validation**: All modules must meet minimum coverage thresholds.

### Test Data Management
```python
# Test data patterns
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def sample_stock_data():
    """Provide sample stock data for testing"""
    return {
        "symbol": "AAPL",
        "price": 150.00,
        "change": 2.50,
        "volume": 1000000,
        "date": "2024-01-01"
    }

@pytest.fixture
def mock_api_response():
    """Mock API response for testing"""
    return {
        "success": True,
        "data": {
            "symbol": "AAPL",
            "price": 150.00
        }
    }

@pytest.fixture
def test_database():
    """Provide test database connection"""
    # Setup test database
    db = create_test_database()
    yield db
    # Cleanup
    db.close()
```

**Code Generation Hint**: This test data pattern will inform all test fixture implementation.

**Validation**: All tests must use proper fixtures and mock data.

## 4. CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install

    - name: Run linting
      run: |
        poetry run flake8 cream_api
        poetry run black --check cream_api

    - name: Run tests
      run: |
        poetry run pytest --cov=cream_api --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

    - name: Run security scan
      run: |
        poetry run bandit -r cream_api/

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: |
        docker build -t creampie:latest .

    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag creampie:latest ${{ secrets.DOCKER_REGISTRY }}/creampie:latest
        docker push ${{ secrets.DOCKER_REGISTRY }}/creampie:latest
```

**Code Generation Hint**: This CI/CD configuration will inform all automated pipeline implementation.

**Validation**: All code changes must pass CI/CD pipeline before deployment.

### Deployment Stages
```yaml
# Deployment configuration
deployment:
  stages:
    - name: development
      branch: develop
      environment: dev
      auto_deploy: true
      tests: required

    - name: staging
      branch: staging
      environment: staging
      auto_deploy: false
      tests: required
      manual_approval: true

    - name: production
      branch: main
      environment: production
      auto_deploy: false
      tests: required
      manual_approval: true
      rollback: enabled
```

**Code Generation Hint**: This deployment configuration will inform all deployment stage management.

**Validation**: All deployments must follow proper stage progression and approval.

## 5. Environment Management

### Environment Configuration
```bash
# Environment variables structure
# .env.development
DATABASE_URL=postgresql://user:pass@localhost:5432/creampie_dev
REDIS_URL=redis://localhost:6379/0
API_KEY=dev_api_key
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# .env.staging
DATABASE_URL=postgresql://user:pass@staging-db:5432/creampie_staging
REDIS_URL=redis://staging-redis:6379/0
API_KEY=staging_api_key
LOG_LEVEL=INFO
ENVIRONMENT=staging

# .env.production
DATABASE_URL=postgresql://user:pass@prod-db:5432/creampie_prod
REDIS_URL=redis://prod-redis:6379/0
API_KEY=prod_api_key
LOG_LEVEL=WARNING
ENVIRONMENT=production
```

**Code Generation Hint**: This environment configuration will inform all environment variable management.

**Validation**: All environments must have proper configuration and secrets management.

### Database Migrations
```bash
# Migration workflow
# Create new migration
poetry run alembic revision --autogenerate -m "description of changes"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1

# Check migration status
poetry run alembic current

# Generate migration script
poetry run alembic revision -m "manual migration"
```

**Code Generation Hint**: This migration workflow will inform all database schema changes.

**Validation**: All database changes must use proper migration procedures.

## 6. Monitoring and Logging

### Application Monitoring
```python
# Monitoring configuration
import logging
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

**Code Generation Hint**: This monitoring configuration will inform all application monitoring implementation.

**Validation**: All applications must include proper monitoring and health checks.

### Error Tracking
```python
# Error tracking configuration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv("ENVIRONMENT", "development")
)

# Custom error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Send to error tracking
    sentry_sdk.capture_exception(exc)

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

**Code Generation Hint**: This error tracking configuration will inform all error handling implementation.

**Validation**: All applications must include proper error tracking and handling.

## 7. Documentation Standards

### Code Documentation
```python
# Function documentation
def process_stock_data(symbol: str, data: dict) -> dict:
    """
    Process raw stock data and return formatted results.

    Args:
        symbol (str): Stock symbol (e.g., 'AAPL')
        data (dict): Raw stock data from API

    Returns:
        dict: Processed stock data with calculated fields

    Raises:
        ValueError: If symbol is invalid or data is malformed
        ProcessingError: If data processing fails

    Example:
        >>> data = {"price": 150.00, "volume": 1000000}
        >>> result = process_stock_data("AAPL", data)
        >>> print(result["formatted_price"])
        '$150.00'
    """
    # Implementation here
    pass
```

**Code Generation Hint**: This documentation pattern will inform all code documentation implementation.

**Validation**: All functions must include proper docstrings and examples.

### API Documentation
```python
# FastAPI documentation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="CreamPie API",
    description="Stock data processing and analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class StockData(BaseModel):
    """Stock data model for API requests"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    date: str = Field(..., description="Date in YYYY-MM-DD format")

    class Config:
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "date": "2024-01-01"
            }
        }

@app.get("/api/stock/{symbol}", response_model=StockData)
async def get_stock_data(
    symbol: str = Path(..., description="Stock symbol to retrieve"),
    date: str = Query(..., description="Date for stock data")
):
    """
    Retrieve stock data for a given symbol and date.

    - **symbol**: Stock symbol (e.g., AAPL, TSLA)
    - **date**: Date in YYYY-MM-DD format

    Returns stock price, volume, and other market data.
    """
    # Implementation here
    pass
```

**Code Generation Hint**: This API documentation pattern will inform all API endpoint documentation.

**Validation**: All API endpoints must include proper documentation and examples.

## Implementation Guidelines

### For AI Assistants
1. **Follow these patterns** for all development workflow implementation
2. **Use proper Git workflow** with meaningful commit messages
3. **Include comprehensive testing** with proper coverage
4. **Follow CI/CD pipeline** requirements and validation
5. **Implement proper monitoring** and error tracking
6. **Update documentation** with all code changes
7. **Follow security best practices** for all deployments
8. **Use proper environment management** for all stages

### For Human Developers
1. **Reference these patterns** when working on the project
2. **Follow Git workflow** for all code changes
3. **Write comprehensive tests** for new functionality
4. **Use CI/CD pipeline** for automated validation
5. **Monitor application health** and performance
6. **Keep documentation updated** with changes
7. **Follow security guidelines** for production deployments

## Quality Assurance

### Development Standards
- All code changes must follow Git workflow and branching strategy
- All commits must include proper commit messages and validation
- All changes must pass automated testing before deployment
- All deployments must follow proper environment promotion
- All documentation must be updated with code changes

### Testing Standards
- Unit tests must cover all new functionality
- Integration tests must validate component interactions
- Test coverage must meet minimum thresholds
- Performance tests must be included for critical paths
- Security tests must validate input handling

### Deployment Standards
- All deployments must pass CI/CD pipeline validation
- Environment promotion must follow proper sequence
- Rollback procedures must be tested and documented
- Monitoring and alerting must be configured
- Security scanning must be performed

### Documentation Standards
- Code must be self-documenting with proper comments
- API documentation must be comprehensive and up-to-date
- README files must include setup and usage instructions
- Architecture documentation must reflect current state
- Change logs must be maintained for all releases

---

**AI Quality Checklist**: Before implementing development workflow changes, ensure:
- [x] Git workflow follows branching strategy and commit standards
- [x] Code review process includes comprehensive checklist
- [x] Testing workflow covers all required test types
- [x] CI/CD pipeline includes all validation steps
- [x] Environment management follows proper configuration
- [x] Monitoring and logging are properly configured
- [x] Documentation standards are followed for all changes
- [x] Security best practices are implemented throughout
