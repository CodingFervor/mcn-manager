# 更新日志

所有重要变更记录在此文件中。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/)。

---

## [2.0.0] - 2026-06-05

### 新增

#### AI 智能引擎
- GMV 预测 (线性回归 + 移动平均 + 季节性调整)
- 智能排班推荐 (贪心匹配 + 疲劳惩罚 + 迟到惩罚)
- 主播画像分析 (五维雷达: 销售/流量/转化/稳定/成长)
- 异常检测 (Z-Score + 规则引擎)
- 运营建议引擎 (25+ 条实时告警)
- 主播-店铺智能匹配

#### 扩展功能 (20个)
- 商品库管理 + 库存预警
- 直播脚本 (段落式) + 话术库
- 直播复盘
- 任务看板 (四列: 待办/进行中/已完成/阻塞)
- 消息中心 + 未读提醒
- 财务报表 (收支/佣金/合同)
- 培训管理 + 目标管理
- 竞品监控 + 粉丝分析
- 营销活动管理
- 达人/KOL对接
- 数据导出 (CSV)
- 实时大屏 (TV投屏)
- 权限管理 (角色/权限)
- 操作日志

#### 架构升级
- Service 层分离 (业务逻辑与 View 解耦)
- Vue Router 替换条件渲染
- Pinia 状态管理
- Element Plus 按需自动导入 (unplugin-auto-import)
- 可复用组件 (StatCard / PageHeader / ChartWrap)
- Composables (useApi / useChart)
- 请求计时中间件 + X-Response-Time 头
- 健康检查端点 GET /api/health/
- 请求限流 100次/分钟
- 慢请求日志告警 (>100ms INFO, >500ms WARNING)
- 写操作自动缓存失效
- requirements.txt

### 优化
- ECharts Tree-shaking (仅引入 BarChart/LineChart/PieChart)
- Vite manualChunks 分包 (element-plus / echarts / vendor)
- defineAsyncComponent 按需加载所有页面
- SQLite WAL 模式 + PRAGMA 优化
- 18 个数据库索引
- 全部 ViewSet 添加 select_related / prefetch_related
- Store overview N+1 修复 (150+ 查询 → 3 查询)
- Dashboard 响应 300ms → 2ms
- AI 接口结果缓存 (120-180s)

---

## [1.0.0] - 2026-05-20

### 新增
- 核心模型: Brand, Store, Team, StreamRoom, Employee, AnchorProfile, Shift, Schedule, Attendance, LeaveRequest, LiveSession, ProductSales, KPIConfig, PerformanceReview (13个)
- 8 个页面: Dashboard, Stores, Employees, Schedules, Attendance, Sessions, Reviews, Shifts
- 15 个 ViewSet (完整 CRUD)
- JWT 认证
- 种子数据管理命令 (seed_data)
- 暗色霓虹 UI 主题
