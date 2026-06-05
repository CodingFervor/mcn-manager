<script setup>
import { ref, onMounted } from 'vue'
import { EventAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_status: {}, total_budget: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '', event_type: '', kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      EventAPI.list(filters.value),
      EventAPI.stats()
    ])
    list.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: list.value.length,
      by_status: {},
      total_budget: list.value.reduce((s, i) => s + (i.budget || 0), 0)
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', event_type: 'live', start_date: '', end_date: '', location: '',
    budget: 0, actual_cost: 0, participants: 0, status: 'planning'
  }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await EventAPI.update(form.value.id, form.value)
    else await EventAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此活动？', '提示', { type: 'warning' })
  await EventAPI.remove(row.id)
  ElMessage.success('删除成功')
  load()
}

const eventTypeMap = { live: '直播', offline: '线下', online: '线上', brand: '品牌' }
const statusMap = { planning: '筹备中', active: '进行中', completed: '已完成' }
const statusColor = { planning: 'info', active: 'success', completed: '' }

const fmtMoney = (v) => {
  const n = Number(v) || 0
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toFixed(0)
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="活动管理" subtitle="活动策划 · 执行管理 · 效果评估" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">活动总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">各状态统计</div>
        <div style="font-size:16px;font-weight:700;color:#00ff9d">
          <span v-for="(v, k) in stats.by_status" :key="k" style="margin-right:12px">{{ statusMap[k] || k }}: {{ v }}</span>
          <span v-if="!stats.by_status || !Object.keys(stats.by_status).length">-</span>
        </div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总预算</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">¥{{ fmtMoney(stats.total_budget) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索活动名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.event_type" placeholder="活动类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in eventTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建活动</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="活动名称" min-width="140" show-overflow-tooltip />
        <el-table-column label="活动类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ eventTypeMap[row.event_type] || row.event_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="110" />
        <el-table-column prop="end_date" label="结束日期" width="110" />
        <el-table-column prop="location" label="地点" width="120" show-overflow-tooltip />
        <el-table-column label="预算" width="100" align="right">
          <template #default="{ row }"><span style="color:#ffd23f;font-weight:600">¥{{ fmtMoney(row.budget) }}</span></template>
        </el-table-column>
        <el-table-column label="实际成本" width="100" align="right">
          <template #default="{ row }"><span style="color:#ff4d9e;font-weight:600">¥{{ fmtMoney(row.actual_cost) }}</span></template>
        </el-table-column>
        <el-table-column label="参与人数" width="90" align="right">
          <template #default="{ row }"><span style="color:#00ff9d;font-weight:600">{{ row.participants }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="活动管理" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="活动名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="活动类型">
          <el-select v-model="form.event_type" style="width:100%">
            <el-option v-for="(v, k) in eventTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="地点"><el-input v-model="form.location" /></el-form-item>
        <el-form-item label="预算"><el-input-number v-model="form.budget" :min="0" :step="100" style="width:100%" /></el-form-item>
        <el-form-item label="实际成本"><el-input-number v-model="form.actual_cost" :min="0" :step="100" style="width:100%" /></el-form-item>
        <el-form-item label="参与人数"><el-input-number v-model="form.participants" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
