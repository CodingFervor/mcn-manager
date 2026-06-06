<script setup>
import { ref, onMounted } from 'vue'
import { IntegrationConfigAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, disabled: 0, types: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', integration_type: '', is_active: '' })

const typeMap = { payment: '支付', sms: '短信', email: '邮件', logistics: '物流', analytics: '分析', crm: 'CRM', erp: 'ERP' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([IntegrationConfigAPI.list(filters.value), IntegrationConfigAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, active: list.value.filter(i => i.is_active).length, disabled: list.value.filter(i => !i.is_active).length, types: new Set(list.value.map(i => i.integration_type)).size }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', integration_type: 'payment', api_endpoint: '', config: '', is_active: true }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row, config: typeof row.config === 'object' ? JSON.stringify(row.config, null, 2) : (row.config || '') }; dialog.value = true }
async function handleSave() {
  try {
    const payload = { ...form.value }
    if (typeof payload.config === 'string' && payload.config.trim()) { try { payload.config = JSON.parse(payload.config) } catch { /* keep as string */ } }
    if (form.value.id) await IntegrationConfigAPI.update(form.value.id, payload)
    else await IntegrationConfigAPI.create(payload)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此集成配置？', '提示', { type: 'warning' })
  await IntegrationConfigAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="集成配置" subtitle="第三方集成 · API对接 · 数据同步" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">集成数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已启用</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已禁用</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ stats.disabled }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">类型数</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.types }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索集成名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.integration_type" placeholder="集成类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建集成</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="140" show-overflow-tooltip />
        <el-table-column label="类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ typeMap[row.integration_type] || row.integration_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="api_endpoint" label="API端点" width="220" show-overflow-tooltip />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_sync" label="最后同步" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="集成配置" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="集成类型">
          <el-select v-model="form.integration_type" style="width:100%">
            <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="API端点"><el-input v-model="form.api_endpoint" /></el-form-item>
        <el-form-item label="配置(JSON)"><el-input v-model="form.config" type="textarea" :rows="5" placeholder='{"key": "value"}' /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
