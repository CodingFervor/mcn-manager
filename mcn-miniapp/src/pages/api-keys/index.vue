<template>
  <view class="page">
    <view class="header">
      <text class="title">API密钥管理</text>
      <view class="btn-create" @tap="createKey">
        <text class="btn-text">创建密钥</text>
      </view>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in apiKeys" :key="idx">
        <view class="card-top">
          <text class="card-name">{{ item.name }}</text>
          <view class="status-dot" :class="item.revoked ? 'dot-off' : 'dot-on'" />
        </view>
        <view class="key-display">
          <text class="key-text">{{ item.maskedKey }}</text>
        </view>
        <view class="perm-tags">
          <view class="perm-tag" v-for="(p, pi) in item.permissions" :key="pi">
            <text class="perm-text">{{ p }}</text>
          </view>
        </view>
        <view class="card-meta">
          <view class="meta-row">
            <text class="meta-label">频率限制</text>
            <text class="meta-value">{{ item.rateLimit }} 次/分</text>
          </view>
          <view class="meta-row">
            <text class="meta-label">上次使用</text>
            <text class="meta-value">{{ item.lastUsed }}</text>
          </view>
          <view class="meta-row">
            <text class="meta-label">到期时间</text>
            <text class="meta-value" :class="item.expiringSoon ? 'text-warn' : ''">{{ item.expiry }}</text>
          </view>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const apiKeys = ref([
  { name: '生产环境主密钥', maskedKey: 'sk_live_••••••••••••4f2a', permissions: ['读取', '写入', '删除'], rateLimit: 1000, lastUsed: '5分钟前', expiry: '2027-06-30', expiringSoon: false, revoked: false },
  { name: '数据分析接口', maskedKey: 'sk_live_••••••••••••8b1c', permissions: ['读取'], rateLimit: 500, lastUsed: '1小时前', expiry: '2026-12-31', expiringSoon: false, revoked: false },
  { name: 'Webhook回调', maskedKey: 'sk_live_••••••••••••e7d3', permissions: ['读取', '写入'], rateLimit: 200, lastUsed: '3小时前', expiry: '2026-06-15', expiringSoon: true, revoked: false },
  { name: '测试环境密钥', maskedKey: 'sk_test_••••••••••••a9f0', permissions: ['读取', '写入', '删除'], rateLimit: 100, lastUsed: '2天前', expiry: '2027-01-31', expiringSoon: false, revoked: false },
  { name: '旧版接口密钥', maskedKey: 'sk_live_••••••••••••2e5b', permissions: ['读取'], rateLimit: 50, lastUsed: '30天前', expiry: '2026-03-01', expiringSoon: false, revoked: true },
])

function createKey() {
  uni.showToast({ title: '密钥创建向导', icon: 'none' })
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

.btn-create {
  padding: 14rpx 28rpx;
  background: linear-gradient(135deg, $neon-purple, #9b7cff);
  border-radius: $radius-sm;
}

.btn-text {
  font-size: 26rpx;
  font-weight: 600;
  color: #fff;
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

.status-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;

  &.dot-on {
    background: $neon-green;
    box-shadow: 0 0 8rpx rgba(0, 255, 157, 0.4);
  }
  &.dot-off {
    background: $text-muted;
  }
}

.key-display {
  padding: 12rpx 16rpx;
  background: rgba(10, 14, 39, 0.6);
  border-radius: $radius-sm;
  border: 1rpx solid rgba(124, 92, 255, 0.1);
  margin-bottom: 12rpx;
}

.key-text {
  font-size: 22rpx;
  font-family: monospace;
  color: $neon-cyan;
  letter-spacing: 1rpx;
}

.perm-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.perm-tag {
  padding: 2rpx 12rpx;
  border-radius: 6rpx;
  background: rgba(124, 92, 255, 0.1);
  border: 1rpx solid rgba(124, 92, 255, 0.15);
}

.perm-text {
  font-size: 20rpx;
  color: $text-secondary;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  padding-top: 12rpx;
  border-top: 1rpx solid rgba(124, 92, 255, 0.06);
}

.meta-row {
  display: flex;
  justify-content: space-between;
}

.meta-label {
  font-size: 22rpx;
  color: $text-muted;
}

.meta-value {
  font-size: 22rpx;
  color: $text-secondary;

  &.text-warn { color: $neon-pink; }
}

.bottom-spacer {
  height: 40rpx;
}
</style>
