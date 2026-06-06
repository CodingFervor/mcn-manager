<template>
  <view class="mcn-clock-btn">
    <view
      class="mcn-clock-btn__button"
      :class="buttonClass"
      @tap="handleClick"
    >
      <view class="mcn-clock-btn__glow"></view>
      <view class="mcn-clock-btn__inner">
        <text class="mcn-clock-btn__time">{{ time }}</text>
        <text class="mcn-clock-btn__label">{{ labelText }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: 'in',
    validator: (val) => ['in', 'out', 'done'].includes(val)
  },
  time: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['click'])

const labelText = computed(() => {
  const map = {
    in: '上班打卡',
    out: '下班打卡',
    done: '已完成'
  }
  return map[props.status] || '上班打卡'
})

const buttonClass = computed(() => {
  return `mcn-clock-btn__button--${props.status}`
})

const handleClick = () => {
  if (props.status !== 'done') {
    emit('click')
  }
}
</script>

<style lang="scss" scoped>
.mcn-clock-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx;

  &__button {
    position: relative;
    width: 280rpx;
    height: 280rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: visible;
    transition: transform 0.2s ease;

    &:active {
      transform: scale(0.95);
    }

    &--in {
      background: linear-gradient(135deg, $neon-purple, $neon-pink);
      box-shadow: 0 0 40rpx rgba($neon-purple, 0.4),
                  0 0 80rpx rgba($neon-purple, 0.2);

      & .mcn-clock-btn__glow {
        border-color: rgba($neon-purple, 0.3);
        animation: mcn-pulse-glow 2s ease-in-out infinite;
      }
    }

    &--out {
      background: linear-gradient(135deg, $neon-cyan, $neon-purple);
      box-shadow: 0 0 40rpx rgba($neon-cyan, 0.4),
                  0 0 80rpx rgba($neon-cyan, 0.2);

      & .mcn-clock-btn__glow {
        border-color: rgba($neon-cyan, 0.3);
        animation: mcn-pulse-glow 2s ease-in-out infinite;
      }
    }

    &--done {
      background: linear-gradient(135deg, $bg-secondary, darken(#131836, 3%));
      box-shadow: 0 0 20rpx rgba($text-muted, 0.15);

      & .mcn-clock-btn__glow {
        border-color: rgba($text-muted, 0.15);
        animation: none;
      }
    }
  }

  &__glow {
    position: absolute;
    top: -12rpx;
    left: -12rpx;
    right: -12rpx;
    bottom: -12rpx;
    border-radius: 50%;
    border: 2rpx solid rgba($neon-purple, 0.3);
  }

  &__inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    z-index: 1;
  }

  &__time {
    font-size: 44rpx;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 8rpx;
  }

  &__label {
    font-size: 26rpx;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.85);
    letter-spacing: 2rpx;
  }

  &__button--done &__time,
  &__button--done &__label {
    color: $text-muted;
  }
}

@keyframes mcn-pulse-glow {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.06);
    opacity: 0.6;
  }
}
</style>
