<script setup>
import { onMounted, ref, nextTick, onUnmounted } from 'vue'
import echarts from '../echarts'
import { ElMessage } from 'element-plus'
import { AttendanceAPI, LeaveAPI, EmployeeAPI } from '../api'
import { Position, Clock, Plus, EditPen, Check, Close } from '@element-plus/icons-vue'

const attendances = ref([])
const leaves = ref([])
const employees = ref([])
const summary = ref(null)
const loading = ref(false)
const clockDialog = ref(false)
const leaveDialog = ref(false)
const clockForm = ref({ employee_id: null, type: 'in' })
const leaveForm = ref({ employee: null, leave_type: 'personal', start_date: '', end_date: '', days: 1, reason: '' })

const today = new Date().toISOString().slice(0, 10)
const filter = ref({ start: new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10), end: today, result: '', employee_id: '' })

const resultChart = ref(null)
let chartInst = null

const load = async () => {
  loading.value = true
  try {
    const [att, lv, emps, sum] = await Promise.all([
      AttendanceAPI.list({ start: filter.value.start, end: filter.value.end, result: filter.value.result, employee_id: filter.value.employee_id }),
      LeaveAPI.list(),
      EmployeeAPI.list(),
      AttendanceAPI.summary({ start: filter.value.start, end: filter.value.end })
    ])
    attendances.value = att; leaves.value = lv; employees.value = emps; summary.value = sum
    await nextTick()
    renderChart()
  } finally { loading.value = false }
}

const renderChart = () => {
  if (!resultChart.value || !summary.value) return
  chartInst = chartInst || echarts.init(resultChart.value)
  const labels = { normal: '正常', late: '迟到', early: '早退', absent: '缺勤', leave: '请假', overtime: '加班' }
  const colors = { normal: '#00ff9d', late: '#ffd23f', early: '#00e5ff', absent: '#ff4d9e', leave: '#7c5cff', overtime: '#00e5ff' }
  const data = Object.entries(summary.value.by_result || {}).map(([k, v]) => ({ name: labels[k] || k, value: v, itemStyle: { color: colors[k] } }))
  chartInst.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', backgroundColor: 'rgba(20,24,56,0.95)', borderColor: '#7c5cff', textStyle: { color: '#fff' } },
    legend: { bottom: 0, textStyle: { color: '#a8b2d1' } },
    series: [{
      type: 'pie', radius: ['45%', '72%'], data,
      label: { formatter: '{b}\n{d}%', color: '#fff' },
      itemStyle: { borderRadius: 8, borderColor: '#0a0e27', borderWidth: 3 },
      emphasis: { itemStyle: { shadowBlur: 20, shadowColor: 'rgba(124,92,255,0.6)' } }
    }]
  })
}
const onResize = () => chartInst?.resize()
window.addEventListener('resize', onResize)
onUnmounted(() => { window.removeEventListener('resize', onResize); chartInst?.dispose() })

const openClock = () => { clockForm.value = { employee_id: null, type: 'in' }; clockDialog.value = true }
const submitClock = async () => {
  if (!clockForm.value.employee_id) { ElMessage.warning('请选择员工'); return }
  try {
    if (clockForm.value.type === 'in') await AttendanceAPI.clockIn({ employee_id: clockForm.value.employee_id })
    else await AttendanceAPI.clockOut({ employee_id: clockForm.value.employee_id })
    ElMessage.success('📍 打卡成功')
    clockDialog.value = false
    load()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '打卡失败') }
}

const openLeave = () => {
  leaveForm.value = { employee: null, leave_type: 'personal', start_date: today, end_date: today, days: 1, reason: '' }
  leaveDialog.value = true
}
const submitLeave = async () => {
  if (!leaveForm.value.employee || !leaveForm.value.reason) { ElMessage.warning('请填写完整'); return }
  await LeaveAPI.create(leaveForm.value)
  ElMessage.success('📝 申请已提交')
  leaveDialog.value = false
  load()
}
const approveLeave = async (row) => { await LeaveAPI.approve(row.id, { approver: 'admin' }); ElMessage.success('✅ 已批准'); load() }
const rejectLeave = async (row) => { await LeaveAPI.reject(row.id, { approver: 'admin' }); ElMessage.success('已拒绝'); load() }

