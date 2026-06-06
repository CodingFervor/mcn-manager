<template>
  <view class="page">
    <view class="header">
      <text class="title">部署记录</text>
    </view>
    <view class="filter-bar">
      <view
        class="filter-item"
        v-for="(f, i) in envFilters"
        :key="i"
        :class="{ active: activeEnv === f.value }"
        @tap="activeEnv = f.value"
      >
        <text class="filter-text">{{ f.label }}</text>
      </view>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="timeline">
        <view class="tl-item" v-for="(item, idx) in filteredDeploys" :key="idx">
          <view class="tl-left">
            <view class="tl-dot" :class="'dot-' + item.status" />
            <view v-if="idx < filteredDeploys.length - 1" class="tl-line" />
          </view>
          <view class="tl-card">
            <view class="card-top">
              <text class="card-version">{{ item.version }}</text>
              <view class="env-tag" :class="'env-' + item.environment">
                <text class="env-text">{{ item.envLabel }}</text>
              </view>
            </view>
            <view class="card-body">
              <view class="info-row">
                <text class="info-label">状态</text>
                <text class="info-value" :class="'val-' + item.status">{{ item.statusLabel }}</text>
              </view>
              <view class="info-row">
                <text class="info-label">部署人</text>
                <text class="info-value">{{ item.deployer }}</text>
              </view>
              <view class="info-row">
                <text class="info-label">时间</text>
                <text class="info-value text-muted">{{ item.time }}</text>
              </view>
            </view>
            <text v-if="item.notes" class="card-notes">{{ item.notes }}</text>
          </view>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'

const activeEnv = ref('all')

const envFilters = [
  { label: '全部', value: 'all' },
  { label: '生产', value: 'production' },
  { label: '预发', value: 'staging' },
  { label: '测试', value: 'development' },
]

const deployments = ref([
  { version: 'v3.2.1', environment: 'production', envLabel: '生产', status: 'success', statusLabel: '成功', deployer: '张三', time: '2026-06-06 10:30', notes: '修复支付回调异常' },
  { version: 'v3.2.0', environment: 'production', envLabel: '生产', status: 'success', statusLabel: '成功', deployer: '李四', time: '2026-06-05 14:00', notes: '新增多租户管理模块' },
  { version: 'v3.2.0-rc2', environment: 'staging', envLabel: '预发', status: 'success', statusLabel: '成功', deployer: '李四', time: '2026-06-05 09:15', notes: '回归测试通过' },
  { version: 'v3.1.9', environment: 'production', envLabel: '生产', status: 'failed', statusLabel: '失败', deployer: '王五', time: '2026-06-04 16:45', notes: '数据库迁移失败，已回滚' },
  { version: 'v3.2.0-rc1', environment: 'staging', envLabel: '预发', status: 'success', statusLabel: '成功', deployer: '李四', time: '2026-06-04 11:00', notes: '功能测试环境部署' },
  { version: 'v3.2.0-beta3', environment: 'development', envLabel: '测试', status: 'success', statusLabel: '成功', deployer: '赵六', time: '2026-06-03 20:30', notes: '新功能内部测试' },
  { version: 'v3.1.8', environment: 'production', envLabel: '生产', status: 'success', statusLabel: '成功', deployer: '张三', time: '2026-06-02 10:00', notes: '性能优化，查询速度提升40%' },
  { version: 'v3.2.0-beta2', environment: 'development', envLabel: '测试', status: 'failed', statusLabel: '失败', deployer: '赵六', time: '2026-06-01 15:20', notes: '内存泄漏，需修复后重试' },
])

const filteredDeploys = computed(() => {
  if (activeEnv.value === 'all') return deployments.value
  return deployments.value.filter(d => d.environment === activeEnv.value)
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
  gap: 12rpx;
}

.filter-item {
  padding: 8rpx 22rpx;
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

.timeline {
  display: flex;
  flex-direction: column;
}

.tl-item {
  display: flex;
}

.tl-left {
  width: 48rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.tl-dot {
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 28rpx;

  &.dot-success {
    background: $neon-green;
    box-shadow: 0 0 10rpx rgba(0, 255, 157, 0.4);
  }
  &.dot-failed {
    background: $neon-pink;
    box-shadow: 0 0 10rpx rgba(255, 77, 158, 0.4);
  }
}

.tl-line {
  width: 2rpx;
  flex: 1;
  background: rgba(124, 92, 255, 0.15);
}

.tl-card {
  flex: 1;
  padding: 20rpx 24rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin: 8rpx 12rpx 16rpx;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.card-version {
  font-size: 28rpx;
  font-weight: 700;
  color: $text-primary;
}

.env-tag {
  padding: 4rpx 14rpx;
  border-radius: 8rpx;

  &.env-production { background: rgba(255, 77, 158, 0.12); }
  &.env-staging { background: rgba(255, 210, 63, 0.12); }
  &.env-development { background: rgba(0, 229, 255, 0.12); }
}

.env-text {
  font-size: 20rpx;
  font-weight: 600;
  .env-production & { color: $neon-pink; }
  &.env-staging & { color: $neon-yellow; }
  .env-staging & { color: $neon-yellow; }
  .env-development & { color: $neon-cyan; }
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  margin-bottom: 8rpx;
}

.info-row {
  display: flex;
  justify-content: space-between;
}

.info-label {
  font-size: 22rpx;
  color: $text-muted;
}

.info-value {
  font-size: 22rpx;
  color: $text-secondary;

  &.text-muted { color: $text-muted; }
  &.val-success { color: $neon-green; }
  &.val-failed { color: $neon-pink; }
}

.card-notes {
  font-size: 22rpx;
  color: $text-muted;
  padding-top: 8rpx;
  border-top: 1rpx solid rgba(124, 92, 255, 0.06);
  font-style: italic;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
