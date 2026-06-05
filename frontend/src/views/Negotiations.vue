<script setup>
import { ref, onMounted } from 'vue'
import { NegotiationAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_stage: {}, avg_probability: 0, total_budget: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', stage: '', cooperation_type: '' })

const coopTypeMap = { live_sale: '直播带货', brand_ambassador: '品牌代言', content: '内容合作', event: '活动合作' }
const stageMap = { initial: '初步接触', negotiating: '商务谈判', proposal: '方案报价', contract: '合同签署', closed: '已成交', lost: '已流失' }
const stageColor = { initial: 'info', negotiating: '', proposal: 'warning', contract: 'primary', closed: 'success', lost: 'danger' }

async function loadStats() {
  try {
    const s = await NegotiationAPI.stats()
    stats.value = { total: s.total || 0, by_stage: s.by_stage || {}, avg_probability: s.avg_probability || 0, total_budget: s.total_budget || 0 }
  } catch {
    stats.value = {
      total: list.value.length,
      by_stage: {},
      avg_probability: list.value.length ? Math.round(list.value.reduce((a, b) => a + (b.probability || 0), 0) / list.value.length) : 0,
      total_budget: list.value.reduce((a, b) => a + (b.budget || 0), 0)
    }
  }
}

async function load() {
  loading.value = true
  try {
    list.value = await NegotiationAPI.list(filters.value)
    loadStats()
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    brand: null, anchor: null, contact_name: '', contact_phone: '',
    cooperation_type: 'live_sale', budget: 0, stage: 'initial', probability: 0,
    note: '', next_follow_up: ''
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  try {
    if (form.value.id) await NegotiationAPI.update(form.value.id, form.value)
    else await NegotiationAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除该洽谈记录？', '提示', { type: 'warning' })
    await NegotiationAPI.remove(id)
    ElMessage.success('删除成功')
    load()
  } catch {}
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="商务洽谈" subtitle="洽谈记录 · 商机漏斗 · 跟进管理" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">洽谈总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">成交/谈判中</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ (stats.by_stage.closed || 0) + (stats.by_stage.negotiating || 0) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均成交概率</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ Number(stats.avg_probability || 0).toFixed(0) }}%</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总预算额</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">¥{{ Number(stats.total_budget || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索品牌/联系人" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.cooperation_type" placeholder="合作类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in coopTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.stage" placeholder="阶段" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in stageMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建洽谈</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="brand_name" label="品牌" min-width="120" show-overflow-tooltip />
        <el-table-column prop="anchor_name" label="主播" width="100" show-overflow-tooltip />
        <el-table-column prop="contact_name" label="联系人" width="100" />
        <el-table-column prop="contact_phone" label="联系电话" width="130" />
        <el-table-column label="合作类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ coopTypeMap[row.cooperation_type] || row.cooperation_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预算" width="110" align="center">
          <template #default="{ row }">
            <span style="color:#00e5ff;font-weight:600">¥{{ Number(row.budget || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="阶段" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="stageColor[row.stage]" size="small">{{ stageMap[row.stage] || row.stage_display || row.stage }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="成交概率" width="100" align="center">
          <template #default="{ row }">
            <span style="font-weight:600" :style="{ color: row.probability >= 70 ? '#00ff9d' : row.probability >= 40 ? '#ffd23f' : '#ff4d9e' }">{{ row.probability }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="next_follow_up" label="下次跟进" width="120" />
        <el-table-column prop="note" label="备注" min-width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑洽谈' : '新建洽谈'" width="700px">
      <el-form :model="form" label-width="110px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="品牌ID"><el-input-number v-model="form.brand" :min="1" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主播ID"><el-input-number v-model="form.anchor" :min="1" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="联系人"><el-input v-model="form.contact_name" placeholder="联系人姓名" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话"><el-input v-model="form.contact_phone" placeholder="联系电话" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="合作类型">
              <el-select v-model="form.cooperation_type" style="width:100%">
                <el-option v-for="(v, k) in coopTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预算金额">
              <el-input-number v-model="form.budget" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="阶段">
              <el-select v-model="form.stage" style="width:100%">
                <el-option v-for="(v, k) in stageMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成交概率%">
              <el-input-number v-model="form.probability" :min="0" :max="100" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="下次跟进">
          <el-date-picker v-model="form.next_follow_up" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.note" type="textarea" :rows="3" placeholder="洽谈备注" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
