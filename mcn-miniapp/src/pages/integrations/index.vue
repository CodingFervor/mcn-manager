<template>
  <view class="page">
    <view class="header">
      <text class="title">集成配置</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="grid">
        <view class="card" v-for="(item, idx) in integrations" :key="idx" @tap="tapCard(idx)">
          <view class="icon-wrap" :style="{ background: item.iconBg }">
            <text class="icon-text">{{ item.icon }}</text>
          </view>
          <text class="card-name">{{ item.name }}</text>
          <text class="card-type">{{ item.type }}</text>
          <view class="card-status">
            <view class="dot" :class="item.active ? 'dot-on' : 'dot-off'" />
            <text class="status-label">{{ item.active ? '已连接' : '未连接' }}</text>
          </view>
          <text class="card-sync">同步: {{ item.lastSync }}</text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const integrations = ref([
  { name: '企业微信', type: '即时通讯', icon: '\u{1F4AC}', iconBg: 'rgba(0, 229, 255, 0.12)', active: true, lastSync: '5分钟前' },
  { name: '钉钉', type: '即时通讯', icon: '\u{1F514}', iconBg: 'rgba(0, 229, 255, 0.12)', active: true, lastSync: '10分钟前' },
  { name: '飞书', type: '即时通讯', icon: '\u{1F4E8}', iconBg: 'rgba(124, 92, 255, 0.12)', active: false, lastSync: '未同步' },
  { name: '支付宝', type: '支付网关', icon: '\u{1F4B3}', iconBg: 'rgba(0, 255, 157, 0.12)', active: true, lastSync: '实时' },
  { name: '微信支付', type: '支付网关', icon: '\u{1F4B0}', iconBg: 'rgba(0, 255, 157, 0.12)', active: true, lastSync: '实时' },
  { name: '阿里云OSS', type: '对象存储', icon: '\u{2601}\u{FE0F}', iconBg: 'rgba(255, 210, 63, 0.12)', active: true, lastSync: '1分钟前' },
  { name: 'Sentry', type: '错误监控', icon: '\u{1F6A9}', iconBg: 'rgba(255, 77, 158, 0.12)', active: true, lastSync: '实时' },
  { name: 'Slack', type: '即时通讯', icon: '\u{1F4E3}', iconBg: 'rgba(124, 92, 255, 0.12)', active: false, lastSync: '未同步' },
])

function tapCard(idx) {
  const item = integrations.value[idx]
  uni.showModal({
    title: item.name,
    content: `类型: ${item.type}\n状态: ${item.active ? '已连接' : '未连接'}\n上次同步: ${item.lastSync}`,
    showCancel: false,
  })
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

.scroll-body {
  flex: 1;
  height: 0;
  padding: 0 24rpx;
}

.grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.card {
  width: calc(50% - 8rpx);
  padding: 24rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.icon-wrap {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12rpx;
}

.icon-text {
  font-size: 36rpx;
}

.card-name {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 4rpx;
}

.card-type {
  font-size: 22rpx;
  color: $text-muted;
  margin-bottom: 12rpx;
}

.card-status {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 8rpx;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;

  &.dot-on {
    background: $neon-green;
    box-shadow: 0 0 8rpx rgba(0, 255, 157, 0.4);
  }
  &.dot-off {
    background: $text-muted;
  }
}

.status-label {
  font-size: 22rpx;
  color: $text-secondary;
}

.card-sync {
  font-size: 20rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
