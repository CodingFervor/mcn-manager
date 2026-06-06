<template>
  <view class="page">
    <view class="header">
      <text class="title">白标配置</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <!-- Preview Card -->
      <view class="preview-card">
        <text class="preview-label">品牌预览</text>
        <view class="preview-body" :style="{ borderColor: brand.primaryColor }">
          <view class="preview-logo" :style="{ background: brand.primaryColor }">
            <text class="logo-text">{{ brand.logoText }}</text>
          </view>
          <text class="preview-name" :style="{ color: brand.primaryColor }">{{ brand.brandName }}</text>
          <view class="preview-bar">
            <view class="bar-item" :style="{ background: brand.primaryColor }" />
            <view class="bar-item" :style="{ background: brand.secondaryColor }" />
            <view class="bar-item" :style="{ background: brand.accentColor }" />
          </view>
          <text class="preview-domain">{{ brand.domain }}</text>
        </view>
      </view>
      <!-- Config -->
      <view class="config-section">
        <text class="section-title">品牌设置</text>
        <view class="field">
          <text class="field-label">品牌名称</text>
          <input class="field-input" v-model="brand.brandName" placeholder="输入品牌名称" />
        </view>
        <view class="field">
          <text class="field-label">Logo文字</text>
          <input class="field-input" v-model="brand.logoText" placeholder="输入Logo文字" />
        </view>
        <view class="field">
          <text class="field-label">主色调</text>
          <view class="color-row">
            <view class="color-dot" :style="{ background: brand.primaryColor }" />
            <input class="field-input flex-1" v-model="brand.primaryColor" placeholder="#7c5cff" />
          </view>
        </view>
        <view class="field">
          <text class="field-label">辅助色</text>
          <view class="color-row">
            <view class="color-dot" :style="{ background: brand.secondaryColor }" />
            <input class="field-input flex-1" v-model="brand.secondaryColor" placeholder="#00e5ff" />
          </view>
        </view>
        <view class="field">
          <text class="field-label">强调色</text>
          <view class="color-row">
            <view class="color-dot" :style="{ background: brand.accentColor }" />
            <input class="field-input flex-1" v-model="brand.accentColor" placeholder="#ff4d9e" />
          </view>
        </view>
        <view class="field">
          <text class="field-label">绑定域名</text>
          <input class="field-input" v-model="brand.domain" placeholder="app.example.com" />
        </view>
      </view>
      <view class="btn-save" @tap="saveConfig">
        <text class="save-text">保存配置</text>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const brand = ref({
  brandName: 'MCN管家',
  logoText: 'MCN',
  primaryColor: '#7c5cff',
  secondaryColor: '#00e5ff',
  accentColor: '#ff4d9e',
  domain: 'app.mcnguanjia.com',
})

function saveConfig() {
  uni.showToast({ title: '配置已保存', icon: 'success' })
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

.scroll-body {
  flex: 1;
  height: 0;
  padding: 0 24rpx;
}

.preview-card {
  padding: 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 24rpx;
}

.preview-label {
  font-size: 24rpx;
  color: $text-muted;
  margin-bottom: 16rpx;
  display: block;
}

.preview-body {
  padding: 32rpx;
  background: rgba(10, 14, 39, 0.8);
  border-radius: $radius-sm;
  border: 2rpx dashed;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.preview-logo {
  width: 96rpx;
  height: 96rpx;
  border-radius: $radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 36rpx;
  font-weight: 700;
  color: #fff;
}

.preview-name {
  font-size: 32rpx;
  font-weight: 700;
}

.preview-bar {
  display: flex;
  gap: 12rpx;
  margin-top: 8rpx;
}

.bar-item {
  width: 48rpx;
  height: 16rpx;
  border-radius: 8rpx;
}

.preview-domain {
  font-size: 22rpx;
  color: $text-muted;
}

.config-section {
  padding: 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 20rpx;
  display: block;
}

.field {
  margin-bottom: 20rpx;
}

.field-label {
  font-size: 24rpx;
  color: $text-secondary;
  margin-bottom: 8rpx;
  display: block;
}

.field-input {
  padding: 16rpx 20rpx;
  background: rgba(10, 14, 39, 0.6);
  border: 1rpx solid rgba(124, 92, 255, 0.15);
  border-radius: $radius-sm;
  font-size: 26rpx;
  color: $text-primary;
}

.flex-1 {
  flex: 1;
}

.color-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.color-dot {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  flex-shrink: 0;
  border: 2rpx solid rgba(255, 255, 255, 0.2);
}

.btn-save {
  padding: 24rpx;
  background: linear-gradient(135deg, $neon-purple, #9b7cff);
  border-radius: $radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
}

.save-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #fff;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
