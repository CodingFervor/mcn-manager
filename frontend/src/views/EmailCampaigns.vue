<script setup>
import { ref, onMounted } from 'vue'
import { EmailCampaignAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_recipients: 0, avg_open_rate: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '', kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      EmailCampaignAPI.list(filters.value),
      EmailCampaignAPI.stats()
    ])
    list.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: list.value.length,
      total_recipients: list.value.reduce((s, i) => s + (i.recipients_count || 0), 0),
      avg_open_rate: list.value.length ? (list.value.reduce((s, i) => s + (i.open_rate || 0), 0) / list.value.length).toFixed(1) : 0
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', subject: '', recipients_count: 0, open_count: 0, click_count: 0,
    open_rate: 0, click_rate: 0, status: 'draft'
  }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await EmailCampaignAPI.update(form.value.id, form.value)
    else await EmailCampaignAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此邮件活动？', '提示', { type: 'warning' })
  await EmailCampaignAPI.update(row.id, { ...row, _delete: true })
  ElMessage.success('删除成功')
  load()
}

const statusMap = { draft: '草稿', scheduled: '已排期', sending: '发送中', sent: '已发送' }
const statusColor = { draft: 'info', scheduled: 'warning', sending: '', sent: 'success' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="邮件营销" subtitle="邮件活动 · 精准触达 · 效果追踪" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">活动总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总收件人</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.total_recipients }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均打开率</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.avg_open_rate }}%</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索活动名称" style="width:200px" @keyup.enter="load" />
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
        <el-table-column prop="subject" label="邮件主题" min-width="160" show-overflow-tooltip />
        <el-table-column label="收件人数" width="100" align="right">
          <template #default="{ row }"><span style="color:#00e5ff;font-weight:600">{{ row.recipients_count }}</span></template>
        </el-table-column>
        <el-table-column label="打开数" width="90" align="right">
          <template #default="{ row }"><span style="color:#00ff9d;font-weight:600">{{ row.open_count }}</span></template>
        </el-table-column>
        <el-table-column label="点击数" width="90" align="right">
          <template #default="{ row }"><span style="color:#ffd23f;font-weight:600">{{ row.click_count }}</span></template>
        </el-table-column>
        <el-table-column label="打开率" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.open_rate >= 30 ? '#00ff9d' : row.open_rate >= 15 ? '#ffd23f' : '#ff4d9e', fontWeight: 700 }">{{ row.open_rate }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="点击率" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.click_rate >= 10 ? '#00ff9d' : row.click_rate >= 5 ? '#ffd23f' : '#ff4d9e', fontWeight: 700 }">{{ row.click_rate }}%</span>
          </template>
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

    <el-dialog v-model="dialog" title="邮件活动" width="550px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="活动名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="邮件主题"><el-input v-model="form.subject" /></el-form-item>
        <el-form-item label="收件人数"><el-input-number v-model="form.recipients_count" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="打开数"><el-input-number v-model="form.open_count" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="点击数"><el-input-number v-model="form.click_count" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="打开率%"><el-input-number v-model="form.open_rate" :min="0" :max="100" :precision="1" style="width:100%" /></el-form-item>
        <el-form-item label="点击率%"><el-input-number v-model="form.click_rate" :min="0" :max="100" :precision="1" style="width:100%" /></el-form-item>
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
