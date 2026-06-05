<script setup>
import { ref, onMounted } from 'vue'
import { ProductLinkAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_clicks: 0, total_conversions: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

const statusMap = { active: '生效中', expired: '已过期', disabled: '已禁用' }
const statusColor = { active: 'success', expired: 'info', disabled: 'danger' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([ProductLinkAPI.list(filters.value), ProductLinkAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, total_clicks: 0, total_conversions: 0 }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { platform: '', url: '', click_count: 0, conversion_count: 0, status: 'active' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }

async function save() {
  try {
    if (form.value.id) await ProductLinkAPI.update(form.value.id, form.value)
    else await ProductLinkAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false; load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (row) => {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await ProductLinkAPI.remove(row.id)
  ElMessage.success('已删除'); load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="商品链接" subtitle="链接管理 · 点击追踪 · 转化分析" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-label">链接总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">总点击量</div>
        <div class="stat-value">{{ Number(stats.total_clicks || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总转化量</div>
        <div class="stat-value">{{ Number(stats.total_conversions || 0).toLocaleString() }}</div>
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
        <el-table-column prop="platform" label="平台" width="120" />
        <el-table-column prop="url" label="链接地址" min-width="220" show-overflow-tooltip />
        <el-table-column label="点击量" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan)">{{ Number(row.click_count || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="转化量" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-pink);font-weight:700">{{ Number(row.conversion_count || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
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

    <el-dialog v-model="dialog" title="商品链接" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="平台"><el-input v-model="form.platform" placeholder="如：抖音、淘宝、京东" /></el-form-item>
        <el-form-item label="链接地址"><el-input v-model="form.url" placeholder="请输入商品链接" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="点击量"><el-input-number v-model="form.click_count" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="转化量"><el-input-number v-model="form.conversion_count" :min="0" style="width:100%" /></el-form-item>
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
