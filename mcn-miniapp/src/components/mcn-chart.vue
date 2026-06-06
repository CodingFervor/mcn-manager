<template>
  <view class="mcn-chart">
    <canvas
      :canvas-id="canvasId"
      :id="canvasId"
      class="mcn-chart__canvas"
      :style="{ height: height }"
    ></canvas>
    <view v-if="placeholder" class="mcn-chart__placeholder">
      <text class="mcn-chart__placeholder-icon">&#128202;</text>
      <text class="mcn-chart__placeholder-text">{{ type }} chart</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'line',
    validator: (val) => ['line', 'bar', 'pie'].includes(val)
  },
  data: {
    type: Object,
    default: () => ({})
  },
  height: {
    type: String,
    default: '400rpx'
  }
})

const canvasId = ref(`mcn-chart-${Date.now()}`)
const placeholder = ref(true)

const renderChart = () => {
  // Stub: actual chart rendering with uCharts or custom canvas drawing
  // will be implemented here. For now we show the canvas placeholder.
  //
  // Example integration point:
  // const ctx = uni.createCanvasContext(canvasId.value)
  // ... draw chart based on props.type and props.data
  // ctx.draw()
  //
  // Or with uCharts:
  // new uCharts({
  //   type: props.type,
  //   canvas: canvasId.value,
  //   canvas2d: true,
  //   ...props.data
  // })

  placeholder.value = true
}

watch(() => props.data, () => {
  nextTick(() => {
    renderChart()
  })
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    renderChart()
  })
})

defineExpose({
  renderChart
})
</script>

<style lang="scss" scoped>
.mcn-chart {
  position: relative;
  width: 100%;
  background: $bg-card;
  border-radius: 20rpx;
  border: 1rpx solid $border-glow;
  overflow: hidden;

  &__canvas {
    width: 100%;
    display: block;
  }

  &__placeholder {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    pointer-events: none;
  }

  &__placeholder-icon {
    font-size: 64rpx;
    margin-bottom: 12rpx;
    opacity: 0.5;
  }

  &__placeholder-text {
    font-size: 24rpx;
    color: $text-muted;
  }
}
</style>
