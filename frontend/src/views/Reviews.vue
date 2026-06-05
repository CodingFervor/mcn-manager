<script setup>
import { onMounted, ref, nextTick, onUnmounted } from 'vue'
import echarts from '../echarts'
import { ElMessage } from 'element-plus'
import { ReviewAPI, EmployeeAPI, KPIConfigAPI } from '../api'
import { Trophy, Money, Star, Lightning, Medal } from '@element-plus/icons-vue'

const reviews = ref([])
const employees = ref([])
const kpis = ref([])
const loading = ref(false)
const calcDialog = ref(false)
const calcForm = ref({ employee_id: null, period: '' })

const filter = ref({ period: '', role: '', level: '' })
const levelChart = ref(null)
const scoreChart = ref(null)
let levelInst = null
let scoreInst = null

const currentPeriod = new Date().toISOString().slice(0, 7)
filter.value.period = currentPeriod

const load = async () => {
  loading.value = true
  try {
    let rs = await ReviewAPI.list({ period: filter.value.period, role: filter.value.role, level: filter.value.level })
    if (rs.length === 0 && !filter.value.role && !filter.value.level) {
      const all = await ReviewAPI.list({})
      if (all.length) {
        const periods = [...new Set(all.map(r => r.period))].sort().reverse()
        filter.value.period = periods[0]
        rs = await ReviewAPI.list({ period: filter.value.period })
      }
    }
    const [emps, ks] = await Promise.all([EmployeeAPI.list(), KPIConfigAPI.list()])
    reviews.value = rs
    employees.value = emps
    kpis.value = ks
    await nextTick()
    renderCharts()
  } finally { loading.value = false }
}

