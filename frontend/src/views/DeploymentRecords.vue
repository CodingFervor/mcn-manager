<script setup>
import { ref, onMounted } from 'vue'
import { DeploymentRecordAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, success: 0, rollback: 0, failed: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', environment: '', status: '' })

const envMap = { development: '开发', staging: '预发布', production: '生产' }
const envColor = { development: 'info', staging: 'warning', production: 'danger' }
const statusMap = { success: '成功', failed: '失败', rollback: '已回滚', deploying: '部署中' }
const statusColor = { success: 'success', failed: 'danger', rollback: 'warning', deploying: '' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([DeploymentRecordAPI.list(filters.value), DeploymentRecordAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, success: list.value.filter(i => i.status === 'success').length, rollback: list.value.filter(i => i.status === 'rollback').length, failed: list.value.filter(i => i.status === 'failed').length }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { version: '', environment: 'staging', description: '', changelog: '' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await DeploymentRecordAPI.update(form.value.id, form.value)
    else await DeploymentRecordAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此部署记录？', '提示', { type: 'warning' })
  await DeploymentRecordAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="部署记录" subtitle="版本管理 · 环境部署 · 回滚追踪" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">部署数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">成功</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.success }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">回滚</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.rollback }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">失败</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ stats.failed }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索版本号" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.environment" placeholder="环境" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in envMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建部署</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="version" label="版本" width="120" />
        <el-table-column label="环境" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="envColor[row.environment]" size="small" effect="dark">{{ envMap[row.environment] || row.environment }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
        <el-table-column prop="deployed_by" label="部署人" width="100" />
        <el-table-column prop="deployed_at" label="部署时间" width="170" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rollback_version" label="回滚版本" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="部署记录" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="版本"><el-input v-model="form.version" placeholder="v1.0.0" /></el-form-item>
        <el-form-item label="环境">
          <el-select v-model="form.environment" style="width:100%">
            <el-option v-for="(v, k) in envMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="变更日志"><el-input v-model="form.changelog" type="textarea" :rows="4" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
