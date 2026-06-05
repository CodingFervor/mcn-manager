<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataImportAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, total_rows: 0, success_rate: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', import_type: '', status: '' })

const importTypeMap = { products: '商品', orders: '订单', employees: '员工', stores: '店铺', analytics: '数据分析' }
const statusMap = { uploading: '上传中', processing: '处理中', completed: '已完成', failed: '失败' }
const statusColor = { uploading: 'primary', processing: 'warning', completed: 'success', failed: 'danger' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      DataImportAPI.list(filters.value),
      DataImportAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { filename: '', import_type: 'products', total_rows: 0, success_rows: 0, fail_rows: 0, status: 'uploading', operator: '' }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  await DataImportAPI.create(form.value)
  ElMessage.success('导入任务已创建')
  dialog.value = false
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="数据导入" subtitle="批量导入 · 数据迁移 · 导入监控" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">导入任务总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总导入行数</div>
        <div class="stat-value">{{ Number(stats.total_rows || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">成功率</div>
        <div class="stat-value">{{ Number(stats.success_rate || 0).toFixed(1) }}%</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索文件名/操作人" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.import_type" placeholder="导入类型" clearable @change="load" style="width: 130px">
        <el-option v-for="(v, k) in importTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex: 1"></div>
      <el-button type="success" @click="openCreate">+ 新建导入</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="filename" label="文件名" min-width="180" show-overflow-tooltip />
        <el-table-column label="导入类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ importTypeMap[row.import_type] || row.import_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_rows" label="总行数" width="100">
          <template #default="{ row }">{{ Number(row.total_rows || 0).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="success_rows" label="成功行数" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan)">{{ Number(row.success_rows || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="fail_rows" label="失败行数" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.fail_rows > 0 ? '#ff4d9e' : 'var(--text-secondary)' }">{{ Number(row.fail_rows || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)" style="color: var(--neon-yellow)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="editingId ? '查看导入详情' : '新建数据导入'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="文件名"><el-input v-model="form.filename" placeholder="请输入文件名" /></el-form-item>
        <el-form-item label="导入类型">
          <el-select v-model="form.import_type" style="width: 100%">
            <el-option v-for="(v, k) in importTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="总行数"><el-input-number v-model="form.total_rows" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="成功行数"><el-input-number v-model="form.success_rows" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="失败行数"><el-input-number v-model="form.fail_rows" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作人"><el-input v-model="form.operator" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">{{ editingId ? '更新' : '提交' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>
