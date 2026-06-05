<script setup>
import { ref, computed, onMounted } from 'vue'
import { SelectionAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const selections = ref([])
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '', kw: '' })

const stats = ref({ total: 0, pending: 0, shortlisted: 0, avg_score: 0 })

async function loadStats() {
  try {
    const s = await SelectionAPI.stats()
    stats.value = { total: s.total || 0, pending: s.pending || 0, shortlisted: s.shortlisted || 0, avg_score: s.avg_score || 0 }
  } catch { stats.value = { total: selections.value.length, pending: selections.value.filter(i => i.status === 'pending').length, shortlisted: selections.value.filter(i => i.status === 'shortlisted').length, avg_score: selections.value.length ? (selections.value.reduce((a, b) => a + (b.total_score || 0), 0) / selections.value.length).toFixed(1) : 0 } }
}

async function load() {
  loading.value = true
  try {
    selections.value = await SelectionAPI.list(filters.value)
    loadStats()
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { product: null, store: null, supplier: null, suggested_by: null, commission_score: 5, market_score: 5, quality_score: 5, supply_score: 5, margin_score: 5, status: 'pending', planned_stream_date: '', target_gmv: 0, meeting_notes: '' }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await SelectionAPI.update(form.value.id, form.value)
    else await SelectionAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此选品记录？', '提示', { type: 'warning' })
  await SelectionAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const scoreColor = (score) => {
  if (score >= 8) return '#00ff9d'
  if (score >= 6) return '#ffd23f'
  if (score >= 4) return '#ff9f43'
  return '#ff4d9e'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="选品管理" subtitle="选品会管理 · 商品评分 · 选品决策" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">待审核</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.pending }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已入围</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.shortlisted }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均分</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.avg_score }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索商品ID" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="load" style="width:140px">
        <el-option label="待审核" value="pending" />
        <el-option label="已入围" value="shortlisted" />
        <el-option label="已通过" value="approved" />
        <el-option label="已拒绝" value="rejected" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新增选品</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="selections" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="product" label="商品ID" width="80" />
        <el-table-column prop="store_name" label="店铺" min-width="140" show-overflow-tooltip />
        <el-table-column prop="suggested_by_name" label="推荐人" width="100" />
        <el-table-column prop="commission_score" label="佣金评分" width="90" align="center" />
        <el-table-column prop="market_score" label="市场评分" width="90" align="center" />
        <el-table-column prop="quality_score" label="品质评分" width="90" align="center" />
        <el-table-column prop="supply_score" label="供应评分" width="90" align="center" />
        <el-table-column prop="margin_score" label="利润评分" width="90" align="center" />
        <el-table-column label="综合得分" width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: scoreColor(row.total_score), fontWeight: 800, fontSize: '15px' }">{{ row.total_score }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'approved' ? 'success' : row.status === 'shortlisted' ? 'warning' : row.status === 'rejected' ? 'danger' : 'info'" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="planned_stream_date" label="计划直播" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="选品记录" width="650px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="商品ID"><el-input-number v-model="form.product" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="店铺ID"><el-input-number v-model="form.store" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="供应商ID"><el-input-number v-model="form.supplier" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="推荐人ID"><el-input-number v-model="form.suggested_by" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="佣金评分">
          <el-slider v-model="form.commission_score" :min="1" :max="10" show-input :show-input-controls="false" style="width:100%" />
        </el-form-item>
        <el-form-item label="市场评分">
          <el-slider v-model="form.market_score" :min="1" :max="10" show-input :show-input-controls="false" style="width:100%" />
        </el-form-item>
        <el-form-item label="品质评分">
          <el-slider v-model="form.quality_score" :min="1" :max="10" show-input :show-input-controls="false" style="width:100%" />
        </el-form-item>
        <el-form-item label="供应评分">
          <el-slider v-model="form.supply_score" :min="1" :max="10" show-input :show-input-controls="false" style="width:100%" />
        </el-form-item>
        <el-form-item label="利润评分">
          <el-slider v-model="form.margin_score" :min="1" :max="10" show-input :show-input-controls="false" style="width:100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="待审核" value="pending" />
            <el-option label="已入围" value="shortlisted" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划直播日期"><el-date-picker v-model="form.planned_stream_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="目标GMV"><el-input-number v-model="form.target_gmv" :min="0" :step="1000" style="width:100%" /></el-form-item>
        <el-form-item label="会议备注"><el-input v-model="form.meeting_notes" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
