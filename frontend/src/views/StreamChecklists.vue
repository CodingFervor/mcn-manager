<script setup>
import { ref, onMounted } from 'vue'
import { StreamChecklistAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, done: 0, pending: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

const statusMap = { pending: '待处理', in_progress: '进行中', done: '已完成' }
const statusColor = { pending: 'danger', in_progress: 'warning', done: 'success' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([StreamChecklistAPI.list(filters.value), StreamChecklistAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, done: 0, pending: 0 }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', status: 'pending', items: [], completed_items: [] }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }

async function save() {
  try {
    if (form.value.id) await StreamChecklistAPI.update(form.value.id, form.value)
    else await StreamChecklistAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false; load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (row) => {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await StreamChecklistAPI.remove(row.id)
  ElMessage.success('已删除'); load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播检查清单" subtitle="开播检查 · 任务追踪 · 完成确认" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-label">清单总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">已完成</div>
        <div class="stat-value">{{ stats.done }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">待处理</div>
        <div class="stat-value">{{ stats.pending }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索" style="width:200px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="清单名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="检查项" width="100">
          <template #default="{ row }">{{ Array.isArray(row.items) ? row.items.length : 0 }}</template>
        </el-table-column>
        <el-table-column label="已完成项" width="100">
          <template #default="{ row }">{{ Array.isArray(row.completed_items) ? row.completed_items.length : 0 }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="检查清单" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="清单名称"><el-input v-model="form.name" placeholder="请输入清单名称" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="检查项">
          <el-input v-model="form.items" type="textarea" :rows="3" placeholder="JSON格式，如：[&quot;设备检查&quot;,&quot;网络测试&quot;]" />
        </el-form-item>
        <el-form-item label="已完成项">
          <el-input v-model="form.completed_items" type="textarea" :rows="3" placeholder="JSON格式，如：[&quot;设备检查&quot;]" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
