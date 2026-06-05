<script setup>
import { ref, onMounted } from 'vue'
import { PaymentAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_amount: 0, by_method: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', method: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      PaymentAPI.list(filters.value),
      PaymentAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    invoice_no: '', payer: '', amount: 0, method: '',
    status: 'pending', paid_at: ''
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
      await PaymentAPI.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await PaymentAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    dialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

const removeItem = (row) => {
  ElMessageBox.confirm('确认删除该付款记录?', '提示', { type: 'warning' }).then(async () => {
    await PaymentAPI.remove(row.id)
    ElMessage.success('删除成功')
    load()
  }).catch(() => {})
}

const methodMap = { bank: '银行转账', alipay: '支付宝', wechat: '微信支付', cash: '现金' }
const statusMap = { pending: '待确认', confirmed: '已确认', failed: '失败' }
const statusColor = { pending: 'warning', confirmed: 'success', failed: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="付款管理" subtitle="收款记录 · 支付确认 · 资金追踪" />

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
        <div class="stat-label">支付方式数</div>
        <div class="stat-value">{{ Object.keys(stats.by_method || {}).length }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">已确认</div>
        <div class="stat-value">{{ stats.by_method?.confirmed || 0 }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索发票号/付款方" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.method" placeholder="支付方式" clearable @change="load" style="width: 130px">
        <el-option v-for="(v, k) in methodMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建付款</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="invoice_no" label="发票号" width="160" />
        <el-table-column prop="payer" label="付款方" min-width="140" show-overflow-tooltip />
        <el-table-column label="金额" width="120">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ Number(row.amount).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="支付方式" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ methodMap[row.method] || row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="paid_at" label="支付时间" width="170" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑付款' : '新建付款'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="发票号"><el-input v-model="form.invoice_no" placeholder="关联发票号" /></el-form-item>
        <el-form-item label="付款方"><el-input v-model="form.payer" placeholder="付款方名称" /></el-form-item>
        <el-form-item label="金额"><el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 100%" /></el-form-item>
        <el-form-item label="支付方式">
          <el-select v-model="form.method" style="width: 100%">
            <el-option v-for="(v, k) in methodMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="支付时间">
          <el-date-picker v-model="form.paid_at" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
