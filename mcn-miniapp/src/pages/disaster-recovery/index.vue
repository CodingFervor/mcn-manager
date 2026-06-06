<template>
  <view class="page">
    <view class="header">
      <text class="title">灾备管理</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in plans" :key="idx">
        <view class="card-top">
          <text class="card-name">{{ item.name }}</text>
          <view class="health-dots">
            <view class="h-dot" v-for="(d, di) in 3" :key="di" :class="{ 'h-ok': di < item.healthLevel }" />
          </view>
        </view>
        <view class="type-tag">
          <text class="type-text">{{ item.type }}</text>
        </view>
        <view class="metrics">
          <view class="metric">
            <text class="metric-label">RPO</text>
            <text class="metric-value">{{ item.rpo }}</text>
          </view>
          <view class="metric-sep" />
          <view class="metric">
            <text class="metric-label">RTO</text>
            <text class="metric-value">{{ item.rto }}</text>
          </view>
          <view class="metric-sep" />
          <view class="metric">
            <text class="metric-label">上次测试</text>
            <text class="metric-value">{{ item.lastTest }}</text>
          </view>
        </view>
        <view class="card-footer">
          <text class="footer-status" :class="item.healthy ? 'text-green' : 'text-red'">
            {{ item.healthy ? '健康' : '异常' }}
          </text>
          <text class="footer-desc">{{ item.description }}</text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const plans = ref([
  { name: '主数据库容灾', type: '热备', rpo: '< 1分钟', rto: '< 5分钟', lastTest: '2026-06-01', healthLevel: 3, healthy: true, description: '跨可用区实时同步，自动故障切换' },
  { name: '文件存储灾备', type: '温备', rpo: '< 1小时', rto: '< 30分钟', lastTest: '2026-05-28', healthLevel: 3, healthy: true, description: '每日增量备份至异地存储' },
  { name: '应用服务容灾', type: '热备', rpo: '0', rto: '< 2分钟', lastTest: '2026-06-05', healthLevel: 3, healthy: true, description: '多节点负载均衡，自动健康检测' },
  { name: '缓存服务灾备', type: '温备', rpo: '< 5分钟', rto: '< 10分钟', lastTest: '2026-05-20', healthLevel: 2, healthy: true, description: 'Redis哨兵模式，自动主从切换' },
  { name: '消息队列灾备', type: '冷备', rpo: '< 30分钟', rto: '< 1小时', lastTest: '2026-04-15', healthLevel: 2, healthy: false, description: '需人工介入恢复，测试覆盖率不足' },
  { name: 'DNS灾备方案', type: '热备', rpo: '0', rto: '< 1分钟', lastTest: '2026-05-30', healthLevel: 3, healthy: true, description: '多DNS服务商自动切换' },
])
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

.card-name {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.health-dots {
  display: flex;
  gap: 6rpx;
}

.h-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: rgba(107, 115, 147, 0.3);

  &.h-ok {
    background: $neon-green;
    box-shadow: 0 0 6rpx rgba(0, 255, 157, 0.4);
  }
}

.type-tag {
  padding: 2rpx 12rpx;
  border-radius: 6rpx;
  background: rgba(124, 92, 255, 0.12);
  align-self: flex-start;
  margin-bottom: 16rpx;
}

.type-text {
  font-size: 20rpx;
  color: $neon-purple;
  font-weight: 500;
}

.metrics {
  display: flex;
  align-items: center;
  padding: 16rpx;
  background: rgba(10, 14, 39, 0.4);
  border-radius: $radius-sm;
  margin-bottom: 16rpx;
}

.metric {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}

.metric-label {
  font-size: 22rpx;
  color: $text-muted;
}

.metric-value {
  font-size: 24rpx;
  font-weight: 600;
  color: $neon-cyan;
}

.metric-sep {
  width: 1rpx;
  height: 40rpx;
  background: rgba(124, 92, 255, 0.15);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-status {
  font-size: 24rpx;
  font-weight: 600;

  &.text-green { color: $neon-green; }
  &.text-red { color: $neon-pink; }
}

.footer-desc {
  font-size: 22rpx;
  color: $text-muted;
  max-width: 360rpx;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
