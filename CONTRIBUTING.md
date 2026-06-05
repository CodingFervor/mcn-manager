# Contributing Guide

Thank you for your interest in the MCN Manager project! This guide will help you get started with contributing.

---

## Quick Start

### 1. Fork & Clone

```bash
git clone https://github.com/CodingFervor/mcn-manager.git
cd mcn-manager
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:

| Type       | Prefix       | Example                        |
|------------|--------------|--------------------------------|
| Feature    | `feature/`   | `feature/export-pdf`           |
| Fix        | `fix/`       | `fix/schedule-conflict`        |
| Refactor   | `refactor/`  | `refactor/api-response-format` |
| Docs       | `docs/`      | `docs/add-ai-docs`             |

### 3. Development Environment

```bash
# Backend
cd anchor_system
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data

# Frontend
cd frontend
npm install
npm run dev
```

---

## Code Standards

### Backend (Python)

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Model fields must include `verbose_name`
- New Models must be registered in `admin.py`
- ViewSet business logic belongs in `services.py`; Views should only handle parameter parsing and responses
- Use `select_related` / `prefetch_related` to avoid N+1 queries
- Add database indexes for high-frequency query fields
- Call `invalidate_cache()` after write operations to clear related caches

**File Organization:**

```
Files to create/modify when developing a new feature:

models.py or models_extra.py         → Define models
serializers.py or serializers_extra.py → Serializers
services.py                          → Business logic (optional)
views.py or views_extra.py           → Views
urls.py                              → Route registration
```

**Example — Adding a New Model:**

```python
# models_extra.py
class MyModel(models.Model):
    name = models.CharField('Name', max_length=100)
    status = models.CharField('Status', max_length=20, default='active')

    class Meta:
        verbose_name = 'My Model'
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

### Frontend (Vue)

- Use `<script setup>` syntax
- Extract reusable logic to `composables/`
- Extract repeated UI patterns to `components/`
- New pages go in `views/`, using defineAsyncComponent for lazy loading
- Define API calls in centralized `api.js` modules
- Use the `composables/useChart.js` hook for charts

**New Page Checklist:**

```
1. views/NewPage.vue         → Page component
2. router/index.js           → Add route
3. api.js                    → Add API module
4. App.vue menuItems         → Add menu item
```

---

## UI Design Guidelines

### Colors

Use CSS variables; do not hardcode colors:

```css
/* Correct */
color: var(--neon-cyan);
background: var(--bg-card);

/* Incorrect */
color: #00e5ff;
background: rgba(20, 24, 56, 0.65);
```

### Stat Cards

Use the `StatCard` component:

```vue
<StatCard label="Monthly GMV" :value="'¥128.5万'" icon="💰" gradient="g1" />
```

Available gradients: `g1` (purple-pink), `g2` (cyan-purple), `g3` (green-cyan), `g4` (orange-pink), `g5` (yellow-orange), `g6` (rainbow)

### Charts

Use the `useChart` hook:

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

## Testing

```bash
# Backend tests
python manage.py test

# Frontend build test
cd frontend && npm run build
```

Before submitting, ensure:
- `python manage.py check` passes with no errors
- `npm run build` succeeds
- Existing API endpoints respond normally

---

## Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

type: feat / fix / docs / style / refactor / perf / test / chore
scope: backend / frontend / ai / docs
```

**Examples:**

```
feat(backend): add product management module
fix(ai): fix crash in GMV prediction when data is insufficient
docs: update API documentation
refactor(frontend): extract StatCard component
perf(backend): add caching to store overview endpoint
```

---

## Pull Request Process

1. Ensure the PR does only one thing (feature / fix / refactor — do not mix)
2. Update related documentation
3. If you added new models, run `python manage.py makemigrations`
4. PR description should explain: what was done, why, and how to test it

**PR Template:**

```markdown
## Changes
Brief description of what was done

## Change Type
- [ ] New Feature
- [ ] Bug Fix
- [ ] Refactor
- [ ] Documentation
- [ ] Performance Improvement

## Testing
- [ ] python manage.py check passes
- [ ] npm run build passes
- [ ] Manual testing passed

## Screenshots
(Attach screenshots for any UI changes)
```

---

## Questions?

- Open an [Issue](https://github.com/CodingFervor/mcn-manager/issues)
- Describe the problem, reproduction steps, and expected behavior
- Attach error logs or screenshots