const resultTag = (r) => ({ normal: 'success', late: 'warning', early: 'warning', absent: 'danger', leave: 'info', overtime: 'success' }[r] || 'info')
const resultLabel = (r) => ({ normal: '✓ 正常', late: '⚠ 迟到', early: '⚠ 早退', absent: '✗ 缺勤', leave: '○ 请假', overtime: '⏰ 加班' }[r] || r)
const leaveLabel = (t) => ({ personal: '事假', sick: '病假', annual: '年假', marriage: '婚假', bereavement: '丧假', maternity: '产假' }[t] || t)

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <h1 class="page-title animate-slide">考勤打卡 <span class="live-dot" style="margin-left: 8px"></span></h1>
    <div class="page-subtitle">实时定位打卡 · 迟到统计 · 请假审批</div>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <div class="stat-card g1"><el-icon class="stat-icon"><Position /></el-icon>
          <div class="stat-label">今日打卡</div>
          <div class="stat-value">{{ summary?.total || 0 }}</div>
          <div class="stat-trend">📍 实时定位</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g3"><el-icon class="stat-icon"><Check /></el-icon>
          <div class="stat-label">正常打卡</div>
          <div class="stat-value">{{ summary?.by_result?.normal || 0 }}</div>
          <div class="stat-trend">✓ 守时</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g5"><el-icon class="stat-icon"><Clock /></el-icon>
          <div class="stat-label">迟到</div>
          <div class="stat-value">{{ summary?.by_result?.late || 0 }}</div>
          <div class="stat-trend">⚠️ 待改进</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g4"><el-icon class="stat-icon"><Close /></el-icon>
          <div class="stat-label">缺勤</div>
          <div class="stat-value">{{ summary?.by_result?.absent || 0 }}</div>
          <div class="stat-trend">🚨 异常</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div style="display: flex; align-items: center; gap: 8px">
              <el-icon style="color: var(--neon-cyan)"><Clock /></el-icon>
              <span>考勤记录</span>
            </div>
          </template>
          <div class="toolbar">
            <el-date-picker v-model="filter.start" type="date" value-format="YYYY-MM-DD" style="width: 140px" />
            <span style="color: var(--neon-cyan)">→</span>
            <el-date-picker v-model="filter.end" type="date" value-format="YYYY-MM-DD" style="width: 140px" />
            <el-select v-model="filter.result" placeholder="结果" clearable style="width: 110px">
              <el-option label="正常" value="normal" />
              <el-option label="迟到" value="late" />
              <el-option label="请假" value="leave" />
            </el-select>
            <el-button type="primary" @click="load">查询</el-button>
            <div style="flex: 1"></div>
            <el-button type="primary" @click="openClock" style="background: var(--grad-1)">
              <el-icon><Position /></el-icon><span style="margin-left: 4px">立即打卡</span>
            </el-button>
          </div>
          <el-table :data="attendances.slice(0, 50)" stripe size="small" max-height="500">
            <el-table-column prop="employee_name" label="员工" width="100" />
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="row.check_type === 'clock_in' ? 'success' : 'info'">
                  {{ row.check_type === 'clock_in' ? '☀ 上班' : '🌙 下班' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="check_time" label="打卡时间" width="180" />
            <el-table-column label="结果" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="resultTag(row.result)">{{ resultLabel(row.result) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="迟到分钟" width="90">
              <template #default="{ row }">
                <span v-if="row.late_minutes" style="color: var(--neon-pink); font-weight: 700">+{{ row.late_minutes }}分</span>
                <span v-else style="color: var(--text-muted)">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="location" label="位置" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span style="display: flex; align-items: center; gap: 8px">
              <el-icon style="color: var(--neon-pink)">📊</el-icon>
              <span>考勤结果分布</span>
            </span>
          </template>
          <div ref="resultChart" style="height: 280px"></div>
        </el-card>
        <el-card v-if="summary" style="margin-top: 16px">
          <template #header>
            <span style="display: flex; align-items: center; gap: 8px">
              <el-icon style="color: var(--neon-yellow)">🏆</el-icon>
              <span>迟到 TOP 5</span>
            </span>
          </template>
          <div style="display: flex; flex-direction: column; gap: 8px">
            <div v-for="(row, i) in (summary.top_late || []).slice(0, 5)" :key="i" style="display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: rgba(255, 255, 255, 0.03); border-radius: 8px">
              <div :class="`stat-card ${i === 0 ? 'g4' : i === 1 ? 'g5' : 'g2'}`" style="width: 28px; height: 28px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; padding: 0">
                {{ i + 1 }}
              </div>
              <span style="flex: 1; font-size: 13px">{{ row.employee__name }}</span>
              <el-tag size="small" type="warning">{{ row.late }}次</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 16px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="display: flex; align-items: center; gap: 8px">
            <el-icon style="color: var(--neon-yellow)">📝</el-icon>
            <span>请假申请</span>
          </span>
          <el-button type="primary" size="small" @click="openLeave"><el-icon><Plus /></el-icon><span style="margin-left: 4px">申请</span></el-button>
        </div>
      </template>
      <el-table :data="leaves" stripe size="small" max-height="400">
        <el-table-column prop="employee_name" label="员工" width="100" />
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <el-tag size="small" effect="dark">{{ leaveLabel(row.leave_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="220">
          <template #default="{ row }">{{ row.start_date }} → {{ row.end_date }} <span style="color: var(--neon-cyan)">({{ row.days }}天)</span></template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'approved' ? 'success' : row.status === 'rejected' ? 'danger' : 'warning'">
              <span class="status-dot" :class="row.status === 'approved' ? 'status-online' : row.status === 'rejected' ? 'status-offline' : 'status-busy'"></span>
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" @click="approveLeave(row)" style="padding: 4px 10px">
                <el-icon><Check /></el-icon><span style="margin-left: 2px">批准</span>
              </el-button>
              <el-button size="small" type="danger" @click="rejectLeave(row)" style="padding: 4px 10px">
                <el-icon><Close /></el-icon><span style="margin-left: 2px">拒绝</span>
              </el-button>
            </template>
            <span v-else style="color: var(--text-muted)">已处理</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="clockDialog" title="📍 员工打卡" width="400px">
      <el-form :model="clockForm" label-width="80px">
        <el-form-item label="员工">
          <el-select v-model="clockForm.employee_id" filterable placeholder="请选择" style="width: 100%">
            <el-option v-for="e in employees.filter(x => x.is_active)" :key="e.id" :label="`${e.name} (${e.role_display})`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="clockForm.type">
            <el-radio value="in">☀ 上班打卡</el-radio>
            <el-radio value="out">🌙 下班打卡</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-alert type="info" :closable="false" show-icon style="background: rgba(0, 229, 255, 0.1); border: 1px solid var(--neon-cyan)">
          <template #title><span style="color: var(--neon-cyan)">系统自动判断迟到/早退/加班</span></template>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="clockDialog = false">取消</el-button>
        <el-button type="primary" @click="submitClock">📍 确认打卡</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="leaveDialog" title="📝 请假申请" width="450px">
      <el-form :model="leaveForm" label-width="90px">
        <el-form-item label="员工">
          <el-select v-model="leaveForm.employee" filterable style="width: 100%">
            <el-option v-for="e in employees.filter(x => x.is_active)" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="请假类型">
          <el-select v-model="leaveForm.leave_type" style="width: 100%">
            <el-option label="事假" value="personal" />
            <el-option label="病假" value="sick" />
            <el-option label="年假" value="annual" />
            <el-option label="婚假" value="marriage" />
            <el-option label="丧假" value="bereavement" />
            <el-option label="产假" value="maternity" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="leaveForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="leaveForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="天数"><el-input-number v-model="leaveForm.days" :min="0.5" :step="0.5" /></el-form-item>
        <el-form-item label="原因"><el-input v-model="leaveForm.reason" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="leaveDialog = false">取消</el-button>
        <el-button type="primary" @click="submitLeave">📝 提交申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>
