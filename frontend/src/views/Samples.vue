<script setup>
import { ref, onMounted } from 'vue'
import { SampleAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const samples = ref([])
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '', kw: '' })

const stats = ref({ total: 0, in_transit: 0, testing: 0, overdue: 0 })

async function loadStats() {
  try {
    const s = await SampleAPI.stats()
    stats.value = { total: s.total || 0, in_transit: s.in_transit || 0, testing: s.testing || 0, overdue: s.overdue || 0 }
  } catch {
    stats.value = {
      total: samples.value.length,
      in_transit: samples.value.filter(i => i.status === 'in_transit').length,
      testing: samples.value.filter(i => i.status === 'testing').length,
      overdue: samples.value.filter(i => i.status === 'overdue').length,
    }
  }
}

async function load() {
  loading.value = true
  try {
    samples.value = await SampleAPI.list(filters.value)
    loadStats()
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { product: null, supplier: null, name: '', quantity: 1, batch_no: '', status: 'requested', requested_by: null, assigned_to: null, store: null, received_date: '', return_deadline: '', test_result: '', notes: '' }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await SampleAPI.update(form.value.id, form.value)
    else await SampleAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此样品记录？', '提示', { type: 'warning' })
  await SampleAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}
const receive = async (row) => {
  await ElMessageBox.confirm('确认收到此样品？', '提示', { type: 'info' })
  await SampleAPI.receive(row.id)
  ElMessage.success('已确认收货')
  load()
}
const returnSample = async (row) => {
  await ElMessageBox.confirm('确认归还此样品？', '提示', { type: 'info' })
  await SampleAPI.returnSample(row.id)
  ElMessage.success('已确认归还')
  load()
}

const statusTagType = (status) => {
  const map = { requested: 'info', in_transit: 'warning', received: '', testing: 'success', returned: 'info', overdue: 'danger' }
  return map[status] || 'info'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="样品管理" subtitle="样品收发 · 测试管理 · 归还追踪" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">运输中</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.in_transit }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">测试中</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.testing }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">逾期</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ stats.overdue }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索样品名称/批次号" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="load" style="width:140px">
        <el-option label="已申请" value="requested" />
        <el-option label="运输中" value="in_transit" />
        <el-option label="已收到" value="received" />
        <el-option label="测试中" value="testing" />
        <el-option label="已归还" value="returned" />
        <el-option label="逾期" value="overdue" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新增样品</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="samples" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="样品名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="product" label="商品ID" width="80" />
        <el-table-column prop="supplier" label="供应商ID" width="90" />
        <el-table-column prop="quantity" label="数量" width="70" align="center" />
        <el-table-column prop="batch_no" label="批次号" width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="requested_by_name" label="申请人" width="100" />
        <el-table-column prop="assigned_to_name" label="使用人" width="100" />
        <el-table-column prop="received_date" label="收到日期" width="110" />
        <el-table-column prop="return_deadline" label="归还截止" width="110" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'in_transit'" size="small" type="success" @click="receive(row)">收货</el-button>
            <el-button v-if="row.status === 'testing' || row.status === 'received'" size="small" type="warning" @click="returnSample(row)">归还</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="样品记录" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="商品ID"><el-input-number v-model="form.product" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="供应商ID"><el-input-number v-model="form.supplier" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="样品名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="数量"><el-input-number v-model="form.quantity" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="批次号"><el-input v-model="form.batch_no" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="已申请" value="requested" />
            <el-option label="运输中" value="in_transit" />
            <el-option label="已收到" value="received" />
            <el-option label="测试中" value="testing" />
            <el-option label="已归还" value="returned" />
            <el-option label="逾期" value="overdue" />
          </el-select>
        </el-form-item>
        <el-form-item label="申请人ID"><el-input-number v-model="form.requested_by" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="使用人ID"><el-input-number v-model="form.assigned_to" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="店铺ID"><el-input-number v-model="form.store" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="收到日期"><el-date-picker v-model="form.received_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="归还截止"><el-date-picker v-model="form.return_deadline" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="测试结果"><el-input v-model="form.test_result" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
