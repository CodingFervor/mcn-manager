<script setup>
import { ref, onMounted } from 'vue'
import { DataBackupAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, success: 0, failed: 0, total_size: '0 GB' })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', backup_type: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([DataBackupAPI.list(filters.value), DataBackupAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, success: list.value.filter(i => i.status === 'success').length, failed: list.value.filter(i => i.status === 'failed').length, total_size: '2.5 GB' }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', file_path: '', backup_type: 'full', status: 'pending' }
  dialog.value = true
}
async function handleSave() {
  try {
    await DataBackupAPI.create(form.value)
    ElMessage.success('备份任务已创建')
    dialog.value = false
    load()
  } catch { ElMessage.error('创建失败') }
}
const runBackup = async (row) => {
  await ElMessageBox.confirm('确定执行此备份任务？', '提示', { type: 'info' })
  await DataBackupAPI.run(row.id)
  ElMessage.success('备份执行中')
  load()
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此备份记录？', '提示', { type: 'warning' })
  await DataBackupAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const typeMap = { full: '全量', incremental: '增量', differential: '差异' }
const statusMap = { pending: '待执行', running: '执行中', success: '成功', failed: '失败' }
const statusColor = { pending: 'info', running: 'warning', success: 'success', failed: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="数据备份" subtitle="备份管理 · 数据安全 · 灾难恢复" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">备份总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">成功</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.success }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">失败</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ stats.failed }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总大小</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.total_size }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索备份名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.backup_type" placeholder="备份类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建备份</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="file_path" label="文件路径" width="180" show-overflow-tooltip />
        <el-table-column prop="size" label="大小" width="100" align="right" />
        <el-table-column label="类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ typeMap[row.backup_type] || row.backup_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="runBackup(row)">执行</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建备份" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="文件路径"><el-input v-model="form.file_path" /></el-form-item>
        <el-form-item label="备份类型">
          <el-select v-model="form.backup_type" style="width:100%">
            <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>
