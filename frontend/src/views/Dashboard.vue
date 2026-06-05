<script setup>
import { onMounted, ref, nextTick, onUnmounted } from 'vue'
import echarts from '../echarts'
import { DashboardAPI, ScheduleAPI } from '../api'
import { Money, Shop, VideoCamera, TrendCharts, DataLine, Trophy, Clock } from '@element-plus/icons-vue'

const data = ref(null)
const schedules = ref([])
const loading = ref(false)

const trendChart = ref(null)
const platformChart = ref(null)
const topChart = ref(null)
let trendInst = null, platformInst = null, topInst = null

const load = async () => {
  loading.value = true
  try {
    const [d, scheds] = await Promise.all([
      DashboardAPI.overview(),
      ScheduleAPI.list({ start: new Date().toISOString().slice(0,10), end: new Date().toISOString().slice(0,10) })
    ])
    data.value = d
    schedules.value = scheds
    await nextTick()
    renderCharts()
  } finally { loading.value = false }
}

const renderCharts = () => {
  if (trendChart.value && data.value?.trend_7d?.length) {
    trendInst = trendInst || echarts.init(trendChart.value)
    trendInst.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(20,24,56,0.95)', borderColor: '#7c5cff', textStyle: { color: '#fff' } },
      legend: { data: ['GMV(万)', '订单数'], textStyle: { color: '#a8b2d1' }, top: 0 },
      grid: { left: 50, right: 50, top: 40, bottom: 30 },
      xAxis: { type: 'category', data: data.value.trend_7d.map(d => d.d.slice(5)), axisLine: { lineStyle: { color: '#3a3f5f' } }, axisLabel: { color: '#a8b2d1' } },
      yAxis: [
        { type: 'value', name: 'GMV(万)', nameTextStyle: { color: '#a8b2d1' }, axisLine: { lineStyle: { color: '#3a3f5f' } }, splitLine: { lineStyle: { color: 'rgba(124,92,255,0.1)' } }, axisLabel: { color: '#a8b2d1' } },
        { type: 'value', name: '订单数', nameTextStyle: { color: '#a8b2d1' }, axisLine: { lineStyle: { color: '#3a3f5f' } }, splitLine: { show: false }, axisLabel: { color: '#a8b2d1' } }
      ],
      series: [
        {
          name: 'GMV(万)', type: 'line', smooth: true,
          data: data.value.trend_7d.map(d => +(d.gmv / 10000).toFixed(2)),
          itemStyle: { color: '#7c5cff' },
          lineStyle: { color: '#7c5cff', width: 3 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(124,92,255,0.4)' }, { offset: 1, color: 'rgba(124,92,255,0)' }]) },
          symbol: 'circle', symbolSize: 8
        },
        {
          name: '订单数', type: 'bar', yAxisIndex: 1,
          data: data.value.trend_7d.map(d => d.orders),
          itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#00ff9d' }, { offset: 1, color: 'rgba(0,255,157,0.2)' }]), borderRadius: [6, 6, 0, 0] }
        }
      ]
    })
  }
  if (platformChart.value && data.value?.platform_dist?.length) {
    platformInst = platformInst || echarts.init(platformChart.value)
    const labels = { douyin: '抖音', kuaishou: '快手', taobao: '淘宝', xiaohongshu: '小红书', pdd: '拼多多', jd: '京东', video_account: '视频号' }
    const items = data.value.platform_dist.map(p => ({
      name: labels[p.store__platform] || p.store__platform,
      value: +(p.gmv / 10000).toFixed(1)
    }))
    platformInst.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}万 ({d}%)', backgroundColor: 'rgba(20,24,56,0.95)', borderColor: '#7c5cff', textStyle: { color: '#fff' } },
      legend: { bottom: 0, textStyle: { color: '#a8b2d1', fontSize: 11 } },
      series: [{
        type: 'pie', radius: ['45%', '72%'],
        data: items,
        label: { formatter: '{b}\n{d}%', color: '#fff', fontSize: 11 },
        itemStyle: { borderRadius: 8, borderColor: '#0a0e27', borderWidth: 3 },
        emphasis: { itemStyle: { shadowBlur: 20, shadowColor: 'rgba(124,92,255,0.6)' } }
      }]
    })
  }
  if (topChart.value && data.value?.top_anchors?.length) {
    topInst = topInst || echarts.init(topChart.value)
    const top8 = data.value.top_anchors.slice().reverse()
    topInst.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(20,24,56,0.95)', borderColor: '#7c5cff', textStyle: { color: '#fff' } },
      grid: { left: 80, right: 30, top: 20, bottom: 20 },
      xAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: 'rgba(124,92,255,0.1)' } }, axisLabel: { color: '#a8b2d1' } },
      yAxis: { type: 'category', data: top8.map(a => a.employee__name), axisLine: { lineStyle: { color: '#3a3f5f' } }, axisLabel: { color: '#a8b2d1' } },
      series: [{
        type: 'bar', barWidth: 14,
        data: top8.map(a => +(a.gmv / 10000).toFixed(1)),
        itemStyle: {
          borderRadius: [0, 8, 8, 0],
          color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [{ offset: 0, color: '#7c5cff' }, { offset: 1, color: '#ff4d9e' }] }
        },
        label: { show: true, position: 'right', color: '#fff', formatter: '{c}万' }
      }]
    })
  }
}
const onResize = () => { trendInst?.resize(); platformInst?.resize(); topInst?.resize() }
window.addEventListener('resize', onResize)
onUnmounted(() => { window.removeEventListener('resize', onResize); trendInst?.dispose(); platformInst?.dispose(); topInst?.dispose() })

