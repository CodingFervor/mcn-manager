<template>
  <view class="page">
    <view class="header">
      <text class="title">权限策略</text>
      <text class="subtitle">{{ policies.length }} 条策略</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="group" v-for="(group, gIdx) in groupedPolicies" :key="gIdx">
        <text class="group-title">{{ group.module }}</text>
        <view class="card" v-for="(item, idx) in group.items" :key="idx">
          <view class="card-row">
            <view class="card-left">
              <text class="card-name">{{ item.name }}</text>
              <view class="module-tag">
                <text class="module-tag-text">{{ item.module }}</text>
              </view>
            </view>
            <view class="switch-wrap" @tap="togglePolicy(gIdx, idx)">
              <view class="switch-track" :class="{ on: item.active }">
                <view class="switch-thumb" />
              </view>
            </view>
          </view>
          <view class="action-tags">
            <view class="action-tag" v-for="(act, ai) in item.actions" :key="ai">
              <text class="action-tag-text">{{ act }}</text>
            </view>
          </view>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'

const policies = ref([
  { name: '内容审核员', module: '内容管理', actions: ['查看', '编辑', '审核'], active: true },
  { name: '内容发布', module: '内容管理', actions: ['查看', '创建', '发布'], active: true },
  { name: '订单查看', module: '订单管理', actions: ['查看', '导出'], active: true },
  { name: '订单退款', module: '订单管理', actions: ['查看', '退款', '审核'], active: false },
  { name: '数据报表', module: '数据分析', actions: ['查看', '导出', '分享'], active: true },
  { name: '系统设置', module: '系统管理', actions: ['查看', '编辑', '删除'], active: false },
  { name: '用户管理', module: '系统管理', actions: ['查看', '创建', '编辑', '禁用'], active: true },
  { name: '财务审批', module: '财务管理', actions: ['查看', '审批', '导出'], active: false },
])

const groupedPolicies = computed(() => {
  const map = {}
  policies.value.forEach(p => {
    if (!map[p.module]) map[p.module] = { module: p.module, items: [] }
    map[p.module].items.push(p)
  })
  return Object.values(map)
})

function togglePolicy(gIdx, idx) {
  const item = groupedPolicies.value[gIdx].items[idx]
  item.active = !item.active
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

.scroll-body {
  flex: 1;
  height: 0;
  padding: 0 24rpx;
}

.group {
  margin-bottom: 16rpx;
}

.group-title {
  font-size: 26rpx;
  font-weight: 600;
  color: $neon-purple;
  padding: 16rpx 8rpx 8rpx;
}

.card {
  padding: 24rpx 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 16rpx;
}

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.card-left {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex: 1;
}

.card-name {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.module-tag {
  padding: 2rpx 12rpx;
  border-radius: 8rpx;
  background: rgba(0, 229, 255, 0.12);
}

.module-tag-text {
  font-size: 20rpx;
  color: $neon-cyan;
}

.switch-track {
  width: 80rpx;
  height: 44rpx;
  border-radius: 22rpx;
  background: rgba(107, 115, 147, 0.3);
  position: relative;
  transition: background 0.3s;

  &.on {
    background: rgba(124, 92, 255, 0.5);
  }
}

.switch-thumb {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: $text-primary;
  position: absolute;
  top: 4rpx;
  left: 4rpx;
  transition: transform 0.3s;

  .on & {
    transform: translateX(36rpx);
  }
}

.action-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.action-tag {
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  background: rgba(124, 92, 255, 0.1);
  border: 1rpx solid rgba(124, 92, 255, 0.15);
}

.action-tag-text {
  font-size: 22rpx;
  color: $text-secondary;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
