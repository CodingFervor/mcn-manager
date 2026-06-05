<script setup>
import { ref, onMounted } from 'vue'
import { ComplaintAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, pending: 0, urgent: 0 })
const loading = ref(false)
const dialog = ref(false)
const resolveDialog = ref(false)
const form = ref({})
const resolveForm = ref({})
const filters = ref({ kw: '', status: '', priority: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      ComplaintAPI.list(filters.value),
      ComplaintAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { order_no: '', store_id: '', customer_name: '', contact: '', complaint_type: '', description: '', priority: 'medium' }
  dialog.value = true
}

async function save() {
  await ComplaintAPI.create(form.value)
  dialog.value = false
  load()
}

const openResolve = (row) => {
  resolveForm.value = { id: row.id, resolution: '' }
  resolveDialog.value = true
}

async function submitResolve() {
  await ComplaintAPI.resolve(resolveForm.value.id, { resolution: resolveForm.value.resolution })
  resolveDialog.value = false
  load()
}

const complaintTypeMap = { quality: '质量问题', logistics: '物流问题', service: '服务态度', fake: '假货问题', description: '描述不符', other: '其他' }
const priorityMap = { low: '低', medium: '中', high: '高', urgent: '紧急' }
const priorityColor = { low: 'info', medium: '', high: 'warning', urgent: 'danger' }
const complaintStatusMap = { pending: '待处理', processing: '处理中', resolved: '已解决', closed: '已关闭' }
const complaintStatusColor = { pending: 'danger', processing: 'warning', resolved: 'success', closed: 'info' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="客户投诉" subtitle="投诉管理 · 售后处理 · 客户满意度" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">投诉总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g4">
        <div class="stat-label">待处理</div>
        <div class="stat-value">{{ stats.pending }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">紧急投诉</div>
        <div class="stat-value">{{ stats.urgent }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索订单号/客户" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in complaintStatusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.priority" placeholder="优先级" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in priorityMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建投诉</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="order_no" label="订单号" width="160" />
        <el-table-column prop="store_name" label="店铺" width="120" />
        <el-table-column prop="customer_name" label="客户" width="100" />
        <el-table-column label="投诉类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ complaintTypeMap[row.complaint_type] || row.complaint_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="priorityColor[row.priority]" effect="dark">{{ priorityMap[row.priority] || row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="complaintStatusColor[row.status]">{{ complaintStatusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="handler_name" label="处理人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending' || row.status === 'processing'" size="small" type="warning" @click="openResolve(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建投诉" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="订单号"><el-input v-model="form.order_no" /></el-form-item>
        <el-form-item label="店铺ID"><el-input-number v-model="form.store_id" :min="1" /></el-form-item>
        <el-form-item label="客户姓名"><el-input v-model="form.customer_name" /></el-form-item>
        <el-form-item label="联系方式"><el-input v-model="form.contact" /></el-form-item>
        <el-form-item label="投诉类型">
          <el-select v-model="form.complaint_type" style="width: 100%">
            <el-option v-for="(v, k) in complaintTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="投诉描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority" style="width: 100%">
            <el-option v-for="(v, k) in priorityMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resolveDialog" title="处理投诉" width="500px">
      <el-form :model="resolveForm" label-width="80px">
        <el-form-item label="处理结果"><el-input v-model="resolveForm.resolution" type="textarea" :rows="4" placeholder="请填写处理结果" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialog = false">取消</el-button>
        <el-button type="primary" @click="submitResolve">确认处理</el-button>
      </template>
    </el-dialog>
  </div>
</template>
