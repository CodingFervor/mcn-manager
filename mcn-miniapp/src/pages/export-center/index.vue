<template>
  <view class="page">
    <view class="header">
      <view class="header-left">
        <text class="title">导出中心</text>
      </view>
      <view class="btn-primary" @tap="createExport">
        <text class="btn-text">新建导出</text>
      </view>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in exports" :key="idx">
        <view class="card-top">
          <view class="card-left">
            <text class="card-name">{{ item.name }}</text>
          </view>
          <view class="status-tag" :class="'tag-' + item.status">
            <text class="status-text">{{ item.statusLabel }}</text>
          </view>
        </view>
        <view class="card-meta">
          <text class="meta-type">{{ item.type }}</text>
          <text class="meta-sep">|</text>
          <text class="meta-size">{{ item.size }}</text>
          <text class="meta-sep">|</text>
          <text class="meta-date">{{ item.date }}</text>
        </view>
        <view v-if="item.status === 'completed'" class="card-actions">
          <view class="btn-download" @tap="download(idx)">
            <text class="dl-text">下载文件</text>
          </view>
        </view>
        <view v-else-if="item.status === 'processing'" class="progress-wrap">
          <view class="progress-track">
            <view class="progress-fill" :style="{ width: item.progress + '%' }" />
          </view>
          <text class="progress-text">{{ item.progress }}%</text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const exports = ref([
  { name: '6月销售数据', type: 'Excel', size: '12.3 MB', date: '2026-06-06', status: 'completed', statusLabel: '已完成', progress: 100 },
  { name: '用户画像报告', type: 'PDF', size: '8.7 MB', date: '2026-06-05', status: 'completed', statusLabel: '已完成', progress: 100 },
  { name: '库存盘点表', type: 'Excel', size: '-', date: '2026-06-06', status: 'processing', statusLabel: '处理中', progress: 67 },
  { name: '直播数据汇总', type: 'CSV', size: '-', date: '2026-06-06', status: 'processing', statusLabel: '处理中', progress: 23 },
  { name: '财务月报', type: 'PDF', size: '-', date: '2026-06-06', status: 'queued', statusLabel: '排队中', progress: 0 },
  { name: '5月绩效数据', type: 'Excel', size: '15.1 MB', date: '2026-06-01', status: 'completed', statusLabel: '已完成', progress: 100 },
  { name: '客户分析报告', type: 'PDF', size: '-', date: '2026-06-04', status: 'failed', statusLabel: '失败', progress: 0 },
])

function download(idx) {
  uni.showToast({ title: '开始下载...', icon: 'success' })
}

function createExport() {
  uni.showToast({ title: '请选择导出类型', icon: 'none' })
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

.status-tag {
  padding: 4rpx 16rpx;
  border-radius: 8rpx;

  &.tag-completed { background: rgba(0, 255, 157, 0.12); }
  &.tag-processing { background: rgba(0, 229, 255, 0.12); }
  &.tag-queued { background: rgba(255, 210, 63, 0.12); }
  &.tag-failed { background: rgba(255, 77, 158, 0.12); }
}

.status-text {
  font-size: 22rpx;
  font-weight: 500;
  .tag-completed & { color: $neon-green; }
  .tag-processing & { color: $neon-cyan; }
  .tag-queued & { color: $neon-yellow; }
  .tag-failed & { color: $neon-pink; }
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.meta-type {
  font-size: 24rpx;
  color: $text-secondary;
}

.meta-sep {
  font-size: 24rpx;
  color: $text-muted;
}

.meta-size {
  font-size: 24rpx;
  color: $text-secondary;
}

.meta-date {
  font-size: 24rpx;
  color: $text-muted;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-download {
  padding: 10rpx 24rpx;
  background: rgba(0, 255, 157, 0.12);
  border: 1rpx solid rgba(0, 255, 157, 0.3);
  border-radius: $radius-sm;
}

.dl-text {
  font-size: 24rpx;
  color: $neon-green;
  font-weight: 500;
}

.progress-wrap {
  display: flex;
  align-items: center;
  gap: 12rpx;
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

.progress-text {
  font-size: 22rpx;
  color: $neon-cyan;
  font-weight: 600;
  min-width: 60rpx;
  text-align: right;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
