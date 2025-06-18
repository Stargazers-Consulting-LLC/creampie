# Architecture Overview

> **For AI Assistants**: This document provides a high-level overview of the CreamPie project architecture, helping AI assistants understand the system design and component relationships. Use this as the foundation for all architectural decisions and implementation guidance.

## AI Metadata

**Template Version:** 2.0
**AI Processing Level:** High
**Required Context:** System architecture, microservices, API design, database design
**Validation Required:** Yes
**Code Generation:** Supported

**Dependencies:**
- `../guide_docs/Core%20Principles.md` - Decision-making frameworks
- `../guide_docs/Language-Specific/FastAPI%20Development%20Guide.md` - API implementation patterns
- `../guide_docs/Language-Specific/Python%20Style%20Guide.md` - Python implementation patterns
- `Common%20Patterns.md` - Project-specific patterns
- `../features/summaries/[COMPLETED]-stock_data_processing_pipeline_summary.md` - Stock data implementation

**Validation Rules:**
- All architectural decisions must align with established patterns
- Component relationships must be clearly defined
- Data flow must be traceable and documented
- Technology choices must be justified and consistent
- Integration points must be well-defined

## Overview

**Document Purpose:** High-level system architecture and component relationships for the CreamPie project
**Scope:** Complete system architecture, data flow, technology stack, and integration patterns
**Target Users:** AI assistants and developers understanding system design
**Last Updated:** Current

**AI Context:** This document serves as the architectural foundation for all development decisions. It provides the system context needed to understand component relationships, data flow, and technology choices throughout the project.

## System Architecture

### High-Level Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   cream_ui      │    │   cream_api     │    │   External      │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   Data Sources  │
│                 │    │                 │    │                 │
│ - React/TS      │    │ - FastAPI       │    │ - Stock APIs    │
│ - Vite          │    │ - SQLAlchemy    │    │ - Web Scraping  │
│ - Tailwind      │    │ - Alembic       │    │ - File Storage  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Code Generation Hint**: This architecture diagram will inform all component design and integration decisions.

**Validation**: All components must follow this architectural pattern and maintain clear separation of concerns.

### Core Modules

#### Backend (`cream_api/`)
- **`main.py`** - FastAPI application entry point and configuration
- **`db.py`** - Database connection and session management
- **`settings.py`** - Application configuration and environment variables
- **`users/`** - User authentication and session management
- **`stock_data/`** - Stock data retrieval, processing, and storage
- **`migrations/`** - Database schema management with Alembic
- **`background_tasks/`** - Asynchronous task processing

**Code Generation Hint**: This module structure will inform all backend development and file organization.

**Validation**: All backend modules must follow this structure and naming conventions.

#### Frontend (`cream_ui/`)
- **`src/App.tsx`** - Main application component
- **`src/pages/`** - Page components (Landing, Auth, etc.)
- **`src/components/`** - Reusable UI components
- **`src/hooks/`** - Custom React hooks
- **`src/lib/`** - Utility functions and configurations

**Code Generation Hint**: This module structure will inform all frontend development and component organization.

**Validation**: All frontend modules must follow this structure and React/TypeScript patterns.

## Data Flow

### Stock Data Pipeline
```
External Source → Retriever → Parser → Processor → Database
     ↓              ↓         ↓         ↓           ↓
  HTML Files    Raw Data   Parsed    Processed   Stored
                Storage    Data      Data        Data
```

**Code Generation Hint**: This data flow will inform all stock data processing implementation and error handling.

**Validation**: All stock data processing must follow this pipeline pattern with proper error handling at each stage.

### User Authentication Flow
```
Frontend → API → Authentication → Session → Database
   ↓        ↓         ↓            ↓         ↓
Login    Validate   Create      Store     Persist
Form     Credentials Session    Token     Session
```

**Code Generation Hint**: This authentication flow will inform all user authentication implementation and security patterns.

**Validation**: All authentication flows must follow this pattern with proper security measures and session management.

## Key Design Patterns

### 1. Separation of Concerns
- **Data Retrieval**: `stock_data/retriever.py` - Handles external data fetching
- **Data Parsing**: `stock_data/parser.py` - Converts raw data to structured format
- **Data Processing**: `stock_data/processor.py` - Business logic and data transformation
- **Data Storage**: `stock_data/loader.py` - Database operations

