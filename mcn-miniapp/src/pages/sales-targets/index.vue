<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">销售目标</text>
    </view>

    <scroll-view scroll-y class="target-list">
      <view
        v-for="target in targets"
        :key="target.id"
        class="glass-card target-card"
      >
        <view class="card-top">
          <text class="target-name">{{ target.name }}</text>
          <text :class="['percent-tag', getPercentClass(target.percent)]">
            {{ formatPercent(target.percent) }}
          </text>
        </view>

        <text class="target-store">{{ target.store }}</text>

        <!-- Progress Bar -->
        <view class="progress-wrap">
          <view class="progress-track">
            <view
              class="progress-fill"
              :style="{ width: Math.min(target.percent, 100) + '%', background: getBarColor(target.percent) }"
            ></view>
          </view>
        </view>

        <view class="values-row">
          <view class="value-item">
            <text class="value-label">当前</text>
            <text class="value-num current">{{ formatMoney(target.currentValue) }}</text>
          </view>
          <view class="value-item">
            <text class="value-label">目标</text>
            <text class="value-num goal">{{ formatMoney(target.targetValue) }}</text>
          </view>
          <view class="value-item">
            <text class="value-label">截止</text>
            <text class="value-num deadline">{{ formatDate(target.deadline) }}</text>
          </view>
        </view>
      </view>

      <view v-if="targets.length === 0" class="empty-tip">
        <text class="tip-text">暂无销售目标</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { SalesTargetAPI } from '@/api'
import { formatMoney, formatDate, formatPercent } from '@/utils/format'

const targets = ref([])

const mockTargets = [
  { id: 1, name: '6月GMV总目标', store: '旗舰店A', currentValue: 458000, targetValue: 800000, percent: 57.3, deadline: '2026-06-30' },
  { id: 2, name: '618大促专场', store: '旗舰店A', currentValue: 125800, targetValue: 500000, percent: 25.2, deadline: '2026-06-18' },
  { id: 3, name: '新品首发目标', store: '品牌店B', currentValue: 89600, targetValue: 100000, percent: 89.6, deadline: '2026-06-15' },
  { id: 4, name: '护肤品类销售', store: '专卖店C', currentValue: 234500, targetValue: 300000, percent: 78.2, deadline: '2026-06-30' },
  { id: 5, name: '彩妆品类销售', store: '专卖店C', currentValue: 67800, targetValue: 200000, percent: 33.9, deadline: '2026-06-30' },
  { id: 6, name: '618预热目标', store: '旗舰店A', currentValue: 156200, targetValue: 200000, percent: 78.1, deadline: '2026-06-10' },
  { id: 7, name: '复购率提升', store: '全店', currentValue: 0, targetValue: 0, percent: 92.0, deadline: '2026-06-30' },
  { id: 8, name: '新增粉丝目标', store: '全店', currentValue: 0, targetValue: 0, percent: 45.5, deadline: '2026-06-30' }
]

// For targets 7 and 8, set realistic mock values
mockTargets[6].currentValue = 3680
mockTargets[6].targetValue = 4000
mockTargets[7].currentValue = 2275
mockTargets[7].targetValue = 5000

function getPercentClass(percent) {
  if (percent >= 80) return 'high'
  if (percent >= 50) return 'medium'
  return 'low'
}

function getBarColor(percent) {
  if (percent >= 80) return $neon-green
  if (percent >= 50) return $neon-yellow
  return $neon-pink
}

async function loadData() {
  try {
    const res = await SalesTargetAPI.list()
    targets.value = res.data?.results || res.data || mockTargets
  } catch {
    targets.value = mockTargets
  }
}

onShow(() => {
  loadData()
})

onPullDownRefresh(async () => {
  await loadData()
  uni.stopPullDownRefresh()
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
}

.page-header {
  padding: 24rpx 32rpx;
}

.page-title {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
}

.target-list {
  padding: 0 32rpx;
  height: calc(100vh - 100rpx);
}

.glass-card {
  background: $bg-card;
  border: 2rpx solid $border-glow;
  border-radius: $radius-md;
  backdrop-filter: blur(20rpx);
}

.target-card {
  padding: 28rpx;
  margin-bottom: 24rpx;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.target-name {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
  flex: 1;
}

.percent-tag {
  font-size: 28rpx;
  font-weight: 700;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;

  &.high {
    background: rgba($neon-green, 0.15);
    color: $neon-green;
  }
  &.medium {
    background: rgba($neon-yellow, 0.15);
    color: $neon-yellow;
  }
  &.low {
    background: rgba($neon-pink, 0.15);
    color: $neon-pink;
  }
}

.target-store {
  font-size: 24rpx;
  color: $text-muted;
  margin-bottom: 20rpx;
}

.progress-wrap {
  margin-bottom: 20rpx;
}

.progress-track {
  height: 20rpx;
  border-radius: 10rpx;
  background: rgba(255, 255, 255, 0.06);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 10rpx;
  transition: width 0.5s ease;
}

.values-row {
  display: flex;
  justify-content: space-between;
}

.value-item {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.value-label {
  font-size: 22rpx;
  color: $text-muted;
}

.value-num {
  font-size: 26rpx;
  font-weight: 600;

  &.current { color: $neon-cyan; }
  &.goal { color: $text-secondary; }
  &.deadline { color: $text-secondary; font-size: 24rpx; }
}

.empty-tip {
  padding: 80rpx 0;
  text-align: center;
}

.tip-text {
  font-size: 28rpx;
  color: $text-muted;
}
</style>
