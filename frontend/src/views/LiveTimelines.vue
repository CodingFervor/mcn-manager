<script setup>
import { ref, onMounted } from 'vue'
import { LiveTimelineAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_event_type: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

const eventTypeMap = { start: '开播', product: '上架商品', coupon: '发券', game: '互动游戏', peak: '流量高峰', end: '下播', other: '其他' }
const eventColor = { start: 'success', product: 'warning', coupon: 'danger', game: 'primary', peak: '', end: 'info', other: 'info' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([LiveTimelineAPI.list(filters.value), LiveTimelineAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, by_event_type: {} }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { event_type: 'start', title: '', offset_seconds: 0, gmv_at_point: 0, viewers_at_point: 0 }
  dialog.value = true
}

async function save() {
  try {
    await LiveTimelineAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false; load()
  } catch { ElMessage.error('保存失败') }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播时间轴" subtitle="事件标注 · 关键节点 · 数据回溯" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-label">事件总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">商品事件</div>
        <div class="stat-value">{{ stats.by_event_type?.product || 0 }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">高峰事件</div>
        <div class="stat-value">{{ stats.by_event_type?.peak || 0 }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索" style="width:200px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="事件类型" width="110">
          <template #default="{ row }">
            <el-tag :type="eventColor[row.event_type]" size="small">{{ eventTypeMap[row.event_type] || row.event_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="事件标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="偏移(秒)" width="100">
          <template #default="{ row }">{{ row.offset_seconds }}s</template>
        </el-table-column>
        <el-table-column label="此时GMV" width="120">
          <template #default="{ row }">
            <span style="color:var(--neon-pink);font-weight:700">¥{{ Number(row.gmv_at_point || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="在线人数" width="110">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan)">{{ Number(row.viewers_at_point || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="时间轴事件" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="事件类型">
          <el-select v-model="form.event_type" style="width:100%">
            <el-option v-for="(v, k) in eventTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="事件标题"><el-input v-model="form.title" placeholder="请输入事件标题" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="偏移(秒)"><el-input-number v-model="form.offset_seconds" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="此时GMV"><el-input-number v-model="form.gmv_at_point" :min="0" :step="100" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="在线人数"><el-input-number v-model="form.viewers_at_point" :min="0" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
