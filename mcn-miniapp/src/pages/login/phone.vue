<template>
  <view class="phone-page">
    <!-- Top Section -->
    <view class="header-area">
      <view class="icon-circle">
        <text class="icon-phone">&#x1F4F1;</text>
      </view>
      <text class="page-title">绑定手机号</text>
      <text class="page-desc">绑定手机号后可关联您的员工信息</text>
    </view>

    <!-- Form Card -->
    <view class="form-card">
      <view class="input-group">
        <view class="input-wrapper" :class="{ focused: phoneFocused }">
          <text class="country-code">+86</text>
          <view class="code-divider" />
          <input
            v-model="phone"
            class="input-field"
            type="number"
            maxlength="11"
            placeholder="请输入手机号码"
            placeholder-class="placeholder"
            :focus="phoneFocused"
            @focus="phoneFocused = true"
            @blur="phoneFocused = false"
          />
        </view>
      </view>

      <!-- Bind Button -->
      <view class="bind-btn" :class="{ disabled: !canBind }" @tap="handleBind" hover-class="btn-hover">
        <text class="bind-btn-text">确认绑定</text>
      </view>
    </view>

    <!-- Skip Link -->
    <view class="skip-area" @tap="handleSkip">
      <text class="skip-text">跳过</text>
    </view>

    <!-- Loading -->
    <view v-if="loading" class="loading-overlay">
      <view class="loading-spinner" />
      <text class="loading-text">绑定中...</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { bindPhone } = useAuth()

const phone = ref('')
const phoneFocused = ref(false)
const loading = ref(false)

const canBind = computed(() => /^1\d{10}$/.test(phone.value))

async function handleBind() {
  if (!canBind.value || loading.value) return
  loading.value = true
  try {
    const res = await bindPhone(phone.value)
    if (res) {
      uni.showToast({ title: '绑定成功', icon: 'success' })
      setTimeout(() => {
        uni.switchTab({ url: '/pages/dashboard/index' })
      }, 500)
    }
  } finally {
    loading.value = false
  }
}

function handleSkip() {
  uni.switchTab({ url: '/pages/dashboard/index' })
}
</script>

<style lang="scss" scoped>
.phone-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0e27 0%, #131836 50%, #0a0e27 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 48rpx;
  padding-top: 200rpx;
  position: relative;
  overflow: hidden;
}

.phone-page::before {
  content: '';
  position: absolute;
  top: -150rpx;
  right: -100rpx;
  width: 400rpx;
  height: 400rpx;
  background: radial-gradient(circle, rgba(0, 229, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.header-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 80rpx;
  position: relative;
  z-index: 2;
}

.icon-circle {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, $neon-purple, $neon-cyan);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 36rpx;
  box-shadow: 0 12rpx 48rpx rgba(124, 92, 255, 0.3);
}

.icon-phone {
  font-size: 52rpx;
}

.page-title {
  font-size: 44rpx;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 16rpx;
}

.page-desc {
  font-size: 28rpx;
  color: $text-secondary;
  text-align: center;
  line-height: 1.6;
}

.form-card {
  width: 100%;
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

.input-group {
  margin-bottom: 40rpx;
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
    border-color: $neon-cyan;
    box-shadow: 0 0 20rpx rgba(0, 229, 255, 0.15);
  }
}

.country-code {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
  margin-right: 8rpx;
  white-space: nowrap;
}

.code-divider {
  width: 1rpx;
  height: 40rpx;
  background: rgba(124, 92, 255, 0.3);
  margin: 0 20rpx 0 12rpx;
}

.input-field {
  flex: 1;
  height: 96rpx;
  font-size: 30rpx;
  color: $text-primary;
  letter-spacing: 2rpx;
}

.placeholder {
  color: $text-muted;
  font-size: 28rpx;
}

.bind-btn {
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, $neon-purple, $neon-cyan);
  border-radius: $radius-md;
  box-shadow: 0 8rpx 32rpx rgba(124, 92, 255, 0.35);
  transition: all 0.2s;

  &.disabled {
    opacity: 0.4;
    box-shadow: none;
  }
}

.bind-btn:active:not(.disabled) {
  transform: scale(0.98);
}

.bind-btn-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
}

.btn-hover {
  opacity: 0.85;
}

.skip-area {
  margin-top: 48rpx;
  padding: 20rpx 40rpx;
  position: relative;
  z-index: 2;
}

.skip-text {
  font-size: 28rpx;
  color: $text-muted;
  text-decoration: underline;
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
