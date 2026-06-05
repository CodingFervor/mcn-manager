# MCN Manager — Live Commerce Operations Management System

> Full-stack management system: Django 6 + Vue 3 + AI Intelligence Engine
> 83 data models · 82 ViewSets · 90+ API endpoints · 60 frontend pages · 6 AI capabilities

---

## Feature Overview

### Core Business
- Data Dashboard / Real-time Analytics Screen
- Store Management (multi-platform: Douyin / Kuaishou / Taobao / Xiaohongshu / Pinduoduo / JD / WeChat Channels)
- Personnel Management (streamers / operators / managers / assistants)
- Smart Scheduling (batch scheduling / conflict detection)
- Attendance Tracking (automatic late-arrival detection)
- Live-stream Performance (GMV / orders / conversion rate)
- Performance Reviews (S/A/B/C/D grading / bonus calculation)

### AI Intelligence Center
- GMV Forecasting (linear regression + moving average + seasonal adjustment)
- Smart Scheduling Recommendations (greedy matching + fatigue penalty)
- Streamer Profiling (five-dimension radar + AI insights)
- Anomaly Detection (Z-Score + rule engine)
- Operational Recommendations (25 real-time alerts)
- Smart Matching (optimal streamer-store combinations)

### Extended Features
- Product Catalog + Stock Alerts
- Live-stream Scripts + Talking-points Library
- Task Board (four columns: To Do / In Progress / Done / Blocked)
- Notification Center + Unread Reminders
- Finance Center (income & expenses / commissions / contracts)
- Marketing Campaign Management
- Competitor Monitoring + Follower Analysis
- Influencer / KOL Outreach
- Training Management + Goal Management
- Data Export (CSV)
- Audit Log + Permission Management

---

## Quick Start

### Backend

```bash
cd anchor_system
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data          # Load sample data (optional)
python manage.py runserver 8000     # Development server
```

### Frontend

```bash
cd frontend
npm install
npm run dev                         # Visit http://127.0.0.1:5173
```

### Production Build

```bash
# Backend
cd anchor_system
python -m waitress --port=8000 backend.wsgi:application

# Frontend
cd frontend
npm run build                       # Output to dist/
```

---

## Technical Architecture

```
Vue 3 + Element Plus + ECharts + Pinia + Vue Router
         │  Vite Proxy
Django 6 + DRF + JWT + Waitress
         │
Service Layer (caching + cache invalidation)
         │
AI Engine (6 intelligent algorithms)
         │
SQLite WAL (83 models + 20+ indexes)
```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Dashboard first load | ~10ms |
| Dashboard cached | ~2ms |
| AI Insights cached | ~3ms |
| Frontend build | ~2s |
| Total models | 83 |
| API endpoints | 90+ |
| Database indexes | 20+ |

---

## Documentation

| Document | Path |
|----------|------|
| System Architecture | [docs/architecture.md](architecture.md) |
| API Reference | [docs/api.md](api.md) |
| Data Models | [docs/models.md](models.md) |
| AI Engine | [docs/ai-engine.md](ai-engine.md) |
| Frontend Pages | [docs/frontend.md](frontend.md) |
| Deployment & Operations | [docs/deployment.md](deployment.md) |

---

## Project Structure

```
anchor_system/          # Django backend
├── backend/            # Project configuration
├── scheduling/         # Main app (models / views / services / AI engine)
└── db.sqlite3          # SQLite database

frontend/               # Vue frontend
├── src/
│   ├── views/          # 60 pages
│   ├── components/     # Reusable components
│   ├── composables/    # Shared hooks
│   ├── stores/         # Pinia store
│   └── router/         # Route configuration
└── docs/               # Project documentation
```

---

## Default Account

Admin user created by seed data: `admin` / `admin123`
