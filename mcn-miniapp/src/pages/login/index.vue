<template>
  <view class="login-page">
    <!-- Custom Nav Bar -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <text class="nav-title">登录</text>
      </view>
    </view>

    <!-- Logo Area -->
    <view class="logo-area">
      <view class="logo-icon">
        <text class="logo-text-m">M</text>
      </view>
      <text class="app-title">MCN管家</text>
      <text class="app-subtitle">直播运营管理平台</text>
    </view>

    <!-- Glass Card Form -->
    <view class="form-card">
      <!-- WeChat Login -->
      <view class="wx-login-btn" @tap="handleWxLogin" hover-class="btn-hover">
        <text class="wx-icon">&#xe6c5;</text>
        <text class="wx-text">微信一键登录</text>
      </view>

      <!-- OR Separator -->
      <view class="separator">
        <view class="sep-line" />
        <text class="sep-text">OR</text>
        <view class="sep-line" />
      </view>

      <!-- Username -->
      <view class="input-group">
        <view class="input-wrapper" :class="{ focused: usernameFocused }">
          <text class="input-icon">&#x1F464;</text>
          <input
            v-model="username"
            class="input-field"
            type="text"
            placeholder="请输入账号"
            placeholder-class="placeholder"
            :focus="usernameFocused"
            @focus="usernameFocused = true"
            @blur="usernameFocused = false"
          />
        </view>
      </view>

      <!-- Password -->
      <view class="input-group">
        <view class="input-wrapper" :class="{ focused: passwordFocused }">
          <text class="input-icon">&#x1F512;</text>
          <input
            v-model="password"
            class="input-field"
            type="password"
            password
            placeholder="请输入密码"
            placeholder-class="placeholder"
            :focus="passwordFocused"
            @focus="passwordFocused = true"
            @blur="passwordFocused = false"
          />
        </view>
      </view>

      <!-- Password Login Button -->
      <view class="login-btn" @tap="handlePasswordLogin" hover-class="btn-hover">
        <text class="login-btn-text">账号登录</text>
      </view>
    </view>

    <!-- Loading Overlay -->
    <view v-if="loading" class="loading-overlay">
      <view class="loading-spinner" />
      <text class="loading-text">登录中...</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { wxLogin, passwordLogin } = useAuth()

const username = ref('')
const password = ref('')
const usernameFocused = ref(false)
const passwordFocused = ref(false)
const loading = ref(false)

const statusBarHeight = ref(0)

// Get status bar height
try {
  const sysInfo = uni.getSystemInfoSync()
  statusBarHeight.value = sysInfo.statusBarHeight || 20
} catch (e) {
  statusBarHeight.value = 20
}

async function handleWxLogin() {
  if (loading.value) return
  loading.value = true
  try {
    await wxLogin()
  } finally {
    loading.value = false
  }
}

async function handlePasswordLogin() {
  if (loading.value) return
  if (!username.value.trim()) {
    uni.showToast({ title: '请输入账号', icon: 'none' })
    return
  }
  if (!password.value.trim()) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }
  loading.value = true
  try {
    const ok = await passwordLogin(username.value.trim(), password.value.trim())
    if (ok) {
      uni.switchTab({ url: '/pages/dashboard/index' })
    }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0e27 0%, #131836 50%, #0a0e27 100%);
  position: relative;
  overflow: hidden;
}

// Background decoration
.login-page::before {
  content: '';
  position: absolute;
  top: -200rpx;
  left: -100rpx;
  width: 500rpx;
  height: 500rpx;
  background: radial-gradient(circle, rgba(124, 92, 255, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.login-page::after {
  content: '';
  position: absolute;
  bottom: -200rpx;
  right: -100rpx;
  width: 500rpx;
  height: 500rpx;
  background: radial-gradient(circle, rgba(255, 77, 158, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.nav-bar {
  width: 100%;
  position: relative;
  z-index: 10;
}

.nav-content {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-title {
  font-size: 34rpx;
  font-weight: 600;
  color: $text-primary;
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 60rpx;
  padding-bottom: 80rpx;
  position: relative;
  z-index: 2;
}

.logo-icon {
  width: 140rpx;
  height: 140rpx;
  border-radius: 36rpx;
  background: linear-gradient(135deg, $neon-purple, $neon-pink);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12rpx 60rpx rgba(124, 92, 255, 0.4);
  margin-bottom: 30rpx;
}

.logo-text-m {
  font-size: 72rpx;
  font-weight: 700;
  color: #fff;
}

.app-title {
  font-size: 52rpx;
  font-weight: 700;
  background: linear-gradient(135deg, $neon-purple, $neon-pink, $neon-cyan);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 40rpx rgba(124, 92, 255, 0.5);
  margin-bottom: 12rpx;
}

.app-subtitle {
  font-size: 26rpx;
  color: $text-muted;
  letter-spacing: 4rpx;
}

.form-card {
  margin: 0 48rpx;
  padding: 48rpx 40rpx;
  background: rgba(20, 24, 56, 0.65);
  border-radius: $radius-lg;
  border: 1rpx solid rgba(124, 92, 255, 0.2);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 16rpx 64rpx rgba(0, 0, 0, 0.3), inset 0 1rpx 0 rgba(255, 255, 255, 0.05);
  position: relative;
  z-index: 2;
}

.wx-login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 96rpx;
  background: linear-gradient(135deg, #07c160, #06ae56);
  border-radius: $radius-md;
  box-shadow: 0 8rpx 32rpx rgba(7, 193, 96, 0.3);
  transition: all 0.2s;
}

.wx-login-btn:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.wx-icon {
  font-size: 40rpx;
  margin-right: 12rpx;
}

.wx-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
}

.separator {
  display: flex;
  align-items: center;
  margin: 40rpx 0;
}

.sep-line {
  flex: 1;
  height: 1rpx;
  background: linear-gradient(90deg, transparent, $border-glow, transparent);
}

.sep-text {
  padding: 0 24rpx;
  font-size: 24rpx;
  color: $text-muted;
}

.input-group {
  margin-bottom: 28rpx;
}

.input-wrapper {
  display: flex;
  align-items: center;
  height: 96rpx;
  padding: 0 28rpx;
  background: rgba(10, 14, 39, 0.6);
  border-radius: $radius-md;
  border: 1rpx solid rgba(124, 92, 255, 0.15);
  transition: all 0.3s;

  &.focused {
    border-color: $neon-purple;
    box-shadow: 0 0 20rpx rgba(124, 92, 255, 0.15);
  }
}

.input-icon {
  font-size: 36rpx;
  margin-right: 16rpx;
}

.input-field {
  flex: 1;
  height: 96rpx;
  font-size: 30rpx;
  color: $text-primary;
}

.placeholder {
  color: $text-muted;
  font-size: 28rpx;
}

.login-btn {
  margin-top: 44rpx;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, $neon-purple, #9b7cff);
  border-radius: $radius-md;
  box-shadow: 0 8rpx 32rpx rgba(124, 92, 255, 0.35);
  transition: all 0.2s;
}

.login-btn:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.login-btn-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
}

.btn-hover {
  opacity: 0.85;
  transform: scale(0.98);
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(10, 14, 39, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.loading-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid rgba(124, 92, 255, 0.2);
  border-top-color: $neon-purple;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 20rpx;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 28rpx;
  color: $text-secondary;
}
</style>
