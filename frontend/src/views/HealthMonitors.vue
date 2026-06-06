<script setup>
import { ref, onMounted } from 'vue'
import { HealthMonitorAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, healthy: 0, degraded: 0, down: 0 })
const loading = ref(false)
const filters = ref({ kw: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([HealthMonitorAPI.list(filters.value), HealthMonitorAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, healthy: list.value.filter(i => i.status === 'healthy').length, degraded: list.value.filter(i => i.status === 'degraded').length, down: list.value.filter(i => i.status === 'down').length }
  } finally { loading.value = false }
}

const checkHealth = async (row) => {
  try {
    await HealthMonitorAPI.check(row.id)
    ElMessage.success('健康检查完成')
    load()
  } catch { ElMessage.error('检查失败') }
}

const statusMap = { healthy: '健康', degraded: '降级', down: '宕机', unknown: '未知' }
const statusColor = { healthy: 'success', degraded: 'warning', down: 'danger', unknown: 'info' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="系统健康监控" subtitle="服务监控 · 健康检查 · 异常告警" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">服务数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">健康</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.healthy }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">降级</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.degraded }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">宕机</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ stats.down }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索服务名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="warning" @click="list.forEach(i => checkHealth(i))">全部检查</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="service_name" label="服务名" min-width="140" show-overflow-tooltip />
        <el-table-column prop="endpoint" label="端点" width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small" effect="dark">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="响应时间" width="100" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.response_time > 500 ? '#ff4d9e' : row.response_time > 200 ? '#ffd23f' : '#00ff9d', fontWeight: 600 }">{{ row.response_time }}ms</span>
          </template>
        </el-table-column>
        <el-table-column prop="last_check" label="最后检查" width="170" />
        <el-table-column prop="error_message" label="错误信息" min-width="160" show-overflow-tooltip />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="checkHealth(row)">检查</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>
