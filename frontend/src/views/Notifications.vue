<script setup>
import { ref, onMounted } from 'vue'
import { NotificationAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'

const notifications = ref([])
const loading = ref(false)
const unreadCount = ref(0)

async function load() {
  loading.value = true
  try {
    notifications.value = await NotificationAPI.list()
    const res = await NotificationAPI.unreadCount()
    unreadCount.value = res.count
  } finally { loading.value = false }
}
const readAll = async () => { await NotificationAPI.readAll(); load() }
const typeIcon = { system: '🔔', schedule: '📅', attendance: '⏰', performance: '🏆', leave: '📝', alert: '⚠️', contract: '📋', task: '📌' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="消息中心" subtitle="系统通知 · 排班提醒 · 预警告警" />
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:20px">
      <StatCard label="未读消息" :value="unreadCount" icon="📬" gradient="g1" />
      <StatCard label="总消息" :value="notifications.length" icon="📨" gradient="g2" />
    </div>
    <div class="toolbar">
      <el-button type="primary" @click="readAll">全部已读</el-button>
    </div>
    <div class="glass" style="padding:20px">
      <div v-if="notifications.length === 0" style="text-align:center;padding:60px;color:var(--text-muted)">
        <div style="font-size:48px;margin-bottom:12px">📭</div>
        <div>暂无消息</div>
      </div>
      <div v-for="(n, i) in notifications" :key="i" :style="{ padding: '16px', marginBottom: '8px', background: n.is_read ? 'rgba(255,255,255,0.02)' : 'rgba(124,92,255,0.08)', borderRadius: '12px', borderLeft: n.is_read ? 'none' : '3px solid var(--neon-purple)' }">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px">
          <span style="font-size:20px">{{ typeIcon[n.type] || '📨' }}</span>
          <span style="font-weight:600;flex:1">{{ n.title }}</span>
          <el-tag v-if="!n.is_read" type="primary" size="small">新</el-tag>
          <span style="font-size:11px;color:var(--text-muted)">{{ n.created_at?.slice(5, 16) }}</span>
        </div>
        <div style="color:var(--text-secondary);font-size:13px;padding-left:32px">{{ n.content }}</div>
      </div>
    </div>
  </div>
</template>
