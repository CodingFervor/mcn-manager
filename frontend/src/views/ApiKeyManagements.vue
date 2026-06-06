<script setup>
import { ref, onMounted } from 'vue'
import { ApiKeyManagementAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, expired: 0, total_calls: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '' })

const statusMap = { active: '活跃', expired: '已过期', revoked: '已撤销' }
const statusColor = { active: 'success', expired: 'danger', revoked: 'info' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([ApiKeyManagementAPI.list(filters.value), ApiKeyManagementAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, active: list.value.filter(i => i.status === 'active').length, expired: list.value.filter(i => i.status === 'expired').length, total_calls: list.value.reduce((s, r) => s + (Number(r.total_calls) || 0), 0) }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', permissions: '', rate_limit: 1000, expires_at: '' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await ApiKeyManagementAPI.update(form.value.id, form.value)
    else await ApiKeyManagementAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此API密钥？此操作不可恢复', '提示', { type: 'warning' })
  await ApiKeyManagementAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="API密钥管理" subtitle="密钥管理 · 权限控制 · 调用监控" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">密钥数</div>
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
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总调用</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.total_calls }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索密钥名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建密钥</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="permissions" label="权限" width="160" show-overflow-tooltip />
        <el-table-column prop="rate_limit" label="限流" width="100" align="right">
          <template #default="{ row }"><span style="font-weight:600">{{ row.rate_limit }}/min</span></template>
        </el-table-column>
        <el-table-column prop="last_used" label="最后使用" width="170" />
        <el-table-column prop="expires_at" label="过期时间" width="170" />
        <el-table-column label="状态" width="90" align="center">
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

    <el-dialog v-model="dialog" title="API密钥" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="权限"><el-input v-model="form.permissions" type="textarea" :rows="3" placeholder="权限列表，逗号分隔" /></el-form-item>
        <el-form-item label="限流"><el-input-number v-model="form.rate_limit" :min="1" style="width:100%" /> <span style="color:#a8b2d1;margin-left:8px">次/分钟</span></el-form-item>
        <el-form-item label="过期时间"><el-date-picker v-model="form.expires_at" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
