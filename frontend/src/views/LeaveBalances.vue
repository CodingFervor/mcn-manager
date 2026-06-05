<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { LeaveBalanceAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, total_annual: 0, total_sick: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', year: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      LeaveBalanceAPI.list(filters.value),
      LeaveBalanceAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { employee_name: '', annual_total: 10, annual_used: 0, sick_total: 10, sick_used: 0, personal_total: 3, personal_used: 0, year: new Date().getFullYear() }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (editingId.value) await LeaveBalanceAPI.update(editingId.value, form.value)
  else await LeaveBalanceAPI.create(form.value)
  ElMessage.success('保存成功')
  dialog.value = false
  load()
}

const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除「${row.employee_name}」的假期余额？`, '提示', { type: 'warning' })
  await LeaveBalanceAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const remainPercent = (total, used) => total > 0 ? Math.round(((total - used) / total) * 100) : 0

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="假期余额" subtitle="年假管理 · 病假统计 · 个人假期" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">员工记录数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">年假总额(天)</div>
        <div class="stat-value">{{ stats.total_annual }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">病假总额(天)</div>
        <div class="stat-value">{{ stats.total_sick }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索员工姓名" style="width: 200px" @keyup.enter="load" />
      <el-date-picker v-model="filters.year" type="year" placeholder="年份" value-format="YYYY" style="width: 130px" @change="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex: 1"></div>
      <el-button type="success" @click="openCreate">+ 新建余额</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="employee_name" label="员工姓名" width="120" fixed />
        <el-table-column label="年假" align="center">
          <el-table-column prop="annual_total" label="总额" width="80" />
          <el-table-column prop="annual_used" label="已用" width="80">
            <template #default="{ row }">
              <span style="color: #ff4d9e">{{ row.annual_used }}</span>
            </template>
          </el-table-column>
          <el-table-column label="剩余" width="80">
            <template #default="{ row }">
              <span style="color: var(--neon-cyan); font-weight: 600">{{ row.annual_total - row.annual_used }}</span>
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="病假" align="center">
          <el-table-column prop="sick_total" label="总额" width="80" />
          <el-table-column prop="sick_used" label="已用" width="80">
            <template #default="{ row }">
              <span style="color: #ff4d9e">{{ row.sick_used }}</span>
            </template>
          </el-table-column>
          <el-table-column label="剩余" width="80">
            <template #default="{ row }">
              <span style="color: var(--neon-cyan); font-weight: 600">{{ row.sick_total - row.sick_used }}</span>
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="事假" align="center">
          <el-table-column prop="personal_total" label="总额" width="80" />
          <el-table-column prop="personal_used" label="已用" width="80">
            <template #default="{ row }">
              <span style="color: #ff4d9e">{{ row.personal_used }}</span>
            </template>
          </el-table-column>
          <el-table-column label="剩余" width="80">
            <template #default="{ row }">
              <span style="color: var(--neon-cyan); font-weight: 600">{{ row.personal_total - row.personal_used }}</span>
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)" style="color: var(--neon-yellow)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="editingId ? '编辑假期余额' : '新建假期余额'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="员工姓名"><el-input v-model="form.employee_name" placeholder="请输入员工姓名" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="年假总额"><el-input-number v-model="form.annual_total" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年假已用"><el-input-number v-model="form.annual_used" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="病假总额"><el-input-number v-model="form.sick_total" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="病假已用"><el-input-number v-model="form.sick_used" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="事假总额"><el-input-number v-model="form.personal_total" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="事假已用"><el-input-number v-model="form.personal_used" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="年份"><el-date-picker v-model="form.year" type="year" value-format="YYYY" style="width: 100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
