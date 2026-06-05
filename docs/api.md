# MCN Manager API 参考

> 版本: 1.0 | 基础路径: `/api/` | 认证: JWT / Session | 默认分页: 50 条/页

---

## 目录

- [通用约定](#通用约定)
- [核心模块](#核心模块)
  - [品牌管理 (brands)](#品牌管理-brands)
  - [店铺管理 (stores)](#店铺管理-stores)
  - [团队管理 (teams)](#团队管理-teams)
  - [直播间管理 (rooms)](#直播间管理-rooms)
  - [员工管理 (employees)](#员工管理-employees)
  - [班次管理 (shifts)](#班次管理-shifts)
  - [排班管理 (schedules)](#排班管理-schedules)
  - [考勤管理 (attendances)](#考勤管理-attendances)
  - [请假管理 (leaves)](#请假管理-leaves)
  - [直播记录 (sessions)](#直播记录-sessions)
  - [商品销售 (product-sales)](#商品销售-product-sales)
  - [KPI 配置 (kpi-configs)](#kpi-配置-kpi-configs)
  - [绩效考核 (reviews)](#绩效考核-reviews)
  - [数据驾驶舱 (dashboard)](#数据驾驶舱-dashboard)
- [AI 智能模块](#ai-智能模块)
- [扩展模块](#扩展模块)
  - [商品与库存](#商品与库存)
  - [直播工具](#直播工具)
  - [任务看板](#任务看板)
  - [消息中心](#消息中心)
  - [财务中心](#财务中心)
  - [佣金管理](#佣金管理)
  - [合同管理](#合同管理)
  - [培训管理](#培训管理)
  - [竞品分析](#竞品分析)
  - [粉丝分析](#粉丝分析)
  - [营销活动](#营销活动)
  - [目标管理](#目标管理)
  - [操作日志](#操作日志)
  - [实时大屏](#实时大屏)
  - [权限管理](#权限管理)
  - [达人对接](#达人对接)
  - [数据导出](#数据导出)

---

## 通用约定

### 认证方式

系统支持 JWT Token 与 Django Session 两种认证方式。使用 JWT 时，在请求 Header 中携带:

```
Authorization: Bearer <access_token>
```

| Token 类型 | 有效期 |
|-----------|--------|
| Access Token | 12 小时 |
| Refresh Token | 7 天 |

### 请求与响应

**Content-Type:** `application/json`

**列表响应 (分页):**

```json
{
  "count": 128,
  "next": "http://host/api/resource/?page=2",
  "previous": null,
  "results": [...]
}
```

**单条响应:**

```json
{
  "id": 1,
  "field_a": "value",
  "created_at": "2026-06-01T10:00:00+08:00"
}
```

**错误响应:**

```json
{
  "detail": "错误描述信息"
}
```

### HTTP 状态码

| 状态码 | 含义 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 / 业务校验失败 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 请求频率超限 |

### 限流策略

匿名用户: **100 次/分钟**，超出返回 429 状态码。可在 `settings.py` 中调整:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/min',
    },
}
```

### 性能约定

所有 API 响应包含 `X-Response-Time` 响应头 (单位: 毫秒)。各接口典型性能:

| 端点 | 首次 | 缓存命中 |
|------|------|----------|
| Dashboard Overview | ~10ms | ~2ms |
| Store Overview | ~5ms | ~2.5ms |
| AI Predict | ~6ms | ~2ms |
| AI Schedule | ~240ms | ~2.5ms |
| AI Insights | ~500ms | ~3ms |
| Health Check | ~1ms | -- |

---

## 核心模块

### 品牌管理 `brands`

标准 RESTful CRUD 接口。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/brands/` | 品牌列表 |
| POST | `/api/brands/` | 创建品牌 |
| GET | `/api/brands/{id}/` | 品牌详情 |
| PUT | `/api/brands/{id}/` | 全量更新 |
| DELETE | `/api/brands/{id}/` | 删除品牌 |

**数据字段:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| name | string | 是 | 品牌名 (唯一) |
| industry | string | 否 | 所属行业 |
| contact | string | 否 | 联系人 |
| phone | string | 否 | 联系电话 |
| logo | url | 否 | 品牌 Logo URL |
| remark | string | 否 | 备注信息 |
| created_at | datetime | -- | 创建时间 (自动生成) |

**创建请求示例:**

```json
{
  "name": "花西子",
  "industry": "美妆",
  "contact": "张经理",
  "phone": "13800001111",
  "logo": "https://cdn.example.com/brands/huaxizi.png"
}
```

**响应示例:**

```json
{
  "id": 1,
  "name": "花西子",
  "industry": "美妆",
  "contact": "张经理",
  "phone": "13800001111",
  "logo": "https://cdn.example.com/brands/huaxizi.png",
  "remark": "",
  "created_at": "2026-05-01T10:00:00+08:00"
}
```

---

### 店铺管理 `stores`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stores/` | 店铺列表 (含统计) |
| POST | `/api/stores/` | 创建店铺 |
| GET | `/api/stores/{id}/` | 店铺详情 |
| PUT | `/api/stores/{id}/` | 全量更新 |
| DELETE | `/api/stores/{id}/` | 删除店铺 |
| GET | `/api/stores/overview/` | 店铺运营总览 |

**列表查询参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| platform | string | 平台筛选: `douyin` / `kuaishou` / `taobao` / `xiaohongshu` / `pdd` / `jd` / `video_account` |
| status | string | 状态筛选: `active` / `paused` / `closed` |
| brand_id | int | 按品牌筛选 |
| kw | string | 店铺名模糊搜索 |

列表响应额外包含 `room_count` (直播间数) 和 `employee_count` (关联员工数) 统计字段。

**店铺运营总览 `overview`:**

按 GMV 降序返回所有店铺的运营数据汇总，缓存 120 秒。

```
GET /api/stores/overview/?start=2026-05-01&end=2026-05-31
```

```json
[
  {
    "id": 1,
    "name": "花西子抖音旗舰店",
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

**创建请求示例:**

```json
{
  "name": "花西子抖音旗舰店",
  "platform": "douyin",
  "brand": 1,
  "store_url": "https://douyin.com/shop/xxx",
  "category": "美妆",
  "monthly_target": "50.00",
  "status": "active"
}
```

---

### 团队管理 `teams`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/teams/` | 团队列表 |
| POST | `/api/teams/` | 创建团队 |
| GET | `/api/teams/{id}/` | 团队详情 |
| PUT | `/api/teams/{id}/` | 全量更新 |
| DELETE | `/api/teams/{id}/` | 删除团队 |

列表响应额外包含 `member_count` (成员数) 聚合字段。

---

### 直播间管理 `rooms`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/rooms/` | 直播间列表 |
| POST | `/api/rooms/` | 创建直播间 |
| GET | `/api/rooms/{id}/` | 直播间详情 |
| PUT | `/api/rooms/{id}/` | 全量更新 |
| DELETE | `/api/rooms/{id}/` | 删除直播间 |

**查询参数:** `store_id` -- 按所属店铺筛选。

**数据字段:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| name | string | 是 | 直播间名称 |
| store | int | 是 | 所属店铺 ID |
| room_id | string | 否 | 平台房间号 |
| is_active | boolean | 否 | 是否启用 (默认 true) |

---

### 员工管理 `employees`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/employees/` | 员工列表 (含档案) |
| POST | `/api/employees/` | 创建员工 |
| GET | `/api/employees/{id}/` | 员工详情 |
| PUT | `/api/employees/{id}/` | 全量更新 |
| DELETE | `/api/employees/{id}/` | 删除员工 |
| GET | `/api/employees/stats/` | 员工统计概览 |

**列表查询参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| role | string | 角色筛选: `admin` / `manager` / `operator` / `anchor` / `assistant` |
| store_id | int | 按负责店铺筛选 |
| team_id | int | 按所属小组筛选 |
| is_active | string | 在职状态: `true` / `false` |
| kw | string | 姓名或手机号模糊搜索 |

**员工统计 `stats`:**

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

**创建请求示例:**

```json
{
  "name": "李佳琦",
  "role": "anchor",
  "phone": "13900001111",
  "team": 1,
  "stores": [1, 2],
  "base_salary": "15000.00",
  "join_date": "2026-01-15"
}
```

响应包含嵌套的 `anchor_profile` 对象 (主播专属字段) 和 `store_names` 数组。

---

### 班次管理 `shifts`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/shifts/` | 班次列表 |
| POST | `/api/shifts/` | 创建班次 |
| GET | `/api/shifts/{id}/` | 班次详情 |
| PUT | `/api/shifts/{id}/` | 全量更新 |
| DELETE | `/api/shifts/{id}/` | 删除班次 |

**数据字段:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| name | string | 是 | 班次名称 |
| type | string | 否 | 班次类型: `morning` / `afternoon` / `evening` / `night` / `custom` |
| start_time | time | 是 | 开始时间 |
| end_time | time | 是 | 结束时间 |
| color | string | 否 | 前端显示颜色 (默认 `#409EFF`) |
| description | string | 否 | 描述 |
| late_minutes | int | 否 | 迟到容忍分钟数 (默认 10) |

响应额外包含 `type_display` 和 `time_range` 字段。

---

### 排班管理 `schedules`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/schedules/` | 排班列表 |
| POST | `/api/schedules/` | 创建排班 (含校验) |
| GET | `/api/schedules/{id}/` | 排班详情 |
| PUT | `/api/schedules/{id}/` | 全量更新 |
| DELETE | `/api/schedules/{id}/` | 删除排班 |
| GET | `/api/schedules/weekly/` | 周排班视图 |
| POST | `/api/schedules/batch_create/` | 批量创建 |

**列表查询参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| start | date | 起始日期 (YYYY-MM-DD) |
| end | date | 截止日期 |
| store_id | int | 店铺筛选 |
| employee_id | int | 员工筛选 |
| role | string | 按员工角色筛选 |
| status | string | 排班状态: `scheduled` / `checked_in` / `completed` / `cancelled` / `absent` |

**创建排班:**

创建时自动校验: 重复排班检测 + 同一时段冲突检测。校验失败返回 400。

```json
{
  "employee": 5,
  "shift": 1,
  "store": 1,
  "room": 1,
  "date": "2026-06-05",
  "note": "618备战"
}
```

**周排班视图 `weekly`:**

```
GET /api/schedules/weekly/?start=2026-06-01
```

返回指定日期所在周 (共 7 天) 的所有排班数据:

```json
{
  "start": "2026-06-01",
  "end": "2026-06-07",
  "items": [
    {
      "id": 1,
      "employee": 5,
      "employee_name": "李佳琦",
      "employee_role": "anchor",
      "shift": 1,
      "shift_name": "早班",
      "shift_color": "#409EFF",
      "start_time": "08:00:00",
      "end_time": "14:00:00",
      "store": 1,
      "store_name": "旗舰店",
      "room": 1,
      "room_name": "1号厅",
      "date": "2026-06-01",
      "status": "scheduled",
      "status_display": "已排班",
      "note": ""
    }
  ]
}
```

**批量创建 `batch_create`:**

```
POST /api/schedules/batch_create/
```

请求体为数组格式，每条记录独立校验:

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
    {"index": 1, "error": "该员工在此时间段已有其他排班，时间冲突"}
  ]
}
```

---

### 考勤管理 `attendances`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/attendances/` | 考勤记录列表 |
| POST | `/api/attendances/clock_in/` | 上班打卡 |
| POST | `/api/attendances/clock_out/` | 下班打卡 |
| GET | `/api/attendances/summary/` | 考勤汇总统计 |

**列表查询参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| employee_id | int | 员工筛选 |
| start | date | 起始日期 |
| end | date | 截止日期 |
| result | string | 考勤结果: `normal` / `late` / `early` / `absent` / `leave` / `overtime` |

**上班打卡 `clock_in`:**

```json
{
  "employee_id": 5,
  "schedule_id": 12,
  "location": "公司总部A座",
  "photo": "https://cdn.example.com/clock_in.jpg"
}
```

打卡逻辑:
1. 通过 `schedule_id` 或 `employee_id` 匹配当日排班
2. 对比班次开始时间与打卡时间
3. 超出容忍分钟数 (班次 `late_minutes`) 则标记 `late`，否则 `normal`
4. 自动将排班状态更新为 `checked_in`

**下班打卡 `clock_out`:**

```json
{
  "employee_id": 5,
  "location": "公司总部A座",
  "photo": ""
}
```

打卡逻辑: 超过班次结束时间标记为 `overtime`，否则 `normal`。同时将排班状态更新为 `completed`。

**考勤汇总 `summary`:**

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
    {"employee_id": 5, "employee__name": "张三", "late": 8, "normal": 22}
  ],
  "start": "2026-05-01",
  "end": "2026-05-31"
}
```

---

### 请假管理 `leaves`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/leaves/` | 请假列表 |
| POST | `/api/leaves/` | 创建请假 |
| GET | `/api/leaves/{id}/` | 请假详情 |
| PUT | `/api/leaves/{id}/` | 全量更新 |
| DELETE | `/api/leaves/{id}/` | 删除请假 |
| POST | `/api/leaves/{id}/approve/` | 审批通过 |
| POST | `/api/leaves/{id}/reject/` | 审批拒绝 |

**查询参数:** `status` (`pending` / `approved` / `rejected`), `employee_id`

**请假类型:** `personal` (事假) / `sick` (病假) / `annual` (年假) / `marriage` (婚假) / `bereavement` (丧假) / `maternity` (产假)

**审批通过:**

```json
{
  "approver": "管理员",
  "remark": "同意，注意休息"
}
```

---

### 直播记录 `sessions`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sessions/` | 直播记录列表 |
| POST | `/api/sessions/` | 创建直播记录 |
| GET | `/api/sessions/{id}/` | 直播记录详情 |
| PUT | `/api/sessions/{id}/` | 全量更新 |
| DELETE | `/api/sessions/{id}/` | 删除直播记录 |
| GET | `/api/sessions/daily_gmv/` | 每日 GMV 统计 |
| GET | `/api/sessions/top_anchors/` | 主播 GMV 排行 |

**列表查询参数:** `employee_id`, `store_id`, `start`, `end`

响应包含嵌套的 `products` 数组 (本场商品销售明细)。

**每日 GMV `daily_gmv`:**

```
GET /api/sessions/daily_gmv/?start=2026-05-01&end=2026-05-31&store_id=1
```

```json
[
  {"d": "2026-05-01", "gmv": 58000.00, "orders": 230, "sessions": 3},
  {"d": "2026-05-02", "gmv": 62000.00, "orders": 255, "sessions": 4}
]
```

**主播排行 `top_anchors`:**

```
GET /api/sessions/top_anchors/?start=2026-05-01&end=2026-05-31&limit=10
```

```json
[
  {
    "employee_id": 5,
    "employee__name": "李佳琦",
    "gmv": 1280000.00,
    "orders": 5600,
    "hours": 7200,
    "sessions": 28
  }
]
```

---

### 商品销售 `product-sales`

标准 CRUD，关联于直播场次。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/product-sales/` | 销售明细列表 |
| POST | `/api/product-sales/` | 创建销售明细 |
| GET | `/api/product-sales/{id}/` | 销售明细详情 |
| PUT | `/api/product-sales/{id}/` | 全量更新 |
| DELETE | `/api/product-sales/{id}/` | 删除销售明细 |

**数据字段:** `session` (直播场次 ID), `product_name`, `sku`, `price`, `quantity`, `gmv`, `commission`

---

### KPI 配置 `kpi-configs`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/kpi-configs/` | KPI 配置列表 |
| POST | `/api/kpi-configs/` | 创建配置 |
| GET | `/api/kpi-configs/{id}/` | 配置详情 |
| PUT | `/api/kpi-configs/{id}/` | 全量更新 |
| DELETE | `/api/kpi-configs/{id}/` | 删除配置 |

**指标类型:** `gmv` / `orders` / `hours` / `followers` / `conversion` / `attendance`

---

### 绩效考核 `reviews`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/reviews/` | 考核列表 |
| POST | `/api/reviews/calculate/` | 自动计算考核 |

**查询参数:** `period` (如 `2026-06`), `employee_id`, `role`, `level` (S/A/B/C/D)

**自动计算 `calculate`:**

```json
{
  "employee_id": 5,
  "period": "2026-05"
}
```

评分公式: GMV 完成率 x 60% + 出勤率 x 20% + 直播时长 x 10% + 订单数 x 10% = 综合得分

| 得分区间 | 等级 |
|---------|------|
| >= 90 | S (优秀) |
| >= 80 | A (良好) |
| >= 60 | B (合格) |
| >= 40 | C (待改进) |
| < 40 | D (不合格) |

绩效奖金 = `max(0, (score - 60) / 40) x base_salary` (仅 60 分以上有奖金)

---

### 数据驾驶舱 `dashboard`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard/overview/` | 驾驶舱总览 |

缓存 60 秒，响应结构:

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
    {"employee_id": 5, "employee__name": "李佳琦", "gmv": 580000.00, "sessions": 12}
  ]
}
```

---

## AI 智能模块

所有 AI 接口注册在 `/api/ai/` 路径下，使用 GET 方法，结果根据参数哈希缓存 120~180 秒。

| 路径 | 说明 | 核心参数 | 缓存 |
|------|------|----------|------|
| `/api/ai/predict/` | GMV 预测 | `days` (1-30), `store_id`, `employee_id` | 120s |
| `/api/ai/schedule/` | 智能排班推荐 | `date` (YYYY-MM-DD), `store_id` | 120s |
| `/api/ai/anchor/` | 主播画像分析 | `employee_id` (必填) | 180s |
| `/api/ai/anomaly/` | 异常数据检测 | `days` (1-30) | 120s |
| `/api/ai/insights/` | 运营建议引擎 | 无参数 | 120s |
| `/api/ai/match/` | 主播-店铺匹配 | `store_id` | 180s |

算法原理、公式推导和完整响应结构请参阅 [AI 引擎文档](ai-engine.md)。

---

## 扩展模块

### 商品与库存

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/product-categories/` | 商品类目 CRUD |
| GET/POST | `/api/products/` | 商品 CRUD |
| GET | `/api/products/low_stock/` | 低库存商品列表 |
| GET/POST | `/api/inventory-alerts/` | 库存预警规则 CRUD |
| GET | `/api/inventory-alerts/triggered/` | 已触发的预警列表 |

**商品查询参数:** `status` (active/inactive/draft), `category_id`, `kw` (名称或 SKU 搜索)

**低库存商品:** 返回库存 <= 10 且状态为 `active` 的商品列表。

**已触发预警:** 遍历所有启用的预警规则，返回当前库存 <= 阈值的商品:

```json
[
  {
    "id": 1,
    "product_id": 15,
    "product_name": "花西子蜜粉",
    "stock": 3,
    "threshold": 10
  }
]
```

---

### 直播工具

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/stream-scripts/` | 直播脚本 CRUD |
| GET/POST | `/api/script-segments/` | 脚本段落 CRUD |
| GET/POST | `/api/sales-scripts/` | 话术模板 CRUD |
| GET/POST | `/api/stream-reviews/` | 直播复盘 CRUD |

**脚本查询参数:** `store_id`, `status` (draft/active/archived)

**话术模板查询参数:** `scene`, `kw`

**段落类型:** `warmup` / `product` / `interaction` / `promotion` / `flash_sale` / `closing`

**话术场景:** `opening` / `product_intro` / `objection` / `closing` / `follow_up` / `interaction` / `flash_sale`

**脚本响应示例:**

```json
{
  "id": 1,
  "title": "618大促直播脚本",
  "store": 1,
  "store_name": "旗舰店",
  "status": "active",
  "status_display": "使用中",
  "duration_minutes": 180,
  "creator": 3,
  "creator_name": "运营小王",
  "segment_count": 8,
  "segments": [
    {
      "id": 1,
      "order": 1,
      "segment_type": "warmup",
      "segment_type_display": "暖场",
      "title": "开场暖场",
      "duration_minutes": 10,
      "product": null,
      "product_name": "",
      "talking_points": "互动拉人气，预热直播间氛围"
    }
  ]
}
```

---

### 任务看板

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/task-boards/` | 看板 CRUD (含嵌套卡片) |
| GET/POST | `/api/task-cards/` | 任务卡片 CRUD |
| POST | `/api/task-cards/{id}/move/` | 移动卡片状态 |

**移动卡片:**

```json
{
  "status": "doing"
}
```

卡片状态流转: `todo` --> `doing` --> `done`，或标记为 `blocked`。

看板响应包含嵌套的 `cards` 数组和 `card_count` 统计字段。

---

### 消息中心

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/notifications/` | 消息列表 |
| POST | `/api/notifications/read_all/` | 全部标记已读 |
| GET | `/api/notifications/unread_count/` | 未读消息数 |

**查询参数:** `target_id` (接收人), `is_read` (true/false), `type`

**消息类型:** `system` / `schedule` / `attendance` / `performance` / `leave` / `alert` / `contract` / `task`

**全部已读:**

```json
{ "target_id": 5 }
```

返回: `{"updated": 12}`

**未读数:**

```
GET /api/notifications/unread_count/?target_id=5
```

返回: `{"count": 8}`

---

### 财务中心

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/finance/` | 财务记录 CRUD |
| GET | `/api/finance/summary/` | 财务汇总 |

**查询参数:** `start`, `end`, `type` (income/expense), `category`, `store_id`

**财务分类:** `gmv` / `commission` / `salary` / `bonus` / `equipment` / `ads` / `logistics` / `other`

**财务汇总:**

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

### 佣金管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/commission-rules/` | 佣金规则 CRUD |
| GET | `/api/commissions/` | 佣金记录列表 |
| POST | `/api/commissions/{id}/settle/` | 结算佣金 |

**查询参数 (佣金记录):** `period`, `status` (pending/settled/cancelled), `employee_id`

**佣金规则计算方式:** `fixed` (固定金额) / `percent` (比例)

结算后自动记录 `settled_at` 时间。

---

### 合同管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/contracts/` | 合同 CRUD |
| GET | `/api/contracts/expiring/` | 即将到期合同列表 |

**查询参数:** `status`, `employee_id`, `contract_type`

**合同类型:** `labor` / `service` / `anchor` / `brand`

**合同状态:** `active` / `expiring` / `expired` / `terminated`

**即将到期:**

```
GET /api/contracts/expiring/?days=30
```

返回指定天数内到期的所有生效中合同。

---

### 培训管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/training-courses/` | 课程 CRUD |
| GET/POST | `/api/training-records/` | 培训记录 CRUD |

**查询参数 (课程):** `status` (draft/active/completed), `category`

课程响应包含嵌套的 `records` 数组 (学员培训记录)。

---

### 竞品分析

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/competitors/` | 竞品信息 CRUD |
| GET/POST | `/api/competitor-data/` | 竞品数据追踪 CRUD |

竞品响应包含嵌套的 `data` 数组 (历史追踪数据)。

---

### 粉丝分析

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/fan-analysis/` | 粉丝数据 CRUD |
| GET | `/api/fan-analysis/trend/` | 粉丝趋势 |

**查询参数:** `store_id`, `start`, `end`

**粉丝趋势:**

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

### 营销活动

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/campaigns/` | 营销活动 CRUD |

**查询参数:** `status` (draft/active/completed/cancelled), `store_id`, `campaign_type`

**活动类型:** `flash_sale` / `coupon` / `gift` / `discount` / `live_debut` / `festival`

响应包含计算字段 `completion_rate` (实际 GMV / 目标 GMV x 100)。

---

### 目标管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/goals/` | 目标 CRUD |
| GET | `/api/goals/board/` | 目标看板汇总 |

**查询参数:** `period`, `employee_id`, `status`, `store_id`

**目标周期:** `weekly` / `monthly` / `quarterly` / `yearly`

**目标看板:**

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

### 操作日志

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/operation-logs/` | 日志列表 (只读) |

**查询参数:** `user`, `action`, `model_name`

系统保留最近 500 条操作日志，单次查询最多返回 200 条。

---

### 实时大屏

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/billboard/` | 大屏配置 CRUD |
| GET | `/api/billboard/data/` | 大屏实时数据 |

`data` 接口返回与 Dashboard Overview 相同的数据结构，可配置 `refresh_interval` 用于前端轮询。

---

### 权限管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/roles/` | 角色管理 CRUD |
| GET/POST | `/api/user-roles/` | 用户角色绑定 CRUD |

角色的 `permissions` 字段为 JSON 数组格式，例如:

```json
{
  "name": "运营经理",
  "description": "店铺和排班管理权限",
  "permissions": ["store:view", "store:edit", "schedule:view", "schedule:edit"]
}
```

角色响应包含 `member_count` 统计字段。

---

### 达人对接

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/kols/` | KOL 资源管理 CRUD |

**查询参数:** `status`, `platform`, `kw` (名称或领域搜索)

**KOL 状态:** `contacting` / `negotiating` / `cooperating` / `completed`

**KOL 平台:** `douyin` / `kuaishou` / `xiaohongshu` / `weibo`

---

### 数据导出

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/exports/` | 导出任务列表 |
| POST | `/api/exports/create_export/` | 创建并执行导出 |

**创建导出:**

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

**支持的导出类型:**

| 类型 | 说明 | 导出字段 |
|------|------|---------|
| `sessions` | 直播记录 | 日期、主播、店铺、GMV、订单数、时长、峰值观看、转化率 |
| `attendance` | 考勤记录 | 员工、打卡类型、打卡时间、结果、迟到分钟 |
| `finance` | 财务记录 | 日期、类型、类目、金额、店铺、备注 |

**响应:**

```json
{
  "id": 1,
  "name": "sessions导出_20260605120000",
  "export_type": "sessions",
  "status": "done",
  "status_display": "已完成",
  "file_url": "/media/exports/1.csv",
  "file_size": 15234,
  "row_count": 200,
  "csv_content": "日期,主播,店铺,GMV,订单数,时长(分),峰值观看,转化率\n..."
}
```

单次导出上限 5000 行数据。
