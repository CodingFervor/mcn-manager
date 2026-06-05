<script setup>
import { ref, onMounted } from 'vue'
import { ReturnAnalysisAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, total_amount: 0, by_reason: {}, by_status: {} })
const loading = ref(false)
const dialog = ref(false)
const resolveDialog = ref(false)
const form = ref({})
const resolveForm = ref({})
const filters = ref({ kw: '', status: '', reason: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      ReturnAnalysisAPI.list(filters.value),
      ReturnAnalysisAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    order_no: '', product: null, anchor: null, session: null,
    reason: '', detail: '', amount: 0, status: 'pending', improvement: ''
  }
  dialog.value = true
}

async function save() {
  if (form.value.id) {
    await ReturnAnalysisAPI.update(form.value.id, form.value)
  } else {
    await ReturnAnalysisAPI.create(form.value)
  }
  dialog.value = false
  load()
}

const openResolve = (row) => {
  resolveForm.value = { id: row.id, improvement: '' }
  resolveDialog.value = true
}

async function submitResolve() {
  await ReturnAnalysisAPI.resolve(resolveForm.value.id, { improvement: resolveForm.value.improvement })
  resolveDialog.value = false
  load()
}

const reasonMap = { quality: '质量问题', description: '描述不符', wrong: '发错货', damage: '破损', size: '尺码问题', change_mind: '不想要了', other: '其他' }
const statusMap = { pending: '待处理', approved: '已通过', rejected: '已驳回', refunded: '已退款', resolved: '已解决' }
const statusColor = { pending: 'warning', approved: 'success', rejected: 'danger', refunded: 'primary', resolved: 'success' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="退货分析" subtitle="退货原因 · 改进措施 · 品质提升" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">退货总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">退货总金额</div>
        <div class="stat-value">¥{{ Number(stats.total_amount || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">待处理</div>
        <div class="stat-value">{{ stats.by_status?.pending || 0 }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">已解决</div>
        <div class="stat-value">{{ stats.by_status?.resolved || 0 }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索订单号" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.reason" placeholder="退货原因" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in reasonMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建退货记录</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="order_no" label="订单号" width="160" />
        <el-table-column prop="product_name" label="商品" min-width="140" show-overflow-tooltip />
        <el-table-column prop="anchor_name" label="主播" width="100" />
        <el-table-column prop="session_name" label="直播场次" width="120" show-overflow-tooltip />
        <el-table-column label="退货原因" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ reasonMap[row.reason] || row.reason }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详细说明" min-width="140" show-overflow-tooltip />
        <el-table-column label="金额" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ Number(row.amount).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="improvement" label="改进措施" min-width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending' || row.status === 'approved'" size="small" type="warning" @click="openResolve(row)">解决</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建退货记录" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="订单号"><el-input v-model="form.order_no" placeholder="请输入订单号" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="商品ID"><el-input-number v-model="form.product" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主播ID"><el-input-number v-model="form.anchor" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="直播场次ID"><el-input-number v-model="form.session" :min="1" style="width: 100%" /></el-form-item>
        <el-form-item label="退货原因">
          <el-select v-model="form.reason" style="width: 100%">
            <el-option v-for="(v, k) in reasonMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="详细说明"><el-input v-model="form.detail" type="textarea" :rows="3" placeholder="退货详细说明" /></el-form-item>
        <el-form-item label="金额"><el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resolveDialog" title="解决退货" width="500px">
      <el-form :model="resolveForm" label-width="80px">
        <el-form-item label="改进措施">
          <el-input v-model="resolveForm.improvement" type="textarea" :rows="4" placeholder="请填写改进措施" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialog = false">取消</el-button>
        <el-button type="primary" @click="submitResolve">确认解决</el-button>
      </template>
    </el-dialog>
  </div>
</template>
