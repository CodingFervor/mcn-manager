<script setup>
import { ref, onMounted } from 'vue'
import { OrderAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_status: {}, total_amount: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

const statusMap = { pending: '待付款', paid: '已付款', shipped: '已发货', completed: '已完成', cancelled: '已取消', refunded: '已退款' }
const statusColor = { pending: 'warning', paid: 'primary', shipped: '', completed: 'success', cancelled: 'info', refunded: 'danger' }
const sourceMap = { live: '直播间', video: '短视频', shop: '店铺' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([OrderAPI.list(filters.value), OrderAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, by_status: {}, total_amount: 0 }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { order_no: '', product_name: '', customer_name: '', quantity: 1, total_amount: 0, status: 'pending', source: 'live' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }

async function save() {
  try {
    if (form.value.id) await OrderAPI.update(form.value.id, form.value)
    else await OrderAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false; load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (row) => {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await OrderAPI.remove(row.id)
  ElMessage.success('已删除'); load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="订单管理" subtitle="订单追踪 · 状态管理 · 销售统计" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-label">订单总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">已完成</div>
        <div class="stat-value">{{ stats.by_status?.completed || 0 }}</div>
      </div>
      <div class="stat-card g4">
        <div class="stat-label">总金额</div>
        <div class="stat-value">¥{{ Number(stats.total_amount || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索订单号/商品/客户" style="width:200px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="order_no" label="订单号" width="160" show-overflow-tooltip />
        <el-table-column prop="product_name" label="商品名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="customer_name" label="客户" width="100" />
        <el-table-column label="数量" width="70">
          <template #default="{ row }">{{ row.quantity }}</template>
        </el-table-column>
        <el-table-column label="金额" width="110">
          <template #default="{ row }">
            <span style="color:var(--neon-pink);font-weight:700">¥{{ Number(row.total_amount || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="100">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ sourceMap[row.source] || row.source }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="订单管理" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="订单号"><el-input v-model="form.order_no" placeholder="请输入订单号" /></el-form-item>
        <el-form-item label="商品名称"><el-input v-model="form.product_name" placeholder="请输入商品名称" /></el-form-item>
        <el-form-item label="客户名称"><el-input v-model="form.customer_name" placeholder="请输入客户名称" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="数量"><el-input-number v-model="form.quantity" :min="1" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="金额"><el-input-number v-model="form.total_amount" :min="0" :precision="2" :step="10" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="来源">
              <el-select v-model="form.source" style="width:100%">
                <el-option v-for="(v, k) in sourceMap" :key="k" :label="v" :value="k" />
              </el-select>
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
