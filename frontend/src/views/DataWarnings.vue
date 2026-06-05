<script setup>
import { ref, onMounted } from 'vue'
import { DataWarningAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const warnings = ref([])
const stats = ref({ total: 0, active: 0, by_severity: {}, total_triggers: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ severity: '', is_active: '', metric: '', kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      DataWarningAPI.list(filters.value),
      DataWarningAPI.stats()
    ])
    warnings.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: warnings.value.length,
      active: warnings.value.filter(w => w.is_active).length,
      by_severity: {},
      total_triggers: warnings.value.reduce((s, r) => s + (Number(r.trigger_count) || 0), 0),
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', metric: 'gmv', condition: 'lt', threshold: 0,
    time_window: 'daily', severity: 'warning', notify_method: 'system',
    notify_users: '', is_active: true
  }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row, notify_users: typeof row.notify_users === 'object' ? row.notify_users.join(',') : (row.notify_users || '') }
  dialog.value = true
}
async function save() {
  try {
    const payload = { ...form.value }
    if (typeof payload.notify_users === 'string') {
      payload.notify_users = payload.notify_users.split(',').map(s => s.trim()).filter(Boolean)
    }
    if (form.value.id) await DataWarningAPI.update(form.value.id, payload)
    else await DataWarningAPI.create(payload)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此预警规则？', '提示', { type: 'warning' })
  await DataWarningAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}
const toggleActive = async (row) => {
  await DataWarningAPI.toggle(row.id)
  ElMessage.success(row.is_active ? '已禁用' : '已启用')
  load()
}

const metricMap = { gmv: 'GMV', viewers: '观看人数', conversion_rate: '转化率', refund_rate: '退款率', complaint_rate: '投诉率', follower_change: '粉丝变化' }
const conditionMap = { gt: '大于', lt: '小于', eq: '等于', drop: '下降', rise: '上升' }
const timeWindowMap = { realtime: '实时', hourly: '每小时', daily: '每日', weekly: '每周' }
const severityMap = { info: '提示', warning: '警告', critical: '严重' }
const severityColor = { info: 'info', warning: 'warning', critical: 'danger' }
const notifyMethodMap = { sms: '短信', wechat: '微信', email: '邮件', system: '系统通知' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="数据预警" subtitle="指标监控 · 预警规则 · 异常通知" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">规则总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">启用中</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">严重等级分布</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ Object.keys(stats.by_severity || {}).length }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">累计触发</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.total_triggers }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索规则名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.metric" placeholder="监控指标" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in metricMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.severity" placeholder="严重等级" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in severityMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.is_active" placeholder="启用状态" clearable @change="load" style="width:120px">
        <el-option label="启用" value="true" />
        <el-option label="禁用" value="false" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建规则</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="warnings" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="规则名称" min-width="140" show-overflow-tooltip />
        <el-table-column label="监控指标" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ metricMap[row.metric] || row.metric }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="条件" width="80" align="center">
          <template #default="{ row }">{{ conditionMap[row.condition] || row.condition }}</template>
        </el-table-column>
        <el-table-column prop="threshold" label="阈值" width="90" align="right">
          <template #default="{ row }"><span style="font-weight:600">{{ row.threshold }}</span></template>
        </el-table-column>
        <el-table-column label="时间窗口" width="90" align="center">
          <template #default="{ row }">{{ timeWindowMap[row.time_window] || row.time_window }}</template>
        </el-table-column>
        <el-table-column label="严重等级" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="severityColor[row.severity]" size="small" effect="dark">{{ severityMap[row.severity] || row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="通知方式" width="100" align="center">
          <template #default="{ row }">{{ notifyMethodMap[row.notify_method] || row.notify_method }}</template>
        </el-table-column>
        <el-table-column prop="trigger_count" label="触发次数" width="90" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.trigger_count > 0 ? '#ff4d9e' : '#a8b2d1', fontWeight: 600 }">{{ row.trigger_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="last_triggered" label="最近触发" width="170" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch :model-value="row.is_active" @change="toggleActive(row)" active-text="" inactive-text="" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="预警规则" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="规则名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="监控指标">
          <el-select v-model="form.metric" style="width:100%">
            <el-option v-for="(v, k) in metricMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="条件">
          <el-select v-model="form.condition" style="width:100%">
            <el-option v-for="(v, k) in conditionMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="阈值"><el-input-number v-model="form.threshold" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="时间窗口">
          <el-select v-model="form.time_window" style="width:100%">
            <el-option v-for="(v, k) in timeWindowMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="严重等级">
          <el-select v-model="form.severity" style="width:100%">
            <el-option v-for="(v, k) in severityMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="通知方式">
          <el-select v-model="form.notify_method" style="width:100%">
            <el-option v-for="(v, k) in notifyMethodMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="通知用户">
          <el-input v-model="form.notify_users" placeholder="用户ID，逗号分隔" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
