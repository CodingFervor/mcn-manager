<script setup>
import { ref, onMounted } from 'vue'
import { WorkflowTemplateAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, manual: 0, event: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', trigger_type: '', is_active: '' })

const triggerMap = { manual: '手动触发', event: '事件触发', schedule: '定时触发', webhook: 'Webhook' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([WorkflowTemplateAPI.list(filters.value), WorkflowTemplateAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, active: list.value.filter(i => i.is_active).length, manual: list.value.filter(i => i.trigger_type === 'manual').length, event: list.value.filter(i => i.trigger_type === 'event').length }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', description: '', trigger_type: 'manual', trigger_config: '', steps: '', is_active: true }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await WorkflowTemplateAPI.update(form.value.id, form.value)
    else await WorkflowTemplateAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此模板？', '提示', { type: 'warning' })
  await WorkflowTemplateAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="工作流模板" subtitle="流程自动化 · 任务编排 · 触发管理" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">模板数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">启用中</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">手动触发</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.manual }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">事件触发</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.event }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索模板名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.trigger_type" placeholder="触发类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in triggerMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建模板</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" width="160" show-overflow-tooltip />
        <el-table-column label="触发类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.trigger_type === 'event' ? 'success' : row.trigger_type === 'schedule' ? 'warning' : ''">{{ triggerMap[row.trigger_type] || row.trigger_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="step_count" label="步骤数" width="80" align="center" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
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

    <el-dialog v-model="dialog" title="工作流模板" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="触发类型">
          <el-select v-model="form.trigger_type" style="width:100%">
            <el-option v-for="(v, k) in triggerMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="触发配置"><el-input v-model="form.trigger_config" type="textarea" :rows="3" placeholder="JSON格式配置" /></el-form-item>
        <el-form-item label="步骤定义"><el-input v-model="form.steps" type="textarea" :rows="5" placeholder="JSON格式步骤定义" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
