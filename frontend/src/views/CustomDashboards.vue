<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CustomDashboardAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, shared: 0, default_count: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', is_shared: '', is_default: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      CustomDashboardAPI.list(filters.value),
      CustomDashboardAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { name: '', owner: '', layout: '{}', widgets: '[]', is_shared: false, is_default: false, refresh_interval: 30 }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = {
    ...row,
    layout: typeof row.layout === 'object' ? JSON.stringify(row.layout) : row.layout,
    widgets: typeof row.widgets === 'object' ? JSON.stringify(row.widgets) : row.widgets
  }
  dialog.value = true
}

async function save() {
  const payload = { ...form.value }
  try { payload.layout = typeof payload.layout === 'string' ? JSON.parse(payload.layout) : payload.layout } catch { payload.layout = {} }
  try { payload.widgets = typeof payload.widgets === 'string' ? JSON.parse(payload.widgets) : payload.widgets } catch { payload.widgets = [] }
  if (editingId.value) await CustomDashboardAPI.update(editingId.value, payload)
  else await CustomDashboardAPI.create(payload)
  ElMessage.success('保存成功')
  dialog.value = false
  load()
}

const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除仪表盘「${row.name}」？`, '提示', { type: 'warning' })
  await CustomDashboardAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="自定义仪表盘" subtitle="看板配置 · 布局管理 · 数据可视化" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">仪表盘总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">已共享</div>
        <div class="stat-value">{{ stats.shared }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">默认看板</div>
        <div class="stat-value">{{ stats.default_count }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索仪表盘名称" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.is_shared" placeholder="共享状态" clearable @change="load" style="width: 120px">
        <el-option label="已共享" value="true" />
        <el-option label="未共享" value="false" />
      </el-select>
      <el-select v-model="filters.is_default" placeholder="默认看板" clearable @change="load" style="width: 120px">
        <el-option label="默认" value="true" />
        <el-option label="非默认" value="false" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex: 1"></div>
      <el-button type="success" @click="openCreate">+ 新建仪表盘</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="仪表盘名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="owner" label="所有者" width="120" />
        <el-table-column label="布局配置" width="120">
          <template #default="{ row }">
            <el-tag size="small" type="info">JSON</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="组件配置" width="120">
          <template #default="{ row }">
            <el-tag size="small" type="info">JSON</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="共享" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_shared ? 'success' : 'info'">{{ row.is_shared ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="默认" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_default ? 'warning' : 'info'">{{ row.is_default ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="refresh_interval" label="刷新间隔(秒)" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)" style="color: var(--neon-yellow)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="editingId ? '编辑仪表盘' : '新建仪表盘'" width="600px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="仪表盘名称"><el-input v-model="form.name" placeholder="请输入仪表盘名称" /></el-form-item>
        <el-form-item label="所有者"><el-input v-model="form.owner" placeholder="请输入所有者" /></el-form-item>
        <el-form-item label="布局配置(JSON)"><el-input v-model="form.layout" type="textarea" :rows="3" placeholder='{"columns": 3}' /></el-form-item>
        <el-form-item label="组件配置(JSON)"><el-input v-model="form.widgets" type="textarea" :rows="3" placeholder='[{"type": "chart"}]' /></el-form-item>
        <el-form-item label="共享">
          <el-switch v-model="form.is_shared" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
        <el-form-item label="刷新间隔(秒)">
          <el-input-number v-model="form.refresh_interval" :min="5" :max="3600" :step="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
