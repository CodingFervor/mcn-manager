<script setup>
import { ref, onMounted } from 'vue'
import { InvoiceAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_status: {}, total_amount: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', invoice_type: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      InvoiceAPI.list(filters.value),
      InvoiceAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    invoice_no: '', client: '', amount: 0, tax: 0, total: 0,
    invoice_type: '', status: 'draft', issue_date: '', due_date: ''
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
      await InvoiceAPI.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await InvoiceAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    dialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

const removeItem = (row) => {
  ElMessageBox.confirm('确认删除该发票记录?', '提示', { type: 'warning' }).then(async () => {
    await InvoiceAPI.remove(row.id)
    ElMessage.success('删除成功')
    load()
  }).catch(() => {})
}

const invoiceTypeMap = { normal: '普通发票', special: '专用发票', electronic: '电子发票' }
const statusMap = { draft: '草稿', issued: '已开具', sent: '已发送', paid: '已支付', void: '已作废' }
const statusColor = { draft: 'info', issued: 'warning', sent: '', paid: 'success', void: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="发票管理" subtitle="发票开具 · 票据追踪 · 财务结算" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">发票总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总金额</div>
        <div class="stat-value">¥{{ Number(stats.total_amount || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">已支付</div>
        <div class="stat-value">{{ stats.by_status?.paid || 0 }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">待处理</div>
        <div class="stat-value">{{ (stats.by_status?.draft || 0) + (stats.by_status?.issued || 0) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索发票号/客户" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.invoice_type" placeholder="发票类型" clearable @change="load" style="width: 130px">
        <el-option v-for="(v, k) in invoiceTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建发票</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="invoice_no" label="发票号" width="160" />
        <el-table-column prop="client" label="客户" min-width="140" show-overflow-tooltip />
        <el-table-column label="发票类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ invoiceTypeMap[row.invoice_type] || row.invoice_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ Number(row.amount).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="税额" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-pink); font-weight: 600">¥{{ Number(row.tax).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="合计" width="120">
          <template #default="{ row }">
            <span style="color: #00ff9d; font-weight: 700">¥{{ Number(row.total).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="issue_date" label="开票日期" width="110" />
        <el-table-column prop="due_date" label="到期日" width="110" />
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

    <el-dialog v-model="dialog" :title="form.id ? '编辑发票' : '新建发票'" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="发票号"><el-input v-model="form.invoice_no" placeholder="请输入发票号" /></el-form-item>
        <el-form-item label="客户"><el-input v-model="form.client" placeholder="客户名称" /></el-form-item>
        <el-form-item label="发票类型">
          <el-select v-model="form.invoice_type" style="width: 100%">
            <el-option v-for="(v, k) in invoiceTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="金额"><el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="税额"><el-input-number v-model="form.tax" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="合计"><el-input-number v-model="form.total" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开票日期">
              <el-date-picker v-model="form.issue_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="到期日">
              <el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
