<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ReportAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const reports = ref([])
const loading = ref(false)
const dialog = ref(false)
const generating = ref({})
const form = ref({})
const filters = ref({ status: '', report_type: '' })

const reportTypeMap = {
  daily: { label: '日报', type: '' },
  weekly: { label: '周报', type: 'warning' },
  monthly: { label: '月报', type: 'success' },
  custom: { label: '自定义', type: 'info' }
}
const categoryMap = {
  gmv: 'GMV', traffic: '流量', anchor: '主播',
  product: '商品', finance: '财务', comprehensive: '综合'
}
const statusColor = { pending: 'info', generating: 'warning', completed: 'success', failed: 'danger' }
const statusLabel = { pending: '待生成', generating: '生成中', completed: '已完成', failed: '失败' }

async function load() {
  loading.value = true
  try { reports.value = await ReportAPI.list(filters.value) }
  finally { loading.value = false }
}

const openCreate = () => {
  form.value = { report_type: 'daily', category: 'comprehensive', date_start: '', date_end: '' }
  dialog.value = true
}

async function save() {
  await ReportAPI.create(form.value)
  dialog.value = false
  ElMessage.success('报表任务已创建')
  load()
}

async function generateReport(row) {
  generating.value[row.id] = true
  try {
    await ReportAPI.generate(row.id)
    ElMessage.success('报表生成中，请稍后刷新查看')
    load()
  } catch { ElMessage.error('生成失败') }
  finally { generating.value[row.id] = false }
}

const remove = async (id) => {
  await ElMessageBox.confirm('确定删除此报表？', '提示', { type: 'warning' })
  await ReportAPI.remove(id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="数据报表" subtitle="报表生成 · 数据分析 · 定期报告" />

    <div class="toolbar">
      <el-select v-model="filters.report_type" placeholder="报表类型" clearable @change="load" style="width:130px">
        <el-option label="日报" value="daily" />
        <el-option label="周报" value="weekly" />
        <el-option label="月报" value="monthly" />
        <el-option label="自定义" value="custom" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="load" style="width:120px">
        <el-option label="待生成" value="pending" />
        <el-option label="生成中" value="generating" />
        <el-option label="已完成" value="completed" />
        <el-option label="失败" value="failed" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建报表</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="reports" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="报表名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="报表类型" width="100">
          <template #default="{ row }">
            <el-tag :type="reportTypeMap[row.report_type]?.type" size="small">{{ reportTypeMap[row.report_type]?.label || row.report_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="90">
          <template #default="{ row }">{{ categoryMap[row.category] || row.category }}</template>
        </el-table-column>
        <el-table-column label="日期范围" width="200">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan)">{{ row.date_start }}</span>
            <span style="margin:0 4px;color:#8892b0">~</span>
            <span style="color:var(--neon-cyan)">{{ row.date_end }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small" effect="dark">{{ statusLabel[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending' || row.status === 'failed'"
              size="small"
              type="primary"
              :loading="generating[row.id]"
              @click="generateReport(row)"
            >生成</el-button>
            <el-button
              v-if="row.file_url"
              size="small"
              type="success"
            >
              <a :href="row.file_url" target="_blank" download style="color:inherit;text-decoration:none">下载</a>
            </el-button>
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建报表" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="报表名称"><el-input v-model="form.title" placeholder="请输入报表名称" /></el-form-item>
        <el-form-item label="报表类型">
          <el-select v-model="form.report_type" style="width:100%">
            <el-option label="日报" value="daily" />
            <el-option label="周报" value="weekly" />
            <el-option label="月报" value="monthly" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="报表分类">
          <el-select v-model="form.category" style="width:100%">
            <el-option label="GMV" value="gmv" />
            <el-option label="流量" value="traffic" />
            <el-option label="主播" value="anchor" />
            <el-option label="商品" value="product" />
            <el-option label="财务" value="finance" />
            <el-option label="综合" value="comprehensive" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始日期">
              <el-date-picker v-model="form.date_start" type="date" value-format="YYYY-MM-DD" placeholder="开始日期" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期">
              <el-date-picker v-model="form.date_end" type="date" value-format="YYYY-MM-DD" placeholder="结束日期" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>