const fmtMoney = (v) => {
  if (v >= 100000000) return (v / 100000000).toFixed(2) + '亿'
  if (v >= 10000) return (v / 10000).toFixed(1) + '万'
  return v.toFixed(0)
}
const todayStatus = (s) => ({ checked_in: 'success', completed: 'success', cancelled: 'info', absent: 'danger' }[s] || 'warning')

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px">
      <div>
        <h1 class="page-title animate-slide">数据驾驶舱 <span class="live-dot" style="margin-left: 12px"></span><span style="font-size: 12px; color: var(--neon-green); vertical-align: middle">实时数据</span></h1>
        <div class="page-subtitle">监控全平台直播运营关键指标 · {{ new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }) }}</div>
      </div>
      <el-button @click="load" style="background: rgba(124, 92, 255, 0.15); border: 1px solid var(--border-glow)">
        <el-icon><DataLine /></el-icon><span style="margin-left: 6px">刷新数据</span>
      </el-button>
    </div>

    <el-row :gutter="16" v-if="data">
      <el-col :span="6">
        <div class="stat-card g1">
          <el-icon class="stat-icon"><Money /></el-icon>
          <div class="stat-label">月度GMV总额</div>
          <div class="stat-value">¥{{ fmtMoney(data.monthly_gmv) }}</div>
          <div class="stat-sub">{{ data.monthly_sessions }} 场直播 · {{ data.monthly_orders.toLocaleString() }} 单</div>
          <div class="stat-trend">🔥 同比 +28.4%</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g2">
          <el-icon class="stat-icon"><Shop /></el-icon>
          <div class="stat-label">活跃店铺</div>
          <div class="stat-value">{{ data.store_total }}</div>
          <div class="stat-sub">覆盖 {{ ['抖音', '快手', '淘宝', '小红书', '拼多多'].slice(0, 5).join('·') }}</div>
          <div class="stat-trend">⚡ 实时同步</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g3">
          <el-icon class="stat-icon"><VideoCamera /></el-icon>
          <div class="stat-label">主播 / 运营</div>
          <div class="stat-value">{{ data.anchor_total }}<span style="font-size: 18px; opacity: 0.8"> / {{ data.operator_total }}</span></div>
          <div class="stat-sub">在职 · 可排班</div>
          <div class="stat-trend">✓ 在岗率 92%</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g4">
          <el-icon class="stat-icon"><Clock /></el-icon>
          <div class="stat-label">今日出勤率</div>
          <div class="stat-value">{{ data.attendance_rate }}%</div>
          <div class="stat-sub">{{ data.today_attended }} / {{ data.today_schedules }} 已打卡</div>
          <div class="stat-trend">📍 实时定位</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px" v-if="data">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span style="display: flex; align-items: center; gap: 8px">
                <el-icon style="color: var(--neon-cyan); font-size: 18px"><TrendCharts /></el-icon>
                <span>近7日GMV与订单趋势</span>
              </span>
              <el-tag size="small" style="background: rgba(0, 229, 255, 0.2); border: 1px solid var(--neon-cyan); color: var(--neon-cyan)">实时</el-tag>
            </div>
          </template>
          <div ref="trendChart" style="height: 320px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span style="display: flex; align-items: center; gap: 8px">
              <el-icon style="color: var(--neon-pink); font-size: 18px"><Trophy /></el-icon>
              <span>平台GMV分布</span>
            </span>
          </template>
          <div ref="platformChart" style="height: 320px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px" v-if="data">
      <el-col :span="14">
        <el-card>
          <template #header>
            <span style="display: flex; align-items: center; gap: 8px">
              <el-icon style="color: var(--neon-yellow); font-size: 18px"><Trophy /></el-icon>
              <span>主播 GMV 排行 TOP 8</span>
            </span>
          </template>
          <div ref="topChart" style="height: 320px"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card>
          <template #header>
            <span style="display: flex; align-items: center; gap: 8px">
              <el-icon style="color: var(--neon-green); font-size: 18px"><Clock /></el-icon>
              <span>今日实时排班</span>
              <el-tag size="small" style="margin-left: auto; background: rgba(0, 255, 157, 0.2); border: 1px solid var(--neon-green); color: var(--neon-green)">{{ schedules.length }} 人</el-tag>
            </span>
          </template>
          <div style="max-height: 320px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px">
            <div v-for="row in schedules.slice(0, 12)" :key="row.id" style="display: flex; align-items: center; padding: 10px 12px; background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-glow); border-radius: 10px; transition: all 0.2s" onmouseover="this.style.background='rgba(124,92,255,0.1)'" onmouseout="this.style.background='rgba(255,255,255,0.03)'">
              <div :style="`width: 36px; height: 36px; border-radius: 10px; background: var(--grad-${row.employee_role === 'anchor' ? 1 : row.employee_role === 'operator' ? 3 : 5}); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 14px; margin-right: 12px`">
                {{ row.employee_name?.[0] || '?' }}
              </div>
              <div style="flex: 1; min-width: 0">
                <div style="display: flex; align-items: center; gap: 6px">
                  <span style="font-weight: 600; color: white">{{ row.employee_name }}</span>
                  <el-tag size="small" :type="row.employee_role === 'anchor' ? 'danger' : row.employee_role === 'operator' ? 'success' : 'warning'">
                    {{ {anchor:'主播', operator:'运营', manager:'经理'}[row.employee_role] }}
                  </el-tag>
                </div>
                <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">
                  {{ row.store_name || '未分配店铺' }} · {{ row.shift_name }} {{ row.start_time?.slice(0,5) }}
                </div>
              </div>
              <el-tag size="small" :type="todayStatus(row.status)" effect="dark" style="flex-shrink: 0">
                <span class="status-dot" :class="row.status === 'checked_in' || row.status === 'completed' ? 'status-online' : 'status-busy'"></span>
                {{ row.status_display }}
              </el-tag>
            </div>
            <el-empty v-if="!schedules.length" description="今天还没有排班" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
