<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">设置</text>
    </view>

    <view class="glass-card menu-card">
      <!-- Notification Toggle -->
      <view class="menu-item" @tap="toggleNotification">
        <view class="menu-left">
          <view class="menu-icon icon-notification">
            <text class="icon-text">N</text>
          </view>
          <text class="menu-label">消息通知</text>
        </view>
        <view class="toggle-switch" :class="{ active: notificationEnabled }">
          <view class="toggle-dot"></view>
        </view>
      </view>

      <view class="menu-divider"></view>

      <!-- Clear Cache -->
      <view class="menu-item" @tap="clearCache">
        <view class="menu-left">
          <view class="menu-icon icon-cache">
            <text class="icon-text">C</text>
          </view>
          <text class="menu-label">清除缓存</text>
        </view>
        <text class="menu-value">{{ cacheSize }}</text>
      </view>

      <view class="menu-divider"></view>

      <!-- About -->
      <view class="menu-item" @tap="showAbout">
        <view class="menu-left">
          <view class="menu-icon icon-about">
            <text class="icon-text">i</text>
          </view>
          <text class="menu-label">关于MCN管家</text>
        </view>
        <text class="menu-arrow">></text>
      </view>

      <view class="menu-divider"></view>

      <!-- Privacy Policy -->
      <view class="menu-item" @tap="openPrivacy">
        <view class="menu-left">
          <view class="menu-icon icon-privacy">
            <text class="icon-text">P</text>
          </view>
          <text class="menu-label">隐私政策</text>
        </view>
        <text class="menu-arrow">></text>
      </view>

      <view class="menu-divider"></view>

      <!-- Account Info -->
      <view class="menu-item" @tap="showAccountInfo">
        <view class="menu-left">
          <view class="menu-icon icon-account">
            <text class="icon-text">U</text>
          </view>
          <text class="menu-label">账号信息</text>
        </view>
        <view class="menu-right-info">
          <text class="menu-info-text">{{ employeeName }}</text>
          <text class="menu-arrow">></text>
        </view>
      </view>
    </view>

    <!-- Logout Button -->
    <button class="btn-logout" @tap="handleLogout">退出登录</button>

    <!-- App Version -->
    <view class="version-info">
      <text class="version-text">MCN管家 v1.0.0</text>
      <text class="version-sub">MCN直播运营管理系统</text>
    </view>

    <!-- About Modal -->
    <view v-if="aboutVisible" class="modal-mask" @tap="aboutVisible = false">
      <view class="modal-content" @tap.stop>
        <text class="modal-title">关于MCN管家</text>
        <view class="modal-divider"></view>
        <view class="modal-info">
          <text class="modal-row">应用名称：MCN管家</text>
          <text class="modal-row">版本号：v1.0.0</text>
          <text class="modal-row">构建号：2025060601</text>
          <text class="modal-row">运行环境：微信小程序</text>
          <text class="modal-row">技术栈：uni-app + Vue 3</text>
        </view>
        <view class="modal-divider"></view>
        <text class="modal-desc">
          MCN管家是一款专为MCN直播运营团队打造的管理工具，涵盖直播排班、绩效考核、团队协作、费用管理等核心功能。
        </text>
        <button class="modal-btn" @tap="aboutVisible = false">确定</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { logout, employeeName } = useAuth()

const notificationEnabled = ref(true)
const cacheSize = ref('12.5 MB')
const aboutVisible = ref(false)

function toggleNotification() {
  notificationEnabled.value = !notificationEnabled.value
  uni.showToast({
    title: notificationEnabled.value ? '已开启通知' : '已关闭通知',
    icon: 'none',
  })
}

function clearCache() {
  uni.showModal({
    title: '清除缓存',
    content: `当前缓存大小 ${cacheSize.value}，确认清除？`,
    success(res) {
      if (res.confirm) {
        cacheSize.value = '0 MB'
        uni.showToast({ title: '缓存已清除', icon: 'success' })
      }
    },
  })
}

function showAbout() {
  aboutVisible.value = true
}

function openPrivacy() {
  uni.showToast({ title: '隐私政策页面', icon: 'none' })
}

function showAccountInfo() {
  uni.showToast({ title: `当前账号: ${employeeName.value || '未登录'}`, icon: 'none' })
}

