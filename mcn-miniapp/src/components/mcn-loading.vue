<template>
  <view class="mcn-loading">
    <view class="mcn-loading__spinner">
      <view class="mcn-loading__ring"></view>
    </view>
    <text class="mcn-loading__text">加载中...</text>
  </view>
</template>

<script setup>
</script>

<style lang="scss" scoped>
.mcn-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60rpx 40rpx;

  &__spinner {
    width: 64rpx;
    height: 64rpx;
    margin-bottom: 20rpx;
  }

  &__ring {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 4rpx solid rgba($neon-purple, 0.2);
    border-top-color: $neon-purple;
    animation: mcn-spin 0.8s linear infinite;
    box-shadow: 0 0 20rpx rgba($neon-purple, 0.3),
                0 0 40rpx rgba($neon-purple, 0.1);
  }

  &__text {
    font-size: 26rpx;
    color: $text-muted;
  }
}

@keyframes mcn-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
