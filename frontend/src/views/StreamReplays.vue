<script setup>
import { ref, onMounted } from 'vue'
import { StreamReplayAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_views: 0, total_duration: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

const statusMap = { processing: '处理中', ready: '已就绪', published: '已发布', archived: '已归档' }
const statusColor = { processing: 'warning', ready: 'info', published: 'success', archived: '' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([StreamReplayAPI.list(filters.value), StreamReplayAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, total_views: 0, total_duration: 0 }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { title: '', url: '', duration: 0, views: 0, status: 'processing' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }

async function save() {
  try {
    if (form.value.id) await StreamReplayAPI.update(form.value.id, form.value)
    else await StreamReplayAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false; load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (row) => {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await StreamReplayAPI.remove(row.id)
  ElMessage.success('已删除'); load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播回放" subtitle="回放管理 · 观看统计 · 内容归档" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-label">回放总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">总观看量</div>
        <div class="stat-value">{{ Number(stats.total_views || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总时长(分钟)</div>
        <div class="stat-value">{{ Number(stats.total_duration || 0).toLocaleString() }}</div>
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
        <el-table-column prop="title" label="回放标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="url" label="回放地址" min-width="200" show-overflow-tooltip />
        <el-table-column label="时长(分钟)" width="110">
          <template #default="{ row }">{{ row.duration }}</template>
        </el-table-column>
        <el-table-column label="观看量" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan)">{{ Number(row.views || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
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

    <el-dialog v-model="dialog" title="直播回放" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="回放标题"><el-input v-model="form.title" placeholder="请输入回放标题" /></el-form-item>
        <el-form-item label="回放地址"><el-input v-model="form.url" placeholder="请输入回放URL" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="时长(分钟)"><el-input-number v-model="form.duration" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="观看量"><el-input-number v-model="form.views" :min="0" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
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
