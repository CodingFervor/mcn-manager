<template>
  <view class="page">
    <view class="header">
      <text class="title">合规审计</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in audits" :key="idx">
        <view class="card-top">
          <text class="card-title">{{ item.title }}</text>
          <view class="status-tag" :class="'st-' + item.status">
            <text class="status-text">{{ item.statusLabel }}</text>
          </view>
        </view>
        <view class="card-meta">
          <view class="standard-badge">
            <text class="standard-text">{{ item.standard }}</text>
          </view>
          <text class="meta-type">{{ item.type }}</text>
        </view>
        <view v-if="item.status === 'in_progress'" class="progress-wrap">
          <view class="progress-track">
            <view class="progress-fill" :style="{ width: item.progress + '%' }" />
          </view>
          <text class="progress-pct">{{ item.progress }}%</text>
        </view>
        <view class="card-footer">
          <view class="findings">
            <text class="findings-label">发现问题</text>
            <text class="findings-count" :class="{ 'has-issues': item.findings > 0 }">{{ item.findings }}</text>
          </view>
          <text class="card-date">{{ item.date }}</text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const audits = ref([
  { title: 'GDPR 数据保护审计', type: '数据合规', standard: 'GDPR', status: 'completed', statusLabel: '已完成', findings: 3, progress: 100, date: '2026-05-28' },
  { title: '信息安全等级保护', type: '安全合规', standard: '等保三级', status: 'in_progress', statusLabel: '进行中', findings: 5, progress: 72, date: '2026-06-06' },
  { title: 'PCI-DSS 支付安全', type: '支付合规', standard: 'PCI-DSS', status: 'in_progress', statusLabel: '进行中', findings: 2, progress: 45, date: '2026-06-04' },
  { title: '个人信息保护审计', type: '隐私合规', standard: 'PIPL', status: 'completed', statusLabel: '已完成', findings: 0, progress: 100, date: '2026-05-15' },
  { title: 'SOC 2 Type II 审计', type: '安全合规', standard: 'SOC 2', status: 'pending', statusLabel: '待开始', findings: 0, progress: 0, date: '2026-07-01' },
  { title: 'ISO 27001 年度审核', type: '体系合规', standard: 'ISO 27001', status: 'completed', statusLabel: '已完成', findings: 1, progress: 100, date: '2026-04-20' },
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

.card-title {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  flex: 1;
}

.status-tag {
  padding: 4rpx 14rpx;
  border-radius: 8rpx;

  &.st-completed { background: rgba(0, 255, 157, 0.12); }
  &.st-in_progress { background: rgba(0, 229, 255, 0.12); }
  &.st-pending { background: rgba(255, 210, 63, 0.12); }
}

.status-text {
  font-size: 22rpx;
  font-weight: 500;
  .st-completed & { color: $neon-green; }
  .st-in_progress & { color: $neon-cyan; }
  .st-pending & { color: $neon-yellow; }
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.standard-badge {
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  background: rgba(124, 92, 255, 0.12);
  border: 1rpx solid rgba(124, 92, 255, 0.2);
}

.standard-text {
  font-size: 22rpx;
  color: $neon-purple;
  font-weight: 600;
}

.meta-type {
  font-size: 24rpx;
  color: $text-muted;
}

.progress-wrap {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.progress-track {
  flex: 1;
  height: 10rpx;
  background: rgba(0, 229, 255, 0.1);
  border-radius: 5rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $neon-cyan, $neon-purple);
  border-radius: 5rpx;
}

.progress-pct {
  font-size: 24rpx;
  color: $neon-cyan;
  font-weight: 600;
  min-width: 64rpx;
  text-align: right;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12rpx;
  border-top: 1rpx solid rgba(124, 92, 255, 0.08);
}

.findings {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.findings-label {
  font-size: 24rpx;
  color: $text-muted;
}

.findings-count {
  font-size: 26rpx;
  font-weight: 700;
  color: $neon-green;

  &.has-issues {
    color: $neon-pink;
  }
}

.card-date {
  font-size: 22rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
