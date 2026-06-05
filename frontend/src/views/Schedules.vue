<script setup>
import { onMounted, ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ScheduleAPI, EmployeeAPI, ShiftAPI, StoreAPI } from '../api'
import { Calendar, Plus, Lightning } from '@element-plus/icons-vue'

const schedules = ref([])
const employees = ref([])
const shifts = ref([])
const stores = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const batchDialog = ref(false)
const form = ref({ employee: null, shift: null, date: '', store: null, status: 'scheduled', note: '' })
const batchForm = ref({ employee_ids: [], shift_id: null, start_date: '', end_date: '', store_id: null })
const weekStart = ref(getWeekStart(new Date()))

const filter = ref({ store_id: '', role: '', employee_id: '' })

const dates = computed(() => {
  const arr = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(weekStart.value); d.setDate(d.getDate() + i)
    arr.push(d.toISOString().slice(0, 10))
  }
  return arr
})

const gridData = computed(() => {
  if (shifts.value.length === 0) return []
  return shifts.value.map(shift => {
    const row = { shift, cells: {} }
    for (const date of dates.value) {
      row.cells[date] = schedules.value.filter(s => s.shift === shift.id && s.date === date)
    }
    return row
  })
})

const today = new Date().toISOString().slice(0, 10)
const isToday = (d) => d === today

function getWeekStart(d) {
  const date = new Date(d); const day = date.getDay()
  const diff = date.getDate() - day + (day === 0 ? -6 : 1)
  return new Date(date.setDate(diff)).toISOString().slice(0, 10)
}

const load = async () => {
  loading.value = true
  try {
    const [scheds, emps, sfs, sts] = await Promise.all([
      ScheduleAPI.list({ start: dates.value[0], end: dates.value[6], store_id: filter.value.store_id, employee_id: filter.value.employee_id, role: filter.value.role }),
      EmployeeAPI.list({ is_active: 'true' }),
      ShiftAPI.list(),
      StoreAPI.list()
    ])
    schedules.value = scheds; employees.value = emps; shifts.value = sfs; stores.value = sts
  } finally { loading.value = false }
}

const prevWeek = () => { const d = new Date(weekStart.value); d.setDate(d.getDate() - 7); weekStart.value = d.toISOString().slice(0,10); load() }
const nextWeek = () => { const d = new Date(weekStart.value); d.setDate(d.getDate() + 7); weekStart.value = d.toISOString().slice(0,10); load() }
const thisWeek = () => { weekStart.value = getWeekStart(new Date()); load() }

const openCreate = (date, shift) => {
  form.value = { employee: null, shift: shift.id, date, store: null, status: 'scheduled', note: '' }
  dialogVisible.value = true
}
const submit = async () => {
  try {
    await ScheduleAPI.create(form.value)
    ElMessage.success('✨ 排班成功')
    dialogVisible.value = false
    load()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '排班失败') }
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此排班？', '提示', { type: 'warning' })
  await ScheduleAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const openBatch = () => {
  batchForm.value = {
    employee_ids: [],
    shift_id: shifts.value[0]?.id,
    start_date: new Date().toISOString().slice(0, 10),
    end_date: new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10),
    store_id: null
  }
  batchDialog.value = true
}
const submitBatch = async () => {
  if (!batchForm.value.employee_ids.length || !batchForm.value.shift_id) { ElMessage.warning('请选择员工和班次'); return }
  const start = new Date(batchForm.value.start_date)
  const end = new Date(batchForm.value.end_date)
  const data = []
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    for (const emp_id of batchForm.value.employee_ids) {
      data.push({ employee: emp_id, shift: batchForm.value.shift_id, date: d.toISOString().slice(0, 10), store: batchForm.value.store_id || null, status: 'scheduled' })
    }
  }
  try {
    const res = await ScheduleAPI.batchCreate(data)
    ElMessage.success(`✅ 批量排班：成功 ${res.created.length} 条，失败 ${res.errors.length} 条`)
    batchDialog.value = false
    load()
  } catch (e) { ElMessage.error('批量排班失败') }
}

