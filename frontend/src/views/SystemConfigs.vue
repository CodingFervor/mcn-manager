<script setup>
import { ref, onMounted } from 'vue'
import { SystemConfigAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, public: 0, categories: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', category: '', is_public: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([SystemConfigAPI.list(filters.value), SystemConfigAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, public: list.value.filter(i => i.is_public).length, categories: new Set(list.value.map(i => i.category)).size }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { key: '', value: '', category: '', description: '', is_public: false }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await SystemConfigAPI.update(form.value.id, form.value)
    else await SystemConfigAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此配置项？', '提示', { type: 'warning' })
  await SystemConfigAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="系统配置" subtitle="全局参数 · 运行时配置 · 环境变量" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">配置项数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">公开配置</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.public }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">分类数</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.categories }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索配置键" style="width:200px" @keyup.enter="load" />
      <el-input v-model="filters.category" placeholder="分类" style="width:140px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建配置</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="key" label="键" width="180" show-overflow-tooltip />
        <el-table-column prop="value" label="值" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="description" label="描述" width="160" show-overflow-tooltip />
        <el-table-column label="是否公开" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'info'" size="small">{{ row.is_public ? '公开' : '私有' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="系统配置" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="键"><el-input v-model="form.key" /></el-form-item>
        <el-form-item label="值"><el-input v-model="form.value" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
        <el-form-item label="是否公开"><el-switch v-model="form.is_public" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
