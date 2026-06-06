<template>
  <view class="mcn-card" :style="{ padding }">
    <view v-if="title" class="mcn-card__header">
      <text class="mcn-card__title">{{ title }}</text>
      <view class="mcn-card__underline"></view>
    </view>
    <view class="mcn-card__body">
      <slot></slot>
    </view>
  </view>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  padding: {
    type: String,
    default: '24rpx'
  }
})
</script>

<style lang="scss" scoped>
.mcn-card {
  background: $bg-card;
  border-radius: 20rpx;
  border: 1rpx solid $border-glow;
  backdrop-filter: blur(20px);
  overflow: hidden;
  transition: border-color 0.3s ease;

  &:active {
    border-color: rgba($neon-purple, 0.5);
  }

  &__header {
    margin-bottom: 20rpx;
  }

  &__title {
    font-size: 30rpx;
    font-weight: 600;
    color: $text-primary;
    display: block;
    margin-bottom: 12rpx;
  }

  &__underline {
    width: 60rpx;
    height: 4rpx;
    border-radius: 2rpx;
    background: linear-gradient(90deg, $neon-purple, $neon-pink);
    box-shadow: 0 0 10rpx rgba($neon-purple, 0.4);
  }

  &__body {
    width: 100%;
  }
}
</style>
