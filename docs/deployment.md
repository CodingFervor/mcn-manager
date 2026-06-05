# MCN Manager Deployment & Operations Guide

> Version: 1.0 | Target Environments: Development / Testing / Production

---

## Table of Contents

- [Environment Requirements](#environment-requirements)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Production Environment Configuration](#production-environment-configuration)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Health Check](#health-check)
- [Monitoring & Logging](#monitoring--logging)
- [Data Backup & Recovery](#data-backup--recovery)
- [FAQ](#faq)

---

## Environment Requirements

### Development Environment

| Dependency | Minimum Version | Recommended Version | Description |
|------|---------|---------|------|
| Python | 3.12 | 3.12+ | Backend runtime |
| Node.js | 18.0 | 20 LTS | Frontend build |
| npm | 9.0 | 10+ | Package manager |
| Git | 2.30 | Latest | Version control |

### Production Environment (Recommended)

| Component | Description | Recommended Configuration |
|------|------|---------|
| Operating System | Ubuntu 22.04 LTS / CentOS 8+ | 2 cores, 4GB minimum |
| PostgreSQL | 15+ (replaces SQLite) | Required for high concurrency |
| Redis | 7+ (caching) | Replaces LocMemCache |
| Nginx | 1.24+ | Reverse proxy + static files |
| Gunicorn | WSGI server | Multi-worker deployment |

---

## Backend Deployment

### 1. Install Dependencies

```bash
cd anchor_system
pip install -r requirements.txt
```

**Core Dependencies:**

| Package | Purpose |
|------|------|
| Django 6.0+ | Web framework |
| djangorestframework | REST API framework |
| django-cors-headers | CORS support |
| djangorestframework-simplejwt | JWT authentication |
| django-redis | Redis cache backend (optional) |
| waitress | WSGI server (Windows compatible) |
| gunicorn | WSGI server (Linux recommended) |

### 2. Initialize Database

```bash
python manage.py migrate
```

On first run, this automatically creates `db.sqlite3` and executes all migrations.

### 3. Import Seed Data (Optional)

```bash
python manage.py seed_data
```

Seed data scale:

| Data | Count |
|------|------|
| Brands | 20 |
| Stores | 50 |
| Live Rooms | 102 |
| Teams | 8 |
| Employees (Anchors) | 100 |
| Employees (Operators) | 80 |
| Employees (Managers) | 5 |
| Shifts | 4 |
| Schedule Records | ~2500 |
| Attendance Records | ~2200 |
| Live Sessions | 336 |
| Product Sales | 1146 |
| Leave Requests | 15 |

### 4. Create Admin Account

```bash
python manage.py createsuperuser
```

Follow the prompts to enter username, email, and password.

### 5. Start Backend Service

**Development Mode:**

```bash
python manage.py runserver 8000
```

Visit `http://127.0.0.1:8000/api/` to verify API availability.

**Production Mode (Linux -- Gunicorn):**

```bash
gunicorn backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

**Production Mode (Windows -- Waitress):**

```bash
python -m waitress --port=8000 --threads=4 backend.wsgi:application
```

---

## Frontend Deployment

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Development Mode

```bash
npm run dev
```

The Vite development server starts at `http://127.0.0.1:5173` and automatically proxies `/api` requests to the backend on port 8000.

### 3. Production Build

```bash
npm run build
```

Build output goes to the `dist/` directory, containing minified HTML, JS, CSS, and static assets.

### 4. Preview Build Output

```bash
npm run preview
```

---

## Production Environment Configuration

### Nginx Configuration

```nginx
upstream mcn_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Frontend static files
    location / {
        root /opt/mcn/frontend/dist;
        try_files $uri $uri/ /index.html;

        # Static asset caching (JS/CSS/images)
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }

    # API reverse proxy
    location /api/ {
        proxy_pass http://mcn_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings (AI endpoints may be slow)
        proxy_connect_timeout 30s;
        proxy_read_timeout 120s;
    }

    # Static files (Django admin, etc.)
    location /static/ {
        alias /opt/mcn/anchor_system/static/;
    }
}
```

### PostgreSQL Configuration

**Installation:**

```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser mcn_user -P
sudo -u postgres createdb mcn_db -O mcn_user
```

**Django Configuration (`settings.py`):**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mcn_db',
        'USER': 'mcn_user',
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your-password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'connect_timeout': 5,
        },
    }
}
```

**Install Dependency:**

```bash
pip install psycopg2-binary
```

**Run Migrations:**

```bash
python manage.py migrate
```

### Redis Configuration

**Installation:**

```bash
sudo apt install redis-server
sudo systemctl enable redis-server
```

**Django Configuration (`settings.py`):**

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 2,
            'SOCKET_TIMEOUT': 2,
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'mcn:',
        'TIMEOUT': 300,
    }
}
```

**Install Dependency:**

```bash
pip install django-redis
```

### Gunicorn Configuration

Recommended configuration file `gunicorn.conf.py`:

```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000          # Memory leak protection
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

Start:

```bash
gunicorn backend.wsgi:application -c gunicorn.conf.py
```

### Production Security Checklist

| Item | Configuration |
|------|------|
| `DEBUG` | Set to `False` |
| `SECRET_KEY` | Inject via environment variable, do not hardcode |
| `ALLOWED_HOSTS` | Set to actual domain/IP |
| `CORS_ALLOW_ALL_ORIGINS` | Set to `False`, configure whitelist |
| HTTPS | Configure SSL certificate (Let's Encrypt) |
| Firewall | Only open ports 80/443 |

---

## Docker Compose Deployment

Example `docker-compose.yml`:

```yaml
version: "3.8"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mcn_db
      POSTGRES_USER: mcn_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-mcn_secure_2026}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mcn_user -d mcn_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./anchor_system
      dockerfile: Dockerfile
    environment:
      - DB_ENGINE=django.db.backends.postgresql
      - DB_HOST=db
      - DB_PORT=5432
      - DB_NAME=mcn_db
      - DB_USER=mcn_user
      - DB_PASSWORD=${DB_PASSWORD:-mcn_secure_2026}
      - REDIS_URL=redis://redis:6379/1
      - SECRET_KEY=${SECRET_KEY:-change-me-in-production}
      - DEBUG=False
      - ALLOWED_HOSTS=*
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: >
      sh -c "python manage.py migrate &&
             gunicorn backend.wsgi:application -c gunicorn.conf.py"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  pgdata:
