<script setup>
import { ref, onMounted } from 'vue'
import { QualityCheckAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_status: {}, avg_score: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', target_type: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      QualityCheckAPI.list(filters.value),
      QualityCheckAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    target_type: '', target_id: null, checker: '',
    score: 0, max_score: 100, issues: '', status: 'pending'
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row, issues: typeof row.issues === 'object' ? JSON.stringify(row.issues) : (row.issues || '') }
  dialog.value = true
}

async function save() {
  try {
    const payload = { ...form.value }
    if (typeof payload.issues === 'string' && payload.issues.trim()) {
      try { payload.issues = JSON.parse(payload.issues) } catch { payload.issues = payload.issues }
    }
    if (form.value.id) {
      await QualityCheckAPI.update(form.value.id, payload)
      ElMessage.success('更新成功')
    } else {
      await QualityCheckAPI.create(payload)
      ElMessage.success('创建成功')
    }
    dialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

const removeItem = (row) => {
  ElMessageBox.confirm('确认删除该质检记录?', '提示', { type: 'warning' }).then(async () => {
    await QualityCheckAPI.remove(row.id)
    ElMessage.success('删除成功')
    load()
  }).catch(() => {})
}

const targetTypeMap = { stream: '直播间', video: '视频', product: '商品', service: '服务' }
const statusMap = { pending: '待检测', passed: '已通过', failed: '未通过', warning: '警告' }
const statusColor = { pending: 'info', passed: 'success', failed: 'danger', warning: 'warning' }

const scoreColor = (score, max) => {
  const ratio = score / (max || 100)
  if (ratio >= 0.9) return '#00ff9d'
  if (ratio >= 0.7) return '#ffd23f'
  return '#ff4d9e'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="质量检测" subtitle="质检管理 · 评分追踪 · 问题整改" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">检测总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">平均分</div>
        <div class="stat-value">{{ Number(stats.avg_score || 0).toFixed(1) }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">已通过</div>
        <div class="stat-value">{{ stats.by_status?.passed || 0 }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">未通过</div>
        <div class="stat-value">{{ stats.by_status?.failed || 0 }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索检测人/目标ID" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.target_type" placeholder="检测对象" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in targetTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建质检</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="检测对象" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ targetTypeMap[row.target_type] || row.target_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_id" label="目标ID" width="80" />
        <el-table-column prop="checker" label="检测人" width="100" />
        <el-table-column label="评分" width="120">
          <template #default="{ row }">
            <span :style="{ color: scoreColor(row.score, row.max_score), fontWeight: 700 }">
              {{ row.score }}/{{ row.max_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="问题" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            {{ typeof row.issues === 'object' ? JSON.stringify(row.issues) : row.issues || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑质检' : '新建质检'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="检测对象">
          <el-select v-model="form.target_type" style="width: 100%">
            <el-option v-for="(v, k) in targetTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标ID"><el-input-number v-model="form.target_id" :min="1" style="width: 100%" /></el-form-item>
        <el-form-item label="检测人"><el-input v-model="form.checker" placeholder="检测人姓名" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="评分"><el-input-number v-model="form.score" :min="0" :precision="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="满分"><el-input-number v-model="form.max_score" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="问题描述"><el-input v-model="form.issues" type="textarea" :rows="3" placeholder="JSON格式或文本描述" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
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
