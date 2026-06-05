<script setup>
import { ref, onMounted } from 'vue'
import { StreamBackupAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, standby: 0, activated: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

const backupTypeMap = { anchor: '主播备选', device: '设备备选', network: '网络备选', content: '内容备选' }
const statusMap = { standby: '待命中', activated: '已启动', resolved: '已解决' }
const statusColor = { standby: 'info', activated: 'warning', resolved: 'success' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([StreamBackupAPI.list(filters.value), StreamBackupAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, standby: 0, activated: 0 }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', backup_type: 'anchor', contact: '', status: 'standby' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }

async function save() {
  try {
    if (form.value.id) await StreamBackupAPI.update(form.value.id, form.value)
    else await StreamBackupAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false; load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (row) => {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await StreamBackupAPI.remove(row.id)
  ElMessage.success('已删除'); load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播备份方案" subtitle="应急预案 · 备选管理 · 快速切换" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-label">方案总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">待命中</div>
        <div class="stat-value">{{ stats.standby }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">已启动</div>
        <div class="stat-value">{{ stats.activated }}</div>
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
        <el-table-column prop="name" label="方案名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="备份类型" width="110">
          <template #default="{ row }">{{ backupTypeMap[row.backup_type] || row.backup_type }}</template>
        </el-table-column>
        <el-table-column prop="contact" label="联系人" width="120" />
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

    <el-dialog v-model="dialog" title="备份方案" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="方案名称"><el-input v-model="form.name" placeholder="请输入方案名称" /></el-form-item>
        <el-form-item label="备份类型">
          <el-select v-model="form.backup_type" style="width:100%">
            <el-option v-for="(v, k) in backupTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact" placeholder="请输入联系人" /></el-form-item>
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