```

**Backend Dockerfile** (`anchor_system/Dockerfile`):

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn psycopg2-binary

COPY . .

EXPOSE 8000

CMD ["gunicorn", "backend.wsgi:application", "-b", "0.0.0.0:8000", "-w", "4"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.24-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Start:**

```bash
docker compose up -d
```

**Initialize Data:**

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_data
```

---

## Health Check

### API Health Check

The system includes a built-in health check middleware that tests database and cache connectivity:

```bash
curl http://127.0.0.1:8000/api/health/
```

Healthy response:

```json
{
  "status": "healthy",
  "checks": {
    "db": "ok",
    "cache": "ok"
  },
  "version": "2.0.0"
}
```

Unhealthy response:

```json
{
  "status": "unhealthy",
  "checks": {
    "db": "ok",
    "cache": "error: Connection refused"
  },
  "version": "2.0.0"
}
```

### External Monitoring Integration

**Cron-based check (every minute):**

```bash
* * * * * curl -sf http://127.0.0.1:8000/api/health/ > /dev/null || echo "MCN API DOWN" | mail -s "MCN Alert" admin@example.com
```

---

## Monitoring & Logging

### Request Duration Monitoring

All API responses include the `X-Response-Time` response header (milliseconds). Backend middleware automatically logs:

| Duration | Log Level | Label |
|------|---------|------|
| > 100ms | INFO | `SLOWISH` |
| > 500ms | WARNING | `SLOW` |

### Logging Configuration

Logs are currently output to the console (`stdout`), with the format:

```
2026-06-05 10:30:15 INFO  SLOWISH /api/dashboard/overview/ 120ms
```

For production, file logging is recommended:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/mcn/app.log',
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)-5s [%(name)s] %(message)s',
        },
    },
    'loggers': {
        'api': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
        },
    },
}
```

### System Resource Monitoring

Prometheus + Grafana is recommended for system-level monitoring. Key metrics:

| Metric | Alert Threshold |
|------|---------|
| API response time P99 | > 2000ms |
| Database connections | > 80% of max connections |
| Redis memory usage | > 80% of maxmemory |
| Disk usage | > 85% |
| CPU usage | Sustained > 80% for over 5 minutes |

---

## Data Backup & Recovery

### SQLite Backup

When using SQLite in development/testing environments:

```bash
# Safe online backup (does not lock tables in WAL mode)
sqlite3 anchor_system/db.sqlite3 ".backup /backup/mcn_$(date +%Y%m%d).db"

