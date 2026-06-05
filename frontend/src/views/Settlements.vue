<script setup>
import { ref, onMounted } from 'vue'
import { SettlementAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, total_gmv: 0, total_commission: 0, total_final: 0, by_status: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', settlement_type: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      SettlementAPI.list(filters.value),
      SettlementAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    settlement_type: '', period_start: '', period_end: '',
    anchor: null, brand: null, store: null,
    total_gmv: 0, total_orders: 0, refund_amount: 0,
    commission: 0, share_amount: 0, deduction: 0, final_amount: 0,
    status: 'draft'
  }
  dialog.value = true
}

async function save() {
  if (form.value.id) {
    await SettlementAPI.update(form.value.id, form.value)
  } else {
    await SettlementAPI.create(form.value)
  }
  dialog.value = false
  load()
}

const approveItem = async (row) => {
  await SettlementAPI.approve(row.id, {})
  load()
}

const payItem = async (row) => {
  await SettlementAPI.pay(row.id, {})
  load()
}

const settlementTypeMap = { anchor: '主播结算', platform: '平台结算', brand: '品牌结算', supplier: '供应商结算' }
const statusMap = { draft: '草稿', confirmed: '已确认', approved: '已审核', paid: '已打款', disputed: '有争议' }
const statusColor = { draft: 'info', confirmed: 'warning', approved: 'success', paid: 'primary', disputed: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="结算管理" subtitle="MCN结算 · 佣金核算 · 打款管理" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">结算单数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总GMV</div>
        <div class="stat-value">¥{{ Number(stats.total_gmv || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">总佣金</div>
        <div class="stat-value">¥{{ Number(stats.total_commission || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">最终结算</div>
        <div class="stat-value">¥{{ Number(stats.total_final || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索结算单" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.settlement_type" placeholder="结算类型" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in settlementTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建结算单</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="结算类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ settlementTypeMap[row.settlement_type] || row.settlement_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="结算周期" width="180">
          <template #default="{ row }">
            <span>{{ row.period_start }} ~ {{ row.period_end }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="anchor_name" label="主播" width="100" />
        <el-table-column prop="brand_name" label="品牌" width="100" />
        <el-table-column prop="store_name" label="店铺" width="100" />
        <el-table-column label="总GMV" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ Number(row.total_gmv).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_orders" label="订单数" width="80" />
        <el-table-column label="退款金额" width="100">
          <template #default="{ row }">
            <span>¥{{ Number(row.refund_amount).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="佣金" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-pink); font-weight: 600">¥{{ Number(row.commission).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="分成金额" width="100">
          <template #default="{ row }">
            <span>¥{{ Number(row.share_amount).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="扣款" width="90">
          <template #default="{ row }">
            <span>¥{{ Number(row.deduction).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="最终金额" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-green); font-weight: 600">¥{{ Number(row.final_amount).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'confirmed'" size="small" type="success" @click="approveItem(row)">审核</el-button>
            <el-button v-if="row.status === 'approved'" size="small" type="primary" @click="payItem(row)">打款</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建结算单" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="结算类型">
          <el-select v-model="form.settlement_type" style="width: 100%">
            <el-option v-for="(v, k) in settlementTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始日期">
              <el-date-picker v-model="form.period_start" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期">
              <el-date-picker v-model="form.period_end" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="主播ID"><el-input-number v-model="form.anchor" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="品牌ID"><el-input-number v-model="form.brand" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="店铺ID"><el-input-number v-model="form.store" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="总GMV"><el-input-number v-model="form.total_gmv" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="订单数"><el-input-number v-model="form.total_orders" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="退款金额"><el-input-number v-model="form.refund_amount" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="佣金"><el-input-number v-model="form.commission" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分成金额"><el-input-number v-model="form.share_amount" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="扣款"><el-input-number v-model="form.deduction" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="最终金额"><el-input-number v-model="form.final_amount" :min="0" :precision="2" style="width: 100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>
