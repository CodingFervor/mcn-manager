<script setup>
import { ref, onMounted } from 'vue'
import { AuditLogAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ today: 0, this_week: 0, action_types: 0, abnormal: 0 })
const loading = ref(false)
const filters = ref({ user: '', action: '', resource_type: '', date_range: [] })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([AuditLogAPI.list(filters.value), AuditLogAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { today: list.value.length, this_week: list.value.length, action_types: new Set(list.value.map(i => i.action)).size, abnormal: list.value.filter(i => i.is_abnormal).length }
  } finally { loading.value = false }
}

const actionColor = { create: 'success', update: 'warning', delete: 'danger', login: '', export: 'info', import: 'info', approve: 'success' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="审计日志" subtitle="操作追踪 · 安全审计 · 异常监控" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">今日日志</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.today }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">本周</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.this_week }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">操作类型</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.action_types }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">异常操作</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ stats.abnormal }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.user" placeholder="搜索用户" style="width:150px" @keyup.enter="load" />
      <el-select v-model="filters.action" placeholder="操作类型" clearable @change="load" style="width:120px">
        <el-option label="创建" value="create" />
        <el-option label="更新" value="update" />
        <el-option label="删除" value="delete" />
        <el-option label="登录" value="login" />
        <el-option label="导出" value="export" />
        <el-option label="导入" value="import" />
        <el-option label="审批" value="approve" />
      </el-select>
      <el-select v-model="filters.resource_type" placeholder="资源类型" clearable @change="load" style="width:130px">
        <el-option label="用户" value="user" />
        <el-option label="订单" value="order" />
        <el-option label="商品" value="product" />
        <el-option label="直播" value="live" />
        <el-option label="系统" value="system" />
      </el-select>
      <el-date-picker v-model="filters.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:260px" @change="load" />
      <el-button type="primary" @click="load">搜索</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="user_name" label="用户" width="100" />
        <el-table-column label="操作" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="actionColor[row.action] || 'info'" size="small">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_type" label="资源类型" width="100" />
        <el-table-column prop="resource_id" label="资源ID" width="90" />
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column prop="created_at" label="时间" width="170" />
      </el-table>
    </div>
  </div>
</template>