# Compressed archive
gzip /backup/mcn_$(date +%Y%m%d).db
```

**Automated Backup Script (`backup.sh`):**

```bash
#!/bin/bash
BACKUP_DIR="/backup/mcn"
mkdir -p $BACKUP_DIR

# Database backup
sqlite3 /opt/mcn/anchor_system/db.sqlite3 ".backup $BACKUP_DIR/mcn_$(date +%Y%m%d_%H%M%S).db"

# Retain only the last 30 days of backups
find $BACKUP_DIR -name "mcn_*.db" -mtime +30 -delete

echo "[$(date)] Backup completed" >> $BACKUP_DIR/backup.log
```

### PostgreSQL Backup

```bash
# Full database backup
pg_dump -U mcn_user -Fc mcn_db > /backup/mcn_$(date +%Y%m%d).dump

# Restore
pg_restore -U mcn_user -d mcn_db /backup/mcn_20260605.dump
```

**Automated Backup (crontab):**

```bash
# Daily backup at 2:00 AM
0 2 * * * pg_dump -U mcn_user -Fc mcn_db | gzip > /backup/mcn_$(date +\%Y\%m\%d).dump.gz
```

### Data Export (API)

Export data in CSV format via the export endpoint:

```bash
# Export live session records
curl -X POST http://127.0.0.1:8000/api/exports/create_export/ \
  -H "Content-Type: application/json" \
  -d '{"export_type": "sessions", "params": {"start": "2026-01-01"}}'

# Export attendance records
curl -X POST http://127.0.0.1:8000/api/exports/create_export/ \
  -H "Content-Type: application/json" \
  -d '{"export_type": "attendance", "params": {"start": "2026-01-01"}}'

# Export finance records
curl -X POST http://127.0.0.1:8000/api/exports/create_export/ \
  -H "Content-Type: application/json" \
  -d '{"export_type": "finance", "params": {"start": "2026-01-01"}}'
```

---

## FAQ

### Q: How much concurrency does SQLite support?

In WAL mode, SQLite supports multiple concurrent readers with a single writer. Read concurrency can reach thousands; write operations are serialized. For fewer than 1000 daily active users, switching databases is unnecessary. If write concurrency exceeds 100/second, consider migrating to PostgreSQL.

### Q: How to migrate from SQLite to PostgreSQL?

1. Install dependency: `pip install psycopg2-binary`
2. Create PostgreSQL database and user
3. Modify the `DATABASES` configuration in `settings.py`
4. Run migrations: `python manage.py migrate`
5. Import old data: use `dumpdata` / `loaddata` or third-party tools

```bash
# Export from SQLite
python manage.py dumpdata --natural-foreign --natural-primary -e auth.Permission -e contenttypes > data.json

# Import after switching to PostgreSQL
python manage.py loaddata data.json
```

### Q: How to enable Redis caching?

1. Install: `pip install django-redis`
2. Switch the `CACHES` configuration in `settings.py` to Redis (commented template is included)
3. Restart the service

### Q: Frontend page is blank after build?

Check that the Nginx configuration has the correct `try_files` directive:

```nginx
location / {
    root /path/to/frontend/dist;
    try_files $uri $uri/ /index.html;  # SPA must fall back to index.html
}
```

### Q: AI endpoints respond slowly?

AI endpoints require querying large amounts of historical data on the first request; subsequent requests will hit the cache (120-180 seconds TTL). For further improvement:

- Enable Redis caching
- Increase Gunicorn worker count
- Add database indexes on query fields

### Q: How to reset the database?

```bash
rm anchor_system/db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
```

### Q: How to view slow requests?

Check the console log or log file, and search for `SLOWISH` / `SLOW` keywords. The `X-Response-Time` field in all response headers can also be used for Nginx log recording:

```nginx
log_format timed '$remote_addr - $request_time - $upstream_response_time - $request';
```
