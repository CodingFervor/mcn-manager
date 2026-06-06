<template>
  <view class="profile-page">
    <scroll-view scroll-y class="scroll-body">
      <!-- Profile Header -->
      <view class="profile-header">
        <view class="avatar-circle">
          <text class="avatar-text">{{ avatarLetter }}</text>
        </view>
        <view class="profile-info">
          <text class="profile-name">{{ employeeName }}</text>
          <text class="profile-role">{{ employeeRole || '主播' }}</text>
          <text class="profile-team">{{ employeeTeam }}</text>
        </view>
      </view>

      <!-- Stats Row -->
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-value">¥8.6万</text>
          <text class="stat-label">本月GMV</text>
        </view>
        <view class="stat-divider" />
        <view class="stat-item">
          <text class="stat-value">24</text>
          <text class="stat-label">直播场次</text>
        </view>
        <view class="stat-divider" />
        <view class="stat-item">
          <text class="stat-value">96.8%</text>
          <text class="stat-label">出勤率</text>
        </view>
      </view>

      <!-- Menu List -->
      <view class="menu-section">
        <text class="menu-section-title">直播管理</text>
        <view class="menu-card">
          <view class="menu-item" v-for="(item, idx) in liveMenus" :key="idx" @tap="navigateTo(item.path)">
            <view class="menu-left">
              <text class="menu-icon">{{ item.icon }}</text>
              <text class="menu-title">{{ item.title }}</text>
            </view>
            <text class="menu-arrow">></text>
          </view>
        </view>
      </view>

      <view class="menu-section">
        <text class="menu-section-title">运营工具</text>
        <view class="menu-card">
          <view class="menu-item" v-for="(item, idx) in opsMenus" :key="idx" @tap="navigateTo(item.path)">
            <view class="menu-left">
              <text class="menu-icon">{{ item.icon }}</text>
              <text class="menu-title">{{ item.title }}</text>
            </view>
            <text class="menu-arrow">></text>
          </view>
        </view>
      </view>

      <view class="menu-section">
        <text class="menu-section-title">个人中心</text>
        <view class="menu-card">
          <view class="menu-item" v-for="(item, idx) in personalMenus" :key="idx" @tap="navigateTo(item.path)">
            <view class="menu-left">
              <text class="menu-icon">{{ item.icon }}</text>
              <text class="menu-title">{{ item.title }}</text>
            </view>
            <text class="menu-arrow">></text>
          </view>
        </view>
      </view>

      <!-- Logout Button -->
      <view class="logout-area">
        <view class="logout-btn" @tap="handleLogout" hover-class="btn-hover">
          <text class="logout-text">退出登录</text>
        </view>
      </view>

      <!-- Version -->
      <view class="version-area">
        <text class="version-text">MCN管家 v2.1.0</text>
      </view>

      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useAuth } from '@/composables/useAuth'

const authStore = useAuthStore()
const { logout } = useAuth()

const employeeName = ref('未登录')
const employeeRole = ref('')
const employeeTeam = ref('')

const avatarLetter = computed(() => {
  const name = employeeName.value
  if (!name || name === '未登录') return 'M'
  return name.charAt(0)
})

const liveMenus = [
  { icon: '\u{1F4FA}', title: '直播记录', path: '/pages/sessions/index' },
  { icon: '\u{1F4CB}', title: '任务看板', path: '/pages/tasks/index' },
  { icon: '\u{1F514}', title: '消息中心', path: '/pages/notifications/index' },
  { icon: '\u{1F4C5}', title: '直播预告', path: '/pages/stream-plans/index' },
]

const opsMenus = [
  { icon: '\u{1F6D2}', title: '商品浏览', path: '/pages/products/index' },
  { icon: '\u{1F4E6}', title: '订单管理', path: '/pages/orders/index' },
  { icon: '\u{1F3AF}', title: '销售目标', path: '/pages/sales-targets/index' },
  { icon: '\u{1F4B0}', title: '财务概览', path: '/pages/finance/index' },
]

