# 系统架构

> MCN 管家的技术架构设计哲学：**分层解耦 · 缓存驱动 · AI 内建 · 渐进增强**

---

## 设计理念

| 原则 | 实践 |
|------|------|
| 分层解耦 | View → Service → Model 三层架构 |
| 缓存驱动 | 读缓存 + 写失效，热接口 2ms 响应 |
| AI 内建 | 纯算法引擎，无外部 API 依赖 |
| 渐进增强 | SQLite → PostgreSQL, LocMem → Redis, 单机 → 分布式 |

---

## 系统分层

```
┌────────────────────────────────────────────────────┐
│                     前端层                           │
│                                                     │
│  Vue 3 SPA · Vue Router · Pinia · Element Plus     │
│  ECharts (Tree-shaking) · Axios · Vite Build        │
│                                                     │
│  21 个页面 · defineAsyncComponent 懒加载             │
│  3 个组件 · 2 个 Composable · 1 个 Store             │
│  暗色霓虹设计系统 · CSS Variables 主题               │
├────────────────────────────────────────────────────┤
│                     网关层                           │
│                                                     │
│  Vite Dev Proxy → Waitress → Django WSGI            │
│  JWT Authentication · Session Authentication        │
│  CORS · AnonRateThrottle 100/min                    │
│  RequestTimingMiddleware → X-Response-Time          │
│  HealthCheckMiddleware → /api/health/               │
├────────────────────────────────────────────────────┤
│                   Service 业务层                     │
│                                                     │
│  DashboardService · StoreService · EmployeeService  │
│  ScheduleService · AttendanceService                │
│  PerformanceService · LiveSessionService            │
│                                                     │
│  cached_result() 装饰器 → MD5 Key → TTL Cache       │
│  invalidate_cache() → 写操作自动清除                 │
├────────────────────────────────────────────────────┤
│                 AI Engine 智能层                     │
│                                                     │
│  GMVPredictor      线性回归 + MA + 季节性            │
│  SmartScheduler    贪心匹配 + 疲劳/迟到惩罚          │
│  AnchorProfiler    五维雷达 + Z-Score + 规则洞察     │
│  AnomalyDetector   Z-Score + 规则引擎               │
│  InsightEngine     多维度运营建议                    │
│  AnchorMatcher     多因子组合评分                    │
│                                                     │
│  所有 AI 结果可缓存 (120-180s)                       │
├────────────────────────────────────────────────────┤
│                    数据层                            │
│                                                     │
│  40 Models · 20+ Indexes · SQLite WAL               │
│  select_related · prefetch_related · annotate       │
│  PRAGMA: WAL · cache 64MB · mmap 256MB              │
│  连接信号: journal_mode=WAL on connection_created   │
└────────────────────────────────────────────────────┘
```

---

## 请求生命周期

```
浏览器请求
    │
    ▼
Vite Dev Proxy (/api → :8000)
    │
    ▼
Waitress WSGI Server
    │
    ▼
SecurityMiddleware → CorsMiddleware → SessionMiddleware → ...
RequestTimingMiddleware (计时开始)
HealthCheckMiddleware (/api/health/ 短路返回)
    │
    ▼
JWT Authentication / Session Authentication
    │
    ▼
Router → ViewSet
    │
    ├── 读取: Service.cached_result() → Cache Hit → 直接返回
    │                       │ Cache Miss
    │                       ▼
    │              ORM Query (select_related/prefetch_related)
    │                       │
    │                       ▼
    │              Cache Set → Response
    │
    └── 写入: Model.save() → invalidate_cache() → Response
    │
    ▼
RequestTimingMiddleware (添加 X-Response-Time 头)
    │
    ▼
JSON Response → 浏览器
```

---

## 缓存策略

### 缓存层级

| 层 | 技术 | TTL | 用途 |
|---|------|-----|------|
| 后端 | LocMemCache / Redis | 60-300s | API 响应缓存 |
| AI | LocMemCache / Redis | 120-180s | AI 计算结果 |
| 前端 | Pinia Store | 30s | Dashboard 数据 |

### 缓存失效

写操作 (create/update/destroy) 触发 `invalidate_cache()`:

```python
def perform_create(self, serializer):
    super().perform_create(serializer)
    invalidate_cache('store_overview', 'dashboard')  # 清除关联缓存
```

### 缓存 Key 生成

```python
key = f'{prefix}:{md5(json.dumps(kwargs, sort_keys=True))}'
```

---

## 数据库优化

### SQLite WAL 模式

```python
# settings.py - connection_created 信号
PRAGMA journal_mode=WAL        # 并发读写
PRAGMA synchronous=NORMAL      # 安全+性能平衡
PRAGMA cache_size=-64000       # 64MB 页缓存
PRAGMA temp_store=MEMORY       # 临时表在内存
PRAGMA mmap_size=268435456     # 256MB 内存映射
```

### 索引策略

| 查询模式 | 索引 |
|---------|------|
| 店铺筛选 | (platform), (status), (brand) |
| 排班查询 | (date, employee), (date, store), (date, status), (employee, date, shift) |
| 考勤查询 | (employee, check_time), (result) |
| 直播查询 | (employee, date), (store, date), (date) |
| 请假审批 | (status), (employee) |
| 绩效考核 | (period), (level) |

### 查询优化

```python
# 避免 N+1: 使用 select_related + prefetch_related
queryset = LiveSession.objects.select_related(
    'employee', 'store', 'room'
).prefetch_related('products')

# 避免 N+1: 使用 annotate 替代 SerializerMethodField
queryset = Store.objects.annotate(
    _room_count=Count('rooms', distinct=True),
    _employee_count=Count('employees', distinct=True),
)

# 批量聚合: 替代 Python 循环
gmv_by_store = dict(
    LiveSession.objects.filter(store_id__in=store_ids)
    .values('store_id').annotate(total_gmv=Sum('gmv'))
    .values_list('store_id', 'total_gmv')
)
```

---

## 前端构建优化

### Tree-shaking

```javascript
// echarts.js - 只引入需要的组件
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
```

### Code-splitting

```javascript
// router/index.js - 所有页面懒加载
{ path: '/ai', component: () => import('../views/AI.vue') }

// vite.config.js - 分包
manualChunks: {
  'element-plus': ['element-plus'],
  'echarts': ['echarts'],
  'vendor': ['vue', 'axios']
}
```

### 按需导入

```javascript
// vite.config.js - Element Plus 按需自动导入
AutoImport({ resolvers: [ElementPlusResolver()] })
Components({ resolvers: [ElementPlusResolver()] })
```

---

## 生产环境升级路径

| 组件 | 开发 | 生产 |
|------|------|------|
| 数据库 | SQLite WAL | PostgreSQL |
| 缓存 | LocMemCache | Redis |
| WSGI | Waitress | Gunicorn + Nginx |
| 前端 | Vite Dev Server | Nginx 静态文件 |
| 认证 | AllowAny | JWT + RBAC |

切换 PostgreSQL 只需修改 `settings.py` 中 `DATABASES` 配置，Django ORM 自动适配。
