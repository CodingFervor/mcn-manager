<script setup>
import { ref, onMounted } from 'vue'
import { LicenseManagementAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, expired: 0, expiring: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', license_type: '', status: '' })

const typeMap = { trial: '试用版', standard: '标准版', professional: '专业版', enterprise: '企业版' }
const typeColor = { trial: 'info', standard: '', professional: 'warning', enterprise: 'danger' }
const statusMap = { active: '活跃', expired: '已过期', expiring: '即将过期', revoked: '已撤销' }
const statusColor = { active: 'success', expired: 'danger', expiring: 'warning', revoked: 'info' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([LicenseManagementAPI.list(filters.value), LicenseManagementAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, active: list.value.filter(i => i.status === 'active').length, expired: list.value.filter(i => i.status === 'expired').length, expiring: list.value.filter(i => i.status === 'expiring').length }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { product_name: '', license_type: 'standard', max_activations: 1, issued_to: '', expires_at: '' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await LicenseManagementAPI.update(form.value.id, form.value)
    else await LicenseManagementAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此许可证？', '提示', { type: 'warning' })
  await LicenseManagementAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="许可证管理" subtitle="授权管理 · 激活控制 · 到期监控" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">许可证数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">活跃</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已过期</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ stats.expired }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">即将过期</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.expiring }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索产品名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.license_type" placeholder="许可类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建许可证</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="product_name" label="产品" min-width="140" show-overflow-tooltip />
        <el-table-column label="许可类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="typeColor[row.license_type]" size="small" effect="dark">{{ typeMap[row.license_type] || row.license_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="issued_to" label="授权对象" width="130" show-overflow-tooltip />
        <el-table-column prop="max_activations" label="最大激活" width="90" align="center" />
        <el-table-column prop="current_activations" label="当前激活" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.current_activations >= row.max_activations ? '#ff4d9e' : '#00ff9d', fontWeight: 600 }">{{ row.current_activations }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="expires_at" label="过期时间" width="170" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="许可证" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="产品"><el-input v-model="form.product_name" /></el-form-item>
        <el-form-item label="许可类型">
          <el-select v-model="form.license_type" style="width:100%">
            <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大激活"><el-input-number v-model="form.max_activations" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="授权对象"><el-input v-model="form.issued_to" /></el-form-item>
        <el-form-item label="过期时间"><el-date-picker v-model="form.expires_at" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
