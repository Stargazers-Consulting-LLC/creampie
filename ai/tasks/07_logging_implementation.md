# Logging System Implementation

## Overview

Implement a comprehensive logging system for the Cream API to enable better monitoring, debugging, and auditing capabilities.

## Requirements

### 1. Logging Configuration

#### Dependencies

```toml
[tool.poetry.dependencies]
structlog = "^24.1.0"
python-json-logger = "^2.0.7"
```

#### Logging Setup

```python
# cream_api/common/logging.py
import logging
import sys
from typing import Any

import structlog
from pythonjsonlogger import jsonlogger

def setup_logging() -> None:
    """Configure structured logging for the application."""
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    def add_fields(self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = self.formatTime(record)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
```

### 2. Log Categories

#### 1. Application Logs

- API request/response logging
- Authentication events
- User actions
- System events

#### 2. Security Logs

- Login attempts
- Password changes
- Token operations
- Access control events

#### 3. Performance Logs

- Request timing
- Database query performance
- External service calls
- Resource usage

#### 4. Error Logs

- Application errors
- Database errors
- External service errors
- Validation errors

### 3. Logging Implementation

#### Request Logging Middleware

```python
# cream_api/middleware/logging.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import structlog

logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(
            "request_started",
            method=request.method,
            url=str(request.url),
            client_host=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log response
            logger.info(
                "request_completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=process_time,
            )

            return response
        except Exception as e:
            logger.error(
                "request_failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                exc_info=True,
            )
            raise
```

#### Authentication Logging

```python
# cream_api/users/routes/auth.py
import structlog

logger = structlog.get_logger()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(
        "login_attempt",
        email=form_data.username,
        success=True,
    )
    # ... existing login logic ...
```

#### Database Logging

```python
# cream_api/db.py
import structlog

logger = structlog.get_logger()

def get_db():
    db = SessionLocal()
    try:
        logger.debug("database_session_started")
        yield db
    except Exception as e:
        logger.error(
            "database_error",
            error=str(e),
            exc_info=True,
        )
        raise
    finally:
        logger.debug("database_session_ended")
        db.close()
```

### 4. Log Storage

#### Log File Configuration

```python
# cream_api/common/logging.py
def configure_file_logging() -> None:
    """Configure file-based logging."""
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setFormatter(CustomJsonFormatter())

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
```

#### Log Rotation

```python
from logging.handlers import RotatingFileHandler

def configure_rotating_logs() -> None:
    """Configure rotating file logs."""
    handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    handler.setFormatter(CustomJsonFormatter())

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
```

### 5. Log Monitoring

#### Health Check Endpoint

```python
# cream_api/main.py
@app.get("/health/logs")
async def check_logs() -> dict:
    """Check logging system health."""
    try:
        logger.info("health_check", component="logging")
        return {"status": "healthy", "component": "logging"}
    except Exception as e:
        logger.error("health_check_failed", component="logging", error=str(e))
        return {"status": "unhealthy", "component": "logging", "error": str(e)}
```

## Implementation Steps

1. **Setup Logging Infrastructure**

   - Install required packages
   - Configure logging format
   - Set up log rotation
   - Create log directories

2. **Implement Logging Middleware**

   - Add request logging
   - Add response logging
   - Add error logging
   - Add performance logging

3. **Add Application Logging**

   - Add authentication logging
   - Add user action logging
   - Add system event logging
   - Add error logging

4. **Configure Log Storage**

   - Set up log file structure
   - Configure log rotation
   - Set up log backup

5. **Add Monitoring**
   - Implement health checks
   - Add log monitoring
   - Set up alerts

## Success Criteria

- All critical operations are logged
- Logs are properly formatted and structured
- Log rotation is working
- Log monitoring is in place
- Logs are easily searchable
- Performance impact is minimal

## Dependencies

- structlog
- python-json-logger
- Log storage system
- Monitoring system

## Timeline

- Setup: 1 day
- Implementation: 2-3 days
- Testing: 1-2 days
- Monitoring: 1 day
- Total: 5-7 days
