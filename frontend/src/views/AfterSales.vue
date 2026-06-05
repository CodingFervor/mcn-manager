<script setup>
import { ref, onMounted } from 'vue'
import { AfterSalesAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, pending: 0, total_amount: 0 })
const loading = ref(false)
const dialog = ref(false)
const resolveDialog = ref(false)
const form = ref({})
const resolveForm = ref({})
const filters = ref({ kw: '', status: '', type: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      AfterSalesAPI.list(filters.value),
      AfterSalesAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    order_no: '', store: null, customer_name: '', customer_contact: '',
    type: '', reason: '', amount: 0, product_name: '', quantity: 1
  }
  dialog.value = true
}

async function save() {
  await AfterSalesAPI.create(form.value)
  dialog.value = false
  load()
}

const approveItem = async (row) => {
  await AfterSalesAPI.approve(row.id, {})
  load()
}

const openComplete = (row) => {
  resolveForm.value = { id: row.id, resolution: '' }
  resolveDialog.value = true
}

async function submitComplete() {
  await AfterSalesAPI.complete(resolveForm.value.id, { resolution: resolveForm.value.resolution })
  resolveDialog.value = false
  load()
}

const typeMap = { return: '退货', exchange: '换货', refund: '退款', repair: '维修', complaint: '投诉', other: '其他' }
const statusMap = { pending: '待处理', approved: '已通过', processing: '处理中', completed: '已完成', rejected: '已驳回', closed: '已关闭' }
const statusColor = { pending: 'danger', approved: 'success', processing: 'warning', completed: 'success', rejected: 'danger', closed: 'info' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="售后工单" subtitle="退换货管理 · 退款处理 · 客服工单" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">工单总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g4">
        <div class="stat-label">待处理</div>
        <div class="stat-value">{{ stats.pending }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">总金额</div>
        <div class="stat-value">¥{{ Number(stats.total_amount || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索订单号/客户" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.type" placeholder="类型" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建工单</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="order_no" label="订单号" width="160" />
        <el-table-column prop="store_name" label="店铺" width="120" />
        <el-table-column prop="customer_name" label="客户" width="100" />
        <el-table-column label="类型" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ typeMap[row.type] || row.type_display || row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" min-width="140" show-overflow-tooltip />
        <el-table-column label="金额" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="商品" width="120" show-overflow-tooltip />
        <el-table-column prop="quantity" label="数量" width="70" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status_display || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="handler_name" label="处理人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" @click="approveItem(row)">通过</el-button>
            </template>
            <template v-if="row.status === 'approved' || row.status === 'processing'">
              <el-button size="small" type="warning" @click="openComplete(row)">完成</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建售后工单" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="订单号"><el-input v-model="form.order_no" placeholder="请输入订单号" /></el-form-item>
        <el-form-item label="店铺ID"><el-input-number v-model="form.store" :min="1" /></el-form-item>
        <el-form-item label="客户姓名"><el-input v-model="form.customer_name" placeholder="客户姓名" /></el-form-item>
        <el-form-item label="联系方式"><el-input v-model="form.customer_contact" placeholder="联系电话" /></el-form-item>
        <el-form-item label="售后类型">
          <el-select v-model="form.type" style="width: 100%">
            <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="原因"><el-input v-model="form.reason" type="textarea" :rows="3" placeholder="售后原因" /></el-form-item>
        <el-form-item label="金额"><el-input-number v-model="form.amount" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="商品名称"><el-input v-model="form.product_name" placeholder="商品名称" /></el-form-item>
        <el-form-item label="数量"><el-input-number v-model="form.quantity" :min="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resolveDialog" title="完成工单" width="500px">
      <el-form :model="resolveForm" label-width="80px">
        <el-form-item label="处理结果"><el-input v-model="resolveForm.resolution" type="textarea" :rows="4" placeholder="请填写处理结果" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialog = false">取消</el-button>
        <el-button type="primary" @click="submitComplete">确认完成</el-button>
      </template>
    </el-dialog>
  </div>
</template>
