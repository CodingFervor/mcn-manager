<script setup>
import { ref, onMounted } from 'vue'
import { ReportSchedulerAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, pdf: 0, excel: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', report_type: '', is_active: '' })

const reportTypeMap = { sales: '销售报表', live: '直播报表', finance: '财务报表', inventory: '库存报表', traffic: '流量报表', user: '用户报表' }
const formatMap = { pdf: 'PDF', excel: 'Excel', csv: 'CSV', html: 'HTML' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([ReportSchedulerAPI.list(filters.value), ReportSchedulerAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, active: list.value.filter(i => i.is_active).length, pdf: list.value.filter(i => i.format === 'pdf').length, excel: list.value.filter(i => i.format === 'excel').length }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', report_type: 'sales', schedule_cron: '0 8 * * *', format: 'pdf', recipients: '', is_active: true }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await ReportSchedulerAPI.update(form.value.id, form.value)
    else await ReportSchedulerAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此报表计划？', '提示', { type: 'warning' })
  await ReportSchedulerAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="报表计划" subtitle="定时报表 · 自动生成 · 多格式导出" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">计划数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">活跃</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">PDF</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.pdf }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">Excel</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.excel }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索计划名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.report_type" placeholder="报表类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in reportTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建计划</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="140" show-overflow-tooltip />
        <el-table-column label="报表类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ reportTypeMap[row.report_type] || row.report_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="schedule_cron" label="Cron表达式" width="130" />
        <el-table-column label="格式" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="dark">{{ formatMap[row.format] || row.format }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="recipient_count" label="接收人数" width="90" align="center" />
        <el-table-column prop="last_run" label="上次运行" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="报表计划" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="报表类型">
          <el-select v-model="form.report_type" style="width:100%">
            <el-option v-for="(v, k) in reportTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="Cron表达式"><el-input v-model="form.schedule_cron" placeholder="0 8 * * *" /></el-form-item>
        <el-form-item label="格式">
          <el-select v-model="form.format" style="width:100%">
            <el-option v-for="(v, k) in formatMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="接收人"><el-input v-model="form.recipients" type="textarea" :rows="3" placeholder="邮箱地址，逗号分隔" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
