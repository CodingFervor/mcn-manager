<script setup>
import { ref, onMounted } from 'vue'
import { TaxRecordAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, total_amount: 0, total_tax: 0, by_type: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', tax_type: '', period: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      TaxRecordAPI.list(filters.value),
      TaxRecordAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    tax_type: '', invoice_no: '', amount: 0, tax_amount: 0,
    tax_rate: 0, counterparty: '', invoice_date: '',
    period: '', file_url: '', status: 'pending'
  }
  dialog.value = true
}

async function save() {
  if (form.value.id) {
    await TaxRecordAPI.update(form.value.id, form.value)
  } else {
    await TaxRecordAPI.create(form.value)
  }
  dialog.value = false
  load()
}

const removeItem = async (row) => {
  await TaxRecordAPI.remove(row.id)
  load()
}

const loadByPeriod = async () => {
  if (!filters.value.period) { load(); return }
  loading.value = true
  try {
    const data = await TaxRecordAPI.byPeriod(filters.value.period)
    list.value = data
  } finally { loading.value = false }
}

const taxTypeMap = { invoice_out: '销项发票', invoice_in: '进项发票', vat: '增值税', income_tax: '企业所得税', individual_tax: '个人所得税', stamp_tax: '印花税' }
const statusMap = { pending: '待处理', issued: '已开具', received: '已收到', filed: '已申报', paid: '已缴纳' }
const statusColor = { pending: 'info', issued: 'warning', received: 'success', filed: '', paid: 'primary' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="税务管理" subtitle="发票管理 · 纳税申报 · 税务合规" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">记录总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总金额</div>
        <div class="stat-value">¥{{ Number(stats.total_amount || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">总税额</div>
        <div class="stat-value">¥{{ Number(stats.total_tax || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">发票类型</div>
        <div class="stat-value">{{ Object.keys(stats.by_type || {}).length }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索发票号/交易方" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.tax_type" placeholder="税务类型" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in taxTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-input v-model="filters.period" placeholder="期间(YYYY-MM)" style="width: 140px" @keyup.enter="loadByPeriod" />
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建税务记录</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="税务类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ taxTypeMap[row.tax_type] || row.tax_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="invoice_no" label="发票号" width="160" />
        <el-table-column label="金额" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ Number(row.amount).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="税额" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-pink); font-weight: 600">¥{{ Number(row.tax_amount).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="税率" width="80">
          <template #default="{ row }">{{ row.tax_rate }}%</template>
        </el-table-column>
        <el-table-column prop="counterparty" label="交易方" min-width="140" show-overflow-tooltip />
        <el-table-column prop="invoice_date" label="发票日期" width="110" />
        <el-table-column prop="period" label="期间" width="100" />
        <el-table-column label="附件" width="80">
          <template #default="{ row }">
            <a v-if="row.file_url" :href="row.file_url" target="_blank" style="color: var(--neon-cyan)">查看</a>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建税务记录" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="税务类型">
          <el-select v-model="form.tax_type" style="width: 100%">
            <el-option v-for="(v, k) in taxTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="发票号"><el-input v-model="form.invoice_no" placeholder="请输入发票号" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="金额"><el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="税额"><el-input-number v-model="form.tax_amount" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="税率%"><el-input-number v-model="form.tax_rate" :min="0" :max="100" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="交易方"><el-input v-model="form.counterparty" placeholder="交易方名称" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="发票日期">
              <el-date-picker v-model="form.invoice_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="期间"><el-input v-model="form.period" placeholder="YYYY-MM" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="附件URL"><el-input v-model="form.file_url" placeholder="发票附件地址" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>
