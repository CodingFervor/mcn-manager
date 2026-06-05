# 贡献指南

感谢你对 MCN 管家项目的关注！本文档将帮助你参与项目开发。

---

## 🚀 快速开始

### 1. Fork & Clone

```bash
git clone https://github.com/yourname/mcn-manager.git
cd mcn-manager
```

### 2. 创建分支

```bash
git checkout -b feature/your-feature-name
```

分支命名规范：

| 类型 | 格式 | 示例 |
|------|------|------|
| 新功能 | `feature/` | `feature/export-pdf` |
| 修复 | `fix/` | `fix/schedule-conflict` |
| 重构 | `refactor/` | `refactor/api-response-format` |
| 文档 | `docs/` | `docs/add-ai-docs` |

### 3. 开发环境

```bash
# 后端
cd anchor_system
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data

# 前端
cd frontend
npm install
npm run dev
```

---

## 📐 代码规范

### 后端 (Python)

- 遵循 [PEP 8](https://peps.python.org/pep-0008/)
- Model 字段必须加 `verbose_name`
- 新增 Model 必须在 `admin.py` 中注册
- ViewSet 业务逻辑放 `services.py`，View 只做参数解析和响应
- 使用 `select_related` / `prefetch_related` 避免 N+1 查询
- 高频查询字段添加数据库索引
- 写操作后调用 `invalidate_cache()` 清除相关缓存

**文件组织：**

```
新功能开发时需要创建/修改的文件：

models.py 或 models_extra.py    → 定义模型
serializers.py 或 serializers_extra.py → 序列化器
services.py                     → 业务逻辑 (可选)
views.py 或 views_extra.py      → 视图
urls.py                         → 路由注册
```

**示例 - 添加新模型：**

```python
# models_extra.py
class MyModel(models.Model):
    name = models.CharField('名称', max_length=100)
    status = models.CharField('状态', max_length=20, default='active')

    class Meta:
        verbose_name = '我的模型'
        ordering = ['-id']
        indexes = [models.Index(fields=['status'])]

# serializers_extra.py
class MyModelSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MyModel
        fields = '__all__'

# views_extra.py
class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer

# urls.py
router.register(r'my-models', MyModelViewSet)
```

### 前端 (Vue)

- 使用 `<script setup>` 语法
- 可复用逻辑提取到 `composables/`
- 重复 UI 提取到 `components/`
- 新页面放 `views/`，使用 defineAsyncComponent 懒加载
- API 调用统一在 `api.js` 中定义模块
- 图表使用 `composables/useChart.js` Hook

**新增页面 Checklist：**

```
1. views/NewPage.vue         → 页面组件
2. router/index.js           → 添加路由
3. api.js                    → 添加 API 模块
4. App.vue menuItems         → 添加菜单项
```

---

## 🎨 UI 设计规范

### 配色

使用 CSS 变量，不要硬编码颜色：

```css
/* 正确 */
color: var(--neon-cyan);
background: var(--bg-card);

/* 错误 */
color: #00e5ff;
background: rgba(20, 24, 56, 0.65);
```

### 统计卡片

使用 `StatCard` 组件：

```vue
<StatCard label="月度GMV" :value="'¥128.5万'" icon="💰" gradient="g1" />
```

gradient 可选: `g1`(紫粉) `g2`(青紫) `g3`(绿青) `g4`(橙粉) `g5`(黄橙) `g6`(彩虹)

### 图表

使用 `useChart` Hook：

```vue
<script setup>
import { useChart } from '../composables/useChart'
const { chartRef } = useChart(() => ({
  // ECharts option
}))
</script>
<template>
  <div ref="chartRef" style="width:100%;height:300px"></div>
</template>
```

---

## 🧪 测试

```bash
# 后端测试
python manage.py test

# 前端构建测试
cd frontend && npm run build
```

提交前确保：
- `python manage.py check` 无错误
- `npm run build` 构建成功
- 已有的 API 端点正常响应

---

## 📝 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <subject>

type: feat / fix / docs / style / refactor / perf / test / chore
scope: backend / frontend / ai / docs
```

**示例：**

```
feat(backend): 添加商品管理模块
fix(ai): 修复GMV预测在数据不足时的崩溃问题
docs: 更新API文档
refactor(frontend): 提取StatCard组件
perf(backend): Store overview 接口添加缓存
```

---

## 🔄 PR 流程

1. 确保 PR 只做一件事（功能/修复/重构，不混合）
2. 更新相关文档
3. 如果添加了新模型，运行 `python manage.py makemigrations`
4. PR 描述说明：做了什么、为什么、怎么测试

**PR 模板：**

```markdown
## 变更说明
简述做了什么

## 变更类型
- [ ] 新功能
- [ ] Bug修复
- [ ] 重构
- [ ] 文档
- [ ] 性能优化

## 测试
- [ ] python manage.py check 通过
- [ ] npm run build 通过
- [ ] 手动测试通过

## 截图
(如有UI变更请附截图)
```

---

## ❓ 有问题？

- 提交 [Issue](https://github.com/yourname/mcn-manager/issues)
- 描述问题、复现步骤、期望行为
- 附上错误日志或截图