function handleLogout() {
  uni.showModal({
    title: '退出登录',
    content: '确定要退出当前账号吗？',
    success(res) {
      if (res.confirm) {
        logout()
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
  padding: 20rpx 24rpx;
}

.page-header {
  margin-bottom: 24rpx;
  padding: 0 8rpx;
}

.page-title {
  font-size: 40rpx;
  font-weight: 700;
  color: $text-primary;
}

.glass-card {
  background: $bg-card;
  border: 1rpx solid $border-glow;
  border-radius: $radius-md;
  padding: 8rpx 28rpx;
  backdrop-filter: blur(20px);
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28rpx 0;

  &:active {
    opacity: 0.7;
  }
}

.menu-left {
  display: flex;
  align-items: center;
}

.menu-icon {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.icon-notification {
  background: rgba($neon-purple, 0.2);
  border: 1rpx solid rgba($neon-purple, 0.3);
}

.icon-cache {
  background: rgba($neon-cyan, 0.2);
  border: 1rpx solid rgba($neon-cyan, 0.3);
}

.icon-about {
  background: rgba($neon-green, 0.2);
  border: 1rpx solid rgba($neon-green, 0.3);
}

.icon-privacy {
  background: rgba($neon-yellow, 0.2);
  border: 1rpx solid rgba($neon-yellow, 0.3);
}

.icon-account {
  background: rgba($neon-pink, 0.2);
  border: 1rpx solid rgba($neon-pink, 0.3);
}

.icon-text {
  font-size: 26rpx;
  font-weight: 700;
  color: $text-primary;
}

.menu-label {
  font-size: 30rpx;
  color: $text-primary;
}

.menu-value {
  font-size: 26rpx;
  color: $text-muted;
}

.menu-arrow {
  font-size: 26rpx;
  color: $text-muted;
}

.menu-right-info {
  display: flex;
  align-items: center;
}

.menu-info-text {
  font-size: 26rpx;
  color: $text-secondary;
  margin-right: 8rpx;
}

.menu-divider {
  height: 1rpx;
  background: rgba(255, 255, 255, 0.04);
}

.toggle-switch {
  width: 88rpx;
  height: 48rpx;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.1);
  border: 1rpx solid rgba(255, 255, 255, 0.15);
  position: relative;
  transition: all 0.3s ease;

  &.active {
    background: rgba($neon-purple, 0.4);
    border-color: rgba($neon-purple, 0.6);
  }
}

.toggle-dot {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: $text-secondary;
  position: absolute;
  top: 3rpx;
  left: 3rpx;
  transition: all 0.3s ease;

  .toggle-switch.active & {
    left: 44rpx;
    background: $neon-purple;
    box-shadow: 0 0 16rpx rgba($neon-purple, 0.5);
  }
}

.btn-logout {
  margin-top: 40rpx;
  background: rgba($neon-pink, 0.15);
  border: 1rpx solid rgba($neon-pink, 0.4);
  color: $neon-pink;
  font-size: 30rpx;
  font-weight: 600;
  border-radius: $radius-sm;
  padding: 24rpx;
  text-align: center;

  &::after {
    border: none;
  }

  &:active {
    background: rgba($neon-pink, 0.3);
  }
}

.version-info {
  margin-top: 40rpx;
  text-align: center;
  padding-bottom: 60rpx;
}

.version-text {
  font-size: 24rpx;
  color: $text-muted;
  display: block;
  margin-bottom: 8rpx;
}

.version-sub {
  font-size: 20rpx;
  color: rgba($text-muted, 0.6);
}

/* Modal */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-content {
  width: 600rpx;
  background: $bg-secondary;
  border: 1rpx solid $border-glow;
  border-radius: $radius-lg;
  padding: 40rpx;
  backdrop-filter: blur(40px);
}

.modal-title {
  font-size: 34rpx;
  font-weight: 700;
  color: $text-primary;
  display: block;
  text-align: center;
  margin-bottom: 24rpx;
}

.modal-divider {
  height: 1rpx;
  background: $border-glow;
  margin: 20rpx 0;
}

.modal-info {
  padding: 8rpx 0;
}

.modal-row {
  font-size: 26rpx;
  color: $text-secondary;
  display: block;
  line-height: 2;
}

.modal-desc {
  font-size: 24rpx;
  color: $text-muted;
  line-height: 1.6;
  display: block;
}

.modal-btn {
  margin-top: 32rpx;
  background: linear-gradient(135deg, $neon-purple, $neon-pink);
  color: #fff;
  font-size: 28rpx;
  font-weight: 600;
  border-radius: $radius-sm;
  border: none;

  &::after {
    border: none;
  }
}
</style>
