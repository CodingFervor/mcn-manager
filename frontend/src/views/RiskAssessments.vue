<script setup>
import { ref, onMounted } from 'vue'
import { RiskAssessmentAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, low: 0, medium: 0, high: 0, critical: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', risk_type: '', severity: '' })

const riskTypeMap = { operational: '运营风险', financial: '财务风险', compliance: '合规风险', technical: '技术风险', reputational: '声誉风险' }
const severityMap = { low: '低', medium: '中', high: '高', critical: '严重' }
const severityColor = { low: 'success', medium: 'warning', high: 'danger', critical: 'danger' }
const statusMap = { open: '待处理', mitigating: '处理中', resolved: '已解决', closed: '已关闭' }
const statusColor = { open: 'danger', mitigating: 'warning', resolved: 'success', closed: 'info' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([RiskAssessmentAPI.list(filters.value), RiskAssessmentAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, low: list.value.filter(i => i.severity === 'low').length, medium: list.value.filter(i => i.severity === 'medium').length, high: list.value.filter(i => i.severity === 'high').length, critical: list.value.filter(i => i.severity === 'critical').length }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { title: '', risk_type: 'operational', severity: 'medium', probability: 'medium', description: '', mitigation_plan: '', owner: '', status: 'open' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await RiskAssessmentAPI.update(form.value.id, form.value)
    else await RiskAssessmentAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此风险评估？', '提示', { type: 'warning' })
  await RiskAssessmentAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="风险评估" subtitle="风险识别 · 严重度分析 · 缓解策略" />

    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">风险数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">低</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.low }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">中</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.medium }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">高</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ stats.high }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">严重</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.critical }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索风险标题" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.risk_type" placeholder="风险类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in riskTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.severity" placeholder="严重程度" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in severityMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建评估</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip />
        <el-table-column label="风险类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ riskTypeMap[row.risk_type] || row.risk_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="严重程度" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="severityColor[row.severity]" size="small" effect="dark">{{ severityMap[row.severity] || row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="概率" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ severityMap[row.probability] || row.probability }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="owner" label="负责人" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="风险评估" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="风险类型">
          <el-select v-model="form.risk_type" style="width:100%">
            <el-option v-for="(v, k) in riskTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="form.severity" style="width:100%">
            <el-option v-for="(v, k) in severityMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="概率">
          <el-select v-model="form.probability" style="width:100%">
            <el-option v-for="(v, k) in severityMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="缓解方案"><el-input v-model="form.mitigation_plan" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="负责人"><el-input v-model="form.owner" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
