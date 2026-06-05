<script setup>
import { ref, onMounted } from 'vue'
import { StreamTemplateAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_category: {}, public_count: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

const categoryMap = { standard: '标准', festival: '节日', brand: '品牌', clearance: '清仓', new_product: '新品' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([StreamTemplateAPI.list(filters.value), StreamTemplateAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, by_category: {}, public_count: 0 }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', category: 'standard', duration_minutes: 0, usage_count: 0, is_public: false }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }

async function save() {
  try {
    if (form.value.id) await StreamTemplateAPI.update(form.value.id, form.value)
    else await StreamTemplateAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false; load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (row) => {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await StreamTemplateAPI.remove(row.id)
  ElMessage.success('已删除'); load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播模板" subtitle="模板管理 · 快速复用 · 分类归档" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-label">模板总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">分类数</div>
        <div class="stat-value">{{ Object.keys(stats.by_category || {}).length }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">公开模板</div>
        <div class="stat-value">{{ stats.public_count }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索" style="width:200px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="模板名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="分类" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ categoryMap[row.category] || row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时长(分钟)" width="110">
          <template #default="{ row }">{{ row.duration_minutes }}</template>
        </el-table-column>
        <el-table-column label="使用次数" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan)">{{ row.usage_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="公开" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'info'" size="small">{{ row.is_public ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="直播模板" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="模板名称"><el-input v-model="form.name" placeholder="请输入模板名称" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" style="width:100%">
            <el-option v-for="(v, k) in categoryMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="时长(分钟)"><el-input-number v-model="form.duration_minutes" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="使用次数"><el-input-number v-model="form.usage_count" :min="0" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="是否公开">
          <el-switch v-model="form.is_public" active-text="公开" inactive-text="私有" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
