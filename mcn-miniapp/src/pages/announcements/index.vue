<template>
  <view class="page">
    <view class="header">
      <text class="title">系统公告</text>
    </view>
    <view class="filter-bar">
      <view
        class="filter-item"
        v-for="(f, i) in filters"
        :key="i"
        :class="{ active: activeFilter === f.value }"
        @tap="activeFilter = f.value"
      >
        <text class="filter-text">{{ f.label }}</text>
      </view>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view
        class="card"
        v-for="(item, idx) in filteredList"
        :key="idx"
        @tap="toggleExpand(idx)"
      >
        <view class="card-top">
          <view class="tag" :class="'tag-' + item.type">
            <text class="tag-text">{{ item.typeLabel }}</text>
          </view>
          <view class="status-wrap">
            <text class="status-text" :class="'status-' + item.status">{{ item.statusLabel }}</text>
          </view>
        </view>
        <text class="card-title">{{ item.title }}</text>
        <text class="card-date">{{ item.date }}</text>
        <view v-if="expandedIdx === idx" class="card-content">
          <text class="content-text">{{ item.content }}</text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'

const activeFilter = ref('all')
const expandedIdx = ref(-1)

const filters = [
  { label: '全部', value: 'all' },
  { label: '通知', value: 'info' },
  { label: '警告', value: 'warning' },
  { label: '紧急', value: 'urgent' },
]

const announcements = ref([
  { title: '系统维护通知', type: 'info', typeLabel: '通知', date: '2026-06-06', status: 'published', statusLabel: '已发布', content: '系统将于2026年6月8日凌晨2:00-4:00进行例行维护，届时部分功能可能暂时不可用，请提前做好准备。' },
  { title: '安全漏洞警告', type: 'warning', typeLabel: '警告', date: '2026-06-05', status: 'published', statusLabel: '已发布', content: '检测到部分模块存在XSS风险，请所有用户尽快更新密码，并检查近期操作记录。' },
  { title: '紧急：数据库故障', type: 'urgent', typeLabel: '紧急', date: '2026-06-04', status: 'resolved', statusLabel: '已解决', content: '主数据库于14:32发生连接异常，已启动备用节点恢复服务，目前正在排查根因。' },
  { title: '版本更新 v3.2.0', type: 'info', typeLabel: '通知', date: '2026-06-03', status: 'published', statusLabel: '已发布', content: '新增多租户管理、白标配置等功能模块，优化了报表生成性能，修复了若干已知问题。' },
  { title: 'SSL证书即将过期', type: 'warning', typeLabel: '警告', date: '2026-06-02', status: 'published', statusLabel: '已发布', content: '主域名SSL证书将于2026年6月15日过期，请及时续签以避免服务中断。' },
  { title: '紧急：异常登录告警', type: 'urgent', typeLabel: '紧急', date: '2026-06-01', status: 'published', statusLabel: '已发布', content: '检测到多个异常登录尝试，已自动封锁相关IP段，请确认账户安全。' },
])

const filteredList = computed(() => {
  if (activeFilter.value === 'all') return announcements.value
  return announcements.value.filter(a => a.type === activeFilter.value)
})

function toggleExpand(idx) {
  expandedIdx.value = expandedIdx.value === idx ? -1 : idx
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 24rpx 32rpx 16rpx;
}

.title {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
}

.filter-bar {
  display: flex;
  padding: 0 24rpx 16rpx;
  gap: 16rpx;
}

.filter-item {
  padding: 10rpx 28rpx;
  border-radius: 32rpx;
  background: rgba(124, 92, 255, 0.08);
  border: 1rpx solid rgba(124, 92, 255, 0.15);

  &.active {
    background: rgba(124, 92, 255, 0.2);
    border-color: $neon-purple;
  }
}

.filter-text {
  font-size: 24rpx;
  color: $text-secondary;

  .active & {
    color: $neon-purple;
    font-weight: 600;
  }
}

.scroll-body {
  flex: 1;
  height: 0;
  padding: 0 24rpx;
}

.card {
  padding: 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 20rpx;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.tag {
  padding: 4rpx 16rpx;
  border-radius: 8rpx;

  &.tag-info { background: rgba(0, 229, 255, 0.15); }
  &.tag-warning { background: rgba(255, 210, 63, 0.15); }
  &.tag-urgent { background: rgba(255, 77, 158, 0.15); }
}

.tag-text {
  font-size: 22rpx;
  font-weight: 600;

  .tag-info & { color: $neon-cyan; }
  .tag-warning & { color: $neon-yellow; }
  .tag-urgent & { color: $neon-pink; }
}

.status-text {
  font-size: 22rpx;
  color: $text-muted;

  &.status-published { color: $neon-green; }
  &.status-resolved { color: $neon-cyan; }
}

.card-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 8rpx;
}

.card-date {
  font-size: 24rpx;
  color: $text-muted;
}

.card-content {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid rgba(124, 92, 255, 0.1);
}

.content-text {
  font-size: 26rpx;
  color: $text-secondary;
  line-height: 1.7;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
