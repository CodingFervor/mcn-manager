<script setup>
import { useChart } from '../composables/useChart'

const props = defineProps({
  optionFn: Function,
  height: { type: String, default: '320px' },
})

const { chartRef, updateChart } = useChart(props.optionFn)

defineExpose({ updateChart })
</script>

<template>
  <div ref="chartRef" :style="{ width: '100%', height }"></div>
</template>
