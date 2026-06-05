<script setup>
import { ref, onMounted } from 'vue'
import { VendorRatingAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, avg_overall_rating: 0, total_reviews: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', period: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      VendorRatingAPI.list(filters.value),
      VendorRatingAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    vendor_name: '', quality_score: 0, delivery_score: 0,
    service_score: 0, price_score: 0, overall_rating: 0,
    review_count: 0, period: ''
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  try {
    if (form.value.id) {
      await VendorRatingAPI.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await VendorRatingAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    dialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

const removeItem = (row) => {
  ElMessageBox.confirm('确认删除该供应商评分?', '提示', { type: 'warning' }).then(async () => {
    await VendorRatingAPI.remove(row.id)
    ElMessage.success('删除成功')
    load()
  }).catch(() => {})
}

const ratingColor = (val) => {
  if (val >= 4) return '#00ff9d'
  if (val >= 3) return '#ffd23f'
  return '#ff4d9e'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="供应商评分" subtitle="供应商评估 · 多维评分 · 绩效追踪" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">供应商数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">平均评分</div>
        <div class="stat-value">{{ Number(stats.avg_overall_rating || 0).toFixed(1) }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">评价总数</div>
        <div class="stat-value">{{ stats.total_reviews }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">优秀供应商</div>
        <div class="stat-value">{{ list.filter(i => i.overall_rating >= 4).length }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索供应商名称" style="width: 200px" @keyup.enter="load" />
      <el-input v-model="filters.period" placeholder="评估周期" style="width: 140px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建评分</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="vendor_name" label="供应商名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="质量分" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: ratingColor(row.quality_score), fontWeight: 600 }">{{ row.quality_score }}</span>
          </template>
        </el-table-column>
        <el-table-column label="交付分" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: ratingColor(row.delivery_score), fontWeight: 600 }">{{ row.delivery_score }}</span>
          </template>
        </el-table-column>
        <el-table-column label="服务分" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: ratingColor(row.service_score), fontWeight: 600 }">{{ row.service_score }}</span>
          </template>
        </el-table-column>
        <el-table-column label="价格分" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: ratingColor(row.price_score), fontWeight: 600 }">{{ row.price_score }}</span>
          </template>
        </el-table-column>
        <el-table-column label="综合评分" width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: ratingColor(row.overall_rating), fontWeight: 700, fontSize: '16px' }">{{ row.overall_rating }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="review_count" label="评价数" width="80" align="center" />
        <el-table-column prop="period" label="评估周期" width="110" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑评分' : '新建评分'" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="供应商"><el-input v-model="form.vendor_name" placeholder="供应商名称" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="质量分"><el-input-number v-model="form.quality_score" :min="0" :max="5" :precision="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="交付分"><el-input-number v-model="form.delivery_score" :min="0" :max="5" :precision="1" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="服务分"><el-input-number v-model="form.service_score" :min="0" :max="5" :precision="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="价格分"><el-input-number v-model="form.price_score" :min="0" :max="5" :precision="1" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="综合评分"><el-input-number v-model="form.overall_rating" :min="0" :max="5" :precision="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="评价数"><el-input-number v-model="form.review_count" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="评估周期"><el-input v-model="form.period" placeholder="如: 2026-Q1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
