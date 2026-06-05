<script setup>
import { ref, onMounted } from 'vue'
import { AdCampaignAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const campaigns = ref([])
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '', platform: '' })

const stats = ref({ total: 0, running: 0, total_budget: 0, total_cost: 0, total_revenue: 0 })

async function loadStats() {
  try {
    const s = await AdCampaignAPI.stats()
    stats.value = { total: s.total || 0, running: s.running || 0, total_budget: s.total_budget || 0, total_cost: s.total_cost || 0, total_revenue: s.total_revenue || 0 }
  } catch {
    stats.value = {
      total: campaigns.value.length,
      running: campaigns.value.filter(i => i.status === 'running').length,
      total_budget: campaigns.value.reduce((a, b) => a + (Number(b.budget) || 0), 0),
      total_cost: campaigns.value.reduce((a, b) => a + (Number(b.actual_cost) || 0), 0),
      total_revenue: campaigns.value.reduce((a, b) => a + (Number(b.revenue) || 0), 0),
    }
  }
}

async function load() {
  loading.value = true
  try {
    campaigns.value = await AdCampaignAPI.list(filters.value)
    loadStats()
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', platform: 'douyin', ad_type: 'live', store: null, session: null, budget: 0, start_time: '', end_time: '', operator: null, status: 'draft' }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await AdCampaignAPI.update(form.value.id, form.value)
    else await AdCampaignAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此投放记录？', '提示', { type: 'warning' })
  await AdCampaignAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const roiColor = (roi) => {
  if (roi >= 3) return '#00ff9d'
  if (roi >= 2) return '#00e5ff'
  if (roi >= 1) return '#ffd23f'
  return '#ff4d9e'
}

const platformTagType = (platform) => {
  const map = { douyin: 'primary', kuaishou: 'warning', taobao: 'danger', xiaohongshu: 'danger', wechat: 'success' }
  return map[platform] || 'info'
}

const fmtMoney = (v) => {
  const n = Number(v) || 0
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toFixed(0)
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="流量投放" subtitle="投流管理 · ROI追踪 · 预算管控" />

    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">投放总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">投放中</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.running }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总预算</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ fmtMoney(stats.total_budget) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总花费</div>
        <div style="font-size:28px;font-weight:800;color:#ff9f43">{{ fmtMoney(stats.total_cost) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总收入</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ fmtMoney(stats.total_revenue) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-select v-model="filters.platform" placeholder="平台筛选" clearable @change="load" style="width:140px">
        <el-option label="抖音" value="douyin" />
        <el-option label="快手" value="kuaishou" />
        <el-option label="淘宝" value="taobao" />
        <el-option label="小红书" value="xiaohongshu" />
        <el-option label="微信" value="wechat" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="load" style="width:140px">
        <el-option label="草稿" value="draft" />
        <el-option label="投放中" value="running" />
        <el-option label="已暂停" value="paused" />
        <el-option label="已结束" value="completed" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新增投放</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="campaigns" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="投放名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="平台" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="platformTagType(row.platform)" size="small" effect="dark">{{ row.platform_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ad_type" label="推广类型" width="100" />
        <el-table-column prop="store_name" label="店铺" width="120" show-overflow-tooltip />
        <el-table-column label="预算" width="100" align="right">
          <template #default="{ row }"><span style="color:#7c5cff">{{ fmtMoney(row.budget) }}</span></template>
        </el-table-column>
        <el-table-column label="实际花费" width="100" align="right">
          <template #default="{ row }"><span style="color:#ff9f43">{{ fmtMoney(row.actual_cost) }}</span></template>
        </el-table-column>
        <el-table-column prop="impressions" label="曝光量" width="100" align="right" />
        <el-table-column prop="clicks" label="点击量" width="90" align="right" />
        <el-table-column prop="conversions" label="转化数" width="90" align="right" />
        <el-table-column label="带来GMV" width="110" align="right">
          <template #default="{ row }"><span style="color:#00ff9d">{{ fmtMoney(row.revenue) }}</span></template>
        </el-table-column>
        <el-table-column label="ROI" width="80" align="center">
          <template #default="{ row }">
            <span :style="{ color: roiColor(row.roi), fontWeight: 800 }">{{ row.roi }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'running' ? 'success' : row.status === 'paused' ? 'warning' : row.status === 'completed' ? 'info' : 'info'" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator_name" label="负责人" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="投放记录" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="投放名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="平台">
          <el-select v-model="form.platform" style="width:100%">
            <el-option label="抖音" value="douyin" />
            <el-option label="快手" value="kuaishou" />
            <el-option label="淘宝" value="taobao" />
            <el-option label="小红书" value="xiaohongshu" />
            <el-option label="微信" value="wechat" />
          </el-select>
        </el-form-item>
        <el-form-item label="推广类型">
          <el-select v-model="form.ad_type" style="width:100%">
            <el-option label="直播间推广" value="live" />
            <el-option label="短视频推广" value="video" />
            <el-option label="商品推广" value="product" />
          </el-select>
        </el-form-item>
        <el-form-item label="店铺ID"><el-input-number v-model="form.store" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="直播场次ID"><el-input-number v-model="form.session" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="预算"><el-input-number v-model="form.budget" :min="0" :step="1000" style="width:100%" /></el-form-item>
        <el-form-item label="开始时间"><el-date-picker v-model="form.start_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%" /></el-form-item>
        <el-form-item label="结束时间"><el-date-picker v-model="form.end_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%" /></el-form-item>
        <el-form-item label="负责人ID"><el-input-number v-model="form.operator" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="草稿" value="draft" />
            <el-option label="投放中" value="running" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已结束" value="completed" />
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