const renderCharts = () => {
  if (levelChart.value) {
    levelInst = levelInst || echarts.init(levelChart.value)
    const counts = { S: 0, A: 0, B: 0, C: 0, D: 0 }
    reviews.value.forEach(r => counts[r.level] = (counts[r.level] || 0) + 1)
    levelInst.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)', backgroundColor: 'rgba(20,24,56,0.95)', borderColor: '#7c5cff', textStyle: { color: '#fff' } },
      legend: { bottom: 0, textStyle: { color: '#a8b2d1' } },
      series: [{
        type: 'pie', radius: ['45%', '72%'],
        data: [
          { name: 'S-优秀', value: counts.S, itemStyle: { color: '#ff4d9e' } },
          { name: 'A-良好', value: counts.A, itemStyle: { color: '#fa541c' } },
          { name: 'B-合格', value: counts.B, itemStyle: { color: '#00e5ff' } },
          { name: 'C-待改进', value: counts.C, itemStyle: { color: '#ffd23f' } },
          { name: 'D-不合格', value: counts.D, itemStyle: { color: '#666' } }
        ],
        label: { formatter: '{b}\n{c}人 ({d}%)', color: '#fff', fontWeight: 600 },
        itemStyle: { borderRadius: 8, borderColor: '#0a0e27', borderWidth: 3 },
        emphasis: { itemStyle: { shadowBlur: 20, shadowColor: 'rgba(124,92,255,0.6)' } }
      }]
    })
  }
  if (scoreChart.value) {
    scoreInst = scoreInst || echarts.init(scoreChart.value)
    const top = reviews.value.slice().sort((a, b) => b.score - a.score).slice(0, 10).reverse()
    scoreInst.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(20,24,56,0.95)', borderColor: '#7c5cff', textStyle: { color: '#fff' } },
      grid: { left: 100, right: 60, top: 20, bottom: 20 },
      xAxis: { type: 'value', max: 100, name: '得分', nameTextStyle: { color: '#a8b2d1' }, axisLine: { show: false }, splitLine: { lineStyle: { color: 'rgba(124,92,255,0.1)' } }, axisLabel: { color: '#a8b2d1' } },
      yAxis: { type: 'category', data: top.map(r => r.employee_name), axisLine: { lineStyle: { color: '#3a3f5f' } }, axisLabel: { color: '#a8b2d1' } },
      series: [{
        type: 'bar', barWidth: 18,
        data: top.map(r => ({
          value: r.score,
          itemStyle: {
            borderRadius: [0, 10, 10, 0],
            color: r.level === 'S' ? { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#7c5cff' }, { offset: 1, color: '#ff4d9e' }] }
                    : r.level === 'A' ? { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#fa541c' }, { offset: 1, color: '#ffd23f' }] }
                    : r.level === 'B' ? { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#00e5ff' }, { offset: 1, color: '#7c5cff' }] }
                    : { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#ffd23f' }, { offset: 1, color: '#fa541c' }] }
          }
        })),
        label: { show: true, position: 'right', color: '#fff', formatter: '{c}分', fontWeight: 700 }
      }]
    })
  }
}
const onResize = () => { levelInst?.resize(); scoreInst?.resize() }
window.addEventListener('resize', onResize)
onUnmounted(() => { window.removeEventListener('resize', onResize); levelInst?.dispose(); scoreInst?.dispose() })

const openCalc = () => {
  calcForm.value = { employee_id: null, period: currentPeriod }
  calcDialog.value = true
}
const submitCalc = async () => {
  if (!calcForm.value.employee_id) { ElMessage.warning('请选择员工'); return }
  try {
    await ReviewAPI.calculate(calcForm.value)
    ElMessage.success('✨ 已计算')
    calcDialog.value = false
    load()
  } catch (e) { ElMessage.error('计算失败') }
}

const roleLabel = (r) => ({ anchor: '主播', operator: '运营', manager: '经理' }[r] || r)
const roleGrad = (r) => ({ anchor: 'g1', operator: 'g3', manager: 'g5' }[r] || 'g2')
const levelStyle = (lv) => ({
  S: { color: '#ff4d9e', bg: 'rgba(255,77,158,0.15)', grad: 'linear-gradient(135deg, #ff4d9e, #7c5cff)' },
  A: { color: '#fa541c', bg: 'rgba(250,84,28,0.15)', grad: 'linear-gradient(135deg, #fa541c, #ffd23f)' },
  B: { color: '#00e5ff', bg: 'rgba(0,229,255,0.15)', grad: 'linear-gradient(135deg, #00e5ff, #7c5cff)' },
  C: { color: '#ffd23f', bg: 'rgba(255,210,63,0.15)', grad: 'linear-gradient(135deg, #ffd23f, #fa541c)' },
  D: { color: '#888', bg: 'rgba(136,136,136,0.15)', grad: 'linear-gradient(135deg, #666, #999)' }
}[lv] || { color: '#888', bg: 'rgba(136,136,136,0.15)', grad: 'linear-gradient(135deg, #666, #999)' })

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <h1 class="page-title animate-slide">绩效考核 <span class="live-dot" style="margin-left: 8px"></span></h1>
    <div class="page-subtitle">KPI 智能评估 · 奖金自动核算 · 等级分布分析</div>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <div class="stat-card g1"><el-icon class="stat-icon"><Trophy /></el-icon>
          <div class="stat-label">考核人数</div>
          <div class="stat-value">{{ reviews.length }}</div>
          <div class="stat-trend">📊 {{ filter.period }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g3"><el-icon class="stat-icon"><Money /></el-icon>
          <div class="stat-label">平均 GMV</div>
          <div class="stat-value">¥{{ reviews.length ? (reviews.reduce((s, r) => s + Number(r.gmv), 0) / reviews.length / 10000).toFixed(1) : 0 }}<span style="font-size: 16px">万</span></div>
          <div class="stat-trend">💰 人均</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g5"><el-icon class="stat-icon"><Star /></el-icon>
          <div class="stat-label">平均得分</div>
          <div class="stat-value">{{ reviews.length ? (reviews.reduce((s, r) => s + Number(r.score), 0) / reviews.length).toFixed(1) : 0 }}</div>
          <div class="stat-trend">⭐ 综合</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g4"><el-icon class="stat-icon"><Medal /></el-icon>
          <div class="stat-label">奖金总额</div>
          <div class="stat-value">¥{{ (reviews.reduce((s, r) => s + Number(r.bonus), 0) / 10000).toFixed(1) }}<span style="font-size: 16px">万</span></div>
          <div class="stat-trend">💎 绩效</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div style="display: flex; align-items: center; gap: 8px">
              <el-icon style="color: var(--neon-pink)">🏆</el-icon>
              <span>评级分布</span>
            </div>
          </template>
          <div ref="levelChart" style="height: 320px"></div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card>
          <template #header>
            <div style="display: flex; align-items: center; gap: 8px">
              <el-icon style="color: var(--neon-yellow)">⭐</el-icon>
              <span>得分 TOP 10</span>
            </div>
          </template>
          <div ref="scoreChart" style="height: 320px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 16px">
      <div class="toolbar">
        <el-date-picker v-model="filter.period" type="month" value-format="YYYY-MM" placeholder="选择月份" style="width: 160px" @change="load" />
        <el-select v-model="filter.role" placeholder="👤 角色" clearable style="width: 130px" @change="load">
          <el-option label="主播" value="anchor" />
          <el-option label="运营" value="operator" />
          <el-option label="经理" value="manager" />
        </el-select>
        <el-select v-model="filter.level" placeholder="🏅 评级" clearable style="width: 130px" @change="load">
          <el-option label="🌟 S 优秀" value="S" />
          <el-option label="🔥 A 良好" value="A" />
          <el-option label="💎 B 合格" value="B" />
          <el-option label="⚠ C 待改进" value="C" />
          <el-option label="❌ D 不合格" value="D" />
        </el-select>
        <el-button @click="load">查询</el-button>
        <div style="flex: 1"></div>
        <el-button type="primary" @click="openCalc" style="background: var(--grad-1)">
          <el-icon><Lightning /></el-icon><span style="margin-left: 4px">计算绩效</span>
        </el-button>
      </div>

      <el-table :data="reviews" stripe size="small" max-height="600">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="员工" width="120" fixed>
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 8px">
              <div :class="`stat-card ${roleGrad(row.employee_role)}`" style="width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; padding: 0; flex-shrink: 0">
                {{ row.employee_name?.[0] }}
              </div>
              <div>
                <div style="font-weight: 600; color: white">{{ row.employee_name }}</div>
                <div style="font-size: 11px; color: var(--text-muted)">{{ roleLabel(row.employee_role) }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="period" label="月份" width="90">
          <template #default="{ row }">
            <el-tag size="small" effect="dark">{{ row.period }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="GMV" width="120">
          <template #default="{ row }">
            <span style="color: var(--neon-pink); font-weight: 700">¥{{ (Number(row.gmv)/10000).toFixed(1) }}万</span>
          </template>
        </el-table-column>
        <el-table-column label="完成率" width="110">
          <template #default="{ row }">
            <el-progress :percentage="Math.min(Math.round(row.gmv_rate || 0), 200)" :status="row.gmv_rate >= 100 ? 'success' : row.gmv_rate < 50 ? 'exception' : ''" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column prop="orders" label="订单" width="80" />
        <el-table-column label="直播时长" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">⏱ {{ row.live_hours }}h</span>
          </template>
        </el-table-column>
        <el-table-column label="出勤" width="100">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 6px">
              <el-progress :percentage="Math.round(row.attendance_rate || 0)" :stroke-width="4" :show-text="false" style="flex: 1" :status="row.attendance_rate >= 90 ? 'success' : row.attendance_rate < 70 ? 'exception' : ''" />
              <span style="font-size: 12px; color: var(--neon-green)">{{ row.attendance_rate }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="综合得分" width="110">
          <template #default="{ row }">
            <div :style="`display: inline-block; background: ${levelStyle(row.level).grad}; padding: 4px 12px; border-radius: 8px; font-weight: 800; color: white; font-size: 14px; box-shadow: 0 0 12px ${levelStyle(row.level).color}80`">
              {{ row.score }} <span style="font-size: 11px; opacity: 0.8">分</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="评级" width="100">
          <template #default="{ row }">
            <div :style="`background: ${levelStyle(row.level).bg}; color: ${levelStyle(row.level).color}; padding: 4px 10px; border-radius: 6px; font-weight: 700; display: inline-block; border: 1px solid ${levelStyle(row.level).color}80`">
              {{ row.level_display }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="奖金" width="120">
          <template #default="{ row }">
            <span style="color: var(--neon-yellow); font-weight: 800; font-size: 15px">💰 ¥{{ Number(row.bonus).toLocaleString() }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card style="margin-top: 16px">
      <template #header>
        <div style="display: flex; align-items: center; gap: 8px">
          <el-icon style="color: var(--neon-cyan)">⚙️</el-icon>
          <span>KPI 指标配置</span>
        </div>
      </template>
      <el-table :data="kpis" stripe size="small">
        <el-table-column prop="role_display" label="适用角色" width="140">
          <template #default="{ row }">
            <el-tag size="small" effect="dark" :type="row.role === 'anchor' ? 'primary' : row.role === 'operator' ? 'success' : 'warning'">
              {{ row.role_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="metric_display" label="指标" width="140" />
        <el-table-column prop="target_value" label="目标值" width="120">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 700">{{ row.target_value }}</span>
          </template>
        </el-table-column>
        <el-table-column label="权重" width="120">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 6px">
              <el-progress :percentage="row.weight" :stroke-width="6" :show-text="false" style="flex: 1" />
              <span style="color: var(--neon-pink); font-weight: 700; font-size: 12px">{{ row.weight }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="period" label="周期" width="100" />
        <el-table-column label="启用" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small" effect="dark">
              <span class="status-dot" :class="row.is_active ? 'status-online' : 'status-offline'"></span>
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="calcDialog" title="⚡ 计算员工绩效" width="450px">
      <el-form :model="calcForm" label-width="80px">
        <el-form-item label="员工">
          <el-select v-model="calcForm.employee_id" filterable style="width: 100%" placeholder="选择员工">
            <el-option v-for="e in employees" :key="e.id" :label="`${e.name} (${e.role_display})`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="月份">
          <el-date-picker v-model="calcForm.period" type="month" value-format="YYYY-MM" style="width: 100%" />
        </el-form-item>
        <el-alert type="info" :closable="false" show-icon style="background: rgba(0, 229, 255, 0.1); border: 1px solid var(--neon-cyan)">
          <template #title><span style="color: var(--neon-cyan)">将自动计算该员工指定月份的 GMV/订单/出勤/得分/奖金</span></template>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="calcDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCalc" style="background: var(--grad-1)">🚀 开始计算</el-button>
      </template>
    </el-dialog>
  </div>
</template>
