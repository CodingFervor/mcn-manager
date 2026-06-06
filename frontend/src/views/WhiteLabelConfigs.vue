<script setup>
import { ref, onMounted } from 'vue'
import { WhiteLabelConfigAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, custom_domains: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', is_active: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([WhiteLabelConfigAPI.list(filters.value), WhiteLabelConfigAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, active: list.value.filter(i => i.is_active).length, custom_domains: list.value.filter(i => i.domain).length }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { brand_name: '', logo_url: '', primary_color: '#00e5ff', secondary_color: '#7c5cff', domain: '', custom_css: '', is_active: true }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await WhiteLabelConfigAPI.update(form.value.id, form.value)
    else await WhiteLabelConfigAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此配置？', '提示', { type: 'warning' })
  await WhiteLabelConfigAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="白标配置" subtitle="品牌定制 · 视觉主题 · 自定义域名" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">配置数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">启用中</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">自定义域名</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.custom_domains }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索品牌名称" style="width:200px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建配置</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="brand_name" label="品牌名" min-width="140" show-overflow-tooltip />
        <el-table-column prop="logo_url" label="Logo" width="160" show-overflow-tooltip />
        <el-table-column label="主色" width="100" align="center">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;justify-content:center;gap:6px">
              <span :style="{ display:'inline-block', width:'18px', height:'18px', borderRadius:'4px', background: row.primary_color }"></span>
              <span style="font-size:12px">{{ row.primary_color }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="副色" width="100" align="center">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;justify-content:center;gap:6px">
              <span :style="{ display:'inline-block', width:'18px', height:'18px', borderRadius:'4px', background: row.secondary_color }"></span>
              <span style="font-size:12px">{{ row.secondary_color }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="domain" label="域名" width="180" show-overflow-tooltip />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="白标配置" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="品牌名"><el-input v-model="form.brand_name" /></el-form-item>
        <el-form-item label="Logo URL"><el-input v-model="form.logo_url" /></el-form-item>
        <el-form-item label="主色">
          <el-color-picker v-model="form.primary_color" />
        </el-form-item>
        <el-form-item label="副色">
          <el-color-picker v-model="form.secondary_color" />
        </el-form-item>
        <el-form-item label="域名"><el-input v-model="form.domain" placeholder="brand.example.com" /></el-form-item>
        <el-form-item label="自定义CSS"><el-input v-model="form.custom_css" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
