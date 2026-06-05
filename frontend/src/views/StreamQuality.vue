<script setup>
import { ref, onMounted } from 'vue'
import { StreamQualityAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, avg_score: 0, avg_fps: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([StreamQualityAPI.list(filters.value), StreamQualityAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, avg_score: 0, avg_fps: 0 }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { resolution: '', bitrate: 0, fps: 0, dropped_frames: 0, audio_level: 0, latency: 0, score: 0 }
  dialog.value = true
}

async function save() {
  try {
    await StreamQualityAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false; load()
  } catch { ElMessage.error('保存失败') }
}

const scoreColor = (s) => s >= 90 ? 'success' : s >= 70 ? 'warning' : 'danger'

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播画质监控" subtitle="画质分析 · 帧率监控 · 质量评分" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-label">记录总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">平均评分</div>
        <div class="stat-value">{{ Number(stats.avg_score || 0).toFixed(1) }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">平均帧率</div>
        <div class="stat-value">{{ Number(stats.avg_fps || 0).toFixed(1) }} fps</div>
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
        <el-table-column prop="resolution" label="分辨率" width="110" />
        <el-table-column label="码率(kbps)" width="110">
          <template #default="{ row }">{{ row.bitrate }}</template>
        </el-table-column>
        <el-table-column label="帧率(fps)" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan)">{{ row.fps }}</span>
          </template>
        </el-table-column>
        <el-table-column label="丢帧数" width="90">
          <template #default="{ row }">{{ row.dropped_frames }}</template>
        </el-table-column>
        <el-table-column label="音量(dB)" width="100">
          <template #default="{ row }">{{ row.audio_level }}</template>
        </el-table-column>
        <el-table-column label="延迟(ms)" width="100">
          <template #default="{ row }">{{ row.latency }}</template>
        </el-table-column>
        <el-table-column label="评分" width="80">
          <template #default="{ row }">
            <el-tag :type="scoreColor(row.score)" size="small" effect="dark">{{ row.score }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="记录时间" width="170" />
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="画质记录" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="分辨率"><el-input v-model="form.resolution" placeholder="如：1920x1080" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="码率(kbps)"><el-input-number v-model="form.bitrate" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="帧率(fps)"><el-input-number v-model="form.fps" :min="0" :precision="1" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="丢帧数"><el-input-number v-model="form.dropped_frames" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="音量(dB)"><el-input-number v-model="form.audio_level" :precision="1" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="延迟(ms)"><el-input-number v-model="form.latency" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="评分"><el-input-number v-model="form.score" :min="0" :max="100" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
