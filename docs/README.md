# MCN 管家 — 直播电商代运营管理系统

> 全栈管理系统：Django 6 + Vue 3 + AI 智能引擎
> 40个数据模型 · 70+ API接口 · 21个前端页面 · 6大AI功能

---

## 功能概览

### 核心业务
- 数据驾驶舱 / 实时大屏
- 店铺管理 (多平台: 抖音/快手/淘宝/小红书/拼多多/京东/视频号)
- 人员管理 (主播/运营/经理/助理)
- 智能排班 (批量排班/冲突检测)
- 考勤打卡 (自动迟到检测)
- 直播业绩 (GMV/订单/转化率)
- 绩效考核 (S/A/B/C/D评级/奖金计算)

### AI 智能中心
- GMV 预测 (线性回归+移动平均+季节性调整)
- 智能排班推荐 (贪心匹配+疲劳惩罚)
- 主播画像 (五维雷达+AI洞察)
- 异常检测 (Z-Score+规则引擎)
- 运营建议 (25条实时告警)
- 智能匹配 (主播-店铺最佳组合)

### 扩展功能
- 商品库管理 + 库存预警
- 直播脚本 + 话术库
- 任务看板 (四列: 待办/进行中/已完成/阻塞)
- 消息中心 + 未读提醒
- 财务中心 (收支/佣金/合同)
- 营销活动管理
- 竞品监控 + 粉丝分析
- 达人/KOL对接
- 培训管理 + 目标管理
- 数据导出 (CSV)
- 操作日志 + 权限管理

---

## 快速开始

### 后端

```bash
cd anchor_system
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data          # 导入示例数据 (可选)
python manage.py runserver 8000     # 开发模式
```

### 前端

```bash
cd frontend
npm install
npm run dev                         # 访问 http://127.0.0.1:5173
```

### 生产构建

```bash
# 后端
cd anchor_system
python -m waitress --port=8000 backend.wsgi:application

# 前端
cd frontend
npm run build                       # 产物输出到 dist/
```

---

## 技术架构

```
Vue 3 + Element Plus + ECharts + Pinia + Vue Router
         │  Vite Proxy
Django 6 + DRF + JWT + Waitress
         │
Service 层 (缓存 + 缓存失效)
         │
AI Engine (6大智能算法)
         │
SQLite WAL (40个模型 + 20+索引)
```

---

## 性能指标

| 指标 | 数值 |
|------|------|
| Dashboard 首次 | ~10ms |
| Dashboard 缓存 | ~2ms |
| AI Insights 缓存 | ~3ms |
| 前端 Build | ~2s |
| 模型总数 | 40 |
| API 端点 | 70+ |
| 数据库索引 | 20+ |

---

## 文档

| 文档 | 路径 |
|------|------|
| 系统架构 | [docs/architecture.md](docs/architecture.md) |
| API 接口 | [docs/api.md](docs/api.md) |
| 数据模型 | [docs/models.md](docs/models.md) |
| AI 引擎 | [docs/ai-engine.md](docs/ai-engine.md) |
| 前端页面 | [docs/frontend.md](docs/frontend.md) |
| 部署运维 | [docs/deployment.md](docs/deployment.md) |

---

## 项目结构

```
anchor_system/          # Django 后端
├── backend/            # 项目配置
├── scheduling/         # 主应用 (模型/视图/服务/AI引擎)
└── db.sqlite3          # SQLite 数据库

frontend/               # Vue 前端
├── src/
│   ├── views/          # 21个页面
│   ├── components/     # 可复用组件
│   ├── composables/    # 通用Hook
│   ├── stores/         # Pinia Store
│   └── router/         # 路由配置
└── docs/               # 项目文档
```

---

## 默认账号

种子数据创建的管理员: `admin` / `admin123`
