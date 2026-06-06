<template>
  <view class="mcn-status-tag" :class="statusClass">
    <text class="mcn-status-tag__text">{{ displayText }}</text>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: ''
  },
  text: {
    type: String,
    default: ''
  }
})

const statusMap = {
  active: 'status-active',
  online: 'status-active',
  enabled: 'status-active',
  live: 'status-active',
  pending: 'status-pending',
  waiting: 'status-pending',
  review: 'status-pending',
  inactive: 'status-inactive',
  offline: 'status-inactive',
  disabled: 'status-inactive',
  closed: 'status-inactive',
  danger: 'status-danger',
  error: 'status-danger',
  failed: 'status-danger',
  rejected: 'status-danger',
  expired: 'status-danger'
}

const statusClass = computed(() => {
  return statusMap[props.status] || 'status-inactive'
})

const displayText = computed(() => {
  return props.text || props.status
})
</script>

<style lang="scss" scoped>
.mcn-status-tag {
  display: inline-flex;
  align-items: center;
  padding: 6rpx 18rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 500;

  &__text {
    font-size: 22rpx;
    color: inherit;
  }
}

.status-active {
  background: rgba($neon-green, 0.12);
  color: $neon-green;
  border: 1rpx solid rgba($neon-green, 0.25);

  &::before {
    content: '';
    display: inline-block;
    width: 10rpx;
    height: 10rpx;
    border-radius: 50%;
    background: $neon-green;
    margin-right: 8rpx;
    box-shadow: 0 0 8rpx $neon-green;
  }
}

.status-pending {
  background: rgba($neon-yellow, 0.12);
  color: $neon-yellow;
  border: 1rpx solid rgba($neon-yellow, 0.25);
}

.status-inactive {
  background: rgba($text-muted, 0.12);
  color: $text-muted;
  border: 1rpx solid rgba($text-muted, 0.25);
}

.status-danger {
  background: rgba($neon-pink, 0.12);
  color: $neon-pink;
  border: 1rpx solid rgba($neon-pink, 0.25);
}
</style>
