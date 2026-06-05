<script setup>
import { ref, onMounted } from 'vue'
import { WorkflowAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, total_runs: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', is_active: '', last_status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      WorkflowAPI.list(filters.value),
      WorkflowAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', trigger_type: '', trigger_config: '', actions: '',
    is_active: true, run_count: 0, last_status: ''
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = {
    ...row,
    trigger_config: typeof row.trigger_config === 'object' ? JSON.stringify(row.trigger_config) : (row.trigger_config || ''),
    actions: typeof row.actions === 'object' ? JSON.stringify(row.actions) : (row.actions || '')
  }
  dialog.value = true
}

async function save() {
  try {
    const payload = { ...form.value }
    if (typeof payload.trigger_config === 'string' && payload.trigger_config.trim()) {
      try { payload.trigger_config = JSON.parse(payload.trigger_config) } catch { /* keep as string */ }
    }
    if (typeof payload.actions === 'string' && payload.actions.trim()) {
      try { payload.actions = JSON.parse(payload.actions) } catch { /* keep as string */ }
    }
    if (form.value.id) {
      await WorkflowAPI.update(form.value.id, payload)
      ElMessage.success('更新成功')
    } else {
      await WorkflowAPI.create(payload)
      ElMessage.success('创建成功')
    }
    dialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

const removeItem = (row) => {
  ElMessageBox.confirm('确认删除该工作流?', '提示', { type: 'warning' }).then(async () => {
    await WorkflowAPI.remove(row.id)
    ElMessage.success('删除成功')
    load()
  }).catch(() => {})
}

const toggleActive = async (row) => {
  try {
    await WorkflowAPI.update(row.id, { is_active: !row.is_active })
    ElMessage.success(row.is_active ? '已停用' : '已启用')
    load()
  } catch { ElMessage.error('操作失败') }
}

const triggerTypeMap = { schedule: '定时触发', event: '事件触发', manual: '手动触发', webhook: 'Webhook' }
const lastStatusMap = { success: '成功', failed: '失败' }
const lastStatusColor = { success: 'success', failed: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="工作流管理" subtitle="自动化流程 · 触发配置 · 运行监控" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">工作流总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">启用中</div>
        <div class="stat-value">{{ stats.active }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">总运行次数</div>
        <div class="stat-value">{{ stats.total_runs }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">停用数</div>
        <div class="stat-value">{{ stats.total - stats.active }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索工作流名称" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.is_active" placeholder="启用状态" clearable @change="load" style="width: 120px">
        <el-option label="启用" :value="true" />
        <el-option label="停用" :value="false" />
      </el-select>
      <el-select v-model="filters.last_status" placeholder="运行状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in lastStatusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建工作流</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="工作流名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="触发类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ triggerTypeMap[row.trigger_type] || row.trigger_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="启用" width="80" align="center">
          <template #default="{ row }">
            <el-switch :model-value="row.is_active" @change="toggleActive(row)" size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="run_count" label="运行次数" width="100" />
        <el-table-column label="最近状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.last_status" size="small" :type="lastStatusColor[row.last_status]">{{ lastStatusMap[row.last_status] || row.last_status }}</el-tag>
            <span v-else style="color: #a8b2d1">-</span>
          </template>
        </el-table-column>
        <el-table-column label="触发配置" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">
            {{ typeof row.trigger_config === 'object' ? JSON.stringify(row.trigger_config) : row.trigger_config || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑工作流' : '新建工作流'" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" placeholder="工作流名称" /></el-form-item>
        <el-form-item label="触发类型">
          <el-select v-model="form.trigger_type" style="width: 100%">
            <el-option v-for="(v, k) in triggerTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="触发配置"><el-input v-model="form.trigger_config" type="textarea" :rows="3" placeholder="JSON格式触发配置" /></el-form-item>
        <el-form-item label="动作配置"><el-input v-model="form.actions" type="textarea" :rows="4" placeholder="JSON格式动作配置" /></el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
