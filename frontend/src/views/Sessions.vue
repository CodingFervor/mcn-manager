<script setup>
import { onMounted, ref, nextTick, onUnmounted } from 'vue'
import echarts from '../echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { SessionAPI, EmployeeAPI, StoreAPI } from '../api'
import { Plus, Money, VideoCamera, User } from '@element-plus/icons-vue'

const sessions = ref([])
const topAnchors = ref([])
const employees = ref([])
const stores = ref([])
const dailyGmv = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = ref({ employee: null, store: null, date: '', duration_minutes: 240, peak_viewers: 0, avg_viewers: 0, new_followers: 0, gmv: 0, orders: 0, conversion_rate: 0 })

const today = new Date().toISOString().slice(0, 10)
const filter = ref({ start: new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10), end: today, employee_id: '', store_id: '' })

const gmvChart = ref(null)
const rankChart = ref(null)
let gmvInst = null, rankInst = null

const load = async () => {
  loading.value = true
  try {
    const [ss, top, emps, sts, daily] = await Promise.all([
      SessionAPI.list({ start: filter.value.start, end: filter.value.end, employee_id: filter.value.employee_id, store_id: filter.value.store_id }),
      SessionAPI.topAnchors({ start: filter.value.start, end: filter.value.end, limit: 10 }),
      EmployeeAPI.list({ role: 'anchor' }),
      StoreAPI.list(),
      SessionAPI.dailyGmv({ start: filter.value.start, end: filter.value.end })
    ])
    sessions.value = ss; topAnchors.value = top; employees.value = emps; stores.value = sts; dailyGmv.value = daily
    await nextTick()
    renderCharts()
  } finally { loading.value = false }
}

const renderCharts = () => {
  if (gmvChart.value) {
    gmvInst = gmvInst || echarts.init(gmvChart.value)
    gmvInst.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(20,24,56,0.95)', borderColor: '#7c5cff', textStyle: { color: '#fff' } },
      legend: { data: ['GMV(万)', '订单数', '直播场次'], textStyle: { color: '#a8b2d1' }, top: 0 },
      grid: { left: 50, right: 50, top: 40, bottom: 40 },
      xAxis: { type: 'category', data: dailyGmv.value.map(d => d.d?.slice(5) || d.d), axisLine: { lineStyle: { color: '#3a3f5f' } }, axisLabel: { color: '#a8b2d1' } },
      yAxis: [
        { type: 'value', name: 'GMV(万)', nameTextStyle: { color: '#a8b2d1' }, axisLine: { lineStyle: { color: '#3a3f5f' } }, splitLine: { lineStyle: { color: 'rgba(124,92,255,0.1)' } }, axisLabel: { color: '#a8b2d1' } },
        { type: 'value', name: '订单/场次', nameTextStyle: { color: '#a8b2d1' }, axisLine: { lineStyle: { color: '#3a3f5f' } }, splitLine: { show: false }, axisLabel: { color: '#a8b2d1' } }
      ],
      series: [
        { name: 'GMV(万)', type: 'line', smooth: true,
          data: dailyGmv.value.map(d => +(d.gmv / 10000).toFixed(1)),
          itemStyle: { color: '#ff4d9e' },
          lineStyle: { color: '#ff4d9e', width: 3 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(255,77,158,0.4)' }, { offset: 1, color: 'rgba(255,77,158,0)' }]) },
          symbol: 'circle', symbolSize: 8
        },
        { name: '订单数', type: 'bar', yAxisIndex: 1,
          data: dailyGmv.value.map(d => d.orders),
          itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#00ff9d' }, { offset: 1, color: 'rgba(0,255,157,0.2)' }]), borderRadius: [6, 6, 0, 0] }
        },
        { name: '直播场次', type: 'line', yAxisIndex: 1, smooth: true,
          data: dailyGmv.value.map(d => d.sessions),
          itemStyle: { color: '#00e5ff' }, lineStyle: { color: '#00e5ff', width: 2 }
        }
      ]
    })
  }
  if (rankChart.value) {
    rankInst = rankInst || echarts.init(rankChart.value)
    const sorted = topAnchors.value.slice().reverse()
    rankInst.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(20,24,56,0.95)', borderColor: '#7c5cff', textStyle: { color: '#fff' } },
      grid: { left: 100, right: 60, top: 20, bottom: 20 },
      xAxis: { type: 'value', name: 'GMV(万)', nameTextStyle: { color: '#a8b2d1' }, axisLine: { show: false }, splitLine: { lineStyle: { color: 'rgba(124,92,255,0.1)' } }, axisLabel: { color: '#a8b2d1' } },
      yAxis: { type: 'category', data: sorted.map(a => a.employee__name), axisLine: { lineStyle: { color: '#3a3f5f' } }, axisLabel: { color: '#a8b2d1' } },
      series: [{
        type: 'bar', barWidth: 18,
        data: sorted.map(a => +(a.gmv / 10000).toFixed(1)),
        itemStyle: {
          borderRadius: [0, 10, 10, 0],
          color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [{ offset: 0, color: '#7c5cff' }, { offset: 0.5, color: '#ff4d9e' }, { offset: 1, color: '#ffd23f' }] }
        },
        label: { show: true, position: 'right', color: '#fff', formatter: '{c}万', fontWeight: 600 }
      }]
    })
  }
}
const onResize = () => { gmvInst?.resize(); rankInst?.resize() }
window.addEventListener('resize', onResize)
onUnmounted(() => { window.removeEventListener('resize', onResize); gmvInst?.dispose(); rankInst?.dispose() })