const personalMenus = [
  { icon: '\u{1F4DA}', title: '知识库', path: '/pages/knowledge/index' },
  { icon: '\u{1F393}', title: '培训课程', path: '/pages/training/index' },
  { icon: '\u{1F4CA}', title: '绩效考核', path: '/pages/performance/index' },
  { icon: '\u{1F4B3}', title: '费用报销', path: '/pages/expenses/index' },
  { icon: '\u{1F3D7}', title: '请假申请', path: '/pages/leave/index' },
  { icon: '\u{1F4AC}', title: '团队沟通', path: '/pages/team-chat/index' },
  { icon: '\u{1F4DE}', title: '客户投诉', path: '/pages/complaints/index' },
  { icon: '\u2699\uFE0F', title: '设置', path: '/pages/settings/index' },
]

onShow(() => {
  employeeName.value = authStore.employeeName || '未登录'
  employeeRole.value = authStore.employeeRole || ''
  const emp = authStore.employee
  if (emp) {
    employeeTeam.value = emp.team_name || emp.department_name || ''
  }
})

function navigateTo(path) {
  uni.navigateTo({
    url: path,
    fail() {
      uni.showToast({ title: '页面开发中', icon: 'none' })
    },
  })
}

function handleLogout() {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    confirmColor: '#7c5cff',
    success(res) {
      if (res.confirm) {
        logout()
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.profile-page {
  min-height: 100vh;
  background: $bg-primary;
  display: flex;
  flex-direction: column;
}

.scroll-body {
  flex: 1;
  height: 0;
}

// Profile Header
.profile-header {
  display: flex;
  align-items: center;
  padding: 32rpx;
  background: linear-gradient(180deg, rgba(124, 92, 255, 0.1) 0%, transparent 100%);
}

.avatar-circle {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, $neon-purple, $neon-pink);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 28rpx;
  flex-shrink: 0;
  box-shadow: 0 8rpx 32rpx rgba(124, 92, 255, 0.3);
}

.avatar-text {
  font-size: 48rpx;
  font-weight: 700;
  color: #fff;
}

.profile-info {
  display: flex;
  flex-direction: column;
}

.profile-name {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 4rpx;
}

.profile-role {
  font-size: 26rpx;
  color: $neon-cyan;
  margin-bottom: 4rpx;
}

.profile-team {
  font-size: 24rpx;
  color: $text-muted;
}

// Stats Row
.stats-row {
  display: flex;
  align-items: center;
  margin: 16rpx 24rpx 0;
  padding: 28rpx 20rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 32rpx;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 6rpx;
}

.stat-label {
  font-size: 22rpx;
  color: $text-muted;
}

.stat-divider {
  width: 1rpx;
  height: 60rpx;
  background: rgba(124, 92, 255, 0.15);
}

// Menu Sections
.menu-section {
  margin-top: 28rpx;
  padding: 0 24rpx;
}

.menu-section-title {
  font-size: 24rpx;
  color: $text-muted;
  margin-bottom: 12rpx;
  padding-left: 8rpx;
  display: block;
}

.menu-card {
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 28rpx;
  border-bottom: 1rpx solid rgba(124, 92, 255, 0.08);
  transition: background 0.2s;

  &:last-child {
    border-bottom: none;
  }

  &:active {
    background: rgba(124, 92, 255, 0.05);
  }
}

.menu-left {
  display: flex;
  align-items: center;
}

.menu-icon {
  font-size: 36rpx;
  margin-right: 20rpx;
}

.menu-title {
  font-size: 28rpx;
  color: $text-primary;
}

.menu-arrow {
  font-size: 28rpx;
  color: $text-muted;
}

// Logout
.logout-area {
  margin: 40rpx 24rpx 0;
}

.logout-btn {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 77, 158, 0.08);
  border: 1rpx solid rgba(255, 77, 158, 0.2);
  border-radius: $radius-md;
  transition: all 0.2s;

  &:active {
    background: rgba(255, 77, 158, 0.15);
  }
}

.logout-text {
  font-size: 30rpx;
  font-weight: 500;
  color: $neon-pink;
}

.btn-hover {
  opacity: 0.85;
}

// Version
.version-area {
  display: flex;
  justify-content: center;
  padding: 32rpx 0 16rpx;
}

.version-text {
  font-size: 22rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
