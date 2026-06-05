# MCN Manager 部署运维指南

> 版本: 1.0 | 适用环境: 开发 / 测试 / 生产

---

## 目录

- [环境要求](#环境要求)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [生产环境配置](#生产环境配置)
- [Docker Compose 部署](#docker-compose-部署)
- [健康检查](#健康检查)
- [监控与日志](#监控与日志)
- [数据备份与恢复](#数据备份与恢复)
- [常见问题](#常见问题)

---

## 环境要求

### 开发环境

| 依赖 | 最低版本 | 推荐版本 | 说明 |
|------|---------|---------|------|
| Python | 3.12 | 3.12+ | 后端运行时 |
| Node.js | 18.0 | 20 LTS | 前端构建 |
| npm | 9.0 | 10+ | 包管理器 |
| Git | 2.30 | 最新 | 版本控制 |

### 生产环境 (推荐)

| 组件 | 说明 | 推荐配置 |
|------|------|---------|
| 操作系统 | Ubuntu 22.04 LTS / CentOS 8+ | 2核 4GB 起步 |
| PostgreSQL | 15+ (替代 SQLite) | 高并发必选 |
| Redis | 7+ (缓存) | 替代 LocMemCache |
| Nginx | 1.24+ | 反向代理 + 静态文件 |
| Gunicorn | WSGI 服务器 | 多 worker 部署 |

---

## 后端部署

### 1. 安装依赖

```bash
cd anchor_system
pip install -r requirements.txt
```

**核心依赖清单:**

| 包名 | 用途 |
|------|------|
| Django 6.0+ | Web 框架 |
| djangorestframework | REST API 框架 |
| django-cors-headers | CORS 跨域支持 |
| djangorestframework-simplejwt | JWT 认证 |
| django-redis | Redis 缓存后端 (可选) |
| waitress | WSGI 服务器 (Windows 兼容) |
| gunicorn | WSGI 服务器 (Linux 推荐) |

### 2. 初始化数据库

```bash
python manage.py migrate
```

首次运行会自动创建 `db.sqlite3` 并执行全部迁移。

### 3. 导入种子数据 (可选)

```bash
python manage.py seed_data
```

种子数据规模:

| 数据 | 数量 |
|------|------|
| 品牌 | 20 |
| 店铺 | 50 |
| 直播间 | 102 |
| 团队 | 8 |
| 员工 (主播) | 100 |
| 员工 (运营) | 80 |
| 员工 (经理) | 5 |
| 班次 | 4 |
| 排班记录 | ~2500 |
| 考勤记录 | ~2200 |
| 直播场次 | 336 |
| 商品销售 | 1146 |
| 请假申请 | 15 |

### 4. 创建管理员账号

```bash
python manage.py createsuperuser
```

按提示输入用户名、邮箱和密码。

### 5. 启动后端服务

**开发模式:**

```bash
python manage.py runserver 8000
```

访问 `http://127.0.0.1:8000/api/` 验证接口可用。

**生产模式 (Linux -- Gunicorn):**

```bash
gunicorn backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

**生产模式 (Windows -- Waitress):**

```bash
python -m waitress --port=8000 --threads=4 backend.wsgi:application
```

---

## 前端部署

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 开发模式

```bash
npm run dev
```

Vite 开发服务器启动于 `http://127.0.0.1:5173`，自动代理 `/api` 请求到后端 `8000` 端口。

### 3. 生产构建

```bash
npm run build
```

构建产物输出到 `dist/` 目录，包含压缩后的 HTML、JS、CSS 及静态资源。

### 4. 预览构建产物

```bash
npm run preview
```

---

## 生产环境配置

### Nginx 配置

```nginx
upstream mcn_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # 前端静态文件
    location / {
        root /opt/mcn/frontend/dist;
        try_files $uri $uri/ /index.html;

        # 静态资源缓存 (JS/CSS/图片)
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://mcn_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置 (AI 接口可能较慢)
        proxy_connect_timeout 30s;
        proxy_read_timeout 120s;
    }

    # 静态文件 (Django admin 等)
    location /static/ {
        alias /opt/mcn/anchor_system/static/;
    }
}
```

### PostgreSQL 配置

**安装:**

```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser mcn_user -P
sudo -u postgres createdb mcn_db -O mcn_user
```

**Django 配置 (`settings.py`):**

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

**安装依赖:**

```bash
pip install psycopg2-binary
```

**迁移:**

```bash
python manage.py migrate
```

### Redis 配置

**安装:**

```bash
sudo apt install redis-server
sudo systemctl enable redis-server
```

**Django 配置 (`settings.py`):**

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

**安装依赖:**

```bash
pip install django-redis
```

### Gunicorn 配置

推荐使用配置文件 `gunicorn.conf.py`:

```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1  # 推荐公式
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000          # 内存泄漏防护
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

启动:

```bash
gunicorn backend.wsgi:application -c gunicorn.conf.py
```

### 生产环境安全检查清单

| 项目 | 配置 |
|------|------|
| `DEBUG` | 设为 `False` |
| `SECRET_KEY` | 使用环境变量注入，不硬编码 |
| `ALLOWED_HOSTS` | 设为实际域名/IP |
| `CORS_ALLOW_ALL_ORIGINS` | 设为 `False`，配置白名单 |
| HTTPS | 配置 SSL 证书 (Let's Encrypt) |
| 防火墙 | 仅开放 80/443 端口 |

---

## Docker Compose 部署

`docker-compose.yml` 示例:

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

**后端 Dockerfile** (`anchor_system/Dockerfile`):

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn psycopg2-binary

COPY . .

EXPOSE 8000

CMD ["gunicorn", "backend.wsgi:application", "-b", "0.0.0.0:8000", "-w", "4"]
```

**前端 Dockerfile** (`frontend/Dockerfile`):

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

**启动:**

```bash
docker compose up -d
```

**初始化数据:**

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_data
```

---

## 健康检查

### API 健康检查

系统内置健康检查中间件，检测数据库和缓存连接状态:

```bash
curl http://127.0.0.1:8000/api/health/
```

正常响应:

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

异常响应:

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

### 外部监控集成

**cron 定时检查 (每分钟):**

```bash
* * * * * curl -sf http://127.0.0.1:8000/api/health/ > /dev/null || echo "MCN API DOWN" | mail -s "MCN Alert" admin@example.com
```

---

## 监控与日志

### 请求耗时监控

所有 API 响应包含 `X-Response-Time` 响应头 (毫秒)。后端中间件自动记录:

| 耗时 | 日志级别 | 标签 |
|------|---------|------|
| > 100ms | INFO | `SLOWISH` |
| > 500ms | WARNING | `SLOW` |

### 日志配置

当前日志输出到控制台 (`stdout`)，格式:

```
2026-06-05 10:30:15 INFO  SLOWISH /api/dashboard/overview/ 120ms
```

生产环境建议添加文件日志:

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

### 系统资源监控

推荐使用 Prometheus + Grafana 进行系统级监控，关键指标:

| 指标 | 告警阈值 |
|------|---------|
| API 响应时间 P99 | > 2000ms |
| 数据库连接数 | > 80% 最大连接数 |
| Redis 内存使用 | > 80% maxmemory |
| 磁盘使用率 | > 85% |
| CPU 使用率 | 持续 > 80% 超过 5 分钟 |

---

## 数据备份与恢复

### SQLite 备份

开发/测试环境使用 SQLite 时:

```bash
# 安全在线备份 (WAL 模式下不锁表)
sqlite3 anchor_system/db.sqlite3 ".backup /backup/mcn_$(date +%Y%m%d).db"

# 压缩归档
gzip /backup/mcn_$(date +%Y%m%d).db
```

**自动备份脚本 (`backup.sh`):**

```bash
#!/bin/bash
BACKUP_DIR="/backup/mcn"
mkdir -p $BACKUP_DIR

# 数据库备份
sqlite3 /opt/mcn/anchor_system/db.sqlite3 ".backup $BACKUP_DIR/mcn_$(date +%Y%m%d_%H%M%S).db"

# 保留最近 30 天备份
find $BACKUP_DIR -name "mcn_*.db" -mtime +30 -delete

echo "[$(date)] Backup completed" >> $BACKUP_DIR/backup.log
```

### PostgreSQL 备份

```bash
# 全库备份
pg_dump -U mcn_user -Fc mcn_db > /backup/mcn_$(date +%Y%m%d).dump

# 恢复
pg_restore -U mcn_user -d mcn_db /backup/mcn_20260605.dump
```

**自动备份 (crontab):**

```bash
# 每天凌晨 2 点备份
0 2 * * * pg_dump -U mcn_user -Fc mcn_db | gzip > /backup/mcn_$(date +\%Y\%m\%d).dump.gz
```

### 数据导出 (API)

通过导出接口获取 CSV 格式数据:

```bash
# 导出直播记录
curl -X POST http://127.0.0.1:8000/api/exports/create_export/ \
  -H "Content-Type: application/json" \
  -d '{"export_type": "sessions", "params": {"start": "2026-01-01"}}'

# 导出考勤记录
curl -X POST http://127.0.0.1:8000/api/exports/create_export/ \
  -H "Content-Type: application/json" \
  -d '{"export_type": "attendance", "params": {"start": "2026-01-01"}}'

# 导出财务记录
curl -X POST http://127.0.0.1:8000/api/exports/create_export/ \
  -H "Content-Type: application/json" \
  -d '{"export_type": "finance", "params": {"start": "2026-01-01"}}'
```

---

## 常见问题

### Q: SQLite 支持多少并发?

WAL 模式下支持多读单写，读并发可达数千级，写操作串行化。日活 1000 用户以下无需切换数据库。超过 100 写并发/秒建议迁移 PostgreSQL。

### Q: 如何从 SQLite 迁移到 PostgreSQL?

1. 安装依赖: `pip install psycopg2-binary`
2. 创建 PostgreSQL 数据库和用户
3. 修改 `settings.py` 中的 `DATABASES` 配置
4. 执行迁移: `python manage.py migrate`
5. 导入旧数据: 使用 `dumpdata` / `loaddata` 或第三方工具

```bash
# 从 SQLite 导出
python manage.py dumpdata --natural-foreign --natural-primary -e auth.Permission -e contenttypes > data.json

# 切换到 PostgreSQL 后导入
python manage.py loaddata data.json
```

### Q: 如何启用 Redis 缓存?

1. 安装: `pip install django-redis`
2. 在 `settings.py` 中将 `CACHES` 配置切换为 Redis (已内置注释模板)
3. 重启服务即可

### Q: 前端构建后页面空白?

检查 Nginx 配置中 `try_files` 是否正确:

```nginx
location / {
    root /path/to/frontend/dist;
    try_files $uri $uri/ /index.html;  # SPA 必须回退到 index.html
}
```

### Q: AI 接口响应较慢?

AI 接口首次请求需要查询大量历史数据，后续请求会命中缓存 (120-180 秒 TTL)。如需进一步提升:

- 启用 Redis 缓存
- 增加 Gunicorn worker 数量
- 对数据库查询字段添加索引

### Q: 如何重置数据库?

```bash
rm anchor_system/db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
```

### Q: 如何查看慢请求?

查看控制台日志或日志文件，搜索 `SLOWISH` / `SLOW` 关键字。所有响应头中的 `X-Response-Time` 字段也可用于 Nginx 日志记录:

```nginx
log_format timed '$remote_addr - $request_time - $upstream_response_time - $request';
```
