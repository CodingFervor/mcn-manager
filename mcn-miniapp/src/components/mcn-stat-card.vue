<template>
  <view class="mcn-stat-card" :style="{ '--accent': color }">
    <view class="mcn-stat-card__icon">
      <text class="mcn-stat-card__emoji">{{ icon }}</text>
    </view>
    <view class="mcn-stat-card__content">
      <text class="mcn-stat-card__label">{{ label }}</text>
      <text class="mcn-stat-card__value">{{ value }}</text>
    </view>
    <view v-if="trend !== undefined && trend !== null" class="mcn-stat-card__trend" :class="trendClass">
      <text class="mcn-stat-card__trend-arrow">{{ trend >= 0 ? '&#9650;' : '&#9660;' }}</text>
      <text class="mcn-stat-card__trend-value">{{ Math.abs(trend) }}%</text>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  value: {
    type: [String, Number],
    default: ''
  },
  trend: {
    type: Number,
    default: undefined
  },
  color: {
    type: String,
    default: '#7c5cff'
  }
})

const trendClass = computed(() => {
  if (props.trend >= 0) return 'mcn-stat-card__trend--up'
  return 'mcn-stat-card__trend--down'
})
</script>

<style lang="scss" scoped>
.mcn-stat-card {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: $bg-card;
  border-radius: 20rpx;
  border: 1rpx solid $border-glow;
  backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4rpx;
    height: 100%;
    background: var(--accent, $neon-purple);
    border-radius: 0 2rpx 2rpx 0;
    box-shadow: 0 0 12rpx var(--accent, $neon-purple);
  }

  &__icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 16rpx;
    background: rgba(124, 92, 255, 0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    flex-shrink: 0;
  }

  &__emoji {
    font-size: 40rpx;
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__label {
    display: block;
    font-size: 24rpx;
    color: $text-secondary;
    margin-bottom: 6rpx;
  }

  &__value {
    display: block;
    font-size: 36rpx;
    font-weight: 700;
    color: $text-primary;
  }

  &__trend {
    display: flex;
    align-items: center;
    padding: 6rpx 14rpx;
    border-radius: 20rpx;
    font-size: 22rpx;
    font-weight: 600;
    flex-shrink: 0;

    &--up {
      background: rgba($neon-green, 0.12);
      color: $neon-green;
    }

    &--down {
      background: rgba($neon-pink, 0.12);
      color: $neon-pink;
    }

    &-arrow {
      margin-right: 4rpx;
      font-size: 20rpx;
    }

    &-value {
      font-size: 22rpx;
    }
  }
}
</style>
