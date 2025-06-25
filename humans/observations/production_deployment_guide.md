# CreamPie Production Deployment Guide

## Overview

This guide outlines the complete process for deploying the CreamPie application to production without using Docker. The application consists of:

- **Backend**: FastAPI Python application (`cream_api`)
- **Frontend**: React TypeScript application (`cream_ui`)
- **Database**: PostgreSQL with Alembic migrations
- **Background Tasks**: Stock data processing pipeline

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04+ or CentOS 8+ (recommended)
- **Python**: 3.12+ (as specified in pyproject.toml)
- **Node.js**: 18+ (for frontend build)
- **PostgreSQL**: 13+ (for database)
- **Nginx**: 1.18+ (for reverse proxy)
- **System Memory**: Minimum 4GB RAM, 8GB+ recommended
- **Storage**: 20GB+ available space

### Required Software

```bash
# System packages
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx
sudo apt install -y nodejs npm yarn
sudo apt install -y git curl wget
sudo apt install -y build-essential libpq-dev
sudo apt install -y supervisor
sudo apt install -y certbot python3-certbot-nginx

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

## Step 1: Server Setup and Security

### 1.1 Create Application User

```bash
# Create dedicated user for the application
sudo useradd -m -s /bin/bash creampie
sudo usermod -aG sudo creampie

# Switch to application user
sudo su - creampie
```

### 1.2 Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS, and PostgreSQL
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5432
sudo ufw enable
```

### 1.3 Set Up SSL Certificate

```bash
# Install SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com
```

## Step 2: Database Setup

### 2.1 PostgreSQL Configuration

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE cream_prod;
CREATE USER creamapp WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE cream_prod TO creamapp;
\q

