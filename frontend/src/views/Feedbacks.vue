<script setup>
import { ref, onMounted } from 'vue'
import { FeedbackAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_category: {}, avg_rating: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', category: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      FeedbackAPI.list(filters.value),
      FeedbackAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    from_user: '', to_user: '', category: '', content: '',
    rating: 3, is_anonymous: false, status: 'pending'
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  try {
    if (form.value.id) {
      await FeedbackAPI.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await FeedbackAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    dialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

const removeItem = (row) => {
  ElMessageBox.confirm('确认删除该反馈记录?', '提示', { type: 'warning' }).then(async () => {
    await FeedbackAPI.remove(row.id)
    ElMessage.success('删除成功')
    load()
  }).catch(() => {})
}

const reviewItem = async (row) => {
  try {
    await FeedbackAPI.update(row.id, { status: 'reviewed' })
    ElMessage.success('已标记为已审阅')
    load()
  } catch { ElMessage.error('操作失败') }
}

const categoryMap = { performance: '绩效反馈', process: '流程建议', product: '产品反馈', service: '服务评价', suggestion: '意见建议', complaint: '投诉' }
const statusMap = { pending: '待处理', reviewed: '已审阅', replied: '已回复', closed: '已关闭' }
const statusColor = { pending: 'warning', reviewed: '', replied: 'success', closed: 'info' }

const ratingStars = (val) => {
  return '★'.repeat(Math.round(val)) + '☆'.repeat(5 - Math.round(val))
}

const ratingColor = (val) => {
  if (val >= 4) return '#00ff9d'
  if (val >= 3) return '#ffd23f'
  return '#ff4d9e'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="反馈管理" subtitle="员工反馈 · 评价管理 · 意见收集" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">反馈总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">平均评分</div>
        <div class="stat-value">{{ Number(stats.avg_rating || 0).toFixed(1) }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">待处理</div>
        <div class="stat-value">{{ list.filter(i => i.status === 'pending').length }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">反馈类别</div>
        <div class="stat-value">{{ Object.keys(stats.by_category || {}).length }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索用户/内容" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.category" placeholder="反馈类别" clearable @change="load" style="width: 130px">
        <el-option v-for="(v, k) in categoryMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建反馈</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="发送人" width="100">
          <template #default="{ row }">
            {{ row.is_anonymous ? '匿名' : (row.from_user || '-') }}
          </template>
        </el-table-column>
        <el-table-column prop="to_user" label="接收人" width="100" />
        <el-table-column label="类别" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ categoryMap[row.category] || row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="反馈内容" min-width="180" show-overflow-tooltip />
        <el-table-column label="评分" width="130" align="center">
          <template #default="{ row }">
            <span :style="{ color: ratingColor(row.rating), fontWeight: 600 }">
              {{ ratingStars(row.rating) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="匿名" width="70" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_anonymous ? 'info' : 'success'">
              {{ row.is_anonymous ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" size="small" type="success" @click="reviewItem(row)">审阅</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑反馈' : '新建反馈'" width="650px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="发送人"><el-input v-model="form.from_user" placeholder="发送人" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="接收人"><el-input v-model="form.to_user" placeholder="接收人" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="反馈类别">
          <el-select v-model="form.category" style="width: 100%">
            <el-option v-for="(v, k) in categoryMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="反馈内容"><el-input v-model="form.content" type="textarea" :rows="4" placeholder="请输入反馈内容" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="评分">
              <el-rate v-model="form.rating" :max="5" show-score />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="匿名">
              <el-switch v-model="form.is_anonymous" active-text="是" inactive-text="否" />
            </el-form-item>
          </el-col>
        </el-row>
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
