<script setup>
import { ref, onMounted } from 'vue'
import { SystemAnnouncementAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, published: 0, pending: 0, expired: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', type: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([SystemAnnouncementAPI.list(filters.value), SystemAnnouncementAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, published: list.value.filter(i => i.status === 'published').length, pending: list.value.filter(i => i.status === 'pending').length, expired: list.value.filter(i => i.status === 'expired').length }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { title: '', content: '', type: 'info', priority: 1, status: 'pending', expires_at: '' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await SystemAnnouncementAPI.update(form.value.id, form.value)
    else await SystemAnnouncementAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此公告？', '提示', { type: 'warning' })
  await SystemAnnouncementAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const typeMap = { info: '通知', warning: '警告', urgent: '紧急' }
const typeColor = { info: 'info', warning: 'warning', urgent: 'danger' }
const statusMap = { pending: '待发布', published: '已发布', expired: '已过期' }
const statusColor = { pending: 'warning', published: 'success', expired: 'info' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="系统公告" subtitle="公告管理 · 消息推送 · 全局通知" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总公告数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已发布</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.published }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">待发布</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.pending }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已过期</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.expired }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索公告标题" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.type" placeholder="类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建公告</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="typeColor[row.type]" size="small" effect="dark">{{ typeMap[row.type] || row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80" align="center" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="published_at" label="发布时间" width="160" />
        <el-table-column prop="expires_at" label="过期时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="系统公告" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" style="width:100%">
            <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级"><el-input-number v-model="form.priority" :min="1" :max="10" style="width:100%" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="过期时间"><el-date-picker v-model="form.expires_at" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
