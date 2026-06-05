<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { OKRAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, by_status: {}, avg_progress: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', status: '', quarter: '' })

const statusMap = { draft: '草稿', active: '进行中', review: '评审中', completed: '已完成' }
const statusColor = { draft: 'info', active: 'primary', review: 'warning', completed: 'success' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      OKRAPI.list(filters.value),
      OKRAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { employee_name: '', objective: '', key_results: '[]', quarter: '', progress: 0, score: 0, status: 'draft', supervisor: '' }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = {
    ...row,
    key_results: typeof row.key_results === 'object' ? JSON.stringify(row.key_results) : row.key_results
  }
  dialog.value = true
}

async function save() {
  const payload = { ...form.value }
  try { payload.key_results = typeof payload.key_results === 'string' ? JSON.parse(payload.key_results) : payload.key_results } catch { payload.key_results = [] }
  if (editingId.value) await OKRAPI.update(editingId.value, payload)
  else await OKRAPI.create(payload)
  ElMessage.success('保存成功')
  dialog.value = false
  load()
}

const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除「${row.employee_name}」的OKR？`, '提示', { type: 'warning' })
  await OKRAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const progressColor = (val) => {
  if (val >= 80) return '#00ff9d'
  if (val >= 50) return 'var(--neon-cyan)'
  if (val >= 25) return '#ffd000'
  return '#ff4d9e'
}

const scoreColor = (val) => {
  if (val >= 0.7) return '#00ff9d'
  if (val >= 0.4) return '#ffd000'
  return '#ff4d9e'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="OKR管理" subtitle="目标设定 · 关键结果 · 进度跟踪" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">OKR总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">各状态分布</div>
        <div class="stat-value" style="font-size: 13px; line-height: 1.6">
          <span v-for="(v, k) in stats.by_status" :key="k" style="margin-right: 8px">{{ statusMap[k] || k }}: {{ v }}</span>
        </div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">平均进度</div>
        <div class="stat-value">{{ Number(stats.avg_progress || 0).toFixed(1) }}%</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索员工/目标" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-input v-model="filters.quarter" placeholder="季度(如 Q1)" style="width: 100px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex: 1"></div>
      <el-button type="success" @click="openCreate">+ 新建OKR</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="employee_name" label="员工姓名" width="110" fixed />
        <el-table-column prop="objective" label="目标(O)" min-width="180" show-overflow-tooltip />
        <el-table-column label="关键结果(KR)" width="130">
          <template #default="{ row }">
            <el-tag size="small" type="info">JSON</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quarter" label="季度" width="80" />
        <el-table-column label="进度" width="110">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :color="progressColor(row.progress)" :stroke-width="8" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="评分" width="80">
          <template #default="{ row }">
            <span :style="{ color: scoreColor(row.score), fontWeight: 700 }">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="supervisor" label="上级" width="90" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)" style="color: var(--neon-yellow)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="editingId ? '编辑OKR' : '新建OKR'" width="650px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="员工姓名"><el-input v-model="form.employee_name" placeholder="请输入员工姓名" /></el-form-item>
        <el-form-item label="目标(O)"><el-input v-model="form.objective" type="textarea" :rows="2" placeholder="请输入目标" /></el-form-item>
        <el-form-item label="关键结果(KR)"><el-input v-model="form.key_results" type="textarea" :rows="4" placeholder='[{"kr": "关键结果1", "progress": 0}]' /></el-form-item>
        <el-form-item label="季度"><el-input v-model="form.quarter" placeholder="如: 2025-Q1" /></el-form-item>
        <el-form-item label="进度(%)"><el-input-number v-model="form.progress" :min="0" :max="100" style="width: 100%" /></el-form-item>
        <el-form-item label="评分(0-1)"><el-input-number v-model="form.score" :min="0" :max="1" :step="0.1" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="上级"><el-input v-model="form.supervisor" placeholder="请输入上级姓名" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
