<script setup>
import { ref, onMounted } from 'vue'
import { ROIAnalysisAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_investment: 0, avg_roi: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '', kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      ROIAnalysisAPI.list(filters.value),
      ROIAnalysisAPI.stats()
    ])
    list.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: list.value.length,
      total_investment: list.value.reduce((s, i) => s + (i.investment || 0), 0),
      avg_roi: list.value.length ? (list.value.reduce((s, i) => s + (i.roi || 0), 0) / list.value.length).toFixed(1) : 0
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    campaign_name: '', investment: 0, revenue: 0, roi: 0,
    cost_per_order: 0, cost_per_click: 0, period: '', category: '', status: 'active'
  }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await ROIAnalysisAPI.update(form.value.id, form.value)
    else await ROIAnalysisAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const statusMap = { active: '进行中', completed: '已完成' }
const statusColor = { active: 'success', completed: '' }

const fmtMoney = (v) => {
  const n = Number(v) || 0
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toFixed(0)
}

const roiColor = (v) => v >= 3 ? '#00ff9d' : v >= 1 ? '#ffd23f' : '#ff4d9e'

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="ROI分析" subtitle="投资回报 · 效果评估 · 决策支持" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">分析总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总投资额</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">¥{{ fmtMoney(stats.total_investment) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均ROI</div>
        <div style="font-size:28px;font-weight:800" :style="{ color: roiColor(stats.avg_roi) }">{{ stats.avg_roi }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索活动名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建分析</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="campaign_name" label="活动名称" min-width="140" show-overflow-tooltip />
        <el-table-column label="投资额" width="110" align="right">
          <template #default="{ row }"><span style="color:#ffd23f;font-weight:600">¥{{ fmtMoney(row.investment) }}</span></template>
        </el-table-column>
        <el-table-column label="收入" width="110" align="right">
          <template #default="{ row }"><span style="color:#00ff9d;font-weight:600">¥{{ fmtMoney(row.revenue) }}</span></template>
        </el-table-column>
        <el-table-column label="ROI" width="80" align="center">
          <template #default="{ row }">
            <span :style="{ color: roiColor(row.roi), fontWeight: 700 }">{{ row.roi }}</span>
          </template>
        </el-table-column>
        <el-table-column label="单订单成本" width="110" align="right">
          <template #default="{ row }"><span style="color:#ff4d9e;font-weight:600">¥{{ row.cost_per_order }}</span></template>
        </el-table-column>
        <el-table-column label="单次点击成本" width="110" align="right">
          <template #default="{ row }"><span style="color:#7c5cff;font-weight:600">¥{{ row.cost_per_click }}</span></template>
        </el-table-column>
        <el-table-column prop="period" label="统计周期" width="100" />
        <el-table-column prop="category" label="分类" width="90" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="ROI分析" width="600px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="活动名称"><el-input v-model="form.campaign_name" /></el-form-item>
        <el-form-item label="投资额"><el-input-number v-model="form.investment" :min="0" :step="100" style="width:100%" /></el-form-item>
        <el-form-item label="收入"><el-input-number v-model="form.revenue" :min="0" :step="100" style="width:100%" /></el-form-item>
        <el-form-item label="ROI"><el-input-number v-model="form.roi" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="单订单成本"><el-input-number v-model="form.cost_per_order" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="单次点击成本"><el-input-number v-model="form.cost_per_click" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="统计周期"><el-input v-model="form.period" placeholder="如: 2026-Q1" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="form.category" placeholder="如: 品牌推广、商品推广" /></el-form-item>
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
