<script setup>
import { ref, onMounted } from 'vue'
import { SLAAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_penalty: 0, by_status: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      SLAAPI.list(filters.value),
      SLAAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', client: '', metric: '', target_value: 0,
    actual_value: 0, unit: '', penalty: 0, status: 'meeting', period: ''
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  try {
    if (form.value.id) {
      await SLAAPI.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await SLAAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    dialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

const removeItem = (row) => {
  ElMessageBox.confirm('确认删除该SLA记录?', '提示', { type: 'warning' }).then(async () => {
    await SLAAPI.remove(row.id)
    ElMessage.success('删除成功')
    load()
  }).catch(() => {})
}

const statusMap = { meeting: '达标', at_risk: '有风险', breached: '已违约' }
const statusColor = { meeting: 'success', at_risk: 'warning', breached: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="SLA管理" subtitle="服务水平协议 · 达标监控 · 违约管理" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">SLA总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">违约罚金</div>
        <div class="stat-value" style="color: #ff4d9e">¥{{ Number(stats.total_penalty || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">达标</div>
        <div class="stat-value">{{ stats.by_status?.meeting || 0 }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">已违约</div>
        <div class="stat-value" style="color: #ff4d9e">{{ stats.by_status?.breached || 0 }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索SLA名称/客户" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建SLA</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="SLA名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="client" label="客户" width="120" show-overflow-tooltip />
        <el-table-column prop="metric" label="指标" width="120" />
        <el-table-column label="目标值" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">{{ row.target_value }}{{ row.unit }}</span>
          </template>
        </el-table-column>
        <el-table-column label="实际值" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.status === 'meeting' ? '#00ff9d' : row.status === 'breached' ? '#ff4d9e' : '#ffd23f', fontWeight: 600 }">
              {{ row.actual_value }}{{ row.unit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="罚金" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-pink); font-weight: 600">¥{{ Number(row.penalty).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="period" label="周期" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
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

    <el-dialog v-model="dialog" :title="form.id ? '编辑SLA' : '新建SLA'" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" placeholder="SLA名称" /></el-form-item>
        <el-form-item label="客户"><el-input v-model="form.client" placeholder="客户名称" /></el-form-item>
        <el-form-item label="指标"><el-input v-model="form.metric" placeholder="如: 响应时间、可用性" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="目标值"><el-input-number v-model="form.target_value" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="实际值"><el-input-number v-model="form.actual_value" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单位"><el-input v-model="form.unit" placeholder="%、ms等" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="违约罚金"><el-input-number v-model="form.penalty" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="周期"><el-input v-model="form.period" placeholder="如: 2026-06" /></el-form-item>
          </el-col>
        </el-row>
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
