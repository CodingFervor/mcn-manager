<script setup>
import { ref, onMounted } from 'vue'
import { ConversionFunnelAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_visitors: 0, avg_overall_rate: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      ConversionFunnelAPI.list(filters.value),
      ConversionFunnelAPI.stats()
    ])
    list.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: list.value.length,
      total_visitors: list.value.reduce((s, i) => s + (i.total_visitors || 0), 0),
      avg_overall_rate: list.value.length ? (list.value.reduce((s, i) => s + (i.overall_rate || 0), 0) / list.value.length).toFixed(1) : 0
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', stages: '', conversion_rates: '', total_visitors: 0,
    total_conversions: 0, overall_rate: 0, period: ''
  }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = {
    ...row,
    stages: typeof row.stages === 'object' ? JSON.stringify(row.stages) : (row.stages || ''),
    conversion_rates: typeof row.conversion_rates === 'object' ? JSON.stringify(row.conversion_rates) : (row.conversion_rates || '')
  }
  dialog.value = true
}
async function save() {
  try {
    const payload = { ...form.value }
    if (typeof payload.stages === 'string') {
      try { payload.stages = JSON.parse(payload.stages) } catch { /* keep as string */ }
    }
    if (typeof payload.conversion_rates === 'string') {
      try { payload.conversion_rates = JSON.parse(payload.conversion_rates) } catch { /* keep as string */ }
    }
    if (form.value.id) await ConversionFunnelAPI.update(form.value.id, payload)
    else await ConversionFunnelAPI.create(payload)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const rateColor = (v) => v >= 5 ? '#00ff9d' : v >= 2 ? '#ffd23f' : '#ff4d9e'

const fmtMoney = (v) => {
  const n = Number(v) || 0
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toFixed(0)
}

const formatJSON = (v) => {
  if (!v) return '-'
  if (typeof v === 'string') return v
  try { return JSON.stringify(v) } catch { return String(v) }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="转化漏斗" subtitle="漏斗分析 · 转化优化 · 流失诊断" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">漏斗总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总访客数</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ fmtMoney(stats.total_visitors) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均总转化率</div>
        <div style="font-size:28px;font-weight:800" :style="{ color: rateColor(stats.avg_overall_rate) }">{{ stats.avg_overall_rate }}%</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索漏斗名称" style="width:200px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建漏斗</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="漏斗名称" min-width="140" show-overflow-tooltip />
        <el-table-column label="阶段" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="color:#a8b2d1">{{ formatJSON(row.stages) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="转化率" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="color:#7c5cff">{{ formatJSON(row.conversion_rates) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="总访客" width="100" align="right">
          <template #default="{ row }"><span style="color:#00e5ff;font-weight:600">{{ fmtMoney(row.total_visitors) }}</span></template>
        </el-table-column>
        <el-table-column label="总转化" width="100" align="right">
          <template #default="{ row }"><span style="color:#00ff9d;font-weight:600">{{ fmtMoney(row.total_conversions) }}</span></template>
        </el-table-column>
        <el-table-column label="总转化率" width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: rateColor(row.overall_rate), fontWeight: 700 }">{{ row.overall_rate }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="period" label="统计周期" width="110" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="转化漏斗" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="漏斗名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="阶段">
          <el-input v-model="form.stages" type="textarea" :rows="3" placeholder='JSON数组，如: ["访问","加购","下单","支付"]' />
        </el-form-item>
        <el-form-item label="转化率">
          <el-input v-model="form.conversion_rates" type="textarea" :rows="3" placeholder='JSON数组，如: [100,45,30,25]' />
        </el-form-item>
        <el-form-item label="总访客数"><el-input-number v-model="form.total_visitors" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="总转化数"><el-input-number v-model="form.total_conversions" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="总转化率%"><el-input-number v-model="form.overall_rate" :min="0" :max="100" :precision="1" style="width:100%" /></el-form-item>
        <el-form-item label="统计周期"><el-input v-model="form.period" placeholder="如: 2026-Q1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
