<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { BudgetAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, total_allocated: 0, total_spent: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', status: '', period: '', department: '' })

const statusMap = { active: '执行中', frozen: '已冻结', closed: '已关闭' }
const statusColor = { active: 'success', frozen: 'warning', closed: 'info' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      BudgetAPI.list(filters.value),
      BudgetAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { department: '', category: '', allocated: 0, spent: 0, remaining: 0, usage_rate: 0, period: '', status: 'active' }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (editingId.value) await BudgetAPI.update(editingId.value, form.value)
  else await BudgetAPI.create(form.value)
  ElMessage.success('保存成功')
  dialog.value = false
  load()
}

const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除「${row.department} - ${row.category}」预算？`, '提示', { type: 'warning' })
  await BudgetAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const formatMoney = (val) => Number(val || 0).toLocaleString()

const usageColor = (rate) => {
  if (rate >= 90) return '#ff4d9e'
  if (rate >= 70) return '#ffd000'
  return '#00ff9d'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="预算管理" subtitle="预算编制 · 执行监控 · 超支预警" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">预算记录数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">预算总额</div>
        <div class="stat-value">¥{{ formatMoney(stats.total_allocated) }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">已使用总额</div>
        <div class="stat-value">¥{{ formatMoney(stats.total_spent) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索部门/类目" style="width: 200px" @keyup.enter="load" />
      <el-input v-model="filters.department" placeholder="部门" style="width: 130px" @keyup.enter="load" />
      <el-input v-model="filters.period" placeholder="周期" style="width: 120px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex: 1"></div>
      <el-button type="success" @click="openCreate">+ 新建预算</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="department" label="部门" width="120" fixed />
        <el-table-column prop="category" label="预算类目" width="130" />
        <el-table-column label="预算金额" width="120">
          <template #default="{ row }">¥{{ formatMoney(row.allocated) }}</template>
        </el-table-column>
        <el-table-column label="已使用" width="120">
          <template #default="{ row }">
            <span style="color: #ff4d9e">¥{{ formatMoney(row.spent) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="剩余" width="120">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ formatMoney(row.remaining) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="使用率" width="110">
          <template #default="{ row }">
            <el-progress :percentage="Number(row.usage_rate || 0)" :color="usageColor(row.usage_rate)" :stroke-width="8" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column prop="period" label="周期" width="100" />
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

    <el-dialog v-model="dialog" :title="editingId ? '编辑预算' : '新建预算'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="部门"><el-input v-model="form.department" placeholder="请输入部门名称" /></el-form-item>
        <el-form-item label="预算类目"><el-input v-model="form.category" placeholder="请输入预算类目" /></el-form-item>
        <el-form-item label="预算金额"><el-input-number v-model="form.allocated" :min="0" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="已使用"><el-input-number v-model="form.spent" :min="0" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="剩余"><el-input-number v-model="form.remaining" :min="0" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="使用率(%)"><el-input-number v-model="form.usage_rate" :min="0" :max="100" :precision="1" style="width: 100%" /></el-form-item>
        <el-form-item label="周期"><el-input v-model="form.period" placeholder="如: 2025-Q1 或 2025-06" /></el-form-item>
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
