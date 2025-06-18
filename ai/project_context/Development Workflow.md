# Development Workflow

This document outlines the development workflow for the CreamPie project, helping AI assistants understand how features progress from conception to deployment.

## Feature Development Lifecycle

### 1. Planning Phase
- **Feature Request**: Identify new functionality or improvements needed
- **Requirements Analysis**: Define what the feature should accomplish
- **Technical Design**: Plan the implementation approach
- **Database Schema**: Design any necessary data model changes

### 2. Implementation Phase
- **Database Migrations**: Create and run schema changes
- **Backend Development**: Implement API endpoints and business logic
- **Frontend Development**: Create UI components and user interface
- **Integration**: Connect frontend and backend components

### 3. Testing Phase
- **Unit Testing**: Test individual components in isolation
- **Integration Testing**: Test component interactions
- **End-to-End Testing**: Test complete user workflows
- **Performance Testing**: Ensure acceptable performance characteristics

### 4. Review Phase
- **Code Review**: Peer review of implementation
- **Documentation**: Update relevant guides and documentation
- **Technical Summary**: Update module summaries if needed

### 5. Deployment Phase
- **Staging Deployment**: Deploy to staging environment
- **Final Testing**: Validate in staging environment
- **Production Deployment**: Deploy to production
- **Monitoring**: Monitor for issues post-deployment

## Development Environment Setup

### Prerequisites
- Python 3.11+ with Poetry
- Node.js 18+ with Yarn
- PostgreSQL (or SQLite for development)
- Git for version control

### Local Development
```bash
# Backend setup
cd cream_api
poetry install
poetry run alembic upgrade head
poetry run uvicorn main:app --reload

# Frontend setup
cd cream_ui
yarn install
yarn dev
```

### Environment Configuration
- **Development**: Uses `.env` files for local configuration
- **Testing**: Uses test-specific configuration
- **Production**: Uses environment variables

## Code Organization Patterns

### Backend Structure
```
cream_api/
├── main.py              # Application entry point
├── settings.py          # Configuration management
├── db.py               # Database connection
├── migrations/         # Database schema changes
├── users/             # User management module
├── stock_data/        # Stock data processing module
├── background_tasks/  # Asynchronous task processing
└── tests/            # Test suite
```

### Frontend Structure
```
cream_ui/src/
├── App.tsx           # Main application component
├── main.tsx          # Application entry point
├── pages/           # Page components
├── components/      # Reusable UI components
├── hooks/          # Custom React hooks
├── lib/            # Utility functions
└── assets/         # Static assets
```

## Testing Strategy

### Backend Testing
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and database operations
- **Fixtures**: Reusable test data and setup
- **Mocking**: Isolate components for testing

### Frontend Testing
- **Component Tests**: Test individual React components
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user workflows
- **Visual Regression**: Ensure UI consistency

### Test Organization
```
tests/
├── conftest.py      # Shared test configuration
├── test_main.py     # Main application tests
├── stock_data/      # Stock data module tests
├── users/          # User management tests
└── common/         # Shared test utilities
```

## Code Quality Standards

### Linting and Formatting
- **Python**: Black for formatting, flake8 for linting
- **TypeScript**: ESLint for linting, Prettier for formatting
- **Pre-commit**: Automated checks before commits

### Documentation Standards
- **Code Comments**: Explain complex logic and decisions
- **Docstrings**: Document all public functions and classes
- **README Files**: Explain module purpose and usage
- **API Documentation**: Auto-generated from FastAPI

### Performance Considerations
- **Database Queries**: Optimize for efficiency
- **API Responses**: Minimize payload size
- **Frontend Rendering**: Use React optimization techniques
- **Background Tasks**: Handle long-running operations appropriately

## Deployment Process

### Staging Deployment
1. **Code Review**: Ensure all changes are reviewed
2. **Testing**: Run full test suite
3. **Build**: Create deployment artifacts
4. **Deploy**: Deploy to staging environment
5. **Validation**: Verify functionality in staging

### Production Deployment
1. **Final Review**: Last review of staging deployment
2. **Database Migration**: Apply any schema changes
3. **Deploy**: Deploy to production environment
4. **Health Check**: Verify system health
5. **Monitoring**: Monitor for issues

### Rollback Strategy
- **Database Rollback**: Revert schema changes if needed
- **Code Rollback**: Revert to previous version
- **Configuration Rollback**: Revert configuration changes

## Common Development Tasks

### Adding New API Endpoints
1. **Define Model**: Create Pydantic models for request/response
2. **Implement Logic**: Add business logic in appropriate module
3. **Create Endpoint**: Add FastAPI route with proper validation
4. **Add Tests**: Write unit and integration tests
5. **Update Documentation**: Update API documentation

### Database Schema Changes
1. **Design Schema**: Plan the new table structure
2. **Create Migration**: Generate Alembic migration
3. **Update Models**: Update SQLAlchemy models
4. **Test Migration**: Verify migration works correctly
5. **Deploy**: Apply migration in staging/production

### Frontend Component Development
1. **Design Interface**: Plan component structure and props
2. **Implement Component**: Create React component
3. **Add Styling**: Apply Tailwind CSS classes
4. **Add Interactivity**: Implement event handlers
5. **Test Component**: Write component tests

### Background Task Implementation
1. **Define Task**: Create task function with proper decorators
2. **Add Configuration**: Configure task parameters
3. **Implement Logic**: Add business logic for the task
4. **Add Error Handling**: Handle potential failures
5. **Test Task**: Verify task works correctly

## Troubleshooting Common Issues

### Database Issues
- **Migration Failures**: Check migration files and database state
- **Connection Issues**: Verify database configuration
- **Performance Issues**: Analyze query performance

### API Issues
- **Validation Errors**: Check request/response models
- **Authentication Issues**: Verify token handling
- **Performance Issues**: Monitor endpoint response times

### Frontend Issues
- **Build Failures**: Check TypeScript errors and dependencies
- **Runtime Errors**: Check browser console for errors
- **Styling Issues**: Verify Tailwind CSS configuration

### Background Task Issues
- **Task Failures**: Check task logs and error handling
- **Performance Issues**: Monitor task execution times
- **Scheduling Issues**: Verify task scheduling configuration

This workflow ensures consistent, high-quality development with proper testing, review, and deployment processes.
