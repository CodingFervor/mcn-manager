<template>
  <view class="page">
    <view class="header">
      <text class="title">功能开关</text>
    </view>
    <view class="filter-bar">
      <view
        class="filter-item"
        :class="{ active: activeFilter === 'all' }"
        @tap="activeFilter = 'all'"
      >
        <text class="filter-text">全部</text>
      </view>
      <view
        class="filter-item"
        :class="{ active: activeFilter === 'enabled' }"
        @tap="activeFilter = 'enabled'"
      >
        <text class="filter-text">已启用</text>
      </view>
      <view
        class="filter-item"
        :class="{ active: activeFilter === 'disabled' }"
        @tap="activeFilter = 'disabled'"
      >
        <text class="filter-text">已关闭</text>
      </view>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in filteredFlags" :key="idx">
        <view class="card-top">
          <view class="card-left">
            <text class="card-name">{{ item.name }}</text>
            <text class="card-code">{{ item.code }}</text>
          </view>
          <view class="switch-wrap" @tap="item.enabled = !item.enabled">
            <view class="switch-track" :class="{ on: item.enabled }">
              <view class="switch-thumb" />
            </view>
          </view>
        </view>
        <view class="rollout-wrap">
          <text class="rollout-label">发布比例</text>
          <view class="rollout-bar">
            <view class="rollout-fill" :style="{ width: item.rollout + '%' }" />
          </view>
          <text class="rollout-pct">{{ item.rollout }}%</text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'

const activeFilter = ref('all')

const flags = ref([
  { name: '新版仪表盘', code: 'new_dashboard', enabled: true, rollout: 100 },
  { name: 'AI智能推荐', code: 'ai_recommendation', enabled: true, rollout: 75 },
  { name: '多租户模式', code: 'multi_tenant', enabled: true, rollout: 50 },
  { name: '实时协作编辑', code: 'realtime_collab', enabled: false, rollout: 0 },
  { name: '暗黑模式', code: 'dark_mode', enabled: true, rollout: 100 },
  { name: '高级搜索', code: 'advanced_search', enabled: true, rollout: 30 },
  { name: '自动翻译', code: 'auto_translate', enabled: false, rollout: 0 },
  { name: '语音助手', code: 'voice_assistant', enabled: false, rollout: 10 },
])

const filteredFlags = computed(() => {
  if (activeFilter.value === 'all') return flags.value
  if (activeFilter.value === 'enabled') return flags.value.filter(f => f.enabled)
  return flags.value.filter(f => !f.enabled)
})
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
  padding: 8rpx 24rpx;
  border-radius: 32rpx;
  background: rgba(124, 92, 255, 0.08);
  border: 1rpx solid rgba(124, 92, 255, 0.12);

  &.active {
    background: rgba(124, 92, 255, 0.2);
    border-color: $neon-purple;
  }
}

.filter-text {
  font-size: 24rpx;
  color: $text-secondary;
  .active & { color: $neon-purple; font-weight: 600; }
}

.scroll-body {
  flex: 1;
  height: 0;
  padding: 0 24rpx;
}

.card {
  padding: 24rpx 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 16rpx;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.card-left {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.card-name {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.card-code {
  font-size: 22rpx;
  color: $text-muted;
  font-family: monospace;
}

.switch-track {
  width: 76rpx;
  height: 42rpx;
  border-radius: 21rpx;
  background: rgba(107, 115, 147, 0.3);
  position: relative;

  &.on { background: rgba(124, 92, 255, 0.5); }
}

.switch-thumb {
  width: 34rpx;
  height: 34rpx;
  border-radius: 50%;
  background: #fff;
  position: absolute;
  top: 4rpx;
  left: 4rpx;
  transition: transform 0.3s;
  .on & { transform: translateX(34rpx); }
}

.rollout-wrap {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.rollout-label {
  font-size: 22rpx;
  color: $text-muted;
  min-width: 80rpx;
}

.rollout-bar {
  flex: 1;
  height: 10rpx;
  background: rgba(124, 92, 255, 0.1);
  border-radius: 5rpx;
  overflow: hidden;
}

.rollout-fill {
  height: 100%;
  background: linear-gradient(90deg, $neon-purple, $neon-cyan);
  border-radius: 5rpx;
}

.rollout-pct {
  font-size: 24rpx;
  color: $neon-cyan;
  font-weight: 600;
  min-width: 64rpx;
  text-align: right;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
