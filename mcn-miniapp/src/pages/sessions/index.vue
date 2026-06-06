<template>
  <view class="page">
    <!-- Filter Tabs -->
    <view class="filter-tabs">
      <view
        v-for="tab in tabs"
        :key="tab.value"
        :class="['tab-item', { active: activeTab === tab.value }]"
        @tap="activeTab = tab.value"
      >
        <text class="tab-text">{{ tab.label }}</text>
      </view>
    </view>

    <!-- Session List -->
    <scroll-view scroll-y class="session-list" @scrolltolower="onReachBottom">
      <view
        v-for="session in filteredSessions"
        :key="session.id"
        class="glass-card session-card"
        @tap="goDetail(session.id)"
      >
        <view class="card-header">
          <text class="store-name">{{ session.storeName }}</text>
          <text :class="['status-tag', getStatusClass(session.status)]">
            {{ getStatusText(session.status) }}
          </text>
        </view>
        <view class="card-date">
          <text class="date-text">{{ formatDate(session.date) }}</text>
          <text class="time-text">{{ session.duration }}</text>
        </view>
        <view class="card-stats">
          <view class="stat-item">
            <text class="stat-value neon-purple">{{ formatMoney(session.gmv) }}</text>
            <text class="stat-label">GMV</text>
          </view>
          <view class="stat-item">
            <text class="stat-value neon-cyan">{{ session.viewers }}</text>
            <text class="stat-label">观看人数</text>
          </view>
          <view class="stat-item">
            <text class="stat-value neon-green">{{ session.peakViewers }}</text>
            <text class="stat-label">峰值在线</text>
          </view>
        </view>
      </view>

      <view v-if="loading" class="loading-tip">
        <text class="tip-text">加载中...</text>
      </view>
      <view v-if="!loading && filteredSessions.length === 0" class="empty-tip">
        <text class="tip-text">暂无直播记录</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow, onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'
import { SessionAPI } from '@/api'
import { formatMoney, formatDate, getStatusClass, getStatusText } from '@/utils/format'

const tabs = [
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' }
]
const activeTab = ref('week')
const loading = ref(false)
const sessions = ref([])

const mockSessions = [
  { id: 1, storeName: '旗舰店A', date: '2026-06-05', duration: '2h30m', gmv: 125800, viewers: 3520, peakViewers: 1280, status: 'completed' },
  { id: 2, storeName: '品牌店B', date: '2026-06-04', duration: '1h45m', gmv: 89600, viewers: 2180, peakViewers: 960, status: 'completed' },
  { id: 3, storeName: '专卖店C', date: '2026-06-03', duration: '3h10m', gmv: 234500, viewers: 5640, peakViewers: 2100, status: 'completed' },
  { id: 4, storeName: '概念店D', date: '2026-06-02', duration: '2h00m', gmv: 67800, viewers: 1890, peakViewers: 720, status: 'completed' },
  { id: 5, storeName: '旗舰店A', date: '2026-06-01', duration: '2h15m', gmv: 156200, viewers: 4100, peakViewers: 1500, status: 'completed' },
  { id: 6, storeName: '品牌店B', date: '2026-05-30', duration: '1h50m', gmv: 98700, viewers: 2450, peakViewers: 1100, status: 'completed' },
  { id: 7, storeName: '专卖店C', date: '2026-05-28', duration: '2h40m', gmv: 189300, viewers: 4780, peakViewers: 1850, status: 'completed' },
  { id: 8, storeName: '旗舰店A', date: '2026-05-25', duration: '3h00m', gmv: 312000, viewers: 7200, peakViewers: 3200, status: 'completed' }
]

const filteredSessions = computed(() => {
  return sessions.value
})

async function loadData() {
  loading.value = true
  try {
    const res = await SessionAPI.list({ period: activeTab.value })
    sessions.value = res.data?.results || res.data || mockSessions
  } catch {
    sessions.value = mockSessions
  } finally {
    loading.value = false
  }
}

function goDetail(id) {
  uni.navigateTo({ url: `/pages/sessions/detail?id=${id}` })
}

onShow(() => {
  loadData()
})

onPullDownRefresh(async () => {
  await loadData()
  uni.stopPullDownRefresh()
})

onReachBottom(() => {
  // pagination could be added here
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
  padding-bottom: env(safe-area-inset-bottom);
}

.filter-tabs {
  display: flex;
  padding: 24rpx 32rpx;
  gap: 20rpx;
}

.tab-item {
  padding: 16rpx 40rpx;
  border-radius: $radius-sm;
  background: $bg-secondary;
  border: 2rpx solid transparent;

  &.active {
    background: rgba($neon-purple, 0.15);
    border-color: $neon-purple;
  }
}

.tab-text {
  font-size: 28rpx;
  color: $text-secondary;

  .active & {
    color: $neon-purple;
    font-weight: 600;
  }
}

.session-list {
  padding: 0 32rpx;
  height: calc(100vh - 120rpx);
}

.session-card {
  margin-bottom: 24rpx;
  padding: 28rpx;
  background: $bg-card;
  border: 2rpx solid $border-glow;
  border-radius: $radius-md;
  backdrop-filter: blur(20rpx);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.store-name {
  font-size: 32rpx;
  font-weight: 600;
  color: $text-primary;
}

.status-tag {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;

  &.status-active,
  &.status-completed {
    background: rgba($neon-green, 0.15);
    color: $neon-green;
  }
}

.card-date {
  display: flex;
  gap: 24rpx;
  margin-bottom: 20rpx;
}

.date-text {
  font-size: 26rpx;
  color: $text-muted;
}

.time-text {
  font-size: 26rpx;
  color: $text-muted;
}

.card-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 20rpx;
  border-top: 2rpx solid rgba(255, 255, 255, 0.05);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
}

.stat-value {
  font-size: 30rpx;
  font-weight: 700;

  &.neon-purple { color: $neon-purple; }
  &.neon-cyan { color: $neon-cyan; }
  &.neon-green { color: $neon-green; }
}

.stat-label {
  font-size: 22rpx;
  color: $text-muted;
}

.loading-tip, .empty-tip {
  padding: 60rpx 0;
  text-align: center;
}

.tip-text {
  font-size: 28rpx;
  color: $text-muted;
}
</style>
