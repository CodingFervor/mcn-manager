<template>
  <view class="page">
    <view class="header">
      <text class="title">审计日志</text>
    </view>
    <view class="filter-bar">
      <picker mode="date" @change="onDateChange">
        <view class="filter-btn">
          <text class="filter-text">{{ dateFilter || '选择日期' }}</text>
        </view>
      </picker>
      <view class="filter-btn" @tap="toggleActionFilter">
        <text class="filter-text">{{ actionFilter || '操作类型' }}</text>
      </view>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in logs" :key="idx">
        <view class="card-header">
          <view class="user-info">
            <view class="avatar">
              <text class="avatar-text">{{ item.user.slice(0, 1) }}</text>
            </view>
            <text class="user-name">{{ item.user }}</text>
          </view>
          <text class="log-time">{{ item.time }}</text>
        </view>
        <view class="card-body">
          <view class="log-row">
            <text class="log-label">操作</text>
            <view class="action-badge" :class="'action-' + item.actionType">
              <text class="action-text">{{ item.action }}</text>
            </view>
          </view>
          <view class="log-row">
            <text class="log-label">资源</text>
            <text class="log-value">{{ item.resource }}</text>
          </view>
          <view class="log-row">
            <text class="log-label">IP地址</text>
            <text class="log-value log-ip">{{ item.ip }}</text>
          </view>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const dateFilter = ref('')
const actionFilter = ref('')

const logs = ref([
  { user: '张三', action: '登录系统', actionType: 'read', resource: '系统登录', time: '2026-06-06 09:12:33', ip: '192.168.1.101' },
  { user: '李四', action: '修改配置', actionType: 'update', resource: '系统配置/邮件服务', time: '2026-06-06 09:08:15', ip: '192.168.1.102' },
  { user: '王五', action: '删除用户', actionType: 'delete', resource: '用户管理/测试账号', time: '2026-06-06 08:55:42', ip: '10.0.0.55' },
  { user: '赵六', action: '导出报表', actionType: 'read', resource: '数据报表/月度销售', time: '2026-06-06 08:30:07', ip: '192.168.1.200' },
  { user: '张三', action: '创建角色', actionType: 'create', resource: '权限管理/运营主管', time: '2026-06-05 17:22:58', ip: '192.168.1.101' },
  { user: '钱七', action: '审批退款', actionType: 'update', resource: '订单管理/ORD-20260605', time: '2026-06-05 16:45:30', ip: '10.0.0.88' },
  { user: '李四', action: '修改密码', actionType: 'update', resource: '账户安全', time: '2026-06-05 14:10:22', ip: '192.168.1.102' },
])

function onDateChange(e) {
  dateFilter.value = e.detail.value
}

function toggleActionFilter() {
  const actions = ['', '登录', '修改', '删除', '创建', '导出']
  const curIdx = actions.indexOf(actionFilter.value)
  actionFilter.value = actions[(curIdx + 1) % actions.length]
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

.filter-bar {
  display: flex;
  padding: 0 24rpx 16rpx;
  gap: 16rpx;
}

.filter-btn {
  padding: 10rpx 24rpx;
  border-radius: $radius-sm;
  background: rgba(124, 92, 255, 0.08);
  border: 1rpx solid rgba(124, 92, 255, 0.15);
}

.filter-text {
  font-size: 24rpx;
  color: $text-secondary;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.avatar {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: rgba(124, 92, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 22rpx;
  font-weight: 600;
  color: $neon-purple;
}

.user-name {
  font-size: 28rpx;
  font-weight: 500;
  color: $text-primary;
}

.log-time {
  font-size: 22rpx;
  color: $text-muted;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.log-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.log-label {
  font-size: 24rpx;
  color: $text-muted;
  min-width: 80rpx;
}

.log-value {
  font-size: 24rpx;
  color: $text-secondary;
}

.log-ip {
  font-family: monospace;
  font-size: 22rpx;
  color: $neon-cyan;
}

.action-badge {
  padding: 2rpx 14rpx;
  border-radius: 8rpx;

  &.action-create { background: rgba(0, 255, 157, 0.12); }
  &.action-read { background: rgba(0, 229, 255, 0.12); }
  &.action-update { background: rgba(255, 210, 63, 0.12); }
  &.action-delete { background: rgba(255, 77, 158, 0.12); }
}

.action-text {
  font-size: 22rpx;
  font-weight: 500;

  .action-create & { color: $neon-green; }
  .action-read & { color: $neon-cyan; }
  .action-update & { color: $neon-yellow; }
  .action-delete & { color: $neon-pink; }
}

.bottom-spacer {
  height: 40rpx;
}
</style>