const openCreate = () => {
  form.value = { employee: null, store: null, date: today, duration_minutes: 240, peak_viewers: 0, avg_viewers: 0, new_followers: 0, gmv: 0, orders: 0, conversion_rate: 0 }
  dialogVisible.value = true
}
const submit = async () => {
  if (!form.value.employee) { ElMessage.warning('请选择主播'); return }
  await SessionAPI.create(form.value)
  ElMessage.success('✨ 录入成功')
  dialogVisible.value = false
  load()
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此场次？', '提示', { type: 'warning' })
  await SessionAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const fmtMoney = (v) => v >= 10000 ? (v / 10000).toFixed(1) + '万' : v.toFixed(0)
onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <h1 class="page-title animate-slide">直播业绩 <span class="live-dot red" style="margin-left: 8px"></span></h1>
    <div class="page-subtitle">实时直播数据 · GMV 趋势 · 主播排行</div>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <div class="stat-card g1"><el-icon class="stat-icon"><Money /></el-icon>
          <div class="stat-label">总 GMV</div>
          <div class="stat-value">¥{{ fmtMoney(sessions.reduce((s, x) => s + Number(x.gmv), 0)) }}</div>
          <div class="stat-trend">🔥 业绩</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g3"><el-icon class="stat-icon"><VideoCamera /></el-icon>
          <div class="stat-label">直播场次</div>
          <div class="stat-value">{{ sessions.length }}</div>
          <div class="stat-trend">📺 持续开播</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g4"><el-icon class="stat-icon"><User /></el-icon>
          <div class="stat-label">总订单</div>
          <div class="stat-value">{{ sessions.reduce((s, x) => s + x.orders, 0).toLocaleString() }}</div>
          <div class="stat-trend">🛒 成交</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g2"><el-icon class="stat-icon"><User /></el-icon>
          <div class="stat-label">场均 GMV</div>
          <div class="stat-value">¥{{ sessions.length ? fmtMoney(sessions.reduce((s, x) => s + Number(x.gmv), 0) / sessions.length) : 0 }}</div>
          <div class="stat-trend">📊 人效</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div style="display: flex; align-items: center; gap: 8px">
              <el-icon style="color: var(--neon-pink)">📈</el-icon>
              <span>每日GMV/订单/场次趋势</span>
            </div>
          </template>
          <div ref="gmvChart" style="height: 320px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div style="display: flex; align-items: center; gap: 8px">
              <el-icon style="color: var(--neon-yellow)">🏆</el-icon>
              <span>主播 GMV 榜</span>
            </div>
          </template>
          <div ref="rankChart" style="height: 320px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 16px">
      <div class="toolbar">
        <el-date-picker v-model="filter.start" type="date" value-format="YYYY-MM-DD" style="width: 140px" />
        <span style="color: var(--neon-cyan)">→</span>
        <el-date-picker v-model="filter.end" type="date" value-format="YYYY-MM-DD" style="width: 140px" />
        <el-select v-model="filter.store_id" placeholder="🏪 店铺" clearable style="width: 180px" @change="load">
          <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-select v-model="filter.employee_id" placeholder="🎤 主播" clearable filterable style="width: 160px" @change="load">
          <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
        </el-select>
        <el-button type="primary" @click="load">查询</el-button>
        <div style="flex: 1"></div>
        <el-button type="primary" @click="openCreate" style="background: var(--grad-1)">
          <el-icon><Plus /></el-icon><span style="margin-left: 4px">录入直播</span>
        </el-button>
      </div>

      <el-table :data="sessions" stripe size="small" max-height="600">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="主播" width="120">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 8px">
              <div class="stat-card g1" style="width: 28px; height: 28px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; padding: 0; flex-shrink: 0">{{ row.employee_name?.[0] }}</div>
              <span style="font-weight: 600">{{ row.employee_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="store_name" label="店铺" min-width="200" show-overflow-tooltip />
        <el-table-column prop="date" label="日期" width="110" />
        <el-table-column label="时长" width="80">
          <template #default="{ row }">⏱ {{ Math.floor(row.duration_minutes/60) }}h{{ row.duration_minutes%60 }}m</template>
        </el-table-column>
        <el-table-column prop="peak_viewers" label="峰值" width="80">
          <template #default="{ row }"><span style="color: var(--neon-cyan)">{{ row.peak_viewers?.toLocaleString() }}</span></template>
        </el-table-column>
        <el-table-column prop="avg_viewers" label="平均" width="80" />
        <el-table-column prop="new_followers" label="新增粉" width="80">
          <template #default="{ row }"><span style="color: var(--neon-green)">+{{ row.new_followers }}</span></template>
        </el-table-column>
        <el-table-column label="GMV" width="130">
          <template #default="{ row }">
            <span style="color: var(--neon-pink); font-weight: 800; font-size: 14px">¥{{ Number(row.gmv).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="orders" label="订单" width="80" />
        <el-table-column prop="conversion_rate" label="转化%" width="80" />
        <el-table-column label="商品" width="80">
          <template #default="{ row }">
            <el-tag size="small" effect="dark">{{ row.products?.length || 0 }} 款</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" link type="danger" @click="remove(row)">删</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="📹 录入直播场次" width="550px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="主播">
          <el-select v-model="form.employee" filterable style="width: 100%">
            <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="店铺">
          <el-select v-model="form.store" filterable style="width: 100%">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期"><el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="直播时长(分)"><el-input-number v-model="form.duration_minutes" :min="0" /></el-form-item>
        <el-form-item label="峰值 / 平均">
          <el-input-number v-model="form.peak_viewers" :min="0" placeholder="峰值" />
          <el-input-number v-model="form.avg_viewers" :min="0" placeholder="平均" style="margin-left: 8px" />
        </el-form-item>
        <el-form-item label="新增粉丝"><el-input-number v-model="form.new_followers" :min="0" /></el-form-item>
        <el-form-item label="GMV(元)"><el-input-number v-model="form.gmv" :min="0" :step="1000" /></el-form-item>
        <el-form-item label="订单数"><el-input-number v-model="form.orders" :min="0" /></el-form-item>
        <el-form-item label="转化率(%)"><el-input-number v-model="form.conversion_rate" :min="0" :max="100" :step="0.1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
