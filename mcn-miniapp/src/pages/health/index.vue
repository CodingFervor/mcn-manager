<template>
  <view class="page">
    <view class="header">
      <text class="title">系统监控</text>
      <view class="btn-refresh" @tap="refreshCheck">
        <text class="btn-text">刷新检测</text>
      </view>
    </view>
    <view class="score-card">
      <view class="score-ring">
        <text class="score-value">{{ healthScore }}</text>
        <text class="score-unit">分</text>
      </view>
      <text class="score-label">系统健康度</text>
      <text class="score-hint">{{ healthScore >= 90 ? '运行良好' : healthScore >= 70 ? '需要关注' : '异常' }}</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in services" :key="idx">
        <view class="card-top">
          <view class="svc-left">
            <view class="status-dot" :class="'dot-' + item.status" />
            <text class="svc-name">{{ item.name }}</text>
          </view>
          <text class="svc-time">{{ item.responseTime }}ms</text>
        </view>
        <view class="card-bottom">
          <text class="svc-status-label">{{ item.statusLabel }}</text>
          <text class="svc-check">上次检测: {{ item.lastCheck }}</text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const healthScore = ref(94)

const services = ref([
  { name: 'API 网关', status: 'green', statusLabel: '正常', responseTime: 23, lastCheck: '1分钟前' },
  { name: '数据库主节点', status: 'green', statusLabel: '正常', responseTime: 5, lastCheck: '1分钟前' },
  { name: '数据库从节点', status: 'green', statusLabel: '正常', responseTime: 8, lastCheck: '1分钟前' },
  { name: 'Redis 缓存', status: 'green', statusLabel: '正常', responseTime: 2, lastCheck: '2分钟前' },
  { name: '消息队列', status: 'yellow', statusLabel: '警告', responseTime: 156, lastCheck: '1分钟前' },
  { name: '文件存储', status: 'green', statusLabel: '正常', responseTime: 45, lastCheck: '3分钟前' },
  { name: '搜索引擎', status: 'green', statusLabel: '正常', responseTime: 18, lastCheck: '2分钟前' },
  { name: '邮件服务', status: 'red', statusLabel: '异常', responseTime: 0, lastCheck: '5分钟前' },
])

function refreshCheck() {
  uni.showLoading({ title: '检测中...' })
  setTimeout(() => {
    services.value.forEach(s => {
      s.responseTime = Math.floor(Math.random() * 200) + 2
      s.lastCheck = '刚刚'
      if (s.name === '邮件服务') {
        s.status = 'yellow'
        s.statusLabel = '恢复中'
        s.responseTime = 320
      }
    })
    healthScore.value = 91
    uni.hideLoading()
    uni.showToast({ title: '检测完成', icon: 'success' })
  }, 1500)
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx 16rpx;
}

.title {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
}

.btn-refresh {
  padding: 12rpx 24rpx;
  background: rgba(0, 229, 255, 0.12);
  border: 1rpx solid rgba(0, 229, 255, 0.3);
  border-radius: $radius-sm;
}

.btn-text {
  font-size: 24rpx;
  color: $neon-cyan;
  font-weight: 500;
}

.score-card {
  margin: 8rpx 24rpx 20rpx;
  padding: 32rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-ring {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  border: 6rpx solid $neon-green;
  display: flex;
  align-items: baseline;
  justify-content: center;
  box-shadow: 0 0 30rpx rgba(0, 255, 157, 0.2);
  margin-bottom: 16rpx;
}

.score-value {
  font-size: 56rpx;
  font-weight: 700;
  color: $neon-green;
}

.score-unit {
  font-size: 24rpx;
  color: $neon-green;
  margin-left: 4rpx;
}

.score-label {
  font-size: 28rpx;
  color: $text-primary;
  font-weight: 500;
}

.score-hint {
  font-size: 24rpx;
  color: $neon-green;
  margin-top: 4rpx;
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
  margin-bottom: 12rpx;
}

.svc-left {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.status-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;

  &.dot-green {
    background: $neon-green;
    box-shadow: 0 0 10rpx rgba(0, 255, 157, 0.4);
  }
  &.dot-yellow {
    background: $neon-yellow;
    box-shadow: 0 0 10rpx rgba(255, 210, 63, 0.4);
  }
  &.dot-red {
    background: $neon-pink;
    box-shadow: 0 0 10rpx rgba(255, 77, 158, 0.4);
  }
}

.svc-name {
  font-size: 28rpx;
  font-weight: 500;
  color: $text-primary;
}

.svc-time {
  font-size: 24rpx;
  color: $neon-cyan;
  font-weight: 600;
}

.card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.svc-status-label {
  font-size: 24rpx;
  color: $text-secondary;
}

.svc-check {
  font-size: 22rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
