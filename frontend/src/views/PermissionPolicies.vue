<script setup>
import { ref, onMounted } from 'vue'
import { PermissionPolicyAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, disabled: 0, modules: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', module: '', is_active: '' })

const moduleMap = { user: '用户管理', content: '内容管理', finance: '财务管理', system: '系统管理', live: '直播管理', product: '商品管理' }
const allActions = ['create', 'read', 'update', 'delete', 'export', 'import', 'approve', 'audit']

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([PermissionPolicyAPI.list(filters.value), PermissionPolicyAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, active: list.value.filter(i => i.is_active).length, disabled: list.value.filter(i => !i.is_active).length, modules: new Set(list.value.map(i => i.module)).size }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', code: '', description: '', module: 'user', actions: [], is_active: true }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row, actions: row.actions || [] }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await PermissionPolicyAPI.update(form.value.id, form.value)
    else await PermissionPolicyAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此策略？', '提示', { type: 'warning' })
  await PermissionPolicyAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="权限策略" subtitle="策略管理 · 操作授权 · 模块控制" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">策略总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">启用中</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">禁用</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ stats.disabled }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">模块数</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.modules }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索策略名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.module" placeholder="模块" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in moduleMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建策略</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="策略名" min-width="140" show-overflow-tooltip />
        <el-table-column prop="code" label="代码" width="140" show-overflow-tooltip />
        <el-table-column label="模块" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ moduleMap[row.module] || row.module }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作列表" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="a in (row.actions || []).slice(0, 4)" :key="a" size="small" style="margin:2px">{{ a }}</el-tag>
            <el-tag v-if="(row.actions || []).length > 4" size="small" type="info" style="margin:2px">+{{ row.actions.length - 4 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
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

    <el-dialog v-model="dialog" title="权限策略" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="策略名"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="代码"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="模块">
          <el-select v-model="form.module" style="width:100%">
            <el-option v-for="(v, k) in moduleMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作权限">
          <el-checkbox-group v-model="form.actions">
            <el-checkbox v-for="a in allActions" :key="a" :label="a">{{ a }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
