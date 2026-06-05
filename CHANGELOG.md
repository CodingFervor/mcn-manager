# Changelog

All notable changes to this project are documented in this file. Format based on [Keep a Changelog](https://keepachangelog.com/en/).

---

## [3.0.0] - 2026-06-06

### Added

#### 20 New Feature Modules
- LiveInteraction — Live stream interaction management (gifts, polls, Q&A)
- Coupon — Coupon creation, distribution, and redemption tracking
- FlashSale — Flash sale campaign management with time-limited offers
- RoomDecoration — Live room decoration and virtual background themes
- ScriptTag — Script tagging and categorization system
- SignContract — Digital contract signing workflow
- BusinessNegotiation — Business negotiation tracking and follow-ups
- Investment — Investment and funding record management
- ContractLedger — Contract ledger with full lifecycle tracking
- Authorization — Resource authorization and permission delegation
- CompetitorRoom — Competitor live room monitoring and benchmarking
- TrafficAnalysis — Traffic source analysis and attribution
- UserPersona — User persona segmentation and profiling
- ABTest — A/B testing framework for campaigns and content
- DataWarning — Data anomaly alerts and threshold-based warnings
- Settlement — Financial settlement and payout management
- Logistics — Logistics and shipping order tracking
- Inventory — Multi-warehouse inventory management
- ReturnAnalysis — Return/refund analysis and reason tracking
- TaxRecord — Tax record keeping and compliance reporting

#### Project Milestones
- Total: **83 models**, **82 ViewSets**, **60 frontend pages**
- GitHub repository created at https://github.com/CodingFervor/mcn-manager

---

## [2.0.0] - 2026-06-05

### Added

#### AI Intelligence Engine
- GMV Prediction (Linear Regression + Moving Average + Seasonal Adjustment)
- Smart Scheduling Recommendation (Greedy Matching + Fatigue Penalty + Lateness Penalty)
- Anchor Profile Analysis (5-Dimension Radar: Sales / Traffic / Conversion / Stability / Growth)
- Anomaly Detection (Z-Score + Rule Engine)
- Operations Advisory Engine (25+ real-time alerts)
- Anchor-Store Intelligent Matching

#### Extended Features (20 modules)
- Product Catalog + Inventory Alerts
- Live Script (section-based) + Talking Points Library
- Live Session Post-Mortem
- Task Board (4 columns: To-Do / In Progress / Done / Blocked)
- Notification Center + Unread Reminders
- Financial Reports (Income/Expense, Commission, Contracts)
- Training Management + Goal Management
- Competitor Monitoring + Fan Analysis
- Marketing Campaign Management
- Influencer / KOL Outreach
- Data Export (CSV)
- Real-Time Dashboard (TV Projection)
- Permission Management (Roles / Permissions)
- Operation Logs

#### Architecture Upgrade
- Service Layer Separation (business logic decoupled from Views)
- Vue Router replacing conditional rendering
- Pinia state management
- Element Plus on-demand auto-import (unplugin-auto-import)
- Reusable Components (StatCard / PageHeader / ChartWrap)
- Composables (useApi / useChart)
- Request timing middleware + X-Response-Time header
- Health check endpoint GET /api/health/
- Rate limiting at 100 requests/minute
- Slow request log alerts (>100ms INFO, >500ms WARNING)
- Automatic cache invalidation on write operations
- requirements.txt

### Optimized
- ECharts Tree-shaking (only BarChart / LineChart / PieChart imported)
- Vite manualChunks splitting (element-plus / echarts / vendor)
- defineAsyncComponent lazy-loading for all pages
- SQLite WAL mode + PRAGMA optimization
- 18 database indexes
- select_related / prefetch_related added to all ViewSets
- Store overview N+1 fix (150+ queries → 3 queries)
- Dashboard response time 300ms → 2ms
- AI endpoint result caching (120–180s)

---

## [1.0.0] - 2026-05-20

### Added
- Core models: Brand, Store, Team, StreamRoom, Employee, AnchorProfile, Shift, Schedule, Attendance, LeaveRequest, LiveSession, ProductSales, KPIConfig, PerformanceReview (13 total)
- 8 pages: Dashboard, Stores, Employees, Schedules, Attendance, Sessions, Reviews, Shifts
- 15 ViewSets (full CRUD)
- JWT Authentication
- Seed data management command (seed_data)
- Dark neon UI theme
