<template>
  <view class="mcn-empty">
    <text class="mcn-empty__icon">{{ icon }}</text>
    <text class="mcn-empty__text">{{ text }}</text>
  </view>
</template>

<script setup>
defineProps({
  text: {
    type: String,
    default: '暂无数据'
  },
  icon: {
    type: String,
    default: '📭'
  }
})
</script>

<style lang="scss" scoped>
.mcn-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx 40rpx;

  &__icon {
    font-size: 100rpx;
    margin-bottom: 24rpx;
    opacity: 0.7;
  }

  &__text {
    font-size: 28rpx;
    color: $text-muted;
    text-align: center;
  }
}
</style>
