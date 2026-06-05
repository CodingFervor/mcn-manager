<script setup>
import { ref, onMounted } from 'vue'
import { InsuranceAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_premium: 0, total_coverage: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', insurance_type: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      InsuranceAPI.list(filters.value),
      InsuranceAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    insurance_type: '', provider: '', policy_no: '', premium: 0,
    coverage: 0, start_date: '', end_date: '', status: 'active'
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
      await InsuranceAPI.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await InsuranceAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    dialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

const removeItem = (row) => {
  ElMessageBox.confirm('确认删除该保险记录?', '提示', { type: 'warning' }).then(async () => {
    await InsuranceAPI.remove(row.id)
    ElMessage.success('删除成功')
    load()
  }).catch(() => {})
}

const typeMap = { employee: '员工保险', property: '财产保险', liability: '责任保险', equipment: '设备保险' }
const statusMap = { active: '有效', expired: '已过期', cancelled: '已取消' }
const statusColor = { active: 'success', expired: 'danger', cancelled: 'info' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="保险管理" subtitle="保单管理 · 保费统计 · 到期预警" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">保单总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总保费</div>
        <div class="stat-value">¥{{ Number(stats.total_premium || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">总保额</div>
        <div class="stat-value">¥{{ Number(stats.total_coverage || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">有效保单</div>
        <div class="stat-value">{{ list.filter(i => i.status === 'active').length }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索保单号/供应商" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.insurance_type" placeholder="保险类型" clearable @change="load" style="width: 130px">
        <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建保单</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="保险类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ typeMap[row.insurance_type] || row.insurance_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="provider" label="保险公司" min-width="130" show-overflow-tooltip />
        <el-table-column prop="policy_no" label="保单号" width="160" />
        <el-table-column label="保费" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ Number(row.premium).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="保额" width="130">
          <template #default="{ row }">
            <span style="color: #00ff9d; font-weight: 700">¥{{ Number(row.coverage).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="生效日期" width="110" />
        <el-table-column prop="end_date" label="到期日" width="110" />
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

    <el-dialog v-model="dialog" :title="form.id ? '编辑保单' : '新建保单'" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="保险类型">
          <el-select v-model="form.insurance_type" style="width: 100%">
            <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="保险公司"><el-input v-model="form.provider" placeholder="保险公司名称" /></el-form-item>
        <el-form-item label="保单号"><el-input v-model="form.policy_no" placeholder="请输入保单号" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="保费"><el-input-number v-model="form.premium" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保额"><el-input-number v-model="form.coverage" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="生效日期">
              <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="到期日">
              <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
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
