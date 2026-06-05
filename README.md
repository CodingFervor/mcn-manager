<div align="center">

# MCN 管家

### 🎬 直播电商代运营管理系统

**一个开箱即用的全栈 MCN 管理系统，覆盖直播电商全链路业务场景**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)](https://djangoproject.com)
[![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[功能预览](#-功能预览) · [快速开始](#-快速开始) · [技术架构](#-技术架构) · [API 文档](docs/api.md) · [部署指南](docs/deployment.md) · [贡献指南](CONTRIBUTING.md)

---

</div>

## 📸 界面预览

| 数据驾驶舱 | AI 智能中心 |
|:---:|:---:|
| 实时 GMV / 平台分布 / 主播排行 / 趋势分析 | GMV 预测 / 智能排班 / 主播画像 / 异常检测 |
| ![Dashboard](docs/screenshots/dashboard.png) | ![AI Center](docs/screenshots/ai.png) |

| 店铺管理 | 智能排班 |
|:---:|:---:|
| 多平台店铺聚合管理 / GMV 达成率可视化 | 周视图网格 / 批量排班 / 冲突检测 |
| ![Stores](docs/screenshots/stores.png) | ![Schedules](docs/screenshots/schedules.png) |

---

## ✨ 功能预览

### 🧠 AI 智能引擎 (6大能力)

| 功能 | 说明 |
|------|------|
| **GMV 预测** | 线性回归 + 移动平均 + 季节性调整，预测未来1-30天GMV |
| **智能排班** | 贪心匹配算法，考虑主播表现/疲劳度/迟到率，自动推荐最优排班 |
| **主播画像** | 五维能力雷达 (销售力/流量力/转化力/稳定性/成长性) + AI洞察 |
| **异常检测** | Z-Score 统计 + 规则引擎，自动发现 GMV/流量/转化异常 |
| **运营建议** | 25+ 条实时告警 (店铺健康/主播疲劳/合同到期/考勤/GMV趋势) |
| **智能匹配** | 主播-店铺组合评分，找到最佳搭档 |

> 纯算法引擎，无需外部 AI API，开箱即用。

### 🏢 核心业务 (8大模块)

| 模块 | 页面 | 核心能力 |
|------|------|---------|
| 数据驾驶舱 | Dashboard | 4维统计卡 / 7天GMV趋势 / 平台分布 / TOP8主播 / 今日排班 |
| 店铺管理 | Stores | 多平台 (抖音/快手/淘宝等) / GMV达成率 / 搜索筛选 / CRUD |
| 人员管理 | Employees | 双视图 (卡片+表格) / 主播档案 / 角色筛选 / 团队管理 |
| 智能排班 | Schedules | 周视图网格 / 批量排班 / 冲突检测 / 今日高亮 |
| 考勤打卡 | Attendance | 自动迟到检测 / 考勤统计 / 迟到TOP5 / 请假审批 |
| 直播业绩 | Sessions | 每日GMV趋势 / 主播排行 / 完整直播记录CRUD |
| 绩效考核 | Reviews | S/A/B/C/D评级 / 自动计算 (GMV 60%+出勤 20%+时长 10%+订单 10%) / 奖金 |
| 班次配置 | Shifts | 卡片视图 / 5种班次类型 / 自定义时间段 |

### 🚀 扩展功能 (12大模块)

| 模块 | 页面 | 说明 |
|------|------|------|
| 商品管理 | Products | 商品库CRUD / 库存预警 / 佣金设置 |
| 直播工具 | Scripts | 直播脚本 (段落式) / 话术库 (场景分类) |
| 任务看板 | Tasks | 四列看板 (待办/进行中/已完成/阻塞) |
| 消息中心 | Notifications | 系统通知 / 排班提醒 / 未读标记 / 全部已读 |
| 财务中心 | Finance | 收支管理 / 佣金结算 / 合同管理 (到期预警) |
| 营销活动 | Campaigns | 活动管理 / 目标GMV / 完成率追踪 |
| 竞品监控 | Competitor | 竞品信息 / 数据追踪 / 粉丝分析 |
| 达人对接 | KOL | KOL资源管理 / 合作状态 / 费用评估 |
| 培训目标 | Training | 培训课程 / 考核记录 / 目标看板 (周/月/季/年) |
| 实时大屏 | Billboard | TV投屏模式 / 30s自动刷新 / TOP排行 |
| 系统工具 | Settings | CSV数据导出 / 操作日志 |
| 权限管理 | - | 角色定义 / 权限绑定 (预留) |

---

## 🛠 技术架构

```
┌──────────────────────────────────────────────────┐
│                    前端层                          │
│   Vue 3 · Element Plus · ECharts · Pinia · Router │
│          Vite Build · Tree-shaking · Code-split   │
├──────────────────────────────────────────────────┤
│                    网关层                          │
│        Vite Proxy · Waitress · Django WSGI        │
│        JWT 认证 · 限流 100/min · CORS              │
├──────────────────────────────────────────────────┤
│                   Service 层                       │
│   Dashboard · Store · Employee · Schedule · ...   │
│        缓存装饰器 · 写操作自动缓存失效               │
├──────────────────────────────────────────────────┤
│                 AI Engine 智能层                    │
│   GMV预测 · 智能排班 · 主播画像 · 异常检测          │
│        运营建议 · 智能匹配 · 结果缓存               │
├──────────────────────────────────────────────────┤
│                  数据层                             │
│   40 个 Model · 20+ 索引 · select_related          │
│   SQLite WAL · 64MB Cache · 256MB mmap            │
└──────────────────────────────────────────────────┘
```

| 层 | 技术 | 说明 |
|---|------|------|
| 前端 | Vue 3 + Element Plus | Composition API · defineAsyncComponent 按需加载 |
| 图表 | ECharts 6 | Tree-shaking (仅引入 BarChart/LineChart/PieChart) |
| 状态 | Pinia | 全局 Dashboard 缓存 · 30s 客户端 TTL |
| 路由 | Vue Router 4 | createWebHistory · lazy loading · fade transition |
| 构建 | Vite 8 | manualChunks 分包 (element-plus/echarts/vendor) |
| 后端 | Django 6 + DRF | Service 层分离 · JSON-only · 分页50条 |
| 缓存 | LocMemCache → Redis | 10000条上限 · 写操作自动失效 |
| 数据库 | SQLite WAL → PostgreSQL | 64MB cache · 256MB mmap · 30s timeout |
| WSGI | Waitress | Windows 友好 · 生产就绪 |

---

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+ / npm 9+

### 一键启动

```bash
# 1. 克隆项目
git clone https://github.com/yourname/mcn-manager.git
cd mcn-manager

# 2. 后端
cd anchor_system
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data    # 可选: 导入示例数据 (20品牌/50店铺/100主播)
python manage.py runserver 8000

# 3. 前端 (新终端)
cd frontend
npm install
npm run dev    # 访问 http://127.0.0.1:5173
```

### 默认账号

种子数据创建的管理员: `admin` / `admin123`

### Docker 部署 (规划中)

```bash
docker-compose up -d
```

---

## 📊 性能

| 指标 | 数值 | 说明 |
|------|------|------|
| Dashboard API | 2ms | 缓存命中 |
| Store Overview | 2.5ms | 缓存命中 |
| AI Insights | 3ms | 缓存命中 (冷启动 ~500ms) |
| AI Schedule | 2.5ms | 缓存命中 (冷启动 ~240ms) |
| AI Predict | 6ms | 冷启动 |
| 前端 Build | 1.6s | Vite + Tree-shaking |
| 健康检查 | 1ms | DB + Cache |

---

## 📁 项目结构

```
mcn-manager/
├── anchor_system/              # 后端 Django 项目
│   ├── backend/
│   │   ├── settings.py         # 配置 (DB/Cache/Limit/Log)
│   │   ├── middleware.py        # 请求计时 + 健康检查
│   │   └── urls.py              # 根路由
│   ├── scheduling/
│   │   ├── models.py            # 核心模型 (13个)
│   │   ├── models_extra.py      # 扩展模型 (27个)
│   │   ├── services.py          # Service 业务层
│   │   ├── ai_engine.py         # AI 智能引擎
│   │   ├── views.py             # 核心视图
│   │   ├── views_extra.py       # 扩展视图
│   │   ├── ai_views.py          # AI 接口
│   │   ├── serializers.py       # 核心序列化器
│   │   └── serializers_extra.py # 扩展序列化器
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                   # 前端 Vue 项目
│   ├── src/
│   │   ├── views/               # 21 个页面
│   │   ├── components/          # 可复用组件 (StatCard/PageHeader/ChartWrap)
│   │   ├── composables/         # Hooks (useApi/useChart)
│   │   ├── stores/              # Pinia Store
│   │   ├── router/              # 路由配置
│   │   ├── api.js               # API 模块 (20+)
│   │   ├── echarts.js           # ECharts Tree-shaking
│   │   ├── style.css            # 暗色霓虹设计系统
│   │   ├── main.js              # 入口
│   │   └── App.vue              # 布局外壳
│   ├── vite.config.js
│   └── package.json
│
├── docs/                        # 文档
│   ├── architecture.md          # 系统架构
│   ├── api.md                   # API 接口文档
│   ├── models.md                # 数据模型文档
│   ├── ai-engine.md             # AI 引擎文档
│   ├── frontend.md              # 前端页面文档
│   ├── deployment.md            # 部署运维文档
│   └── screenshots/             # 截图
│
├── CONTRIBUTING.md              # 贡献指南
├── CHANGELOG.md                 # 更新日志
├── LICENSE                      # MIT 许可证
└── README.md                    # 本文件
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [系统架构](docs/architecture.md) | 分层架构、技术选型、项目结构 |
| [快速开始](#-快速开始) | 安装、配置、启动 |
| [API 文档](docs/api.md) | 70+ 接口完整说明 |
| [数据模型](docs/models.md) | 40 个模型字段定义 |
| [AI 引擎](docs/ai-engine.md) | 6 大算法原理与使用 |
| [前端页面](docs/frontend.md) | 21 个页面、设计系统、组件 |
| [部署指南](docs/deployment.md) | 生产部署、Nginx、PostgreSQL、Redis |
| [贡献指南](CONTRIBUTING.md) | 如何参与开发 |
| [更新日志](CHANGELOG.md) | 版本历史 |

---

## 🤝 贡献

欢迎贡献！请阅读 [贡献指南](CONTRIBUTING.md)。

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

---

## 📄 许可证

[MIT License](LICENSE)

---

## 🙏 致谢

- [Django](https://www.djangoproject.com/) — Web 框架
- [Vue.js](https://vuejs.org/) — 前端框架
- [Element Plus](https://element-plus.org/) — UI 组件库
- [ECharts](https://echarts.apache.org/) — 数据可视化
- [Waitress](https://docs.pylonsproject.org/projects/waitress/) — WSGI 服务器

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

</div>
