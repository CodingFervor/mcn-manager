<script setup>
import { ref, onMounted } from 'vue'
import { ExpenseAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total_claims: 0, pending: 0, approved: 0, pending_amount: 0 })
const loading = ref(false)
const dialog = ref(false)
const rejectDialog = ref(false)
const form = ref({})
const rejectForm = ref({})
const filters = ref({ kw: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      ExpenseAPI.list(filters.value),
      ExpenseAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { employee_id: '', title: '', category: '', amount: 0, description: '', receipt_url: '' }
  dialog.value = true
}

async function save() {
  await ExpenseAPI.create(form.value)
  dialog.value = false
  load()
}

const approveItem = async (row) => {
  await ExpenseAPI.approve(row.id, {})
  load()
}

const openReject = (row) => {
  rejectForm.value = { id: row.id, reason: '' }
  rejectDialog.value = true
}

async function submitReject() {
  await ExpenseAPI.reject(rejectForm.value.id, { reason: rejectForm.value.reason })
  rejectDialog.value = false
  load()
}

const expenseCategoryMap = { travel: '差旅', equipment: '设备', marketing: '营销', office: '办公', communication: '通讯', other: '其他' }
const expenseStatusMap = { pending: '待审批', approved: '已通过', rejected: '已驳回', paid: '已支付' }
const expenseStatusColor = { pending: 'warning', approved: 'success', rejected: 'danger', paid: 'primary' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="费用报销" subtitle="费用申请 · 审批管理 · 报销追踪" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">报销总数</div>
        <div class="stat-value">{{ stats.total_claims }}</div>
      </div>
      <div class="stat-card g4">
        <div class="stat-label">待审批</div>
        <div class="stat-value">{{ stats.pending }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">已通过</div>
        <div class="stat-value">{{ stats.approved }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">待批金额</div>
        <div class="stat-value">¥{{ Number(stats.pending_amount || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索申请人/事由" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in expenseStatusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 申请报销</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="employee_name" label="申请人" width="100" />
        <el-table-column prop="title" label="报销事由" min-width="180" show-overflow-tooltip />
        <el-table-column label="费用类型" width="100">
          <template #default="{ row }">{{ expenseCategoryMap[row.category] || row.category }}</template>
        </el-table-column>
        <el-table-column label="金额" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="expenseStatusColor[row.status]">{{ expenseStatusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="approved_by_name" label="审批人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" @click="approveItem(row)">通过</el-button>
              <el-button size="small" type="danger" @click="openReject(row)">驳回</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="申请报销" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="员工ID"><el-input-number v-model="form.employee_id" :min="1" /></el-form-item>
        <el-form-item label="报销事由"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="费用类型">
          <el-select v-model="form.category" style="width: 100%">
            <el-option v-for="(v, k) in expenseCategoryMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额"><el-input-number v-model="form.amount" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="说明"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="票据链接"><el-input v-model="form.receipt_url" placeholder="发票/收据链接" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="rejectDialog" title="驳回报销" width="500px">
      <el-form :model="rejectForm" label-width="80px">
        <el-form-item label="驳回原因"><el-input v-model="rejectForm.reason" type="textarea" :rows="4" placeholder="请填写驳回原因" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialog = false">取消</el-button>
        <el-button type="danger" @click="submitReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>
