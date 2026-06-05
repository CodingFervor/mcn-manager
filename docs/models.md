# MCN Manager 数据模型参考

> 共 40 个模型，横跨 5 大业务领域 | Django ORM | SQLite / PostgreSQL

---

## 目录

- [模型总览](#模型总览)
- [领域一: 组织架构](#领域一-组织架构)
- [领域二: 人员管理](#领域二-人员管理)
- [领域三: 排班与考勤](#领域三-排班与考勤)
- [领域四: 业绩与绩效](#领域四-业绩与绩效)
- [领域五: 扩展业务](#领域五-扩展业务)
- [关系图](#关系图)

---

## 模型总览

### 领域划分

| 领域 | 模型数 | 模型列表 |
|------|--------|---------|
| 组织架构 | 4 | Brand, Store, Team, StreamRoom |
| 人员管理 | 2 | Employee, AnchorProfile |
| 排班考勤 | 4 | Shift, Schedule, Attendance, LeaveRequest |
| 业绩绩效 | 4 | LiveSession, ProductSales, KPIConfig, PerformanceReview |
| 扩展业务 | 26 | ProductCategory, Product, InventoryAlert, StreamScript, ScriptSegment, SalesScript, StreamReview, TaskBoard, TaskCard, Notification, FinanceRecord, CommissionRule, CommissionRecord, Contract, TrainingCourse, TrainingRecord, Competitor, CompetitorData, FanAnalysis, Campaign, Goal, OperationLog, BillboardConfig, Role, UserRole, KOLContact, ExportTask |

### 关系概览

```
Brand  1---N  Store  1---N  StreamRoom
                  |
                  +--M2M-- Employee ---1--- AnchorProfile
                  |              |
                  |              +-- 1:N -- Schedule (FK Shift)
                  |              |              |
                  |              |              +-- 1:N -- Attendance
                  |              |
                  |              +-- 1:N -- LeaveRequest
                  |              |
                  |              +-- 1:N -- LiveSession -- 1:N -- ProductSales
                  |              |
                  |              +-- 1:N -- PerformanceReview
                  |
                  +-- 1:N -- FanAnalysis
                  +-- 1:N -- Campaign -- M2M -- Product
```

---

## 领域一: 组织架构

### Brand -- 品牌方

合作品牌方信息管理。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| name | varchar(100) | **唯一**, 非空 | 品牌名称 |
| industry | varchar(50) | 可空 | 所属行业 |
| contact | varchar(50) | 可空 | 联系人 |
| phone | varchar(20) | 可空 | 联系电话 |
| logo | url | 可空 | 品牌 Logo URL |
| remark | text | 可空 | 备注信息 |
| created_at | datetime | 自动生成 | 创建时间 |

**排序:** 按 `name` 升序

**反向关系:**
- `stores` -- Store (一对多)

---

### Store -- 店铺

跨平台店铺管理，支持抖音、快手、淘宝等 7 个平台。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| name | varchar(100) | 非空 | 店铺名称 |
| platform | varchar(20) | 默认 `douyin` | 平台选择 (见下表) |
| brand | FK -> Brand | 可空, SET_NULL | 所属品牌 |
| store_url | url | 可空 | 店铺链接 |
| category | varchar(50) | 可空 | 经营类目 |
| status | varchar(20) | 默认 `active` | 店铺状态 |
| monthly_target | decimal(12,2) | 默认 0 | 月度 GMV 目标 (万元) |
| remark | text | 可空 | 备注信息 |
| created_at | datetime | 自动生成 | 创建时间 |

**platform 选项:**

| 值 | 显示名 |
|----|--------|
| douyin | 抖音 |
| kuaishou | 快手 |
| taobao | 淘宝 |
| xiaohongshu | 小红书 |
| pdd | 拼多多 |
| jd | 京东 |
| video_account | 视频号 |

**status 选项:** `active` (运营中) / `paused` (已暂停) / `closed` (已关停)

**索引:** `platform`, `status`, `brand`

**反向关系:**
- `rooms` -- StreamRoom (一对多)
- `employees` -- Employee (多对多)
- `schedules` -- Schedule (一对多)
- `fan_analysis` -- FanAnalysis (一对多)

---

### Team -- 运营小组

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| name | varchar(50) | **唯一**, 非空 | 小组名称 |
| leader | varchar(50) | 可空 | 组长姓名 |
| description | varchar(200) | 可空 | 职责描述 |
| created_at | datetime | 自动生成 | 创建时间 |

**反向关系:**
- `members` -- Employee (一对多)

---

### StreamRoom -- 直播间

一个店铺可拥有多个直播间。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| name | varchar(100) | 非空 | 直播间名称 |
| store | FK -> Store | **CASCADE**, 非空 | 所属店铺 |
| room_id | varchar(50) | 可空 | 平台房间号 |
| is_active | boolean | 默认 true | 是否启用 |
| created_at | datetime | 自动生成 | 创建时间 |

**反向关系:**
- `schedules` -- Schedule (一对多)

---

## 领域二: 人员管理

### Employee -- 员工

统一管理所有角色人员，包括主播、运营、管理员等。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| user | OneToOne -> User | 可空, SET_NULL | 关联 Django 认证用户 |
| name | varchar(50) | 非空 | 姓名 |
| role | varchar(20) | 默认 `anchor` | 员工角色 |
| phone | varchar(20) | 可空 | 联系电话 |
| wechat | varchar(50) | 可空 | 微信号 |
| avatar | url | 可空 | 头像 URL |
| id_card | varchar(20) | 可空 | 身份证号 |
| team | FK -> Team | 可空, SET_NULL | 所属小组 |
| stores | M2M -> Store | 可空 | 负责店铺 (多对多) |
| join_date | date | 可空 | 入职日期 |
| base_salary | decimal(10,2) | 默认 0 | 底薪 (元) |
| is_active | boolean | 默认 true | 是否在职 |
| remark | text | 可空 | 备注信息 |
| created_at | datetime | 自动生成 | 创建时间 |

**role 选项:**

| 值 | 显示名 |
|----|--------|
| admin | 管理员 |
| manager | 运营经理 |
| operator | 运营/中控 |
| anchor | 主播 |
| assistant | 助理 |

**索引:** `(role, is_active)`, `team`

**排序:** 按 `created_at` 降序

**反向关系:**
- `anchor_profile` -- AnchorProfile (一对一)
- `schedules` -- Schedule (一对多)
- `attendances` -- Attendance (一对多)
- `leaves` -- LeaveRequest (一对多)
- `sessions` -- LiveSession (一对多)
- `reviews` -- PerformanceReview (一对多)
- `commissions` -- CommissionRecord (一对多)
- `contracts` -- Contract (一对多)
- `roles` -- UserRole (一对多)

---

### AnchorProfile -- 主播档案

主播特有的数据档案，与 Employee 一对一关联。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| employee | OneToOne -> Employee | **CASCADE**, 非空 | 关联员工 |
| nickname | varchar(50) | 非空 | 直播昵称 |
| level | varchar(20) | 默认 `普通` | 主播等级 |
| style | varchar(100) | 可空 | 风格 (如: 搞笑/专业/邻家) |
| category_tags | varchar(200) | 可空 | 擅长类目 |
| fans_count | int | 默认 0 | 粉丝总数 |
| follower_count | int | 默认 0 | 关注数 |
| avg_watch | int | 默认 0 | 场均观看 |
| conversion_rate | decimal(5,2) | 默认 0 | 转化率 (%) |
| contract_end | date | 可空 | 合同到期日 |

---

## 领域三: 排班与考勤

### Shift -- 班次模板

定义可复用的班次模板，包含时间段和迟到容忍度。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| name | varchar(50) | 非空 | 班次名称 |
| type | varchar(20) | 默认 `morning` | 班次类型 |
| start_time | time | 非空 | 开始时间 |
| end_time | time | 非空 | 结束时间 |
| color | varchar(20) | 默认 `#409EFF` | 前端显示颜色 |
| description | varchar(200) | 可空 | 描述 |
| late_minutes | int | 默认 10 | 迟到容忍分钟数 |

**type 选项:** `morning` (早班) / `afternoon` (中班) / `evening` (晚班) / `night` (夜班) / `custom` (自定义)

**排序:** 按 `start_time` 升序

---

### Schedule -- 排班

员工在特定日期的排班安排，关联班次、店铺和直播间。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| employee | FK -> Employee | **CASCADE**, 非空 | 员工 |
| shift | FK -> Shift | **CASCADE**, 非空 | 班次 |
| store | FK -> Store | 可空, SET_NULL | 店铺 |
| room | FK -> StreamRoom | 可空, SET_NULL | 直播间 |
| date | date | 非空 | 排班日期 |
| status | varchar(20) | 默认 `scheduled` | 排班状态 |
| note | varchar(200) | 可空 | 备注 |
| created_at | datetime | 自动生成 | 创建时间 |
| updated_at | datetime | 自动更新 | 更新时间 |

**status 选项:** `scheduled` (已排班) / `checked_in` (已打卡) / `completed` (已完成) / `cancelled` (已取消) / `absent` (缺勤)

**索引:** `(date, employee)`, `(date, store)`, `(date, status)`, `(employee, date, shift)`

**排序:** 按 `date`, `shift.start_time` 升序

---

### Attendance -- 考勤记录

每次打卡生成一条记录，包含打卡结果和迟到分钟数。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| schedule | FK -> Schedule | **CASCADE**, 非空 | 关联排班 |
| employee | FK -> Employee | **CASCADE**, 非空 | 员工 |
| check_type | varchar(20) | 非空 | 打卡类型 |
| check_time | datetime | 非空 | 打卡时间 |
| result | varchar(20) | 默认 `normal` | 考勤结果 |
| location | varchar(200) | 可空 | 打卡位置 |
| photo | url | 可空 | 打卡照片 |
| late_minutes | int | 默认 0 | 迟到分钟数 |
| remark | varchar(200) | 可空 | 备注 |
| created_at | datetime | 自动生成 | 创建时间 |

**check_type 选项:** `clock_in` (上班打卡) / `clock_out` (下班打卡)

**result 选项:** `normal` (正常) / `late` (迟到) / `early` (早退) / `absent` (缺勤) / `leave` (请假) / `overtime` (加班)

**索引:** `(employee, check_time)`, `result`

**排序:** 按 `check_time` 降序

---

### LeaveRequest -- 请假申请

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| employee | FK -> Employee | **CASCADE**, 非空 | 员工 |
| leave_type | varchar(20) | 非空 | 请假类型 |
| start_date | date | 非空 | 开始日期 |
| end_date | date | 非空 | 结束日期 |
| days | decimal(5,1) | 默认 1 | 请假天数 |
| reason | text | 非空 | 请假原因 |
| status | varchar(20) | 默认 `pending` | 审批状态 |
| approver | varchar(50) | 可空 | 审批人 |
| approve_time | datetime | 可空 | 审批时间 |
| approve_remark | varchar(200) | 可空 | 审批意见 |
| created_at | datetime | 自动生成 | 创建时间 |

**leave_type 选项:** `personal` (事假) / `sick` (病假) / `annual` (年假) / `marriage` (婚假) / `bereavement` (丧假) / `maternity` (产假)

**status 选项:** `pending` (待审批) / `approved` (已批准) / `rejected` (已拒绝)

**索引:** `status`, `employee`

---

## 领域四: 业绩与绩效

### LiveSession -- 直播记录

一场完整直播的数据记录。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| schedule | FK -> Schedule | 可空, SET_NULL | 关联排班 |
| employee | FK -> Employee | **CASCADE**, 非空 | 主播 |
| store | FK -> Store | 可空, SET_NULL | 店铺 |
| room | FK -> StreamRoom | 可空, SET_NULL | 直播间 |
| date | date | 非空 | 直播日期 |
| start_time | datetime | 非空 | 开始时间 |
| end_time | datetime | 可空 | 结束时间 |
| duration_minutes | int | 默认 0 | 直播时长 (分钟) |
| peak_viewers | int | 默认 0 | 峰值在线人数 |
| avg_viewers | int | 默认 0 | 平均在线人数 |
| new_followers | int | 默认 0 | 新增粉丝 |
| gmv | decimal(12,2) | 默认 0 | GMV (元) |
| orders | int | 默认 0 | 订单数 |
| conversion_rate | decimal(5,2) | 默认 0 | 转化率 (%) |
| created_at | datetime | 自动生成 | 创建时间 |

**索引:** `(employee, date)`, `(store, date)`, `date`

**排序:** 按 `date` 降序, `start_time` 降序

**反向关系:**
- `products` -- ProductSales (一对多)
- `review` -- StreamReview (一对一)

---

### ProductSales -- 商品销售明细

单场直播中的商品级别销售数据。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| session | FK -> LiveSession | **CASCADE**, 非空 | 直播场次 |
| product_name | varchar(200) | 非空 | 商品名称 |
| sku | varchar(50) | 可空 | SKU 编码 |
| price | decimal(10,2) | 默认 0 | 单价 |
| quantity | int | 默认 0 | 销售数量 |
| gmv | decimal(12,2) | 默认 0 | GMV |
| commission | decimal(10,2) | 默认 0 | 佣金 |

**索引:** `session`

---

### KPIConfig -- KPI 指标配置

定义各角色的 KPI 考核指标和目标值。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| role | varchar(20) | 默认 `anchor` | 适用角色 |
| metric | varchar(20) | 非空 | 指标类型 |
| target_value | decimal(12,2) | 默认 0 | 月度目标值 |
| weight | decimal(5,2) | 默认 0 | 权重 (%) |
| period | varchar(20) | 默认 `monthly` | 考核周期 |
| is_active | boolean | 默认 true | 是否启用 |

**metric 选项:** `gmv` / `orders` / `hours` / `followers` / `conversion` / `attendance`

---

### PerformanceReview -- 绩效考核

按月度自动计算的员工绩效评级。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, 自增 | 主键 |
| employee | FK -> Employee | **CASCADE**, 非空 | 员工 |
| period | varchar(20) | 非空 | 考核周期 (格式: 2026-06) |
| gmv | decimal(12,2) | 默认 0 | GMV 实际达成 |
| gmv_target | decimal(12,2) | 默认 0 | GMV 目标 |
| gmv_rate | decimal(5,2) | 默认 0 | GMV 完成率 (%) |
| orders | int | 默认 0 | 订单数 |
| live_hours | decimal(8,2) | 默认 0 | 直播时长 |
| attendance_rate | decimal(5,2) | 默认 0 | 出勤率 (%) |
| score | decimal(5,2) | 默认 0 | 综合得分 |
| level | varchar(5) | 默认 `B` | 评级 |
| bonus | decimal(10,2) | 默认 0 | 绩效奖金 |
| remark | text | 可空 | 评语 |
| created_at | datetime | 自动生成 | 创建时间 |

**level 选项:** `S` (优秀) / `A` (良好) / `B` (合格) / `C` (待改进) / `D` (不合格)

**唯一约束:** `(employee, period)`

**索引:** `period`, `level`

**排序:** 按 `period` 降序, `score` 降序

---

## 领域五: 扩展业务

### 商品与库存管理

#### ProductCategory -- 商品类目

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| name | varchar(50) | 非空 | 类目名称 |
| parent | FK -> self | 可空, SET_NULL | 父类目 (树形结构) |
| sort_order | int | 默认 0 | 排序权重 |

**排序:** 按 `sort_order` 升序

#### Product -- 商品库

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| name | varchar(200) | 非空 | 商品名称 |
| sku | varchar(50) | 可空 | SKU 编码 |
| category | FK -> ProductCategory | 可空, SET_NULL | 商品类目 |
| brand | varchar(100) | 可空 | 品牌名 |
| cover | url | 可空 | 主图 URL |
| price | decimal(10,2) | 默认 0 | 售价 |
| cost | decimal(10,2) | 默认 0 | 成本价 |
| commission_rate | decimal(5,2) | 默认 0 | 佣金比例 (%) |
| stock | int | 默认 0 | 库存数量 |
| status | varchar(20) | 默认 `active` | 状态 (active/inactive/draft) |
| tags | varchar(200) | 可空 | 标签 (逗号分隔) |
| supplier | varchar(100) | 可空 | 供应商 |
| supplier_contact | varchar(50) | 可空 | 供应商联系方式 |

**索引:** `status`, `category`

#### InventoryAlert -- 库存预警

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| product | FK -> Product | **CASCADE**, 非空 | 商品 |
| threshold | int | 默认 10 | 预警阈值 |
| is_active | boolean | 默认 true | 是否启用 |
| last_alerted | datetime | 可空 | 最后告警时间 |

**唯一约束:** `(product,)`

---

### 直播工具

#### StreamScript -- 直播脚本

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| title | varchar(200) | 非空 | 脚本标题 |
| store | FK -> Store | 可空, SET_NULL | 适用店铺 |
| duration_minutes | int | 默认 120 | 预计时长 (分钟) |
| status | varchar(20) | 默认 `draft` | 状态 (draft/active/archived) |
| creator | FK -> Employee | 可空, SET_NULL | 创建人 |
| note | text | 可空 | 备注 |

**反向关系:** `segments` -- ScriptSegment (一对多)

#### ScriptSegment -- 脚本段落

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| script | FK -> StreamScript | **CASCADE**, 非空 | 所属脚本 |
| order | int | 默认 0 | 排序序号 |
| segment_type | varchar(20) | 默认 `product` | 段落类型 |
| title | varchar(200) | 非空 | 段落标题 |
| duration_minutes | int | 默认 10 | 时长 (分钟) |
| product | FK -> Product | 可空, SET_NULL | 关联商品 |
| talking_points | text | 可空 | 话术要点 |

**段落类型:** `warmup` (暖场) / `product` (商品讲解) / `interaction` (互动) / `promotion` (促销) / `flash_sale` (限时秒杀) / `closing` (收尾)

#### SalesScript -- 话术模板

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| title | varchar(200) | 非空 | 话术标题 |
| scene | varchar(20) | 默认 `product_intro` | 适用场景 |
| content | text | 非空 | 话术内容 |
| tags | varchar(200) | 可空 | 标签 |
| use_count | int | 默认 0 | 使用次数 |
| rating | decimal(3,1) | 默认 0 | 评分 |
| creator | FK -> Employee | 可空, SET_NULL | 创建人 |

**索引:** `scene`

#### StreamReview -- 直播复盘

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| session | OneToOne -> LiveSession | **CASCADE**, 非空 | 直播场次 |
| highlights | text | 可空 | 亮点 |
| issues | text | 可空 | 问题 |
| improvements | text | 可空 | 改进建议 |
| best_moments | text | 可空 | 高光时刻 |
| audience_feedback | text | 可空 | 观众反馈摘要 |
| next_action | text | 可空 | 下一步行动 |
| rating | int | 默认 3 | 自评 (1-5) |
| reviewer | FK -> Employee | 可空, SET_NULL | 复盘人 |

---

### 协作管理

#### TaskBoard -- 任务看板

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| name | varchar(100) | 非空 | 看板名称 |
| team | varchar(50) | 可空 | 团队标识 |

**反向关系:** `cards` -- TaskCard (一对多)

#### TaskCard -- 任务卡片

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| board | FK -> TaskBoard | **CASCADE**, 非空 | 所属看板 |
| title | varchar(200) | 非空 | 任务标题 |
| description | text | 可空 | 任务描述 |
| priority | varchar(10) | 默认 `medium` | 优先级 (high/medium/low) |
| status | varchar(10) | 默认 `todo` | 状态 (todo/doing/done/blocked) |
| assignee | FK -> Employee | 可空, SET_NULL | 负责人 |
| due_date | date | 可空 | 截止日期 |
| order | int | 默认 0 | 排序权重 |

**索引:** `status`, `assignee`

#### Notification -- 消息通知

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| title | varchar(200) | 非空 | 消息标题 |
| content | text | 非空 | 消息内容 |
| type | varchar(20) | 默认 `system` | 消息类型 |
| target | FK -> Employee | 可空, SET_NULL | 接收人 |
| is_read | boolean | 默认 false | 是否已读 |
| link | varchar(200) | 可空 | 跳转链接 |

**消息类型:** `system` / `schedule` / `attendance` / `performance` / `leave` / `alert` / `contract` / `task`

**索引:** `(target, is_read)`

---

### 财务管理

#### FinanceRecord -- 财务记录

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| date | date | 非空 | 日期 |
| type | varchar(10) | 非空 | 类型 (income/expense) |
| category | varchar(20) | 非空 | 财务类目 |
| amount | decimal(12,2) | 非空 | 金额 |
| store | FK -> Store | 可空, SET_NULL | 关联店铺 |
| employee | FK -> Employee | 可空, SET_NULL | 关联人员 |
| remark | varchar(200) | 可空 | 备注 |

**category 选项:** `gmv` / `commission` / `salary` / `bonus` / `equipment` / `ads` / `logistics` / `other`

**索引:** `date`, `(type, category)`, `(store, date)`

#### CommissionRule -- 佣金规则

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| name | varchar(100) | 非空 | 规则名称 |
| calc_type | varchar(10) | 默认 `percent` | 计算方式 (fixed/percent) |
| value | decimal(10,2) | 非空 | 佣金值 (金额或比例%) |
| min_gmv | decimal(12,2) | 默认 0 | 最低 GMV 门槛 |
| is_active | boolean | 默认 true | 是否启用 |

#### CommissionRecord -- 佣金记录

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| employee | FK -> Employee | **CASCADE**, 非空 | 员工 |
| period | varchar(20) | 非空 | 结算周期 (如 2026-06) |
| gmv | decimal(12,2) | 默认 0 | GMV |
| commission | decimal(10,2) | 默认 0 | 佣金金额 |
| rule | FK -> CommissionRule | 可空, SET_NULL | 佣金规则 |
| status | varchar(20) | 默认 `pending` | 状态 (pending/settled/cancelled) |
| settled_at | datetime | 可空 | 结算时间 |

**唯一约束:** `(employee, period)`

#### Contract -- 合同管理

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| employee | FK -> Employee | **CASCADE**, 非空 | 员工 |
| contract_type | varchar(20) | 默认 `labor` | 合同类型 |
| contract_no | varchar(50) | 可空 | 合同编号 |
| start_date | date | 非空 | 开始日期 |
| end_date | date | 非空 | 到期日期 |
| status | varchar(20) | 默认 `active` | 状态 |
| salary | decimal(10,2) | 默认 0 | 合同薪资 |
| attachment | url | 可空 | 合同附件 |

**contract_type:** `labor` / `service` / `anchor` / `brand`

**status:** `active` / `expiring` / `expired` / `terminated`

**索引:** `status`, `end_date`

---

### 培训与目标

#### TrainingCourse -- 培训课程

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| title | varchar(200) | 非空 | 课程名称 |
| description | text | 可空 | 课程简介 |
| trainer | FK -> Employee | 可空, SET_NULL | 讲师 |
| category | varchar(50) | 可空 | 分类 |
| duration_minutes | int | 默认 60 | 时长 (分钟) |
| status | varchar(20) | 默认 `draft` | 状态 (draft/active/completed) |
| start_date | date | 可空 | 开始日期 |
| material_url | url | 可空 | 课件链接 |

**反向关系:** `records` -- TrainingRecord (一对多)

#### TrainingRecord -- 培训记录

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| course | FK -> TrainingCourse | **CASCADE**, 非空 | 课程 |
| employee | FK -> Employee | **CASCADE**, 非空 | 学员 |
| score | decimal(5,2) | 默认 0 | 考核分数 |
| passed | boolean | 默认 false | 是否通过 |
| feedback | text | 可空 | 学员反馈 |
| completed_at | datetime | 可空 | 完成时间 |

**唯一约束:** `(course, employee)`

#### Goal -- 目标管理

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| employee | FK -> Employee | **CASCADE**, 非空 | 员工 |
| period_type | varchar(20) | 默认 `monthly` | 周期 (weekly/monthly/quarterly/yearly) |
| period | varchar(20) | 非空 | 周期值 (如 2026-06) |
| metric | varchar(20) | 非空 | 指标 (gmv/orders/hours/followers/conversion) |
| target_value | decimal(12,2) | 默认 0 | 目标值 |
| actual_value | decimal(12,2) | 默认 0 | 实际值 |
| status | varchar(20) | 默认 `active` | 状态 (active/completed/failed) |
| store | FK -> Store | 可空, SET_NULL | 关联店铺 |

**索引:** `(employee, period)`

---

### 市场与营销

#### Competitor -- 竞品信息

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| name | varchar(100) | 非空 | 竞品名称 |
| platform | varchar(20) | 默认 `douyin` | 平台 |
| account_id | varchar(100) | 可空 | 账号 ID |
| followers | int | 默认 0 | 粉丝数 |
| category | varchar(50) | 可空 | 主营类目 |

**反向关系:** `data` -- CompetitorData (一对多)

#### CompetitorData -- 竞品数据追踪

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| competitor | FK -> Competitor | **CASCADE**, 非空 | 竞品 |
| date | date | 非空 | 日期 |
| followers | int | 默认 0 | 粉丝数 |
| gmv_estimate | decimal(12,2) | 默认 0 | 预估 GMV |
| live_sessions | int | 默认 0 | 直播场次 |
| avg_viewers | int | 默认 0 | 场均观看 |
| hot_products | varchar(500) | 可空 | 热销商品 |

**唯一约束:** `(competitor, date)`

#### FanAnalysis -- 粉丝分析

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| store | FK -> Store | **CASCADE**, 非空 | 店铺 |
| date | date | 非空 | 日期 |
| total_fans | int | 默认 0 | 总粉丝数 |
| new_fans | int | 默认 0 | 新增粉丝 |
| lost_fans | int | 默认 0 | 流失粉丝 |
| male_ratio | decimal(5,2) | 默认 0 | 男性比例 (%) |
| age_18_24 | decimal(5,2) | 默认 0 | 18-24 岁 (%) |
| age_25_34 | decimal(5,2) | 默认 0 | 25-34 岁 (%) |
| age_35_44 | decimal(5,2) | 默认 0 | 35-44 岁 (%) |
| age_45plus | decimal(5,2) | 默认 0 | 45 岁以上 (%) |
| top_cities | varchar(200) | 可空 | TOP 城市 (JSON) |
| engagement_rate | decimal(5,2) | 默认 0 | 互动率 (%) |

**唯一约束:** `(store, date)`

#### Campaign -- 营销活动

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| name | varchar(200) | 非空 | 活动名称 |
| campaign_type | varchar(20) | 默认 `flash_sale` | 活动类型 |
| store | FK -> Store | 可空, SET_NULL | 店铺 |
| start_date | datetime | 非空 | 开始时间 |
| end_date | datetime | 非空 | 结束时间 |
| status | varchar(20) | 默认 `draft` | 状态 |
| target_gmv | decimal(12,2) | 默认 0 | 目标 GMV |
| actual_gmv | decimal(12,2) | 默认 0 | 实际 GMV |
| budget | decimal(10,2) | 默认 0 | 活动预算 |
| products | M2M -> Product | 可空 | 活动商品 |
| creator | FK -> Employee | 可空, SET_NULL | 创建人 |

**campaign_type:** `flash_sale` / `coupon` / `gift` / `discount` / `live_debut` / `festival`

---

### 系统管理

#### OperationLog -- 操作日志

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| user | varchar(50) | 非空 | 操作人 |
| action | varchar(50) | 非空 | 操作类型 |
| model_name | varchar(50) | 非空 | 目标模型 |
| object_id | varchar(50) | 可空 | 对象 ID |
| detail | text | 可空 | 详情 |
| ip | varchar(50) | 可空 | IP 地址 |
| created_at | datetime | 自动生成 | 创建时间 |

**排序:** 按 `created_at` 降序，仅保留最近 500 条。

#### BillboardConfig -- 大屏配置

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| name | varchar(100) | 非空 | 配置名称 |
| is_default | boolean | 默认 false | 是否默认配置 |
| show_gmv | boolean | 默认 true | 显示 GMV |
| show_orders | boolean | 默认 true | 显示订单 |
| show_viewers | boolean | 默认 true | 显示观看 |
| show_top_anchors | boolean | 默认 true | 显示主播排行 |
| show_platform_dist | boolean | 默认 true | 显示平台分布 |
| show_trend | boolean | 默认 true | 显示趋势 |
| refresh_interval | int | 默认 30 | 刷新间隔 (秒) |
| store | FK -> Store | 可空, SET_NULL | 限定店铺 |

#### Role -- 角色

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| name | varchar(50) | **唯一**, 非空 | 角色名 |
| description | varchar(200) | 可空 | 描述 |
| permissions | text | 可空 | 权限列表 (JSON 数组) |

#### UserRole -- 用户角色绑定

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| employee | FK -> Employee | **CASCADE**, 非空 | 员工 |
| role | FK -> Role | **CASCADE**, 非空 | 角色 |

**唯一约束:** `(employee, role)`

#### KOLContact -- 达人资源

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| name | varchar(100) | 非空 | 达人名称 |
| platform | varchar(20) | 默认 `douyin` | 平台 |
| account_id | varchar(100) | 可空 | 账号 ID |
| followers | int | 默认 0 | 粉丝数 |
| category | varchar(50) | 可空 | 领域 |
| contact_person | varchar(50) | 可空 | 联系人 |
| contact_phone | varchar(50) | 可空 | 联系方式 |
| fee_estimate | decimal(10,2) | 默认 0 | 预估合作费用 |
| status | varchar(20) | 默认 `contacting` | 状态 |
| our_contact | FK -> Employee | 可空, SET_NULL | 我方对接人 |

**status:** `contacting` / `negotiating` / `cooperating` / `completed`

#### ExportTask -- 数据导出任务

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK | 主键 |
| name | varchar(200) | 非空 | 导出名称 |
| export_type | varchar(50) | 非空 | 导出类型 (sessions/attendance/finance) |
| params | text | 可空 | 查询参数 (JSON) |
| file_url | url | 可空 | 文件链接 |
| file_size | bigint | 默认 0 | 文件大小 (bytes) |
| row_count | int | 默认 0 | 数据行数 |
| status | varchar(20) | 默认 `pending` | 状态 (pending/processing/done/failed) |
| creator | varchar(50) | 可空 | 创建人 |
| error_msg | text | 可空 | 错误信息 |
| completed_at | datetime | 可空 | 完成时间 |

---

## 关系图

```
                              +----------+
                              |  Brand   |
                              +----+-----+
                                   | 1:N
                              +----v-----+
                       +----->|  Store   |<-------+
                       |      +----+-----+        |
                       |           | 1:N          | M2M
                       |      +----v-----+        |
                       |      |StreamRoom|        |
                       |      +----------+        |
                       |                        +-v-------+
                  +----+-----+                  | Employee +----+
                  |   Team   | 1:N              +-+--+--+--+    |
                  +----------+         +---------+  |  |  +----+
                                      |            |  |       |
                              +-------v--+   +-----v+ | +--v--------+
                              | Anchor   |   |Schedule| | LeaveRequest|
                              | Profile  |   +---+---+ +-------------+
                              +----------+       | 1:N
                                            +----v-----+
                                            |Attendance|
                                            +----------+

                  +----------+ 1:N +----------+ 1:N +------------+
                  |LiveSession+--->|ProductSales|   | StreamReview|
                  +-----+----+    +----------+   +------------+
                        ^
                        | 1:N
                  +-----+-----+
                  | KPIConfig  |     +------------------+
                  +-----------+     |PerformanceReview |
                                    +------------------+
```

```
  +------------+ 1:N +-----------+     +------------+
  | Product    +---->|Campaign   |     | FinanceRecord|
  | Category   |     +-----------+     +------------+
  +-----+------+  M2M
        | 1:N
  +-----v------+
  | Product    +---+ InventoryAlert
  +------------+

  +--------------+ 1:N +-------------+
  | StreamScript +---->|ScriptSegment|
  +--------------+     +-------------+

  +----------+ 1:N +---------+
  |TaskBoard +---->|TaskCard |
  +----------+     +---------+

  +-----------+ 1:N +----------------+
  |Competitor +---->|CompetitorData  |
  +-----------+     +----------------+

  +-----------+     +---------------+
  |  Role     +---->|  UserRole     |
  +-----------+     +---------------+
```
