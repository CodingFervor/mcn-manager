<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ProfitAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, total_revenue: 0, avg_margin: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', period: '', category: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      ProfitAPI.list(filters.value),
      ProfitAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { revenue: 0, cost: 0, gross_profit: 0, operating_cost: 0, net_profit: 0, margin: 0, category: '', period: '' }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (editingId.value) await ProfitAPI.update(editingId.value, form.value)
  else await ProfitAPI.create(form.value)
  ElMessage.success('保存成功')
  dialog.value = false
  load()
}

const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除「${row.category || row.period}」的利润记录？`, '提示', { type: 'warning' })
  await ProfitAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const formatMoney = (val) => Number(val || 0).toLocaleString()

const marginColor = (val) => {
  if (val >= 30) return '#00ff9d'
  if (val >= 15) return 'var(--neon-cyan)'
  if (val >= 0) return '#ffd000'
  return '#ff4d9e'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="利润分析" subtitle="收入成本 · 毛利净利 · 利润率" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">记录总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总收入</div>
        <div class="stat-value">¥{{ formatMoney(stats.total_revenue) }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">平均利润率</div>
        <div class="stat-value">{{ Number(stats.avg_margin || 0).toFixed(1) }}%</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索类目/周期" style="width: 200px" @keyup.enter="load" />
      <el-input v-model="filters.category" placeholder="类目" style="width: 130px" @keyup.enter="load" />
      <el-input v-model="filters.period" placeholder="周期" style="width: 120px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex: 1"></div>
      <el-button type="success" @click="openCreate">+ 新建记录</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="收入" width="120">
          <template #default="{ row }">
            <span style="color: #00ff9d; font-weight: 600">¥{{ formatMoney(row.revenue) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="成本" width="120">
          <template #default="{ row }">
            <span style="color: #ff4d9e">¥{{ formatMoney(row.cost) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="毛利润" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.gross_profit >= 0 ? 'var(--neon-cyan)' : '#ff4d9e', fontWeight: 600 }">¥{{ formatMoney(row.gross_profit) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="运营成本" width="120">
          <template #default="{ row }">
            <span style="color: #ffd000">¥{{ formatMoney(row.operating_cost) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="净利润" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.net_profit >= 0 ? '#00ff9d' : '#ff4d9e', fontWeight: 700, fontSize: '14px' }">¥{{ formatMoney(row.net_profit) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="利润率" width="100">
          <template #default="{ row }">
            <span :style="{ color: marginColor(row.margin), fontWeight: 700 }">{{ Number(row.margin || 0).toFixed(1) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="类目" width="120" />
        <el-table-column prop="period" label="周期" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)" style="color: var(--neon-yellow)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="editingId ? '编辑利润' : '新建利润'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="收入"><el-input-number v-model="form.revenue" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="成本"><el-input-number v-model="form.cost" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="毛利润"><el-input-number v-model="form.gross_profit" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="运营成本"><el-input-number v-model="form.operating_cost" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="净利润"><el-input-number v-model="form.net_profit" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="利润率(%)"><el-input-number v-model="form.margin" :precision="1" style="width: 100%" /></el-form-item>
        <el-form-item label="类目"><el-input v-model="form.category" placeholder="请输入类目" /></el-form-item>
        <el-form-item label="周期"><el-input v-model="form.period" placeholder="如: 2025-Q1 或 2025-06" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
