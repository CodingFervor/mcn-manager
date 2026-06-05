<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { OnboardingAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, by_status: {}, avg_completion: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', status: '' })

const statusMap = { in_progress: '进行中', completed: '已完成', overdue: '已逾期' }
const statusColor = { in_progress: 'primary', completed: 'success', overdue: 'danger' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      OnboardingAPI.list(filters.value),
      OnboardingAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { employee_name: '', progress: '{}', mentor: '', start_date: '', end_date: '', completion: 0, status: 'in_progress' }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = {
    ...row,
    progress: typeof row.progress === 'object' ? JSON.stringify(row.progress) : row.progress
  }
  dialog.value = true
}

async function save() {
  const payload = { ...form.value }
  try { payload.progress = typeof payload.progress === 'string' ? JSON.parse(payload.progress) : payload.progress } catch { payload.progress = {} }
  if (editingId.value) await OnboardingAPI.update(editingId.value, payload)
  else await OnboardingAPI.create(payload)
  ElMessage.success('保存成功')
  dialog.value = false
  load()
}

const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除「${row.employee_name}」的入职记录？`, '提示', { type: 'warning' })
  await OnboardingAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const progressColor = (val) => {
  if (val >= 100) return '#00ff9d'
  if (val >= 60) return 'var(--neon-cyan)'
  if (val >= 30) return '#ffd000'
  return '#ff4d9e'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="入职管理" subtitle="入职流程 · 导师分配 · 进度追踪" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">入职记录数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">各状态分布</div>
        <div class="stat-value" style="font-size: 13px; line-height: 1.6">
          <span v-for="(v, k) in stats.by_status" :key="k" style="margin-right: 8px">{{ statusMap[k] || k }}: {{ v }}</span>
        </div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">平均完成度</div>
        <div class="stat-value">{{ Number(stats.avg_completion || 0).toFixed(1) }}%</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索员工姓名/导师" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex: 1"></div>
      <el-button type="success" @click="openCreate">+ 新建入职</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="employee_name" label="员工姓名" width="120" fixed />
        <el-table-column label="入职进度" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.completion" :color="progressColor(row.completion)" :stroke-width="8" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="进度详情(JSON)" width="130">
          <template #default="{ row }">
            <el-tag size="small" type="info">JSON</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="mentor" label="导师" width="100" />
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="end_date" label="结束日期" width="120" />
        <el-table-column label="完成度" width="90">
          <template #default="{ row }">
            <span :style="{ color: progressColor(row.completion), fontWeight: 600 }">{{ row.completion }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)" style="color: var(--neon-yellow)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="editingId ? '编辑入职' : '新建入职'" width="600px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="员工姓名"><el-input v-model="form.employee_name" placeholder="请输入员工姓名" /></el-form-item>
        <el-form-item label="进度详情(JSON)"><el-input v-model="form.progress" type="textarea" :rows="3" placeholder='{"step1": true, "step2": false}' /></el-form-item>
        <el-form-item label="导师"><el-input v-model="form.mentor" placeholder="请输入导师姓名" /></el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="完成度(%)"><el-input-number v-model="form.completion" :min="0" :max="100" style="width: 100%" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
