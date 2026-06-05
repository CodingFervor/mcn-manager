<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { SalaryAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, total_net_salary: 0, avg_salary: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', period: '', status: '' })

const statusMap = { draft: '草稿', confirmed: '已确认', paid: '已发放' }
const statusColor = { draft: 'info', confirmed: 'warning', paid: 'success' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      SalaryAPI.list(filters.value),
      SalaryAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { employee_name: '', base_salary: 0, bonus: 0, commission: 0, deduction: 0, net_salary: 0, period: '', status: 'draft' }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (editingId.value) await SalaryAPI.update(editingId.value, form.value)
  else await SalaryAPI.create(form.value)
  ElMessage.success('保存成功')
  dialog.value = false
  load()
}

const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除「${row.employee_name}」的薪资记录？`, '提示', { type: 'warning' })
  await SalaryAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const formatMoney = (val) => Number(val || 0).toLocaleString()

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="薪资管理" subtitle="工资核算 · 奖金提成 · 薪资发放" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">薪资记录数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">应发总额</div>
        <div class="stat-value">¥{{ formatMoney(stats.total_net_salary) }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">平均薪资</div>
        <div class="stat-value">¥{{ formatMoney(stats.avg_salary) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索员工姓名" style="width: 200px" @keyup.enter="load" />
      <el-date-picker v-model="filters.period" type="month" placeholder="薪资周期" value-format="YYYY-MM" style="width: 160px" @change="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex: 1"></div>
      <el-button type="success" @click="openCreate">+ 新建薪资</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="employee_name" label="员工姓名" width="120" fixed />
        <el-table-column label="基本工资" width="110">
          <template #default="{ row }">¥{{ formatMoney(row.base_salary) }}</template>
        </el-table-column>
        <el-table-column label="奖金" width="100">
          <template #default="{ row }">
            <span style="color: #00ff9d">¥{{ formatMoney(row.bonus) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="提成" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan)">¥{{ formatMoney(row.commission) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="扣款" width="100">
          <template #default="{ row }">
            <span style="color: #ff4d9e">¥{{ formatMoney(row.deduction) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="实发工资" width="120">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 700; font-size: 14px">¥{{ formatMoney(row.net_salary) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="period" label="周期" width="90" />
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

    <el-dialog v-model="dialog" :title="editingId ? '编辑薪资' : '新建薪资'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="员工姓名"><el-input v-model="form.employee_name" placeholder="请输入员工姓名" /></el-form-item>
        <el-form-item label="基本工资"><el-input-number v-model="form.base_salary" :min="0" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="奖金"><el-input-number v-model="form.bonus" :min="0" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="提成"><el-input-number v-model="form.commission" :min="0" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="扣款"><el-input-number v-model="form.deduction" :min="0" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="实发工资"><el-input-number v-model="form.net_salary" :min="0" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="薪资周期"><el-date-picker v-model="form.period" type="month" value-format="YYYY-MM" placeholder="选择月份" style="width: 100%" /></el-form-item>
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
