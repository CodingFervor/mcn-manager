<script setup>
import { ref, onMounted } from 'vue'
import { ComplianceAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const reviews = ref([])
const loading = ref(false)
const dialog = ref(false)
const actionDialog = ref(false)
const actionType = ref('')
const currentRow = ref(null)
const form = ref({})
const actionForm = ref({})

const filters = ref({ status: '', review_type: '' })
const stats = ref({ total: 0, pending: 0, high_risk: 0 })

async function loadStats() {
  try {
    const s = await ComplianceAPI.stats()
    stats.value = { total: s.total || 0, pending: s.pending || 0, high_risk: s.high_risk || 0 }
  } catch {
    stats.value = {
      total: reviews.value.length,
      pending: reviews.value.filter(i => i.status === 'pending').length,
      high_risk: reviews.value.filter(i => i.risk_level === 'high').length,
    }
  }
}

async function load() {
  loading.value = true
  try {
    reviews.value = await ComplianceAPI.list(filters.value)
    loadStats()
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { title: '', review_type: 'content', content: '', related_session: null, store: null, risk_level: 'low', submitted_by: null }
  dialog.value = true
}
async function save() {
  try {
    await ComplianceAPI.create(form.value)
    ElMessage.success('提交成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('提交失败') }
}

const openApprove = (row) => {
  currentRow.value = row
  actionType.value = 'approve'
  actionForm.value = { suggestions: '' }
  actionDialog.value = true
}
const openReject = (row) => {
  currentRow.value = row
  actionType.value = 'reject'
  actionForm.value = { violations: '', suggestions: '' }
  actionDialog.value = true
}
async function submitAction() {
  try {
    if (actionType.value === 'approve') {
      await ComplianceAPI.approve(currentRow.value.id, actionForm.value)
      ElMessage.success('已通过审核')
    } else {
      if (!actionForm.value.violations) { ElMessage.warning('请填写违规说明'); return }
      await ComplianceAPI.reject(currentRow.value.id, actionForm.value)
      ElMessage.success('已拒绝审核')
    }
    actionDialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

const riskColor = (level) => {
  const map = { high: '#ff4d9e', medium: '#ffd23f', low: '#00ff9d' }
  return map[level] || '#a8b2d1'
}
const riskTagType = (level) => {
  const map = { high: 'danger', medium: 'warning', low: 'success' }
  return map[level] || 'info'
}
const statusTagType = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="合规审核" subtitle="内容审核 · 广告法合规 · 风险管控" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">审核总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">待审核</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.pending }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">高风险</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ stats.high_risk }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-select v-model="filters.review_type" placeholder="审核类型" clearable @change="load" style="width:140px">
        <el-option label="内容审核" value="content" />
        <el-option label="广告法合规" value="ad_law" />
        <el-option label="产品合规" value="product" />
        <el-option label="话术合规" value="script" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="load" style="width:140px">
        <el-option label="待审核" value="pending" />
        <el-option label="已通过" value="approved" />
        <el-option label="已拒绝" value="rejected" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新增审核</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="reviews" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="审核标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="审核类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.review_type_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="风险等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="riskTagType(row.risk_level)" size="small" effect="dark">{{ row.risk_level_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ row.status_display || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reviewer_name" label="审核人" width="100" />
        <el-table-column prop="submitted_by_name" label="提交人" width="100" />
        <el-table-column prop="store_name" label="店铺" width="120" show-overflow-tooltip />
        <el-table-column prop="submitted_at" label="提交时间" width="160" />
        <el-table-column prop="reviewed_at" label="审核时间" width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" size="small" type="success" @click="openApprove(row)">通过</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="danger" @click="openReject(row)">拒绝</el-button>
            <span v-if="row.status !== 'pending'" style="color:#a8b2d1;font-size:12px">已处理</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新增合规审核" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="审核标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="审核类型">
          <el-select v-model="form.review_type" style="width:100%">
            <el-option label="内容审核" value="content" />
            <el-option label="广告法合规" value="ad_law" />
            <el-option label="产品合规" value="product" />
            <el-option label="话术合规" value="script" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核内容"><el-input v-model="form.content" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="关联场次ID"><el-input-number v-model="form.related_session" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="店铺ID"><el-input-number v-model="form.store" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="form.risk_level" style="width:100%">
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item label="提交人ID"><el-input-number v-model="form.submitted_by" :min="1" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交审核</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="actionDialog" :title="actionType === 'approve' ? '通过审核' : '拒绝审核'" width="500px">
      <el-form :model="actionForm" label-width="100px">
        <el-form-item v-if="actionType === 'reject'" label="违规说明">
          <el-input v-model="actionForm.violations" type="textarea" :rows="3" placeholder="请填写违规内容说明" />
        </el-form-item>
        <el-form-item label="审核建议">
          <el-input v-model="actionForm.suggestions" type="textarea" :rows="3" placeholder="请填写审核建议" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="actionDialog = false">取消</el-button>
        <el-button :type="actionType === 'approve' ? 'success' : 'danger'" @click="submitAction">{{ actionType === 'approve' ? '确认通过' : '确认拒绝' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>
