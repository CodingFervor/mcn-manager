<script setup>
import { ref, onMounted } from 'vue'
import { RealtimeAnalyticsAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_metric_type: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ metric_type: '', kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      RealtimeAnalyticsAPI.list(filters.value),
      RealtimeAnalyticsAPI.stats()
    ])
    list.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: list.value.length,
      by_metric_type: {}
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    metric_type: 'gmv', value: 0, dimension: '', source: '', timestamp: ''
  }
  dialog.value = true
}
async function save() {
  try {
    await RealtimeAnalyticsAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const metricTypeMap = { gmv: 'GMV', viewers: '观看人数', orders: '订单量', conversion: '转化率', engagement: '互动率' }
const metricTypeColor = { gmv: 'warning', viewers: 'success', orders: '', conversion: 'danger', engagement: 'info' }

const fmtMoney = (v) => {
  const n = Number(v) || 0
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toFixed(0)
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="实时数据" subtitle="实时监控 · 指标追踪 · 即时分析" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">数据点总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">指标类型分布</div>
        <div style="font-size:16px;font-weight:700;color:#00ff9d">
          <span v-for="(v, k) in stats.by_metric_type" :key="k" style="margin-right:12px">{{ metricTypeMap[k] || k }}: {{ v }}</span>
          <span v-if="!stats.by_metric_type || !Object.keys(stats.by_metric_type).length">-</span>
        </div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">最新数据</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ list.length ? fmtMoney(list[0].value) : '-' }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索来源/维度" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.metric_type" placeholder="指标类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in metricTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新增数据</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="指标类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="metricTypeColor[row.metric_type]" size="small">{{ metricTypeMap[row.metric_type] || row.metric_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="数值" width="120" align="right">
          <template #default="{ row }"><span style="color:#00e5ff;font-weight:700;font-size:15px">{{ fmtMoney(row.value) }}</span></template>
        </el-table-column>
        <el-table-column prop="dimension" label="维度" width="120" show-overflow-tooltip />
        <el-table-column prop="source" label="来源" width="120" show-overflow-tooltip />
        <el-table-column prop="timestamp" label="时间戳" min-width="160" />
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="实时数据" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="指标类型">
          <el-select v-model="form.metric_type" style="width:100%">
            <el-option v-for="(v, k) in metricTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="数值"><el-input-number v-model="form.value" :min="0" :step="100" style="width:100%" /></el-form-item>
        <el-form-item label="维度"><el-input v-model="form.dimension" /></el-form-item>
        <el-form-item label="来源"><el-input v-model="form.source" /></el-form-item>
        <el-form-item label="时间戳"><el-date-picker v-model="form.timestamp" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
