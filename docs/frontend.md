# MCN Manager 前端架构文档

> 版本: 1.0 | Vue 3 + Vite + Element Plus + ECharts | 暗色霓虹主题

---

## 目录

- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [页面清单](#页面清单)
- [设计系统](#设计系统)
- [组件库](#组件库)
- [Composables](#composables)
- [状态管理](#状态管理)
- [路由配置](#路由配置)
- [API 层](#api-层)
- [构建与部署](#构建与部署)

---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | 3.x | 前端框架 (Composition API) |
| Vite | 最新 | 构建工具 + 开发服务器 |
| Vue Router | 4.x | 单页路由 |
| Pinia | 最新 | 状态管理 |
| Element Plus | 最新 | UI 组件库 |
| ECharts | 5.x | 数据可视化 |
| Axios | 最新 | HTTP 客户端 |

---

## 项目结构

```
frontend/
  src/
    main.js                    # 应用入口
    App.vue                    # 根组件 (侧边栏 + 顶栏 + 路由视图)
    style.css                  # 全局样式 (设计变量 + 霓虹主题)
    api.js                     # API 请求层 (统一封装)
    echarts.js                 # ECharts 按需导入配置
    router/
      index.js                 # 路由配置 (21 个懒加载路由)
    stores/
      app.js                   # Pinia 全局 Store (Dashboard 缓存)
    composables/
      useApi.js                # 异步请求 Hook
      useChart.js              # ECharts 生命周期 Hook
    components/
      StatCard.vue             # 渐变统计卡片
      PageHeader.vue           # 页面标题组件
      ChartWrap.vue            # ECharts 包装组件
    views/
      Dashboard.vue            # 数据驾驶舱
      AI.vue                   # AI 智能中心
      Stores.vue               # 店铺管理
      Employees.vue            # 人员管理
      Products.vue             # 商品管理
      Schedules.vue            # 智能排班
      Attendance.vue           # 考勤打卡
      Sessions.vue             # 直播业绩
      Scripts.vue              # 直播工具 (脚本 + 话术)
      Reviews.vue              # 绩效考核
      Shifts.vue               # 班次配置
      Finance.vue              # 财务中心
      Campaigns.vue            # 营销活动
      Tasks.vue                # 任务看板
      Notifications.vue        # 消息中心
      Competitor.vue           # 竞品与粉丝
      KOL.vue                  # 达人对接
      Training.vue             # 培训与目标
      Billboard.vue            # 实时大屏
      Settings.vue             # 系统工具
```

---

## 页面清单

共 21 个页面，全部使用路由懒加载，切换带 fade 过渡动画。

| # | 路径 | 页面名 | 核心功能 |
|---|------|--------|---------|
| 1 | `/dashboard` | 数据驾驶舱 | 4 统计卡 + GMV 趋势图 + 平台分布饼图 + TOP8 主播 + 今日排班 |
| 2 | `/billboard` | 实时大屏 | TV 投屏模式，30s 自动刷新，GMV/店铺/出勤率 + 趋势图 + 排行 |
| 3 | `/ai` | AI 智能中心 | 6 个 Tab: 运营建议/GMV 预测/智能排班/主播画像/异常检测/智能匹配 |
| 4 | `/stores` | 店铺管理 | CRUD 表格 + 4 统计卡 + TOP12 店铺 GMV 图表 + 搜索筛选 |
| 5 | `/employees` | 人员管理 | CRUD + 双视图 (卡片/表格) + 主播档案 + 搜索筛选 |
| 6 | `/products` | 商品管理 | CRUD 表格 + 库存预警标识 + 佣金设置 |
| 7 | `/schedules` | 智能排班 | 周视图网格 + 批量排班弹窗 + 今日高亮 |
| 8 | `/attendance` | 考勤打卡 | 打卡按钮 + 考勤统计图 + 迟到 TOP5 + 请假管理 |
| 9 | `/sessions` | 直播业绩 | 4 统计卡 + 每日 GMV 趋势图 + 主播排行 + 直播记录 CRUD |
| 10 | `/scripts` | 直播工具 | 双 Tab: 直播脚本管理 + 话术库 |
| 11 | `/reviews` | 绩效考核 | 评级分布饼图 + TOP10 + 考核记录 + KPI 配置 |
| 12 | `/shifts` | 班次配置 | CRUD + 卡片视图 + 表格视图 |
| 13 | `/finance` | 财务中心 | 三 Tab: 收支管理/合同管理/佣金结算 |
| 14 | `/campaigns` | 营销活动 | 活动卡片列表 + 完成率进度条 + 状态统计 |
| 15 | `/tasks` | 任务看板 | 四列看板 (待办/进行中/已完成/阻塞) + 拖拽移动 |
| 16 | `/notifications` | 消息中心 | 消息列表 + 未读标记 + 全部已读按钮 |
| 17 | `/competitor` | 竞品与粉丝 | 双 Tab: 竞品监控列表 + 粉丝趋势图 |
| 18 | `/kol` | 达人对接 | 达人卡片列表 + 状态筛选 + 粉丝数格式化 |
| 19 | `/training` | 培训与目标 | 双 Tab: 培训课程列表 + 目标看板 |
| 20 | `/settings` | 系统工具 | 数据导出 (CSV 下载) + 操作日志表格 |

---

## 设计系统

### 暗色霓虹主题

应用采用深色科技感主题，配合霓虹色系营造专业数据可视化氛围。

#### 主色板

| CSS 变量 | 色值 | 用途 |
|----------|------|------|
| `--neon-purple` | `#7c5cff` | 主色调，侧边栏强调，品牌色 |
| `--neon-pink` | `#ff4d9e` | 危险/警告，删除操作 |
| `--neon-cyan` | `#00e5ff` | 信息/高亮，搜索框，系统状态 |
| `--neon-green` | `#00ff9d` | 成功/正向，在线状态，GMV 上涨 |
| `--neon-yellow` | `#ffd23f` | 警告提示，中等优先级 |
| `--neon-orange` | `#ff7a45` | 次级警告，库存预警 |

#### 背景色

| CSS 变量 | 色值 | 用途 |
|----------|------|------|
| `--bg-primary` | `#0a0e27` | 页面主背景 |
| `--bg-card` | `rgba(20,24,56,0.65)` | 卡片背景 (半透明毛玻璃) |

#### 文字色

| CSS 变量 | 色值 | 用途 |
|----------|------|------|
| `--text-primary` | `#e8eaf6` | 主文字 |
| `--text-secondary` | `#9fa8da` | 次级文字 |
| `--text-muted` | `#5c6bc0` | 占位文字/说明 |

#### 边框

| CSS 变量 | 色值 | 用途 |
|----------|------|------|
| `--border-glow` | `rgba(124,92,255,0.2)` | 卡片/区域边框 (微光效果) |

### 渐变色系

StatCard 组件使用 6 组渐变色:

| CSS 类名 | 渐变方向 | 色值 |
|----------|---------|------|
| `.g1` | 紫色 -> 粉色 | `#7c5cff` -> `#ff4d9e` |
| `.g2` | 青色 -> 紫色 | `#00e5ff` -> `#7c5cff` |
| `.g3` | 绿色 -> 青色 | `#00ff9d` -> `#00e5ff` |
| `.g4` | 橙色 -> 粉色 | `#ff7a45` -> `#ff4d9e` |
| `.g5` | 黄色 -> 橙色 | `#ffd23f` -> `#ff7a45` |
| `.g6` | 粉色 -> 紫色 -> 青色 | 三色渐变 |

### 毛玻璃效果

卡片和顶栏使用 `backdrop-filter: blur()` 实现毛玻璃效果:

```css
background: rgba(20, 24, 56, 0.65);
backdrop-filter: blur(20px);
border: 1px solid var(--border-glow);
border-radius: 16px;
```

### 侧边栏

侧边栏使用深色渐变背景:

```css
background: linear-gradient(180deg, #0d1230 0%, #1a1f4a 100%);
```

Logo 区域使用 `filter: drop-shadow()` 实现图标发光效果。

---

## 组件库

### StatCard -- 渐变统计卡片

**文件:** `components/StatCard.vue`

数据驾驶舱等页面使用的核心统计展示卡片，支持渐变背景和趋势标签。

**Props:**

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| label | string | 是 | 指标名称 (如 "月度GMV") |
| value | string/number | 是 | 数值显示 |
| sub | string | 否 | 附加说明文字 |
| icon | string | 否 | Emoji 图标 |
| gradient | string | 否 | 渐变色方案 (g1-g6, 默认 g1) |
| trend | string | 否 | 趋势标签 (如 "+12.5%") |

**使用示例:**

```vue
<StatCard
  label="月度GMV"
  :value="3850000"
  icon="💰"
  gradient="g1"
  sub="较上月 +15.2%"
  trend="+15.2%"
/>
```

**CSS 类名:** `.stat-card.g1` ~ `.stat-card.g6`，每个类名对应一组渐变背景。

---

### PageHeader -- 页面标题

**文件:** `components/PageHeader.vue`

统一的页面标题栏组件。

**Props:**

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 页面标题 |
| subtitle | string | 否 | 副标题/描述 |

**使用示例:**

```vue
<PageHeader title="店铺管理" subtitle="管理所有平台店铺和运营数据" />
```

---

### ChartWrap -- ECharts 包装组件

**文件:** `components/ChartWrap.vue`

封装 ECharts 初始化、ResizeObserver 自适应和销毁生命周期。

**Props:**

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| optionFn | Function | 是 | 返回 ECharts option 的函数 |
| height | string | 否 | 图表高度 (默认 `320px`) |

**Exposed 方法:**

| 方法 | 说明 |
|------|------|
| `updateChart(opts)` | 更新图表配置 (合并模式) |

**使用示例:**

```vue
<ChartWrap
  :optionFn="() => ({
    xAxis: { type: 'category', data: dates },
    yAxis: { type: 'value' },
    series: [{ type: 'line', data: gmvValues }]
  })"
  height="400px"
/>
```

---

## Composables

### useApi -- 异步请求 Hook

**文件:** `composables/useApi.js`

统一的异步数据请求封装，提供响应式状态管理。

**签名:**

```javascript
function useApi(apiFn, options = {}): {
  data: Ref,
  loading: Ref<boolean>,
  error: Ref<Error | null>,
  execute: (...args) => Promise,
  refresh: (...args) => Promise
}
```

**参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| apiFn | Function | 返回 Promise 的 API 调用函数 |
| options.default | any | data 的初始值 |
| options.immediate | boolean | 是否在 onMounted 自动调用 (默认 true) |
| options.onError | Function | 错误回调 |

**使用示例:**

```vue
<script setup>
import { useApi } from '../composables/useApi'
import { SessionAPI } from '../api'

const { data: sessions, loading, execute: fetchSessions } = useApi(
  () => SessionAPI.list({ start: '2026-06-01' }),
  { immediate: true }
)
</script>
```

---

### useChart -- ECharts 生命周期 Hook

**文件:** `composables/useChart.js`

管理 ECharts 实例的创建、更新、自适应和销毁。

**签名:**

```javascript
function useChart(optionsFn): {
  chartRef: Ref<HTMLElement | null>,
  initChart: () => void,
  updateChart: (opts) => void,
  getChart: () => ECharts | null
}
```

**特性:**

| 功能 | 实现 |
|------|------|
| 自动初始化 | onMounted + nextTick |
| 自适应大小 | ResizeObserver 监听容器 |
| 自动销毁 | onUnmounted 时 dispose |
| 防止内存泄漏 | 销毁时断开 ResizeObserver |

**使用示例:**

```vue
<script setup>
import { useChart } from '../composables/useChart'

const { chartRef, updateChart } = useChart(() => ({
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed'] },
  yAxis: { type: 'value' },
  series: [{ data: [150, 230, 224], type: 'line' }]
}))
</script>

<template>
  <div ref="chartRef" style="width: 100%; height: 300px"></div>
</template>
```

---

## 状态管理

### useAppStore -- 全局应用 Store

**文件:** `stores/app.js`

Pinia Store，管理 Dashboard 数据的全局缓存。

**状态:**

| 字段 | 类型 | 说明 |
|------|------|------|
| dashboard | ref(null) | 驾驶舱数据 |
| loading | ref(false) | 加载状态 |
| lastFetch | ref(0) | 上次获取时间戳 |

**缓存策略:** 客户端 30 秒 TTL (CACHE_TTL = 30000ms)。

**Actions:**

| 方法 | 参数 | 说明 |
|------|------|------|
| `fetchDashboard` | `force?: boolean` | 获取驾驶舱数据 (30s 缓存) |
| `invalidateDashboard` | 无 | 强制清除缓存 |

**使用示例:**

```javascript
import { useAppStore } from '../stores/app'

const store = useAppStore()
const data = await store.fetchDashboard()
```

**缓存判断逻辑:**

```javascript
if (!force && dashboard.value && Date.now() - lastFetch.value < 30000) {
  return dashboard.value  // 返回缓存
}
// 否则重新请求
```

---

## 路由配置

**文件:** `router/index.js`

使用 Vue Router 的 `createWebHistory` 模式，所有页面均为懒加载。

### 路由表

| 路径 | name | 页面 | meta.title |
|------|------|------|-----------|
| `/` | -- | 重定向到 `/dashboard` | -- |
| `/dashboard` | dashboard | Dashboard.vue | 数据驾驶舱 |
| `/ai` | ai | AI.vue | AI智能中心 |
| `/stores` | stores | Stores.vue | 店铺管理 |
| `/employees` | employees | Employees.vue | 人员管理 |
| `/products` | products | Products.vue | 商品管理 |
| `/schedules` | schedules | Schedules.vue | 智能排班 |
| `/attendance` | attendance | Attendance.vue | 考勤打卡 |
| `/sessions` | sessions | Sessions.vue | 直播业绩 |
| `/scripts` | scripts | Scripts.vue | 直播工具 |
| `/reviews` | reviews | Reviews.vue | 绩效考核 |
| `/shifts` | shifts | Shifts.vue | 班次配置 |
| `/finance` | finance | Finance.vue | 财务中心 |
| `/campaigns` | campaigns | Campaigns.vue | 营销活动 |
| `/tasks` | tasks | Tasks.vue | 任务看板 |
| `/notifications` | notifications | Notifications.vue | 消息中心 |
| `/competitor` | competitor | Competitor.vue | 竞品与粉丝 |
| `/kol` | kol | KOL.vue | 达人对接 |
| `/training` | training | Training.vue | 培训与目标 |
| `/billboard` | billboard | Billboard.vue | 实时大屏 |
| `/settings` | settings | Settings.vue | 系统工具 |

### 后置钩子

```javascript
router.afterEach((to) => {
  document.title = `${to.meta.title || 'MCN管家'} - MCN 管家`
})
```

### 页面过渡

根组件 `<router-view>` 使用 `transition` 包裹，切换时应用 fade 动画:

```vue
<router-view v-slot="{ Component }">
  <transition name="fade" mode="out-in">
    <component :is="Component" />
  </transition>
</router-view>
```

---

## API 层

**文件:** `api.js`

统一封装所有后端 API 调用，基于 Axios 实例。

### Axios 实例配置

```javascript
const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})
```

### 请求拦截器

自动增加全局 loading 计数。

### 响应拦截器

- 成功响应: 自动解包 `res.data`
- 错误响应: 提取 `detail` 或 `message` 字段，非 400 状态码自动弹出 ElMessage 错误提示
- `wrap()` 辅助函数: 自动解包分页响应 (`data.results || data`)

### API 模块清单

| 模块名 | 方法数 | 说明 |
|--------|--------|------|
| BrandAPI | 4 | list, create, update, remove |
| StoreAPI | 5 | list, overview, create, update, remove |
| TeamAPI | 4 | list, create, update, remove |
| RoomAPI | 3 | list, create, remove |
| EmployeeAPI | 5 | list, stats, create, update, remove |
| ShiftAPI | 4 | list, create, update, remove |
| ScheduleAPI | 5 | list, weekly, create, update, remove, batchCreate |
| AttendanceAPI | 4 | list, clockIn, clockOut, summary |
| LeaveAPI | 4 | list, create, approve, reject |
| SessionAPI | 5 | list, dailyGmv, topAnchors, create, update, remove |
| ReviewAPI | 2 | list, calculate |
| KPIConfigAPI | 4 | list, create, update, remove |
| DashboardAPI | 1 | overview |
| AI_API | 6 | predict, schedule, anchor, anomaly, insights, match |
| ProductAPI | 4 | list, create, update, remove |
| ScriptAPI | 3 | list, create, salesList |
| TaskAPI | 4 | list, create, createCard, move |
| NotificationAPI | 3 | list, readAll, unreadCount |
| FinanceAPI | 2 | list, summary |
| ContractAPI | 1 | list |
| CommissionAPI | 2 | list, settle |
| TrainingAPI | 1 | list |
| GoalAPI | 1 | board |
| CompetitorAPI | 1 | list |
| FanAPI | 1 | trend |
| CampaignAPI | 1 | list |
| KOLAPI | 1 | list |
| BillboardAPI | 1 | data |
| ExportAPI | 2 | list, create |

### 使用示例

```javascript
import { SessionAPI, AI_API } from '../api'

// 获取直播记录
const sessions = await SessionAPI.list({ start: '2026-06-01', end: '2026-06-30' })

// GMV 预测
const prediction = await AI_API.predict({ days: 7, store_id: 1 })

// 上班打卡
await AttendanceAPI.clockIn({
  employee_id: 5,
  schedule_id: 12,
  location: '公司总部'
})
```

---

## 构建与部署

### 开发环境

```bash
cd frontend
npm install
npm run dev
```

Vite 开发服务器默认启动于 `http://127.0.0.1:5173`，自动代理 API 请求到 `http://127.0.0.1:8000`。

### 生产构建

```bash
npm run build
```

产物输出到 `dist/` 目录，包含:
- `index.html` -- SPA 入口
- `assets/` -- JS/CSS/图片等静态资源 (带 hash)

### Vite 代理配置

开发环境通过 Vite 的 `proxy` 配置解决跨域:

```javascript
// vite.config.js (示例)
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
```

生产环境通过 Nginx 反向代理实现，详见 [部署文档](deployment.md)。
