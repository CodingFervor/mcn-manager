<script setup>
import { ref, onMounted } from 'vue'
import { ContractLedgerAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_type: {}, total_amount: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', contract_type: '' })

const contractTypeMap = { brand: '品牌合同', anchor: '主播合同', supplier: '供应商合同', platform: '平台合同', service: '服务合同', other: '其他' }
const statusMap = { draft: '草稿', signed: '已签署', active: '履行中', expired: '已到期', terminated: '已终止' }
const statusColor = { draft: 'info', signed: '', active: 'success', expired: 'warning', terminated: 'danger' }

async function loadStats() {
  try {
    const s = await ContractLedgerAPI.stats()
    stats.value = { total: s.total || 0, by_type: s.by_type || {}, total_amount: s.total_amount || 0 }
  } catch {
    stats.value = {
      total: list.value.length,
      by_type: {},
      total_amount: list.value.reduce((a, b) => a + (b.amount || 0), 0)
    }
  }
}

async function load() {
  loading.value = true
  try {
    list.value = await ContractLedgerAPI.list(filters.value)
    loadStats()
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', contract_no: '', contract_type: 'brand', party_a: '', party_b: '',
    amount: 0, sign_date: '', start_date: '', end_date: '', file_url: '',
    remind_days: 30, status: 'draft'
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  try {
    if (form.value.id) await ContractLedgerAPI.update(form.value.id, form.value)
    else await ContractLedgerAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除该合同记录？', '提示', { type: 'warning' })
    await ContractLedgerAPI.remove(id)
    ElMessage.success('删除成功')
    load()
  } catch {}
}

const isExpiringSoon = (row) => {
  if (row.status !== 'active' || !row.end_date) return false
  const daysLeft = Math.ceil((new Date(row.end_date) - new Date()) / (1000 * 60 * 60 * 24))
  return daysLeft >= 0 && daysLeft <= (row.remind_days || 30)
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="合同台账" subtitle="合同归档 · 到期提醒 · 全生命周期" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">合同总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">履行中</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.by_type.active || 0 }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">合同总金额</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">¥{{ Number(stats.total_amount || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索合同名称/编号" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.contract_type" placeholder="合同类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in contractTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建合同</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="合同名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="contract_no" label="合同编号" width="140" show-overflow-tooltip />
        <el-table-column label="合同类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ contractTypeMap[row.contract_type] || row.contract_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="party_a" label="甲方" width="120" show-overflow-tooltip />
        <el-table-column prop="party_b" label="乙方" width="120" show-overflow-tooltip />
        <el-table-column label="金额" width="110" align="center">
          <template #default="{ row }">
            <span style="color:#00e5ff;font-weight:600">¥{{ Number(row.amount || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="sign_date" label="签署日期" width="110" />
        <el-table-column label="合同周期" width="200">
          <template #default="{ row }">
            <span>{{ row.start_date }} ~ {{ row.end_date }}</span>
          </template>
        </el-table-column>
        <el-table-column label="到期提醒" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="isExpiringSoon(row)" type="danger" size="small" effect="dark">即将到期</el-tag>
            <span v-else style="color:#a8b2d1">{{ row.remind_days }}天</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status_display || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑合同' : '新建合同'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="合同名称"><el-input v-model="form.name" placeholder="合同名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合同编号"><el-input v-model="form.contract_no" placeholder="合同编号" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="合同类型">
              <el-select v-model="form.contract_type" style="width:100%">
                <el-option v-for="(v, k) in contractTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合同金额">
              <el-input-number v-model="form.amount" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="甲方"><el-input v-model="form.party_a" placeholder="甲方名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="乙方"><el-input v-model="form.party_b" placeholder="乙方名称" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="签署日期">
              <el-date-picker v-model="form.sign_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="开始日期">
              <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="结束日期">
              <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
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
            <el-form-item label="提醒天数">
              <el-input-number v-model="form.remind_days" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="合同文件"><el-input v-model="form.file_url" placeholder="合同文件链接" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
