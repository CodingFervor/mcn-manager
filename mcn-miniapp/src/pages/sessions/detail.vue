<template>
  <view class="page">
    <!-- Header -->
    <view class="glass-card header-card">
      <view class="header-top">
        <text class="store-name">{{ session.storeName }}</text>
        <text :class="['status-tag', getStatusClass(session.status)]">
          {{ getStatusText(session.status) }}
        </text>
      </view>
      <text class="header-date">{{ formatDate(session.date) }} {{ session.startTime }} - {{ session.endTime }}</text>
    </view>

    <!-- Stats Grid -->
    <view class="stats-grid">
      <view class="glass-card stat-card">
        <text class="stat-value neon-purple">{{ formatMoney(session.gmv) }}</text>
        <text class="stat-label">GMV</text>
      </view>
      <view class="glass-card stat-card">
        <text class="stat-value neon-cyan">{{ session.viewers }}</text>
        <text class="stat-label">观看人数</text>
      </view>
      <view class="glass-card stat-card">
        <text class="stat-value neon-green">{{ session.peakViewers }}</text>
        <text class="stat-label">在线峰值</text>
      </view>
      <view class="glass-card stat-card">
        <text class="stat-value neon-yellow">{{ session.duration }}</text>
        <text class="stat-label">时长</text>
      </view>
    </view>

    <!-- Viewer Trend Chart Placeholder -->
    <view class="glass-card chart-card">
      <text class="section-title">观众趋势</text>
      <view class="chart-placeholder">
        <view
          v-for="(bar, idx) in viewerTrend"
          :key="idx"
          class="chart-bar-wrapper"
        >
          <view class="chart-bar" :style="{ height: bar.height + '%', background: bar.color }"></view>
          <text class="chart-bar-label">{{ bar.label }}</text>
        </view>
      </view>
    </view>

    <!-- Product Sales List -->
    <view class="glass-card product-section">
      <text class="section-title">商品销售明细</text>
      <view
        v-for="product in products"
        :key="product.id"
        class="product-row"
      >
        <view class="product-info">
          <text class="product-name">{{ product.name }}</text>
          <text class="product-qty">销量: {{ product.quantity }}件</text>
        </view>
        <text class="product-revenue">{{ formatMoney(product.revenue) }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { SessionAPI } from '@/api'
import { formatMoney, formatDate, getStatusClass, getStatusText } from '@/utils/format'

const sessionId = ref('')
const session = ref({
  storeName: '',
  date: '',
  startTime: '',
  endTime: '',
  gmv: 0,
  viewers: 0,
  peakViewers: 0,
  duration: '',
  status: 'completed'
})

const products = ref([])
const viewerTrend = ref([])

const mockSession = {
  id: 1,
  storeName: '旗舰店A',
  date: '2026-06-05',
  startTime: '19:00',
  endTime: '21:30',
  gmv: 125800,
  viewers: 3520,
  peakViewers: 1280,
  duration: '2h30m',
  status: 'completed'
}

const mockProducts = [
  { id: 1, name: '玻尿酸精华液30ml', quantity: 128, revenue: 38272 },
  { id: 2, name: '烟酰胺美白面霜50g', quantity: 96, revenue: 28800 },
  { id: 3, name: '氨基酸洁面乳120ml', quantity: 215, revenue: 21500 },
  { id: 4, name: '防晒喷雾SPF50+', quantity: 78, revenue: 19110 },
  { id: 5, name: '修复面膜10片装', quantity: 64, revenue: 12288 },
  { id: 6, name: '眼霜抗皱紧致20g', quantity: 42, revenue: 5830 }
]

const mockViewerTrend = [
  { label: '19:00', height: 20, color: 'rgba(124,92,255,0.6)' },
  { label: '19:15', height: 35, color: 'rgba(124,92,255,0.7)' },
  { label: '19:30', height: 55, color: 'rgba(124,92,255,0.8)' },
  { label: '19:45', height: 72, color: 'rgba(0,229,255,0.7)' },
  { label: '20:00', height: 95, color: 'rgba(0,229,255,0.9)' },
  { label: '20:15', height: 100, color: 'rgba(0,255,157,0.9)' },
  { label: '20:30', height: 88, color: 'rgba(0,255,157,0.7)' },
  { label: '20:45', height: 70, color: 'rgba(0,229,255,0.7)' },
  { label: '21:00', height: 50, color: 'rgba(124,92,255,0.7)' },
  { label: '21:15', height: 30, color: 'rgba(124,92,255,0.6)' },
  { label: '21:30', height: 15, color: 'rgba(124,92,255,0.4)' }
]

async function loadDetail(id) {
  try {
    const res = await SessionAPI.detail(id)
    session.value = res.data || mockSession
  } catch {
    session.value = mockSession
  }
  products.value = mockProducts
  viewerTrend.value = mockViewerTrend
}

onLoad((query) => {
  sessionId.value = query.id || '1'
  loadDetail(sessionId.value)
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
  padding: 24rpx 32rpx;
  padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
}

.glass-card {
  background: $bg-card;
  border: 2rpx solid $border-glow;
  border-radius: $radius-md;
  backdrop-filter: blur(20rpx);
  padding: 28rpx;
  margin-bottom: 24rpx;
}

.header-card {
  margin-bottom: 24rpx;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.store-name {
  font-size: 36rpx;
  font-weight: 700;
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

.header-date {
  font-size: 26rpx;
  color: $text-secondary;
}

.stats-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.stat-card {
  flex: 1;
  min-width: 45%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24rpx 16rpx;
  margin-bottom: 0;
}

.stat-value {
  font-size: 34rpx;
  font-weight: 700;
  margin-bottom: 8rpx;

  &.neon-purple { color: $neon-purple; }
  &.neon-cyan { color: $neon-cyan; }
  &.neon-green { color: $neon-green; }
  &.neon-yellow { color: $neon-yellow; }
}

.stat-label {
  font-size: 24rpx;
  color: $text-muted;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 24rpx;
  display: block;
}

.chart-card {
  margin-bottom: 24rpx;
}

.chart-placeholder {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 300rpx;
  padding: 0 8rpx;
}

.chart-bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  height: 100%;
  justify-content: flex-end;
}

.chart-bar {
  width: 70%;
  border-radius: 8rpx 8rpx 0 0;
  min-height: 8rpx;
  transition: height 0.3s;
}

.chart-bar-label {
  font-size: 18rpx;
  color: $text-muted;
  margin-top: 8rpx;
}

.product-section {
  margin-bottom: 0;
}

.product-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 2rpx solid rgba(255, 255, 255, 0.04);

  &:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  flex: 1;
}

.product-name {
  font-size: 28rpx;
  color: $text-primary;
}

.product-qty {
  font-size: 24rpx;
  color: $text-muted;
}

.product-revenue {
  font-size: 28rpx;
  font-weight: 600;
  color: $neon-purple;
}
</style>