const formatDate = (d) => { const date = new Date(d); return `${date.getMonth()+1}/${date.getDate()}` }
const dayName = (d) => { const n = ['日','一','二','三','四','五','六']; return '周' + n[new Date(d).getDay()] }
const roleGrad = (r) => ({ anchor: 'g1', operator: 'g3', manager: 'g5' }[r] || 'g2')
const roles = [['anchor','主播'],['operator','运营'],['manager','经理']]

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <h1 class="page-title animate-slide">智能排班 <span class="live-dot" style="margin-left: 8px"></span></h1>
    <div class="page-subtitle">可视化周排班 · 智能冲突检测 · 批量排班</div>

    <el-card>
      <div class="toolbar">
        <el-button @click="prevWeek">←</el-button>
        <el-button type="primary" @click="thisWeek" style="background: var(--grad-1)"><el-icon><Calendar /></el-icon><span style="margin-left: 4px">本周</span></el-button>
        <el-button @click="nextWeek">→</el-button>
        <span style="margin-left: 12px; padding: 8px 16px; background: rgba(124, 92, 255, 0.15); border: 1px solid var(--border-glow); border-radius: 10px; font-weight: 600; color: var(--neon-cyan)">
          {{ dates[0] }} → {{ dates[6] }}
        </span>
        <el-divider direction="vertical" />
        <el-select v-model="filter.store_id" placeholder="🏪 店铺" clearable style="width: 180px" @change="load">
          <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-select v-model="filter.role" placeholder="👤 角色" clearable style="width: 120px" @change="load">
          <el-option v-for="r in roles" :key="r[0]" :label="r[1]" :value="r[0]" />
        </el-select>
        <el-button @click="load">查询</el-button>
        <div style="flex: 1"></div>
        <el-button type="primary" @click="openBatch"><el-icon><Lightning /></el-icon><span style="margin-left: 4px">批量排班</span></el-button>
      </div>

      <el-table :data="gridData" border style="border-radius: 12px; overflow: hidden">
        <el-table-column label="班次" width="160" fixed>
          <template #default="{ row }">
            <el-tag :color="row.shift.color" style="color: white; border: none; font-weight: 600; padding: 6px 12px; border-radius: 10px">
              {{ row.shift.name }}
            </el-tag>
            <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px">⏰ {{ row.shift.time_range }}</div>
          </template>
        </el-table-column>
        <el-table-column v-for="date in dates" :key="date" :label="`${formatDate(date)} ${dayName(date)}`" min-width="170" :class-name="isToday(date) ? 'today-col' : ''">
          <template #default="{ row }">
            <div style="display: flex; flex-direction: column; gap: 6px; min-height: 60px">
              <div v-for="item in row.cells[date]" :key="item.id" :style="`background: linear-gradient(135deg, ${row.shift.color}25, ${row.shift.color}10); border-left: 3px solid ${row.shift.color}; padding: 6px 10px; border-radius: 8px; display: flex; align-items: center; gap: 6px; transition: all 0.2s`" onmouseover="this.style.transform='translateX(2px)'" onmouseout="this.style.transform='none'">
                <div :class="`stat-card ${roleGrad(item.employee_role)}`" style="width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; padding: 0; flex-shrink: 0">
                  {{ item.employee_name?.[0] }}
                </div>
                <div style="flex: 1; min-width: 0; overflow: hidden">
                  <div style="font-size: 12px; font-weight: 600; color: white; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">{{ item.employee_name }}</div>
                  <div v-if="item.store_name" style="font-size: 10px; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap">@{{ item.store_name }}</div>
                </div>
                <el-button link size="small" type="danger" @click="remove(item)" style="padding: 0; height: 18px; width: 18px; font-size: 14px">×</el-button>
              </div>
              <el-button size="small" type="primary" link @click="openCreate(date, row.shift)" style="font-size: 12px; padding: 2px 0">
                <el-icon><Plus /></el-icon> 添加
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="✨ 新增排班" width="450px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="员工">
          <el-select v-model="form.employee" placeholder="请选择员工" filterable style="width: 100%">
            <el-option v-for="e in employees" :key="e.id" :label="`${e.name} (${e.role_display})`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期"><el-input :value="form.date" disabled /></el-form-item>
        <el-form-item label="店铺">
          <el-select v-model="form.store" placeholder="可选" clearable style="width: 100%">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.note" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="batchDialog" title="⚡ 批量排班" width="600px">
      <el-form :model="batchForm" label-width="100px">
        <el-form-item label="选择员工">
          <el-select v-model="batchForm.employee_ids" multiple filterable placeholder="可多选" style="width: 100%">
            <el-option v-for="e in employees" :key="e.id" :label="`${e.name} (${e.role_display})`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="班次">
          <el-select v-model="batchForm.shift_id" style="width: 100%">
            <el-option v-for="s in shifts" :key="s.id" :label="`${s.name} (${s.time_range})`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker v-model="batchForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 45%" />
          <span style="margin: 0 8px; color: var(--neon-cyan)">→</span>
          <el-date-picker v-model="batchForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 45%" />
        </el-form-item>
        <el-form-item label="店铺">
          <el-select v-model="batchForm.store_id" clearable style="width: 100%">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-alert type="info" :closable="false" show-icon style="background: rgba(0, 229, 255, 0.1); border: 1px solid var(--neon-cyan)">
          <template #title><span style="color: var(--neon-cyan)">系统自动跳过时间冲突的排班</span></template>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="batchDialog = false">取消</el-button>
        <el-button type="primary" @click="submitBatch">🚀 开始排班</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style>
.today-col .cell { background: rgba(0, 229, 255, 0.05) !important; }
</style>
