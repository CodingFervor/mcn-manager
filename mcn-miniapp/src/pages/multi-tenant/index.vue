<template>
  <view class="page">
    <view class="header">
      <text class="title">多租户配置</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in tenants" :key="idx">
        <view class="card-top">
          <text class="card-name">{{ item.name }}</text>
          <view class="plan-badge" :class="'plan-' + item.plan">
            <text class="plan-text">{{ item.planLabel }}</text>
          </view>
        </view>
        <view class="stats-row">
          <view class="stat">
            <text class="stat-value">{{ item.users }}</text>
            <text class="stat-label">用户数</text>
          </view>
          <view class="stat-divider" />
          <view class="stat">
            <text class="stat-value">{{ item.stores }}</text>
            <text class="stat-label">门店数</text>
          </view>
          <view class="stat-divider" />
          <view class="stat">
            <text class="stat-value">{{ item.orders }}</text>
            <text class="stat-label">本月订单</text>
          </view>
        </view>
        <view class="card-footer">
          <view class="status-wrap">
            <view class="status-dot" :class="item.active ? 'dot-on' : 'dot-off'" />
            <text class="status-text">{{ item.active ? '运行中' : '已暂停' }}</text>
          </view>
          <text class="expiry-text">到期: {{ item.expiry }}</text>
        </view>
      </view>
      <!-- Plan Comparison -->
      <view class="compare-section">
        <text class="section-title">套餐对比</text>
        <view class="compare-row" v-for="(p, pi) in plans" :key="pi">
          <view class="plan-indicator" :class="'pi-' + p.key" />
          <text class="plan-name">{{ p.name }}</text>
          <text class="plan-price">{{ p.price }}</text>
          <text class="plan-limits">{{ p.limits }}</text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const tenants = ref([
  { name: '美妆旗舰店', plan: 'enterprise', planLabel: '企业版', users: 128, stores: 12, orders: 3420, active: true, expiry: '2027-03-15' },
  { name: '服饰连锁', plan: 'pro', planLabel: '专业版', users: 56, stores: 8, orders: 1850, active: true, expiry: '2026-12-31' },
  { name: '食品电商', plan: 'pro', planLabel: '专业版', users: 32, stores: 5, orders: 980, active: true, expiry: '2026-09-20' },
  { name: '数码家电', plan: 'starter', planLabel: '基础版', users: 15, stores: 2, orders: 320, active: true, expiry: '2026-07-30' },
  { name: '家居生活馆', plan: 'starter', planLabel: '基础版', users: 8, stores: 1, orders: 156, active: false, expiry: '2026-06-10' },
])

const plans = [
  { key: 'starter', name: '基础版', price: '¥299/月', limits: '5用户 / 3门店' },
  { key: 'pro', name: '专业版', price: '¥999/月', limits: '50用户 / 10门店' },
  { key: 'enterprise', name: '企业版', price: '¥2999/月', limits: '不限用户 / 不限门店' },
]
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

.plan-badge {
  padding: 4rpx 14rpx;
  border-radius: 8rpx;

  &.plan-starter { background: rgba(107, 115, 147, 0.15); }
  &.plan-pro { background: rgba(0, 229, 255, 0.12); }
  &.plan-enterprise { background: rgba(124, 92, 255, 0.15); }
}

.plan-text {
  font-size: 22rpx;
  font-weight: 600;
  .plan-starter & { color: $text-muted; }
  .plan-pro & { color: $neon-cyan; }
  .plan-enterprise & { color: $neon-purple; }
}

.stats-row {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 16rpx 0;
  margin-bottom: 16rpx;
  background: rgba(10, 14, 39, 0.4);
  border-radius: $radius-sm;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}

.stat-value {
  font-size: 30rpx;
  font-weight: 700;
  color: $text-primary;
}

.stat-label {
  font-size: 22rpx;
  color: $text-muted;
}

.stat-divider {
  width: 1rpx;
  height: 48rpx;
  background: rgba(124, 92, 255, 0.15);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-wrap {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.status-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;

  &.dot-on { background: $neon-green; box-shadow: 0 0 8rpx rgba(0, 255, 157, 0.4); }
  &.dot-off { background: $text-muted; }
}

.status-text {
  font-size: 24rpx;
  color: $text-secondary;
}

.expiry-text {
  font-size: 22rpx;
  color: $text-muted;
}

.compare-section {
  padding: 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 20rpx;
  display: block;
}

.compare-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 12rpx 0;
  border-bottom: 1rpx solid rgba(124, 92, 255, 0.06);

  &:last-child { border-bottom: none; }
}

.plan-indicator {
  width: 8rpx;
  height: 32rpx;
  border-radius: 4rpx;

  &.pi-starter { background: $text-muted; }
  &.pi-pro { background: $neon-cyan; }
  &.pi-enterprise { background: $neon-purple; }
}

.plan-name {
  font-size: 26rpx;
  color: $text-primary;
  font-weight: 500;
  min-width: 100rpx;
}

.plan-price {
  font-size: 24rpx;
  color: $neon-yellow;
  font-weight: 600;
  min-width: 140rpx;
}

.plan-limits {
  font-size: 22rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
