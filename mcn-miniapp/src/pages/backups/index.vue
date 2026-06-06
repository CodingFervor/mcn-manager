<template>
  <view class="page">
    <view class="header">
      <view class="header-left">
        <text class="title">数据备份</text>
        <text class="subtitle">{{ backups.length }} 条记录</text>
      </view>
      <view class="btn-primary" @tap="startBackup">
        <text class="btn-text">立即备份</text>
      </view>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view v-if="isRunning" class="progress-card">
        <view class="progress-top">
          <text class="progress-label">正在备份中...</text>
          <text class="progress-pct">{{ progress }}%</text>
        </view>
        <view class="progress-track">
          <view class="progress-fill" :style="{ width: progress + '%' }" />
        </view>
      </view>
      <view class="card" v-for="(item, idx) in backups" :key="idx">
        <view class="card-top">
          <text class="card-name">{{ item.name }}</text>
          <view class="status-tag" :class="'status-' + item.status">
            <text class="status-text">{{ item.statusLabel }}</text>
          </view>
        </view>
        <view class="card-meta">
          <view class="meta-row">
            <text class="meta-label">类型</text>
            <text class="meta-value">{{ item.type }}</text>
          </view>
          <view class="meta-row">
            <text class="meta-label">大小</text>
            <text class="meta-value">{{ item.size }}</text>
          </view>
        </view>
        <text class="card-date">{{ item.date }}</text>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const isRunning = ref(false)
const progress = ref(0)

const backups = ref([
  { name: '自动备份-20260606', type: '全量备份', size: '2.3 GB', status: 'completed', statusLabel: '已完成', date: '2026-06-06 03:00' },
  { name: '手动备份-20260605', type: '增量备份', size: '456 MB', status: 'completed', statusLabel: '已完成', date: '2026-06-05 15:32' },
  { name: '自动备份-20260605', type: '全量备份', size: '2.2 GB', status: 'completed', statusLabel: '已完成', date: '2026-06-05 03:00' },
  { name: '手动备份-20260604', type: '增量备份', size: '389 MB', status: 'completed', statusLabel: '已完成', date: '2026-06-04 11:20' },
  { name: '自动备份-20260604', type: '全量备份', size: '2.1 GB', status: 'failed', statusLabel: '失败', date: '2026-06-04 03:00' },
])

function startBackup() {
  if (isRunning.value) return
  isRunning.value = true
  progress.value = 0
  const timer = setInterval(() => {
    progress.value += Math.floor(Math.random() * 12) + 3
    if (progress.value >= 100) {
      progress.value = 100
      clearInterval(timer)
      setTimeout(() => {
        isRunning.value = false
        backups.value.unshift({
          name: '手动备份-' + new Date().toISOString().slice(0, 10).replace(/-/g, ''),
          type: '全量备份', size: '2.4 GB', status: 'completed', statusLabel: '已完成',
          date: new Date().toLocaleString('zh-CN'),
        })
        uni.showToast({ title: '备份完成', icon: 'success' })
      }, 500)
    }
  }, 300)
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

.subtitle {
  font-size: 24rpx;
  color: $text-muted;
  margin-top: 4rpx;
}

.btn-primary {
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

.progress-card {
  padding: 24rpx 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid rgba(0, 229, 255, 0.3);
  margin-bottom: 20rpx;
}

.progress-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.progress-label {
  font-size: 26rpx;
  color: $neon-cyan;
  font-weight: 500;
}

.progress-pct {
  font-size: 26rpx;
  color: $neon-cyan;
  font-weight: 700;
}

.progress-track {
  height: 12rpx;
  background: rgba(0, 229, 255, 0.1);
  border-radius: 6rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $neon-cyan, $neon-purple);
  border-radius: 6rpx;
  transition: width 0.3s;
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

.card-name {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.status-tag {
  padding: 4rpx 16rpx;
  border-radius: 8rpx;

  &.status-completed { background: rgba(0, 255, 157, 0.12); }
  &.status-failed { background: rgba(255, 77, 158, 0.12); }
}

.status-text {
  font-size: 22rpx;
  font-weight: 500;
  .status-completed & { color: $neon-green; }
  .status-failed & { color: $neon-pink; }
}

.card-meta {
  display: flex;
  gap: 32rpx;
  margin-bottom: 12rpx;
}

.meta-row {
  display: flex;
  gap: 8rpx;
}

.meta-label {
  font-size: 24rpx;
  color: $text-muted;
}

.meta-value {
  font-size: 24rpx;
  color: $text-secondary;
}

.card-date {
  font-size: 22rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
