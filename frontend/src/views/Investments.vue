<script setup>
import { ref, onMounted } from 'vue'
import { InvestmentAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_stage: {}, avg_score: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', stage: '', source: '' })

const sourceMap = { referral: '转介绍', exhibition: '展会', online: '线上', cold_call: '电话营销', other: '其他' }
const stageMap = { inquiry: '咨询', qualified: '意向确认', sample: '样品阶段', trial: '试播阶段', formal: '正式合作', paused: '已暂停' }
const stageColor = { inquiry: 'info', qualified: '', sample: 'warning', trial: 'primary', formal: 'success', paused: 'danger' }

async function loadStats() {
  try {
    const s = await InvestmentAPI.stats()
    stats.value = { total: s.total || 0, by_stage: s.by_stage || {}, avg_score: s.avg_score || 0 }
  } catch {
    stats.value = {
      total: list.value.length,
      by_stage: {},
      avg_score: list.value.length ? (list.value.reduce((a, b) => a + (b.score || 0), 0) / list.value.length).toFixed(1) : 0
    }
  }
}

async function load() {
  loading.value = true
  try {
    list.value = await InvestmentAPI.list(filters.value)
    loadStats()
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    brand_name: '', contact: '', phone: '', category: '',
    source: 'online', commission_rate: 0, monthly_budget: 0,
    stage: 'inquiry', score: 0, remark: ''
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  try {
    if (form.value.id) await InvestmentAPI.update(form.value.id, form.value)
    else await InvestmentAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除该招商记录？', '提示', { type: 'warning' })
    await InvestmentAPI.remove(id)
    ElMessage.success('删除成功')
    load()
  } catch {}
}

const scoreColor = (score) => {
  if (score >= 80) return '#00ff9d'
  if (score >= 60) return '#ffd23f'
  if (score >= 40) return '#00e5ff'
  return '#ff4d9e'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="招商管理" subtitle="商家入驻 · 意向评分 · 招商漏斗" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">招商总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">正式合作</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.by_stage.formal || 0 }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均意向评分</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ Number(stats.avg_score || 0).toFixed(1) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索品牌/联系人" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.source" placeholder="来源渠道" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in sourceMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.stage" placeholder="阶段" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in stageMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建招商</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="brand_name" label="品牌名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="contact" label="联系人" width="100" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="category" label="品类" width="100" show-overflow-tooltip />
        <el-table-column label="来源" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ sourceMap[row.source] || row.source }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="佣金比例" width="100" align="center">
          <template #default="{ row }">
            <span style="color:#00e5ff;font-weight:600">{{ row.commission_rate }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="月预算" width="110" align="center">
          <template #default="{ row }">
            <span style="color:#00ff9d;font-weight:600">¥{{ Number(row.monthly_budget || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="阶段" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="stageColor[row.stage]" size="small">{{ stageMap[row.stage] || row.stage_display || row.stage }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="意向评分" width="100" align="center">
          <template #default="{ row }">
            <span style="font-weight:700" :style="{ color: scoreColor(row.score) }">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑招商' : '新建招商'" width="700px">
      <el-form :model="form" label-width="110px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="品牌名称"><el-input v-model="form.brand_name" placeholder="品牌名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="品类"><el-input v-model="form.category" placeholder="主营品类" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="联系人"><el-input v-model="form.contact" placeholder="联系人姓名" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话"><el-input v-model="form.phone" placeholder="联系电话" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="来源渠道">
              <el-select v-model="form.source" style="width:100%">
                <el-option v-for="(v, k) in sourceMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="阶段">
              <el-select v-model="form.stage" style="width:100%">
                <el-option v-for="(v, k) in stageMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="佣金比例%">
              <el-input-number v-model="form.commission_rate" :min="0" :max="100" :precision="1" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="月预算">
              <el-input-number v-model="form.monthly_budget" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="意向评分">
          <el-input-number v-model="form.score" :min="0" :max="100" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="3" placeholder="备注信息" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
