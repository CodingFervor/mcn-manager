<template>
  <view class="page">
    <view class="header">
      <text class="title">许可证管理</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in licenses" :key="idx">
        <view class="card-top">
          <text class="card-product">{{ item.product }}</text>
          <view class="type-badge" :class="'badge-' + item.type">
            <text class="badge-text">{{ item.typeLabel }}</text>
          </view>
        </view>
        <view class="card-meta">
          <view class="meta-row">
            <text class="meta-label">已激活</text>
            <text class="meta-value">{{ item.activations }} / {{ item.maxActivations }}</text>
          </view>
          <view class="activation-bar">
            <view class="activation-fill" :style="{ width: (item.activations / item.maxActivations * 100) + '%' }" />
          </view>
        </view>
        <view class="card-footer">
          <view class="expiry-wrap" v-if="item.expiringSoon">
            <text class="warn-icon">!</text>
            <text class="expiry-warn">即将到期</text>
          </view>
          <text class="expiry-date" v-else>到期: {{ item.expiry }}</text>
          <text class="expiry-date">{{ item.expiry }}</text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const licenses = ref([
  { product: 'MCN管家 专业版', type: 'professional', typeLabel: '专业版', activations: 45, maxActivations: 100, expiry: '2027-06-30', expiringSoon: false },
  { product: '数据分析模块', type: 'addon', typeLabel: '增值模块', activations: 12, maxActivations: 50, expiry: '2026-12-31', expiringSoon: false },
  { product: 'API 高级接口', type: 'enterprise', typeLabel: '企业版', activations: 3, maxActivations: 10, expiry: '2027-03-15', expiringSoon: false },
  { product: 'SSL通配符证书', type: 'standard', typeLabel: '标准版', activations: 5, maxActivations: 5, expiry: '2026-06-20', expiringSoon: true },
  { product: '短信服务包', type: 'addon', typeLabel: '增值模块', activations: 1, maxActivations: 1, expiry: '2026-06-15', expiringSoon: true },
  { product: '对象存储扩展', type: 'professional', typeLabel: '专业版', activations: 2, maxActivations: 10, expiry: '2027-01-31', expiringSoon: false },
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
  margin-bottom: 16rpx;
}

.card-product {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.type-badge {
  padding: 4rpx 14rpx;
  border-radius: 8rpx;

  &.badge-standard { background: rgba(107, 115, 147, 0.15); }
  &.badge-professional { background: rgba(0, 229, 255, 0.12); }
  &.badge-enterprise { background: rgba(124, 92, 255, 0.15); }
  &.badge-addon { background: rgba(255, 210, 63, 0.12); }
}

.badge-text {
  font-size: 22rpx;
  font-weight: 500;
  .badge-standard & { color: $text-muted; }
  .badge-professional & { color: $neon-cyan; }
  .badge-enterprise & { color: $neon-purple; }
  .badge-addon & { color: $neon-yellow; }
}

.card-meta {
  margin-bottom: 16rpx;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8rpx;
}

.meta-label {
  font-size: 24rpx;
  color: $text-muted;
}

.meta-value {
  font-size: 24rpx;
  color: $text-secondary;
  font-weight: 500;
}

.activation-bar {
  height: 8rpx;
  background: rgba(124, 92, 255, 0.1);
  border-radius: 4rpx;
  overflow: hidden;
}

.activation-fill {
  height: 100%;
  background: linear-gradient(90deg, $neon-purple, $neon-cyan);
  border-radius: 4rpx;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12rpx;
  border-top: 1rpx solid rgba(124, 92, 255, 0.08);
}

.expiry-wrap {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.warn-icon {
  width: 28rpx;
  height: 28rpx;
  border-radius: 50%;
  background: rgba(255, 77, 158, 0.2);
  color: $neon-pink;
  font-size: 20rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  line-height: 28rpx;
}

.expiry-warn {
  font-size: 24rpx;
  color: $neon-pink;
  font-weight: 500;
}

.expiry-date {
  font-size: 22rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
