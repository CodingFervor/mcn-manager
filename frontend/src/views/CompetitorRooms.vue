<script setup>
import { ref, onMounted } from 'vue'
import { CompetitorRoomAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const rooms = ref([])
const stats = ref({ total: 0, avg_viewers: 0, avg_gmv: 0, by_platform: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ platform: '', kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      CompetitorRoomAPI.list(filters.value),
      CompetitorRoomAPI.stats()
    ])
    rooms.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: rooms.value.length,
      avg_viewers: rooms.value.length ? Math.round(rooms.value.reduce((s, r) => s + (Number(r.avg_viewers) || 0), 0) / rooms.value.length) : 0,
      avg_gmv: rooms.value.length ? Math.round(rooms.value.reduce((s, r) => s + (Number(r.avg_gmv) || 0), 0) / rooms.value.length) : 0,
      by_platform: {}
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { platform: 'douyin', room_id: '', anchor_name: '', follower_count: 0, avg_viewers: 0, avg_gmv: 0, peak_viewers: 0, live_frequency: '', top_product: '', strategy: '' }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await CompetitorRoomAPI.update(form.value.id, form.value)
    else await CompetitorRoomAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此竞品直播间？', '提示', { type: 'warning' })
  await CompetitorRoomAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const platformMap = { douyin: '抖音', kuaishou: '快手', taobao: '淘宝', xiaohongshu: '小红书' }
const platformTagType = { douyin: 'primary', kuaishou: 'warning', taobao: 'danger', xiaohongshu: 'danger' }

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
    <PageHeader title="竞品直播间" subtitle="竞品采集 · 数据对比 · 排行榜" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">竞品总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">场均观看</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ fmtNum(stats.avg_viewers) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">场均GMV</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ fmtMoney(stats.avg_gmv) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平台分布</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ Object.keys(stats.by_platform || {}).length }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索主播/直播间ID" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.platform" placeholder="平台筛选" clearable @change="load" style="width:140px">
        <el-option v-for="(v, k) in platformMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 添加竞品</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="rooms" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="anchor_name" label="主播名称" min-width="120" show-overflow-tooltip />
        <el-table-column label="平台" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="platformTagType[row.platform]" size="small" effect="dark">{{ platformMap[row.platform] || row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="room_id" label="直播间ID" width="130" show-overflow-tooltip />
        <el-table-column label="粉丝数" width="100" align="right">
          <template #default="{ row }">{{ fmtNum(row.follower_count) }}</template>
        </el-table-column>
        <el-table-column label="场均观看" width="100" align="right">
          <template #default="{ row }"><span style="color:#ffd23f;font-weight:600">{{ fmtNum(row.avg_viewers) }}</span></template>
        </el-table-column>
        <el-table-column label="场均GMV" width="110" align="right">
          <template #default="{ row }"><span style="color:#00ff9d;font-weight:600">{{ fmtMoney(row.avg_gmv) }}</span></template>
        </el-table-column>
        <el-table-column label="峰值观看" width="100" align="right">
          <template #default="{ row }"><span style="color:#00e5ff">{{ fmtNum(row.peak_viewers) }}</span></template>
        </el-table-column>
        <el-table-column prop="live_frequency" label="开播频率" width="100" />
        <el-table-column prop="top_product" label="爆款商品" width="120" show-overflow-tooltip />
        <el-table-column prop="strategy" label="运营策略" min-width="150" show-overflow-tooltip />
        <el-table-column prop="last_tracked" label="最近追踪" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="竞品直播间" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="平台">
          <el-select v-model="form.platform" style="width:100%">
            <el-option v-for="(v, k) in platformMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="直播间ID"><el-input v-model="form.room_id" /></el-form-item>
        <el-form-item label="主播名称"><el-input v-model="form.anchor_name" /></el-form-item>
        <el-form-item label="粉丝数"><el-input-number v-model="form.follower_count" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="场均观看"><el-input-number v-model="form.avg_viewers" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="场均GMV"><el-input-number v-model="form.avg_gmv" :min="0" :step="100" style="width:100%" /></el-form-item>
        <el-form-item label="峰值观看"><el-input-number v-model="form.peak_viewers" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="开播频率"><el-input v-model="form.live_frequency" placeholder="如: 每日/每周3次" /></el-form-item>
        <el-form-item label="爆款商品"><el-input v-model="form.top_product" /></el-form-item>
        <el-form-item label="运营策略"><el-input v-model="form.strategy" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