**Code Generation Hint**: This separation of concerns will inform all module design and responsibility assignment.

**Validation**: All modules must maintain clear separation of concerns and single responsibility principle.

### 2. Configuration Management
- **Environment-based**: Settings loaded from environment variables
- **Module-specific**: Each module has its own configuration
- **Type-safe**: Pydantic models for configuration validation

**Code Generation Hint**: This configuration pattern will inform all settings management and environment variable usage.

**Validation**: All configuration must use Pydantic models and environment variable support.

### 3. Background Processing
- **Asynchronous Tasks**: Long-running operations handled in background
- **File Processing**: Batch processing of downloaded files
- **Periodic Tasks**: Scheduled data retrieval and processing

**Code Generation Hint**: This background processing pattern will inform all asynchronous task implementation.

**Validation**: All background tasks must include proper error handling and lifecycle management.

### 4. Error Handling
- **Custom Exceptions**: Domain-specific error types
- **Graceful Degradation**: System continues operating despite failures
- **Comprehensive Logging**: Detailed error tracking and debugging

**Code Generation Hint**: This error handling pattern will inform all exception handling and logging implementation.

**Validation**: All error handling must follow established patterns with proper logging and graceful degradation.

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and settings management
- **aiohttp**: Asynchronous HTTP client/server
- **BeautifulSoup**: HTML parsing and web scraping

**Code Generation Hint**: This technology stack will inform all backend implementation and dependency choices.

**Validation**: All backend development must use these technologies and follow their best practices.

### Frontend
- **React**: UI library with TypeScript
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality component library

**Code Generation Hint**: This technology stack will inform all frontend implementation and component development.

**Validation**: All frontend development must use these technologies and follow their established patterns.

### Database
- **PostgreSQL**: Primary database
- **SQLite**: Development and testing database

**Code Generation Hint**: This database strategy will inform all database design and migration decisions.

**Validation**: All database operations must support both PostgreSQL and SQLite environments.

### Development Tools
- **Poetry**: Python dependency management
- **Yarn**: JavaScript package management
- **pytest**: Python testing framework
- **ESLint**: JavaScript/TypeScript linting

**Code Generation Hint**: This tooling will inform all development workflow and quality assurance processes.

**Validation**: All development must use these tools and follow their established workflows.

## Integration Points

### API Endpoints
- **Authentication**: `/auth/*` - Login, registration, session management
- **Stock Data**: `/stock-data/*` - Data retrieval and processing
- **User Management**: `/users/*` - User profile and preferences

**Code Generation Hint**: This API structure will inform all endpoint design and routing decisions.

**Validation**: All API endpoints must follow this structure and include proper documentation.

### Database Schema
- **Users**: Authentication and session data
- **Stock Data**: Processed financial data
- **File Storage**: Raw and parsed data files

**Code Generation Hint**: This database schema will inform all data modeling and migration decisions.

**Validation**: All database schema changes must maintain data integrity and follow established patterns.

### External Integrations
- **Stock APIs**: Real-time and historical data
- **Web Scraping**: Alternative data sources
- **File System**: Local storage for downloaded data

**Code Generation Hint**: This integration strategy will inform all external service integration and error handling.

**Validation**: All external integrations must include proper error handling and fallback mechanisms.

## Development Workflow

### Feature Development
1. **Database**: Create migrations for schema changes
2. **Backend**: Implement API endpoints and business logic
3. **Frontend**: Create UI components and integrate with API
4. **Testing**: Write unit and integration tests
5. **Documentation**: Update guides and technical summaries

**Code Generation Hint**: This development workflow will inform all feature implementation and project management.

**Validation**: All feature development must follow this workflow and include proper testing and documentation.

### Deployment Pipeline
1. **Development**: Local development with hot reloading
2. **Testing**: Automated tests and code quality checks
3. **Staging**: Environment for integration testing
4. **Production**: Live deployment with monitoring

**Code Generation Hint**: This deployment pipeline will inform all deployment and environment management decisions.

**Validation**: All deployments must follow this pipeline and include proper testing and monitoring.

## Common Patterns

### Error Handling
```python
try:
    # Operation that might fail
    result = await some_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise CustomException("User-friendly message") from e
```