# Configure PostgreSQL for production
sudo nano /etc/postgresql/*/main/postgresql.conf

# Add/modify these settings:
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 2.2 Database Migration Setup

```bash
# Create migration directory structure
sudo mkdir -p /opt/creampie/migrations
sudo chown creampie:creampie /opt/creampie/migrations

# Copy migration files
sudo cp -r cream_api/migrations/* /opt/creampie/migrations/
```

## Step 3: Backend Deployment

### 3.1 Application Directory Setup

```bash
# Create application directory
sudo mkdir -p /opt/creampie
sudo chown creampie:creampie /opt/creampie

# Clone repository
cd /opt/creampie
git clone https://github.com/your-repo/creampie.git .
```

### 3.2 Python Environment Setup

```bash
# Install Poetry dependencies
cd /opt/creampie
poetry install --no-dev

# Create virtual environment
poetry env use python3.12
```

### 3.3 Environment Configuration

Create `/opt/creampie/cream_api/.env`:

```bash
# Database Configuration
DB_USER=creamapp
DB_HOST=localhost
DB_NAME=cream_prod
DB_PASSWORD=secure_password_here
DB_ADMIN_USER=postgres
DB_ADMIN_PASSWORD=admin_password_here

# Application Configuration
FRONTEND_URL=https://yourdomain.com
ENABLE_BACKGROUND_TASKS=true
DEBUG_MODE=false
LOG_LEVEL=INFO
LOG_FILE=/opt/creampie/logs/cream_api.log
LOG_MAX_SIZE_MB=50
LOG_BACKUP_COUNT=10

# Security (generate secure keys)
JWT_SECRET_KEY=your_secure_jwt_secret_here
SECRET_KEY=your_secure_secret_key_here
```

### 3.4 Create Required Directories

```bash
# Create log and data directories
mkdir -p /opt/creampie/logs
mkdir -p /opt/creampie/stock_data/files/raw_responses
mkdir -p /opt/creampie/stock_data/files/parsed_responses
mkdir -p /opt/creampie/stock_data/files/deadletter_responses
mkdir -p /opt/creampie/downloaded_files

# Set permissions
chmod 755 /opt/creampie/logs
chmod 755 /opt/creampie/stock_data
```

### 3.5 Run Database Migrations

```bash
cd /opt/creampie
poetry run alembic upgrade head
```

### 3.6 Gunicorn Configuration

Create `/opt/creampie/gunicorn.conf.py`:

```python
# Gunicorn configuration
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

### 3.7 Supervisor Configuration

Create `/etc/supervisor/conf.d/creampie.conf`:

```ini
[program:creampie-api]
command=/opt/creampie/.venv/bin/gunicorn -c /opt/creampie/gunicorn.conf.py cream_api.main:app
directory=/opt/creampie
user=creampie
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/creampie/logs/gunicorn.log
environment=PYTHONPATH="/opt/creampie"
```

## Step 4: Frontend Deployment

### 4.1 Build Frontend

```bash
cd /opt/creampie/cream_ui

# Install dependencies
yarn install

# Build for production
yarn build
```

### 4.2 Configure Frontend for Production

Update `cream_ui/vite.config.ts` for production:

```typescript
import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});
```

## Step 5: Nginx Configuration

### 5.1 Main Nginx Configuration

Create `/etc/nginx/sites-available/creampie`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend static files
    location / {
        root /opt/creampie/cream_ui/dist;
        try_files $uri $uri/ /index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/;
        access_log off;
    }
}
```

### 5.2 Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/creampie /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 6: Service Management

### 6.1 Start Services

```bash
# Start supervisor
sudo systemctl enable supervisor
sudo systemctl start supervisor

# Reload supervisor configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start the application
sudo supervisorctl start creampie-api
```

### 6.2 Service Status Commands

```bash
# Check application status
sudo supervisorctl status creampie-api

# View logs
sudo tail -f /opt/creampie/logs/gunicorn.log
sudo tail -f /opt/creampie/logs/cream_api.log

# Restart application
sudo supervisorctl restart creampie-api
```

## Step 7: Monitoring and Logging

### 7.1 Log Rotation

Create `/etc/logrotate.d/creampie`:

```
/opt/creampie/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 creampie creampie
    postrotate
        supervisorctl restart creampie-api
    endscript
}
```

### 7.2 Health Monitoring

Create `/opt/creampie/scripts/health_check.sh`:

```bash
#!/bin/bash

# Health check script
API_URL="http://127.0.0.1:8000/"
FRONTEND_URL="https://yourdomain.com"

# Check API
if curl -f -s "$API_URL" > /dev/null; then
    echo "API is healthy"
else
    echo "API is down"
    exit 1
fi

# Check frontend
if curl -f -s "$FRONTEND_URL" > /dev/null; then
    echo "Frontend is healthy"
else
    echo "Frontend is down"
    exit 1
fi
```

## Step 8: Backup Strategy

### 8.1 Database Backup

Create `/opt/creampie/scripts/backup_db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/creampie/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/cream_prod_$DATE.sql"

mkdir -p "$BACKUP_DIR"

# Create database backup
pg_dump -h localhost -U creamapp cream_prod > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
```

### 8.2 Application Backup

```bash
# Backup application files
tar -czf /opt/creampie/backups/app_$(date +%Y%m%d_%H%M%S).tar.gz \
    --exclude=node_modules \
    --exclude=.git \
    --exclude=logs \
    /opt/creampie
```

## Step 9: Security Hardening

### 9.1 File Permissions

```bash
# Set secure permissions
sudo chown -R creampie:creampie /opt/creampie
sudo chmod 755 /opt/creampie
sudo chmod 600 /opt/creampie/cream_api/.env
sudo chmod 644 /opt/creampie/logs/*.log
```

### 9.2 Database Security

```bash
# Configure PostgreSQL for security
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Add these lines:
local   cream_prod    creamapp                    md5
host    cream_prod    creamapp    127.0.0.1/32    md5
host    cream_prod    creamapp    ::1/128         md5
```

## Step 10: Deployment Verification

### 10.1 Smoke Tests

```bash
# Test API endpoints
curl -f https://yourdomain.com/api/
curl -f https://yourdomain.com/health

# Test frontend
curl -f https://yourdomain.com/

# Test database connection
cd /opt/creampie
poetry run python -c "
from cream_api.db import get_db
from cream_api.settings import get_app_settings
settings = get_app_settings()
print(f'Database connection: {settings.get_connection_string()}')
"
```

### 10.2 Performance Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API performance
ab -n 1000 -c 10 https://yourdomain.com/api/

# Test frontend performance
ab -n 1000 -c 10 https://yourdomain.com/
```

## Step 11: Maintenance Procedures

### 11.1 Application Updates

```bash
# Update application
cd /opt/creampie
git pull origin main

# Update dependencies
poetry install --no-dev

# Run migrations
poetry run alembic upgrade head

# Rebuild frontend
cd cream_ui
yarn install
yarn build

# Restart services
sudo supervisorctl restart creampie-api
sudo systemctl reload nginx
```

### 11.2 Log Management

```bash
# View recent logs
sudo tail -f /opt/creampie/logs/cream_api.log
sudo tail -f /opt/creampie/logs/gunicorn.log

# Check disk usage
df -h /opt/creampie

# Clean old logs
sudo find /opt/creampie/logs -name "*.log.*" -mtime +30 -delete
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check PostgreSQL service status: `sudo systemctl status postgresql`
   - Verify connection string in `.env` file
   - Check firewall settings

2. **Application Won't Start**
   - Check supervisor logs: `sudo supervisorctl tail creampie-api`
   - Verify Python environment: `poetry env info`
   - Check file permissions

3. **Frontend Not Loading**
   - Verify build output exists: `ls -la /opt/creampie/cream_ui/dist`
   - Check Nginx configuration: `sudo nginx -t`
   - Verify SSL certificate: `sudo certbot certificates`

4. **Background Tasks Not Working**
   - Check background task logs
   - Verify `ENABLE_BACKGROUND_TASKS=true` in `.env`
   - Check file permissions for data directories

### Emergency Procedures

```bash
# Emergency restart
sudo supervisorctl restart creampie-api
sudo systemctl reload nginx

# Rollback to previous version
cd /opt/creampie
git checkout HEAD~1
sudo supervisorctl restart creampie-api

# Database rollback
poetry run alembic downgrade -1
```

## Conclusion

This deployment guide provides a comprehensive approach to deploying the CreamPie application in production without Docker. The setup includes:

- Secure server configuration
- Proper service management with Supervisor
- Nginx reverse proxy with SSL
- Database setup and migration management
- Monitoring and backup strategies
- Security hardening measures

Remember to:
- Regularly update dependencies and security patches
- Monitor application performance and logs
- Maintain regular backups
- Test the deployment process in a staging environment first
- Document any environment-specific configurations

For additional support, refer to the project's AI documentation system in the `ai/` directory for specific implementation details and patterns.
