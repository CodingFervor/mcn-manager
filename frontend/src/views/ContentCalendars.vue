<script setup>
import { ref, onMounted } from 'vue'
import { ContentCalendarAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_status: {}, by_content_type: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', content_type: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      ContentCalendarAPI.list(filters.value),
      ContentCalendarAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    title: '', content_type: 'live', platform: '', publish_date: '',
    assignee: '', status: 'draft'
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await ContentCalendarAPI.update(form.value.id, form.value)
  else await ContentCalendarAPI.create(form.value)
  ElMessage.success(form.value.id ? '更新成功' : '创建成功')
  dialog.value = false
  load()
}

const removeItem = async (row) => {
  await ElMessageBox.confirm('确认删除该内容计划？', '提示', { type: 'warning' })
  await ContentCalendarAPI.remove(row.id)
  ElMessage.success('删除成功')
  load()
}

const contentTypeMap = { live: '直播', video: '短视频', article: '文章', story: '动态' }
const statusMap = { draft: '草稿', scheduled: '已排期', published: '已发布', cancelled: '已取消' }
const statusColor = { draft: 'info', scheduled: 'warning', published: 'success', cancelled: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="内容日历" subtitle="内容排期 · 发布管理 · 多平台协同" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">内容总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">按状态</div>
        <div style="font-size:16px;font-weight:700">
          <span v-for="(v, k) in stats.by_status" :key="k" style="margin:0 4px">
            {{ statusMap[k] || k }}: <span style="color:#ffd23f">{{ v }}</span>
          </span>
        </div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">按类型</div>
        <div style="font-size:16px;font-weight:700">
          <span v-for="(v, k) in stats.by_content_type" :key="k" style="margin:0 4px">
            {{ contentTypeMap[k] || k }}: <span style="color:#00ff9d">{{ v }}</span>
          </span>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索标题" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.content_type" placeholder="内容类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in contentTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建内容</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip />
        <el-table-column label="内容类型" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ contentTypeMap[row.content_type] || row.content_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="platform" label="平台" width="90" />
        <el-table-column label="发布日期" width="120">
          <template #default="{ row }">
            <span>{{ row.publish_date?.slice(0, 10) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="assignee" label="负责人" width="100" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑内容' : '新建内容'" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="标题"><el-input v-model="form.title" placeholder="请输入内容标题" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="内容类型">
              <el-select v-model="form.content_type" style="width:100%">
                <el-option v-for="(v, k) in contentTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="平台"><el-input v-model="form.platform" placeholder="发布平台" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="发布日期">
              <el-date-picker v-model="form.publish_date" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人"><el-input v-model="form.assignee" placeholder="负责人" /></el-form-item>
          </el-col>
        </el-row>
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
