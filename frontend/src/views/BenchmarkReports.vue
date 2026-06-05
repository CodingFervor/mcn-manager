<script setup>
import { ref, onMounted } from 'vue'
import { BenchmarkReportAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, avg_score: 0, by_category: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      BenchmarkReportAPI.list(filters.value),
      BenchmarkReportAPI.stats()
    ])
    list.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: list.value.length,
      avg_score: list.value.length ? (list.value.reduce((s, i) => s + (i.score || 0), 0) / list.value.length).toFixed(0) : 0,
      by_category: {}
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', category: '', metrics: '', industry_avg: '', ranking: 0,
    total_compared: 0, period: '', score: 0
  }
  dialog.value = true
}
async function save() {
  try {
    const payload = { ...form.value }
    if (typeof payload.metrics === 'string') {
      try { payload.metrics = JSON.parse(payload.metrics) } catch { /* keep as string */ }
    }
    if (typeof payload.industry_avg === 'string') {
      try { payload.industry_avg = JSON.parse(payload.industry_avg) } catch { /* keep as string */ }
    }
    await BenchmarkReportAPI.create(payload)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const scoreColor = (v) => v >= 80 ? '#00ff9d' : v >= 60 ? '#ffd23f' : '#ff4d9e'

const formatJSON = (v) => {
  if (!v) return '-'
  if (typeof v === 'string') return v
  try { return JSON.stringify(v) } catch { return String(v) }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="行业对标" subtitle="竞品对标 · 行业排名 · 差距分析" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">报告总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均评分</div>
        <div style="font-size:28px;font-weight:800" :style="{ color: scoreColor(stats.avg_score) }">{{ stats.avg_score }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">分类统计</div>
        <div style="font-size:16px;font-weight:700;color:#00ff9d">
          <span v-for="(v, k) in stats.by_category" :key="k" style="margin-right:12px">{{ k }}: {{ v }}</span>
          <span v-if="!stats.by_category || !Object.keys(stats.by_category).length">-</span>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索报告名称" style="width:200px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建报告</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="报告名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column label="指标" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="color:#7c5cff">{{ formatJSON(row.metrics) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="行业均值" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="color:#a8b2d1">{{ formatJSON(row.industry_avg) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="排名" width="80" align="center">
          <template #default="{ row }"><span style="color:#00e5ff;font-weight:700">{{ row.ranking }}</span></template>
        </el-table-column>
        <el-table-column label="对标总数" width="90" align="right">
          <template #default="{ row }">{{ row.total_compared }}</template>
        </el-table-column>
        <el-table-column prop="period" label="统计周期" width="100" />
        <el-table-column label="评分" width="80" align="center">
          <template #default="{ row }">
            <span :style="{ color: scoreColor(row.score), fontWeight: 700 }">{{ row.score }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="行业对标" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="报告名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="form.category" placeholder="如: 直播电商、短视频" /></el-form-item>
        <el-form-item label="指标">
          <el-input v-model="form.metrics" type="textarea" :rows="3" placeholder='JSON格式，如: {"gmv":100,"转化率":2.5}' />
        </el-form-item>
        <el-form-item label="行业均值">
          <el-input v-model="form.industry_avg" type="textarea" :rows="3" placeholder='JSON格式，如: {"gmv":80,"转化率":1.8}' />
        </el-form-item>
        <el-form-item label="排名"><el-input-number v-model="form.ranking" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="对标总数"><el-input-number v-model="form.total_compared" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="统计周期"><el-input v-model="form.period" placeholder="如: 2026-Q1" /></el-form-item>
        <el-form-item label="评分"><el-input-number v-model="form.score" :min="0" :max="100" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
