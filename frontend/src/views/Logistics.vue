<script setup>
import { ref, onMounted } from 'vue'
import { LogisticsAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, by_status: {}, by_type: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', logistics_type: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      LogisticsAPI.list(filters.value),
      LogisticsAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    order_no: '', product_name: '', quantity: 1,
    logistics_type: '', carrier: '', tracking_no: '',
    sender_address: '', receiver_address: ''
  }
  dialog.value = true
}

async function save() {
  if (form.value.id) {
    await LogisticsAPI.update(form.value.id, form.value)
  } else {
    await LogisticsAPI.create(form.value)
  }
  dialog.value = false
  load()
}

const shipItem = async (row) => {
  await LogisticsAPI.ship(row.id, {})
  load()
}

const deliverItem = async (row) => {
  await LogisticsAPI.deliver(row.id, {})
  load()
}

const logisticsTypeMap = { delivery: '发货', return: '退货', exchange: '换货' }
const statusMap = { pending: '待发货', shipped: '已发货', in_transit: '运输中', delivered: '已签收', returned: '已退回', lost: '丢失' }
const statusColor = { pending: 'info', shipped: 'warning', in_transit: '', delivered: 'success', returned: 'danger', lost: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="物流跟踪" subtitle="发货管理 · 物流追踪 · 签收确认" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">物流单数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">待发货</div>
        <div class="stat-value">{{ stats.by_status?.pending || 0 }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">运输中</div>
        <div class="stat-value">{{ stats.by_status?.in_transit || 0 }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">已签收</div>
        <div class="stat-value">{{ stats.by_status?.delivered || 0 }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索订单号/物流单号" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.logistics_type" placeholder="物流类型" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in logisticsTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建物流单</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="order_no" label="订单号" width="160" />
        <el-table-column prop="product_name" label="商品名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="quantity" label="数量" width="70" />
        <el-table-column label="物流类型" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ logisticsTypeMap[row.logistics_type] || row.logistics_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="carrier" label="承运商" width="100" />
        <el-table-column prop="tracking_no" label="物流单号" width="160" />
        <el-table-column prop="sender_address" label="发件地址" min-width="140" show-overflow-tooltip />
        <el-table-column prop="receiver_address" label="收件地址" min-width="140" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="shipped_at" label="发货时间" width="170" />
        <el-table-column prop="delivered_at" label="签收时间" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" size="small" type="warning" @click="shipItem(row)">发货</el-button>
            <el-button v-if="row.status === 'shipped' || row.status === 'in_transit'" size="small" type="success" @click="deliverItem(row)">签收</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建物流单" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="订单号"><el-input v-model="form.order_no" placeholder="请输入订单号" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="16">
            <el-form-item label="商品名称"><el-input v-model="form.product_name" placeholder="商品名称" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="数量"><el-input-number v-model="form.quantity" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="物流类型">
          <el-select v-model="form.logistics_type" style="width: 100%">
            <el-option v-for="(v, k) in logisticsTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="承运商"><el-input v-model="form.carrier" placeholder="承运商" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="物流单号"><el-input v-model="form.tracking_no" placeholder="物流单号" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="发件地址"><el-input v-model="form.sender_address" placeholder="发件地址" /></el-form-item>
        <el-form-item label="收件地址"><el-input v-model="form.receiver_address" placeholder="收件地址" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>
