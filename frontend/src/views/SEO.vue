<script setup>
import { ref, onMounted } from 'vue'
import { SEOAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, avg_score: 0, avg_page_speed: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      SEOAPI.list(filters.value),
      SEOAPI.stats()
    ])
    list.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: list.value.length,
      avg_score: list.value.length ? (list.value.reduce((s, i) => s + (i.score || 0), 0) / list.value.length).toFixed(0) : 0,
      avg_page_speed: list.value.length ? (list.value.reduce((s, i) => s + (i.page_speed || 0), 0) / list.value.length).toFixed(0) : 0
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    page_url: '', title: '', keywords: '', description: '', score: 0,
    page_speed: 0, mobile_score: 0, last_audit: ''
  }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await SEOAPI.update(form.value.id, form.value)
    else await SEOAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此SEO记录？', '提示', { type: 'warning' })
  await SEOAPI.remove(row.id)
  ElMessage.success('删除成功')
  load()
}

const scoreColor = (v) => v >= 80 ? '#00ff9d' : v >= 60 ? '#ffd23f' : '#ff4d9e'

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="SEO优化" subtitle="页面审计 · 评分监控 · 搜索优化" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">页面总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均评分</div>
        <div style="font-size:28px;font-weight:800" :style="{ color: scoreColor(stats.avg_score) }">{{ stats.avg_score }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均页面速度</div>
        <div style="font-size:28px;font-weight:800" :style="{ color: scoreColor(stats.avg_page_speed) }">{{ stats.avg_page_speed }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索页面URL/标题" style="width:220px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建SEO记录</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="page_url" label="页面URL" min-width="180" show-overflow-tooltip />
        <el-table-column prop="title" label="标题" min-width="140" show-overflow-tooltip />
        <el-table-column prop="keywords" label="关键词" width="140" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" width="160" show-overflow-tooltip />
        <el-table-column label="评分" width="80" align="center">
          <template #default="{ row }">
            <span :style="{ color: scoreColor(row.score), fontWeight: 700 }">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column label="页面速度" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: scoreColor(row.page_speed), fontWeight: 700 }">{{ row.page_speed }}</span>
          </template>
        </el-table-column>
        <el-table-column label="移动评分" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: scoreColor(row.mobile_score), fontWeight: 700 }">{{ row.mobile_score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="last_audit" label="最近审计" width="110" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="SEO优化" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="页面URL"><el-input v-model="form.page_url" /></el-form-item>
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="关键词"><el-input v-model="form.keywords" placeholder="多个关键词用逗号分隔" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="评分"><el-input-number v-model="form.score" :min="0" :max="100" style="width:100%" /></el-form-item>
        <el-form-item label="页面速度"><el-input-number v-model="form.page_speed" :min="0" :max="100" style="width:100%" /></el-form-item>
        <el-form-item label="移动评分"><el-input-number v-model="form.mobile_score" :min="0" :max="100" style="width:100%" /></el-form-item>
        <el-form-item label="最近审计"><el-date-picker v-model="form.last_audit" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
