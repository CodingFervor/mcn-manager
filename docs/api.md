# MCN Manager API Reference

> Version: 1.0 | Base Path: `/api/` | Authentication: JWT / Session | Default Pagination: 50 items/page

---

## Table of Contents

- [General Conventions](#general-conventions)
- [Core Modules](#core-modules)
  - [Brand Management (brands)](#brand-management-brands)
  - [Store Management (stores)](#store-management-stores)
  - [Team Management (teams)](#team-management-teams)
  - [Live Room Management (rooms)](#live-room-management-rooms)
  - [Employee Management (employees)](#employee-management-employees)
  - [Shift Management (shifts)](#shift-management-shifts)
  - [Schedule Management (schedules)](#schedule-management-schedules)
  - [Attendance Management (attendances)](#attendance-management-attendances)
  - [Leave Management (leaves)](#leave-management-leaves)
  - [Live Sessions (sessions)](#live-sessions-sessions)
  - [Product Sales (product-sales)](#product-sales-product-sales)
  - [KPI Configuration (kpi-configs)](#kpi-configuration-kpi-configs)
  - [Performance Reviews (reviews)](#performance-reviews-reviews)
  - [Dashboard (dashboard)](#dashboard-dashboard)
- [AI Module](#ai-module)
- [Extended Modules](#extended-modules)
  - [Products & Inventory](#products--inventory)
  - [Live Streaming Tools](#live-streaming-tools)
  - [Task Board](#task-board)
  - [Notification Center](#notification-center)
  - [Finance Center](#finance-center)
  - [Commission Management](#commission-management)
  - [Contract Management](#contract-management)
  - [Training Management](#training-management)
  - [Competitor Analysis](#competitor-analysis)
  - [Fan Analysis](#fan-analysis)
  - [Marketing Campaigns](#marketing-campaigns)
  - [Goal Management](#goal-management)
  - [Operation Logs](#operation-logs)
  - [Billboard / Live Screen](#billboard--live-screen)
  - [Permission Management](#permission-management)
  - [KOL / Influencer Management](#kol--influencer-management)
  - [Data Export](#data-export)
- [4th Round Extension Modules](#4th-round-extension-modules)
  - [Live Interactions](#live-interactions-live-interactions)
  - [Coupons](#coupons-coupons)
  - [Flash Sales](#flash-sales-flash-sales)
  - [Room Decorations](#room-decorations-room-decorations)
  - [Script Tags](#script-tags-script-tags)
  - [Sign Contracts](#sign-contracts-sign-contracts)
  - [Negotiations](#negotiations-negotiations)
  - [Investments](#investments-investments)
  - [Contract Ledger](#contract-ledger-contract-ledger)
  - [Authorizations](#authorizations-authorizations)
  - [Competitor Rooms](#competitor-rooms-competitor-rooms)
  - [Traffic Analysis](#traffic-analysis-traffic-analysis)
  - [User Personas](#user-personas-user-personas)
  - [A/B Tests](#ab-tests-ab-tests)
  - [Data Warnings](#data-warnings-data-warnings)
  - [Settlements](#settlements-settlements)
  - [Logistics](#logistics-logistics)
  - [Inventories](#inventories-inventories)
  - [Return Analysis](#return-analysis-return-analysis)
  - [Tax Records](#tax-records-tax-records)

---

## General Conventions

### Authentication

The system supports both JWT Token and Django Session authentication. When using JWT, include the following in the request header:

```
Authorization: Bearer <access_token>
```

| Token Type | Validity |
|-----------|----------|
| Access Token | 12 hours |
| Refresh Token | 7 days |

### Request & Response

**Content-Type:** `application/json`

**List Response (Paginated):**

```json
{
  "count": 128,
  "next": "http://host/api/resource/?page=2",
  "previous": null,
  "results": [...]
}
```

**Single Item Response:**

```json
{
  "id": 1,
  "field_a": "value",
  "created_at": "2026-06-01T10:00:00+08:00"
}
```

**Error Response:**

```json
{
  "detail": "Error description message"
}
```

### HTTP Status Codes

| Status Code | Meaning |
|--------|------|
| 200 | Request successful |
| 201 | Created successfully |
| 400 | Bad request / Business validation failed |
| 401 | Not authenticated |
| 403 | Permission denied |
| 404 | Resource not found |
| 429 | Rate limit exceeded |

### Rate Limiting

Anonymous users: **100 requests/minute**. Exceeding this returns a 429 status code. Configurable in `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/min',
    },
}
```

### Performance Conventions

All API responses include the `X-Response-Time` response header (in milliseconds). Typical performance by endpoint:

| Endpoint | First Request | Cache Hit |
|------|------|----------|
| Dashboard Overview | ~10ms | ~2ms |
| Store Overview | ~5ms | ~2.5ms |
| AI Predict | ~6ms | ~2ms |
| AI Schedule | ~240ms | ~2.5ms |
| AI Insights | ~500ms | ~3ms |
| Health Check | ~1ms | -- |

---

## Core Modules

### Brand Management `brands`

Standard RESTful CRUD endpoints.

| Method | Path | Description |
|------|------|------|
| GET | `/api/brands/` | Brand list |
| POST | `/api/brands/` | Create brand |
| GET | `/api/brands/{id}/` | Brand detail |
| PUT | `/api/brands/{id}/` | Full update |
| DELETE | `/api/brands/{id}/` | Delete brand |

**Data Fields:**

| Field | Type | Required | Description |
|------|------|:----:|------|
| name | string | Yes | Brand name (unique) |
| industry | string | No | Industry |
| contact | string | No | Contact person |
| phone | string | No | Contact phone |
| logo | url | No | Brand logo URL |
| remark | string | No | Remarks |
| created_at | datetime | -- | Created timestamp (auto-generated) |

**Create Request Example:**

```json
{
  "name": "Florasis",
  "industry": "Beauty",
  "contact": "Manager Zhang",
  "phone": "13800001111",
  "logo": "https://cdn.example.com/brands/florasis.png"
}
```

**Response Example:**

```json
{
  "id": 1,
  "name": "Florasis",
  "industry": "Beauty",
  "contact": "Manager Zhang",
  "phone": "13800001111",
  "logo": "https://cdn.example.com/brands/florasis.png",
  "remark": "",
  "created_at": "2026-05-01T10:00:00+08:00"
}
```

---

### Store Management `stores`

| Method | Path | Description |
|------|------|------|
| GET | `/api/stores/` | Store list (with statistics) |
| POST | `/api/stores/` | Create store |
| GET | `/api/stores/{id}/` | Store detail |
| PUT | `/api/stores/{id}/` | Full update |
| DELETE | `/api/stores/{id}/` | Delete store |
| GET | `/api/stores/overview/` | Store operations overview |

**List Query Parameters:**

| Parameter | Type | Description |
|------|------|------|
| platform | string | Platform filter: `douyin` / `kuaishou` / `taobao` / `xiaohongshu` / `pdd` / `jd` / `video_account` |
| status | string | Status filter: `active` / `paused` / `closed` |
| brand_id | int | Filter by brand |
| kw | string | Fuzzy search by store name |

List response additionally includes `room_count` (number of live rooms) and `employee_count` (associated employees) aggregate fields.

**Store Operations Overview `overview`:**

Returns aggregated operational data for all stores, sorted by GMV descending, cached for 120 seconds.

```
GET /api/stores/overview/?start=2026-05-01&end=2026-05-31
```

```json
[
  {
    "id": 1,
    "name": "Florasis Douyin Flagship Store",
    "platform": "douyin",
    "status": "active",
    "monthly_target": "50.00",
    "monthly_gmv": 385000.00,
    "sessions_count": 45,
    "anchor_count": 3,
    "target_rate": 77.0
  }
]
```

**Create Request Example:**

```json
{
  "name": "Florasis Douyin Flagship Store",
  "platform": "douyin",
  "brand": 1,
  "store_url": "https://douyin.com/shop/xxx",
  "category": "Beauty",
  "monthly_target": "50.00",
  "status": "active"
}
```

---

### Team Management `teams`

| Method | Path | Description |
|------|------|------|
| GET | `/api/teams/` | Team list |
| POST | `/api/teams/` | Create team |
| GET | `/api/teams/{id}/` | Team detail |
| PUT | `/api/teams/{id}/` | Full update |
| DELETE | `/api/teams/{id}/` | Delete team |

List response additionally includes `member_count` (member count) aggregate field.

---

### Live Room Management `rooms`

| Method | Path | Description |
|------|------|------|
| GET | `/api/rooms/` | Live room list |
| POST | `/api/rooms/` | Create live room |
| GET | `/api/rooms/{id}/` | Live room detail |
| PUT | `/api/rooms/{id}/` | Full update |
| DELETE | `/api/rooms/{id}/` | Delete live room |

**Query Parameters:** `store_id` -- filter by parent store.

**Data Fields:**

| Field | Type | Required | Description |
|------|------|:----:|------|
| name | string | Yes | Live room name |
| store | int | Yes | Parent store ID |
| room_id | string | No | Platform room ID |
| is_active | boolean | No | Whether active (default true) |

---

### Employee Management `employees`

| Method | Path | Description |
|------|------|------|
| GET | `/api/employees/` | Employee list (with profiles) |
| POST | `/api/employees/` | Create employee |
| GET | `/api/employees/{id}/` | Employee detail |
| PUT | `/api/employees/{id}/` | Full update |
| DELETE | `/api/employees/{id}/` | Delete employee |
| GET | `/api/employees/stats/` | Employee statistics overview |

**List Query Parameters:**

| Parameter | Type | Description |
|------|------|------|
| role | string | Role filter: `admin` / `manager` / `operator` / `anchor` / `assistant` |
| store_id | int | Filter by assigned store |
| team_id | int | Filter by team |
| is_active | string | Active status: `true` / `false` |
| kw | string | Fuzzy search by name or phone number |

**Employee Statistics `stats`:**

```json
{
  "total": 42,
  "active": 38,
  "by_role": {
    "anchor": 15,
    "operator": 12,
    "manager": 5,
    "assistant": 4,
    "admin": 2
  }
}
```

**Create Request Example:**

```json
{
  "name": "Li Jiaqi",
  "role": "anchor",
  "phone": "13900001111",
  "team": 1,
  "stores": [1, 2],
  "base_salary": "15000.00",
  "join_date": "2026-01-15"
}
```

Response includes nested `anchor_profile` object (anchor-specific fields) and `store_names` array.

---

### Shift Management `shifts`

| Method | Path | Description |
|------|------|------|
| GET | `/api/shifts/` | Shift list |
| POST | `/api/shifts/` | Create shift |
| GET | `/api/shifts/{id}/` | Shift detail |
| PUT | `/api/shifts/{id}/` | Full update |
| DELETE | `/api/shifts/{id}/` | Delete shift |

**Data Fields:**

| Field | Type | Required | Description |
|------|------|:----:|------|
| name | string | Yes | Shift name |
| type | string | No | Shift type: `morning` / `afternoon` / `evening` / `night` / `custom` |
| start_time | time | Yes | Start time |
| end_time | time | Yes | End time |
| color | string | No | Frontend display color (default `#409EFF`) |
| description | string | No | Description |
| late_minutes | int | No | Late tolerance in minutes (default 10) |

Response additionally includes `type_display` and `time_range` fields.

---

### Schedule Management `schedules`

| Method | Path | Description |
|------|------|------|
| GET | `/api/schedules/` | Schedule list |
| POST | `/api/schedules/` | Create schedule (with validation) |
| GET | `/api/schedules/{id}/` | Schedule detail |
| PUT | `/api/schedules/{id}/` | Full update |
| DELETE | `/api/schedules/{id}/` | Delete schedule |
| GET | `/api/schedules/weekly/` | Weekly schedule view |
| POST | `/api/schedules/batch_create/` | Batch create |

**List Query Parameters:**

| Parameter | Type | Description |
|------|------|------|
| start | date | Start date (YYYY-MM-DD) |
| end | date | End date |
| store_id | int | Store filter |
| employee_id | int | Employee filter |
| role | string | Filter by employee role |
| status | string | Schedule status: `scheduled` / `checked_in` / `completed` / `cancelled` / `absent` |

**Create Schedule:**

Auto-validates on creation: duplicate schedule detection + time slot conflict detection. Returns 400 on validation failure.

```json
{
  "employee": 5,
  "shift": 1,
  "store": 1,
  "room": 1,
  "date": "2026-06-05",
  "note": "618 campaign prep"
}
```

**Weekly Schedule View `weekly`:**

```
GET /api/schedules/weekly/?start=2026-06-01
```

Returns all schedule data for the week containing the specified date (7 days total):

```json
{
  "start": "2026-06-01",
  "end": "2026-06-07",
  "items": [
    {
      "id": 1,
      "employee": 5,
      "employee_name": "Li Jiaqi",
      "employee_role": "anchor",
      "shift": 1,
      "shift_name": "Morning Shift",
      "shift_color": "#409EFF",
      "start_time": "08:00:00",
      "end_time": "14:00:00",
      "store": 1,
      "store_name": "Flagship Store",
      "room": 1,
      "room_name": "Studio 1",
      "date": "2026-06-01",
      "status": "scheduled",
      "status_display": "Scheduled",
      "note": ""
    }
  ]
}
```

**Batch Create `batch_create`:**

```
POST /api/schedules/batch_create/
```

Request body is an array format; each record is validated independently:

```json
[
  {"employee": 5, "shift": 1, "store": 1, "date": "2026-06-01"},
  {"employee": 6, "shift": 2, "store": 1, "date": "2026-06-01"},
  {"employee": 7, "shift": 1, "store": 2, "date": "2026-06-01"}
]
```

```json
{
  "created": [
    {"employee": 5, "shift": 1, "store": 1, "date": "2026-06-01", ...}
  ],
  "errors": [
    {"index": 1, "error": "This employee already has another schedule in this time slot, time conflict"}
  ]
}
```

---

### Attendance Management `attendances`

| Method | Path | Description |
|------|------|------|
| GET | `/api/attendances/` | Attendance record list |
| POST | `/api/attendances/clock_in/` | Clock in |
| POST | `/api/attendances/clock_out/` | Clock out |
| GET | `/api/attendances/summary/` | Attendance summary statistics |

**List Query Parameters:**

| Parameter | Type | Description |
|------|------|------|
| employee_id | int | Employee filter |
| start | date | Start date |
| end | date | End date |
| result | string | Attendance result: `normal` / `late` / `early` / `absent` / `leave` / `overtime` |

**Clock In `clock_in`:**

```json
{
  "employee_id": 5,
  "schedule_id": 12,
  "location": "HQ Building A",
  "photo": "https://cdn.example.com/clock_in.jpg"
}
```

Clock-in logic:
1. Match today's schedule via `schedule_id` or `employee_id`
2. Compare shift start time with clock-in time
3. If exceeding tolerance minutes (shift `late_minutes`), mark as `late`; otherwise `normal`
4. Automatically update schedule status to `checked_in`

**Clock Out `clock_out`:**

```json
{
  "employee_id": 5,
  "location": "HQ Building A",
  "photo": ""
}
```

Clock-out logic: If past shift end time, mark as `overtime`; otherwise `normal`. Also updates schedule status to `completed`.

**Attendance Summary `summary`:**

```
GET /api/attendances/summary/?start=2026-05-01&end=2026-05-31
```

```json
{
  "total": 320,
  "by_result": {
    "normal": 280,
    "late": 25,
    "early": 5,
    "absent": 3,
    "overtime": 7
  },
  "top_late": [
    {"employee_id": 5, "employee__name": "Zhang San", "late": 8, "normal": 22}
  ],
  "start": "2026-05-01",
  "end": "2026-05-31"
}
```

---

### Leave Management `leaves`

| Method | Path | Description |
|------|------|------|
| GET | `/api/leaves/` | Leave request list |
| POST | `/api/leaves/` | Create leave request |
| GET | `/api/leaves/{id}/` | Leave detail |
| PUT | `/api/leaves/{id}/` | Full update |
| DELETE | `/api/leaves/{id}/` | Delete leave request |
| POST | `/api/leaves/{id}/approve/` | Approve leave |
| POST | `/api/leaves/{id}/reject/` | Reject leave |

**Query Parameters:** `status` (`pending` / `approved` / `rejected`), `employee_id`

**Leave Types:** `personal` / `sick` / `annual` / `marriage` / `bereavement` / `maternity`

**Approve Leave:**

```json
{
  "approver": "Admin",
  "remark": "Approved, please rest well"
}
```

---

### Live Sessions `sessions`

| Method | Path | Description |
|------|------|------|
| GET | `/api/sessions/` | Live session list |
| POST | `/api/sessions/` | Create live session |
| GET | `/api/sessions/{id}/` | Session detail |
| PUT | `/api/sessions/{id}/` | Full update |
| DELETE | `/api/sessions/{id}/` | Delete live session |
| GET | `/api/sessions/daily_gmv/` | Daily GMV statistics |
| GET | `/api/sessions/top_anchors/` | Anchor GMV ranking |

**List Query Parameters:** `employee_id`, `store_id`, `start`, `end`

Response includes nested `products` array (product sales details for the session).

**Daily GMV `daily_gmv`:**

```
GET /api/sessions/daily_gmv/?start=2026-05-01&end=2026-05-31&store_id=1
```

```json
[
  {"d": "2026-05-01", "gmv": 58000.00, "orders": 230, "sessions": 3},
  {"d": "2026-05-02", "gmv": 62000.00, "orders": 255, "sessions": 4}
]
```

**Top Anchors `top_anchors`:**

```
GET /api/sessions/top_anchors/?start=2026-05-01&end=2026-05-31&limit=10
```

```json
[
  {
    "employee_id": 5,
    "employee__name": "Li Jiaqi",
    "gmv": 1280000.00,
    "orders": 5600,
    "hours": 7200,
    "sessions": 28
  }
]
```

---

### Product Sales `product-sales`

Standard CRUD, associated with live sessions.

| Method | Path | Description |
|------|------|------|
| GET | `/api/product-sales/` | Sales detail list |
| POST | `/api/product-sales/` | Create sales record |
| GET | `/api/product-sales/{id}/` | Sales detail |
| PUT | `/api/product-sales/{id}/` | Full update |
| DELETE | `/api/product-sales/{id}/` | Delete sales record |

**Data Fields:** `session` (live session ID), `product_name`, `sku`, `price`, `quantity`, `gmv`, `commission`

---

### KPI Configuration `kpi-configs`

| Method | Path | Description |
|------|------|------|
| GET | `/api/kpi-configs/` | KPI configuration list |
| POST | `/api/kpi-configs/` | Create configuration |
| GET | `/api/kpi-configs/{id}/` | Configuration detail |
| PUT | `/api/kpi-configs/{id}/` | Full update |
| DELETE | `/api/kpi-configs/{id}/` | Delete configuration |

**Metric Types:** `gmv` / `orders` / `hours` / `followers` / `conversion` / `attendance`

---

### Performance Reviews `reviews`

| Method | Path | Description |
|------|------|------|
| GET | `/api/reviews/` | Review list |
| POST | `/api/reviews/calculate/` | Auto-calculate review |

**Query Parameters:** `period` (e.g., `2026-06`), `employee_id`, `role`, `level` (S/A/B/C/D)

**Auto-Calculate `calculate`:**

```json
{
  "employee_id": 5,
  "period": "2026-05"
}
```

Scoring formula: GMV completion rate x 60% + Attendance rate x 20% + Live streaming hours x 10% + Order count x 10% = Overall score

| Score Range | Grade |
|---------|------|
| >= 90 | S (Excellent) |
| >= 80 | A (Good) |
| >= 60 | B (Satisfactory) |
| >= 40 | C (Needs Improvement) |
| < 40 | D (Unsatisfactory) |

Performance bonus = `max(0, (score - 60) / 40) x base_salary` (only scores above 60 receive bonus)

---

### Dashboard `dashboard`

| Method | Path | Description |
|------|------|------|
| GET | `/api/dashboard/overview/` | Dashboard overview |

Cached for 60 seconds. Response structure:

```json
{
  "store_total": 8,
  "anchor_total": 15,
  "operator_total": 17,
  "monthly_gmv": 3850000.00,
  "monthly_orders": 15200,
  "monthly_sessions": 320,
  "today_gmv": 128000.00,
  "today_orders": 520,
  "today_schedules": 12,
  "today_attended": 10,
  "attendance_rate": 83.33,
  "pending_leave": 3,
  "trend_7d": [
    {"d": "2026-05-30", "gmv": 98000.00, "orders": 380}
  ],
  "platform_dist": [
    {"platform": "douyin", "gmv": 2500000.00, "sessions": 200}
  ],
  "top_anchors": [
    {"employee_id": 5, "employee__name": "Li Jiaqi", "gmv": 580000.00, "sessions": 12}
  ]
}
```

---

## AI Module

All AI endpoints are registered under the `/api/ai/` path, using GET method. Results are cached for 120-180 seconds based on parameter hash.

| Path | Description | Key Parameters | Cache |
|------|------|----------|------|
| `/api/ai/predict/` | GMV prediction | `days` (1-30), `store_id`, `employee_id` | 120s |
| `/api/ai/schedule/` | Smart scheduling recommendation | `date` (YYYY-MM-DD), `store_id` | 120s |
| `/api/ai/anchor/` | Anchor profile analysis | `employee_id` (required) | 180s |
| `/api/ai/anomaly/` | Anomaly data detection | `days` (1-30) | 120s |
| `/api/ai/insights/` | Operations insight engine | No parameters | 120s |
| `/api/ai/match/` | Anchor-store matching | `store_id` | 180s |

For algorithm details, formula derivations, and full response structures, see the [AI Engine Document](ai-engine.md).

---

## Extended Modules

### Products & Inventory

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/product-categories/` | Product category CRUD |
| GET/POST | `/api/products/` | Product CRUD |
| GET | `/api/products/low_stock/` | Low stock product list |
| GET/POST | `/api/inventory-alerts/` | Inventory alert rules CRUD |
| GET | `/api/inventory-alerts/triggered/` | Triggered alerts list |

**Product Query Parameters:** `status` (active/inactive/draft), `category_id`, `kw` (name or SKU search)

**Low Stock Products:** Returns products with stock <= 10 and status `active`.

**Triggered Alerts:** Iterates all enabled alert rules and returns products with current stock <= threshold:

```json
[
  {
    "id": 1,
    "product_id": 15,
    "product_name": "Florasis Loose Powder",
    "stock": 3,
    "threshold": 10
  }
]
```

---

### Live Streaming Tools

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/stream-scripts/` | Live script CRUD |
| GET/POST | `/api/script-segments/` | Script segment CRUD |
| GET/POST | `/api/sales-scripts/` | Sales pitch template CRUD |
| GET/POST | `/api/stream-reviews/` | Live stream review CRUD |

**Script Query Parameters:** `store_id`, `status` (draft/active/archived)

**Sales Pitch Query Parameters:** `scene`, `kw`

**Segment Types:** `warmup` / `product` / `interaction` / `promotion` / `flash_sale` / `closing`

**Pitch Scenes:** `opening` / `product_intro` / `objection` / `closing` / `follow_up` / `interaction` / `flash_sale`

**Script Response Example:**

```json
{
  "id": 1,
  "title": "618 Campaign Live Script",
  "store": 1,
  "store_name": "Flagship Store",
  "status": "active",
  "status_display": "In Use",
  "duration_minutes": 180,
  "creator": 3,
  "creator_name": "Operator Wang",
  "segment_count": 8,
  "segments": [
    {
      "id": 1,
      "order": 1,
      "segment_type": "warmup",
      "segment_type_display": "Warm-up",
      "title": "Opening Warm-up",
      "duration_minutes": 10,
      "product": null,
      "product_name": "",
      "talking_points": "Interactive engagement to build atmosphere"
    }
  ]
}
```

---

### Task Board

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/task-boards/` | Board CRUD (with nested cards) |
| GET/POST | `/api/task-cards/` | Task card CRUD |
| POST | `/api/task-cards/{id}/move/` | Move card status |

**Move Card:**

```json
{
  "status": "doing"
}
```

Card status flow: `todo` --> `doing` --> `done`, or mark as `blocked`.

Board response includes nested `cards` array and `card_count` statistics field.

---

### Notification Center

| Method | Path | Description |
|------|------|------|
| GET | `/api/notifications/` | Notification list |
| POST | `/api/notifications/read_all/` | Mark all as read |
| GET | `/api/notifications/unread_count/` | Unread notification count |

**Query Parameters:** `target_id` (recipient), `is_read` (true/false), `type`

**Notification Types:** `system` / `schedule` / `attendance` / `performance` / `leave` / `alert` / `contract` / `task`

**Mark All Read:**

```json
{ "target_id": 5 }
```

Returns: `{"updated": 12}`

**Unread Count:**

```
GET /api/notifications/unread_count/?target_id=5
```

Returns: `{"count": 8}`

---

### Finance Center

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/finance/` | Finance record CRUD |
| GET | `/api/finance/summary/` | Finance summary |

**Query Parameters:** `start`, `end`, `type` (income/expense), `category`, `store_id`

**Finance Categories:** `gmv` / `commission` / `salary` / `bonus` / `equipment` / `ads` / `logistics` / `other`

**Finance Summary:**

```
GET /api/finance/summary/?start=2026-05-01&end=2026-05-31&store_id=1
```

```json
{
  "income": 3850000.00,
  "expense": 1280000.00,
  "profit": 2570000.00,
  "by_category": [
    {"type": "income", "category": "gmv", "total": 3200000.00},
    {"type": "expense", "category": "salary", "total": 580000.00}
  ]
}
```

---

### Commission Management

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/commission-rules/` | Commission rules CRUD |
| GET | `/api/commissions/` | Commission record list |
| POST | `/api/commissions/{id}/settle/` | Settle commission |

**Query Parameters (commission records):** `period`, `status` (pending/settled/cancelled), `employee_id`

**Commission Rule Calculation Method:** `fixed` (fixed amount) / `percent` (percentage)

After settlement, `settled_at` timestamp is automatically recorded.

---

### Contract Management

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/contracts/` | Contract CRUD |
| GET | `/api/contracts/expiring/` | Soon-to-expire contracts |

**Query Parameters:** `status`, `employee_id`, `contract_type`

**Contract Types:** `labor` / `service` / `anchor` / `brand`

**Contract Status:** `active` / `expiring` / `expired` / `terminated`

**Expiring Contracts:**

```
GET /api/contracts/expiring/?days=30
```

Returns all active contracts expiring within the specified number of days.

---

### Training Management

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/training-courses/` | Course CRUD |
| GET/POST | `/api/training-records/` | Training record CRUD |

**Query Parameters (courses):** `status` (draft/active/completed), `category`

Course response includes nested `records` array (student training records).

---

### Competitor Analysis

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/competitors/` | Competitor info CRUD |
| GET/POST | `/api/competitor-data/` | Competitor data tracking CRUD |

Competitor response includes nested `data` array (historical tracking data).

---

### Fan Analysis

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/fan-analysis/` | Fan data CRUD |
| GET | `/api/fan-analysis/trend/` | Fan trend |

**Query Parameters:** `store_id`, `start`, `end`

**Fan Trend:**

```
GET /api/fan-analysis/trend/?store_id=1&days=30
```

```json
[
  {
    "date": "2026-05-01",
    "total_fans": 120000,
    "new_fans": 3500,
    "lost_fans": 200,
    "engagement_rate": "4.50"
  }
]
```

---

### Marketing Campaigns

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/campaigns/` | Campaign CRUD |

**Query Parameters:** `status` (draft/active/completed/cancelled), `store_id`, `campaign_type`

**Campaign Types:** `flash_sale` / `coupon` / `gift` / `discount` / `live_debut` / `festival`

Response includes computed field `completion_rate` (actual GMV / target GMV x 100).

---

### Goal Management

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/goals/` | Goal CRUD |
| GET | `/api/goals/board/` | Goal board summary |

**Query Parameters:** `period`, `employee_id`, `status`, `store_id`

**Goal Periods:** `weekly` / `monthly` / `quarterly` / `yearly`

**Goal Board:**

```
GET /api/goals/board/?period=2026-06
```

```json
{
  "goals": [...],
  "summary": {
    "total_target": 500000.00,
    "total_actual": 380000.00,
    "count": 15,
    "completed": 8
  }
}
```

---

### Operation Logs

| Method | Path | Description |
|------|------|------|
| GET | `/api/operation-logs/` | Log list (read-only) |

**Query Parameters:** `user`, `action`, `model_name`

The system retains the most recent 500 operation logs, with a maximum of 200 records per query.

---

### Billboard / Live Screen

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/billboard/` | Billboard configuration CRUD |
| GET | `/api/billboard/data/` | Billboard real-time data |

The `data` endpoint returns the same data structure as Dashboard Overview. `refresh_interval` can be configured for frontend polling.

---

### Permission Management

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/roles/` | Role management CRUD |
| GET/POST | `/api/user-roles/` | User-role binding CRUD |

The `permissions` field of a role is a JSON array, for example:

```json
{
  "name": "Operations Manager",
  "description": "Store and schedule management permissions",
  "permissions": ["store:view", "store:edit", "schedule:view", "schedule:edit"]
}
```

Role response includes `member_count` statistics field.

---

### KOL / Influencer Management

| Method | Path | Description |
|------|------|------|
| GET/POST | `/api/kols/` | KOL resource management CRUD |

**Query Parameters:** `status`, `platform`, `kw` (name or domain search)

**KOL Status:** `contacting` / `negotiating` / `cooperating` / `completed`

**KOL Platforms:** `douyin` / `kuaishou` / `xiaohongshu` / `weibo`

---

### Data Export

| Method | Path | Description |
|------|------|------|
| GET | `/api/exports/` | Export task list |
| POST | `/api/exports/create_export/` | Create and execute export |

**Create Export:**

```json
{
  "export_type": "sessions",
  "params": {
    "start": "2026-05-01",
    "end": "2026-05-31"
  },
  "creator": "admin"
}
```

**Supported Export Types:**

| Type | Description | Export Fields |
|------|------|---------|
| `sessions` | Live session records | Date, anchor, store, GMV, orders, duration, peak viewers, conversion rate |
| `attendance` | Attendance records | Employee, clock type, clock time, result, late minutes |
| `finance` | Finance records | Date, type, category, amount, store, remarks |

**Response:**

```json
{
  "id": 1,
  "name": "sessions_export_20260605120000",
  "export_type": "sessions",
  "status": "done",
  "status_display": "Completed",
  "file_url": "/media/exports/1.csv",
  "file_size": 15234,
  "row_count": 200,
  "csv_content": "Date,Anchor,Store,GMV,Orders,Duration(min),Peak Viewers,Conversion Rate\n..."
}
```

Maximum 5000 rows per export.

---

## 4th Round Extension Modules

The following 20 API endpoint groups were introduced in the 4th development round. Each provides standard CRUD operations plus custom actions as noted.

### Live Interactions `live-interactions`

Manages real-time interaction events during live streams (polls, Q&A, lucky draws, etc.).

| Method | Path | Description |
|------|------|------|
| GET | `/api/live-interactions/` | List live interactions |
| POST | `/api/live-interactions/` | Create interaction |
| GET | `/api/live-interactions/{id}/` | Interaction detail |
| PUT | `/api/live-interactions/{id}/` | Full update |
| DELETE | `/api/live-interactions/{id}/` | Delete interaction |
| GET | `/api/live-interactions/stats/` | Interaction statistics |
| POST | `/api/live-interactions/{id}/toggle/` | Enable/disable interaction |

**Data Fields:** `session` (live session ID), `type` (poll / qa / lucky_draw / quiz), `title`, `config` (JSON), `is_active`, `start_time`, `end_time`

---

### Coupons `coupons`

Coupon management for live stream promotions.

| Method | Path | Description |
|------|------|------|
| GET | `/api/coupons/` | List coupons |
| POST | `/api/coupons/` | Create coupon |
| GET | `/api/coupons/{id}/` | Coupon detail |
| PUT | `/api/coupons/{id}/` | Full update |
| DELETE | `/api/coupons/{id}/` | Delete coupon |
| GET | `/api/coupons/stats/` | Coupon usage statistics |
| POST | `/api/coupons/{id}/toggle/` | Enable/disable coupon |

**Data Fields:** `code`, `type` (percent / fixed), `value`, `min_purchase`, `max_uses`, `used_count`, `valid_from`, `valid_to`, `store`, `is_active`

---

### Flash Sales `flash-sales`

Time-limited promotional sales events during live streams.

| Method | Path | Description |
|------|------|------|
| GET | `/api/flash-sales/` | List flash sales |
| POST | `/api/flash-sales/` | Create flash sale |
| GET | `/api/flash-sales/{id}/` | Flash sale detail |
| PUT | `/api/flash-sales/{id}/` | Full update |
| DELETE | `/api/flash-sales/{id}/` | Delete flash sale |
| GET | `/api/flash-sales/stats/` | Flash sale statistics |
| POST | `/api/flash-sales/{id}/toggle/` | Activate/deactivate flash sale |

**Data Fields:** `product`, `original_price`, `sale_price`, `stock_limit`, `sold_count`, `start_time`, `end_time`, `session`, `is_active`

---

### Room Decorations `room-decorations`

Virtual room decoration and background management for live streams.

| Method | Path | Description |
|------|------|------|
| GET | `/api/room-decorations/` | List room decorations |
| POST | `/api/room-decorations/` | Create decoration |
| GET | `/api/room-decorations/{id}/` | Decoration detail |
| PUT | `/api/room-decorations/{id}/` | Full update |
| DELETE | `/api/room-decorations/{id}/` | Delete decoration |
| GET | `/api/room-decorations/stats/` | Decoration usage statistics |
| POST | `/api/room-decorations/{id}/toggle/` | Show/hide decoration |

**Data Fields:** `room`, `type` (background / overlay / badge / banner), `name`, `image_url`, `config` (JSON), `is_active`, `valid_from`, `valid_to`

---

### Script Tags `script-tags`

Tagging and categorization system for live stream scripts.

| Method | Path | Description |
|------|------|------|
| GET | `/api/script-tags/` | List script tags |
| POST | `/api/script-tags/` | Create tag |
| GET | `/api/script-tags/{id}/` | Tag detail |
| PUT | `/api/script-tags/{id}/` | Full update |
| DELETE | `/api/script-tags/{id}/` | Delete tag |
| GET | `/api/script-tags/stats/` | Tag usage statistics |

**Data Fields:** `name`, `color`, `category` (topic / style / season / campaign), `usage_count`

---

### Sign Contracts `sign-contracts`

Digital contract signing workflow management.

| Method | Path | Description |
|------|------|------|
| GET | `/api/sign-contracts/` | List sign contracts |
| POST | `/api/sign-contracts/` | Create sign contract |
| GET | `/api/sign-contracts/{id}/` | Sign contract detail |
| PUT | `/api/sign-contracts/{id}/` | Full update |
| DELETE | `/api/sign-contracts/{id}/` | Delete sign contract |
| GET | `/api/sign-contracts/stats/` | Contract statistics |
| POST | `/api/sign-contracts/{id}/approve/` | Approve contract |
| POST | `/api/sign-contracts/{id}/reject/` | Reject contract |
| POST | `/api/sign-contracts/{id}/sign/` | Sign contract |

**Data Fields:** `title`, `party_a`, `party_b`, `contract_type`, `amount`, `status` (draft / pending / approved / rejected / signed / expired), `valid_from`, `valid_to`, `attachment`

---

### Negotiations `negotiations`

KOL/partner negotiation tracking and management.

| Method | Path | Description |
|------|------|------|
| GET | `/api/negotiations/` | List negotiations |
| POST | `/api/negotiations/` | Create negotiation |
| GET | `/api/negotiations/{id}/` | Negotiation detail |
| PUT | `/api/negotiations/{id}/` | Full update |
| DELETE | `/api/negotiations/{id}/` | Delete negotiation |
| GET | `/api/negotiations/stats/` | Negotiation statistics |
| POST | `/api/negotiations/{id}/approve/` | Approve negotiation |
| POST | `/api/negotiations/{id}/reject/` | Reject negotiation |

**Data Fields:** `kol`, `store`, `type` (brand_deal / commission / exclusive), `status` (initiated / in_progress / approved / rejected / completed), `proposed_terms` (JSON), `final_terms` (JSON), `notes`

---

### Investments `investments`

Investment and funding tracking for MCN operations.

| Method | Path | Description |
|------|------|------|
| GET | `/api/investments/` | List investments |
| POST | `/api/investments/` | Create investment |
| GET | `/api/investments/{id}/` | Investment detail |
| PUT | `/api/investments/{id}/` | Full update |
| DELETE | `/api/investments/{id}/` | Delete investment |
| GET | `/api/investments/stats/` | Investment statistics |
| POST | `/api/investments/{id}/approve/` | Approve investment |
| POST | `/api/investments/{id}/reject/` | Reject investment |

**Data Fields:** `title`, `type` (equipment / marketing / talent / r_and_d), `amount`, `status` (proposed / approved / rejected / disbursed / completed), `roi_target`, `actual_roi`, `requestor`, `approver`, `disbursed_at`

---

### Contract Ledger `contract-ledger`

Financial ledger entries associated with contracts.

| Method | Path | Description |
|------|------|------|
| GET | `/api/contract-ledger/` | List ledger entries |
| POST | `/api/contract-ledger/` | Create ledger entry |
| GET | `/api/contract-ledger/{id}/` | Ledger entry detail |
| PUT | `/api/contract-ledger/{id}/` | Full update |
| DELETE | `/api/contract-ledger/{id}/` | Delete ledger entry |
| GET | `/api/contract-ledger/stats/` | Ledger statistics |

**Data Fields:** `contract`, `type` (receivable / payable / settlement / adjustment), `amount`, `balance`, `due_date`, `settled_date`, `status` (pending / partial / settled), `description`

---

### Authorizations `authorizations`

Authorization and access delegation management for third-party services and platforms.

| Method | Path | Description |
|------|------|------|
| GET | `/api/authorizations/` | List authorizations |
| POST | `/api/authorizations/` | Create authorization |
| GET | `/api/authorizations/{id}/` | Authorization detail |
| PUT | `/api/authorizations/{id}/` | Full update |
| DELETE | `/api/authorizations/{id}/` | Delete authorization |
| GET | `/api/authorizations/stats/` | Authorization statistics |
| POST | `/api/authorizations/{id}/approve/` | Approve authorization |
| POST | `/api/authorizations/{id}/revoke/` | Revoke authorization |

**Data Fields:** `platform`, `account_name`, `auth_type` (oauth / api_key / token), `scope` (JSON), `status` (pending / active / revoked / expired), `granted_at`, `expires_at`, `store`

---

### Competitor Rooms `competitor-rooms`

Monitoring and tracking of competitor live rooms.

| Method | Path | Description |
|------|------|------|
| GET | `/api/competitor-rooms/` | List competitor rooms |
| POST | `/api/competitor-rooms/` | Create competitor room |
| GET | `/api/competitor-rooms/{id}/` | Competitor room detail |
| PUT | `/api/competitor-rooms/{id}/` | Full update |
| DELETE | `/api/competitor-rooms/{id}/` | Delete competitor room |
| GET | `/api/competitor-rooms/stats/` | Competitor room statistics |

**Data Fields:** `competitor`, `room_id`, `platform`, `room_name`, `avg_viewers`, `peak_viewers`, `avg_gmv`, `live_frequency`, `last_tracked`

---

### Traffic Analysis `traffic-analysis`

Traffic source and funnel analysis for live streams.

| Method | Path | Description |
|------|------|------|
| GET | `/api/traffic-analysis/` | List traffic analysis records |
| POST | `/api/traffic-analysis/` | Create traffic analysis record |
| GET | `/api/traffic-analysis/{id}/` | Record detail |
| PUT | `/api/traffic-analysis/{id}/` | Full update |
| DELETE | `/api/traffic-analysis/{id}/` | Delete record |
| GET | `/api/traffic-analysis/stats/` | Traffic statistics |

**Data Fields:** `session`, `source` (organic / paid / referral / recommendation / search), `views`, `clicks`, `ctr`, `conversions`, `conversion_rate`, `cost`, `date`

---

### User Personas `user-personas`

Audience/user persona analysis and segmentation.

| Method | Path | Description |
|------|------|------|
| GET | `/api/user-personas/` | List user personas |
| POST | `/api/user-personas/` | Create user persona |
| GET | `/api/user-personas/{id}/` | Persona detail |
| PUT | `/api/user-personas/{id}/` | Full update |
| DELETE | `/api/user-personas/{id}/` | Delete persona |
| GET | `/api/user-personas/stats/` | Persona statistics |

**Data Fields:** `store`, `segment_name`, `age_range`, `gender_ratio` (JSON), `top_cities` (JSON), `avg_order_value`, `preferences` (JSON), `size`, `engagement_score`

---

### A/B Tests `ab-tests`

A/B testing framework for live stream content and strategies.

| Method | Path | Description |
|------|------|------|
| GET | `/api/ab-tests/` | List A/B tests |
| POST | `/api/ab-tests/` | Create A/B test |
| GET | `/api/ab-tests/{id}/` | A/B test detail |
| PUT | `/api/ab-tests/{id}/` | Full update |
| DELETE | `/api/ab-tests/{id}/` | Delete A/B test |
| GET | `/api/ab-tests/stats/` | A/B test statistics |
| POST | `/api/ab-tests/{id}/toggle/` | Start/stop test |
| POST | `/api/ab-tests/{id}/resolve/` | Resolve and pick winner |

**Data Fields:** `name`, `type` (script / thumbnail / timing / product_layout), `variant_a` (JSON), `variant_b` (JSON), `metric` (gmv / conversion / viewers / engagement), `status` (draft / running / paused / completed), `winner`, `start_date`, `end_date`, `store`

---

### Data Warnings `data-warnings`

Automated data anomaly warning and alerting system.

| Method | Path | Description |
|------|------|------|
| GET | `/api/data-warnings/` | List data warnings |
| POST | `/api/data-warnings/` | Create data warning |
| GET | `/api/data-warnings/{id}/` | Warning detail |
| PUT | `/api/data-warnings/{id}/` | Full update |
| DELETE | `/api/data-warnings/{id}/` | Delete warning |
| GET | `/api/data-warnings/stats/` | Warning statistics |
| POST | `/api/data-warnings/{id}/resolve/` | Resolve warning |
| POST | `/api/data-warnings/{id}/toggle/` | Enable/disable warning rule |

**Data Fields:** `name`, `metric` (gmv / conversion / viewers / orders / attendance), `condition` (below / above / change_rate), `threshold`, `period` (1h / 6h / 24h / 7d), `severity` (info / warning / critical), `status` (active / triggered / resolved / disabled), `store`, `last_triggered`

---

### Settlements `settlements`

Financial settlement and payout management.

| Method | Path | Description |
|------|------|------|
| GET | `/api/settlements/` | List settlements |
| POST | `/api/settlements/` | Create settlement |
| GET | `/api/settlements/{id}/` | Settlement detail |
| PUT | `/api/settlements/{id}/` | Full update |
| DELETE | `/api/settlements/{id}/` | Delete settlement |
| GET | `/api/settlements/stats/` | Settlement statistics |
| POST | `/api/settlements/{id}/approve/` | Approve settlement |
| POST | `/api/settlements/{id}/pay/` | Execute payment |

**Data Fields:** `contract`, `employee`, `type` (salary / commission / bonus / reimbursement), `amount`, `period`, `status` (pending / approved / paid / cancelled), `approved_by`, `paid_at`, `payment_method`, `reference_number`

---

### Logistics `logistics`

Shipping and delivery tracking for orders placed during live streams.

| Method | Path | Description |
|------|------|------|
| GET | `/api/logistics/` | List logistics records |
| POST | `/api/logistics/` | Create logistics record |
| GET | `/api/logistics/{id}/` | Logistics detail |
| PUT | `/api/logistics/{id}/` | Full update |
| DELETE | `/api/logistics/{id}/` | Delete logistics record |
| GET | `/api/logistics/stats/` | Logistics statistics |
| POST | `/api/logistics/{id}/ship/` | Mark as shipped |
| POST | `/api/logistics/{id}/deliver/` | Mark as delivered |

**Data Fields:** `order_id`, `carrier`, `tracking_number`, `status` (pending / shipped / in_transit / delivered / failed), `shipped_at`, `delivered_at`, `origin`, `destination`, `estimated_delivery`, `store`

---

### Inventories `inventories`

Warehouse and multi-location inventory management.

| Method | Path | Description |
|------|------|------|
| GET | `/api/inventories/` | List inventory records |
| POST | `/api/inventories/` | Create inventory record |
| GET | `/api/inventories/{id}/` | Inventory detail |
| PUT | `/api/inventories/{id}/` | Full update |
| DELETE | `/api/inventories/{id}/` | Delete inventory record |
| GET | `/api/inventories/stats/` | Inventory statistics |

**Data Fields:** `product`, `warehouse`, `quantity`, `reserved`, `available`, `cost_price`, `last_restocked`, `min_stock`, `max_stock`

---

### Return Analysis `return-analysis`

Product return tracking, analysis, and management.

| Method | Path | Description |
|------|------|------|
| GET | `/api/return-analysis/` | List return records |
| POST | `/api/return-analysis/` | Create return record |
| GET | `/api/return-analysis/{id}/` | Return detail |
| PUT | `/api/return-analysis/{id}/` | Full update |
| DELETE | `/api/return-analysis/{id}/` | Delete return record |
| GET | `/api/return-analysis/stats/` | Return statistics |
| POST | `/api/return-analysis/{id}/resolve/` | Resolve return |
| POST | `/api/return-analysis/{id}/approve/` | Approve return |

**Data Fields:** `order_id`, `product`, `quantity`, `reason` (defective / wrong_item / not_as_described / changed_mind / other), `status` (requested / approved / rejected / processing / refunded / resolved), `refund_amount`, `store`, `session`, `resolution_notes`, `resolved_at`

---

### Tax Records `tax-records`

Tax filing and record management for financial compliance.

| Method | Path | Description |
|------|------|------|
| GET | `/api/tax-records/` | List tax records |
| POST | `/api/tax-records/` | Create tax record |
| GET | `/api/tax-records/{id}/` | Tax record detail |
| PUT | `/api/tax-records/{id}/` | Full update |
| DELETE | `/api/tax-records/{id}/` | Delete tax record |
| GET | `/api/tax-records/stats/` | Tax statistics |
| POST | `/api/tax-records/{id}/approve/` | Approve tax record |
| POST | `/api/tax-records/{id}/pay/` | Mark tax as paid |

**Data Fields:** `type` (vat / income / withholding / stamp / other), `period`, `amount`, `tax_base`, `rate`, `status` (pending / approved / paid / filed), `due_date`, `paid_date`, `store`, `filing_number`, `notes`