**Code Generation Hint**: This error handling pattern will inform all exception handling implementation.

**Validation**: All error handling must follow this pattern with proper logging and user-friendly messages.

### Configuration Loading
```python
# Load once at module level
config = get_module_config()

def some_function():
    # Use module-level config
    processor = DataProcessor(config=config)
```

**Code Generation Hint**: This configuration pattern will inform all settings management implementation.

**Validation**: All configuration must be loaded at module level and cached appropriately.

### Database Operations
```python
async with AsyncSessionLocal() as session:
    async with session.begin():
        # Database operations
        session.add(model)
        await session.commit()
```

**Code Generation Hint**: This database pattern will inform all database operation implementation.

**Validation**: All database operations must use proper session management and transaction handling.

### Background Tasks
```python
@background_task
async def process_files():
    # Long-running operation
    await file_processor.process_all_files()
```

**Code Generation Hint**: This background task pattern will inform all asynchronous task implementation.

**Validation**: All background tasks must include proper error handling and lifecycle management.

## Architecture Principles

### 1. Scalability
- **Horizontal Scaling**: Design for multiple instances
- **Database Optimization**: Efficient queries and indexing
- **Caching Strategy**: Reduce database load
- **Async Processing**: Handle concurrent requests

**Code Generation Hint**: These scalability principles will inform all performance optimization decisions.

**Validation**: All components must be designed for scalability and performance.

### 2. Maintainability
- **Clear Separation**: Well-defined module boundaries
- **Consistent Patterns**: Standardized implementation approaches
- **Comprehensive Testing**: High test coverage
- **Documentation**: Clear and up-to-date documentation

**Code Generation Hint**: These maintainability principles will inform all code organization and quality decisions.

**Validation**: All code must follow maintainability principles and include proper documentation.

### 3. Security
- **Authentication**: Secure user authentication
- **Authorization**: Role-based access control
- **Data Validation**: Input validation and sanitization
- **Secure Communication**: HTTPS and secure headers

**Code Generation Hint**: These security principles will inform all security implementation and validation.

**Validation**: All components must implement proper security measures and validation.

### 4. Reliability
- **Error Handling**: Comprehensive exception handling
- **Graceful Degradation**: System continues operating despite failures
- **Monitoring**: Health checks and performance monitoring
- **Backup Strategy**: Data backup and recovery procedures

**Code Generation Hint**: These reliability principles will inform all system resilience and monitoring decisions.

**Validation**: All components must include proper error handling and monitoring.

## Implementation Guidelines

### For AI Assistants
1. **Reference this architecture** for all development decisions
2. **Follow established patterns** for consistency
3. **Maintain separation of concerns** in all modules
4. **Use appropriate technologies** from the defined stack
5. **Implement proper error handling** and logging
6. **Follow security best practices** for all components
7. **Design for scalability** and performance
8. **Include comprehensive testing** for all features

### For Human Developers
1. **Understand the architecture** before making changes
2. **Follow established patterns** for consistency
3. **Maintain code quality** and documentation
4. **Test thoroughly** before deployment
5. **Monitor performance** and errors
6. **Update documentation** when making changes
7. **Follow security guidelines** for all implementations

## Quality Assurance

### Architectural Standards
- All components must follow established architectural patterns
- Data flow must be traceable and well-documented
- Integration points must be clearly defined
- Technology choices must be consistent and justified

### Performance Standards
- API response times must be under 500ms for simple operations
- Database queries must be optimized and indexed
- Background tasks must not block main application flow
- System must handle concurrent requests efficiently

### Security Standards
- All endpoints must implement proper authentication
- Data validation must be comprehensive
- Sensitive data must be encrypted
- Security headers must be properly configured

### Reliability Standards
- System must handle failures gracefully
- Error logging must be comprehensive
- Health checks must be implemented
- Backup and recovery procedures must be in place

---

**AI Quality Checklist**: Before implementing architectural changes, ensure:
- [x] Changes align with established architectural patterns
- [x] Data flow is properly documented and traceable
- [x] Integration points are clearly defined
- [x] Technology choices are consistent and justified
- [x] Performance implications are considered
- [x] Security measures are implemented
- [x] Error handling is comprehensive
- [x] Documentation is updated accordingly
