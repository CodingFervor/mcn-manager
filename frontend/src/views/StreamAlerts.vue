<script setup>
import { ref, onMounted } from 'vue'
import { StreamAlertAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, pending: 0, critical: 0, today_resolved: 0 })
const loading = ref(false)
const dialog = ref(false)
const resolveDialog = ref(false)
const form = ref({})
const resolveForm = ref({})
const filters = ref({ kw: '', status: '', severity: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      StreamAlertAPI.list(filters.value),
      StreamAlertAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { store_id: '', alert_type: '', severity: '', message: '', threshold: '' }
  dialog.value = true
}

async function save() {
  await StreamAlertAPI.create(form.value)
  dialog.value = false
  load()
}

const openResolve = (row) => {
  resolveForm.value = { id: row.id, resolution: '' }
  resolveDialog.value = true
}

async function submitResolve() {
  await StreamAlertAPI.resolve(resolveForm.value.id, { resolution: resolveForm.value.resolution })
  resolveDialog.value = false
  load()
}

const alertTypeMap = { offline: '掉线', bitrate_low: '码率低', no_audio: '无音频', no_video: '无画面', delay_high: '高延迟', gmv_drop: 'GMV骤降', other: '其他' }
const severityMap = { low: '低', medium: '中', high: '高', critical: '严重' }
const severityColor = { low: 'info', medium: 'warning', high: 'danger', critical: 'danger' }
const statusMap = { pending: '待处理', processing: '处理中', resolved: '已解决', ignored: '已忽略' }
const statusColor = { pending: 'danger', processing: 'warning', resolved: 'success', ignored: 'info' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播监控" subtitle="实时监控 · 告警管理 · 异常处理" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">告警总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g4">
        <div class="stat-label">待处理</div>
        <div class="stat-value">{{ stats.pending }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">严重告警</div>
        <div class="stat-value">{{ stats.critical }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">今日已处理</div>
        <div class="stat-value">{{ stats.today_resolved }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索店铺/告警信息" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.severity" placeholder="严重等级" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in severityMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新增告警</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="store_name" label="店铺" width="120" />
        <el-table-column label="告警类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ alertTypeMap[row.alert_type] || row.alert_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="严重等级" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="severityColor[row.severity]" effect="dark">{{ severityMap[row.severity] || row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="告警信息" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resolved_by_name" label="处理人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending' || row.status === 'processing'" size="small" type="warning" @click="openResolve(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新增告警" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="店铺ID"><el-input-number v-model="form.store_id" :min="1" /></el-form-item>
        <el-form-item label="告警类型">
          <el-select v-model="form.alert_type" style="width: 100%">
            <el-option v-for="(v, k) in alertTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="严重等级">
          <el-select v-model="form.severity" style="width: 100%">
            <el-option v-for="(v, k) in severityMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="告警信息"><el-input v-model="form.message" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="阈值"><el-input-number v-model="form.threshold" :min="0" :precision="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resolveDialog" title="处理告警" width="500px">
      <el-form :model="resolveForm" label-width="80px">
        <el-form-item label="处理说明"><el-input v-model="resolveForm.resolution" type="textarea" :rows="4" placeholder="请填写处理说明" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialog = false">取消</el-button>
        <el-button type="primary" @click="submitResolve">确认处理</el-button>
      </template>
    </el-dialog>
  </div>
</template>
