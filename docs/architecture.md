# System Architecture

> MCN Manager technical architecture design philosophy: **Layered Decoupling · Cache-Driven · AI Built-In · Progressive Enhancement**

---

## Design Philosophy

| Principle | Practice |
|-----------|----------|
| Layered Decoupling | View -> Service -> Model three-tier architecture |
| Cache-Driven | Read cache + write invalidation, hot endpoints respond in 2ms |
| AI Built-In | Pure algorithm engine, no external API dependencies |
| Progressive Enhancement | SQLite -> PostgreSQL, LocMem -> Redis, standalone -> distributed |

---

## System Layers

```
+----------------------------------------------------+
|                   Frontend Layer                     |
|                                                     |
|  Vue 3 SPA · Vue Router · Pinia · Element Plus     |
|  ECharts (Tree-shaking) · Axios · Vite Build        |
|                                                     |
|  21 Pages · defineAsyncComponent Lazy Loading       |
|  3 Components · 2 Composables · 1 Store             |
|  Dark Neon Design System · CSS Variables Theme      |
+----------------------------------------------------+
|                   Gateway Layer                      |
|                                                     |
|  Vite Dev Proxy -> Waitress -> Django WSGI          |
|  JWT Authentication · Session Authentication        |
|  CORS · AnonRateThrottle 100/min                    |
|  RequestTimingMiddleware -> X-Response-Time         |
|  HealthCheckMiddleware -> /api/health/              |
+----------------------------------------------------+
|                 Service Layer                        |
|                                                     |
|  DashboardService · StoreService · EmployeeService  |
|  ScheduleService · AttendanceService                |
|  PerformanceService · LiveSessionService            |
|                                                     |
|  cached_result() Decorator -> MD5 Key -> TTL Cache  |
|  invalidate_cache() -> Auto-Clear on Write          |
+----------------------------------------------------+
|                 AI Engine Layer                      |
|                                                     |
|  GMVPredictor      Linear Regression + MA + Season  |
|  SmartScheduler    Greedy Match + Fatigue/Penalty   |
|  AnchorProfiler    5-Dim Radar + Z-Score + Insights |
|  AnomalyDetector   Z-Score + Rule Engine            |
|  InsightEngine     Multi-Dim Operation Suggestions  |
|  AnchorMatcher     Multi-Factor Composite Scoring   |
|                                                     |
|  All AI Results Cacheable (120-180s)                |
+----------------------------------------------------+
|                   Data Layer                         |
|                                                     |
|  83 Models · 20+ Indexes · SQLite WAL               |
|  select_related · prefetch_related · annotate       |
|  PRAGMA: WAL · cache 64MB · mmap 256MB              |
|  Connection signal: journal_mode=WAL on conn_created|
+----------------------------------------------------+
```

---

## Request Lifecycle

```
Browser Request
    |
    v
Vite Dev Proxy (/api -> :8000)
    |
    v
Waitress WSGI Server
    |
    v
SecurityMiddleware -> CorsMiddleware -> SessionMiddleware -> ...
RequestTimingMiddleware (timing starts)
HealthCheckMiddleware (/api/health/ short-circuit return)
    |
    v
JWT Authentication / Session Authentication
    |
    v
Router -> ViewSet
    |
    +-- Read: Service.cached_result() -> Cache Hit -> Return Directly
    |                       | Cache Miss
    |                       v
    |              ORM Query (select_related/prefetch_related)
    |                       |
    |                       v
    |              Cache Set -> Response
    |
    +-- Write: Model.save() -> invalidate_cache() -> Response
    |
    v
RequestTimingMiddleware (adds X-Response-Time header)
    |
    v
JSON Response -> Browser
```

---

## Cache Strategy

### Cache Tiers

| Tier | Technology | TTL | Purpose |
|-----|-----------|-----|---------|
| Backend | LocMemCache / Redis | 60-300s | API response cache |
| AI | LocMemCache / Redis | 120-180s | AI computation results |
| Frontend | Pinia Store | 30s | Dashboard data |

### Cache Invalidation

Write operations (create/update/destroy) trigger `invalidate_cache()`:

```python
def perform_create(self, serializer):
    super().perform_create(serializer)
    invalidate_cache('store_overview', 'dashboard')  # Clear related caches
```

### Cache Key Generation

```python
key = f'{prefix}:{md5(json.dumps(kwargs, sort_keys=True))}'
```

---

## Database Optimization

### SQLite WAL Mode

```python
# settings.py - connection_created signal
PRAGMA journal_mode=WAL        # Concurrent read/write
PRAGMA synchronous=NORMAL      # Safety + performance balance
PRAGMA cache_size=-64000       # 64MB page cache
PRAGMA temp_store=MEMORY       # Temp tables in memory
PRAGMA mmap_size=268435456     # 256MB memory-mapped I/O
```

### Index Strategy

| Query Pattern | Indexes |
|--------------|---------|
| Store Filter | (platform), (status), (brand) |
| Schedule Query | (date, employee), (date, store), (date, status), (employee, date, shift) |
| Attendance Query | (employee, check_time), (result) |
| Live Session Query | (employee, date), (store, date), (date) |
| Leave Approval | (status), (employee) |
| Performance Review | (period), (level) |

### Query Optimization

```python
# Avoid N+1: Use select_related + prefetch_related
queryset = LiveSession.objects.select_related(
    'employee', 'store', 'room'
).prefetch_related('products')

# Avoid N+1: Use annotate instead of SerializerMethodField
queryset = Store.objects.annotate(
    _room_count=Count('rooms', distinct=True),
    _employee_count=Count('employees', distinct=True),
)

# Bulk aggregation: Replace Python loops
gmv_by_store = dict(
    LiveSession.objects.filter(store_id__in=store_ids)
    .values('store_id').annotate(total_gmv=Sum('gmv'))
    .values_list('store_id', 'total_gmv')
)
```

---

## Frontend Build Optimization

### Tree-shaking

```javascript
// echarts.js - Only import needed components
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
```

### Code-splitting

```javascript
// router/index.js - All pages lazy-loaded
{ path: '/ai', component: () => import('../views/AI.vue') }

// vite.config.js - Chunk splitting
manualChunks: {
  'element-plus': ['element-plus'],
  'echarts': ['echarts'],
  'vendor': ['vue', 'axios']
}
```

### On-Demand Import

```javascript
// vite.config.js - Element Plus on-demand auto-import
AutoImport({ resolvers: [ElementPlusResolver()] })
Components({ resolvers: [ElementPlusResolver()] })
```

---

## Production Upgrade Path

| Component | Development | Production |
|-----------|------------|------------|
| Database | SQLite WAL | PostgreSQL |
| Cache | LocMemCache | Redis |
| WSGI | Waitress | Gunicorn + Nginx |
| Frontend | Vite Dev Server | Nginx Static Files |
| Auth | AllowAny | JWT + RBAC |

Switching to PostgreSQL only requires changing the `DATABASES` configuration in `settings.py`; Django ORM adapts automatically.
