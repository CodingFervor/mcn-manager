<script setup>
import { ref, onMounted } from 'vue'
import { ComplianceAuditAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, in_progress: 0, completed: 0, findings: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', audit_type: '', status: '' })

const auditTypeMap = { internal: '内部审计', external: '外部审计', regulatory: '监管审计', security: '安全审计' }
const statusMap = { planned: '已计划', in_progress: '进行中', completed: '已完成', cancelled: '已取消' }
const statusColor = { planned: 'info', in_progress: 'warning', completed: 'success', cancelled: 'danger' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([ComplianceAuditAPI.list(filters.value), ComplianceAuditAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, in_progress: list.value.filter(i => i.status === 'in_progress').length, completed: list.value.filter(i => i.status === 'completed').length, findings: list.value.reduce((s, r) => s + (Number(r.findings) || 0), 0) }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { title: '', audit_type: 'internal', standard: '', auditor: '', start_date: '', end_date: '' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await ComplianceAuditAPI.update(form.value.id, form.value)
    else await ComplianceAuditAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此审计记录？', '提示', { type: 'warning' })
  await ComplianceAuditAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="合规审计" subtitle="审计管理 · 合规检查 · 发现跟踪" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">审计数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">进行中</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.in_progress }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已完成</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.completed }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">发现项</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ stats.findings }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索审计标题" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.audit_type" placeholder="审计类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in auditTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建审计</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip />
        <el-table-column label="审计类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ auditTypeMap[row.audit_type] || row.audit_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="standard" label="标准" width="110" show-overflow-tooltip />
        <el-table-column prop="auditor" label="审计师" width="100" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="findings" label="发现项" width="80" align="center" />
        <el-table-column prop="critical_findings" label="严重发现" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.critical_findings > 0 ? '#ff4d9e' : '#a8b2d1', fontWeight: 600 }">{{ row.critical_findings }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="110" />
        <el-table-column prop="end_date" label="结束日期" width="110" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="合规审计" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="审计类型">
          <el-select v-model="form.audit_type" style="width:100%">
            <el-option v-for="(v, k) in auditTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="标准"><el-input v-model="form.standard" placeholder="如 ISO 27001" /></el-form-item>
        <el-form-item label="审计师"><el-input v-model="form.auditor" /></el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
