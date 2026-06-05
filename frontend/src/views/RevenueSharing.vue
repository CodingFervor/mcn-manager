<script setup>
import { ref, onMounted } from 'vue'
import { RevenueSharingAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total_records: 0, total_revenue: 0, total_mcn_share: 0, total_anchor_share: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', period_type: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      RevenueSharingAPI.list(filters.value),
      RevenueSharingAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    title: '', period_type: 'monthly', period_start: '', period_end: '',
    store: null, anchor: null, total_revenue: 0, platform_fee: 0,
    mcn_share: 0, anchor_share: 0, mcn_ratio: 0, anchor_ratio: 0, notes: ''
  }
  dialog.value = true
}

async function save() {
  await RevenueSharingAPI.create(form.value)
  dialog.value = false
  load()
}

const settleItem = async (row) => {
  await RevenueSharingAPI.settle(row.id, {})
  load()
}

const periodTypeMap = { daily: '日结', weekly: '周结', monthly: '月结' }
const statusMap = { pending: '待结算', settled: '已结算', paid: '已打款', cancelled: '已取消' }
const statusColor = { pending: 'warning', settled: 'success', paid: 'primary', cancelled: 'info' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="MCN分成" subtitle="利润分配 · 分成结算 · 打款管理" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">记录总数</div>
        <div class="stat-value">{{ stats.total_records }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总营收</div>
        <div class="stat-value">¥{{ Number(stats.total_revenue || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">MCN分成</div>
        <div class="stat-value">¥{{ Number(stats.total_mcn_share || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">主播分成</div>
        <div class="stat-value">¥{{ Number(stats.total_anchor_share || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索结算名称" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.period_type" placeholder="周期类型" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in periodTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建分成</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="结算名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="周期类型" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ periodTypeMap[row.period_type] || row.period_type_display || row.period_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="周期" width="180">
          <template #default="{ row }">
            <span>{{ row.period_start }} ~ {{ row.period_end }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="store_name" label="店铺" width="120" />
        <el-table-column prop="anchor_name" label="主播" width="100" />
        <el-table-column label="总营收" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ Number(row.total_revenue).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="平台扣点" width="100">
          <template #default="{ row }">
            <span>¥{{ Number(row.platform_fee).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="MCN分成" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-pink); font-weight: 600">¥{{ Number(row.mcn_share).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="主播分成" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-green); font-weight: 600">¥{{ Number(row.anchor_share).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="MCN比例" width="90">
          <template #default="{ row }">{{ row.mcn_ratio }}%</template>
        </el-table-column>
        <el-table-column label="主播比例" width="90">
          <template #default="{ row }">{{ row.anchor_ratio }}%</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status_display || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" size="small" type="success" @click="settleItem(row)">结算</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建分成记录" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="结算名称"><el-input v-model="form.title" placeholder="请输入结算名称" /></el-form-item>
        <el-form-item label="周期类型">
          <el-select v-model="form.period_type" style="width: 100%">
            <el-option v-for="(v, k) in periodTypeMap" :key="k" :label="v" :value="k" />
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
          <el-col :span="12">
            <el-form-item label="店铺ID"><el-input-number v-model="form.store" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主播ID"><el-input-number v-model="form.anchor" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="总营收"><el-input-number v-model="form.total_revenue" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="平台扣点"><el-input-number v-model="form.platform_fee" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="MCN分成"><el-input-number v-model="form.mcn_share" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主播分成"><el-input-number v-model="form.anchor_share" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="MCN比例%"><el-input-number v-model="form.mcn_ratio" :min="0" :max="100" :precision="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主播比例%"><el-input-number v-model="form.anchor_ratio" :min="0" :max="100" :precision="1" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="3" placeholder="备注信息" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>
