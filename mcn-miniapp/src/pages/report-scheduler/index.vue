<template>
  <view class="page">
    <view class="header">
      <text class="title">报表计划</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in schedules" :key="idx">
        <view class="card-top">
          <view class="card-left">
            <text class="card-name">{{ item.name }}</text>
          </view>
          <view class="switch-wrap" @tap="item.active = !item.active">
            <view class="switch-track" :class="{ on: item.active }">
              <view class="switch-thumb" />
            </view>
          </view>
        </view>
        <view class="card-meta">
          <view class="meta-item">
            <text class="meta-label">执行周期</text>
            <text class="meta-value cron-text">{{ item.cron }}</text>
          </view>
          <view class="meta-item">
            <text class="meta-label">输出格式</text>
            <view class="format-tag">
              <text class="format-text">{{ item.format }}</text>
            </view>
          </view>
          <view class="meta-item">
            <text class="meta-label">接收人</text>
            <text class="meta-value">{{ item.recipients }} 人</text>
          </view>
        </view>
        <view class="card-footer">
          <text class="footer-label">上次执行</text>
          <text class="footer-value" :class="item.lastStatus === 'success' ? 'text-green' : 'text-red'">
            {{ item.lastRun }}
          </text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const schedules = ref([
  { name: '日报-销售汇总', cron: '0 8 * * *', format: 'PDF', recipients: 12, active: true, lastRun: '2026-06-06 08:00', lastStatus: 'success' },
  { name: '周报-运营分析', cron: '0 9 * * 1', format: 'Excel', recipients: 8, active: true, lastRun: '2026-06-02 09:00', lastStatus: 'success' },
  { name: '月报-财务结算', cron: '0 10 1 * *', format: 'PDF', recipients: 5, active: true, lastRun: '2026-06-01 10:00', lastStatus: 'success' },
  { name: '实时库存预警', cron: '*/30 * * * *', format: '邮件', recipients: 3, active: false, lastRun: '2026-05-30 15:30', lastStatus: 'failed' },
  { name: '直播数据报告', cron: '0 20 * * *', format: 'Excel', recipients: 6, active: true, lastRun: '2026-06-05 20:00', lastStatus: 'success' },
  { name: '客户留存分析', cron: '0 10 * * 5', format: 'PDF', recipients: 4, active: true, lastRun: '2026-05-30 10:00', lastStatus: 'success' },
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
  margin-bottom: 20rpx;
}

.card-name {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
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

.card-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.meta-label {
  font-size: 22rpx;
  color: $text-muted;
}

.meta-value {
  font-size: 24rpx;
  color: $text-secondary;
}

.cron-text {
  font-family: monospace;
  font-size: 22rpx;
  color: $neon-cyan;
}

.format-tag {
  padding: 2rpx 12rpx;
  border-radius: 6rpx;
  background: rgba(124, 92, 255, 0.12);
  align-self: flex-start;
}

.format-text {
  font-size: 22rpx;
  color: $neon-purple;
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16rpx;
  border-top: 1rpx solid rgba(124, 92, 255, 0.08);
}

.footer-label {
  font-size: 22rpx;
  color: $text-muted;
}

.footer-value {
  font-size: 22rpx;

  &.text-green { color: $neon-green; }
  &.text-red { color: $neon-pink; }
}

.bottom-spacer {
  height: 40rpx;
}
</style>
