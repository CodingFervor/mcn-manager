<script setup>
import { ref, onMounted, computed } from 'vue'
import echarts from '../echarts'
import { AI_API } from '../api'
import StatCard from '../components/StatCard.vue'

const activeTab = ref('insights')
const loading = ref(false)

// ===== AI Insights =====
const insights = ref([])
const insightSummary = ref({ total: 0, high: 0, medium: 0 })

async function loadInsights() {
  loading.value = true
  try {
    const res = await AI_API.insights()
    insights.value = res.recommendations || []
    insightSummary.value = res.summary || {}
  } finally { loading.value = false }
}

// ===== GMV Predict =====
const predictDays = ref(7)
const predictResult = ref(null)

async function loadPredict() {
  loading.value = true
  try {
    predictResult.value = await AI_API.predict({ days: predictDays.value })
    if (predictResult.value.status === 'ok') {
      renderPredictChart()
    }
  } finally { loading.value = false }
}

const predictChartRef = ref(null)
function renderPredictChart() {
  if (!predictChartRef.value || !predictResult.value?.predictions) return
  const chart = echarts.init(predictChartRef.value)
  const history = predictResult.value.history_trend || []
  const predictions = predictResult.value.predictions || []
  const allDates = [...history.map(h => h.date), ...predictions.map(p => p.date)]
  const historyGmv = history.map(h => h.gmv)
  const predGmv = new Array(history.length).fill(null).concat(predictions.map(p => p.predicted_gmv))

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(20,24,56,0.95)', borderColor: 'rgba(124,92,255,0.3)', textStyle: { color: '#fff' } },
    legend: { data: ['历史GMV', '预测GMV'], textStyle: { color: '#a8b2d1' }, top: 0 },
    grid: { top: 40, right: 20, bottom: 30, left: 60 },
    xAxis: { type: 'category', data: allDates, axisLabel: { color: '#6b7393', fontSize: 10, rotate: 30 }, axisLine: { lineStyle: { color: 'rgba(124,92,255,0.2)' } } },
    yAxis: { type: 'value', axisLabel: { color: '#6b7393', formatter: v => (v / 10000).toFixed(0) + '万' }, splitLine: { lineStyle: { color: 'rgba(124,92,255,0.1)' } } },
    series: [
      { name: '历史GMV', type: 'line', data: historyGmv, smooth: true, lineStyle: { color: '#00e5ff', width: 2 }, itemStyle: { color: '#00e5ff' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,229,255,0.3)' }, { offset: 1, color: 'rgba(0,229,255,0)' }] } } },
      { name: '预测GMV', type: 'line', data: predGmv, smooth: true, lineStyle: { color: '#ff4d9e', width: 2, type: 'dashed' }, itemStyle: { color: '#ff4d9e' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(255,77,158,0.2)' }, { offset: 1, color: 'rgba(255,77,158,0)' }] } } },
    ],
  })
  const ro = new ResizeObserver(() => chart.resize())
  ro.observe(predictChartRef.value)
}

// ===== Smart Schedule =====
const scheduleDate = ref(new Date().toISOString().split('T')[0])
const scheduleResult = ref(null)

async function loadSchedule() {
  loading.value = true
  try {
    scheduleResult.value = await AI_API.schedule({ date: scheduleDate.value })
  } finally { loading.value = false }
}

// ===== Anchor Profile =====
const anchorId = ref('')
const anchorResult = ref(null)

async function loadAnchor() {
  if (!anchorId.value) return
  loading.value = true
  try {
    anchorResult.value = await AI_API.anchor({ employee_id: anchorId.value })
    if (anchorResult.value.status === 'ok') {
      renderRadarChart()
    }
  } finally { loading.value = false }
}

const radarChartRef = ref(null)
function renderRadarChart() {
  if (!radarChartRef.value || !anchorResult.value?.dimensions) return
  const chart = echarts.init(radarChartRef.value)
  const dims = anchorResult.value.dimensions
  const indicators = [
    { name: '销售力', max: 100 }, { name: '流量力', max: 100 },
    { name: '转化力', max: 100 }, { name: '稳定性', max: 100 }, { name: '成长性', max: 100 },
  ]
  chart.setOption({
    backgroundColor: 'transparent',
    radar: { indicator: indicators, radius: '65%', axisName: { color: '#a8b2d1' }, splitArea: { areaStyle: { color: ['rgba(124,92,255,0.05)', 'rgba(124,92,255,0.1)'] } }, splitLine: { lineStyle: { color: 'rgba(124,92,255,0.2)' } } },
    series: [{
      type: 'radar',
      data: [{
        value: [dims.sales, dims.traffic, dims.conversion, dims.stability, dims.growth],
        name: '能力值',
        areaStyle: { color: 'rgba(124,92,255,0.3)' },
        lineStyle: { color: '#7c5cff', width: 2 },
        itemStyle: { color: '#7c5cff' },
      }],
    }],
  })
  const ro = new ResizeObserver(() => chart.resize())
  ro.observe(radarChartRef.value)
}

// ===== Anomaly Detection =====
const anomalyDays = ref(7)
const anomalyResult = ref(null)

async function loadAnomaly() {
  loading.value = true
  try {
    anomalyResult.value = await AI_API.anomaly({ days: anomalyDays.value })
  } finally { loading.value = false }
}

// ===== Anchor-Store Match =====
const matchResult = ref(null)

async function loadMatch() {
  loading.value = true
  try {
    matchResult.value = await AI_API.match()
  } finally { loading.value = false }
}

const priorityColor = { high: 'danger', medium: 'warning', low: 'info' }
const severityIcon = { critical: '🔴', warning: '🟡' }

onMounted(() => {
  loadInsights()
})
</script>

<template>
  <div class="page">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <div>
        <h2 class="page-title">🤖 AI 智能中心</h2>
        <p class="page-subtitle">基于历史数据的智能分析与预测引擎</p>
      </div>
    </div>

    <el-tabs v-model="activeTab" style="color:var(--text-primary)">
      <!-- ===== AI 运营建议 ===== -->
      <el-tab-pane label="💡 运营建议" name="insights">
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
          <StatCard label="总建议数" :value="insightSummary.total" icon="📊" gradient="g1" />
          <StatCard label="高优先级" :value="insightSummary.high" icon="🔴" gradient="g4" />
          <StatCard label="中优先级" :value="insightSummary.medium" icon="🟡" gradient="g5" />
        </div>

        <div class="glass" style="padding:20px">
          <div style="font-size:16px;font-weight:700;margin-bottom:16px">📋 智能运营建议</div>
          <div v-if="insights.length === 0" style="text-align:center;padding:40px;color:var(--text-muted)">
            <div style="font-size:48px;margin-bottom:12px">🎉</div>
            <div>暂无告警建议，系统运营良好</div>
          </div>
          <div v-for="(item, i) in insights" :key="i" style="padding:16px;margin-bottom:12px;background:rgba(255,255,255,0.03);border:1px solid var(--border-glow);border-radius:12px;display:flex;gap:16px;align-items:flex-start">
            <div style="font-size:28px;min-width:40px;text-align:center">{{ item.icon }}</div>
            <div style="flex:1">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                <span style="font-weight:600;font-size:15px">{{ item.title }}</span>
                <el-tag :type="priorityColor[item.priority]" size="small">{{ item.priority === 'high' ? '高优' : item.priority === 'medium' ? '中优' : '低优' }}</el-tag>
              </div>
              <div style="color:var(--text-secondary);font-size:13px;line-height:1.6">{{ item.detail }}</div>
            </div>
            <el-button size="small" type="primary" plain>{{ item.action }}</el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- ===== GMV 预测 ===== -->
      <el-tab-pane label="📈 GMV预测" name="predict">
        <div style="display:flex;gap:12px;align-items:center;margin-bottom:20px">
          <span style="color:var(--text-secondary)">预测天数:</span>
          <el-input-number v-model="predictDays" :min="1" :max="30" size="small" />
          <el-button type="primary" @click="loadPredict" :loading="loading">🧠 开始预测</el-button>
        </div>

        <template v-if="predictResult">
          <div v-if="predictResult.status === 'insufficient_data'" class="glass" style="padding:40px;text-align:center">
            <div style="font-size:48px;margin-bottom:12px">📭</div>
            <div style="color:var(--text-muted)">{{ predictResult.message }}</div>
          </div>
          <template v-else>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
              <StatCard label="预测总GMV" :value="'¥' + (predictResult.summary.total_predicted / 10000).toFixed(1) + '万'" icon="💰" gradient="g1" />
              <StatCard label="日均预测" :value="'¥' + (predictResult.summary.daily_avg / 10000).toFixed(1) + '万'" icon="📊" gradient="g2" />
              <StatCard label="趋势" :value="(predictResult.summary.trend > 0 ? '+' : '') + predictResult.summary.trend + '%'" icon="📈" :gradient="predictResult.summary.trend >= 0 ? 'g3' : 'g4'" />
              <StatCard label="置信度" :value="predictResult.summary.confidence === 'high' ? '高' : predictResult.summary.confidence === 'medium' ? '中' : '低'" icon="🎯" :gradient="predictResult.summary.confidence === 'high' ? 'g3' : 'g5'" />
            </div>

            <div class="glass" style="padding:20px;margin-bottom:20px">
              <div style="font-size:15px;font-weight:600;margin-bottom:12px">📈 历史趋势 + AI预测</div>
              <div ref="predictChartRef" style="width:100%;height:350px"></div>
            </div>

            <div class="glass" style="padding:20px">
              <div style="font-size:15px;font-weight:600;margin-bottom:12px">📅 逐日预测明细</div>
              <el-table :data="predictResult.predictions" stripe style="width:100%">
                <el-table-column prop="date" label="日期" width="120" />
                <el-table-column prop="weekday" label="星期" width="80">
                  <template #default="{ row }">周{{ row.weekday }}</template>
                </el-table-column>
                <el-table-column prop="predicted_gmv" label="预测GMV">
                  <template #default="{ row }">
                    <span style="color:var(--neon-cyan);font-weight:600">¥{{ (row.predicted_gmv / 10000).toFixed(2) }}万</span>
                  </template>
                </el-table-column>
                <el-table-column prop="confidence" label="置信度">
                  <template #default="{ row }">
                    <el-progress :percentage="row.confidence" :stroke-width="6" :color="row.confidence > 60 ? '#00ff9d' : row.confidence > 30 ? '#ffd23f' : '#ff4d9e'" />
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </template>
      </el-tab-pane>

      <!-- ===== 智能排班 ===== -->
      <el-tab-pane label="📅 智能排班" name="schedule">
        <div style="display:flex;gap:12px;align-items:center;margin-bottom:20px">
          <span style="color:var(--text-secondary)">目标日期:</span>
          <el-date-picker v-model="scheduleDate" type="date" value-format="YYYY-MM-DD" size="small" />
          <el-button type="primary" @click="loadSchedule" :loading="loading">🧠 AI 排班推荐</el-button>
        </div>

        <template v-if="scheduleResult">
          <div v-if="scheduleResult.status !== 'ok'" class="glass" style="padding:40px;text-align:center">
            <div style="font-size:48px;margin-bottom:12px">📭</div>
            <div style="color:var(--text-muted)">{{ scheduleResult.message }}</div>
          </div>
          <template v-else>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
              <StatCard label="目标日期" :value="scheduleResult.target_date" icon="📅" gradient="g2" />
              <StatCard label="可用主播" :value="scheduleResult.summary.available_anchors + '/' + scheduleResult.summary.total_anchors" icon="👥" gradient="g1" />
              <StatCard label="最优组合评分" :value="scheduleResult.summary.best_combo_score?.toFixed(1)" icon="⭐" gradient="g3" />
            </div>

            <div class="glass" style="padding:20px">
              <div style="font-size:15px;font-weight:600;margin-bottom:16px">🎯 AI 排班推荐方案</div>
              <div v-for="(rec, i) in scheduleResult.recommendations" :key="i" style="padding:16px;margin-bottom:16px;background:rgba(255,255,255,0.03);border:1px solid var(--border-glow);border-radius:12px">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
                  <el-tag type="primary" size="large">{{ rec.shift_name }}</el-tag>
                  <span style="color:var(--neon-cyan);font-weight:600">{{ rec.shift_time }}</span>
                </div>
                <div v-for="(c, j) in rec.candidates" :key="j" style="display:flex;align-items:center;gap:16px;padding:10px 12px;margin-bottom:8px;background:rgba(124,92,255,0.05);border-radius:8px">
                  <div style="display:flex;align-items:center;gap:8px;min-width:160px">
                    <div style="width:32px;height:32px;border-radius:50%;background:var(--grad-1);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700">{{ c.anchor_name?.[0] }}</div>
                    <div>
                      <div style="font-weight:600;font-size:14px">{{ c.anchor_name }}</div>
                      <div style="font-size:11px;color:var(--text-muted)">{{ c.reason }}</div>
                    </div>
                  </div>
                  <div style="flex:1">
                    <el-progress :percentage="c.score" :stroke-width="8" :color="c.score >= 80 ? '#00ff9d' : c.score >= 60 ? '#00e5ff' : '#ffd23f'" />
                  </div>
                  <el-tag v-if="j === 0" type="success" size="small">推荐</el-tag>
                  <div style="font-size:12px;color:var(--text-secondary)">评分 {{ c.score }}</div>
                </div>
              </div>
            </div>
          </template>
        </template>
      </el-tab-pane>

      <!-- ===== 主播画像 ===== -->
      <el-tab-pane label="👤 主播画像" name="anchor">
        <div style="display:flex;gap:12px;align-items:center;margin-bottom:20px">
          <span style="color:var(--text-secondary)">主播ID:</span>
          <el-input v-model="anchorId" placeholder="输入主播ID" size="small" style="width:200px" />
          <el-button type="primary" @click="loadAnchor" :loading="loading">🧠 分析画像</el-button>
        </div>

        <template v-if="anchorResult">
          <div v-if="anchorResult.status !== 'ok'" class="glass" style="padding:40px;text-align:center">
            <div style="font-size:48px;margin-bottom:12px">📭</div>
            <div style="color:var(--text-muted)">{{ anchorResult.message }}</div>
          </div>
          <template v-else>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px">
              <div class="glass" style="padding:24px">
                <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px">
                  <div style="width:56px;height:56px;border-radius:50%;background:var(--grad-1);display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800">{{ anchorResult.anchor.name?.[0] }}</div>
                  <div>
                    <div style="font-size:20px;font-weight:700">{{ anchorResult.anchor.nickname }}</div>
                    <div style="color:var(--text-muted);font-size:13px">{{ anchorResult.anchor.level }} · 粉丝 {{ (anchorResult.anchor.fans / 10000).toFixed(1) }}万</div>
                  </div>
                  <div style="margin-left:auto;text-align:center">
                    <div style="font-size:32px;font-weight:800" class="glow-text">{{ anchorResult.overall_score }}</div>
                    <div style="font-size:11px;color:var(--text-muted)">综合评分</div>
                  </div>
                </div>

                <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px">
                  <div style="padding:12px;background:rgba(255,255,255,0.03);border-radius:10px">
                    <div style="font-size:11px;color:var(--text-muted)">30天GMV</div>
                    <div style="font-size:18px;font-weight:700;color:var(--neon-cyan)">¥{{ (anchorResult.metrics_30d.gmv / 10000).toFixed(1) }}万</div>
                  </div>
                  <div style="padding:12px;background:rgba(255,255,255,0.03);border-radius:10px">
                    <div style="font-size:11px;color:var(--text-muted)">场均观看</div>
                    <div style="font-size:18px;font-weight:700;color:var(--neon-purple)">{{ anchorResult.metrics_30d.avg_viewers }}</div>
                  </div>
                  <div style="padding:12px;background:rgba(255,255,255,0.03);border-radius:10px">
                    <div style="font-size:11px;color:var(--text-muted)">转化率</div>
                    <div style="font-size:18px;font-weight:700;color:var(--neon-green)">{{ anchorResult.metrics_30d.avg_conversion }}%</div>
                  </div>
                  <div style="padding:12px;background:rgba(255,255,255,0.03);border-radius:10px">
                    <div style="font-size:11px;color:var(--text-muted)">出勤率</div>
                    <div style="font-size:18px;font-weight:700;color:var(--neon-yellow)">{{ anchorResult.metrics_30d.attendance_rate }}%</div>
                  </div>
                </div>
              </div>

              <div class="glass" style="padding:24px">
                <div style="font-size:15px;font-weight:600;margin-bottom:12px">🎯 五维能力雷达</div>
                <div ref="radarChartRef" style="width:100%;height:280px"></div>
              </div>
            </div>

            <!-- AI Insights -->
            <div class="glass" style="padding:20px;margin-bottom:20px">
              <div style="font-size:15px;font-weight:600;margin-bottom:12px">🧠 AI 洞察</div>
              <div v-for="(insight, i) in anchorResult.insights" :key="i" style="padding:12px;margin-bottom:8px;display:flex;align-items:center;gap:12px;background:rgba(255,255,255,0.03);border-radius:10px">
                <span style="font-size:20px">{{ insight.icon }}</span>
                <el-tag :type="insight.type === 'success' ? 'success' : insight.type === 'danger' ? 'danger' : insight.type === 'warning' ? 'warning' : 'info'" size="small">{{ insight.type }}</el-tag>
                <span style="color:var(--text-secondary);font-size:13px">{{ insight.text }}</span>
              </div>
            </div>

            <!-- Best Hours & Stores -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
              <div class="glass" style="padding:20px">
                <div style="font-size:15px;font-weight:600;margin-bottom:12px">⏰ 最佳开播时段</div>
                <div v-for="h in anchorResult.best_hours" :key="h.hour" style="display:flex;align-items:center;gap:12px;padding:10px;margin-bottom:8px;background:rgba(255,255,255,0.03);border-radius:8px">
                  <span style="font-weight:700;color:var(--neon-cyan);min-width:60px">{{ h.hour }}:00</span>
                  <el-progress :percentage="Math.min(100, h.avg_gmv / 100000 * 100)" :stroke-width="8" style="flex:1" />
                  <span style="font-size:12px;color:var(--text-muted)">{{ (h.avg_gmv / 10000).toFixed(1) }}万</span>
                </div>
              </div>
              <div class="glass" style="padding:20px">
                <div style="font-size:15px;font-weight:600;margin-bottom:12px">🏪 最佳店铺</div>
                <div v-for="s in anchorResult.best_stores" :key="s.name" style="display:flex;align-items:center;gap:12px;padding:10px;margin-bottom:8px;background:rgba(255,255,255,0.03);border-radius:8px">
                  <span style="font-weight:600;flex:1">{{ s.name }}</span>
                  <el-tag size="small">{{ s.platform }}</el-tag>
                  <span style="color:var(--neon-cyan);font-weight:600">¥{{ (s.gmv / 10000).toFixed(1) }}万</span>
                </div>
              </div>
            </div>
          </template>
        </template>
      </el-tab-pane>

      <!-- ===== 异常检测 ===== -->
      <el-tab-pane label="🔍 异常检测" name="anomaly">
        <div style="display:flex;gap:12px;align-items:center;margin-bottom:20px">
          <span style="color:var(--text-secondary)">检测天数:</span>
          <el-input-number v-model="anomalyDays" :min="1" :max="30" size="small" />
          <el-button type="primary" @click="loadAnomaly" :loading="loading">🔍 开始检测</el-button>
        </div>

        <template v-if="anomalyResult">
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
            <StatCard label="检测场次" :value="anomalyResult.summary.total_checked" icon="📺" gradient="g1" />
            <StatCard label="异常数" :value="anomalyResult.summary.anomaly_count" icon="⚠️" gradient="g4" />
            <StatCard label="严重异常" :value="anomalyResult.summary.critical_count" icon="🔴" gradient="g4" />
            <StatCard label="异常率" :value="anomalyResult.summary.anomaly_rate + '%'" icon="📊" :gradient="anomalyResult.summary.anomaly_rate > 20 ? 'g4' : 'g3'" />
          </div>

          <div class="glass" style="padding:20px">
            <div style="font-size:15px;font-weight:600;margin-bottom:12px">🚨 异常记录</div>
            <div v-if="anomalyResult.anomalies.length === 0" style="text-align:center;padding:40px;color:var(--text-muted)">
              <div style="font-size:48px;margin-bottom:12px">✅</div>
              <div>未检测到异常数据</div>
            </div>
            <el-table v-else :data="anomalyResult.anomalies" stripe style="width:100%">
              <el-table-column prop="date" label="日期" width="110" />
              <el-table-column prop="anchor" label="主播" width="100" />
              <el-table-column prop="store" label="店铺" width="140" />
              <el-table-column prop="gmv" label="GMV" width="120">
                <template #default="{ row }">¥{{ (row.gmv / 10000).toFixed(2) }}万</template>
              </el-table-column>
              <el-table-column label="异常标记">
                <template #default="{ row }">
                  <el-tag v-for="(f, i) in row.flags" :key="i" :type="row.severity === 'critical' ? 'danger' : 'warning'" size="small" style="margin:2px">{{ f }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="severity" label="级别" width="80">
                <template #default="{ row }">
                  <span>{{ severityIcon[row.severity] }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </el-tab-pane>

      <!-- ===== 主播-店铺匹配 ===== -->
      <el-tab-pane label="🔗 智能匹配" name="match">
        <div style="margin-bottom:20px">
          <el-button type="primary" @click="loadMatch" :loading="loading">🧠 AI 智能匹配分析</el-button>
        </div>

        <template v-if="matchResult">
          <div class="glass" style="padding:20px;margin-bottom:20px">
            <div style="font-size:15px;font-weight:600;margin-bottom:16px">🏆 最佳主播-店铺组合 TOP 20</div>
            <el-table :data="matchResult.best_combos" stripe style="width:100%">
              <el-table-column prop="anchor_name" label="主播" width="100" />
              <el-table-column prop="store_name" label="店铺" width="180" />
              <el-table-column prop="platform" label="平台" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.platform }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="gmv" label="30天GMV" width="120">
                <template #default="{ row }">¥{{ (row.gmv / 10000).toFixed(1) }}万</template>
              </el-table-column>
              <el-table-column prop="sessions" label="场次" width="80" />
              <el-table-column prop="avg_viewers" label="场均观看" width="100" />
              <el-table-column prop="avg_conversion" label="转化率" width="90">
                <template #default="{ row }">{{ row.avg_conversion }}%</template>
              </el-table-column>
              <el-table-column prop="score" label="匹配评分" width="200">
                <template #default="{ row }">
                  <el-progress :percentage="row.score" :stroke-width="8" :color="row.score >= 70 ? '#00ff9d' : row.score >= 50 ? '#00e5ff' : '#ffd23f'" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
