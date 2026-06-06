<template>
  <view class="mcn-list-item" @tap="handleTap">
    <view class="mcn-list-item__icon">
      <slot name="icon"></slot>
    </view>
    <view class="mcn-list-item__content">
      <text class="mcn-list-item__title">{{ title }}</text>
      <text v-if="subtitle" class="mcn-list-item__subtitle">{{ subtitle }}</text>
    </view>
    <view v-if="value" class="mcn-list-item__value">
      <text class="mcn-list-item__value-text">{{ value }}</text>
    </view>
    <view v-if="showArrow" class="mcn-list-item__arrow">
      <text class="mcn-list-item__arrow-icon">&#8250;</text>
    </view>
  </view>
</template>

<script setup>
const emit = defineEmits(['click'])

defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  value: {
    type: String,
    default: ''
  },
  showArrow: {
    type: Boolean,
    default: true
  }
})

const handleTap = () => {
  emit('click')
}
</script>

<style lang="scss" scoped>
.mcn-list-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: $bg-card;
  border-radius: 16rpx;
  border: 1rpx solid $border-glow;
  transition: all 0.2s ease;

  &:active {
    background: rgba($neon-purple, 0.08);
    border-color: rgba($neon-purple, 0.4);
  }

  &__icon {
    flex-shrink: 0;
    margin-right: 20rpx;
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__title {
    display: block;
    font-size: 28rpx;
    font-weight: 500;
    color: $text-primary;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__subtitle {
    display: block;
    font-size: 24rpx;
    color: $text-muted;
    margin-top: 4rpx;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__value {
    flex-shrink: 0;
    margin-right: 8rpx;
    max-width: 240rpx;
  }

  &__value-text {
    font-size: 26rpx;
    color: $text-secondary;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__arrow {
    flex-shrink: 0;
    width: 32rpx;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__arrow-icon {
    font-size: 32rpx;
    color: $text-muted;
    font-weight: 300;
  }
}
</style>
