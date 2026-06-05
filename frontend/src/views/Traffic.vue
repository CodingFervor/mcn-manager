<script setup>
import { ref, onMounted } from 'vue'
import { TrafficAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const trafficList = ref([])
const stats = ref({ total: 0, total_impressions: 0, total_clicks: 0, total_cost: 0, total_conversions: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ traffic_type: '', source: '', kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      TrafficAPI.list(filters.value),
      TrafficAPI.stats()
    ])
    trafficList.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: trafficList.value.length,
      total_impressions: trafficList.value.reduce((s, r) => s + (Number(r.impressions) || 0), 0),
      total_clicks: trafficList.value.reduce((s, r) => s + (Number(r.clicks) || 0), 0),
      total_cost: trafficList.value.reduce((s, r) => s + (Number(r.cost) || 0), 0),
      total_conversions: trafficList.value.reduce((s, r) => s + (Number(r.conversions) || 0), 0),
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { session: null, traffic_type: 'natural', source: 'homepage', impressions: 0, clicks: 0, cost: 0, conversions: 0, recorded_at: '' }
  dialog.value = true
}
async function save() {
  try {
    await TrafficAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const trafficTypeMap = { natural: '自然流量', paid: '付费流量', private: '私域流量', recommend: '推荐流量' }
const trafficTypeColor = { natural: 'success', paid: 'warning', private: 'primary', recommend: '' }
const sourceMap = { homepage: '首页', search: '搜索', live_tab: '直播tab', follow: '关注', dou_plus: 'DOU+', qianchuan: '千川', private: '私域', share: '分享' }

const fmtNum = (n) => {
  const v = Number(n) || 0
  return v >= 10000 ? (v / 10000).toFixed(1) + '万' : v.toLocaleString()
}
const fmtMoney = (v) => {
  const n = Number(v) || 0
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toFixed(0)
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="流量分析" subtitle="流量来源 · 投放效果 · 转化追踪" />

    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">记录总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总曝光量</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ fmtNum(stats.total_impressions) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总点击量</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ fmtNum(stats.total_clicks) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总花费</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ fmtMoney(stats.total_cost) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总转化数</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ fmtNum(stats.total_conversions) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索场次/来源" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.traffic_type" placeholder="流量类型" clearable @change="load" style="width:140px">
        <el-option v-for="(v, k) in trafficTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.source" placeholder="流量来源" clearable @change="load" style="width:140px">
        <el-option v-for="(v, k) in sourceMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新增记录</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="trafficList" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="session_display" label="直播场次" width="150" show-overflow-tooltip />
        <el-table-column label="流量类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="trafficTypeColor[row.traffic_type]" size="small">{{ trafficTypeMap[row.traffic_type] || row.traffic_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="流量来源" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ sourceMap[row.source] || row.source }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="曝光量" width="100" align="right">
          <template #default="{ row }"><span style="color:#ffd23f;font-weight:600">{{ fmtNum(row.impressions) }}</span></template>
        </el-table-column>
        <el-table-column label="点击量" width="100" align="right">
          <template #default="{ row }"><span style="color:#00e5ff;font-weight:600">{{ fmtNum(row.clicks) }}</span></template>
        </el-table-column>
        <el-table-column label="点击率" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.ctr >= 5 ? '#00ff9d' : row.ctr >= 2 ? '#ffd23f' : '#ff4d9e', fontWeight: 600 }">{{ row.ctr }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="花费" width="100" align="right">
          <template #default="{ row }"><span style="color:#7c5cff;font-weight:600">¥{{ fmtMoney(row.cost) }}</span></template>
        </el-table-column>
        <el-table-column label="转化数" width="90" align="right">
          <template #default="{ row }"><span style="color:#00ff9d;font-weight:600">{{ row.conversions }}</span></template>
        </el-table-column>
        <el-table-column label="转化率" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.cvr >= 10 ? '#00ff9d' : row.cvr >= 3 ? '#ffd23f' : '#ff4d9e', fontWeight: 600 }">{{ row.cvr }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="recorded_at" label="记录时间" width="170" />
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新增流量记录" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="直播场次ID"><el-input-number v-model="form.session" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="流量类型">
          <el-select v-model="form.traffic_type" style="width:100%">
            <el-option v-for="(v, k) in trafficTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="流量来源">
          <el-select v-model="form.source" style="width:100%">
            <el-option v-for="(v, k) in sourceMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="曝光量"><el-input-number v-model="form.impressions" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="点击量"><el-input-number v-model="form.clicks" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="花费"><el-input-number v-model="form.cost" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="转化数"><el-input-number v-model="form.conversions" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="记录时间"><el-date-picker v-model="form.recorded_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
