<script setup>
import { ref, onMounted } from 'vue'
import { MultiTenantConfigAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, free: 0, pro: 0, enterprise: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', plan: '', is_active: '' })

const planMap = { free: 'Free', pro: 'Pro', enterprise: 'Enterprise' }
const planColor = { free: 'info', pro: 'warning', enterprise: 'danger' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([MultiTenantConfigAPI.list(filters.value), MultiTenantConfigAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, free: list.value.filter(i => i.plan === 'free').length, pro: list.value.filter(i => i.plan === 'pro').length, enterprise: list.value.filter(i => i.plan === 'enterprise').length }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { tenant_name: '', tenant_code: '', plan: 'free', max_users: 10, max_stores: 1, features: '', is_active: true }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await MultiTenantConfigAPI.update(form.value.id, form.value)
    else await MultiTenantConfigAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此租户配置？', '提示', { type: 'warning' })
  await MultiTenantConfigAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="多租户配置" subtitle="租户管理 · 套餐控制 · 资源隔离" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">租户数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">Free</div>
        <div style="font-size:28px;font-weight:800;color:#a8b2d1">{{ stats.free }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">Pro</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.pro }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">Enterprise</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.enterprise }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索租户名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.plan" placeholder="套餐" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in planMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建租户</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="tenant_name" label="租户名" min-width="140" show-overflow-tooltip />
        <el-table-column prop="tenant_code" label="代码" width="120" show-overflow-tooltip />
        <el-table-column label="套餐" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="planColor[row.plan]" size="small" effect="dark">{{ planMap[row.plan] || row.plan }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="max_users" label="最大用户" width="90" align="right" />
        <el-table-column prop="max_stores" label="最大店铺" width="90" align="right" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="expires_at" label="过期时间" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="租户配置" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="租户名"><el-input v-model="form.tenant_name" /></el-form-item>
        <el-form-item label="代码"><el-input v-model="form.tenant_code" /></el-form-item>
        <el-form-item label="套餐">
          <el-select v-model="form.plan" style="width:100%">
            <el-option v-for="(v, k) in planMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大用户"><el-input-number v-model="form.max_users" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="最大店铺"><el-input-number v-model="form.max_stores" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="功能特性"><el-input v-model="form.features" type="textarea" :rows="3" placeholder="JSON格式功能配置" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
