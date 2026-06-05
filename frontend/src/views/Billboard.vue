<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import echarts from '../echarts'
import { BillboardAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const data = ref(null)
const chartRef1 = ref(null)
const chartRef2 = ref(null)
let charts = []
let timer = null

async function load() {
  data.value = await BillboardAPI.data()
  if (data.value) renderCharts()
}

function renderCharts() {
  charts.forEach(c => c.dispose())
  charts = []

  if (chartRef1.value && data.value.trend_7d?.length) {
    const c1 = echarts.init(chartRef1.value)
    charts.push(c1)
    c1.setOption({
      backgroundColor: 'transparent',
      title: { text: '7天GMV趋势', textStyle: { color: '#fff', fontSize: 16 } },
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(20,24,56,0.95)', borderColor: 'rgba(124,92,255,0.3)', textStyle: { color: '#fff' } },
      grid: { top: 50, right: 20, bottom: 30, left: 60 },
      xAxis: { type: 'category', data: data.value.trend_7d.map(t => t.d), axisLabel: { color: '#6b7393' }, axisLine: { lineStyle: { color: 'rgba(124,92,255,0.2)' } } },
      yAxis: { type: 'value', axisLabel: { color: '#6b7393', formatter: v => (v/10000).toFixed(0) + '万' }, splitLine: { lineStyle: { color: 'rgba(124,92,255,0.1)' } } },
      series: [{ type: 'line', data: data.value.trend_7d.map(t => t.gmv), smooth: true, lineStyle: { color: '#00e5ff', width: 3 }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,229,255,0.4)' }, { offset: 1, color: 'rgba(0,229,255,0)' }] } }, itemStyle: { color: '#00e5ff' } }],
    })
  }

  if (chartRef2.value && data.value.platform_dist?.length) {
    const c2 = echarts.init(chartRef2.value)
    charts.push(c2)
    c2.setOption({
      backgroundColor: 'transparent',
      title: { text: '平台GMV分布', textStyle: { color: '#fff', fontSize: 16 } },
      tooltip: { trigger: 'item', backgroundColor: 'rgba(20,24,56,0.95)', borderColor: 'rgba(124,92,255,0.3)', textStyle: { color: '#fff' } },
      series: [{ type: 'pie', radius: ['40%', '70%'], data: data.value.platform_dist.map(p => ({ name: p.platform || p.store__platform, value: p.gmv })), label: { color: '#a8b2d1' }, emphasis: { itemStyle: { shadowBlur: 20, shadowColor: 'rgba(124,92,255,0.5)' } } }],
    })
  }
}

onMounted(() => { load(); timer = setInterval(load, 30000) })
onUnmounted(() => { if (timer) clearInterval(timer); charts.forEach(c => c.dispose()) })
</script>

<template>
  <div class="page">
    <PageHeader title="实时大屏" subtitle="TV投屏 · 实时数据 · 自动刷新(30s)" />
    <div v-if="data" style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px">
      <div class="stat-card g1"><span class="stat-icon">💰</span><div class="stat-label">月度GMV</div><div class="stat-value">¥{{ (data.monthly_gmv / 10000).toFixed(1) }}万</div></div>
      <div class="stat-card g2"><span class="stat-icon">🏪</span><div class="stat-label">活跃店铺</div><div class="stat-value">{{ data.store_total }}</div></div>
      <div class="stat-card g3"><span class="stat-icon">👥</span><div class="stat-label">主播/运营</div><div class="stat-value">{{ data.anchor_total }}/{{ data.operator_total }}</div></div>
      <div class="stat-card g5"><span class="stat-icon">📊</span><div class="stat-label">今日出勤率</div><div class="stat-value">{{ data.attendance_rate }}%</div></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
      <div class="glass" style="padding:20px"><div ref="chartRef1" style="width:100%;height:350px"></div></div>
      <div class="glass" style="padding:20px"><div ref="chartRef2" style="width:100%;height:350px"></div></div>
    </div>
    <div class="glass" style="padding:20px;margin-top:20px">
      <div style="font-size:16px;font-weight:700;margin-bottom:12px">🌟 TOP8 主播排行</div>
      <div v-for="(a, i) in (data?.top_anchors || [])" :key="i" style="display:flex;align-items:center;gap:16px;padding:10px;margin-bottom:6px;background:rgba(255,255,255,0.03);border-radius:8px">
        <span style="font-size:20px;font-weight:800;min-width:30px" :style="{ color: i === 0 ? '#ffd23f' : i === 1 ? '#c0c0c0' : i === 2 ? '#cd7f32' : 'var(--text-muted)' }">{{ i + 1 }}</span>
        <span style="font-weight:600;flex:1">{{ a.employee__name }}</span>
        <span style="color:var(--neon-cyan);font-weight:700">¥{{ (a.gmv / 10000).toFixed(1) }}万</span>
        <span style="color:var(--text-muted);font-size:12px">{{ a.sessions }}场</span>
      </div>
    </div>
  </div>
</template>
