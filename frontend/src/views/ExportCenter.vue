<script setup>
import { ref, onMounted } from 'vue'
import { ExportCenterAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, processing: 0, completed: 0, total_rows: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', export_type: '', status: '' })

const typeMap = { orders: '订单', products: '商品', users: '用户', finance: '财务', inventory: '库存', analytics: '分析' }
const statusMap = { pending: '排队中', processing: '处理中', completed: '已完成', failed: '失败' }
const statusColor = { pending: 'info', processing: 'warning', completed: 'success', failed: 'danger' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([ExportCenterAPI.list(filters.value), ExportCenterAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, processing: list.value.filter(i => i.status === 'processing').length, completed: list.value.filter(i => i.status === 'completed').length, total_rows: list.value.reduce((s, r) => s + (Number(r.total_rows) || 0), 0) }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', export_type: 'orders', filters: '', format: 'xlsx' }
  dialog.value = true
}
async function handleSave() {
  try {
    await ExportCenterAPI.create(form.value)
    ElMessage.success('导出任务已创建')
    dialog.value = false
    load()
  } catch { ElMessage.error('创建失败') }
}
const download = (row) => {
  ExportCenterAPI.download(row.id)
  ElMessage.success('开始下载')
}

const fmtSize = (v) => {
  const n = Number(v) || 0
  if (n >= 1048576) return (n / 1048576).toFixed(1) + ' MB'
  if (n >= 1024) return (n / 1024).toFixed(1) + ' KB'
  return n + ' B'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="导出中心" subtitle="数据导出 · 批量处理 · 文件下载" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">导出总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">处理中</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.processing }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已完成</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.completed }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总行数</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.total_rows }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索导出名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.export_type" placeholder="导出类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建导出</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ typeMap[row.export_type] || row.export_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="文件大小" width="100" align="right">
          <template #default="{ row }">{{ fmtSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="total_rows" label="总行数" width="90" align="right" />
        <el-table-column prop="created_by" label="创建人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'completed'" size="small" type="primary" @click="download(row)">下载</el-button>
            <span v-else style="color:#a8b2d1;font-size:12px">{{ row.status === 'failed' ? '失败' : '等待中' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建导出" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="导出类型">
          <el-select v-model="form.export_type" style="width:100%">
            <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="筛选条件"><el-input v-model="form.filters" type="textarea" :rows="3" placeholder="JSON格式筛选条件" /></el-form-item>
        <el-form-item label="格式">
          <el-select v-model="form.format" style="width:100%">
            <el-option label="Excel" value="xlsx" />
            <el-option label="CSV" value="csv" />
            <el-option label="JSON" value="json" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">创建导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>
