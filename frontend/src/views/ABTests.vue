<script setup>
import { ref, onMounted } from 'vue'
import { ABTestAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const tests = ref([])
const stats = ref({ total: 0, running: 0, completed: 0, by_type: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '', test_type: '', kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      ABTestAPI.list(filters.value),
      ABTestAPI.stats()
    ])
    tests.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: tests.value.length,
      running: tests.value.filter(t => t.status === 'running').length,
      completed: tests.value.filter(t => t.status === 'completed').length,
      by_type: {}
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', test_type: 'script', hypothesis: '', control_plan: '', test_plan: '',
    control_sessions: 0, test_sessions: 0, control_gmv: 0, test_gmv: 0,
    control_metric: 0, test_metric: 0, confidence: 0, winner: '',
    status: 'draft', start_date: '', end_date: ''
  }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await ABTestAPI.update(form.value.id, form.value)
    else await ABTestAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const completeTest = async (row) => {
  await ElMessageBox.confirm('确定结束此AB测试？结束后将标记为已完成', '提示', { type: 'warning' })
  await ABTestAPI.complete(row.id)
  ElMessage.success('测试已结束')
  load()
}

const testTypeMap = { script: '话术', scene: '场景', product: '商品', price: '价格', time: '时间', title: '标题' }
const statusMap = { draft: '草稿', running: '进行中', completed: '已完成', cancelled: '已取消' }
const statusColor = { draft: 'info', running: 'success', completed: '', cancelled: 'danger' }
const winnerMap = { control: '对照组', test: '实验组', tie: '持平' }
const winnerColor = { control: 'warning', test: 'success', tie: 'info' }

const fmtMoney = (v) => {
  const n = Number(v) || 0
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toFixed(0)
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="AB测试" subtitle="策略实验 · 效果对比 · 数据决策" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">测试总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">进行中</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.running }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已完成</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.completed }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">测试类型</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ Object.keys(stats.by_type || {}).length }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索测试名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.test_type" placeholder="测试类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in testTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建测试</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="tests" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="测试名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="测试类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ testTypeMap[row.test_type] || row.test_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hypothesis" label="假设" width="130" show-overflow-tooltip />
        <el-table-column label="对照组GMV" width="110" align="right">
          <template #default="{ row }"><span style="color:#ffd23f;font-weight:600">¥{{ fmtMoney(row.control_gmv) }}</span></template>
        </el-table-column>
        <el-table-column label="实验组GMV" width="110" align="right">
          <template #default="{ row }"><span style="color:#00ff9d;font-weight:600">¥{{ fmtMoney(row.test_gmv) }}</span></template>
        </el-table-column>
        <el-table-column label="置信度" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.confidence >= 95 ? '#00ff9d' : row.confidence >= 80 ? '#ffd23f' : '#ff4d9e', fontWeight: 700 }">{{ row.confidence }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="胜出方案" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.winner" :type="winnerColor[row.winner]" size="small" effect="dark">{{ winnerMap[row.winner] }}</el-tag>
            <span v-else style="color:#a8b2d1">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="110" />
        <el-table-column prop="end_date" label="结束日期" width="110" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'running'" size="small" type="warning" @click="completeTest(row)">结束</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="AB测试" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="测试名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="测试类型">
          <el-select v-model="form.test_type" style="width:100%">
            <el-option v-for="(v, k) in testTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="假设"><el-input v-model="form.hypothesis" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="对照组方案"><el-input v-model="form.control_plan" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="实验组方案"><el-input v-model="form.test_plan" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="对照场次数"><el-input-number v-model="form.control_sessions" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="实验场次数"><el-input-number v-model="form.test_sessions" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="对照组GMV"><el-input-number v-model="form.control_gmv" :min="0" :step="100" style="width:100%" /></el-form-item>
        <el-form-item label="实验组GMV"><el-input-number v-model="form.test_gmv" :min="0" :step="100" style="width:100%" /></el-form-item>
        <el-form-item label="对照指标"><el-input-number v-model="form.control_metric" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="实验指标"><el-input-number v-model="form.test_metric" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="置信度%"><el-input-number v-model="form.confidence" :min="0" :max="100" :precision="1" style="width:100%" /></el-form-item>
        <el-form-item label="胜出方案">
          <el-select v-model="form.winner" clearable style="width:100%">
            <el-option v-for="(v, k) in winnerMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
