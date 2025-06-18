# Architecture Overview

This document provides a high-level overview of the CreamPie project architecture, helping AI assistants understand the system design and component relationships.

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

### Core Modules

#### Backend (`cream_api/`)
- **`main.py`** - FastAPI application entry point and configuration
- **`db.py`** - Database connection and session management
- **`settings.py`** - Application configuration and environment variables
- **`users/`** - User authentication and session management
- **`stock_data/`** - Stock data retrieval, processing, and storage
- **`migrations/`** - Database schema management with Alembic
- **`background_tasks/`** - Asynchronous task processing

#### Frontend (`cream_ui/`)
- **`src/App.tsx`** - Main application component
- **`src/pages/`** - Page components (Landing, Auth, etc.)
- **`src/components/`** - Reusable UI components
- **`src/hooks/`** - Custom React hooks
- **`src/lib/`** - Utility functions and configurations

## Data Flow

### Stock Data Pipeline
```
External Source → Retriever → Parser → Processor → Database
     ↓              ↓         ↓         ↓           ↓
  HTML Files    Raw Data   Parsed    Processed   Stored
                Storage    Data      Data        Data
```

### User Authentication Flow
```
Frontend → API → Authentication → Session → Database
   ↓        ↓         ↓            ↓         ↓
Login    Validate   Create      Store     Persist
Form     Credentials Session    Token     Session
```

## Key Design Patterns

### 1. Separation of Concerns
- **Data Retrieval**: `stock_data/retriever.py` - Handles external data fetching
- **Data Parsing**: `stock_data/parser.py` - Converts raw data to structured format
- **Data Processing**: `stock_data/processor.py` - Business logic and data transformation
- **Data Storage**: `stock_data/loader.py` - Database operations

### 2. Configuration Management
- **Environment-based**: Settings loaded from environment variables
- **Module-specific**: Each module has its own configuration
- **Type-safe**: Pydantic models for configuration validation

### 3. Background Processing
- **Asynchronous Tasks**: Long-running operations handled in background
- **File Processing**: Batch processing of downloaded files
- **Periodic Tasks**: Scheduled data retrieval and processing

### 4. Error Handling
- **Custom Exceptions**: Domain-specific error types
- **Graceful Degradation**: System continues operating despite failures
- **Comprehensive Logging**: Detailed error tracking and debugging

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and settings management
- **aiohttp**: Asynchronous HTTP client/server
- **BeautifulSoup**: HTML parsing and web scraping

### Frontend
- **React**: UI library with TypeScript
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality component library

### Database
- **PostgreSQL**: Primary database
- **SQLite**: Development and testing database

### Development Tools
- **Poetry**: Python dependency management
- **Yarn**: JavaScript package management
- **pytest**: Python testing framework
- **ESLint**: JavaScript/TypeScript linting

## Integration Points

### API Endpoints
- **Authentication**: `/auth/*` - Login, registration, session management
- **Stock Data**: `/stock-data/*` - Data retrieval and processing
- **User Management**: `/users/*` - User profile and preferences

### Database Schema
- **Users**: Authentication and session data
- **Stock Data**: Processed financial data
- **File Storage**: Raw and parsed data files

### External Integrations
- **Stock APIs**: Real-time and historical data
- **Web Scraping**: Alternative data sources
- **File System**: Local storage for downloaded data

## Development Workflow

### Feature Development
1. **Database**: Create migrations for schema changes
2. **Backend**: Implement API endpoints and business logic
3. **Frontend**: Create UI components and integrate with API
4. **Testing**: Write unit and integration tests
5. **Documentation**: Update guides and technical summaries

### Deployment Pipeline
1. **Development**: Local development with hot reloading
2. **Testing**: Automated tests and code quality checks
3. **Staging**: Environment for integration testing
4. **Production**: Live deployment with monitoring

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

### Configuration Loading
```python
# Load once at module level
config = get_module_config()

def some_function():
    # Use module-level config
    processor = DataProcessor(config=config)
```

### Database Operations
```python
async with AsyncSessionLocal() as session:
    async with session.begin():
        # Database operations
        session.add(model)
        await session.commit()
```

### Background Tasks
```python
@background_task
async def process_files():
    # Long-running operation
    await file_processor.process_all_files()
```

This architecture provides a solid foundation for scalable, maintainable development with clear separation of concerns and robust error handling.
