<script setup>
import { ref, onMounted } from 'vue'
import { RefundAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_status: {}, total_amount: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      RefundAPI.list(filters.value),
      RefundAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    order_no: '', product_name: '', reason: '', amount: 0, status: 'pending'
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await RefundAPI.update(form.value.id, form.value)
  else await RefundAPI.create(form.value)
  ElMessage.success(form.value.id ? '更新成功' : '创建成功')
  dialog.value = false
  load()
}

const removeItem = async (row) => {
  await ElMessageBox.confirm('确认删除该退款记录？', '提示', { type: 'warning' })
  await RefundAPI.update(row.id, { ...row, status: 'rejected' })
  ElMessage.success('操作成功')
  load()
}

const statusMap = { pending: '待处理', approved: '已批准', rejected: '已驳回', completed: '已完成' }
const statusColor = { pending: 'warning', approved: 'success', rejected: 'danger', completed: 'info' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="退款管理" subtitle="退款审核 · 退款追踪 · 金额统计" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">退款总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">各状态统计</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">
          <span v-for="(v, k) in stats.by_status" :key="k" style="margin:0 4px;font-size:16px">
            {{ statusMap[k] || k }}: {{ v }}
          </span>
        </div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">退款总金额</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">¥{{ Number(stats.total_amount || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索订单号/商品" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建退款</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="order_no" label="订单号" width="160" />
        <el-table-column prop="product_name" label="商品名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="reason" label="退款原因" min-width="140" show-overflow-tooltip />
        <el-table-column label="退款金额" width="110">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan);font-weight:600">¥{{ row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑退款' : '新建退款'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="订单号"><el-input v-model="form.order_no" placeholder="请输入订单号" /></el-form-item>
        <el-form-item label="商品名称"><el-input v-model="form.product_name" placeholder="请输入商品名称" /></el-form-item>
        <el-form-item label="退款原因"><el-input v-model="form.reason" type="textarea" :rows="3" placeholder="请输入退款原因" /></el-form-item>
        <el-form-item label="退款金额"><el-input-number v-model="form.amount" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
