import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import echarts from '../echarts'

export function useChart(optionsFn) {
  const chartRef = ref(null)
  let chart = null
  let resizeObserver = null

  function initChart() {
    if (!chartRef.value) return
    if (chart) chart.dispose()
    chart = echarts.init(chartRef.value, null, { renderer: 'canvas' })
    const opts = typeof optionsFn === 'function' ? optionsFn() : optionsFn
    if (opts) chart.setOption(opts)
  }

  function updateChart(opts) {
    if (!chart) return
    chart.setOption(opts, { notMerge: false })
  }

  onMounted(() => {
    nextTick(initChart)
    resizeObserver = new ResizeObserver(() => chart?.resize())
    if (chartRef.value) resizeObserver.observe(chartRef.value)
  })

  onUnmounted(() => {
    resizeObserver?.disconnect()
    chart?.dispose()
    chart = null
  })

  return { chartRef, initChart, updateChart, getChart: () => chart }
}
